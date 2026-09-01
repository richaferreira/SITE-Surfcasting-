from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.beach import Beach
    from app.models.role import Role


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True)
    role_id: Mapped[int] = mapped_column(
        mysql.TINYINT(unsigned=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    username: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)

    role: Mapped[Role] = relationship(back_populates="users", lazy="joined")
    beaches_created: Mapped[list[Beach]] = relationship(
        back_populates="created_by_user",
        foreign_keys="Beach.created_by_id",
    )
    beaches_updated: Mapped[list[Beach]] = relationship(
        back_populates="updated_by_user",
        foreign_keys="Beach.updated_by_id",
    )

    def record_login(self) -> None:
        self.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)
