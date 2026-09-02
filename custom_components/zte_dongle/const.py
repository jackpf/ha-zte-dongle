from datetime import timedelta

DOMAIN = "zte_dongle"

CONF_IP = "ip"
CONF_PASSWORD = "password"

DEFAULT_IP = "192.168.0.1"
UPDATE_INTERVAL = timedelta(seconds=30)

# Maps ZTE GoForm param name → normalized snake_case key used throughout the integration.
# Most params are already snake_case; only the WiFi ones need remapping.
METRICS_PARAMS: dict[str, str] = {
    # Connection & modem state
    "modem_main_state": "modem_main_state",
    "ppp_status": "ppp_status",
    "opms_wan_mode": "opms_wan_mode",
    "network_type": "network_type",
    "network_provider": "network_provider",
    "simcard_roam": "simcard_roam",
    # Signal
    "signalbar": "signalbar",
    "rssi": "rssi",
    "rscp": "rscp",
    "lte_rsrp": "lte_rsrp",
    "lte_snr": "lte_snr",
    "ecio": "ecio",
    "lte_pci": "lte_pci",
    "cell_id": "cell_id",
    "wan_active_band": "wan_active_band",
    "wan_active_channel": "wan_active_channel",
    "wan_lte_ca": "wan_lte_ca",
    "lte_ca_pcell_band": "lte_ca_pcell_band",
    "lte_ca_pcell_bandwidth": "lte_ca_pcell_bandwidth",
    "lte_ca_pcell_arfcn": "lte_ca_pcell_arfcn",
    "lte_ca_scell_band": "lte_ca_scell_band",
    "lte_ca_scell_bandwidth": "lte_ca_scell_bandwidth",
    "lte_ca_scell_arfcn": "lte_ca_scell_arfcn",
    "lte_multi_ca_scell_info": "lte_multi_ca_scell_info",
    "Z5g_snr": "z5g_snr",
    "Z5g_rsrp": "z5g_rsrp",
    "Z5g_SINR": "z5g_sinr",
    "Z5g_dlEarfcn": "z5g_dl_earfcn",
    "Z5g_CELL_ID": "z5g_cell_id",
    "nr5g_pci": "nr5g_pci",
    "nr5g_action_band": "nr5g_action_band",
    "nr5g_action_channel": "nr5g_action_channel",
    "nr5g_cell_id": "nr5g_cell_id",
    # Realtime throughput
    "realtime_tx_bytes": "realtime_tx_bytes",
    "realtime_rx_bytes": "realtime_rx_bytes",
    "realtime_time": "realtime_time",
    "realtime_tx_thrpt": "realtime_tx_thrpt",
    "realtime_rx_thrpt": "realtime_rx_thrpt",
    # Monthly usage
    "monthly_tx_bytes": "monthly_tx_bytes",
    "monthly_rx_bytes": "monthly_rx_bytes",
    "monthly_time": "monthly_time",
    "date_month": "date_month",
    "data_volume_limit_switch": "data_volume_limit_switch",
    "data_volume_limit_unit": "data_volume_limit_unit",
    "data_volume_limit_size": "data_volume_limit_size",
    "data_volume_alert_percent": "data_volume_alert_percent",
    "wan_auto_clear_flow_data_switch": "wan_auto_clear_flow_data_switch",
    "traffic_clear_date": "traffic_clear_date",
    # Battery
    "battery_vol_percent": "battery_vol_percent",
    "battery_charging": "battery_charging",
    "battery_charg_type": "battery_charg_type",
    "battery_temp": "battery_temp",
    "external_charging_flag": "external_charging_flag",
    # WiFi
    "RadioOff": "radio_off",
    "m_ssid_enable": "m_ssid_enable",
    "SSID1": "ssid1",
    "m_SSID": "m_ssid",
    "HideSSID": "hide_ssid",
    "m_HideSSID": "m_hide_ssid",
    "AuthMode": "auth_mode",
    "station_num_ssid2": "station_num_ssid2",
}
