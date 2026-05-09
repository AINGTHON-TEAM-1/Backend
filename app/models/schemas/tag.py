from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TagOwnerType = Literal["giver_profile", "taker_post"]


class TagCreate(BaseModel):
    owner_type: TagOwnerType
    owner_id: uuid.UUID
    tag: str = Field(..., min_length=1, max_length=30)
    is_ai_suggested: bool = False


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_type: TagOwnerType
    owner_id: uuid.UUID
    tag: str
    is_ai_suggested: bool
    created_at: datetime
