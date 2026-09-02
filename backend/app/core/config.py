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

    jwt_secret: str = "troque-esta-chave-em-producao"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "surfcasting-regiao-dos-lagos"
    access_token_expire_minutes: int = 720
    refresh_token_expire_days: int = 30

    openweather_api_key: str = ""
    stormglass_api_key: str = ""

    mysql_url: str = "mysql+pymysql://surfcasting:surfcasting_dev@localhost:3306/surfcasting"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    admin_name: str = "Administrador"
    admin_username: str = "admin"
    admin_email: str = "admin@example.com"
    admin_password: str = "troque-esta-senha"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

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

        if errors:
            raise RuntimeError("Configuração insegura para produção: " + "; ".join(errors))


@lru_cache
def get_settings() -> Settings:
    return Settings()
