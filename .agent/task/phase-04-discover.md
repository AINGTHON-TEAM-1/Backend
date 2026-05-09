# Phase 4 — ⭐ 양방향 탐색 API (핵심)

> **목표**: Taker가 Giver를 찾고, Giver가 Taker 구인글을 찾는 양방향 탐색이 검색·필터·정렬과 함께 완전히 작동한다.

| 항목 | 내용 |
|------|------|
| PRD 매핑 | FR-DISCOVER-01, FR-DISCOVER-02, FR-DISCOVER-03, §8.4 |
| 해커톤 일정 | Day 2 AM (10~16h) — 가장 많은 시간 배정 |
| 선행 의존성 | Phase 3 완료 (Giver/Post 데이터 존재) |
| 후속 Phase | Phase 7 (통합 검증) |

---

## 작업 체크리스트

### 1. Discover 서비스 (`app/services/discover_service.py`)

#### 1-1. `search_givers()` — Giver 탐색 (Taker가 사용)

- [ ] 함수 시그니처:
  ```python
  async def search_givers(
      q: str | None,
      categories: list[str] | None,
      formats: list[str] | None,
      price_min: int,
      price_max: int,
      rating_min: float,
      tag: str | None,
      sort: str,
      page: int,
      size: int,
      db: AsyncSession,
  ) -> tuple[int, list[GiverCardResponse]]
  ```

- [ ] **텍스트 검색** (`q`): `User.nickname`, `GiverProfile.bio_long`, `GiverExperience.community_name` ILIKE 검색
  - 세 컬럼 OR 조건

- [ ] **카테고리 필터** (`categories`): `GiverExperience.categories && ARRAY[...]` (GIN 인덱스 활용)
  - SQLAlchemy: `.where(GiverExperience.categories.overlap(categories))`

- [ ] **만남 형식 필터** (`formats`):
  - `freechat` → `GiverProfile.freechat_enabled == True`
  - `coffeechat` → `GiverProfile.coffeechat_enabled == True`
  - `mealchat` → `GiverProfile.mealchat_enabled == True`
  - 다중 선택 시 OR 조건

- [ ] **가격 범위 필터** (`price_min`, `price_max`): `GiverProfile.coffeechat_price BETWEEN price_min AND price_max`

- [ ] **평점 필터** (`rating_min`): `GiverProfile.rating_avg >= rating_min`

- [ ] **태그 필터** (`tag`): `tags` 테이블 JOIN → `Tag.owner_type='giver_profile' AND Tag.tag=tag`

- [ ] **정렬** (`sort`):
  | sort 값 | 정렬 기준 |
  |---------|----------|
  | `latest` | `GiverProfile.created_at DESC` |
  | `rating` | `GiverProfile.rating_avg DESC` |
  | `popular` | `GiverProfile.match_count DESC` |
  | `price_asc` | `GiverProfile.coffeechat_price ASC` |

- [ ] **페이지네이션**: `OFFSET (page-1)*size LIMIT size`, 전체 count 별도 쿼리

- [ ] **Cold Start 부스팅**: `is_newbie=True`인 Giver는 `latest` 정렬 시 상위 노출
  - 구현: `ORDER BY is_newbie DESC, created_at DESC`

#### 1-2. `search_posts()` — Taker 구인글 탐색 (Giver가 사용)

- [ ] 함수 시그니처:
  ```python
  async def search_posts(
      q: str | None,
      categories: list[str] | None,
      formats: list[str] | None,
      budget_min: int | None,
      budget_max: int | None,
      active_only: bool,
      tag: str | None,
      sort: str,
      page: int,
      size: int,
      db: AsyncSession,
  ) -> tuple[int, list[PostCardResponse]]
  ```

- [ ] **텍스트 검색** (`q`): PostgreSQL Full Text Search 활용
  ```sql
  to_tsvector('simple', title || ' ' || body) @@ plainto_tsquery('simple', q)
  ```
  - SQLAlchemy: `func.to_tsvector('simple', ...).op('@@')(func.plainto_tsquery('simple', q))`

- [ ] **카테고리 필터**: `TakerPost.category IN categories`

- [ ] **만남 형식 필터**: `TakerPost.preferred_format IN formats`

- [ ] **예산 범위 필터**: `TakerPost.budget_max >= budget_min AND TakerPost.budget_min <= budget_max`

- [ ] **상태 필터** (`active_only`): `TakerPost.status = 'open'`

- [ ] **태그 필터**: `tags` 테이블 JOIN → `Tag.owner_type='taker_post' AND Tag.tag=tag`

