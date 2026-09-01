from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rate_limit import enforce_community_rate_limit
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.enums import CommunityCategory
from app.models.user import User
from app.repositories.community import CommunityRepository
from app.schemas.community import (
    CommunityCommentCreate,
    CommunityCommentResponse,
    CommunityReactionResponse,
    CommunityThreadCreate,
    CommunityThreadDetailResponse,
    CommunityThreadListResponse,
    CommunityThreadSummaryResponse,
)
from app.services.community import CommunityService


router = APIRouter(prefix="/community", tags=["Comunidade"])


@router.get("/threads", response_model=CommunityThreadListResponse)
def list_threads(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    category: CommunityCategory | None = None,
    beach_id: Annotated[int | None, Query(gt=0)] = None,
    query: Annotated[str | None, Query(min_length=2, max_length=100)] = None,
) -> CommunityThreadListResponse:
    items, total = CommunityRepository(db).list_threads(offset, limit, category, beach_id, query)
    return CommunityThreadListResponse(
        items=[CommunityThreadSummaryResponse.from_model(item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/threads/{thread_id}", response_model=CommunityThreadDetailResponse)
def get_thread(
    thread_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> CommunityThreadDetailResponse:
    thread = CommunityRepository(db).get_thread(thread_id, public_only=True)
    if thread is None:
        raise NotFoundError("Discussão não encontrada.")
    return CommunityThreadDetailResponse.from_model(thread)


@router.post(
    "/threads",
    response_model=CommunityThreadSummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_thread(
    payload: CommunityThreadCreate,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[User, Depends(get_current_user)],
    rate_limit: Annotated[None, Depends(enforce_community_rate_limit)],
) -> CommunityThreadSummaryResponse:
    del rate_limit
    return CommunityThreadSummaryResponse.from_model(
        CommunityService(db).create_thread(payload, actor)
    )


@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommunityCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    thread_id: int,
    payload: CommunityCommentCreate,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[User, Depends(get_current_user)],
    rate_limit: Annotated[None, Depends(enforce_community_rate_limit)],
) -> CommunityCommentResponse:
    del rate_limit
    return CommunityCommentResponse.from_model(
        CommunityService(db).add_comment(thread_id, payload, actor)
    )


@router.post("/threads/{thread_id}/reactions", response_model=CommunityReactionResponse)
def react(
    thread_id: int,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[User, Depends(get_current_user)],
    rate_limit: Annotated[None, Depends(enforce_community_rate_limit)],
) -> CommunityReactionResponse:
    del rate_limit
    reacted, count = CommunityService(db).set_reaction(thread_id, actor, True)
    return CommunityReactionResponse(reacted=reacted, reaction_count=count)


@router.delete("/threads/{thread_id}/reactions", response_model=CommunityReactionResponse)
def remove_reaction(
    thread_id: int,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[User, Depends(get_current_user)],
    rate_limit: Annotated[None, Depends(enforce_community_rate_limit)],
) -> CommunityReactionResponse:
    del rate_limit
    reacted, count = CommunityService(db).set_reaction(thread_id, actor, False)
    return CommunityReactionResponse(reacted=reacted, reaction_count=count)


@router.delete("/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_thread(
    thread_id: int,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[User, Depends(get_current_user)],
) -> Response:
    CommunityService(db).archive_own_thread(thread_id, actor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
