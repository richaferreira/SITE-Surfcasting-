from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.db.session import get_db
from app.models.enums import RoleCode
from app.models.user import User
from app.repositories.post import PostRepository
from app.schemas.post import PostCreate, PostListResponse, PostResponse, PostUpdate
from app.services.post import PostService


router = APIRouter(prefix="/admin/posts", tags=["Backoffice - Academia"])
editor_dependency = require_roles(RoleCode.ADMIN, RoleCode.AUTHOR)


@router.get("", response_model=PostListResponse)
def list_managed_posts(
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[User, Depends(editor_dependency)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PostListResponse:
    author_id = None if actor.role.code == RoleCode.ADMIN.value else actor.id
    items, total = PostRepository(db).list_admin(offset, limit, author_id)
    return PostListResponse(
        items=[PostResponse.model_validate(item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[User, Depends(editor_dependency)],
) -> PostResponse:
    post = PostService(db).create(payload, actor=actor)
    return PostResponse.model_validate(post)


@router.patch("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[User, Depends(editor_dependency)],
) -> PostResponse:
    post = PostService(db).update(post_id, payload, actor=actor)
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_post(
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
    actor: Annotated[User, Depends(editor_dependency)],
) -> Response:
    PostService(db).archive(post_id, actor=actor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

