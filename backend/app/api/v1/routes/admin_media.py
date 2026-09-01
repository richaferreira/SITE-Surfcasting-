from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.enums import RoleCode
from app.models.user import User
from app.repositories.media import MediaRepository
from app.schemas.media import MediaAssetListResponse, MediaAssetResponse
from app.services.media import MediaService


router = APIRouter(prefix="/admin/media", tags=["Backoffice - Mídia"])
editor_dependency = require_roles(RoleCode.ADMIN, RoleCode.AUTHOR)


@router.get("", response_model=MediaAssetListResponse)
def list_media_assets(
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[User, Depends(editor_dependency)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> MediaAssetListResponse:
    del actor
    items, total = MediaRepository(db).list(offset, limit)
    return MediaAssetListResponse(
        items=[MediaAssetResponse.model_validate(item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("", response_model=MediaAssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_media_asset(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    actor: Annotated[User, Depends(editor_dependency)],
) -> MediaAssetResponse:
    asset = await MediaService(db, settings).save(file, actor=actor)
    return MediaAssetResponse.model_validate(asset)

