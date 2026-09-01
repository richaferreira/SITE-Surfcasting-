from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import PostContentType, PostStatus
from app.models.post import Post


class PostRepository:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _with_relations():
        return select(Post).options(
            selectinload(Post.author),
            selectinload(Post.equipment_specification),
        )

    def get_by_id(self, post_id: int) -> Post | None:
        return self.session.scalar(self._with_relations().where(Post.id == post_id))

    def get_by_slug(self, slug: str, published_only: bool = False) -> Post | None:
        statement = self._with_relations().where(Post.slug == slug)
        if published_only:
            statement = statement.where(
                Post.status == PostStatus.PUBLICADO,
                Post.published_at.is_not(None),
                Post.published_at <= func.utc_timestamp(),
            )
        return self.session.scalar(statement)

    def list_public(
        self,
        offset: int,
        limit: int,
        content_type: PostContentType | None,
        query: str | None,
    ) -> tuple[list[Post], int]:
        filters = [
            Post.status == PostStatus.PUBLICADO,
            Post.published_at.is_not(None),
            Post.published_at <= func.utc_timestamp(),
        ]
        if content_type is not None:
            filters.append(Post.content_type == content_type)
        if query:
            pattern = f"%{query.strip()}%"
            filters.append(or_(Post.title.like(pattern), Post.excerpt.like(pattern)))
        statement = (
            self._with_relations()
            .where(*filters)
            .order_by(Post.published_at.desc(), Post.id.desc())
            .offset(offset)
            .limit(limit)
        )
        count_statement = select(func.count()).select_from(Post).where(*filters)
        return list(self.session.scalars(statement)), int(self.session.scalar(count_statement) or 0)

    def list_admin(
        self,
        offset: int,
        limit: int,
        author_id: int | None,
    ) -> tuple[list[Post], int]:
        filters = [Post.author_id == author_id] if author_id is not None else []
        statement = (
            self._with_relations()
            .where(*filters)
            .order_by(Post.updated_at.desc(), Post.id.desc())
            .offset(offset)
            .limit(limit)
        )
        count_statement = select(func.count()).select_from(Post).where(*filters)
        return list(self.session.scalars(statement)), int(self.session.scalar(count_statement) or 0)

    def add(self, post: Post) -> Post:
        self.session.add(post)
        self.session.flush()
        return post

