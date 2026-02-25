from urllib.parse import quote

import httpx


class PhpIpamError(Exception):
    pass


class PhpIpamClient:
    def __init__(self, url: str, app_id: str, token: str) -> None:
        self.base_url = f"{url.rstrip('/')}/api/{app_id}"
        self.token = token

    def _headers(self) -> dict[str, str]:
        return {"token": self.token, "Content-Type": "application/json"}

    def _build_url(self, *parts: str | int) -> str:
        segments = [quote(str(p), safe="/") for p in parts]
        return f"{self.base_url}/{'/'.join(segments)}/"

    def _handle_response(self, response: httpx.Response) -> dict:
        data = response.json()
        if not data.get("success"):
            raise PhpIpamError(data.get("message", f"HTTP {response.status_code}"))
        return data

    @staticmethod
    def authenticate(
        url: str, app_id: str, username: str, password: str
    ) -> str:
        base = f"{url.rstrip('/')}/api/{app_id}"
        response = httpx.post(
            f"{base}/user/",
            auth=(username, password),
        )
        data = response.json()
        if not data.get("success"):
            raise PhpIpamError(data.get("message", "Authentication failed"))
        return data["data"]["token"]

    def get(self, controller: str, *path: str | int) -> dict | list:
        url = self._build_url(controller, *path)
        response = httpx.get(url, headers=self._headers())
        return self._handle_response(response)["data"]

    def post(self, controller: str, *path: str | int, data: dict) -> dict:
        url = self._build_url(controller, *path)
        response = httpx.post(url, headers=self._headers(), json=data)
        return self._handle_response(response)

    def patch(
        self, controller: str, resource_id: int, *, data: dict
    ) -> dict:
        url = self._build_url(controller, resource_id)
        response = httpx.patch(url, headers=self._headers(), json=data)
        return self._handle_response(response)

    def delete(self, controller: str, resource_id: int) -> dict:
        url = self._build_url(controller, resource_id)
        response = httpx.delete(url, headers=self._headers())
        return self._handle_response(response)
