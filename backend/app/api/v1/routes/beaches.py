from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.repositories.beach import BeachRepository
from app.schemas.beach import PublicBeachListResponse, PublicBeachResponse

router = APIRouter(prefix="/beaches", tags=["Praias"])


@router.get("", response_model=PublicBeachListResponse)
def list_published_beaches(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PublicBeachListResponse:
    items, total = BeachRepository(db).list(offset, limit, published_only=True)
    return PublicBeachListResponse(
        items=[PublicBeachResponse.model_validate(item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{slug}", response_model=PublicBeachResponse)
def get_published_beach(
    slug: str,
    db: Annotated[Session, Depends(get_db)],
) -> PublicBeachResponse:
    beach = BeachRepository(db).get_by_slug(slug, published_only=True)
    if beach is None:
        raise NotFoundError("Praia não encontrada.")
    return PublicBeachResponse.model_validate(beach)
