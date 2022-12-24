# victron_ble

## Commands

* `victron-ble discover` - Discover Victron device IDs

```bash
❯ victron-ble discover --help                                                                                      ⏎ ✹
Usage: victron-ble discover [OPTIONS]

  Discover Victron devices with Instant Readout

Options:
  --help  Show this message and exit.
```

* `victron-ble read` - Parse data from Victron instant readouts
```bash
❯ victron-ble read --help                                                                                          ⏎ ✹
Usage: victron-ble read [OPTIONS] [DEVICE_KEYS]...

  Read data from specified devices

Options:
  --help  Show this message and exit.
```
## Devices

### SmartShunt
Sample output:

```json
{
    "remaining_mins": 65535,
    "aux_mode": 3,
    "current": 0,
    "voltage": 12.53,
    "consumed_ah": 0.0,
    "soc": 100.0,
    "alarm": {
        "low_voltage": false,
        "high_voltage": false,
        "low_soc": false,
        "low_starter_voltage": false,
        "high_starter_voltage": false,
        "low_temperature": false,
        "high_temperature": false,
        "mid_voltage": false
    }
}
```

When aux_mode is equal to the following values, an additional property will be included in the output:

* 0 => `"starter_voltage": -0.02`
* 1 => `"midpoint_voltage": 12.35`
* 2 => `"temperature": 29.35`
* 3 => Disabled



### Smart Battery Sense
Sample output:

```json
{
    'temperature': 29.565,
    'voltage': 12.22
}
```
