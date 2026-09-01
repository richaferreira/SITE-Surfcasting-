from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.enums import PostContentType
from app.repositories.post import PostRepository
from app.schemas.post import (
    PublicPostListResponse,
    PublicPostResponse,
    PublicPostSummaryResponse,
)


router = APIRouter(prefix="/academy/posts", tags=["Academia Long Cast"])


@router.get("", response_model=PublicPostListResponse)
def list_published_posts(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 12,
    content_type: PostContentType | None = None,
    query: Annotated[str | None, Query(min_length=2, max_length=100)] = None,
) -> PublicPostListResponse:
    items, total = PostRepository(db).list_public(offset, limit, content_type, query)
    return PublicPostListResponse(
        items=[PublicPostSummaryResponse.model_validate(item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{slug}", response_model=PublicPostResponse)
def get_published_post(
    slug: str,
    db: Annotated[Session, Depends(get_db)],
) -> PublicPostResponse:
    post = PostRepository(db).get_by_slug(slug, published_only=True)
    if post is None:
        raise NotFoundError("Conteúdo não encontrado.")
    return PublicPostResponse.model_validate(post)
