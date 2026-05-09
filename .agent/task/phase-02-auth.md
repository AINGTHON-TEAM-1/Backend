# Phase 2 — 유저 스위처 (auth 사실상 생략)

> **목표**: 시드 유저 10명 중 한 명의 ID를 `X-User-Id` 헤더로 보내면, 그 사용자로 행세하는 것처럼 동작한다. JWT/쿠키/카카오/비밀번호 모두 없음.
>
> ⚠️ **해커톤 결정 (변경 사항)**: 원래 dev-login(JWT 발급)을 계획했으나, 발표자 합의로 **유저 스위처** 방식으로 한 단계 더 단순화. 핵심 매칭 ownership(`taker_id/giver_id` 식별)은 유지하면서 인증 코드를 ~40 LOC 미만으로 축소.
>
> 프로덕션 전환 시 `get_current_user` 내부 구현만 OAuth로 교체.

| 항목 | 내용 |
|------|------|
| PRD 매핑 | FR-AUTH-01, FR-AUTH-02 (간소화 구현) |
| 해커톤 일정 | Day 1 PM (1~2h, 원래 계획 대비 절반 이하) |
| 선행 의존성 | Phase 1 완료 (users 테이블 + 시드 유저 존재) |
| 후속 Phase | Phase 3 (Giver/Taker 작성 API) |

---

## 동작 흐름

```
[프론트 로그인 화면]
    └── GET /api/v1/auth/users  →  시드 유저 10명 카드 표시
[유저 카드 클릭]
    └── localStorage.setItem('userId', <UUID>)
[이후 모든 API 호출]
    └── 헤더에 X-User-Id: <UUID> 자동 첨부 (axios 인터셉터)
```

---

## 작업 체크리스트

### 1. 의존성 (`app/auth/dev.py`)

- [ ] `get_current_user(x_user_id: UUID = Header(...), db) -> User`
  - 헤더 없으면 HTTP 401
  - 유저 미존재면 HTTP 404
- [ ] `get_current_user_optional(...)` — 헤더 없거나 미존재 시 `None` 반환 (공개 엔드포인트에서 "현재 유저가 봤는지" 추적용 — Phase 4에서 필요할 수도)

### 2. 인증 라우터 (`app/routers/auth.py`)

- [ ] `GET /api/v1/auth/users` — 시드 유저 리스트 (프론트 로그인 화면용)
  - Response: `list[UserResponse]`
  - 인증 불필요 (로그인 화면이므로)
- [ ] `GET /api/v1/auth/me` — 현재 유저 (X-User-Id 기반)
  - 인증 필수
  - Response: `UserResponse`

### 3. main.py 라우터 마운트

```python
from app.routers import auth
app.include_router(auth.router, prefix="/api/v1")
```

---

## 산출 파일 트리

```
Backend/
└── app/
    ├── auth/
    │   ├── __init__.py
    │   └── dev.py              # get_current_user 의존성
    ├── routers/
    │   ├── __init__.py
    │   └── auth.py             # /auth/users, /auth/me
    └── main.py                 # 라우터 마운트 추가
```

---

## 검증 기준 (DoD)

| 검증 항목 | 방법 | 기대 결과 |
|----------|------|----------|
| 시드 유저 리스트 | `GET /api/v1/auth/users` (헤더 없이) | HTTP 200, 10명 |
| 인증 필요 + 헤더 없음 | `GET /api/v1/auth/me` (헤더 없이) | HTTP 401 |
| 인증 후 me 조회 | `GET /api/v1/auth/me -H 'X-User-Id: <시드 UUID>'` | HTTP 200, 해당 유저 |
| 존재하지 않는 UUID | `GET /api/v1/auth/me -H 'X-User-Id: 00000000-...'` | HTTP 404 |

---

## 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| 시드 유저 미생성 상태 | Phase 1 시드 실행 선행 (`PYTHONPATH=. python scripts/seed.py`) |
| 외부 노출 시 누구나 임의 유저 행세 | 데모 모드임을 README 명시. 외부 도메인 배포 금지 |
| 라우터 의존성 어긋남 | 모든 인증 필요 라우터는 동일하게 `Depends(get_current_user)` 사용 (FastAPI skill 컨벤션) |

---

## 프로덕션 전환 시 (참고)

```python
# 현재 (데모)
async def get_current_user(x_user_id: UUID = Header(...), db) -> User:
    user = await db.get(User, x_user_id)
    ...

# 프로덕션 (카카오 OAuth + JWT)
async def get_current_user(request: Request, db) -> User:
    token = request.cookies.get("access_token")
    payload = jwt.decode(token, settings.jwt_secret, ...)
    user = await db.get(User, payload["sub"])
    ...
```

→ **라우터/서비스 코드는 한 줄도 안 바뀜**. 의존성 내부만 교체.
