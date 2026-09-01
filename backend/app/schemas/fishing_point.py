from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import AccessibilityLevel, FishingPointType
from app.schemas.beach import SLUG_PATTERN


class FishingPointCreate(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    slug: str | None = Field(default=None, min_length=3, max_length=180, pattern=SLUG_PATTERN)
    point_type: FishingPointType
    description: str | None = Field(default=None, max_length=10000)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accessibility: AccessibilityLevel = AccessibilityLevel.MODERADA
    access_notes: str | None = Field(default=None, max_length=500)
    risk_notes: str | None = Field(default=None, max_length=500)
    verified_at: datetime | None = None
    is_active: bool = True

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class FishingPointUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=150)
    slug: str | None = Field(default=None, min_length=3, max_length=180, pattern=SLUG_PATTERN)
    point_type: FishingPointType | None = None
    description: str | None = Field(default=None, max_length=10000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    accessibility: AccessibilityLevel | None = None
    access_notes: str | None = Field(default=None, max_length=500)
    risk_notes: str | None = Field(default=None, max_length=500)
    verified_at: datetime | None = None
    is_active: bool | None = None

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_update(self) -> "FishingPointUpdate":
        if not self.model_fields_set:
            raise ValueError("Informe pelo menos um campo para atualização.")
        non_nullable = {
            "name",
            "slug",
            "point_type",
            "latitude",
            "longitude",
            "accessibility",
            "is_active",
        }
        invalid = sorted(
            field
            for field in non_nullable.intersection(self.model_fields_set)
            if getattr(self, field) is None
        )
        if invalid:
            raise ValueError("Estes campos não aceitam valor nulo: " + ", ".join(invalid) + ".")
        return self


class PublicFishingPointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    point_type: FishingPointType
    description: str | None
    latitude: float
    longitude: float
    accessibility: AccessibilityLevel
    access_notes: str | None
    risk_notes: str | None
    verified_at: datetime | None


class FishingPointResponse(PublicFishingPointResponse):
    beach_id: int
    is_active: bool
    created_by_id: int
    created_at: datetime
    updated_at: datetime


class PublicFishingPointListResponse(BaseModel):
    items: list[PublicFishingPointResponse]
    total: int


class FishingPointListResponse(BaseModel):
    items: list[FishingPointResponse]
    total: int

