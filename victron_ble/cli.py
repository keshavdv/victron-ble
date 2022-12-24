import asyncio
import logging
from typing import List, Tuple

import click

from victron_ble.scanner import DebugScanner, DiscoveryScanner, Scanner

logger = logging.getLogger("victron_ble")
logging.basicConfig()


class DeviceKeyParam(click.ParamType):
    name = "device_key"

    def convert(self, value, param, ctx):
        if isinstance(value, str):
            parts = value.split("@")
            if len(parts) == 2:
                addr = parts[0].strip()
                key = parts[1].strip()
                return (addr, key)

        self.fail(f"{value} is not a valid <addr>@<key> pair", param, ctx)


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Increase logging output")
def cli(verbose):
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)


@cli.command(help="Discover Victron devices with Instant Readout")
def discover():
    loop = asyncio.get_event_loop()

    async def scan():
        scanner = DiscoveryScanner()
        await scanner.start()

    asyncio.ensure_future(scan())
    loop.run_forever()


@cli.command(help="Dump all advertisements matching the given device ID")
@click.argument("id", type=str)
def dump(id: str):
    loop = asyncio.get_event_loop()

    async def scan():
        scanner = DebugScanner(id)
        await scanner.start()

    asyncio.ensure_future(scan())
    loop.run_forever()


@cli.command(help="Read data from specified devices")
@click.argument("device_keys", nargs=-1, type=DeviceKeyParam())
def read(device_keys: List[Tuple[str, str]]):
    loop = asyncio.get_event_loop()

    async def scan(keys):
        scanner = Scanner(keys)
        await scanner.start()

    asyncio.ensure_future(scan({k: v for k, v in device_keys}))
    loop.run_forever()


if __name__ == "__main__":
    cli()
