from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GiverProfile(Base):
    __tablename__ = "giver_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    bio_short: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bio_long: Mapped[str | None] = mapped_column(Text, nullable=True)

    freechat_enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"), nullable=False)
    coffeechat_enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"), nullable=False)
    mealchat_enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"), nullable=False)

    coffeechat_price: Mapped[int] = mapped_column(Integer, server_default=text("5000"), nullable=False)
    mealchat_price: Mapped[int] = mapped_column(Integer, server_default=text("10000"), nullable=False)

    pricing_score: Mapped[Decimal] = mapped_column(Numeric(3, 2), server_default=text("0"), nullable=False)
    pricing_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    rating_avg: Mapped[Decimal] = mapped_column(Numeric(3, 2), server_default=text("0"), nullable=False)
    rating_count: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=False)
    match_count: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=False)

    is_newbie: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="giver_profile")
    experiences: Mapped[list["GiverExperience"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )


class GiverExperience(Base):
    __tablename__ = "giver_experiences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    giver_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("giver_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    community_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    categories: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default=text("'{}'::text[]"))
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_member_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    proof_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    achievement: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    profile: Mapped["GiverProfile"] = relationship(back_populates="experiences")
