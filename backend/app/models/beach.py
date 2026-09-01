from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, LargeBinary, String, Text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import BeachProfile
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Beach(TimestampMixin, Base):
    __tablename__ = "praias"

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(2), nullable=False, default="RJ")
    description: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[Decimal] = mapped_column(mysql.DECIMAL(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(mysql.DECIMAL(9, 6), nullable=False)
    location: Mapped[bytes] = mapped_column(LargeBinary, nullable=False, deferred=True)
    sea_bearing_deg: Mapped[Decimal] = mapped_column(mysql.DECIMAL(5, 2), nullable=False)
    beach_profile: Mapped[BeachProfile] = mapped_column(
        SAEnum(
            BeachProfile,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=True,
        ),
        nullable=False,
    )
    accessibility_summary: Mapped[str | None] = mapped_column(String(500))
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by_id: Mapped[int] = mapped_column(
        "created_by",
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        "updated_by",
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )

    created_by_user: Mapped[User] = relationship(
        back_populates="beaches_created",
        foreign_keys=[created_by_id],
    )
    updated_by_user: Mapped[User | None] = relationship(
        back_populates="beaches_updated",
        foreign_keys=[updated_by_id],
    )
