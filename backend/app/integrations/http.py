from __future__ import annotations

from typing import Any
from time import perf_counter

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.exceptions import ExternalAPIError
from app.monitoring import monitoring_registry


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
        started_at = perf_counter()
        response: requests.Response | None = None
        success = False
        error_code: str | None = None
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
            error_code = "timeout"
            raise ExternalAPIError(f"Tempo esgotado ao consultar {provider_name}.") from exc
        except requests.RequestException as exc:
            error_code = "http_error"
            raise ExternalAPIError(f"Falha HTTP ao consultar {provider_name}.") from exc
        except ValueError as exc:
            error_code = "invalid_json"
            raise ExternalAPIError(f"{provider_name} retornou JSON inválido.") from exc
        else:
            if not isinstance(payload, dict):
                error_code = "unexpected_payload"
                raise ExternalAPIError(f"{provider_name} retornou uma estrutura inesperada.")
            success = True
            return payload
        finally:
            monitoring_registry.record_external(
                provider_name,
                success=success,
                latency_ms=(perf_counter() - started_at) * 1000,
                status_code=response.status_code if response is not None else None,
                error_code=error_code,
            )
