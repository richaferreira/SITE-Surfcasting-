from functools import lru_cache
from pathlib import Path
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

    media_root: Path = Path("uploads")
    media_url_prefix: str = "/media"
    media_max_upload_mb: int = Field(default=250, ge=1, le=2048)
    media_image_max_dimension: int = Field(default=2400, ge=320, le=8000)
    media_image_quality: int = Field(default=82, ge=40, le=95)
    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"

    score_cache_ttl_seconds: int = Field(default=600, ge=30, le=3600)
    score_cache_max_entries: int = Field(default=1000, ge=10, le=10000)
    score_rate_limit_per_minute: int = Field(default=30, ge=1, le=1000)
    auth_rate_limit_per_minute: int = Field(default=10, ge=1, le=1000)
    community_rate_limit_per_minute: int = Field(default=20, ge=1, le=1000)

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
