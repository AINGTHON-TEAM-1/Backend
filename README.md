# GIVE:RUN — Backend

> **"운영하는 사람들의 첫 만남을 5분 안에 만든다."**

커뮤니티를 만들고 싶은 대학생(Taker)과, 커뮤니티를 성공적으로 운영해본 사람(Giver)을 연결하는 **양방향 매칭 플랫폼**의 백엔드 서버입니다.

---

## 목차

- [서비스 소개](#서비스-소개)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [API 엔드포인트](#api-엔드포인트)
- [로컬 개발 환경 설정](#로컬-개발-환경-설정)
- [환경변수](#환경변수)
- [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
- [시드 데이터](#시드-데이터)
- [배포](#배포)
- [Git 컨벤션](#git-컨벤션)
- [문의](#문의)
- [라이선스](#라이선스)

---

## 서비스 소개

### 핵심 기능

| 기능 | 설명 |
|------|------|
| **양방향 탐색** | Taker가 Giver를 찾거나, Giver가 Taker 구인글을 찾을 수 있음 |
| **AI 태그 추천** | Gemini 기반 태그 자동 추천 (결정은 사용자가 직접) |
| **가격 자동 산정** | 평점(60%) + 활동량(40%) 기반 Giver 가격 자동 계산 |
| **매칭 플로우** | 신청 → 수락 → 결제(Mock) → 완료 상태 전이 |
| **커뮤니티/라운지** | Giver·Taker 자유 게시판 |

### 설계 원칙

1. **양방향 탐색**: Taker → Giver 탐색, Giver → Taker 구인글 탐색 모두 지원
2. **AI는 보조 도구**: 태그 추천에만 활용. 매칭 로직에 AI 개입 없음

---

## 기술 스택

| 항목 | 기술 |
|------|------|
| 언어 | Python 3.11 |
| 웹 프레임워크 | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| DB | PostgreSQL 16 (GCP Docker) |
| 마이그레이션 | Alembic |
| AI | Google Gemini 3.1 Flash |
| 인증 | JWT (httpOnly 쿠키) |
| 배포 | GCP Cloud Run |

---

## 프로젝트 구조

```
Backend/
├── app/
│   ├── main.py                  # FastAPI 앱 + 라우터 마운트
│   ├── core/
│   │   └── config.py            # Pydantic Settings (환경변수)
│   ├── db/
│   │   ├── session.py           # async engine + session
│   │   └── base.py              # DeclarativeBase
│   ├── auth/
│   │   └── jwt.py               # JWT 발급·검증, get_current_user
│   ├── models/
│   │   ├── db/                  # SQLAlchemy ORM 모델
│   │   │   ├── user.py
│   │   │   ├── giver.py
│   │   │   ├── post.py
│   │   │   ├── tag.py
│   │   │   ├── match.py
│   │   │   └── community.py
│   │   └── schemas/             # Pydantic 스키마
│   │       ├── user.py
│   │       ├── giver.py
│   │       ├── post.py
│   │       ├── tag.py
│   │       ├── match.py
│   │       ├── auth.py
│   │       ├── discover.py
│   │       ├── ai.py
│   │       └── community.py
│   ├── routers/
│   │   ├── auth.py              # /api/v1/auth/*
│   │   ├── givers.py            # /api/v1/givers/*
│   │   ├── posts.py             # /api/v1/posts/*
│   │   ├── discover.py          # /api/v1/discover/*
│   │   ├── ai.py                # /api/v1/ai/*
│   │   ├── matches.py           # /api/v1/matches/*
│   │   └── community.py         # /api/v1/community/*
│   └── services/
│       ├── pricing.py           # 가격 자동 산정 (순수 함수)
│       ├── giver_service.py
│       ├── post_service.py
│       ├── discover_service.py
│       ├── ai_service.py
│       ├── match_service.py
│       └── community_service.py
├── alembic/
│   ├── env.py
│   └── versions/
│       ├── 001_initial_schema.py
│       └── 002_community.py
├── scripts/
│   └── seed.py                  # 시드 데이터 (Giver 5명, 구인글 5건)
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_discover.py
│   ├── test_pricing.py
│   └── test_match_flow.py
├── docker-compose.yml           # 로컬 개발용 PostgreSQL
├── pyproject.toml
├── Dockerfile
├── .env.example
└── alembic.ini
```

---

## API 엔드포인트

### 인증 (`/api/v1/auth`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/auth/dev-login` | 시드 유저 UUID로 로그인 (JWT 쿠키 발급) |
| `POST` | `/auth/logout` | 로그아웃 (쿠키 삭제) |
| `GET` | `/auth/me` 🔒 | 현재 로그인 유저 정보 |

### Giver (`/api/v1/givers`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/givers/profile` 🔒 | Giver 프로필 등록 |
| `GET` | `/givers/{giver_id}` | Giver 프로필 상세 조회 |
| `PATCH` | `/givers/profile` 🔒 | 내 프로필 수정 |
| `POST` | `/givers/experiences` 🔒 | 운영 경험 등록 |

### 구인글 (`/api/v1/posts`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/posts` 🔒 | 구인글 작성 |
| `GET` | `/posts/{post_id}` | 구인글 상세 조회 |
| `PATCH` | `/posts/{post_id}` 🔒 | 구인글 수정 |
| `DELETE` | `/posts/{post_id}` 🔒 | 구인글 삭제 |

### 양방향 탐색 (`/api/v1/discover`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/discover/givers` | Giver 탐색 (검색·필터·정렬·페이지네이션) |
| `GET` | `/discover/posts` | 구인글 탐색 (FTS·블루오션 정렬) |
| `GET` | `/discover/popular-tags` | 인기 태그 Top 10 |

**Giver 탐색 쿼리 파라미터**: `q`, `categories`, `format`, `price_min`, `price_max`, `rating_min`, `tag`, `sort` (`latest`/`rating`/`popular`/`price_asc`), `page`, `size`

**구인글 탐색 쿼리 파라미터**: `q`, `categories`, `format`, `budget_min`, `budget_max`, `active_only`, `tag`, `sort` (`latest`/`applications_asc`/`budget_desc`), `page`, `size`

### AI 태그 추천 (`/api/v1/ai`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/ai/suggest-tags` 🔒 | 텍스트 기반 태그 5개 추천 (3초 타임아웃) |

### 매칭 (`/api/v1/matches`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/matches` 🔒 | 매칭 신청 (Taker→Giver / Giver→Taker 양방향) |
| `GET` | `/matches/me` 🔒 | 내 매칭 목록 |
| `PATCH` | `/matches/{id}/accept` 🔒 | 수락 |
| `PATCH` | `/matches/{id}/reject` 🔒 | 거절 |
| `POST` | `/matches/{id}/pay` 🔒 | 결제 Mock (2초 딜레이) |

### 커뮤니티 (`/api/v1/community`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/community/posts` 🔒 | 글 작성 |
| `GET` | `/community/posts` | 글 목록 (카테고리 필터, 페이지네이션) |
| `GET` | `/community/posts/{post_id}` | 글 상세 |
| `DELETE` | `/community/posts/{post_id}` 🔒 | 글 삭제 |

> 🔒 = 인증 필요 (JWT 쿠키)

---

## 로컬 개발 환경 설정

### 1. 저장소 클론

```bash
git clone https://github.com/AINGTHON-TEAM-1/Backend.git
cd Backend
```

### 2. 의존성 설치

```bash
pip install -e ".[dev]"
```

### 3. PostgreSQL 컨테이너 실행

```bash
docker compose up -d db
```

### 4. 환경변수 설정

```bash
cp .env.example .env
# .env 파일에서 JWT_SECRET, GEMINI_API_KEY 등 설정
```

### 5. DB 마이그레이션 & 시드 데이터

```bash
alembic upgrade head
python scripts/seed.py
```

### 6. 서버 실행

```bash
uvicorn app.main:app --reload
```

서버 기동 후 `http://localhost:8000/docs` 에서 Swagger UI 확인 가능.

---

## 환경변수

`.env.example` 참고:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/giverun
JWT_SECRET=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
```

---

## 데이터베이스 마이그레이션

```bash
# 마이그레이션 적용
alembic upgrade head

# 현재 상태 확인
alembic current

# 새 마이그레이션 생성
alembic revision --autogenerate -m "description"
```

---

## 시드 데이터

데모용 고정 UUID 시드 유저:

| 역할 | nickname | UUID |
|------|----------|------|
| Giver | 김운영 | `00000000-0000-0000-0000-000000000001` |
| Giver | 이커뮤 | `00000000-0000-0000-0000-000000000002` |
| Giver | 박리더 | `00000000-0000-0000-0000-000000000003` |
| Giver | 최활성 | `00000000-0000-0000-0000-000000000004` |
| Giver | 정인기 | `00000000-0000-0000-0000-000000000005` |
| Taker | 한구인 | `00000000-0000-0000-0000-000000000006` |
| Taker | 오탐색 | `00000000-0000-0000-0000-000000000007` |

```bash
python scripts/seed.py
```

dev-login 예시:
```bash
curl -X POST http://localhost:8000/api/v1/auth/dev-login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "00000000-0000-0000-0000-000000000001"}'
```

---

## 배포

### GCP Cloud Run + PostgreSQL Docker

**PostgreSQL (GCP Compute Engine VM)**:
```bash
docker run -d \
  --name giverun-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=<SECRET> \
  -e POSTGRES_DB=giverun \
  -p 5432:5432 \
  postgres:16-alpine
```

**FastAPI (Cloud Run)**:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/give-run-api

gcloud run deploy give-run-api \
  --image gcr.io/PROJECT_ID/give-run-api \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=...,JWT_SECRET=...,GEMINI_API_KEY=...
```

---

## 테스트

```bash
# 전체 테스트
pytest

# 가격 산정 단위 테스트
pytest tests/test_pricing.py -v

# 탐색 통합 테스트
pytest tests/test_discover.py -v
```

---

## 헬스체크

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

---

## Git 컨벤션

### 브랜치 전략

```
main          ← 배포 브랜치 (직접 push 금지)
develop       ← 통합 브랜치
feat/<name>   ← 기능 개발
fix/<name>    ← 버그 수정
chore/<name>  ← 설정·의존성·문서 등 기타
```

### 커밋 메시지

```
<type>: <subject>

[optional body]
```

| type | 설명 |
|------|------|
| `feat` | 새 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 수정 |
| `style` | 코드 포맷·세미콜론 등 (로직 변경 없음) |
| `refactor` | 리팩토링 (기능 변경 없음) |
| `test` | 테스트 추가·수정 |
| `chore` | 빌드·설정·의존성 변경 |

**예시**:
```
feat: Giver 프로필 등록 API 구현
fix: 매칭 수락 시 소유권 검증 누락 수정
docs: README 배포 섹션 추가
chore: asyncpg 의존성 추가
```

### Pull Request

- PR 제목은 커밋 메시지 형식과 동일하게 작성
- 최소 1명 리뷰 후 merge
- `develop` → `main` merge는 배포 직전에만

---

## 문의

버그 리포트, 기능 제안, 질문은 모두 **GitHub Issues**를 이용해 주세요.

👉 [Issues 바로가기](https://github.com/AINGTHON-TEAM-1/Backend/issues)

---

## 라이선스

```
MIT License

Copyright (c) 2026 AINGTHON TEAM 1

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
