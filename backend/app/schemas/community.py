from datetime import datetime

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    title: str = Field(min_length=4, max_length=220)
    slug: str = Field(min_length=4, max_length=240, pattern=r"^[a-z0-9-]+$")
    excerpt: str | None = Field(default=None, max_length=500)
    content: str = Field(min_length=20)
    content_type: str = Field(default="ARTIGO", pattern=r"^(ARTIGO|TUTORIAL|VIDEO|EQUIPAMENTO)$")
    featured_image_url: str | None = Field(default=None, max_length=500)
    video_url: str | None = Field(default=None, max_length=500)


class PostResponse(BaseModel):
    id: int
    author_id: int
    author_name: str
    title: str
    slug: str
    excerpt: str | None = None
    content: str
    content_type: str
    featured_image_url: str | None = None
    video_url: str | None = None
    published_at: datetime | None = None
    created_at: datetime
    likes: int = 0
    comments: int = 0


class CommentCreate(BaseModel):
    content: str = Field(min_length=2, max_length=3000)


class CommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    author_name: str
    content: str
    created_at: datetime


class CatchCreate(BaseModel):
    praia_id: int | None = None
    species_name: str = Field(min_length=2, max_length=120)
    bait: str | None = Field(default=None, max_length=120)
    technique: str | None = Field(default=None, max_length=120)
    weight_kg: float | None = Field(default=None, ge=0, le=500)
    length_cm: float | None = Field(default=None, ge=0, le=1000)
    image_url: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=1000)
    caught_at: datetime
    is_public: bool = True


class CatchResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    praia_id: int | None = None
    beach_name: str | None = None
    species_name: str
    bait: str | None = None
    technique: str | None = None
    weight_kg: float | None = None
    length_cm: float | None = None
    image_url: str | None = None
    notes: str | None = None
    caught_at: datetime
    created_at: datetime
