from sqlalchemy import or_, select
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
