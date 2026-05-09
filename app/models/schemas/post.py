from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.schemas.giver import Category

PreferredFormat = Literal["freechat", "coffeechat", "mealchat"]
PostStatus = Literal["open", "matched", "closed"]


class TakerPostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    body: str = Field(..., min_length=1)
    category: Category | None = None
    preferred_format: PreferredFormat | None = None
    budget_min: int | None = Field(default=None, ge=0)
    budget_max: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _validate_budget(self) -> "TakerPostBase":
        if (
            self.budget_min is not None
            and self.budget_max is not None
            and self.budget_min > self.budget_max
        ):
            raise ValueError("budget_min must be <= budget_max")
        return self


class TakerPostCreate(TakerPostBase):
    pass


class TakerPostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=50)
    body: str | None = Field(default=None, min_length=1)
    category: Category | None = None
    preferred_format: PreferredFormat | None = None
    budget_min: int | None = Field(default=None, ge=0)
    budget_max: int | None = Field(default=None, ge=0)
    status: PostStatus | None = None


class TakerPostResponse(TakerPostBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    status: PostStatus
    application_count: int
    created_at: datetime
