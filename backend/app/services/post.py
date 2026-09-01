from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError
from app.models.enums import PostContentType, PostStatus, RoleCode
from app.models.post import EquipmentSpecification, Post
from app.models.user import User
from app.repositories.post import PostRepository
from app.schemas.post import EquipmentSpecificationInput, PostCreate, PostUpdate
from app.utils.slug import slugify


class PostService:
    def __init__(self, session: Session):
        self.session = session
        self.posts = PostRepository(session)

    @staticmethod
    def _is_admin(actor: User) -> bool:
        return actor.role.code == RoleCode.ADMIN.value

    def _assert_can_publish(self, actor: User, status: PostStatus) -> None:
        if status is PostStatus.PUBLICADO and not self._is_admin(actor):
            raise AuthorizationError("Somente administradores podem publicar conteúdo.")

    def _assert_can_manage(self, actor: User, post: Post) -> None:
        if not self._is_admin(actor) and post.author_id != actor.id:
            raise AuthorizationError("Autores só podem gerenciar o próprio conteúdo.")

    @staticmethod
    def _equipment_model(payload: EquipmentSpecificationInput) -> EquipmentSpecification:
        return EquipmentSpecification(**payload.model_dump())

    def create(self, payload: PostCreate, actor: User) -> Post:
        self._assert_can_publish(actor, payload.status)
        post_slug = payload.slug or slugify(payload.title)
        if not post_slug:
            raise ConflictError("Não foi possível gerar um slug válido para o conteúdo.")
        if self.posts.get_by_slug(post_slug) is not None:
            raise ConflictError("Já existe um conteúdo com este slug.")

        post = Post(
            author_id=actor.id,
            title=payload.title,
            slug=post_slug,
            excerpt=payload.excerpt,
            content=payload.content,
            content_type=payload.content_type,
            status=payload.status,
            featured_image_url=payload.featured_image_url,
            video_url=payload.video_url,
            seo_title=payload.seo_title,
            seo_description=payload.seo_description,
            published_at=(
                datetime.now(timezone.utc).replace(tzinfo=None)
                if payload.status is PostStatus.PUBLICADO
                else None
            ),
        )
        if payload.equipment_specification is not None:
            post.equipment_specification = self._equipment_model(payload.equipment_specification)
        try:
            self.posts.add(post)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("Não foi possível cadastrar o conteúdo.") from exc
        return self.posts.get_by_id(post.id) or post

    def update(self, post_id: int, payload: PostUpdate, actor: User) -> Post:
        post = self.posts.get_by_id(post_id)
        if post is None:
            raise NotFoundError("Conteúdo não encontrado.")
        self._assert_can_manage(actor, post)
        changes = payload.model_dump(exclude_unset=True, exclude={"equipment_specification"})
        requested_status = changes.get("status", post.status)
        self._assert_can_publish(actor, requested_status)
        new_slug = changes.get("slug")
        if new_slug:
            existing = self.posts.get_by_slug(new_slug)
            if existing is not None and existing.id != post.id:
                raise ConflictError("Já existe um conteúdo com este slug.")
        for field, value in changes.items():
            setattr(post, field, value)
        if requested_status is PostStatus.PUBLICADO and post.published_at is None:
            post.published_at = datetime.now(timezone.utc).replace(tzinfo=None)
        elif requested_status is not PostStatus.PUBLICADO:
            post.published_at = None

        if "equipment_specification" in payload.model_fields_set:
            equipment = payload.equipment_specification
            if equipment is not None and post.content_type is not PostContentType.EQUIPAMENTO:
                raise ConflictError(
                    "Ficha técnica só pode ser usada em conteúdo de equipamento."
                )
            post.equipment_specification = (
                self._equipment_model(equipment) if equipment is not None else None
            )
        elif post.content_type is not PostContentType.EQUIPAMENTO:
            post.equipment_specification = None
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("Não foi possível atualizar o conteúdo.") from exc
        return self.posts.get_by_id(post.id) or post

    def archive(self, post_id: int, actor: User) -> None:
        post = self.posts.get_by_id(post_id)
        if post is None:
            raise NotFoundError("Conteúdo não encontrado.")
        self._assert_can_manage(actor, post)
        post.status = PostStatus.ARQUIVADO
        post.published_at = None
        self.session.commit()
