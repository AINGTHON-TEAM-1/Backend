"""AI 태그 추천 (Gemini).

PRD §0 핵심 설계 원칙: AI는 추천만, 결정은 사용자.
이 모듈은 태그 후보를 제안할 뿐이며, 매칭 로직에는 일절 개입하지 않는다.
"""

from __future__ import annotations

import asyncio
import logging
import time

from app.core.config import settings

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = (
    "다음 텍스트에서 커뮤니티 운영 관련 핵심 키워드 5개를 추출해줘.\n"
    "규칙:\n"
    "- 한글 명사 또는 짧은 구\n"
    "- # 없이 단어만, 콤마 구분\n"
    "\n"
    "텍스트: {text}"
)

_MODEL = None
_MODEL_INIT_FAILED = False


def _get_model():
    """Lazy 초기화 — settings.gemini_api_key 미설정 시 None 반환 (빈 결과 fallback)."""
    global _MODEL, _MODEL_INIT_FAILED
    if _MODEL is not None or _MODEL_INIT_FAILED:
        return _MODEL
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY not configured; tag suggestion will return empty list")
        _MODEL_INIT_FAILED = True
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        _MODEL = genai.GenerativeModel("gemini-3.1-flash")
    except Exception:
        logger.exception("Failed to initialize Gemini model")
        _MODEL_INIT_FAILED = True
        return None
    return _MODEL


def _parse_tags(raw: str) -> list[str]:
    parts = [p.strip().lstrip("#").strip() for p in raw.split(",")]
    return [p for p in parts if p][:5]


async def suggest_tags(text: str) -> tuple[list[str], int]:
    """텍스트에서 태그 5개 추천. 실패 시 빈 리스트.

    Returns (tags, processing_time_ms). 타임아웃 3초 (PRD §11.1).
    """
    start = time.perf_counter()
    model = _get_model()
    if model is None:
        return [], int((time.perf_counter() - start) * 1000)

    prompt = _PROMPT_TEMPLATE.format(text=text)
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(model.generate_content, prompt),
            timeout=3.0,
        )
    except asyncio.TimeoutError:
        logger.warning("Gemini suggest_tags timed out (>3s)")
        return [], int((time.perf_counter() - start) * 1000)
    except Exception:
        logger.exception("Gemini suggest_tags failed")
        return [], int((time.perf_counter() - start) * 1000)

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    raw_text = getattr(response, "text", "") or ""
    if not raw_text:
        return [], elapsed_ms

    try:
        tags = _parse_tags(raw_text)
    except Exception:
        logger.exception("Gemini response parse failed: %r", raw_text)
        return [], elapsed_ms
    return tags, elapsed_ms
