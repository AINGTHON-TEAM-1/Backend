# Phase 8 — 커뮤니티/라운지

> **목표**: Giver와 Taker가 자유롭게 글을 올리고 소통할 수 있는 커뮤니티(라운지) 공간을 제공한다.
>
> ⚠️ **PRD 변경**: PRD §12 Out of Scope에 있던 "Giver/Taker 자체 커뮤니티"가 MVP 범위로 편입됨.  
> 상세 기능 명세는 PRD에 미정의 상태이므로, 최소 기능(게시글 CRUD + 목록 조회)으로 구현한다.

| 항목 | 내용 |
|------|------|
| PRD 매핑 | §12 (MVP 편입), §4.7 v2 "Giver/Taker 라운지" |
| 해커톤 일정 | Day 3 AM (Phase 7과 병렬, 시간 여유 시) |
| 선행 의존성 | Phase 3 완료 (인증 의존성 사용) |
| 후속 Phase | 없음 |

---

## 작업 체크리스트

### 1. DB 스키마 추가 (`alembic/versions/002_community.py`)

- [ ] `community_posts` 테이블
  - `id UUID PK`, `user_id UUID FK→users`, `title VARCHAR(100)`, `body TEXT`, `category VARCHAR(20) CHECK IN ('giver','taker','both')`, `created_at`, `updated_at`
  - 인덱스: `idx_community_posts_created ON (category, created_at DESC)`

### 2. ORM 모델 (`app/models/db/community.py`)

- [ ] `CommunityPost` 모델

### 3. Pydantic 스키마 (`app/models/schemas/community.py`)

- [ ] `CommunityPostCreate` — `title`, `body`, `category`
- [ ] `CommunityPostResponse` — 전체 필드 + `author_nickname`

### 4. 커뮤니티 서비스 (`app/services/community_service.py`)

- [ ] `create_post(user_id, data, db) -> CommunityPost`
- [ ] `list_posts(category, page, size, db) -> tuple[int, list]`
- [ ] `get_post(post_id, db) -> CommunityPost`
- [ ] `delete_post(post_id, user_id, db) -> None` — 소유권 검증

### 5. 커뮤니티 라우터 (`app/routers/community.py`)

- [ ] `POST /api/v1/community/posts` 🔒 — 글 작성 (201)
- [ ] `GET /api/v1/community/posts` — 글 목록 (공개, 페이지네이션)
  - Query: `category=giver|taker|both`, `page`, `size`
- [ ] `GET /api/v1/community/posts/{post_id}` — 글 상세 (공개)
- [ ] `DELETE /api/v1/community/posts/{post_id}` 🔒 — 글 삭제 (204)

---

## 산출 파일 트리

```
Backend/
├── alembic/
│   └── versions/
│       └── 002_community.py
└── app/
    ├── models/
    │   ├── db/
    │   │   └── community.py
    │   └── schemas/
    │       └── community.py
    ├── routers/
    │   └── community.py
    └── services/
        └── community_service.py
```

`app/main.py`에 라우터 마운트 추가:
```python
from app.routers import community
app.include_router(community.router, prefix="/api/v1")
```

---

## 검증 기준 (DoD)

| 검증 항목 | 방법 | 기대 결과 |
|----------|------|----------|
| 글 작성 | `POST /community/posts` (인증 포함) | 201 |
| 목록 조회 | `GET /community/posts` | 페이지네이션 응답 |
| 카테고리 필터 | `GET /community/posts?category=giver` | 해당 카테고리 글만 |
| 소유권 검증 | 타인 글 `DELETE` | HTTP 403 |

---

## 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| PRD 상세 명세 미정의 | 최소 기능(CRUD)만 구현, 추후 확장 |
| 해커톤 시간 부족 | Phase 7 완료 후 시간 여유 있을 때만 진행 (P1 하위) |
