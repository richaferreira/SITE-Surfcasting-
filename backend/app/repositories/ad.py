from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.ad import AdCampaign
from app.models.enums import AdPlacement


class AdRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, campaign_id: int) -> AdCampaign | None:
        return self.session.get(AdCampaign, campaign_id)

    def list_admin(self) -> tuple[list[AdCampaign], int]:
        statement = select(AdCampaign).order_by(AdCampaign.created_at.desc())
        return list(self.session.scalars(statement)), int(
            self.session.scalar(select(func.count()).select_from(AdCampaign)) or 0
        )

    def list_public(self, placement: AdPlacement | None) -> list[AdCampaign]:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        filters = [
            AdCampaign.is_active.is_(True),
            AdCampaign.starts_at <= now,
            AdCampaign.ends_at > now,
        ]
        if placement is not None:
            filters.append(AdCampaign.placement == placement)
        return list(
            self.session.scalars(
                select(AdCampaign).where(*filters).order_by(AdCampaign.created_at.desc())
            )
        )

    def add(self, campaign: AdCampaign) -> AdCampaign:
        self.session.add(campaign)
        self.session.flush()
        return campaign
