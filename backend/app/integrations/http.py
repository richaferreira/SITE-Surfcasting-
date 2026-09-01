from __future__ import annotations

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.exceptions import ExternalAPIError


class JsonHttpClient:
    def __init__(self, timeout_seconds: float = 10.0, session: requests.Session | None = None):
        self.timeout_seconds = timeout_seconds
        self.session = session or self._build_session()

    @staticmethod
    def _build_session() -> requests.Session:
        retry = Retry(
            total=2,
            connect=2,
            read=2,
            backoff_factor=0.25,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            respect_retry_after_header=True,
        )
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=retry))
        return session

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, Any],
        headers: dict[str, str] | None = None,
        provider_name: str,
    ) -> dict[str, Any]:
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.Timeout as exc:
            raise ExternalAPIError(f"Tempo esgotado ao consultar {provider_name}.") from exc
        except requests.RequestException as exc:
            raise ExternalAPIError(f"Falha HTTP ao consultar {provider_name}.") from exc
        except ValueError as exc:
            raise ExternalAPIError(f"{provider_name} retornou JSON inválido.") from exc

        if not isinstance(payload, dict):
            raise ExternalAPIError(f"{provider_name} retornou uma estrutura inesperada.")
        return payload
