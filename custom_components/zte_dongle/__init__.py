from __future__ import annotations


async def async_setup_entry(hass, entry) -> bool:
    from homeassistant.const import Platform

    from .const import DOMAIN
    from .coordinator import ZTEDongleCoordinator

    coordinator = ZTEDongleCoordinator(
        hass,
        ip=entry.data["ip"],
        password=entry.data["password"],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])
    return True


async def async_unload_entry(hass, entry) -> bool:
    from homeassistant.const import Platform

    from .const import DOMAIN

    ok = await hass.config_entries.async_unload_platforms(entry, [Platform.SENSOR])
    if ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return ok