- [ ] **정렬** (`sort`):
  | sort 값 | 정렬 기준 |
  |---------|----------|
  | `latest` | `TakerPost.created_at DESC` |
  | `applications_asc` | `TakerPost.application_count ASC` (블루오션) |
  | `budget_desc` | `TakerPost.budget_max DESC` |

#### 1-3. `get_popular_tags()` — 인기 태그 Top 10

- [ ] 최근 30일 내 등록된 태그 사용 빈도 집계
  ```sql
  SELECT tag, COUNT(*) as cnt
  FROM tags
  WHERE created_at >= NOW() - INTERVAL '30 days'
  GROUP BY tag
  ORDER BY cnt DESC
  LIMIT 10
  ```

### 2. Discover 라우터 (`app/routers/discover.py`)

PRD §8.4 응답 스키마 그대로.

- [ ] `GET /api/v1/discover/givers`
  ```
  Query params:
  q, categories (다중), format (다중), price_min, price_max,
  rating_min, tag, sort, page (default=1), size (default=12)
  ```
  Response:
  ```json
  {
    "total": 47,
    "page": 1,
    "items": [{ "id", "nickname", "profile_image_url", "bio_short",
                "rating_avg", "rating_count", "match_count",
                "tags", "categories",
                "freechat_enabled", "coffeechat_price", "mealchat_price" }]
  }
  ```

- [ ] `GET /api/v1/discover/posts`
  ```
  Query params:
  q, categories (다중), format (다중), budget_min, budget_max,
  active_only (default=false), tag, sort, page (default=1), size (default=12)
  ```
  Response:
  ```json
  {
    "total": 8,
    "page": 1,
    "items": [{ "id", "title", "body_preview", "category",
                "preferred_format", "budget_min", "budget_max",
                "tags", "application_count", "status",
                "author_nickname", "created_at" }]
  }
  ```

- [ ] `GET /api/v1/discover/popular-tags`
  Response: `{"tags": [{"tag": "리텐션", "count": 23}, ...]}`

### 3. Pydantic 응답 스키마 추가 (`app/models/schemas/discover.py`)

- [ ] `GiverCardResponse` — 탐색 카드용 (상세 페이지보다 필드 적음)
- [ ] `PostCardResponse` — 구인글 카드용
- [ ] `DiscoverGiversResponse` — `total`, `page`, `items: list[GiverCardResponse]`
- [ ] `DiscoverPostsResponse` — `total`, `page`, `items: list[PostCardResponse]`
- [ ] `PopularTagItem` — `tag: str`, `count: int`

---

## 산출 파일 트리

```
Backend/
└── app/
    ├── services/
    │   └── discover_service.py
    ├── routers/
    │   └── discover.py
    └── models/
        └── schemas/
            └── discover.py
```

`app/main.py`에 라우터 마운트 추가:
```python
from app.routers import discover
app.include_router(discover.router, prefix="/api/v1")
```

---

## 검증 기준 (DoD)

| 검증 항목 | 방법 | 기대 결과 |
|----------|------|----------|
| 기본 목록 조회 | `GET /discover/givers` | 시드 Giver 5명 반환 |
| 텍스트 검색 | `GET /discover/givers?q=디스코드` | 관련 Giver만 필터링 |
| 카테고리 필터 | `GET /discover/givers?categories=community,circle` | 해당 카테고리 Giver만 |
| 평점 정렬 | `GET /discover/givers?sort=rating` | 평점 높은 순 정렬 |
| 구인글 FTS | `GET /discover/posts?q=알고리즘` | 본문 포함 게시글 반환 |
| 블루오션 정렬 | `GET /discover/posts?sort=applications_asc` | 신청 적은 순 정렬 |
| 인기 태그 | `GET /discover/popular-tags` | 최대 10개 태그 반환 |
| 응답 시간 | 시드 데이터 기준 | < 1초 (PRD §5) |
| 페이지네이션 | `?page=1&size=3` | 3개 반환, total 정확 |

---

## 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| 다중 JOIN 시 N+1 쿼리 | `selectinload` 또는 서브쿼리로 태그 일괄 로딩 |
| FTS `plainto_tsquery` 한글 미지원 | `'simple'` 설정 사용 (형태소 분석 없이 단순 매칭) |
| 카테고리 다중 선택 쿼리 파라미터 파싱 | `Query(None)` + `list[str]` 타입 힌트로 FastAPI 자동 파싱 |
| Cold Start 부스팅 정렬 복잡도 | `is_newbie DESC` 선행 정렬로 단순 구현 |
