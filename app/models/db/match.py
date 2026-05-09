from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


INITIATED_BY_VALUES = "('taker','giver')"
MATCH_FORMAT_VALUES = "('freechat','coffeechat','mealchat')"
MATCH_STATUS_VALUES = "('pending','accepted','rejected','paid','completed','cancelled')"


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        CheckConstraint(
            f"initiated_by IN {INITIATED_BY_VALUES}", name="ck_matches_initiated_by"
        ),
        CheckConstraint(f"format IN {MATCH_FORMAT_VALUES}", name="ck_matches_format"),
        CheckConstraint(f"status IN {MATCH_STATUS_VALUES}", name="ck_matches_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    taker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    giver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    taker_post_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("taker_posts.id"), nullable=True
    )

    initiated_by: Mapped[str] = mapped_column(String(10), nullable=False)
    format: Mapped[str | None] = mapped_column(String(20), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_dates: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    status: Mapped[str] = mapped_column(
        String(20), server_default=text("'pending'"), nullable=False
    )
    payment_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
