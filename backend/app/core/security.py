from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import Settings
from app.core.exceptions import AuthenticationError

password_hasher = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hasher.hash("timing-only-password-9d7c3e")


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(
    user_id: int,
    settings: Settings,
    now: datetime | None = None,
) -> tuple[str, int]:
    if len(settings.jwt_secret_key) < 32:
        raise RuntimeError("JWT_SECRET_KEY deve possuir pelo menos 32 caracteres.")

    issued_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    expires_in = settings.jwt_access_token_expire_minutes * 60
    expires_at = issued_at + timedelta(seconds=expires_in)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": "access",
        "iat": issued_at,
        "exp": expires_at,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return token, expires_in


def decode_access_token(token: str, settings: Settings) -> int:
    if len(settings.jwt_secret_key) < 32:
        raise AuthenticationError("Autenticação indisponível: chave JWT não configurada.")

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["sub", "type", "iat", "exp", "iss", "aud"]},
        )
        if payload.get("type") != "access":
            raise AuthenticationError("Tipo de token inválido.")
        return int(payload["sub"])
    except AuthenticationError:
        raise
    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError("Token de acesso inválido ou expirado.") from exc
