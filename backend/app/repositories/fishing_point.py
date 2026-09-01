from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.fishing_point import FishingPoint
from app.models.spatial import mysql_point_expression


class FishingPointRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, point_id: int, active_only: bool = False) -> FishingPoint | None:
        statement = select(FishingPoint).where(FishingPoint.id == point_id)
        if active_only:
            statement = statement.where(FishingPoint.is_active.is_(True))
        return self.session.scalar(statement)

    def get_by_slug(self, beach_id: int, slug: str) -> FishingPoint | None:
        return self.session.scalar(
            select(FishingPoint).where(
                FishingPoint.beach_id == beach_id,
                FishingPoint.slug == slug,
            )
        )

    def list_by_beach(
        self,
        beach_id: int,
        *,
        active_only: bool,
    ) -> tuple[list[FishingPoint], int]:
        filters = [FishingPoint.beach_id == beach_id]
        if active_only:
            filters.append(FishingPoint.is_active.is_(True))
        statement = (
            select(FishingPoint)
            .where(*filters)
            .order_by(FishingPoint.point_type, FishingPoint.name)
        )
        count_statement = select(func.count()).select_from(FishingPoint).where(*filters)
        return list(self.session.scalars(statement)), int(self.session.scalar(count_statement) or 0)

    def add(self, point: FishingPoint) -> FishingPoint:
        point.location = mysql_point_expression(float(point.latitude), float(point.longitude))
        self.session.add(point)
        self.session.flush()
        return point

    def update_location(self, point: FishingPoint) -> None:
        point.location = mysql_point_expression(float(point.latitude), float(point.longitude))

