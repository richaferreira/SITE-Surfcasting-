from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import PostContentType, PostStatus
from app.schemas.beach import SLUG_PATTERN


class EquipmentSpecificationInput(BaseModel):
    rod_length_m: float | None = Field(default=None, gt=0, le=10)
    rod_construction: str | None = Field(default=None, max_length=80)
    reel_size: int | None = Field(default=None, ge=500, le=30000)
    main_line_material: str | None = Field(default=None, max_length=80)
    main_line_diameter_mm: float | None = Field(default=None, gt=0, le=2)
    shock_leader_type: str | None = Field(default=None, max_length=100)
    casting_weight_min_g: int | None = Field(default=None, ge=0, le=1000)
    casting_weight_max_g: int | None = Field(default=None, ge=0, le=1000)
    extra_specs: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_casting_range(self) -> "EquipmentSpecificationInput":
        if (
            self.casting_weight_min_g is not None
            and self.casting_weight_max_g is not None
            and self.casting_weight_max_g < self.casting_weight_min_g
        ):
            raise ValueError("O peso máximo de arremesso deve ser maior ou igual ao mínimo.")
        return self


class EquipmentSpecificationResponse(EquipmentSpecificationInput):
    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(min_length=5, max_length=220)
    slug: str | None = Field(default=None, min_length=3, max_length=240, pattern=SLUG_PATTERN)
    excerpt: str | None = Field(default=None, max_length=500)
    content: str = Field(min_length=20)
    content_type: PostContentType
    status: PostStatus = PostStatus.RASCUNHO
    featured_image_url: str | None = Field(default=None, max_length=500)
    video_url: str | None = Field(default=None, max_length=500)
    seo_title: str | None = Field(default=None, max_length=70)
    seo_description: str | None = Field(default=None, max_length=160)
    equipment_specification: EquipmentSpecificationInput | None = None

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_equipment_specification(self) -> "PostCreate":
        if self.equipment_specification and self.content_type is not PostContentType.EQUIPAMENTO:
            raise ValueError("Ficha técnica só pode ser usada em conteúdo de equipamento.")
        return self


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=220)
    slug: str | None = Field(default=None, min_length=3, max_length=240, pattern=SLUG_PATTERN)
    excerpt: str | None = Field(default=None, max_length=500)
    content: str | None = Field(default=None, min_length=20)
    content_type: PostContentType | None = None
    status: PostStatus | None = None
    featured_image_url: str | None = Field(default=None, max_length=500)
    video_url: str | None = Field(default=None, max_length=500)
    seo_title: str | None = Field(default=None, max_length=70)
    seo_description: str | None = Field(default=None, max_length=160)
    equipment_specification: EquipmentSpecificationInput | None = None

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_update(self) -> "PostUpdate":
        if not self.model_fields_set:
            raise ValueError("Informe pelo menos um campo para atualização.")
        non_nullable = {"title", "slug", "content", "content_type", "status"}
        invalid = sorted(
            field
            for field in non_nullable.intersection(self.model_fields_set)
            if getattr(self, field) is None
        )
        if invalid:
            raise ValueError("Estes campos não aceitam valor nulo: " + ", ".join(invalid) + ".")
        return self


class PublicAuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    username: str


class PublicPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    excerpt: str | None
    content: str
    content_type: PostContentType
    featured_image_url: str | None
    video_url: str | None
    seo_title: str | None
    seo_description: str | None
    published_at: datetime | None
    author: PublicAuthorResponse
    equipment_specification: EquipmentSpecificationResponse | None


class PublicPostSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    excerpt: str | None
    content_type: PostContentType
    featured_image_url: str | None
    seo_title: str | None
    seo_description: str | None
    published_at: datetime | None
    author: PublicAuthorResponse


class PostResponse(PublicPostResponse):
    author_id: int
    status: PostStatus
    created_at: datetime
    updated_at: datetime


class PublicPostListResponse(BaseModel):
    items: list[PublicPostSummaryResponse]
    total: int
    offset: int
    limit: int


class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int
    offset: int
    limit: int
