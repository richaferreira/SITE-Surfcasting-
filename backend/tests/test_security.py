import pytest
from fastapi import HTTPException

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    token_digest,
    verify_password,
)
from app.services.recommendations import degrees_to_compass


def test_password_hash_roundtrip() -> None:
    digest = hash_password("Senha-Segura-123")
    assert digest != "Senha-Segura-123"
    assert verify_password("Senha-Segura-123", digest)
    assert not verify_password("senha-errada", digest)


def test_access_token_roundtrip() -> None:
    token = create_access_token("42", "USER", expires_minutes=5)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "USER"
    assert payload["typ"] == "access"


def test_refresh_token_roundtrip_and_digest() -> None:
    token = create_refresh_token("42", expires_days=2)
    payload = decode_refresh_token(token)
    assert payload["sub"] == "42"
    assert payload["typ"] == "refresh"
    assert payload["jti"]
    assert len(token_digest(token)) == 64
    assert token_digest(token) == token_digest(token)


def test_access_and_refresh_tokens_are_not_interchangeable() -> None:
    access_token = create_access_token("42", "USER", expires_minutes=5)
    refresh_token = create_refresh_token("42", expires_days=2)

    with pytest.raises(HTTPException):
        decode_refresh_token(access_token)
    with pytest.raises(HTTPException):
        decode_access_token(refresh_token)


def test_degrees_to_compass() -> None:
    assert degrees_to_compass(0) == "N"
    assert degrees_to_compass(45) == "NE"
    assert degrees_to_compass(180) == "S"
    assert degrees_to_compass(225) == "SW"
    assert degrees_to_compass(359) == "N"
