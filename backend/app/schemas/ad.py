from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import AdPlacement


class AdCampaignInput(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    placement: AdPlacement
    title: str = Field(min_length=3, max_length=120)
    image_url: str = Field(min_length=1, max_length=500)
    target_url: str = Field(min_length=1, max_length=500)
    alt_text: str = Field(min_length=5, max_length=180)
    starts_at: datetime
    ends_at: datetime
    is_active: bool = True

    @field_validator("name", "title", "alt_text", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, value: str) -> str:
        if not (value.startswith("/media/") or value.startswith("https://")):
            raise ValueError("A imagem deve usar HTTPS ou um arquivo do Gestor de Mídia.")
        return value

    @field_validator("target_url")
    @classmethod
    def validate_target_url(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError("O destino do anúncio deve usar HTTPS.")
        return value

    @model_validator(mode="after")
    def validate_period(self) -> "AdCampaignInput":
        if self.ends_at <= self.starts_at:
            raise ValueError("O término deve ser posterior ao início da campanha.")
        return self


class AdCampaignUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=120)
    placement: AdPlacement | None = None
    title: str | None = Field(default=None, min_length=3, max_length=120)
    image_url: str | None = Field(default=None, min_length=1, max_length=500)
    target_url: str | None = Field(default=None, min_length=1, max_length=500)
    alt_text: str | None = Field(default=None, min_length=5, max_length=180)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def reject_empty(self) -> "AdCampaignUpdate":
        if not self.model_fields_set:
            raise ValueError("Informe pelo menos um campo para atualização.")
        return self


class AdCampaignResponse(AdCampaignInput):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime


class PublicAdResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    placement: AdPlacement
    title: str
    image_url: str
    target_url: str
    alt_text: str


class AdCampaignListResponse(BaseModel):
    items: list[AdCampaignResponse]
    total: int


class PublicAdListResponse(BaseModel):
    items: list[PublicAdResponse]
