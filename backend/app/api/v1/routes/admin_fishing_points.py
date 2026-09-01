from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.enums import RoleCode
from app.models.user import User
from app.repositories.beach import BeachRepository
from app.repositories.fishing_point import FishingPointRepository
from app.schemas.fishing_point import (
    FishingPointCreate,
    FishingPointListResponse,
    FishingPointResponse,
    FishingPointUpdate,
)
from app.services.fishing_point import FishingPointService


router = APIRouter(prefix="/admin", tags=["Backoffice - Pontos de Pesca"])
admin_dependency = require_roles(RoleCode.ADMIN)


@router.get("/beaches/{beach_id}/points", response_model=FishingPointListResponse)
def list_all_fishing_points(
    beach_id: int,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> FishingPointListResponse:
    del admin
    if BeachRepository(db).get_by_id(beach_id) is None:
        raise NotFoundError("Praia não encontrada.")
    items, total = FishingPointRepository(db).list_by_beach(beach_id, active_only=False)
    return FishingPointListResponse(
        items=[FishingPointResponse.model_validate(item) for item in items],
        total=total,
    )


@router.post(
    "/beaches/{beach_id}/points",
    response_model=FishingPointResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_fishing_point(
    beach_id: int,
    payload: FishingPointCreate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> FishingPointResponse:
    point = FishingPointService(db).create(beach_id, payload, actor=admin)
    return FishingPointResponse.model_validate(point)


@router.patch("/points/{point_id}", response_model=FishingPointResponse)
def update_fishing_point(
    point_id: int,
    payload: FishingPointUpdate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> FishingPointResponse:
    del admin
    point = FishingPointService(db).update(point_id, payload)
    return FishingPointResponse.model_validate(point)


@router.delete("/points/{point_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_fishing_point(
    point_id: int,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> Response:
    del admin
    FishingPointService(db).archive(point_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
