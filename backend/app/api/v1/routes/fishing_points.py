from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.repositories.beach import BeachRepository
from app.repositories.fishing_point import FishingPointRepository
from app.schemas.fishing_point import (
    PublicFishingPointListResponse,
    PublicFishingPointResponse,
)


router = APIRouter(prefix="/beaches", tags=["Mapa de Pesca"])


@router.get("/{beach_slug}/points", response_model=PublicFishingPointListResponse)
def list_public_fishing_points(
    beach_slug: str,
    db: Annotated[Session, Depends(get_db)],
) -> PublicFishingPointListResponse:
    beach = BeachRepository(db).get_by_slug(beach_slug, published_only=True)
    if beach is None:
        raise NotFoundError("Praia não encontrada.")
    items, total = FishingPointRepository(db).list_by_beach(beach.id, active_only=True)
    return PublicFishingPointListResponse(
        items=[PublicFishingPointResponse.model_validate(item) for item in items],
        total=total,
    )

