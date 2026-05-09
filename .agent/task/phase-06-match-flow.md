# Phase 6 — 매칭 신청 → 수락 → 결제 Mock 플로우

> **목표**: Taker→Giver, Giver→Taker 양방향 신청이 모두 작동하고, 수락 → 결제 Mock → 매칭 완료까지 상태 전이가 정확히 동작한다.

| 항목 | 내용 |
|------|------|
| PRD 매핑 | FR-FLOW-01~04, §8.6 매칭 플로우 |
| 해커톤 일정 | Day 2 PM (18~22h) |
| 선행 의존성 | Phase 3 완료 (Giver/Post 데이터, 인증) |
| 후속 Phase | Phase 7 (통합 검증) |

---

## 매칭 상태 전이도

```
[신청] pending
    ├── 수락 → accepted
    │       └── 결제 → paid → completed (만남 후)
    └── 거절 → rejected

cancelled: 양측 취소 (MVP에서는 UI만, 실제 취소 정책은 v1.5)
```

---

## 작업 체크리스트

### 1. 매칭 서비스 (`app/services/match_service.py`)

#### 1-1. `create_match()` — 매칭 신청 (양방향)

- [ ] 함수 시그니처:
  ```python
  async def create_match(
      current_user: User,
      data: MatchCreate,
      db: AsyncSession,
  ) -> Match
  ```

- [ ] `target_type='giver'` (Taker → Giver 신청):
  - `taker_id = current_user.id`
  - `giver_id` = 대상 Giver의 user_id 조회
  - `initiated_by = 'taker'`
  - `post_id` 있으면 연결 (선택)

- [ ] `target_type='taker_post'` (Giver → Taker 신청):
  - `giver_id = current_user.id`
  - `taker_id` = 해당 구인글 작성자 user_id 조회
  - `initiated_by = 'giver'`
  - `taker_post_id = data.target_id`
  - 구인글 `application_count` +1 (원자적 업데이트)

- [ ] 중복 신청 방지: 동일 (taker_id, giver_id, status='pending') 조합 존재 시 HTTP 409

- [ ] `payment_amount` 스냅샷:
  - `format='freechat'` → `payment_amount = 0`
  - `format='coffeechat'` → `payment_amount = giver_profile.coffeechat_price` (현재 시점 스냅샷)
  - `format='mealchat'` → `payment_amount = giver_profile.mealchat_price` (현재 시점 스냅샷)
  - **중요**: 이후 Giver 가격이 바뀌어도 이 값은 변하지 않음 (PRD FR-FLOW-03)

#### 1-2. `accept_match()` — 수락

- [ ] 상태 검증: `status='pending'` 아니면 HTTP 400
- [ ] 소유권 검증: 수락 권한은 신청 받은 쪽 (Taker가 신청했으면 Giver가 수락, 반대도 동일)
- [ ] `status = 'accepted'`, `accepted_at = now()`
- [ ] 구인글 있으면 `taker_posts.status = 'matched'`로 업데이트

#### 1-3. `reject_match()` — 거절

- [ ] 상태 검증: `status='pending'` 아니면 HTTP 400
- [ ] 소유권 검증 (수락과 동일)
- [ ] `status = 'rejected'`
- [ ] 구인글 `application_count` -1 (Giver가 신청한 경우)

#### 1-4. `pay_match()` — 결제 Mock

- [ ] 상태 검증: `status='accepted'` 아니면 HTTP 400
- [ ] 소유권 검증: 결제는 Taker만 가능
- [ ] `format='freechat'` → 결제 단계 스킵, 즉시 `status='paid'`
- [ ] 유료 형식:
  ```python
  import asyncio, uuid
  await asyncio.sleep(2)  # 2초 로딩 Mock (PRD FR-FLOW-03)
  match.payment_id = f"mock_{uuid.uuid4().hex[:8]}"
  match.status = 'paid'
  match.paid_at = now()
  ```
- [ ] 결제 완료 후 `recalculate_giver_pricing()` 호출 훅 (match_count 증가 반영)
  - `giver_profile.match_count += 1`
  - `is_newbie = match_count < 3`
  - 새 가격 계산 후 `giver_profile.coffeechat_price`, `mealchat_price` 업데이트

