from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
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


def test_degrees_to_compass() -> None:
    assert degrees_to_compass(0) == "N"
    assert degrees_to_compass(45) == "NE"
    assert degrees_to_compass(180) == "S"
    assert degrees_to_compass(225) == "SW"
    assert degrees_to_compass(359) == "N"
