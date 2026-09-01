from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.beach import Beach


class BeachRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, beach_id: int) -> Beach | None:
        return self.session.get(Beach, beach_id)

    def get_by_slug(self, slug: str, published_only: bool = False) -> Beach | None:
        statement = select(Beach).where(Beach.slug == slug)
        if published_only:
            statement = statement.where(Beach.is_published.is_(True))
        return self.session.scalar(statement)

    def list(self, offset: int, limit: int, published_only: bool) -> tuple[list[Beach], int]:
        filters = [Beach.is_published.is_(True)] if published_only else []
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
        beach.location = func.ST_SRID(func.POINT(longitude, latitude), 4326)
        self.session.add(beach)
        self.session.flush()
        return beach

    def update_location(self, beach: Beach) -> None:
        beach.location = func.ST_SRID(
            func.POINT(float(beach.longitude), float(beach.latitude)),
            4326,
        )

    def delete(self, beach: Beach) -> None:
        self.session.delete(beach)
