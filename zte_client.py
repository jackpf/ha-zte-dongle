import hashlib

import requests


class ZTEClient:
    _HEADERS = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "X-Requested-With": "XMLHttpRequest",
    }

    def __init__(self, ip: str, password: str):
        self.ip = ip
        self.password = password
        self._base_url = f"http://{ip}"
        self._session = requests.Session()
        self._session.headers.update({
            **self._HEADERS,
            "Referer": f"http://{ip}/index.html",
            "Host": ip,
        })
        self._firmware_md5: str | None = None

    @staticmethod
    def _sha256(s: str) -> str:
        return hashlib.sha256(s.encode()).hexdigest().upper()

    @staticmethod
    def _md5(s: str) -> str:
        return hashlib.md5(s.encode()).hexdigest()

    def _get_raw(self, cmd: str) -> dict:
        resp = self._session.get(
            f"{self._base_url}/goform/goform_get_cmd_process",
            params={"isTest": "false", "cmd": cmd, "multi_data": "1"},
        )
        resp.raise_for_status()
        return resp.json()

    def login(self) -> None:
        """Authenticate and store the session stok cookie."""
        ld = self._get_raw("LD")["LD"]
        inner = self._sha256(self.password)
        login_pass = self._sha256(inner + ld)
        resp = self._session.post(
            f"{self._base_url}/goform/goform_set_cmd_process",
            headers={"Origin": self._base_url},
            data={"isTest": "false", "goformId": "LOGIN", "password": login_pass},
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("result") != "0":
            raise RuntimeError(f"Login failed (result={result.get('result')})")

    def _get_firmware_md5(self) -> str:
        """Cache MD5(wa_inner_version + cr_version) used in AD token computation."""
        if self._firmware_md5 is None:
            data = self._get_raw("wa_inner_version,cr_version")
            self._firmware_md5 = self._md5(data["wa_inner_version"] + data["cr_version"])
        return self._firmware_md5

    def get_params(self, *params: str) -> dict:
        """Fetch one or more device parameters by name."""
        return self._get_raw(",".join(params))

    def post_command(self, goform_id: str, extra: dict | None = None) -> dict:
        """Send an authenticated command. Computes AD = MD5(MD5(fw_versions) + RD)."""
        fw_md5 = self._get_firmware_md5()
        rd = self._get_raw("RD")["RD"]
        ad = self._md5(fw_md5 + rd)

        payload = {
            "isTest": "false",
            "notCallback": "true",
            "goformId": goform_id,
            "AD": ad,
            **(extra or {}),
        }
        resp = self._session.post(
            f"{self._base_url}/goform/goform_set_cmd_process",
            headers={"Origin": self._base_url},
            data=payload,
        )
        resp.raise_for_status()
        return resp.json()
