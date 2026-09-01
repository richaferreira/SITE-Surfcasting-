from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email.lower())
        return self.session.scalar(statement)

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username.lower())
        return self.session.scalar(statement)

    def get_by_login(self, login: str) -> User | None:
        normalized = login.strip().lower()
        statement = select(User).where(
            or_(User.email == normalized, User.username == normalized)
        )
        return self.session.scalar(statement)

    def get_role(self, code: str) -> Role | None:
        return self.session.scalar(select(Role).where(Role.code == code))

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def list(self, offset: int, limit: int) -> tuple[list[User], int]:
        statement = (
            select(User)
            .order_by(User.created_at.desc(), User.id.desc())
            .offset(offset)
            .limit(limit)
        )
        count = select(func.count()).select_from(User)
        return list(self.session.scalars(statement)), int(self.session.scalar(count) or 0)

    def count_active_admins(self) -> int:
        statement = (
            select(func.count())
            .select_from(User)
            .join(Role)
            .where(Role.code == "ADMIN", User.is_active.is_(True))
        )
        return int(self.session.scalar(statement) or 0)
