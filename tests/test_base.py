import pytest

from victron_ble.devices.base import (
    _HAVE_CRYPTOGRAPHY,
    _HAVE_PYCRYPTODOME,
    BitReader,
    _aes_ctr_decrypt,
    _pkcs7_pad16,
)


class TestBitReader:
    def test_to_signed_int(self) -> None:
        assert BitReader.to_signed_int(0x000, 12) == 0x000
        assert BitReader.to_signed_int(0x001, 12) == 0x001
        assert BitReader.to_signed_int(0x242, 12) == 0x242
        assert BitReader.to_signed_int(0x7FF, 12) == 0x7FF
        assert BitReader.to_signed_int(0x800, 12) == -0x800
        assert BitReader.to_signed_int(0xCAD, 12) == -0x353
        assert BitReader.to_signed_int(0xFFF, 12) == -0x001

        assert BitReader.to_signed_int(0x00, 5) == 0x00
        assert BitReader.to_signed_int(0x01, 5) == 0x01
        assert BitReader.to_signed_int(0x0F, 5) == 0x0F
        assert BitReader.to_signed_int(0x10, 5) == -0x10
        assert BitReader.to_signed_int(0x1F, 5) == -0x01

    def test_read(self) -> None:
        data = "1a2b3c4d5e6f7890"
        reader = BitReader(bytes.fromhex(data))

        assert reader.read_bit() == 0
        assert reader.read_bit() == 1
        assert reader.read_bit() == 0
        assert reader.read_bit() == 1
        assert reader.read_unsigned_int(6) == 0x31
        assert reader.read_signed_int(6) == 0x0A
        assert reader.read_signed_int(4) == -0x04
        assert reader.read_unsigned_int(11) == 0x4D3
        assert reader.read_bit() == 0
        assert reader.read_unsigned_int(32) == 0x90786F5E


class TestPkcs7Pad16:
    def test_zero_length(self) -> None:
        assert _pkcs7_pad16(b"") == bytes([16]) * 16

    def test_one_short_of_block(self) -> None:
        data = b"A" * 15
        padded = _pkcs7_pad16(data)
        assert len(padded) == 16
        assert padded[-1] == 1

    def test_exact_block_pads_to_next_block(self) -> None:
        data = b"A" * 16
        padded = _pkcs7_pad16(data)
        assert len(padded) == 32
        assert padded[16:] == bytes([16]) * 16

    def test_partial_block(self) -> None:
        data = b"hello"
        padded = _pkcs7_pad16(data)
        assert len(padded) == 16
        assert padded[5:] == bytes([11]) * 11


class TestAesCtrDecrypt:
    def test_at_least_one_backend_available(self) -> None:
        assert _HAVE_CRYPTOGRAPHY or _HAVE_PYCRYPTODOME

    def test_known_vector(self) -> None:
        # AES-128-CTR with a 128-bit little-endian counter, captured
        # from the PyCryptodome reference path so the test passes
        # regardless of which backend is selected at runtime.
        key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
        iv = 0xABCD
        ciphertext = bytes.fromhex("a1b2c3d4e5f60718293a4b5c6d7e8f90")
        expected = bytes.fromhex(
            "ffdfb8e3520c96d024e3777391dd7d84" "c42bccdd20ac34c7fb149e3cb063a4eb"
        )
        assert _aes_ctr_decrypt(key, iv, ciphertext) == expected

    def test_short_ciphertext_padded_to_block(self) -> None:
        key = b"\x00" * 16
        iv = 0
        plain = _aes_ctr_decrypt(key, iv, b"\x00" * 5)
        assert len(plain) == 16

    @pytest.mark.skipif(
        not (_HAVE_CRYPTOGRAPHY and _HAVE_PYCRYPTODOME),
        reason="cross-backend check requires both libraries",
    )
    def test_backends_agree_single_block(self) -> None:
        from Crypto.Cipher import AES
        from Crypto.Util import Counter
        from Crypto.Util.Padding import pad as _pycd_pad

        key = bytes(range(16))
        iv = 0xABCD
        ciphertext = b"victron-ble-test"  # 16 bytes
        ctr = Counter.new(128, initial_value=iv, little_endian=True)
        ref = AES.new(key, AES.MODE_CTR, counter=ctr).decrypt(_pycd_pad(ciphertext, 16))
        got = _aes_ctr_decrypt(key, iv, ciphertext)
        assert got == ref

    @pytest.mark.skipif(
        not (_HAVE_CRYPTOGRAPHY and _HAVE_PYCRYPTODOME),
        reason="cross-backend check requires both libraries",
    )
    def test_backends_agree_multi_block(self) -> None:
        # Spans counter increments to catch backends that mis-handle
        # the little-endian carry across blocks.
        from Crypto.Cipher import AES
        from Crypto.Util import Counter
        from Crypto.Util.Padding import pad as _pycd_pad

        key = bytes(range(16))
        iv = 0xABCD
        ciphertext = bytes(range(256))  # 16 full blocks
        ctr = Counter.new(128, initial_value=iv, little_endian=True)
        ref = AES.new(key, AES.MODE_CTR, counter=ctr).decrypt(_pycd_pad(ciphertext, 16))
        got = _aes_ctr_decrypt(key, iv, ciphertext)
        assert got == ref

    @pytest.mark.skipif(
        not (_HAVE_CRYPTOGRAPHY and _HAVE_PYCRYPTODOME),
        reason="cross-backend check requires both libraries",
    )
    def test_backends_agree_across_le_carry(self) -> None:
        # iv = 0xFF triggers a low-byte carry on the very first
        # increment, which would mismatch a big-endian counter.
        from Crypto.Cipher import AES
        from Crypto.Util import Counter
        from Crypto.Util.Padding import pad as _pycd_pad

        key = bytes(range(16))
        iv = 0xFF
        ciphertext = bytes(range(48))  # 3 full blocks
        ctr = Counter.new(128, initial_value=iv, little_endian=True)
        ref = AES.new(key, AES.MODE_CTR, counter=ctr).decrypt(_pycd_pad(ciphertext, 16))
        got = _aes_ctr_decrypt(key, iv, ciphertext)
        assert got == ref
