from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

InitiatedBy = Literal["taker", "giver"]
MatchFormat = Literal["freechat", "coffeechat", "mealchat"]
MatchStatus = Literal[
    "pending", "accepted", "rejected", "paid", "completed", "cancelled"
]
MatchTargetType = Literal["giver", "taker_post"]
RejectReason = Literal["time_mismatch", "field_mismatch", "other"]
MyMatchKind = Literal["sent", "received", "matched"]


class MatchCreate(BaseModel):
    """매칭 신청. target_type으로 양방향 흐름을 구분.

    - target_type='giver': Taker가 Giver에게 직접 신청 (target_id=Giver의 user_id, post_id 선택)
    - target_type='taker_post': Giver가 Taker 구인글에 신청 (target_id=taker_posts.id)
    """

    target_type: MatchTargetType
    target_id: uuid.UUID = Field(
        ..., description="target_type에 따라 user.id(giver) 또는 taker_posts.id"
    )
    post_id: uuid.UUID | None = Field(
        default=None, description="Taker가 자신의 구인글과 신청을 연결할 때만"
    )
    format: MatchFormat
    message: str = Field(..., max_length=200)
    preferred_dates: list[Any] | dict[str, Any] | None = None


class RejectRequest(BaseModel):
    reason: RejectReason


class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    taker_id: uuid.UUID
    giver_id: uuid.UUID
    taker_post_id: uuid.UUID | None
    initiated_by: InitiatedBy
    format: MatchFormat | None
    message: str | None
    preferred_dates: Any | None
    status: MatchStatus
    payment_amount: int | None
    payment_id: str | None
    created_at: datetime
    accepted_at: datetime | None
    paid_at: datetime | None
