from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.db.session import get_db
from app.models.enums import RoleCode
from app.models.user import User
from app.repositories.ad import AdRepository
from app.schemas.ad import (
    AdCampaignInput,
    AdCampaignListResponse,
    AdCampaignResponse,
    AdCampaignUpdate,
)
from app.services.ad import AdService


router = APIRouter(prefix="/admin/ads", tags=["Backoffice - Anúncios"])
admin_dependency = require_roles(RoleCode.ADMIN)


@router.get("", response_model=AdCampaignListResponse)
def list_campaigns(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> AdCampaignListResponse:
    del admin
    items, total = AdRepository(db).list_admin()
    return AdCampaignListResponse(
        items=[AdCampaignResponse.model_validate(item) for item in items], total=total
    )


@router.post("", response_model=AdCampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    payload: AdCampaignInput,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> AdCampaignResponse:
    return AdCampaignResponse.model_validate(AdService(db).create(payload, admin))


@router.patch("/{campaign_id}", response_model=AdCampaignResponse)
def update_campaign(
    campaign_id: int,
    payload: AdCampaignUpdate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> AdCampaignResponse:
    del admin
    return AdCampaignResponse.model_validate(AdService(db).update(campaign_id, payload))


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_campaign(
    campaign_id: int,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(admin_dependency)],
) -> Response:
    del admin
    AdService(db).archive(campaign_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
