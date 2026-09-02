from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import get_db

settings = get_settings()
password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=True)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, password_digest: str) -> bool:
    return password_hash.verify(password, password_digest)


def token_digest(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def _encode_token(payload: dict[str, Any]) -> str:
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, role: str, expires_minutes: int | None = None) -> str:
    minutes = expires_minutes or settings.access_token_expire_minutes
    now = datetime.now(UTC)
    return _encode_token(
        {
            "sub": subject,
            "role": role,
            "typ": "access",
            "iat": now,
            "exp": now + timedelta(minutes=minutes),
            "iss": settings.jwt_issuer,
        }
    )


def create_refresh_token(subject: str, expires_days: int | None = None) -> str:
    days = expires_days or settings.refresh_token_expire_days
    now = datetime.now(UTC)
    return _encode_token(
        {
            "sub": subject,
            "typ": "refresh",
            "jti": uuid4().hex,
            "iat": now,
            "exp": now + timedelta(days=days),
            "iss": settings.jwt_issuer,
        }
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if payload.get("typ") != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token inválido para esta operação.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def decode_access_token(token: str) -> dict[str, Any]:
    return decode_token(token, "access")


def decode_refresh_token(token: str) -> dict[str, Any]:
    return decode_token(token, "refresh")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token sem usuário associado.")

    row = db.execute(
        text(
            """
            SELECT u.id, u.name, u.username, u.email, u.avatar_url, u.bio, u.is_active,
                   r.code AS role
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE u.id = :user_id
            LIMIT 1
            """
        ),
        {"user_id": int(user_id)},
    ).mappings().first()

    if not row or not row["is_active"]:
        raise HTTPException(status_code=401, detail="Usuário inexistente ou inativo.")
    return dict(row)


def require_roles(*roles: str):
    def dependency(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        if current_user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Você não possui permissão para esta operação.")
        return current_user

    return dependency
