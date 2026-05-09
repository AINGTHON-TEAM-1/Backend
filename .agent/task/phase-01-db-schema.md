# Phase 1 — DB 스키마 & ORM/Pydantic 모델

> **목표**: PRD §7 스키마를 Alembic 마이그레이션으로 적용하고, SQLAlchemy ORM 모델과 Pydantic 스키마를 완성한다. 시드 데이터도 이 Phase에서 준비한다.  
> DB: GCP 상에 띄운 PostgreSQL Docker 컨테이너 (로컬 개발은 `docker-compose.yml` 사용)

| 항목 | 내용 |
|------|------|
| PRD 매핑 | §7 Data Model, §14.1 명칭 정의 |
| 해커톤 일정 | Day 1 AM (2~4h) |
| 선행 의존성 | Phase 0 완료 |
| 후속 Phase | Phase 2, 시드 데이터 즉시 실행 |

---

## 작업 체크리스트

### 1. Alembic 마이그레이션 (`alembic/versions/001_initial_schema.py`)

PRD §7 SQL을 그대로 반영. 누락 없이 인덱스까지 포함.

- [ ] `users` 테이블
  - `id UUID PK`, `nickname VARCHAR(30)`, `profile_image_url TEXT`, `email VARCHAR(100)`, `role VARCHAR(10) CHECK IN ('giver','taker')`, `created_at`, `updated_at`
  - ⚠️ `kakao_id` 컬럼 없음 — 해커톤 목데이터 기반이므로 불필요

- [ ] `giver_profiles` 테이블
  - `id UUID PK`, `user_id UUID UNIQUE FK→users`, `bio_short VARCHAR(50)`, `bio_long TEXT`
  - 만남 형식 토글: `freechat_enabled BOOL DEFAULT TRUE`, `coffeechat_enabled BOOL DEFAULT FALSE`, `mealchat_enabled BOOL DEFAULT FALSE`
  - 가격 (시스템 산정): `coffeechat_price INT DEFAULT 5000`, `mealchat_price INT DEFAULT 10000`
  - 통계: `pricing_score DECIMAL(3,2) DEFAULT 0`, `rating_avg DECIMAL(3,2) DEFAULT 0`, `rating_count INT DEFAULT 0`, `match_count INT DEFAULT 0`
  - Cold Start: `is_newbie BOOL DEFAULT TRUE`

- [ ] `giver_experiences` 테이블
  - `id UUID PK`, `giver_profile_id UUID FK→giver_profiles`
  - `community_name VARCHAR(100)`, `categories TEXT[] CHECK <@ ARRAY[6종]`, `duration_months INT`, `max_member_count INT`, `proof_url TEXT`, `achievement TEXT`
  - **GIN 인덱스**: `idx_giver_categories ON giver_experiences USING GIN (categories)`

- [ ] `taker_posts` 테이블
  - `id UUID PK`, `user_id UUID FK→users`, `title VARCHAR(50)`, `body TEXT`, `category VARCHAR(20) CHECK IN (6종)`, `preferred_format VARCHAR(20) CHECK IN ('freechat','coffeechat','mealchat')`, `budget_min INT`, `budget_max INT`, `status VARCHAR(20) DEFAULT 'open' CHECK IN ('open','matched','closed')`, `application_count INT DEFAULT 0`
  - **Full Text 인덱스**: `idx_posts_text USING GIN (to_tsvector('simple', title||' '||body))`
  - **복합 인덱스**: `idx_posts_status_created ON (status, created_at DESC)`

- [ ] `tags` 테이블 (polymorphic)
  - `id UUID PK`, `owner_type VARCHAR(20) CHECK IN ('giver_profile','taker_post')`, `owner_id UUID`, `tag VARCHAR(30)`, `is_ai_suggested BOOL DEFAULT FALSE`
  - 인덱스: `idx_tags_owner ON (owner_type, owner_id)`, `idx_tags_value ON (tag)`

- [ ] `matches` 테이블
  - `id UUID PK`, `taker_id UUID FK→users`, `giver_id UUID FK→users`, `taker_post_id UUID FK→taker_posts (NULL 가능)`, `initiated_by VARCHAR(10) CHECK IN ('taker','giver')`
  - `format VARCHAR(20)`, `message TEXT`, `preferred_dates JSONB`
  - `status VARCHAR(20) DEFAULT 'pending' CHECK IN ('pending','accepted','rejected','paid','completed','cancelled')`
  - `payment_amount INT`, `payment_id VARCHAR(100)`, `accepted_at TIMESTAMPTZ`, `paid_at TIMESTAMPTZ`
  - 인덱스: `idx_matches_taker_status ON (taker_id, status)`, `idx_matches_giver_status ON (giver_id, status)`

