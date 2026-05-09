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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


CATEGORY_VALUES = "('network','league','community','crew','circle','party')"
FORMAT_VALUES = "('freechat','coffeechat','mealchat')"
POST_STATUS_VALUES = "('open','matched','closed')"


class TakerPost(Base):
    __tablename__ = "taker_posts"
    __table_args__ = (
        CheckConstraint(f"category IN {CATEGORY_VALUES}", name="ck_taker_posts_category"),
        CheckConstraint(
            f"preferred_format IN {FORMAT_VALUES}",
            name="ck_taker_posts_preferred_format",
        ),
        CheckConstraint(f"status IN {POST_STATUS_VALUES}", name="ck_taker_posts_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(50), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    preferred_format: Mapped[str | None] = mapped_column(String(20), nullable=True)
    budget_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), server_default=text("'open'"), nullable=False
    )
    application_count: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="taker_posts")
