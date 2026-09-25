"""Cliente mínimo para la API REST de NetBox con paginación automática."""

from __future__ import annotations

import os
from typing import Any, Iterator

import requests


class NetBoxError(Exception):
    """Error devuelto por la API de NetBox o de configuración."""


class NetBoxClient:
    def __init__(
        self,
        url: str,
        token: str,
        verify_ssl: bool = True,
        timeout: int = 30,
        page_size: int = 200,
    ) -> None:
        if not url or not token:
            raise NetBoxError("Hace falta NETBOX_URL y NETBOX_TOKEN")
        self.api_url = url.rstrip("/") + "/api"
        self.timeout = timeout
        self.page_size = page_size
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.headers.update(
            {
                "Authorization": f"Token {token}",
                "Accept": "application/json",
            }
        )

    @classmethod
    def from_env(cls, verify_ssl: bool | None = None) -> "NetBoxClient":
        if verify_ssl is None:
            verify_ssl = os.getenv("NETBOX_VERIFY_SSL", "true").lower() != "false"
        return cls(
            url=os.getenv("NETBOX_URL", ""),
            token=os.getenv("NETBOX_TOKEN", ""),
            verify_ssl=verify_ssl,
        )

    def get_all(self, endpoint: str, **filters: Any) -> Iterator[dict]:
        """Itera sobre todos los objetos de un endpoint siguiendo el campo `next`."""
        url: str | None = f"{self.api_url}/{endpoint.strip('/')}/"
        params: dict | None = {"limit": self.page_size, **filters}

        while url:
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
            except requests.RequestException as exc:
                raise NetBoxError(f"No se pudo conectar con NetBox: {exc}") from exc

            if resp.status_code != 200:
                raise NetBoxError(f"{resp.status_code} en {url}: {resp.text[:200]}")

            data = resp.json()
            yield from data.get("results", [])
            url = data.get("next")
            params = None  # `next` ya trae los parámetros en la URL
