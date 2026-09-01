from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import MediaKind
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class MediaAsset(TimestampMixin, Base):
    __tablename__ = "media_assets"

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True)
    uploaded_by_id: Mapped[int] = mapped_column(
        "uploaded_by",
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    kind: Mapped[MediaKind] = mapped_column(
        SAEnum(MediaKind, values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
    )
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    original_size_bytes: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), nullable=False)
    size_bytes: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), nullable=False)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)

    uploaded_by_user: Mapped[User] = relationship()
