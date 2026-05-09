# Phase 3 — Giver/Taker 작성 API + 가격 자동 산정

> **목표**: Giver 프로필 등록, Taker 구인글 작성, 태그 저장, 가격 자동 산정 로직이 완전히 작동한다.

| 항목 | 내용 |
|------|------|
| PRD 매핑 | FR-GIVER-01~03, FR-TAKER-01, §8.2 가격 산정 로직 |
| 해커톤 일정 | Day 1 PM (7~10h) |
| 선행 의존성 | Phase 2 완료 (dev-login JWT 의존성 사용) |
| 후속 Phase | Phase 4, 5, 6 (병렬 진행 가능) |

---

## 작업 체크리스트

### 1. 가격 산정 서비스 (`app/services/pricing.py`)

PRD §8.2 의사코드를 그대로 구현. 이 함수는 순수 함수 — DB 접근 없음.

- [ ] `recalculate_giver_pricing(match_count: int, rating_avg: float) -> tuple[int, int]`
  ```
  입력: match_count, rating_avg
  출력: (coffeechat_price, mealchat_price)

  규칙:
  - match_count < 3 → (5000, 10000) 하한선 고정
  - rating_norm = max(0, (rating_avg - 3.0) / 2.0)
  - activity_norm = min(1.0, (match_count - 3) / 27)
  - score = 0.6 * rating_norm + 0.4 * activity_norm
  - coffee = round((5000 + 20000 * score) / 500) * 500
  - meal   = round((10000 + 40000 * score) / 500) * 500
  ```
- [ ] 단위 테스트용 예시 5가지 (PRD §8.2 표 기준):
  - A(신규): (5000, 10000)
  - B(입문 4.0/5건): (11500, 23500)
  - C(활성 4.5/15건): (17500, 35000)
  - D(인기 4.8/30건): (23500, 47500)
  - E(저평점 3.2/20건): (11000, 22500)

### 2. Giver 서비스 (`app/services/giver_service.py`)

- [ ] `create_giver_profile(user_id, data: GiverProfileCreate, db) -> GiverProfile`
  - `giver_profiles` 레코드 생성
  - `recalculate_giver_pricing(0, 0)` 호출 → 하한선 가격 자동 부여
  - `is_newbie=True` 설정
  - 경험 데이터(`experience`) 있으면 `giver_experiences` 레코드도 생성
  - 태그 목록(`tags`) 있으면 `tags` 테이블에 `owner_type='giver_profile'`로 저장

- [ ] `get_giver_profile(giver_id, db) -> GiverProfileResponse`
  - 프로필 + 경험 + 태그 조인 조회
  - 산정된 가격 포함 응답

- [ ] `update_giver_profile(user_id, data: GiverProfileUpdate, db) -> GiverProfileResponse`
  - 가격 관련 필드는 업데이트 무시 (서비스 레이어에서 필터링)

### 3. Giver 라우터 (`app/routers/givers.py`)

fastapi-skill 패턴 적용.

- [ ] `POST /api/v1/givers/profile` 🔒
  - Request: `GiverProfileCreate` (가격 필드 없음)
  - 이미 프로필 있으면 HTTP 409
  - Response: `GiverProfileResponse` (201)

- [ ] `GET /api/v1/givers/{giver_id}`
  - 공개 엔드포인트 (인증 불필요)
  - Response: `GiverProfileResponse`

- [ ] `PATCH /api/v1/givers/profile` 🔒
  - 본인 프로필만 수정 가능 (소유권 검증)
  - Response: `GiverProfileResponse`

- [ ] `POST /api/v1/givers/experiences` 🔒
  - Giver 프로필이 없으면 HTTP 404
  - MVP: 1개만 허용 (이미 있으면 HTTP 409, v1.5에서 다중 허용)

### 4. Post 서비스 (`app/services/post_service.py`)

- [ ] `create_post(user_id, data: TakerPostCreate, db) -> TakerPost`
  - `taker_posts` 레코드 생성
  - 태그 목록 있으면 `tags` 테이블에 `owner_type='taker_post'`로 저장

- [ ] `get_post(post_id, db) -> TakerPostResponse`
  - 게시글 + 태그 조인 조회

- [ ] `update_post(post_id, user_id, data: TakerPostUpdate, db) -> TakerPostResponse`
  - 소유권 검증 (작성자만 수정)

- [ ] `delete_post(post_id, user_id, db) -> None`
  - 소유권 검증 후 삭제

### 5. Post 라우터 (`app/routers/posts.py`)

- [ ] `POST /api/v1/posts` 🔒 — 구인글 작성 (201)
- [ ] `GET /api/v1/posts/{post_id}` — 구인글 상세 (공개)
- [ ] `PATCH /api/v1/posts/{post_id}` 🔒 — 구인글 수정
- [ ] `DELETE /api/v1/posts/{post_id}` 🔒 — 구인글 삭제 (204)

### 6. 태그 처리 공통 패턴

Giver 프로필과 Taker 구인글 모두 동일한 방식으로 태그 저장.

```python
# 태그 저장 헬퍼 (서비스 레이어 공통)
async def save_tags(owner_type: str, owner_id: UUID, tags: list[str],
                    is_ai_suggested: bool, db: AsyncSession):
    tag_records = [
        Tag(owner_type=owner_type, owner_id=owner_id,
            tag=t, is_ai_suggested=is_ai_suggested)
        for t in tags
    ]
    db.add_all(tag_records)
```

- `is_ai_suggested=True`: AI 추천 후 사용자가 수락한 태그
- `is_ai_suggested=False`: 사용자가 직접 입력한 태그

---

## 산출 파일 트리

```
Backend/
└── app/
    ├── services/
    │   ├── pricing.py
    │   ├── giver_service.py
    │   └── post_service.py
    └── routers/
        ├── givers.py
        └── posts.py
```

`app/main.py`에 라우터 마운트 추가:
```python
from app.routers import givers, posts
app.include_router(givers.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")
```

---

## 검증 기준 (DoD)

| 검증 항목 | 방법 | 기대 결과 |
|----------|------|----------|
| 가격 산정 단위 테스트 | `pytest tests/test_pricing.py` | PRD §8.2 표의 5가지 시나리오 모두 통과 |
| Giver 프로필 등록 | `POST /givers/profile` (인증 포함) | 201, 가격 5000/10000 자동 부여 |
| 가격 필드 무시 | `POST /givers/profile` body에 `coffeechat_price` 포함 | 무시되고 5000으로 저장 |
| 구인글 작성 | `POST /posts` | 201, 태그 저장 확인 |
| 소유권 검증 | 타인 게시글 `DELETE` | HTTP 403 |
| 중복 프로필 | 동일 사용자 `POST /givers/profile` 2회 | HTTP 409 |

---

## 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| 태그 저장 시 N+1 쿼리 | `db.add_all()` 배치 삽입으로 처리 |
| 가격 산정 부동소수점 오차 | `round(.../ 500) * 500` 정수 연산으로 처리 |
| 경험 + 프로필 원자적 저장 실패 | 단일 트랜잭션 내 처리 (`async with db.begin()`) |
