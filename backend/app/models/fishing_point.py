from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AccessibilityLevel, FishingPointType
from app.models.mixins import TimestampMixin
from app.models.spatial import MySQLPoint

if TYPE_CHECKING:
    from app.models.beach import Beach
    from app.models.user import User


class FishingPoint(TimestampMixin, Base):
    __tablename__ = "pontos_pesca"

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True)
    beach_id: Mapped[int] = mapped_column(
        "praia_id",
        mysql.BIGINT(unsigned=True),
        ForeignKey("praias.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), nullable=False)
    point_type: Mapped[FishingPointType] = mapped_column(
        SAEnum(FishingPointType, values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[Decimal] = mapped_column(mysql.DECIMAL(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(mysql.DECIMAL(9, 6), nullable=False)
    location: Mapped[bytes] = mapped_column(MySQLPoint(4326), nullable=False, deferred=True)
    accessibility: Mapped[AccessibilityLevel] = mapped_column(
        SAEnum(AccessibilityLevel, values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
        default=AccessibilityLevel.MODERADA,
    )
    access_notes: Mapped[str | None] = mapped_column(String(500))
    risk_notes: Mapped[str | None] = mapped_column(String(500))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_id: Mapped[int] = mapped_column(
        "created_by",
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    beach: Mapped[Beach] = relationship()
    created_by_user: Mapped[User] = relationship()

