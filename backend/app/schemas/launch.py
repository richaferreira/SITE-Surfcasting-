from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


ReportReason = Literal["SPAM", "ABUSO", "CONTEUDO_IMPROPRIO", "DESINFORMACAO", "OUTRO"]
ReportStatus = Literal["ABERTO", "EM_ANALISE", "RESOLVIDO", "DESCARTADO"]


class ReportCreate(BaseModel):
    post_id: int | None = Field(default=None, ge=1)
    comment_id: int | None = Field(default=None, ge=1)
    reason: ReportReason
    details: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def exactly_one_target(self) -> "ReportCreate":
        if (self.post_id is None) == (self.comment_id is None):
            raise ValueError("Informe exatamente um alvo: post_id ou comment_id.")
        return self


class ReportStatusUpdate(BaseModel):
    status: ReportStatus


class ReportResponse(BaseModel):
    id: int
    reporter_id: int
    post_id: int | None = None
    comment_id: int | None = None
    reason: str
    details: str | None = None
    status: str
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None
    created_at: datetime


class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    message: str
    action_url: str | None = None
    read_at: datetime | None = None
    created_at: datetime


class AnalyticsEventCreate(BaseModel):
    event_name: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_.:-]+$")
    session_id: str | None = Field(default=None, max_length=80)
    page_path: str | None = Field(default=None, max_length=500)
    beach_slug: str | None = Field(default=None, max_length=180)
    metadata: dict[str, Any] | None = None


class AnalyticsSummary(BaseModel):
    total_events: int
    unique_sessions: int
    top_pages: list[dict[str, Any]]
    top_beaches: list[dict[str, Any]]
    top_events: list[dict[str, Any]]


class MediaAssetResponse(BaseModel):
    id: int
    original_name: str
    mime_type: str
    size_bytes: int
    public_url: str
    created_at: datetime
