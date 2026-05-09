# GIVE:RUN Backend API 명세서

> **버전**: v0.1.0 (해커톤 MVP)
> **Base URL (로컬)**: `http://localhost:8000`
> **API Prefix**: `/api/v1`
> **인터랙티브 docs**: `http://localhost:8000/docs` (Swagger UI), `/redoc`
> **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 목차

1. [공통 사항](#공통-사항)
2. [인증 (Auth)](#1-인증-auth)
3. [Giver 프로필](#2-giver-프로필)
4. [Taker 구인글 (Posts)](#3-taker-구인글-posts)
5. [양방향 탐색 (Discover)](#4-양방향-탐색-discover)
6. [AI 태그 추천](#5-ai-태그-추천)
7. [매칭 플로우 (Matches)](#6-매칭-플로우-matches)
8. [커뮤니티 / 라운지](#7-커뮤니티--라운지)
9. [헬스체크](#8-헬스체크)
10. [Enum 사전](#enum-사전)
11. [에러 포맷](#에러-포맷)
12. [통합 시나리오 예시](#통합-시나리오-예시)

---

## 공통 사항

### 인증 방식 (해커톤 한정 — dev-login)

> ⚠️ 해커톤 특성상 카카오 OAuth 대신 **시드 유저 UUID 기반 dev-login**을 사용합니다.
> 모든 인증 필요 엔드포인트는 HTTP 헤더 `X-User-Id: <UUID>` 로 식별합니다.

```
X-User-Id: 8a1f2c3d-...-...-...
```

- 시드 유저 목록은 `GET /api/v1/auth/users`로 조회.
- 헤더 없거나 잘못된 UUID → `401 Unauthorized`
- DB에 존재하지 않는 UUID → `404 Not Found`

### Content-Type / Accept

- 요청: `application/json`
- 응답: `application/json`
- 모든 datetime은 ISO 8601 (`2026-05-10T12:34:56+00:00`)
- 모든 ID는 UUID v4 문자열

### CORS

기본 허용 origin (`.env`의 `CORS_ORIGINS`):
- `http://localhost:3000`
- `http://localhost:5173`

### 페이지네이션 표준

리스트 응답은 다음 공통 구조:

```json
{
  "total": 47,
  "page": 1,
  "items": [...]
}
```

- `page` 시작값: `1`
- `size` 기본값: `12` (max `100`)

---

## 1. 인증 (Auth)

### 1.1 시드 유저 목록

데모/dev-login 화면에서 사용자가 어떤 계정으로 들어갈지 선택.

```
GET /api/v1/auth/users
```

**인증**: 불필요 (공개)

**응답 200**:
```json
[
  {
    "id": "8a1f2c3d-1111-2222-3333-444455556666",
    "nickname": "신규Giver",
    "profile_image_url": null,
    "email": "newbie@example.com",
    "role": "giver",
    "created_at": "2026-05-10T00:00:00+00:00",
    "updated_at": "2026-05-10T00:00:00+00:00"
  },
  {
    "id": "9b2e3d4e-...",
    "nickname": "동아리회장A",
    "role": "taker",
    "...": "..."
  }
]
```

---

### 1.2 내 정보 조회

```
GET /api/v1/auth/me
```

**인증**: 필요 (`X-User-Id` 헤더)

**응답 200**: 단일 `UserResponse` (위 1.1 항목 형식과 동일)

**에러**:
- `401`: 헤더 누락
- `404`: 헤더 UUID에 해당하는 유저 없음

---

## 2. Giver 프로필

### 2.1 Giver 프로필 생성

```
POST /api/v1/givers/profile
```

**인증**: 필요

**요청**:
```json
{
  "bio_short": "30명 디스코드 1년 운영",
  "bio_long": "활동 지속률 60% 유지를 위한 실전 노하우.",
  "freechat_enabled": true,
  "coffeechat_enabled": true,
  "mealchat_enabled": false
}
```

| 필드 | 타입 | 제약 |
|------|------|------|
| `bio_short` | string \| null | max 50자 |
| `bio_long` | string \| null | max 500자 |
| `freechat_enabled` | bool | default `true` |
| `coffeechat_enabled` | bool | default `false` |
| `mealchat_enabled` | bool | default `false` |

> ⚠️ **가격(`coffeechat_price`, `mealchat_price`)은 시스템이 자동 산정**. 클라이언트 입력 금지.
> 추가 필드 전달 시 `422` 에러 (`extra='forbid'`).

**응답 201**: `GiverProfileResponse`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "bio_short": "...",
  "bio_long": "...",
  "freechat_enabled": true,
  "coffeechat_enabled": true,
  "mealchat_enabled": false,
  "coffeechat_price": 5000,
  "mealchat_price": 10000,
  "pricing_score": "0.00",
  "pricing_updated_at": "2026-05-10T00:00:00+00:00",
  "rating_avg": "0.00",
  "rating_count": 0,
  "match_count": 0,
  "is_newbie": true,
  "created_at": "2026-05-10T00:00:00+00:00"
}
```

**에러**:
- `409`: 이미 프로필 보유

---

### 2.2 Giver 프로필 조회 (공개)

```
GET /api/v1/givers/{user_id}
```

**인증**: 불필요

**응답 200**: `GiverProfileResponse` (실험 정보 포함)
**에러**: `404`

---

### 2.3 내 Giver 프로필 수정

```
PATCH /api/v1/givers/profile
```

**인증**: 필요

**요청** (모두 optional, `extra='forbid'`):
```json
{
  "bio_short": "...",
  "bio_long": "...",
  "freechat_enabled": true,
  "coffeechat_enabled": false,
  "mealchat_enabled": false
}
```

**응답 200**: `GiverProfileResponse`

---

### 2.4 Giver 경험 추가

> ⚠️ MVP는 Giver당 **1개 경험만** 허용 (PRD FR-GIVER-02).

```
POST /api/v1/givers/experiences
```

**인증**: 필요

**요청**:
```json
{
  "community_name": "프론트엔드 디스코드",
  "categories": ["network", "community"],
  "duration_months": 18,
  "max_member_count": 120,
  "proof_url": "https://...",
  "achievement": "정기 행사 12회 주최, 월간 활성 60%+"
}
```

| 필드 | 타입 | 제약 |
|------|------|------|
| `community_name` | string \| null | max 100자 |
| `categories` | string[] | [Category enum](#category) 값만 |
| `duration_months` | int \| null | ≥ 0 |
| `max_member_count` | int \| null | ≥ 0 |
| `proof_url` | string \| null | URL |
| `achievement` | string \| null | text |

**응답 201**:
```json
{
  "id": "uuid",
  "giver_profile_id": "uuid",
  "community_name": "프론트엔드 디스코드",
  "categories": ["network", "community"],
  "duration_months": 18,
  "max_member_count": 120,
  "proof_url": null,
  "achievement": "...",
  "created_at": "..."
}
```

**에러**:
- `404`: 본인 Giver 프로필이 없음 — 먼저 생성 필요
- `409`: 경험 이미 등록됨

---

## 3. Taker 구인글 (Posts)

### 3.1 구인글 작성

```
POST /api/v1/posts
```

**인증**: 필요

**요청**:
```json
{
  "title": "동아리 운영 도움 필요",
  "body": "30명 동아리 신학기 모집을 어떻게 시작할지 막막합니다.",
  "category": "circle",
  "preferred_format": "coffeechat",
  "budget_min": 5000,
  "budget_max": 15000
}
```

| 필드 | 타입 | 제약 |
|------|------|------|
| `title` | string | 1~50자 |
| `body` | string | 1자 이상 |
| `category` | [Category](#category) \| null | |
| `preferred_format` | [Format](#format) \| null | |
| `budget_min` | int \| null | ≥ 0 |
| `budget_max` | int \| null | ≥ 0, `budget_min` 이상 |

**응답 201**: `TakerPostResponse`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "...",
  "body": "...",
  "category": "circle",
  "preferred_format": "coffeechat",
  "budget_min": 5000,
  "budget_max": 15000,
  "status": "open",
  "application_count": 0,
  "created_at": "..."
}
```

---

### 3.2 구인글 단건 조회 (공개)

```
GET /api/v1/posts/{post_id}
```

**응답 200**: `TakerPostResponse`
**에러**: `404`

---

### 3.3 구인글 수정

```
PATCH /api/v1/posts/{post_id}
```

**인증**: 필요 (작성자만)

**요청** (모두 optional):
```json
{
  "title": "...",
  "body": "...",
  "category": "...",
  "preferred_format": "...",
  "budget_min": 0,
  "budget_max": 0,
  "status": "closed"
}
```

**에러**:
- `403`: 본인 글이 아님
- `404`

---

### 3.4 구인글 삭제

```
DELETE /api/v1/posts/{post_id}
```

**인증**: 필요 (작성자만)

**응답**: `204 No Content`
**에러**: `403`, `404`

---

## 4. 양방향 탐색 (Discover)

> 모두 **공개** 엔드포인트 — `X-User-Id` 헤더 불필요.
> 응답 시간 KPI: < 1초.

### 4.1 Giver 탐색

```
GET /api/v1/discover/givers
```

**Query 파라미터**:

| 이름 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `q` | string \| null | — | 텍스트 검색 (닉네임, bio_long, 운영 커뮤니티명 ILIKE) |
| `categories` | string[] | — | 카테고리 다중 (`?categories=community&categories=circle`) |
| `format` | string[] | — | 만남 형식 다중 (`freechat`/`coffeechat`/`mealchat`) |
| `price_min` | int | `0` | 커피챗 가격 하한 |
| `price_max` | int | `99999999` | 커피챗 가격 상한 |
| `rating_min` | float | `0.0` | 평점 하한 (0~5) |
| `tag` | string \| null | — | 단일 태그 일치 |
| `sort` | string | `latest` | `latest` \| `rating` \| `popular` \| `price_asc` |
| `page` | int | `1` | ≥ 1 |
| `size` | int | `12` | 1~100 |

**`sort` 동작**:

| 값 | 정렬 |
|---|---|
| `latest` | `is_newbie DESC, created_at DESC` (Cold Start 부스팅) |
| `rating` | `rating_avg DESC, created_at DESC` |
| `popular` | `match_count DESC, created_at DESC` |
| `price_asc` | `coffeechat_price ASC, created_at DESC` |

**응답 200** (`DiscoverGiversResponse`):
```json
{
  "total": 5,
  "page": 1,
  "items": [
    {
      "id": "uuid (giver_profile.id)",
      "nickname": "활성Giver",
      "profile_image_url": null,
      "bio_short": "100명 디스코드 1년 운영",
      "rating_avg": "4.50",
      "rating_count": 12,
      "match_count": 15,
      "tags": ["디스코드", "프론트엔드", "커뮤니티운영"],
      "categories": ["network", "community"],
      "freechat_enabled": true,
      "coffeechat_price": 14000,
      "mealchat_price": 28000
    }
  ]
}
```

> 📌 `id`는 **Giver의 `giver_profile.id`가 아니라 `user_id`**. 매칭 신청 시 `target_id`로 사용.

---

### 4.2 Taker 구인글 탐색

```
GET /api/v1/discover/posts
```

**Query 파라미터**:

| 이름 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `q` | string \| null | — | PostgreSQL FTS (`to_tsvector('simple', title \|\| body)`) |
| `categories` | string[] | — | 카테고리 다중 |
| `format` | string[] | — | `preferred_format` 다중 |
| `budget_min` | int \| null | — | 예산 하한 (post.budget_max ≥ 이 값) |
| `budget_max` | int \| null | — | 예산 상한 (post.budget_min ≤ 이 값) |
| `active_only` | bool | `false` | `true` → `status='open'`만 |
| `tag` | string \| null | — | 단일 태그 |
| `sort` | string | `latest` | `latest` \| `applications_asc` \| `budget_desc` |
| `page` | int | `1` | |
| `size` | int | `12` | 1~100 |

**`sort` 동작**:

| 값 | 정렬 | 의미 |
|---|---|---|
| `latest` | `created_at DESC` | 최신 |
| `applications_asc` | `application_count ASC, created_at DESC` | **블루오션** (신청 적은 순) |
| `budget_desc` | `budget_max DESC, created_at DESC` | 예산 큰 순 |

**응답 200** (`DiscoverPostsResponse`):
```json
{
  "total": 5,
  "page": 1,
  "items": [
    {
      "id": "uuid",
      "title": "신입 모집·이벤트 기획 도와주세요",
      "body_preview": "교내 알고리즘 동아리 회장입니다. 신학기 신입 모집을 어떻게 시작...",
      "category": "circle",
      "preferred_format": "coffeechat",
      "budget_min": 5000,
      "budget_max": 15000,
      "tags": ["동아리", "신입모집", "이벤트기획"],
      "application_count": 0,
      "status": "open",
      "author_nickname": "동아리회장A",
      "created_at": "2026-05-10T..."
    }
  ]
}
```

> `body_preview`는 본문 첫 120자.

---

### 4.3 인기 태그 Top 10

```
GET /api/v1/discover/popular-tags
```

최근 30일 내 등록된 태그 사용 빈도 Top 10.

**응답 200** (`PopularTagsResponse`):
```json
{
  "tags": [
    { "tag": "리텐션", "count": 23 },
    { "tag": "디스코드", "count": 18 },
    ...
  ]
}
```

---

## 5. AI 태그 추천

### 5.1 태그 5개 추천 (Gemini)

```
POST /api/v1/ai/suggest-tags
```

**인증**: 필요 (무분별한 호출 방지)

**요청**:
```json
{
  "text": "30명 규모 보드게임 동아리를 1년째 운영 중인데 신입 모집이 어렵다."
}
```

| 필드 | 타입 | 제약 |
|------|------|------|
| `text` | string | 10자 이상, 1000자 이하 |

**응답 200** (`TagSuggestResponse`):

성공 시:
```json
{
  "success": true,
  "suggested_tags": ["중규모", "장기운영", "오프라인", "신입유치", "리텐션"],
  "processing_time_ms": 1820,
  "note": "AI 추천입니다. 자유롭게 편집하세요."
}
```

실패 시 (타임아웃 3초 초과 / API 키 미설정 / 파싱 실패) — **HTTP 200 유지**:
```json
{
  "success": false,
  "suggested_tags": [],
  "processing_time_ms": 3000,
  "note": "태그 추천에 실패했습니다. 직접 입력해 주세요."
}
```

> ⚠️ AI는 **태그 후보 추천만** 함. 매칭 로직에는 일절 개입하지 않음 (PRD §0).

**에러**:
- `401`: 인증 누락
- `422`: 텍스트 길이 위반

---

## 6. 매칭 플로우 (Matches)

### 매칭 상태 전이

```
[신청] pending
    ├── 수락 → accepted
    │       └── 결제 → paid → completed (만남 후, MVP 미구현)
    └── 거절 → rejected
```

| 상태 | 의미 |
|------|------|
| `pending` | 신청 후 수락 대기 |
| `accepted` | 수락됨, 결제 가능 |
| `rejected` | 거절됨 |
| `paid` | 결제 완료 (만남 예정) |
| `completed` | 만남 종료 (MVP 미구현, 데이터만 모델에 존재) |
| `cancelled` | 취소 (MVP UI mock, 실 정책 없음) |

### `initiated_by` 양방향 흐름

| 값 | 의미 | 수락 권한 | 결제 권한 |
|---|---|---|---|
| `taker` | Taker가 Giver에게 신청 | Giver | Taker |
| `giver` | Giver가 Taker 구인글에 신청 | Taker | Taker |

---

### 6.1 매칭 신청

```
POST /api/v1/matches
```

**인증**: 필요

**요청 (Taker → Giver, 케이스 1)**:
```json
{
  "target_type": "giver",
  "target_id": "<giver의 user_id>",
  "post_id": null,
  "format": "coffeechat",
  "message": "커피챗 부탁드립니다",
  "preferred_dates": ["2026-05-15T18:00:00+09:00", "2026-05-16T18:00:00+09:00"]
}
```

**요청 (Giver → Taker 구인글, 케이스 2)**:
```json
{
  "target_type": "taker_post",
  "target_id": "<taker_posts.id>",
  "format": "freechat",
  "message": "도와드리겠습니다",
  "preferred_dates": null
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `target_type` | `"giver"` \| `"taker_post"` | 양방향 구분 |
| `target_id` | UUID | giver: `user.id`, taker_post: `taker_posts.id` |
| `post_id` | UUID \| null | (선택) Taker가 본인 구인글과 신청 연결할 때 |
| `format` | [Format](#format) | `freechat`/`coffeechat`/`mealchat` |
| `message` | string | max 200자 |
| `preferred_dates` | array \| object \| null | 자유 형식 (ISO datetime 추천) |

**응답 201** (`MatchResponse`):
```json
{
  "id": "uuid",
  "taker_id": "uuid",
  "giver_id": "uuid",
  "taker_post_id": "uuid|null",
  "initiated_by": "taker",
  "format": "coffeechat",
  "message": "커피챗 부탁드립니다",
  "preferred_dates": [...],
  "status": "pending",
  "payment_amount": 14000,
  "payment_id": null,
  "created_at": "...",
  "accepted_at": null,
  "paid_at": null
}
```

> 📌 **`payment_amount`는 신청 시점의 Giver 가격 스냅샷**. 이후 Giver 가격이 변동해도 이 값은 불변.
> - `freechat` → 0
> - `coffeechat` → `giver_profile.coffeechat_price`
> - `mealchat` → `giver_profile.mealchat_price`

**에러**:
- `404` (`Target not found`): target_id에 해당하는 Giver/Post 없거나, Giver 프로필 없음, post_id가 본인 글 아님
- `409` (`A pending match already exists`): 동일 (taker_id, giver_id) 조합으로 pending 매칭이 이미 존재

---

### 6.2 내 매칭 목록

```
GET /api/v1/matches/me?type=sent
```

**인증**: 필요

**Query**:

| 이름 | 값 | 설명 |
|---|---|---|
| `type` | `sent` | 내가 신청한 것만 |
| `type` | `received` | 내가 받은 신청 |
| `type` | `matched` | 성사된 매칭 (`accepted`/`paid`/`completed`) |
| (생략) | — | 내가 taker 또는 giver인 모든 매칭 |

**응답 200**: `list[MatchResponse]` — 최근순, 최대 100개

---

### 6.3 매칭 수락

```
PATCH /api/v1/matches/{match_id}/accept
```

**인증**: 필요 (수신자만)

**응답 200**: `MatchResponse` (status=`accepted`, accepted_at 채워짐)

> 부수효과: 연결된 `taker_post`가 있으면 `status` → `matched`.

**에러**:
- `400` (`Invalid match state`): pending 아닌 상태에서 수락 시도
- `403` (`Not allowed`): 권한 없음 (자기가 신청한 걸 자기가 수락 등)
- `404`

---

### 6.4 매칭 거절

```
PATCH /api/v1/matches/{match_id}/reject
```

**인증**: 필요 (수신자만)

**요청**:
```json
{
  "reason": "time_mismatch"
}
```

| `reason` 값 |
|---|
| `time_mismatch` |
| `field_mismatch` |
| `other` |

**응답 200**: `MatchResponse` (status=`rejected`)

> 부수효과: Giver-initiated인 경우 연결된 `taker_post.application_count -= 1` (0 미만 방지).

**에러**: `400`, `403`, `404` (수락과 동일)

---

### 6.5 결제 Mock

```
POST /api/v1/matches/{match_id}/pay
```

**인증**: 필요 (Taker만)

> ⚠️ 동작:
> - `format='freechat'` → 즉시 `status='paid'`, `payment_id=null`
> - 그 외 → **2초 대기 (Mock)** 후 `payment_id="mock_xxxxxxxx"` 발급
> - 결제 완료 시 자동으로 Giver `match_count++`, `is_newbie` 재계산, 가격 재산정 (`SELECT FOR UPDATE` 잠금)

**응답 200**: `MatchResponse` (status=`paid`, paid_at, payment_id 포함)

**에러**:
- `400`: status가 `accepted`가 아님
- `403`: Taker가 아닌 사람이 결제 시도
- `404`

---

## 7. 커뮤니티 / 라운지

### 7.1 커뮤니티 글 작성

```
POST /api/v1/community/posts
```

**인증**: 필요

**요청**:
```json
{
  "title": "운영 노하우 공유",
  "body": "본문 내용...",
  "category": "giver"
}
```

| 필드 | 타입 | 제약 |
|------|------|------|
| `title` | string | 1~100자 |
| `body` | string | 1자 이상 |
| `category` | `"giver"` \| `"taker"` \| `"both"` | 필수 |

**응답 201** (`CommunityPostResponse`):
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "...",
  "body": "...",
  "category": "giver",
  "created_at": "...",
  "updated_at": "...",
  "author_nickname": "활성Giver"
}
```

---

### 7.2 커뮤니티 글 목록 (공개)

```
GET /api/v1/community/posts?category=giver&page=1&size=12
```

**Query**:

| 이름 | 타입 | 기본값 |
|---|---|---|
| `category` | `giver` \| `taker` \| `both` \| 생략 | 생략 시 전체 |
| `page` | int | `1` |
| `size` | int | `12` (1~100) |

**응답 200**:
```json
{
  "total": 8,
  "page": 1,
  "items": [ /* CommunityPostResponse[] */ ]
}
```

---

### 7.3 커뮤니티 글 단건 조회 (공개)

```
GET /api/v1/community/posts/{post_id}
```

**응답 200**: `CommunityPostResponse`
**에러**: `404`

---

### 7.4 커뮤니티 글 삭제

```
DELETE /api/v1/community/posts/{post_id}
```

**인증**: 필요 (작성자만)

**응답**: `204 No Content`
**에러**: `403`, `404`

---

## 8. 헬스체크

```
GET /health
```

**응답 200**:
```json
{ "status": "ok" }
```

---

## Enum 사전

### Category

Giver 운영 경험 / Taker 구인글 카테고리.

| 값 | 설명 |
|---|---|
| `network` | 네트워킹 / 컨퍼런스 |
| `league` | 스터디 / 리그 |
| `community` | 일반 커뮤니티 |
| `crew` | 크루 / 사이드 프로젝트 팀 |
| `circle` | 동아리 |
| `party` | 파티 / 이벤트 |

### Format

만남 형식.

| 값 | 의미 | 가격 |
|---|---|---|
| `freechat` | 무료 채팅/문의 | 0원 |
| `coffeechat` | 1:1 커피챗 | `coffeechat_price` (5,000~25,000원) |
| `mealchat` | 식사 미팅 | `mealchat_price` (10,000~50,000원) |

### Match Status

| 값 | 설명 |
|---|---|
| `pending` | 수락 대기 |
| `accepted` | 수락됨 |
| `rejected` | 거절됨 |
| `paid` | 결제 완료 |
| `completed` | 만남 종료 (MVP 미구현) |
| `cancelled` | 취소 (MVP UI mock) |

### Match initiated_by

| 값 | 설명 |
|---|---|
| `taker` | Taker → Giver 신청 |
| `giver` | Giver → Taker 구인글 신청 |

### Reject reason

| 값 |
|---|
| `time_mismatch` |
| `field_mismatch` |
| `other` |

### TakerPost status

| 값 | 설명 |
|---|---|
| `open` | 모집 중 |
| `matched` | 매칭 성사됨 (수락 시 자동 전환) |
| `closed` | 작성자가 마감 |

### Community category

| 값 | 노출 대상 |
|---|---|
| `giver` | Giver 라운지 |
| `taker` | Taker 라운지 |
| `both` | 공용 게시판 |

---

## 에러 포맷

FastAPI 표준 형식:

```json
{ "detail": "에러 메시지" }
```

Pydantic 검증 실패 (`422`):
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "text"],
      "msg": "String should have at least 10 characters",
      "input": "안녕"
    }
  ]
}
```

### 공통 HTTP 코드

| 코드 | 의미 |
|---|---|
| `200` | 정상 응답 |
| `201` | 생성 완료 |
| `204` | 삭제 완료 (본문 없음) |
| `400` | 잘못된 상태 전이 (매칭 등) |
| `401` | 인증 헤더 누락 |
| `403` | 권한 없음 (소유권/수락권한 위반) |
| `404` | 리소스 없음 |
| `409` | 중복 생성 (프로필/매칭 등) |
| `422` | 입력 검증 실패 (Pydantic) |
| `500` | 서버 내부 오류 |

---

## 통합 시나리오 예시

> 모든 예시는 `Base URL = http://localhost:8000`, prefix `/api/v1` 가정.

### 시나리오 A — Taker → Giver 매칭 (PRD §11.1)

```bash
# 1. 시드 유저 목록에서 Taker 선택
curl http://localhost:8000/api/v1/auth/users
# → Taker UUID = 9b2e3d4e-...

# 2. Giver 탐색 (블루오션 = 신규 Giver 우선)
curl 'http://localhost:8000/api/v1/discover/givers?sort=latest&size=12'

# 3. Giver 상세 조회 (Giver UUID = 8a1f2c3d-...)
curl http://localhost:8000/api/v1/givers/8a1f2c3d-...

# 4. 커피챗 신청 (Taker로 로그인)
curl -X POST http://localhost:8000/api/v1/matches \
  -H 'X-User-Id: 9b2e3d4e-...' \
  -H 'Content-Type: application/json' \
  -d '{
    "target_type": "giver",
    "target_id": "8a1f2c3d-...",
    "format": "coffeechat",
    "message": "커피챗 신청합니다",
    "preferred_dates": ["2026-05-15T18:00:00+09:00"]
  }'
# → match_id, payment_amount=14000

# 5. Giver로 전환해서 수락
curl -X PATCH http://localhost:8000/api/v1/matches/<match_id>/accept \
  -H 'X-User-Id: 8a1f2c3d-...'

# 6. Taker가 결제 (2초 대기 후 mock_xxxxxxxx 발급)
curl -X POST http://localhost:8000/api/v1/matches/<match_id>/pay \
  -H 'X-User-Id: 9b2e3d4e-...'
```

### 시나리오 B — Giver → Taker 구인글 매칭

```bash
# 1. 구인글 탐색 (블루오션 정렬)
curl 'http://localhost:8000/api/v1/discover/posts?sort=applications_asc&active_only=true'

# 2. 구인글에 "도와드리겠습니다" (Giver로 로그인)
curl -X POST http://localhost:8000/api/v1/matches \
  -H 'X-User-Id: 8a1f2c3d-...' \
  -H 'Content-Type: application/json' \
  -d '{
    "target_type": "taker_post",
    "target_id": "<post_id>",
    "format": "freechat",
    "message": "도와드리겠습니다"
  }'
# → application_count++, payment_amount=0

# 3. Taker로 전환해서 수락
curl -X PATCH http://localhost:8000/api/v1/matches/<match_id>/accept \
  -H 'X-User-Id: <taker_id>'
# → 구인글 status='matched'로 자동 전환

# 4. freechat이라 결제 단계 즉시 처리 (Mock 2초 없음)
curl -X POST http://localhost:8000/api/v1/matches/<match_id>/pay \
  -H 'X-User-Id: <taker_id>'
```

### 시나리오 C — AI 태그 추천

```bash
# 1. 구인글 본문을 입력하다가 "AI 태그 추천" 클릭
curl -X POST http://localhost:8000/api/v1/ai/suggest-tags \
  -H 'X-User-Id: <user_id>' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "30명 규모 보드게임 동아리를 1년째 운영 중인데 신입 모집이 어렵다."
  }'
# → suggested_tags: ["중규모", "장기운영", "오프라인", "신입유치", "리텐션"]
# → 사용자가 일부 수락/거절 후 직접 편집한 최종 태그로 글 등록
```

---

## 부록 — 시드 데이터 요약

`python scripts/seed.py`로 채워지는 데이터 (PRD §10.2 P0 데모용).

### Giver 5명

| 닉네임 | match_count | rating | coffee/meal | 특징 |
|---|---|---|---|---|
| 신규Giver | 0 | 0.00 | 5,000 / 10,000 | Cold start |
| 입문Giver | 5 | 4.00 | 8,500 / 16,000 | newbie 졸업 직전 |
| 활성Giver | 15 | 4.50 | 14,000 / 28,000 | 표준 |
| 인기Giver | 30 | 4.80 | 23,000 / 45,000 | 상위권 |
| 저평점Giver | 20 | 3.20 | 9,500 / 18,000 | 활동량 많지만 평점 낮음 |

### Taker 구인글 5건

| 작성자 | 카테고리 | format | 예산 |
|---|---|---|---|
| 동아리회장A | circle | coffeechat | 5,000 ~ 15,000 |
| 디스코드운영자B | community | mealchat | 10,000 ~ 30,000 |
| 스터디그룹장C | league | freechat | 0 ~ 0 |
| 사이드팀장D | crew | coffeechat | 8,000 ~ 20,000 |
| 행사기획E | party | mealchat | 15,000 ~ 40,000 |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|---|---|---|
| v0.1.0 | 2026-05-10 | 해커톤 MVP 초안 (Phase 0~8 통합) |
