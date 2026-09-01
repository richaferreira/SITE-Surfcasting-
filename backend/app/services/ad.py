from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.ad import AdCampaign
from app.models.user import User
from app.repositories.ad import AdRepository
from app.schemas.ad import AdCampaignInput, AdCampaignUpdate


def _utc_naive(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


class AdService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = AdRepository(session)

    def create(self, payload: AdCampaignInput, actor: User) -> AdCampaign:
        campaign = AdCampaign(
            **payload.model_dump(exclude={"starts_at", "ends_at"}),
            starts_at=_utc_naive(payload.starts_at),
            ends_at=_utc_naive(payload.ends_at),
            created_by_id=actor.id,
        )
        self.repository.add(campaign)
        self.session.commit()
        return campaign

    def update(self, campaign_id: int, payload: AdCampaignUpdate) -> AdCampaign:
        campaign = self.repository.get(campaign_id)
        if campaign is None:
            raise NotFoundError("Campanha não encontrada.")
        current = {
            "name": campaign.name,
            "placement": campaign.placement,
            "title": campaign.title,
            "image_url": campaign.image_url,
            "target_url": campaign.target_url,
            "alt_text": campaign.alt_text,
            "starts_at": campaign.starts_at,
            "ends_at": campaign.ends_at,
            "is_active": campaign.is_active,
        }
        current.update(payload.model_dump(exclude_unset=True))
        try:
            validated = AdCampaignInput.model_validate(current)
        except ValueError as exc:
            raise ConflictError(str(exc)) from exc
        for field, value in validated.model_dump(exclude={"starts_at", "ends_at"}).items():
            setattr(campaign, field, value)
        campaign.starts_at = _utc_naive(validated.starts_at)
        campaign.ends_at = _utc_naive(validated.ends_at)
        self.session.commit()
        return campaign

    def archive(self, campaign_id: int) -> None:
        campaign = self.repository.get(campaign_id)
        if campaign is None:
            raise NotFoundError("Campanha não encontrada.")
        campaign.is_active = False
        self.session.commit()
