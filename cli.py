#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_components"))

import aiohttp

from zte_dongle.client import ZTEClient
from zte_dongle.const import DEFAULT_IP, METRICS_PARAMS


async def cmd_enable(client: ZTEClient, target: str) -> dict:
    if target == "cellular":
        return await client.post_command("CONNECT_NETWORK")
    return await client.post_command("SET_WIFI_INFO", {
        "wifiEnabled": "1",
        "m_ssid_enable": "0",
        "lan_sec_ssid_control": "1",
    })


async def cmd_disable(client: ZTEClient, target: str) -> dict:
    if target == "cellular":
        return await client.post_command("DISCONNECT_NETWORK")
    return await client.post_command("SET_WIFI_INFO", {"wifiEnabled": "0"})


async def cmd_metrics(client: ZTEClient) -> dict:
    return await client.get_params(*METRICS_PARAMS)


async def run(args: argparse.Namespace) -> None:
    async with aiohttp.ClientSession() as session:
        client = ZTEClient(args.ip, args.password, session)
        await client.login()

        if args.command == "enable":
            result = await cmd_enable(client, args.target)
        elif args.command == "disable":
            result = await cmd_disable(client, args.target)
        elif args.command == "metrics":
            result = await cmd_metrics(client)

    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="ZTE dongle control")
    parser.add_argument("--ip", default=DEFAULT_IP)
    parser.add_argument("--password", required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for action in ("enable", "disable"):
        sub = subparsers.add_parser(action)
        sub.add_argument("target", choices=["cellular", "wifi"])

    subparsers.add_parser("metrics")

    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
