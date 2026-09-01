from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.db.session import get_db
from app.models.enums import CommunityStatus, RoleCode
from app.models.user import User
from app.repositories.community import CommunityRepository
from app.schemas.community import (
    CommentModerationUpdate,
    CommunityModerationUpdate,
    CommunityThreadDetailResponse,
    CommunityManagedThreadListResponse,
    CommunityManagedThreadResponse,
    CommunityThreadSummaryResponse,
)
from app.services.community import CommunityService


router = APIRouter(prefix="/admin/community", tags=["Backoffice - Comunidade"])
admin_dependency = require_roles(RoleCode.ADMIN)


@router.get("/threads", response_model=CommunityManagedThreadListResponse)
def list_all_threads(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> CommunityManagedThreadListResponse:
    del admin
    items, total = CommunityRepository(db).list_threads(
        offset, limit, None, None, None, include_moderated=True
    )
    return CommunityManagedThreadListResponse(
        items=[CommunityManagedThreadResponse.from_model(item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.patch("/threads/{thread_id}", response_model=CommunityThreadDetailResponse)
def moderate_thread(
    thread_id: int,
    payload: CommunityModerationUpdate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> CommunityThreadDetailResponse:
    del admin
    thread = CommunityService(db).moderate_thread(thread_id, payload.status)
    return CommunityThreadDetailResponse.from_model(thread)


@router.patch("/comments/{comment_id}")
def moderate_comment(
    comment_id: int,
    payload: CommentModerationUpdate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> dict[str, bool | int]:
    del admin
    comment = CommunityService(db).moderate_comment(comment_id, payload.is_hidden)
    return {"id": comment.id, "is_hidden": comment.is_hidden}
