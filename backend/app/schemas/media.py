from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import MediaKind


class MediaAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: MediaKind
    original_name: str
    mime_type: str
    url: str
    original_size_bytes: int
    size_bytes: int
    width: int | None
    height: int | None
    duration_seconds: int | None
    uploaded_by_id: int
    created_at: datetime


class MediaAssetListResponse(BaseModel):
    items: list[MediaAssetResponse]
    total: int
    offset: int
    limit: int
