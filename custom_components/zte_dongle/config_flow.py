from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .client import ZTEAuthError, ZTEClient
from .const import CONF_IP, CONF_PASSWORD, DEFAULT_IP, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ZTEDongleConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the ZTE Dongle config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            ip = user_input[CONF_IP]
            password = user_input[CONF_PASSWORD]

            try:
                async with aiohttp.ClientSession() as session:
                    client = ZTEClient(ip, password, session)
                    await client.login()
            except ZTEAuthError:
                errors["base"] = "invalid_auth"
            except (aiohttp.ClientError, OSError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during ZTE Dongle setup")
                errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(ip)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"ZTE Dongle ({ip})",
                    data={CONF_IP: ip, CONF_PASSWORD: password},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_IP, default=DEFAULT_IP): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
