from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GiverCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nickname: str
    profile_image_url: str | None
    bio_short: str | None
    rating_avg: Decimal
    rating_count: int
    match_count: int
    tags: list[str]
    categories: list[str]
    freechat_enabled: bool
    coffeechat_price: int
    mealchat_price: int


class PostCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    body_preview: str
    category: str | None
    preferred_format: str | None
    budget_min: int | None
    budget_max: int | None
    tags: list[str]
    application_count: int
    status: str
    author_nickname: str
    created_at: datetime


class DiscoverGiversResponse(BaseModel):
    total: int
    page: int
    items: list[GiverCardResponse]


class DiscoverPostsResponse(BaseModel):
    total: int
    page: int
    items: list[PostCardResponse]


class PopularTagItem(BaseModel):
    tag: str
    count: int


class PopularTagsResponse(BaseModel):
    tags: list[PopularTagItem]
