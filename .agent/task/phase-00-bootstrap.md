# Phase 0 — 프로젝트 부트스트랩

> **목표**: FastAPI 백엔드가 로컬에서 실행되고, DB 연결이 확인되는 최소 골격을 만든다.

| 항목 | 내용 |
|------|------|
| PRD 매핑 | §9.1 Tech Stack, §9.3 환경변수 |
| 해커톤 일정 | Day 1 AM (0~2h) |
| 선행 의존성 | 없음 (시작점) |
| 후속 Phase | Phase 1 (DB 스키마) |

---

## 작업 체크리스트

### 1. 패키지 설정
- [ ] `pyproject.toml` 생성 (hatch 또는 poetry 기반)
  - 의존성: `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]>=2.0`, `asyncpg`, `pydantic>=2.0`, `pydantic-settings`, `python-jose[cryptography]`, `httpx`, `google-generativeai`, `alembic`
  - dev 의존성: `pytest`, `pytest-asyncio`, `httpx`

### 2. 환경변수
- [ ] `.env.example` 생성 (PRD §9.3 기준)
  ```
  DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/giverun
  JWT_SECRET=...
  KAKAO_CLIENT_ID=...
  KAKAO_CLIENT_SECRET=...
  KAKAO_REDIRECT_URI=http://localhost:8000/api/v1/auth/kakao/callback
  GEMINI_API_KEY=...
  ```
- [ ] `app/core/config.py` — `pydantic-settings`의 `BaseSettings`로 환경변수 로딩

### 2-1. PostgreSQL Docker 설정 (로컬 개발용)
- [ ] `docker-compose.yml` 생성 — 로컬 개발 시 PostgreSQL 컨테이너 실행
  ```yaml
  services:
    db:
      image: postgres:16-alpine
      environment:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: password
        POSTGRES_DB: giverun
      ports:
        - "5432:5432"
      volumes:
        - postgres_data:/var/lib/postgresql/data
  volumes:
    postgres_data:
  ```
- [ ] 로컬 DB 기동: `docker compose up -d db`

### 3. DB 연결
- [ ] `app/db/base.py` — `DeclarativeBase` 정의
- [ ] `app/db/session.py` — `create_async_engine` + `AsyncSession` 팩토리 + `get_db` 의존성

### 4. FastAPI 앱 진입점
- [ ] `app/main.py`
  - `FastAPI(title="GIVE:RUN API", version="0.1.0")`
  - CORS 미들웨어 (프론트엔드 도메인 허용)
  - 라우터 마운트 자리 확보 (`/api/v1` prefix)
  - 헬스체크: `GET /health` → `{"status": "ok"}`

### 5. Alembic 초기화
- [ ] `alembic init alembic`
- [ ] `alembic/env.py` — async 엔진 연결 설정, `target_metadata` 연결

### 6. Dockerfile
- [ ] `Dockerfile` (Cloud Run 배포 대비, PRD §9.1)
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY pyproject.toml .
  RUN pip install .
  COPY app/ app/
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
  ```

---

## 산출 파일 트리

```
Backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   └── config.py
│   └── db/
│       ├── base.py
│       └── session.py
├── alembic/
│   ├── env.py
│   └── versions/   (비어있음)
├── docker-compose.yml
├── pyproject.toml
├── Dockerfile
├── .env.example
└── alembic.ini
```

---

## 검증 기준 (DoD)

| 검증 항목 | 명령 | 기대 결과 |
|----------|------|----------|
| 서버 기동 | `uvicorn app.main:app --reload` | 오류 없이 기동 |
| 헬스체크 | `curl http://localhost:8000/health` | `{"status":"ok"}` |
| DB 연결 | `alembic current` | 오류 없이 실행 |
| 환경변수 로딩 | Python REPL에서 `from app.core.config import settings` | 오류 없음 |

---

## 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| asyncpg 설치 실패 (C 컴파일러 필요) | `pip install asyncpg --pre` 또는 Docker 내 빌드 |
| PostgreSQL 컨테이너 미기동 | `docker compose up -d db` 후 재시도 |
