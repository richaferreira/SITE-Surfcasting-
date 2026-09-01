from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.beach import Beach
from app.models.spatial import mysql_point_expression


class BeachRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, beach_id: int) -> Beach | None:
        return self.session.scalar(
            select(Beach).where(Beach.id == beach_id, Beach.deleted_at.is_(None))
        )

    def get_by_slug(self, slug: str, published_only: bool = False) -> Beach | None:
        statement = select(Beach).where(Beach.slug == slug, Beach.deleted_at.is_(None))
        if published_only:
            statement = statement.where(Beach.is_published.is_(True))
        return self.session.scalar(statement)

    def list(self, offset: int, limit: int, published_only: bool) -> tuple[list[Beach], int]:
        filters = [Beach.deleted_at.is_(None)]
        if published_only:
            filters.append(Beach.is_published.is_(True))
        items_statement = (
            select(Beach)
            .where(*filters)
            .order_by(Beach.city, Beach.name)
            .offset(offset)
            .limit(limit)
        )
        count_statement = select(func.count()).select_from(Beach).where(*filters)
        items = list(self.session.scalars(items_statement))
        total = int(self.session.scalar(count_statement) or 0)
        return items, total

    def add(self, beach: Beach, latitude: float, longitude: float) -> Beach:
        beach.location = self._location_expression(latitude, longitude)
        self.session.add(beach)
        self.session.flush()
        return beach

    def update_location(self, beach: Beach) -> None:
        beach.location = self._location_expression(
            float(beach.latitude),
            float(beach.longitude),
        )

    @staticmethod
    def _location_expression(latitude: float, longitude: float):
        return mysql_point_expression(latitude, longitude)

    def archive(self, beach: Beach, actor_id: int) -> None:
        beach.is_published = False
        beach.deleted_at = func.utc_timestamp()
        beach.deleted_by_id = actor_id
