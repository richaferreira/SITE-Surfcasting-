from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CommunityCategory, CommunityStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.beach import Beach
    from app.models.user import User


class CommunityThread(TimestampMixin, Base):
    __tablename__ = "community_threads"

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True)
    author_id: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    beach_id: Mapped[int | None] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("praias.id", ondelete="SET NULL"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[CommunityCategory] = mapped_column(
        SAEnum(CommunityCategory, values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
    )
    status: Mapped[CommunityStatus] = mapped_column(
        SAEnum(CommunityStatus, values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
        default=CommunityStatus.PUBLICADO,
    )
    media_url: Mapped[str | None] = mapped_column(String(500))

    author: Mapped[User] = relationship(foreign_keys=[author_id], lazy="joined")
    beach: Mapped[Beach | None] = relationship(foreign_keys=[beach_id], lazy="joined")
    comments: Mapped[list[CommunityComment]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
    )
    reactions: Mapped[list[CommunityReaction]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
    )


class CommunityComment(TimestampMixin, Base):
    __tablename__ = "community_comments"

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True)
    thread_id: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("community_threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(nullable=False, default=False)

    thread: Mapped[CommunityThread] = relationship(back_populates="comments")
    author: Mapped[User] = relationship(foreign_keys=[author_id], lazy="joined")


class CommunityReaction(Base):
    __tablename__ = "community_reactions"

    thread_id: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("community_threads.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    thread: Mapped[CommunityThread] = relationship(back_populates="reactions")
