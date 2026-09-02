from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZTEDongleCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ZTEDongleCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        CellularSwitch(coordinator, entry),
        WiFiSwitch(coordinator, entry),
    ])


class _ZTESwitch(CoordinatorEntity[ZTEDongleCoordinator], SwitchEntity):
    """Base class for ZTE dongle switches."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ZTEDongleCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)},
            name=self._entry.title,
            manufacturer="ZTE",
        )


class CellularSwitch(_ZTESwitch):
    """Switch to connect/disconnect the cellular WAN."""

    _attr_name = "Cellular"
    _attr_icon = "mdi:signal-cellular-3"

    def __init__(self, coordinator: ZTEDongleCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.unique_id}_cellular"

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("ppp_status") == "ipv4_ipv6_connected"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_cellular(enabled=True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_cellular(enabled=False)
        await self.coordinator.async_request_refresh()


class WiFiSwitch(_ZTESwitch):
    """Switch to enable/disable the WiFi radio."""

    _attr_name = "Wi-Fi"
    _attr_icon = "mdi:wifi"

    def __init__(self, coordinator: ZTEDongleCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.unique_id}_wifi"

    @property
    def is_on(self) -> bool | None:
        val = self.coordinator.data.get("radio_off")
        if val == "0":
            return True   # radio on = wifi on
        if val == "1":
            return False  # radio explicitly off
        return None       # "2" = transitioning, unknow

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_wifi(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_wifi(False)
        await self.coordinator.async_request_refresh()
