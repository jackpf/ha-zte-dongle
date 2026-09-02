from __future__ import annotations

import hashlib
from typing import Any

import aiohttp

from .const import METRICS_PARAMS


class ZTEAuthError(Exception):
    """Raised when login fails."""


class ZTEClient:
    _HEADERS = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "X-Requested-With": "XMLHttpRequest",
    }

    def __init__(self, ip: str, password: str, session: aiohttp.ClientSession) -> None:
        self._ip = ip
        self._password = password
        self._session = session
        self._base_url = f"http://{ip}"
        self._headers = {
            **self._HEADERS,
            "Referer": f"http://{ip}/index.html",
            "Host": ip,
        }
        self._firmware_md5: str | None = None

    @staticmethod
    def _sha256(s: str) -> str:
        return hashlib.sha256(s.encode()).hexdigest().upper()

    @staticmethod
    def _md5(s: str) -> str:
        return hashlib.md5(s.encode()).hexdigest()

    async def _get_raw(self, cmd: str) -> dict[str, Any]:
        async with self._session.get(
            f"{self._base_url}/goform/goform_get_cmd_process",
            params={"isTest": "false", "cmd": cmd, "multi_data": "1"},
            headers=self._headers,
        ) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=None)

    async def login(self) -> None:
        """Authenticate and store the session stok cookie."""
        ld = (await self._get_raw("LD"))["LD"]
        inner = self._sha256(self._password)
        login_pass = self._sha256(inner + ld)
        async with self._session.post(
            f"{self._base_url}/goform/goform_set_cmd_process",
            headers={**self._headers, "Origin": self._base_url},
            data={"isTest": "false", "goformId": "LOGIN", "password": login_pass},
        ) as resp:
            resp.raise_for_status()
            result = await resp.json(content_type=None)
        if result.get("result") != "0":
            raise ZTEAuthError(f"Login failed (result={result.get('result')})")

    async def _get_firmware_md5(self) -> str:
        """Cache MD5(wa_inner_version + cr_version) used in AD token computation."""
        if self._firmware_md5 is None:
            data = await self._get_raw("wa_inner_version,cr_version")
            self._firmware_md5 = self._md5(data["wa_inner_version"] + data["cr_version"])
        return self._firmware_md5

    async def get_params(self, *params: str) -> dict[str, Any]:
        """Fetch one or more device parameters by name."""
        return await self._get_raw(",".join(params))

    async def post_command(
        self, goform_id: str, extra: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Send an authenticated command. Computes AD = MD5(MD5(fw_versions) + RD)."""
        fw_md5 = await self._get_firmware_md5()
        rd = (await self._get_raw("RD"))["RD"]
        ad = self._md5(fw_md5 + rd)

        payload = {
            "isTest": "false",
            "notCallback": "true",
            "goformId": goform_id,
            "AD": ad,
            **(extra or {}),
        }
        async with self._session.post(
            f"{self._base_url}/goform/goform_set_cmd_process",
            headers={**self._headers, "Origin": self._base_url},
            data=payload,
        ) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=None)

    async def connect_cellular(self) -> dict[str, Any]:
        return await self.post_command("CONNECT_NETWORK")

    async def disconnect_cellular(self) -> dict[str, Any]:
        return await self.post_command("DISCONNECT_NETWORK")

    async def set_wifi(self, enabled: bool) -> dict[str, Any]:
        if enabled:
            return await self.post_command(
                "SET_WIFI_INFO",
                {"wifiEnabled": "1", "m_ssid_enable": "0", "lan_sec_ssid_control": "1"},
            )
        return await self.post_command("SET_WIFI_INFO", {"wifiEnabled": "0"})

    async def fetch_metrics(self) -> dict[str, Any]:
        raw = await self.get_params(*METRICS_PARAMS.keys())
        return {METRICS_PARAMS[k]: v for k, v in raw.items() if k in METRICS_PARAMS}
