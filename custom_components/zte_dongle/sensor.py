from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfDataRate, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZTEDongleCoordinator


def _non_empty(data: dict[str, Any], key: str) -> str | None:
    v = data.get(key, "")
    return v if v != "" else None


@dataclass(frozen=True, kw_only=True)
class ZTESensorDescription(SensorEntityDescription):
    """Extends SensorEntityDescription with a value extractor."""

    value_fn: Any = None  # Callable[[dict], Any]


SENSOR_DESCRIPTIONS: tuple[ZTESensorDescription, ...] = (
    # --- Connection ---
    ZTESensorDescription(
        key="modem_main_state",
        name="Modem State",
        value_fn=lambda d: _non_empty(d, "modem_main_state"),
    ),
    ZTESensorDescription(
        key="ppp_status",
        name="WAN Status",
        value_fn=lambda d: _non_empty(d, "ppp_status"),
    ),
    ZTESensorDescription(
        key="network_type",
        name="Network Type",
        value_fn=lambda d: _non_empty(d, "network_type"),
    ),
    ZTESensorDescription(
        key="network_provider",
        name="Network Provider",
        value_fn=lambda d: _non_empty(d, "network_provider"),
    ),
    ZTESensorDescription(
        key="simcard_roam",
        name="Roaming",
        value_fn=lambda d: _non_empty(d, "simcard_roam"),
    ),
    # --- Signal ---
    ZTESensorDescription(
        key="signalbar",
        name="Signal Bars",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: int(v) if (v := _non_empty(d, "signalbar")) else None,
    ),
    ZTESensorDescription(
        key="lte_rsrp",
        name="LTE RSRP",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dBm",
        value_fn=lambda d: int(v) if (v := _non_empty(d, "lte_rsrp")) else None,
    ),
    ZTESensorDescription(
        key="lte_snr",
        name="LTE SNR",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="dB",
        value_fn=lambda d: float(v) if (v := _non_empty(d, "lte_snr")) else None,
    ),
    ZTESensorDescription(
        key="wan_active_band",
        name="Active Band",
        value_fn=lambda d: _non_empty(d, "wan_active_band"),
    ),
    # --- Realtime throughput ---
    ZTESensorDescription(
        key="realtime_tx_bytes",
        name="Session Upload",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        value_fn=lambda d: int(v) if (v := _non_empty(d, "realtime_tx_bytes")) else None,
    ),
    ZTESensorDescription(
        key="realtime_rx_bytes",
        name="Session Download",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        value_fn=lambda d: int(v) if (v := _non_empty(d, "realtime_rx_bytes")) else None,
    ),
    ZTESensorDescription(
        key="realtime_tx_thrpt",
        name="Upload Rate",
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        value_fn=lambda d: int(v) if (v := _non_empty(d, "realtime_tx_thrpt")) else None,
    ),
    ZTESensorDescription(
        key="realtime_rx_thrpt",
        name="Download Rate",
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        value_fn=lambda d: int(v) if (v := _non_empty(d, "realtime_rx_thrpt")) else None,
    ),
    # --- Monthly usage ---
    ZTESensorDescription(
        key="monthly_tx_bytes",
        name="Monthly Upload",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        value_fn=lambda d: int(v) if (v := _non_empty(d, "monthly_tx_bytes")) else None,
    ),
    ZTESensorDescription(
        key="monthly_rx_bytes",
        name="Monthly Download",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        value_fn=lambda d: int(v) if (v := _non_empty(d, "monthly_rx_bytes")) else None,
    ),
    ZTESensorDescription(
        key="data_volume_limit_size",
        name="Data Cap",
        value_fn=lambda d: _non_empty(d, "data_volume_limit_size"),
    ),
    ZTESensorDescription(
        key="data_volume_alert_percent",
        name="Data Alert Threshold",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda d: int(v) if (v := _non_empty(d, "data_volume_alert_percent")) else None,
    ),
    # --- Battery (populated on battery-powered models) ---
    ZTESensorDescription(
        key="battery_vol_percent",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda d: int(v) if (v := _non_empty(d, "battery_vol_percent")) else None,
    ),
    ZTESensorDescription(
        key="battery_charging",
        name="Battery Charging",
        value_fn=lambda d: _non_empty(d, "battery_charging"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ZTEDongleCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ZTESensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class ZTESensor(CoordinatorEntity[ZTEDongleCoordinator], SensorEntity):
    """A single sensor entity backed by ZTEDongleCoordinator."""

    entity_description: ZTESensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ZTEDongleCoordinator,
        entry: ConfigEntry,
        description: ZTESensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)},
            name=self._entry.title,
            manufacturer="ZTE",
        )

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