### 2. SQLAlchemy ORM 모델 (`app/models/db/`)

pydantic-skill 패턴 참고. 각 파일은 단일 테이블 담당.

- [ ] `app/models/db/user.py` — `User` 모델
- [ ] `app/models/db/giver.py` — `GiverProfile`, `GiverExperience` 모델
  - `categories` 컬럼: `ARRAY(String)` 타입
- [ ] `app/models/db/post.py` — `TakerPost` 모델
- [ ] `app/models/db/tag.py` — `Tag` 모델
- [ ] `app/models/db/match.py` — `Match` 모델
- [ ] `app/models/db/__init__.py` — 전체 export (Alembic `target_metadata` 연결용)

**공통 패턴**:
```python
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
import uuid

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ...
```

### 3. Pydantic 스키마 (`app/models/schemas/`)

pydantic-skill의 Base/Create/Update/Response 패턴 적용.

- [ ] `app/models/schemas/user.py`
  - `UserBase`, `UserCreate`, `UserUpdate`, `UserResponse`

- [ ] `app/models/schemas/giver.py`
  - `GiverProfileBase`, `GiverProfileCreate` (가격 필드 **없음** — 입력 불가), `GiverProfileUpdate`, `GiverProfileResponse` (가격 포함 읽기 전용)
  - `GiverExperienceCreate`, `GiverExperienceResponse`
  - `categories` 필드: `list[Literal['network','league','community','crew','circle','party']]`

- [ ] `app/models/schemas/post.py`
  - `TakerPostBase`, `TakerPostCreate`, `TakerPostUpdate`, `TakerPostResponse`

- [ ] `app/models/schemas/tag.py`
  - `TagCreate`, `TagResponse`

- [ ] `app/models/schemas/match.py`
  - `MatchCreate`, `MatchResponse`
  - `MatchCreate.target_type: Literal['giver', 'taker_post']`

### 4. 시드 데이터 (`scripts/seed.py`)

데모 필수 (PRD §10.2 P0).

- [ ] Giver 5명 (다양한 카테고리, 평점, 매칭 수 — 가격 산정 결과가 다르게 나오도록)
  - 신규 Giver 1명 (match_count=0 → 가격 5,000/10,000)
  - 입문 Giver 1명 (rating=4.0, match_count=5)
  - 활성 Giver 1명 (rating=4.5, match_count=15)
  - 인기 Giver 1명 (rating=4.8, match_count=30)
  - 저평점 Giver 1명 (rating=3.2, match_count=20)
- [ ] Taker 구인글 5건 (다양한 카테고리, 태그, 상태)
- [ ] 각 Giver에 태그 3~5개 (AI 추천 + 직접 추가 혼합)

---

## 산출 파일 트리

```
Backend/
├── alembic/
│   └── versions/
│       └── 001_initial_schema.py
├── app/
│   └── models/
│       ├── db/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── giver.py
│       │   ├── post.py
│       │   ├── tag.py
│       │   └── match.py
│       └── schemas/
│           ├── user.py
│           ├── giver.py
│           ├── post.py
│           ├── tag.py
│           └── match.py
└── scripts/
    └── seed.py
```

---

## 검증 기준 (DoD)

| 검증 항목 | 명령 | 기대 결과 |
|----------|------|----------|
| 마이그레이션 적용 | `alembic upgrade head` | 오류 없이 6개 테이블 생성 |
| 인덱스 확인 | `\d giver_experiences` (psql) | GIN 인덱스 존재 |
| 시드 실행 | `python scripts/seed.py` | Giver 5명, 구인글 5건 삽입 |
| 스키마 import | `from app.models.schemas.giver import GiverProfileCreate` | 오류 없음 |
| 가격 필드 차단 | `GiverProfileCreate(coffeechat_price=99999)` | Pydantic ValidationError |

---

## 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| `TEXT[]` 타입 Alembic 미지원 | `postgresql.ARRAY(String)` 명시적 사용 |
| GIN 인덱스 Alembic 자동 감지 안 됨 | `op.execute()` 로 raw SQL 인덱스 생성 |
| UUID 기본값 DB vs Python 불일치 | `server_default=text("gen_random_uuid()")` 사용 |
