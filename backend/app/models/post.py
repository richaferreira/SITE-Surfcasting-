from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PostContentType, PostStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Post(TimestampMixin, Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(mysql.BIGINT(unsigned=True), primary_key=True)
    author_id: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    slug: Mapped[str] = mapped_column(String(240), nullable=False, unique=True)
    excerpt: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(
        Text().with_variant(mysql.LONGTEXT(), "mysql"),
        nullable=False,
    )
    content_type: Mapped[PostContentType] = mapped_column(
        SAEnum(PostContentType, values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
    )
    status: Mapped[PostStatus] = mapped_column(
        SAEnum(PostStatus, values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
        default=PostStatus.RASCUNHO,
    )
    featured_image_url: Mapped[str | None] = mapped_column(String(500))
    video_url: Mapped[str | None] = mapped_column(String(500))
    seo_title: Mapped[str | None] = mapped_column(String(70))
    seo_description: Mapped[str | None] = mapped_column(String(160))
    published_at: Mapped[datetime | None] = mapped_column(DateTime)

    author: Mapped[User] = relationship()
    equipment_specification: Mapped[EquipmentSpecification | None] = relationship(
        back_populates="post",
        uselist=False,
        cascade="all, delete-orphan",
    )


class EquipmentSpecification(Base):
    __tablename__ = "equipment_specifications"

    post_id: Mapped[int] = mapped_column(
        mysql.BIGINT(unsigned=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    rod_length_m: Mapped[Decimal | None] = mapped_column(mysql.DECIMAL(4, 2))
    rod_construction: Mapped[str | None] = mapped_column(String(80))
    reel_size: Mapped[int | None] = mapped_column(Integer)
    main_line_material: Mapped[str | None] = mapped_column(String(80))
    main_line_diameter_mm: Mapped[Decimal | None] = mapped_column(mysql.DECIMAL(4, 3))
    shock_leader_type: Mapped[str | None] = mapped_column(String(100))
    casting_weight_min_g: Mapped[int | None] = mapped_column(Integer)
    casting_weight_max_g: Mapped[int | None] = mapped_column(Integer)
    extra_specs: Mapped[dict[str, Any] | None] = mapped_column(mysql.JSON)

    post: Mapped[Post] = relationship(back_populates="equipment_specification")
