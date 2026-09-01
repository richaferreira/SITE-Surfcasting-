from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import BeachProfile

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class BeachCreate(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    slug: str | None = Field(default=None, min_length=3, max_length=180, pattern=SLUG_PATTERN)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(default="RJ", min_length=2, max_length=2)
    description: str | None = Field(default=None, max_length=10000)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    sea_bearing_deg: float = Field(ge=0, lt=360)
    beach_profile: BeachProfile
    accessibility_summary: str | None = Field(default=None, max_length=500)
    is_published: bool = False

    @field_validator("name", "city")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("state")
    @classmethod
    def normalize_state(cls, value: str) -> str:
        return value.strip().upper()


class BeachUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=150)
    slug: str | None = Field(default=None, min_length=3, max_length=180, pattern=SLUG_PATTERN)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    description: str | None = Field(default=None, max_length=10000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    sea_bearing_deg: float | None = Field(default=None, ge=0, lt=360)
    beach_profile: BeachProfile | None = None
    accessibility_summary: str | None = Field(default=None, max_length=500)
    is_published: bool | None = None

    @field_validator("name", "city")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("state")
    @classmethod
    def normalize_state(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else None

    @model_validator(mode="after")
    def reject_empty_update(self) -> "BeachUpdate":
        if not self.model_fields_set:
            raise ValueError("Informe pelo menos um campo para atualização.")
        non_nullable_fields = {
            "name",
            "slug",
            "city",
            "state",
            "latitude",
            "longitude",
            "sea_bearing_deg",
            "beach_profile",
            "is_published",
        }
        invalid_nulls = sorted(
            field
            for field in non_nullable_fields.intersection(self.model_fields_set)
            if getattr(self, field) is None
        )
        if invalid_nulls:
            raise ValueError(
                "Estes campos não aceitam valor nulo: " + ", ".join(invalid_nulls) + "."
            )
        return self


class BeachResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    city: str
    state: str
    description: str | None
    latitude: float
    longitude: float
    sea_bearing_deg: float
    beach_profile: BeachProfile
    accessibility_summary: str | None
    is_published: bool
    created_by_id: int
    updated_by_id: int | None
    created_at: datetime
    updated_at: datetime


class BeachListResponse(BaseModel):
    items: list[BeachResponse]
    total: int
    offset: int
    limit: int
