from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.enums import RoleCode
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import AdminUserUpdate


class UserAdminService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = UserRepository(session)

    def update(self, user_id: int, payload: AdminUserUpdate) -> User:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuário não encontrado.")
        removing_active_admin = (
            user.role.code == RoleCode.ADMIN.value
            and user.is_active
            and (
                payload.role is not None and payload.role is not RoleCode.ADMIN
                or payload.is_active is False
            )
        )
        if removing_active_admin and self.repository.count_active_admins() <= 1:
            raise ConflictError("Não é possível remover ou desativar o último administrador.")
        if payload.role is not None:
            role = self.repository.get_role(payload.role.value)
            if role is None:
                raise NotFoundError("Papel de acesso não encontrado.")
            user.role = role
            user.role_id = role.id
        if payload.is_active is not None:
            user.is_active = payload.is_active
        self.session.commit()
        return user
