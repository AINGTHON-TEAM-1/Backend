from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

UserRole = Literal["giver", "taker"]


class UserBase(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=30)
    profile_image_url: str | None = None
    email: str | None = Field(default=None, max_length=100)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=30)
    profile_image_url: str | None = None
    email: str | None = Field(default=None, max_length=100)
    role: UserRole | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: UserRole | None = None
    created_at: datetime
    updated_at: datetime
