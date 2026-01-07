from __future__ import annotations

from dataclasses import dataclass

import requests

from apps.api.app.core.config import settings


@dataclass
class EskomAPIError(Exception):
    status_code: int
    message: str


class EskomClient:
    BASE_URL = "https://developer.sepush.co.za/business/2.0"

    def __init__(self, token: str | None = None) -> None:
        self.token = token or settings.eskom_token_key

    def _headers(self) -> dict:
        if not self.token:
            raise EskomAPIError(status_code=500, message="Missing ESKOM_TOKEN_KEY.")
        return {"token": self.token}

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.BASE_URL}{path}"
        response = requests.get(url, headers=self._headers(), params=params, timeout=10)
        if response.status_code == 429 or response.status_code >= 500:
            raise EskomAPIError(status_code=response.status_code, message=response.text)
        response.raise_for_status()
        return response.json()

    def search_areas(self, text: str) -> dict:
        return self._get("/areas_search", params={"text": text})

    def get_area(self, area_id: str) -> dict:
        return self._get("/area", params={"id": area_id})

    def get_status_current(self) -> dict:
        return self._get("/status/current")
