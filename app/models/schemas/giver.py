from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Category = Literal["network", "league", "community", "crew", "circle", "party"]


class GiverProfileBase(BaseModel):
    bio_short: str | None = Field(default=None, max_length=50)
    bio_long: str | None = Field(default=None, max_length=500)
    freechat_enabled: bool = True
    coffeechat_enabled: bool = False
    mealchat_enabled: bool = False


class GiverProfileCreate(GiverProfileBase):
    """가격은 시스템 산정, 입력 불가 (PRD FR-GIVER-03).

    extra='forbid'로 가격/평점 등 시스템 필드 입력을 ValidationError로 차단.
    """

    model_config = ConfigDict(extra="forbid")


class GiverProfileUpdate(BaseModel):
    """가격 필드는 update 스키마에도 없음 (PRD FR-GIVER-03)."""

    model_config = ConfigDict(extra="forbid")

    bio_short: str | None = Field(default=None, max_length=50)
    bio_long: str | None = Field(default=None, max_length=500)
    freechat_enabled: bool | None = None
    coffeechat_enabled: bool | None = None
    mealchat_enabled: bool | None = None


class GiverProfileResponse(GiverProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    coffeechat_price: int
    mealchat_price: int
    pricing_score: Decimal
    pricing_updated_at: datetime
    rating_avg: Decimal
    rating_count: int
    match_count: int
    is_newbie: bool
    created_at: datetime


class GiverExperienceBase(BaseModel):
    community_name: str | None = Field(default=None, max_length=100)
    categories: list[Category] = Field(default_factory=list)
    duration_months: int | None = Field(default=None, ge=0)
    max_member_count: int | None = Field(default=None, ge=0)
    proof_url: str | None = None
    achievement: str | None = None


class GiverExperienceCreate(GiverExperienceBase):
    pass


class GiverExperienceResponse(GiverExperienceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    giver_profile_id: uuid.UUID
    created_at: datetime
