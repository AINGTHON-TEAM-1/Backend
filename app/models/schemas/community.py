from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CommunityCategory = Literal["giver", "taker", "both"]


class CommunityPostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1)
    category: CommunityCategory


class CommunityPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    body: str
    category: CommunityCategory
    created_at: datetime
    updated_at: datetime
    author_nickname: str


class CommunityPostListResponse(BaseModel):
    total: int
    page: int
    items: list[CommunityPostResponse]
