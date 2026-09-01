from __future__ import annotations

import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import ZTEAuthError, ZTEClient
from .const import CONF_IP, CONF_PASSWORD, DOMAIN, METRICS_PARAMS, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ZTEDongleCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the ZTE dongle for all metrics on a fixed interval."""

    def __init__(self, hass: HomeAssistant, ip: str, password: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self._ip = ip
        self._password = password
        self._session: aiohttp.ClientSession | None = None
        self._client: ZTEClient | None = None

    async def _async_setup(self) -> None:
        self._session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))
        self._client = ZTEClient(self._ip, self._password, self._session)
        try:
            await self._client.login()
        except ZTEAuthError as err:
            raise ConfigEntryAuthFailed from err

    async def _async_update_data(self) -> dict[str, Any]:
        if self._client is None:
            await self._async_setup()

        try:
            await self._client.login()
            raw = await self._client.get_params(*METRICS_PARAMS.keys())
            return {METRICS_PARAMS[k]: v for k, v in raw.items() if k in METRICS_PARAMS}
        except ZTEAuthError as err:
            raise ConfigEntryAuthFailed from err
        except (aiohttp.ClientError, OSError) as err:
            raise UpdateFailed(f"Error communicating with dongle: {err}") from err

    async def async_command(self, goform_id: str, extra: dict | None = None) -> dict:
        """Send an authenticated GoForm command."""
        return await self._client.post_command(goform_id, extra)

    async def async_shutdown(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None
        await super().async_shutdown()
