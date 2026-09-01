from datetime import datetime, timezone

import pytest

from app.core.config import Settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.enums import RoleCode
from app.models.role import Role
from app.models.user import User
from app.api.dependencies.auth import require_roles


def security_settings(**overrides: object) -> Settings:
    values = {
        "jwt_secret_key": "test-secret-key-with-more-than-32-characters",
        "jwt_algorithm": "HS256",
        "jwt_access_token_expire_minutes": 30,
        "jwt_issuer": "surfcasting-tests",
        "jwt_audience": "surfcasting-test-client",
    }
    values.update(overrides)
    return Settings(**values)


def build_user(role_code: RoleCode) -> User:
    role = Role(id=1, code=role_code.value, name=role_code.value)
    return User(
        id=10,
        role_id=1,
        role=role,
        name="Usuário Teste",
        username="usuario.teste",
        email="usuario@example.com",
        password_hash="unused",
        is_active=True,
    )


def test_argon2_hash_never_contains_plain_password() -> None:
    plain_password = "PescaSegura123"
    password_hash = hash_password(plain_password)

    assert plain_password not in password_hash
    assert verify_password(plain_password, password_hash)
    assert not verify_password("senha-incorreta", password_hash)


def test_access_token_round_trip() -> None:
    settings = security_settings()
    token, expires_in = create_access_token(42, settings)

    assert expires_in == 1800
    assert decode_access_token(token, settings) == 42


def test_expired_access_token_is_rejected() -> None:
    settings = security_settings(jwt_access_token_expire_minutes=-1)
    token, _ = create_access_token(
        42,
        settings,
        now=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    with pytest.raises(AuthenticationError):
        decode_access_token(token, settings)


def test_rbac_allows_admin_and_rejects_common_user() -> None:
    dependency = require_roles(RoleCode.ADMIN)
    admin = build_user(RoleCode.ADMIN)
    common_user = build_user(RoleCode.USER)

    assert dependency(admin) is admin
    with pytest.raises(AuthorizationError):
        dependency(common_user)
