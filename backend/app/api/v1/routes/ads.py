from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import AdPlacement
from app.repositories.ad import AdRepository
from app.schemas.ad import PublicAdListResponse, PublicAdResponse


router = APIRouter(prefix="/ads", tags=["Anúncios"])


@router.get("", response_model=PublicAdListResponse)
def list_active_ads(
    db: Annotated[Session, Depends(get_db)],
    placement: AdPlacement | None = None,
) -> PublicAdListResponse:
    items = AdRepository(db).list_public(placement)
    return PublicAdListResponse(items=[PublicAdResponse.model_validate(item) for item in items])
