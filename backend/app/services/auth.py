from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import DUMMY_PASSWORD_HASH, hash_password, verify_password
from app.models.enums import RoleCode
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import UserRegistration


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)

    def register(self, payload: UserRegistration) -> User:
        email = str(payload.email).lower()
        if self.users.get_by_email(email) is not None:
            raise ConflictError("Este e-mail já está cadastrado.")
        if self.users.get_by_username(payload.username) is not None:
            raise ConflictError("Este nome de usuário já está em uso.")

        role = self.users.get_role(RoleCode.USER.value)
        if role is None:
            raise RuntimeError(
                "A role USER não foi encontrada. Execute o schema inicial do banco."
            )

        user = User(
            role_id=role.id,
            name=payload.name,
            username=payload.username,
            email=email,
            password_hash=hash_password(payload.password),
            is_active=True,
        )
        try:
            self.users.add(user)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("E-mail ou nome de usuário já cadastrado.") from exc
        return user

    def authenticate(self, login: str, password: str) -> User:
        user = self.users.get_by_login(login)
        if user is None:
            verify_password(password, DUMMY_PASSWORD_HASH)
            raise AuthenticationError("Usuário/e-mail ou senha inválidos.")
        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Usuário/e-mail ou senha inválidos.")
        if not user.is_active:
            raise AuthenticationError("Este usuário está inativo.")

        user.record_login()
        self.session.commit()
        return user
