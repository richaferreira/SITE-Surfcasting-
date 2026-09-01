from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.community import CommunityComment, CommunityThread
from app.models.enums import CommunityCategory, CommunityStatus


class CommunityAuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    username: str
    avatar_url: str | None


class CommunityBeachResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    slug: str


class CommunityThreadCreate(BaseModel):
    title: str = Field(min_length=5, max_length=160)
    content: str = Field(min_length=10, max_length=5000)
    category: CommunityCategory
    beach_id: int | None = Field(default=None, gt=0)
    media_url: str | None = Field(default=None, max_length=500)

    @field_validator("title", "content", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("media_url")
    @classmethod
    def validate_media_url(cls, value: str | None) -> str | None:
        if value and not (value.startswith("/media/") or value.startswith("https://")):
            raise ValueError("A mídia deve usar HTTPS ou um arquivo do Gestor de Mídia.")
        return value


class CommunityCommentCreate(BaseModel):
    content: str = Field(min_length=2, max_length=2000)

    @field_validator("content", mode="before")
    @classmethod
    def strip_content(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class CommunityCommentResponse(BaseModel):
    id: int
    content: str
    author: CommunityAuthorResponse
    created_at: datetime

    @classmethod
    def from_model(cls, comment: CommunityComment) -> "CommunityCommentResponse":
        return cls(
            id=comment.id,
            content=comment.content,
            author=CommunityAuthorResponse.model_validate(comment.author),
            created_at=comment.created_at,
        )


class CommunityThreadSummaryResponse(BaseModel):
    id: int
    title: str
    content: str
    category: CommunityCategory
    media_url: str | None
    author: CommunityAuthorResponse
    beach: CommunityBeachResponse | None
    comment_count: int
    reaction_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, thread: CommunityThread) -> "CommunityThreadSummaryResponse":
        return cls(
            id=thread.id,
            title=thread.title,
            content=thread.content,
            category=thread.category,
            media_url=thread.media_url,
            author=CommunityAuthorResponse.model_validate(thread.author),
            beach=(CommunityBeachResponse.model_validate(thread.beach) if thread.beach else None),
            comment_count=sum(not comment.is_hidden for comment in thread.comments),
            reaction_count=len(thread.reactions),
            created_at=thread.created_at,
            updated_at=thread.updated_at,
        )


class CommunityThreadDetailResponse(CommunityThreadSummaryResponse):
    comments: list[CommunityCommentResponse]

    @classmethod
    def from_model(cls, thread: CommunityThread) -> "CommunityThreadDetailResponse":
        summary = CommunityThreadSummaryResponse.from_model(thread)
        return cls(
            **summary.model_dump(),
            comments=[
                CommunityCommentResponse.from_model(comment)
                for comment in thread.comments
                if not comment.is_hidden
            ],
        )


class CommunityThreadListResponse(BaseModel):
    items: list[CommunityThreadSummaryResponse]
    total: int
    offset: int
    limit: int


class CommunityManagedThreadResponse(CommunityThreadSummaryResponse):
    status: CommunityStatus

    @classmethod
    def from_model(cls, thread: CommunityThread) -> "CommunityManagedThreadResponse":
        summary = CommunityThreadSummaryResponse.from_model(thread)
        return cls(**summary.model_dump(), status=thread.status)


class CommunityManagedThreadListResponse(BaseModel):
    items: list[CommunityManagedThreadResponse]
    total: int
    offset: int
    limit: int


class CommunityReactionResponse(BaseModel):
    reacted: bool
    reaction_count: int


class CommunityModerationUpdate(BaseModel):
    status: CommunityStatus


class CommentModerationUpdate(BaseModel):
    is_hidden: bool
