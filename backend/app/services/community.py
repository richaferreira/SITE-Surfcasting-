from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AuthorizationError, ConflictError, NotFoundError
from app.models.community import CommunityComment, CommunityReaction, CommunityThread
from app.models.enums import CommunityStatus, RoleCode
from app.models.user import User
from app.repositories.beach import BeachRepository
from app.repositories.community import CommunityRepository
from app.schemas.community import CommunityCommentCreate, CommunityThreadCreate


class CommunityService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = CommunityRepository(session)
        self.beaches = BeachRepository(session)

    def create_thread(self, payload: CommunityThreadCreate, actor: User) -> CommunityThread:
        if payload.beach_id is not None and self.beaches.get_by_id(payload.beach_id) is None:
            raise NotFoundError("Praia não encontrada.")
        thread = CommunityThread(
            author_id=actor.id,
            beach_id=payload.beach_id,
            title=payload.title,
            content=payload.content,
            category=payload.category,
            status=CommunityStatus.PUBLICADO,
            media_url=payload.media_url,
        )
        try:
            self.repository.add_thread(thread)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("Não foi possível criar a discussão.") from exc
        return self.repository.get_thread(thread.id) or thread

    def add_comment(
        self,
        thread_id: int,
        payload: CommunityCommentCreate,
        actor: User,
    ) -> CommunityComment:
        if self.repository.get_thread(thread_id, public_only=True) is None:
            raise NotFoundError("Discussão não encontrada.")
        comment = CommunityComment(
            thread_id=thread_id,
            author_id=actor.id,
            content=payload.content,
            is_hidden=False,
        )
        self.repository.add_comment(comment)
        self.session.commit()
        return comment

    def set_reaction(self, thread_id: int, actor: User, reacted: bool) -> tuple[bool, int]:
        if self.repository.get_thread(thread_id, public_only=True) is None:
            raise NotFoundError("Discussão não encontrada.")
        existing = self.repository.get_reaction(thread_id, actor.id)
        if reacted and existing is None:
            self.session.add(CommunityReaction(thread_id=thread_id, user_id=actor.id))
        elif not reacted and existing is not None:
            self.session.delete(existing)
        self.session.commit()
        return reacted, self.repository.reaction_count(thread_id)

    def archive_own_thread(self, thread_id: int, actor: User) -> None:
        thread = self.repository.get_thread(thread_id)
        if thread is None:
            raise NotFoundError("Discussão não encontrada.")
        is_admin = actor.role.code == RoleCode.ADMIN.value
        if not is_admin and thread.author_id != actor.id:
            raise AuthorizationError("Você só pode arquivar suas próprias discussões.")
        thread.status = CommunityStatus.ARQUIVADO
        self.session.commit()

    def moderate_thread(self, thread_id: int, status: CommunityStatus) -> CommunityThread:
        thread = self.repository.get_thread(thread_id)
        if thread is None:
            raise NotFoundError("Discussão não encontrada.")
        thread.status = status
        self.session.commit()
        return self.repository.get_thread(thread.id) or thread

    def moderate_comment(self, comment_id: int, is_hidden: bool) -> CommunityComment:
        comment = self.repository.get_comment(comment_id)
        if comment is None:
            raise NotFoundError("Comentário não encontrado.")
        comment.is_hidden = is_hidden
        self.session.commit()
        return comment
