# Phase 5 — AI 태그 추천 (Gemini)

> **목표**: 사용자가 글 작성 후 버튼을 누르면 Gemini가 3초 이내에 태그 5개를 제안한다. 실패 시 빈 배열로 graceful fallback.

| 항목 | 내용 |
|------|------|
| PRD 매핑 | FR-GIVER-04, FR-TAKER-02, §8.5 AI 태그 추천 |
| 해커톤 일정 | Day 2 PM (16~18h) |
| 선행 의존성 | Phase 3 완료 (인증 의존성 사용) |
| 후속 Phase | Phase 7 (통합 검증) |

---

## 핵심 설계 원칙 (PRD §0)

> ⚠️ **AI는 추천만, 결정은 사용자.** 이 엔드포인트는 태그 후보를 제안할 뿐이다.  
> 매칭 로직에 AI가 개입하지 않는다. 이 원칙을 코드 주석에도 명시한다.

---

## 작업 체크리스트

### 1. AI 서비스 (`app/services/ai_service.py`)

- [ ] Gemini 클라이언트 초기화
  ```python
  import google.generativeai as genai
  from app.core.config import settings

  genai.configure(api_key=settings.GEMINI_API_KEY)
  _model = genai.GenerativeModel("gemini-3.1-flash")
  ```

- [ ] `suggest_tags(text: str) -> list[str]`
  - PRD §14.2 프롬프트 그대로 사용:
    ```
    다음 텍스트에서 커뮤니티 운영 관련 핵심 키워드 5개를 추출해줘.
    규칙:
    - 한글 명사 또는 짧은 구
    - # 없이 단어만, 콤마 구분

    텍스트: {text}
    ```
  - 응답 파싱: `response.text.split(",")` → strip → 최대 5개
  - **타임아웃 3초** (PRD §10.3 리스크 대응):
    ```python
    import asyncio
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(_model.generate_content, prompt),
            timeout=3.0
        )
    except asyncio.TimeoutError:
        return []  # fallback: 빈 배열
    ```
  - Gemini API 오류 시 빈 배열 반환 (try/except)
  - 응답 시간 측정 (`time.perf_counter()`)

### 2. AI 라우터 (`app/routers/ai.py`)

- [ ] `POST /api/v1/ai/suggest-tags` 🔒

  Request:
  ```json
  { "text": "30명 규모 보드게임 동아리를 1년째 운영 중인데..." }
  ```

  Response (PRD §8.5 그대로):
  ```json
  {
    "success": true,
    "suggested_tags": ["중규모", "장기", "오프라인", "신입유치", "리텐션"],
    "processing_time_ms": 1820,
    "note": "AI 추천입니다. 자유롭게 편집하세요."
  }
  ```

  - `text` 최소 10자, 최대 1000자 (Pydantic 검증)
  - Gemini 실패 시: `{"success": false, "suggested_tags": [], "note": "태그 추천에 실패했습니다. 직접 입력해 주세요."}`
  - 인증 필수 (무분별한 API 호출 방지)

### 3. Pydantic 스키마 (`app/models/schemas/ai.py`)

- [ ] `TagSuggestRequest`
  ```python
  class TagSuggestRequest(BaseModel):
      text: str = Field(..., min_length=10, max_length=1000)
  ```

- [ ] `TagSuggestResponse`
  ```python
  class TagSuggestResponse(BaseModel):
      success: bool
      suggested_tags: list[str]
      processing_time_ms: int
      note: str
  ```

---

## 산출 파일 트리

```
Backend/
└── app/
    ├── services/
    │   └── ai_service.py
    ├── routers/
    │   └── ai.py
    └── models/
        └── schemas/
            └── ai.py
```

`app/main.py`에 라우터 마운트 추가:
```python
from app.routers import ai
app.include_router(ai.router, prefix="/api/v1")
```

---

## 검증 기준 (DoD)

| 검증 항목 | 방법 | 기대 결과 |
|----------|------|----------|
| 정상 응답 | `POST /ai/suggest-tags` (유효한 텍스트) | 태그 1~5개, `processing_time_ms` 포함 |
| 응답 시간 | 실제 Gemini 호출 | < 3초 (PRD §11.1) |
| 타임아웃 fallback | 네트워크 차단 후 호출 | `success: false`, 빈 배열, HTTP 200 |
| 인증 없이 호출 | 쿠키 없이 `POST /ai/suggest-tags` | HTTP 401 |
| 짧은 텍스트 | `text: "안녕"` (10자 미만) | HTTP 422 Validation Error |

---

## 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| Gemini API 응답 지연 | `asyncio.wait_for(timeout=3.0)` + 빈 배열 fallback |
| Gemini API 키 미설정 | 서버 기동 시 `settings.GEMINI_API_KEY` 검증, 없으면 경고 로그 |
| 콤마 외 구분자로 응답 | 파싱 실패 시 전체 응답을 단일 태그로 처리하거나 빈 배열 반환 |
| 해커톤 데모 중 API 한도 초과 | 사용자당 분당 10회 제한 (간단한 in-memory 카운터) |
