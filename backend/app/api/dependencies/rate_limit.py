from fastapi import Request

from app.core.config import get_settings
from app.core.exceptions import RateLimitExceededError
from app.core.rate_limit import public_rate_limiter


def _client_key(request: Request, scope: str) -> str:
    host = request.client.host if request.client else "unknown"
    return f"{scope}:{host}"


def enforce_score_rate_limit(request: Request) -> None:
    settings = get_settings()
    if not public_rate_limiter.allow(
        _client_key(request, "score"),
        limit=settings.score_rate_limit_per_minute,
    ):
        raise RateLimitExceededError("Muitas consultas de score. Tente novamente em um minuto.")


def enforce_auth_rate_limit(request: Request) -> None:
    settings = get_settings()
    if not public_rate_limiter.allow(
        _client_key(request, "auth"),
        limit=settings.auth_rate_limit_per_minute,
    ):
        raise RateLimitExceededError("Muitas tentativas de autenticação. Aguarde um minuto.")


def enforce_community_rate_limit(request: Request) -> None:
    settings = get_settings()
    if not public_rate_limiter.allow(
        _client_key(request, "community"),
        limit=settings.community_rate_limit_per_minute,
    ):
        raise RateLimitExceededError("Muitas interações na comunidade. Aguarde um minuto.")
