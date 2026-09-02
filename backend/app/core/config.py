from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Surfcasting Região dos Lagos API"
    app_env: str = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"
    request_timeout_seconds: float = 10.0
    cors_origins: str = "http://localhost:3000"
    frontend_url: str = "http://localhost:3000"

    jwt_secret: str = "troque-esta-chave-em-producao"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "surfcasting-regiao-dos-lagos"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    auth_cookie_secure: bool = False
    auth_cookie_domain: str = ""
    access_cookie_name: str = "srl_access"
    refresh_cookie_name: str = "srl_refresh"
    csrf_cookie_name: str = "srl_csrf"
    csrf_header_name: str = "X-CSRF-Token"

    auth_rate_limit_per_minute: int = 10
    community_rate_limit_per_minute: int = 30
    public_api_rate_limit_per_minute: int = 60

    openweather_api_key: str = ""
    stormglass_api_key: str = ""

    mysql_url: str = "mysql+pymysql://surfcasting:surfcasting_dev@localhost:3306/surfcasting"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "no-reply@surfcasting.local"
    smtp_from_name: str = "Surfcasting Região dos Lagos"
    smtp_use_tls: bool = True

    media_root: str = "uploads"
    media_public_url: str = "/media"
    media_max_image_mb: int = 8

    admin_name: str = "Administrador"
    admin_username: str = "admin"
    admin_email: str = "admin@example.com"
    admin_password: str = "troque-esta-senha"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def cookie_domain(self) -> str | None:
        value = self.auth_cookie_domain.strip()
        return value or None

    def validate_runtime(self) -> None:
        if self.app_env.lower() != "production":
            return

        errors: list[str] = []
        if self.app_debug:
            errors.append("APP_DEBUG deve ser false em produção")
        if self.jwt_secret == "troque-esta-chave-em-producao" or len(self.jwt_secret) < 32:
            errors.append("JWT_SECRET deve ter pelo menos 32 caracteres e não pode usar o valor padrão")
        if self.admin_password == "troque-esta-senha" or len(self.admin_password) < 12:
            errors.append("ADMIN_PASSWORD deve ter pelo menos 12 caracteres e não pode usar o valor padrão")
        if not self.neo4j_password:
            errors.append("NEO4J_PASSWORD deve ser definido em produção")
        if "*" in self.cors_origin_list:
            errors.append("CORS_ORIGINS não pode conter wildcard em produção")
        if not self.auth_cookie_secure:
            errors.append("AUTH_COOKIE_SECURE deve ser true em produção")
        if not self.frontend_url.lower().startswith("https://"):
            errors.append("FRONTEND_URL deve usar HTTPS em produção")
        if not self.smtp_host:
            errors.append("SMTP_HOST deve ser definido em produção para verificação e recuperação de conta")

        if errors:
            raise RuntimeError("Configuração insegura para produção: " + "; ".join(errors))


@lru_cache
def get_settings() -> Settings:
    return Settings()
