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
    )
    settings.validate_runtime()
