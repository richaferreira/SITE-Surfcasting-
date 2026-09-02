from fastapi import HTTPException, Request, status

from app.core.config import get_settings
from app.core.rate_limit import public_rate_limiter


def _client_key(request: Request, scope: str) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    host = forwarded or (request.client.host if request.client else "unknown")
    return f"{scope}:{host}"


def _enforce(request: Request, scope: str, limit: int, detail: str) -> None:
    if not public_rate_limiter.allow(_client_key(request, scope), limit=limit):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": "60"},
        )


def enforce_auth_rate_limit(request: Request) -> None:
    settings = get_settings()
    _enforce(
        request,
        "auth",
        settings.auth_rate_limit_per_minute,
        "Muitas tentativas de autenticação. Aguarde um minuto.",
    )


def enforce_community_rate_limit(request: Request) -> None:
    settings = get_settings()
    _enforce(
        request,
        "community",
        settings.community_rate_limit_per_minute,
        "Muitas interações na comunidade. Aguarde um minuto.",
    )


def enforce_public_api_rate_limit(request: Request) -> None:
    settings = get_settings()
    _enforce(
        request,
        "public-api",
        settings.public_api_rate_limit_per_minute,
        "Limite temporário de consultas atingido. Aguarde um minuto.",
    )
