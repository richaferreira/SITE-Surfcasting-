from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.media import MediaAsset


class MediaRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, offset: int, limit: int) -> tuple[list[MediaAsset], int]:
        statement = (
            select(MediaAsset)
            .order_by(MediaAsset.created_at.desc(), MediaAsset.id.desc())
            .offset(offset)
            .limit(limit)
        )
        count_statement = select(func.count()).select_from(MediaAsset)
        return list(self.session.scalars(statement)), int(self.session.scalar(count_statement) or 0)

    def add(self, asset: MediaAsset) -> MediaAsset:
        self.session.add(asset)
        self.session.flush()
        return asset

