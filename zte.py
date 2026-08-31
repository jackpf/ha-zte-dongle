#!/usr/bin/env python3
import argparse
import json
import sys

from zte_client import ZTEClient

DEFAULT_IP = "192.168.0.1"

METRICS_PARAMS = [
    # Connection & modem state
    "modem_main_state",
    "ppp_status",
    "opms_wan_mode",
    "network_type",
    "network_provider",
    "simcard_roam",
    # Signal
    "signalbar",
    "rssi",
    "rscp",
    "lte_rsrp",
    "lte_snr",
    "ecio",
    "lte_pci",
    "cell_id",
    "wan_active_band",
    "wan_active_channel",
    "wan_lte_ca",
    "lte_ca_pcell_band",
    "lte_ca_pcell_bandwidth",
    "lte_ca_pcell_arfcn",
    "lte_ca_scell_band",
    "lte_ca_scell_bandwidth",
    "lte_ca_scell_arfcn",
    "lte_multi_ca_scell_info",
    "Z5g_snr",
    "Z5g_rsrp",
    "Z5g_SINR",
    "Z5g_dlEarfcn",
    "Z5g_CELL_ID",
    "nr5g_pci",
    "nr5g_action_band",
    "nr5g_action_channel",
    "nr5g_cell_id",
    # Realtime throughput
    "realtime_tx_bytes",
    "realtime_rx_bytes",
    "realtime_time",
    "realtime_tx_thrpt",
    "realtime_rx_thrpt",
    # Monthly usage
    "monthly_tx_bytes",
    "monthly_rx_bytes",
    "monthly_time",
    "date_month",
    "data_volume_limit_switch",
    "data_volume_limit_unit",
    "data_volume_limit_size",
    "data_volume_alert_percent",
    "wan_auto_clear_flow_data_switch",
    "traffic_clear_date",
    # Battery
    "battery_vol_percent",
    "battery_charging",
    "battery_charg_type",
    "battery_temp",
    "external_charging_flag",
]


def cmd_enable(client: ZTEClient, target: str) -> dict:
    if target == "cellular":
        return client.post_command("CONNECT_NETWORK")
    return client.post_command("SET_WIFI_INFO", {
        "wifiEnabled": "1",
        "m_ssid_enable": "0",
        "lan_sec_ssid_control": "1",
    })


def cmd_disable(client: ZTEClient, target: str) -> dict:
    if target == "cellular":
        return client.post_command("DISCONNECT_NETWORK")
    return client.post_command("SET_WIFI_INFO", {"wifiEnabled": "0"})


def cmd_metrics(client: ZTEClient) -> dict:
    return client.get_params(*METRICS_PARAMS)


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

    client = ZTEClient(args.ip, args.password)
    client.login()

    if args.command == "enable":
        result = cmd_enable(client, args.target)
    elif args.command == "disable":
        result = cmd_disable(client, args.target)
    elif args.command == "metrics":
        result = cmd_metrics(client)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
