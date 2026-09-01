from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.db.session import get_db
from app.models.enums import RoleCode
from app.models.user import User
from app.repositories.beach import BeachRepository
from app.schemas.beach import BeachCreate, BeachListResponse, BeachResponse, BeachUpdate
from app.services.beach import BeachService

router = APIRouter(prefix="/admin/beaches", tags=["Backoffice - Praias"])
admin_dependency = require_roles(RoleCode.ADMIN)


@router.get("", response_model=BeachListResponse)
def list_all_beaches(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> BeachListResponse:
    del admin
    items, total = BeachRepository(db).list(offset, limit, published_only=False)
    return BeachListResponse(
        items=[BeachResponse.model_validate(item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("", response_model=BeachResponse, status_code=status.HTTP_201_CREATED)
def create_beach(
    payload: BeachCreate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> BeachResponse:
    beach = BeachService(db).create(payload, actor=admin)
    return BeachResponse.model_validate(beach)


@router.patch("/{beach_id}", response_model=BeachResponse)
def update_beach(
    beach_id: int,
    payload: BeachUpdate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> BeachResponse:
    beach = BeachService(db).update(beach_id, payload, actor=admin)
    return BeachResponse.model_validate(beach)


@router.delete("/{beach_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_beach(
    beach_id: int,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> Response:
    del admin
    BeachService(db).delete(beach_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
