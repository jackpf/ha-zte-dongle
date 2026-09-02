#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_components"))
sys.path.insert(0, "/config/custom_components")

import aiohttp

from zte_dongle.client import ZTEClient
from zte_dongle.const import DEFAULT_IP


async def run(args: argparse.Namespace) -> None:
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:
        client = ZTEClient(args.ip, args.password, session)
        await client.login()

        if args.command == "enable":
            if args.target == "cellular":
                result = await client.set_cellular(True)
            else:
                result = await client.set_wifi(True)
        elif args.command == "disable":
            if args.target == "cellular":
                result = await client.set_cellular(False)
            else:
                result = await client.set_wifi(False)
        elif args.command == "metrics":
            result = await client.fetch_metrics()

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
