import pytest

from app.core.config import Settings
from app.services.health import DependencyStatus


def test_dependency_status_requires_both_datastores() -> None:
    assert DependencyStatus(mysql=True, neo4j=True).ready
    assert not DependencyStatus(mysql=True, neo4j=False).ready
    assert not DependencyStatus(mysql=False, neo4j=True).ready


def test_dependency_status_payload() -> None:
    payload = DependencyStatus(mysql=True, neo4j=False).as_dict()
    assert payload["status"] == "not_ready"
    assert payload["dependencies"] == {"mysql": "ok", "neo4j": "unavailable"}


def test_development_accepts_local_defaults() -> None:
    settings = Settings(app_env="development")
    settings.validate_runtime()


def test_production_rejects_insecure_defaults() -> None:
    settings = Settings(app_env="production")
    with pytest.raises(RuntimeError, match="Configuração insegura para produção"):
        settings.validate_runtime()


def test_production_accepts_secure_runtime_configuration() -> None:
    settings = Settings(
        app_env="production",
        app_debug=False,
        jwt_secret="s" * 48,
        admin_password="Senha-Forte-123456",
        neo4j_password="senha-neo4j-forte",
        cors_origins="https://surfcasting.example.com",
        frontend_url="https://surfcasting.example.com",
        media_public_origin="https://surfcasting.example.com",
        auth_cookie_secure=True,
        smtp_host="smtp.example.com",
    )
    settings.validate_runtime()


def test_production_rejects_insecure_cookie_or_http_origins() -> None:
    settings = Settings(
        app_env="production",
        app_debug=False,
        jwt_secret="s" * 48,
        admin_password="Senha-Forte-123456",
        neo4j_password="senha-neo4j-forte",
        cors_origins="https://surfcasting.example.com",
        frontend_url="http://surfcasting.example.com",
        media_public_origin="http://surfcasting.example.com",
        auth_cookie_secure=False,
        smtp_host="smtp.example.com",
    )
    with pytest.raises(RuntimeError) as exc_info:
        settings.validate_runtime()
    message = str(exc_info.value)
    assert "AUTH_COOKIE_SECURE" in message
    assert "FRONTEND_URL" in message
    assert "MEDIA_PUBLIC_ORIGIN" in message
