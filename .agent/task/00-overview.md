# GIVE:RUN Backend — 워크플로우 전체 지도

> PRD 기준: `prd.md` (해커톤 MVP)  
> 스택: FastAPI 3.11 · SQLAlchemy 2.0 async · PostgreSQL (GCP Docker) · Gemini 3.1 Flash  
> ⚠️ **인증**: 해커톤 특성상 카카오 OAuth 대신 목데이터(시드 유저) 기반 dev-login 사용

---

## 1. Phase 의존성 그래프

```
Phase 0 (부트스트랩)
    └── Phase 1 (DB 스키마 & 모델)
            ├── Phase 2 (dev-login) ← 카카오 OAuth 대신 목데이터 기반 간단 인증
            │       └── Phase 3 (Giver/Taker 작성 API)
            │               ├── Phase 4 (양방향 탐색 API) ⭐
            │               ├── Phase 5 (AI 태그 추천)
            │               └── Phase 6 (매칭 플로우)
            │                       └── Phase 7 (통합 검증 & 데모)
            └── (시드 데이터 — Phase 1 완료 후 즉시 실행)
```

Phase 4·5·6은 Phase 3 완료 후 **병렬 진행 가능**.

---

## 2. PRD 우선순위 매핑

| Phase | PRD 우선순위 | FR 식별자 | 해커톤 일정 |
|-------|------------|-----------|------------|
| 0 — 부트스트랩 | 🔴 P0 | — | Day 1 AM |
| 1 — DB 스키마 | 🔴 P0 | §7 Data Model | Day 1 AM |
| 2 — dev-login (인증 간소화) | 🔴 P0 | — | Day 1 PM |
| 3 — Giver/Taker 작성 | 🔴 P0 | FR-GIVER-01~03, FR-TAKER-01 | Day 1 PM |
| 4 — 양방향 탐색 ⭐ | 🔴 P0 | FR-DISCOVER-01~03 | Day 2 AM |
| 5 — AI 태그 추천 | 🔴 P0 | FR-GIVER-04, FR-TAKER-02 | Day 2 PM |
| 6 — 매칭 플로우 | 🟠 P1 | FR-FLOW-01~04 | Day 2 PM |
| 7 — 통합 검증 | 🟠 P1 | §11 KPI | Day 3 AM |

---

## 3. 디렉토리 구조 (최종 목표)

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
│   │   └── jwt.py               # JWT 발급·검증, get_current_user (dev-login용)
│   ├── models/
│   │   ├── db/                  # SQLAlchemy ORM 모델
│   │   │   ├── user.py
│   │   │   ├── giver.py
│   │   │   ├── post.py
│   │   │   ├── tag.py
│   │   │   └── match.py
│   │   └── schemas/             # Pydantic 스키마 (Base/Create/Update/Response)
│   │       ├── user.py
│   │       ├── giver.py
│   │       ├── post.py
│   │       ├── tag.py
│   │       └── match.py
│   ├── routers/
│   │   ├── auth.py              # /auth/*
│   │   ├── givers.py            # /givers/*
│   │   ├── posts.py             # /posts/*
│   │   ├── discover.py          # /discover/*
│   │   ├── ai.py                # /ai/*
│   │   └── matches.py           # /matches/*
│   └── services/
│       ├── pricing.py           # recalculate_giver_pricing()
│       ├── giver_service.py
│       ├── post_service.py
│       ├── discover_service.py
│       ├── ai_service.py
│       └── match_service.py
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema.py
├── scripts/
│   └── seed.py                  # 시드 데이터 (Giver 5명, 구인글 5건)
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_discover.py         # ⭐ 양방향 탐색 핵심 테스트
│   ├── test_pricing.py          # 가격 산정 단위 테스트
│   └── test_match_flow.py
├── pyproject.toml
├── Dockerfile
├── .env.example
└── alembic.ini
```

---

## 4. 핵심 설계 결정 (PRD 준수)

| 결정 | 근거 |
|------|------|
| pgvector 미사용 | PRD §7 명시: "일반 인덱싱으로 검색 처리" |
| AI는 태그 추천 단일 용도 | PRD §0 핵심 설계 원칙 2 |
| Giver 가격 입력 불가 | PRD FR-GIVER-03: 시스템 자동 산정 |
| `initiated_by` 컬럼으로 양방향 추적 | PRD §7 matches 테이블 |
| 결제는 Mock | PRD FR-FLOW-03 |
| 인증은 dev-login (목데이터 기반) | 해커톤 특성상 카카오 OAuth 생략 |
| JWT httpOnly 쿠키 | PRD §5 보안 요구사항 (dev-login에서도 동일 방식 사용) |

---

## 5. 비기능 요구사항 체크포인트

| 항목 | 목표 | 검증 방법 |
|------|------|----------|
| 검색 응답 | < 1초 | Phase 7 통합 테스트 |
| AI 태그 추천 | < 3초 | Phase 5 타임아웃 설정 |
| 페이지 로딩 | < 2초 | Cloud Run 배포 후 확인 |
| SQL Injection 방어 | ORM 사용 | SQLAlchemy 파라미터 바인딩 |

---

## 6. Out of Scope (MVP에서 제외)

PRD §12 기준:
- 실 결제 (토스페이먼츠)
- 채팅 / 실시간 알림
- 평점·후기 시스템 (UI mock만)
- AI 기반 매칭 추천 / 임베딩
- 푸시 알림 / 어드민 대시보드
- Giver 등급제
