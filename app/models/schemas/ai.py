from __future__ import annotations

from pydantic import BaseModel, Field


class TagSuggestRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=1000)


class TagSuggestResponse(BaseModel):
    success: bool
    suggested_tags: list[str]
    processing_time_ms: int
    note: str
