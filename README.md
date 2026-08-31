# ZTE Dongle — Home Assistant Integration

[![Validate](https://github.com/jackpf/ha-zte-dongle/actions/workflows/validate.yml/badge.svg)](https://github.com/jackpf/ha-zte-dongle/actions/workflows/validate.yml)

Home Assistant integration for ZTE LTE USB dongles (MiFi hotspots).

Tested with the ZTE MF79U. Should work with other ZTE dongles using the GoForm API.

## Features

- Connection status and network type
- Signal strength (bars, RSRP, SNR)
- Realtime and monthly data usage
- Data cap monitoring
- Battery status (for battery-powered models)

## Installation

Install via [HACS](https://hacs.xyz) or copy `custom_components/zte_dongle/` into your HA config directory.

## Configuration

Add the integration via the HA UI. You will be prompted for:

- **IP address** — default `192.168.0.1`
- **Password** — your dongle's web UI password

## CLI

A standalone CLI is included for testing outside of Home Assistant:

```bash
pip install -r requirements.txt
python3 cli.py --password <password> metrics
python3 cli.py --password <password> enable cellular
python3 cli.py --password <password> disable cellular
python3 cli.py --password <password> enable wifi
python3 cli.py --password <password> disable wifi
```
