from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth.dev import get_current_user
from app.models.db import User
from app.models.schemas.ai import TagSuggestRequest, TagSuggestResponse
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/suggest-tags", response_model=TagSuggestResponse)
async def suggest_tags(
    data: TagSuggestRequest,
    _: User = Depends(get_current_user),
) -> TagSuggestResponse:
    tags, elapsed_ms = await ai_service.suggest_tags(data.text)
    if tags:
        return TagSuggestResponse(
            success=True,
            suggested_tags=tags,
            processing_time_ms=elapsed_ms,
            note="AI 추천입니다. 자유롭게 편집하세요.",
        )
    return TagSuggestResponse(
        success=False,
        suggested_tags=[],
        processing_time_ms=elapsed_ms,
        note="태그 추천에 실패했습니다. 직접 입력해 주세요.",
    )
