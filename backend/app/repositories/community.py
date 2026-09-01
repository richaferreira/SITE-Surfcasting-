from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.community import CommunityComment, CommunityReaction, CommunityThread
from app.models.enums import CommunityCategory, CommunityStatus


class CommunityRepository:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _with_relations():
        return select(CommunityThread).options(
            selectinload(CommunityThread.author),
            selectinload(CommunityThread.beach),
            selectinload(CommunityThread.comments).selectinload(CommunityComment.author),
            selectinload(CommunityThread.reactions),
        )

    def get_thread(self, thread_id: int, public_only: bool = False) -> CommunityThread | None:
        statement = self._with_relations().where(CommunityThread.id == thread_id)
        if public_only:
            statement = statement.where(CommunityThread.status == CommunityStatus.PUBLICADO)
        return self.session.scalar(statement)

    def list_threads(
        self,
        offset: int,
        limit: int,
        category: CommunityCategory | None,
        beach_id: int | None,
        query: str | None,
        include_moderated: bool = False,
    ) -> tuple[list[CommunityThread], int]:
        filters = [] if include_moderated else [CommunityThread.status == CommunityStatus.PUBLICADO]
        if category is not None:
            filters.append(CommunityThread.category == category)
        if beach_id is not None:
            filters.append(CommunityThread.beach_id == beach_id)
        if query:
            pattern = f"%{query.strip()}%"
            filters.append(
                or_(
                    CommunityThread.title.like(pattern),
                    CommunityThread.content.like(pattern),
                )
            )
        statement = (
            self._with_relations()
            .where(*filters)
            .order_by(CommunityThread.updated_at.desc(), CommunityThread.id.desc())
            .offset(offset)
            .limit(limit)
        )
        count = select(func.count()).select_from(CommunityThread).where(*filters)
        return list(self.session.scalars(statement)), int(self.session.scalar(count) or 0)

    def add_thread(self, thread: CommunityThread) -> CommunityThread:
        self.session.add(thread)
        self.session.flush()
        return thread

    def add_comment(self, comment: CommunityComment) -> CommunityComment:
        self.session.add(comment)
        self.session.flush()
        return comment

    def get_comment(self, comment_id: int) -> CommunityComment | None:
        return self.session.get(CommunityComment, comment_id)

    def get_reaction(self, thread_id: int, user_id: int) -> CommunityReaction | None:
        return self.session.get(CommunityReaction, (thread_id, user_id))

    def reaction_count(self, thread_id: int) -> int:
        statement = select(func.count()).select_from(CommunityReaction).where(
            CommunityReaction.thread_id == thread_id
        )
        return int(self.session.scalar(statement) or 0)
