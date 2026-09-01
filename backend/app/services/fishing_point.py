from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.fishing_point import FishingPoint
from app.models.user import User
from app.repositories.beach import BeachRepository
from app.repositories.fishing_point import FishingPointRepository
from app.schemas.fishing_point import FishingPointCreate, FishingPointUpdate
from app.utils.slug import slugify


class FishingPointService:
    def __init__(self, session: Session):
        self.session = session
        self.beaches = BeachRepository(session)
        self.points = FishingPointRepository(session)

    def create(self, beach_id: int, payload: FishingPointCreate, actor: User) -> FishingPoint:
        if self.beaches.get_by_id(beach_id) is None:
            raise NotFoundError("Praia não encontrada.")
        point_slug = payload.slug or slugify(payload.name)
        if not point_slug:
            raise ConflictError("Não foi possível gerar um slug válido para o ponto.")
        if self.points.get_by_slug(beach_id, point_slug) is not None:
            raise ConflictError("Já existe um ponto com este slug nesta praia.")

        point = FishingPoint(
            beach_id=beach_id,
            name=payload.name,
            slug=point_slug,
            point_type=payload.point_type,
            description=payload.description,
            latitude=payload.latitude,
            longitude=payload.longitude,
            accessibility=payload.accessibility,
            access_notes=payload.access_notes,
            risk_notes=payload.risk_notes,
            verified_at=payload.verified_at,
            is_active=payload.is_active,
            created_by_id=actor.id,
        )
        try:
            self.points.add(point)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("Não foi possível cadastrar o ponto de pesca.") from exc
        return point

    def update(
        self,
        point_id: int,
        payload: FishingPointUpdate,
    ) -> FishingPoint:
        point = self.points.get_by_id(point_id)
        if point is None:
            raise NotFoundError("Ponto de pesca não encontrado.")
        changes = payload.model_dump(exclude_unset=True)
        new_slug = changes.get("slug")
        if new_slug:
            existing = self.points.get_by_slug(point.beach_id, new_slug)
            if existing is not None and existing.id != point.id:
                raise ConflictError("Já existe um ponto com este slug nesta praia.")
        coordinates_changed = "latitude" in changes or "longitude" in changes
        for field, value in changes.items():
            setattr(point, field, value)
        if coordinates_changed:
            self.points.update_location(point)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("Não foi possível atualizar o ponto de pesca.") from exc
        return point

    def archive(self, point_id: int) -> None:
        point = self.points.get_by_id(point_id)
        if point is None:
            raise NotFoundError("Ponto de pesca não encontrado.")
        point.is_active = False
        self.session.commit()