#### 1-5. `get_my_matches()` — 내 매칭 목록

- [ ] `sent`: 내가 신청한 매칭 (`initiated_by` 기준)
- [ ] `received`: 내가 받은 신청
- [ ] `matched`: 성사된 매칭 (`status IN ('accepted','paid','completed')`)

### 2. 매칭 라우터 (`app/routers/matches.py`)

- [ ] `POST /api/v1/matches` 🔒 — 매칭 신청 (201)
  - Request: `MatchCreate`
  - Response: `MatchResponse`

- [ ] `GET /api/v1/matches/me` 🔒 — 내 매칭 목록
  - Query: `type=sent|received|matched` (default: 전체)
  - Response: `list[MatchResponse]`

- [ ] `PATCH /api/v1/matches/{match_id}/accept` 🔒 — 수락
  - Response: `MatchResponse`

- [ ] `PATCH /api/v1/matches/{match_id}/reject` 🔒 — 거절
  - Request body: `{"reason": "time_mismatch" | "field_mismatch" | "other"}`
  - Response: `MatchResponse`

- [ ] `POST /api/v1/matches/{match_id}/pay` 🔒 — 결제 Mock
  - Response: `MatchResponse` (status='paid', payment_id 포함)

### 3. Pydantic 스키마 보완 (`app/models/schemas/match.py`)

- [ ] `MatchCreate`:
  ```python
  class MatchCreate(BaseModel):
      target_type: Literal['giver', 'taker_post']
      target_id: UUID
      post_id: UUID | None = None       # Taker가 연결할 구인글 (선택)
      format: Literal['freechat', 'coffeechat', 'mealchat']
      message: str = Field(..., max_length=200)
      preferred_dates: list[str]        # ISO 8601 datetime 문자열 최대 3개
  ```

- [ ] `RejectRequest`: `reason: Literal['time_mismatch', 'field_mismatch', 'other']`

- [ ] `MatchResponse`: 전체 필드 + `payment_amount`, `payment_id`, 상태 포함

---

## 산출 파일 트리

```
Backend/
└── app/
    ├── services/
    │   └── match_service.py
    └── routers/
        └── matches.py
```

`app/main.py`에 라우터 마운트 추가:
```python
from app.routers import matches
app.include_router(matches.router, prefix="/api/v1")
```

---

## 검증 기준 (DoD)

| 검증 항목 | 방법 | 기대 결과 |
|----------|------|----------|
| Taker→Giver 신청 | `POST /matches` (target_type='giver') | 201, `initiated_by='taker'`, 가격 스냅샷 |
| Giver→Taker 신청 | `POST /matches` (target_type='taker_post') | 201, `initiated_by='giver'`, `application_count` +1 |
| 중복 신청 방지 | 동일 조합 2회 신청 | HTTP 409 |
| 수락 권한 검증 | 신청한 사람이 수락 시도 | HTTP 403 |
| 상태 전이 검증 | `accepted` 상태에서 다시 수락 | HTTP 400 |
| 결제 Mock | `POST /matches/{id}/pay` | 2초 후 `status='paid'`, `payment_id` 생성 |
| 프리챗 결제 스킵 | `format='freechat'` 결제 | 즉시 `status='paid'`, `payment_amount=0` |
| 가격 재산정 | 결제 완료 후 Giver 프로필 조회 | `match_count` +1, 가격 재계산 반영 |

---

## 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| 결제 Mock 2초 sleep이 서버 블로킹 | `asyncio.sleep(2)` 사용 (비동기, 블로킹 없음) |
| 가격 재산정 중 동시 요청 | 트랜잭션 내 `SELECT FOR UPDATE`로 giver_profile 잠금 |
| `application_count` 동시 증가 | `UPDATE taker_posts SET application_count = application_count + 1` 원자적 쿼리 |
| 양방향 수락 권한 로직 복잡 | `initiated_by` 컬럼으로 단순 분기: `initiated_by='taker'` → Giver가 수락 권한 |
