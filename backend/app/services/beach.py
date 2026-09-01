from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.beach import Beach
from app.models.user import User
from app.repositories.beach import BeachRepository
from app.schemas.beach import BeachCreate, BeachUpdate
from app.utils.slug import slugify


class BeachService:
    def __init__(self, session: Session):
        self.session = session
        self.beaches = BeachRepository(session)

    def create(self, payload: BeachCreate, actor: User) -> Beach:
        beach_slug = payload.slug or slugify(payload.name)
        if not beach_slug:
            raise ConflictError("Não foi possível gerar um slug válido para a praia.")
        if self.beaches.get_by_slug(beach_slug) is not None:
            raise ConflictError("Já existe uma praia com este slug.")

        beach = Beach(
            name=payload.name,
            slug=beach_slug,
            city=payload.city,
            state=payload.state,
            description=payload.description,
            latitude=payload.latitude,
            longitude=payload.longitude,
            sea_bearing_deg=payload.sea_bearing_deg,
            beach_profile=payload.beach_profile,
            accessibility_summary=payload.accessibility_summary,
            is_published=payload.is_published,
            created_by_id=actor.id,
        )
        try:
            self.beaches.add(beach, payload.latitude, payload.longitude)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError(
                "Não foi possível cadastrar a praia com os dados informados."
            ) from exc
        return beach

    def update(self, beach_id: int, payload: BeachUpdate, actor: User) -> Beach:
        beach = self.beaches.get_by_id(beach_id)
        if beach is None:
            raise NotFoundError("Praia não encontrada.")

        changes = payload.model_dump(exclude_unset=True)
        new_slug = changes.get("slug")
        if new_slug:
            existing = self.beaches.get_by_slug(new_slug)
            if existing is not None and existing.id != beach.id:
                raise ConflictError("Já existe uma praia com este slug.")

        coordinates_changed = "latitude" in changes or "longitude" in changes
        for field, value in changes.items():
            setattr(beach, field, value)
        beach.updated_by_id = actor.id
        if coordinates_changed:
            self.beaches.update_location(beach)

        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("Não foi possível atualizar a praia.") from exc
        return beach

    def delete(self, beach_id: int, actor: User) -> None:
        beach = self.beaches.get_by_id(beach_id)
        if beach is None:
            raise NotFoundError("Praia não encontrada.")
        self.beaches.archive(beach, actor_id=actor.id)
        self.session.commit()
