# Phase 2 — dev-login (목데이터 기반 인증)

> **목표**: 시드 유저 중 한 명으로 로그인하면 JWT가 발급되고, 이후 인증이 필요한 엔드포인트에서 `get_current_user`가 정상 동작한다.
>
> ⚠️ **해커톤 결정**: 카카오 OAuth는 앱 등록·심사 시간 비용이 크므로 생략. 시드 유저 ID를 직접 지정하는 `POST /auth/dev-login`으로 대체한다.

| 항목 | 내용 |
|------|------|
| PRD 매핑 | FR-AUTH-01, FR-AUTH-02 (간소화 구현) |
| 해커톤 일정 | Day 1 PM (4~6h) |
| 선행 의존성 | Phase 1 완료 (users 테이블 + 시드 유저 존재) |
| 후속 Phase | Phase 3 (Giver/Taker 작성 API) |

---

## 작업 체크리스트

### 1. JWT 유틸리티 (`app/auth/jwt.py`)

- [ ] `create_access_token(user_id: str) -> str` — JWT 생성
  - payload: `{"sub": user_id, "exp": now + 7days}`
  - 알고리즘: HS256, 시크릿: `settings.JWT_SECRET`
- [ ] `decode_access_token(token: str) -> str | None` — JWT 검증 → user_id 반환
- [ ] `get_current_user(request: Request, db: AsyncSession) -> User | None` — 쿠키에서 JWT 추출 → User 조회 (인증 선택적)
- [ ] `get_current_user_required(...)` — 인증 필수 버전, 미인증 시 HTTP 401

### 2. 인증 라우터 (`app/routers/auth.py`)

- [ ] `POST /api/v1/auth/dev-login`
  - Request body: `{"user_id": "<시드 유저 UUID>"}`
  - DB에서 해당 user_id 조회 → 없으면 HTTP 404
  - JWT 생성 → httpOnly 쿠키 설정
    ```python
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,   # 로컬/데모 환경
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7일
    )
    ```
  - Response: `UserResponse`

- [ ] `POST /api/v1/auth/logout`
  - 쿠키 삭제 (`response.delete_cookie("access_token")`)
  - `{"message": "logged out"}`

- [ ] `GET /api/v1/auth/me` 🔒
  - 현재 로그인된 유저 정보 반환
  - Response: `UserResponse`

### 3. Pydantic 스키마 (`app/models/schemas/auth.py`)

- [ ] `DevLoginRequest` — `user_id: UUID`

---

## 시드 유저 목록 (데모용)

`scripts/seed.py`에서 생성되는 유저 UUID를 고정값으로 사용:

| 역할 | nickname | UUID (고정) |
|------|----------|------------|
| Giver | 김운영 | `00000000-0000-0000-0000-000000000001` |
| Giver | 이커뮤 | `00000000-0000-0000-0000-000000000002` |
| Giver | 박리더 | `00000000-0000-0000-0000-000000000003` |
| Giver | 최활성 | `00000000-0000-0000-0000-000000000004` |
| Giver | 정인기 | `00000000-0000-0000-0000-000000000005` |
| Taker | 한구인 | `00000000-0000-0000-0000-000000000006` |
| Taker | 오탐색 | `00000000-0000-0000-0000-000000000007` |

---

## 산출 파일 트리

```
Backend/
└── app/
    ├── auth/
    │   └── jwt.py
    ├── routers/
    │   └── auth.py
    └── models/
        └── schemas/
            └── auth.py
```

`app/main.py`에 라우터 마운트 추가:
```python
from app.routers import auth
app.include_router(auth.router, prefix="/api/v1")
```

---

## 검증 기준 (DoD)

| 검증 항목 | 방법 | 기대 결과 |
|----------|------|----------|
| dev-login | `POST /auth/dev-login {"user_id": "00000000-...01"}` | `access_token` httpOnly 쿠키 설정됨 |
| 인증 필요 엔드포인트 | 쿠키 없이 `GET /auth/me` | HTTP 401 |
| 인증 후 me 조회 | dev-login 후 `GET /auth/me` | 해당 유저 정보 반환 |
| 로그아웃 | `POST /auth/logout` | 쿠키 삭제됨 |
| 잘못된 user_id | 존재하지 않는 UUID로 dev-login | HTTP 404 |

---

## 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| 시드 유저 미생성 상태에서 dev-login | Phase 1 시드 실행 선행 필수 (`python scripts/seed.py`) |
| JWT_SECRET 미설정 | 서버 기동 시 `settings.JWT_SECRET` 검증, 없으면 기동 실패 |
