from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
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
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    openweather_api_key: str = ""
    stormglass_api_key: str = ""

    jwt_secret_key: str = ""
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=30, gt=0, le=1440)
    jwt_issuer: str = "surfcasting-regiao-dos-lagos"
    jwt_audience: str = "surfcasting-web"

    mysql_url: str = "mysql+pymysql://surfcasting:surfcasting_dev@localhost:3306/surfcasting"
    mysql_echo: bool = False
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    @field_validator("api_v1_prefix")
    @classmethod
    def normalize_api_prefix(cls, value: str) -> str:
        normalized = "/" + value.strip().strip("/")
        if normalized == "/":
            raise ValueError("API_V1_PREFIX não pode ser vazio.")
        return normalized

    @field_validator("jwt_secret_key")
    @classmethod
    def reject_example_secrets(cls, value: str) -> str:
        normalized = value.strip()
        if normalized.lower().startswith(("substitua", "change-me", "changeme")):
            raise ValueError("JWT_SECRET_KEY contém um valor de exemplo inseguro.")
        return normalized

    @model_validator(mode="after")
    def require_production_secrets(self) -> "Settings":
        if self.app_env.lower() in {"production", "staging"} and len(self.jwt_secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY deve possuir pelo menos 32 caracteres neste ambiente.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
