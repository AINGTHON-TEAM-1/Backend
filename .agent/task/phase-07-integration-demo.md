# Phase 7 — 통합 검증 & 데모 배포

> **목표**: 5개 핵심 플로우가 막힘 없이 시연 가능하고, Cloud Run에 배포되어 데모 준비가 완료된다.

| 항목 | 내용 |
|------|------|
| PRD 매핑 | §10.2 P0 기능 목록, §11.1 해커톤 KPI, §10.3 위험 요소 |
| 해커톤 일정 | Day 3 AM (22~28h) |
| 선행 의존성 | Phase 4, 5, 6 모두 완료 |
| 후속 Phase | 없음 (최종 단계) |

---

## 데모 시나리오 (PRD §11.1 KPI 기준)

### 시나리오 A — Taker 능동 탐색형 (경로 B)
```
1. Taker dev-login (시드 유저 UUID 사용)
2. Giver 탐색 페이지 → 검색·필터 사용
3. Giver 카드 클릭 → 상세 페이지
4. "커피챗 신청" → 신청 폼 작성
5. Giver dev-login으로 전환 → 수락 → 결제 Mock → 매칭 완료
```

### 시나리오 B — Giver 능동 탐색형 (양방향 핵심 데모)
```
1. Giver dev-login (시드 유저 UUID 사용)
2. Taker 구인글 탐색 → "신청 적은 순" 정렬
3. 구인글 클릭 → "도와드리겠습니다" 신청
4. Taker dev-login으로 전환 → 수락 → 매칭 완료
```

### 시나리오 C — AI 태그 추천 데모
```
1. 구인글 작성 중 본문 입력
2. "AI 태그 추천 받기" 클릭 → 스피너 → 5개 태그 제안
3. 일부 수락, 일부 거절, 직접 추가
4. 최종 태그로 등록
```

---

## 작업 체크리스트

### 1. 통합 테스트 (`tests/`)

#### `tests/conftest.py`
- [ ] 테스트용 async DB 세션 픽스처
- [ ] 테스트용 FastAPI 클라이언트 (`AsyncClient`)
- [ ] 테스트 사용자 생성 헬퍼 (Giver, Taker 각 1명)

#### `tests/test_pricing.py` — 가격 산정 단위 테스트
- [ ] PRD §8.2 표의 5가지 시나리오 파라미터화 테스트
  ```python
  @pytest.mark.parametrize("match_count,rating_avg,expected_coffee,expected_meal", [
      (0, 0.0, 5000, 10000),    # A: 신규
      (5, 4.0, 11500, 23500),   # B: 입문
      (15, 4.5, 17500, 35000),  # C: 활성
      (30, 4.8, 23500, 47500),  # D: 인기
      (20, 3.2, 11000, 22500),  # E: 저평점
  ])
  def test_pricing(match_count, rating_avg, expected_coffee, expected_meal):
      coffee, meal = recalculate_giver_pricing(match_count, rating_avg)
      assert coffee == expected_coffee
      assert meal == expected_meal
  ```

#### `tests/test_discover.py` — 양방향 탐색 통합 테스트
- [ ] Giver 탐색: 기본 목록, 텍스트 검색, 카테고리 필터, 평점 정렬
- [ ] Post 탐색: 기본 목록, FTS 검색, 블루오션 정렬, 상태 필터
- [ ] 인기 태그 조회
- [ ] 응답 시간 < 1초 검증 (시드 데이터 기준)

#### `tests/test_match_flow.py` — 매칭 플로우 통합 테스트
- [ ] 시나리오 A: Taker→Giver 신청 → 수락 → 결제 전체 플로우
- [ ] 시나리오 B: Giver→Taker 신청 → 수락 전체 플로우
- [ ] 상태 전이 오류 케이스 (잘못된 상태에서 수락 시도 등)
- [ ] 가격 스냅샷 검증 (결제 후 Giver 가격 변경해도 payment_amount 불변)

### 2. OpenAPI 문서 정비

- [ ] 모든 엔드포인트에 `summary`, `description` 추가 (데모 시 `/docs` 화면 활용)
- [ ] 응답 예시 (`response_model_include` 또는 `openapi_extra`) 추가
- [ ] 태그 그룹핑: `auth`, `givers`, `posts`, `discover`, `ai`, `matches`

### 3. 시드 데이터 최종 확인

- [ ] `python scripts/seed.py` 운영 DB에 1회 실행
- [ ] 시드 데이터 검증:
  - Giver 5명 (다양한 가격대 — 데모 시 가격 차이 시각적으로 확인 가능)
  - 구인글 5건 (다양한 카테고리, 태그)
  - 각 Giver에 태그 3~5개
- [ ] 시드 중복 실행 방지 (고정 UUID 기준 upsert)

### 4. GCP 배포 (FastAPI + PostgreSQL Docker)

#### 4-1. PostgreSQL 컨테이너 (GCP VM 또는 Cloud Run Jobs)
- [ ] GCP Compute Engine VM에 PostgreSQL Docker 컨테이너 실행
  ```bash
  # GCP VM에서 실행
  docker run -d \
    --name giverun-db \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=<SECRET> \
    -e POSTGRES_DB=giverun \
    -p 5432:5432 \
    -v /data/postgres:/var/lib/postgresql/data \
    postgres:16-alpine
  ```
- [ ] VM 내부 IP 확인 → `DATABASE_URL`에 반영
- [ ] 방화벽 규칙: Cloud Run → VM 5432 포트 허용 (VPC 내부 통신)

#### 4-2. FastAPI Cloud Run 배포
- [ ] `Dockerfile` 최종 확인 (포트 8080, 환경변수 주입)
- [ ] Docker 이미지 빌드 & GCR 푸시
  ```bash
  gcloud builds submit --tag gcr.io/PROJECT_ID/give-run-api
  ```
- [ ] Cloud Run 서비스 생성
  ```bash
  gcloud run deploy give-run-api \
    --image gcr.io/PROJECT_ID/give-run-api \
    --platform managed \
    --region asia-northeast3 \
    --allow-unauthenticated \
    --set-env-vars DATABASE_URL=postgresql+asyncpg://postgres:<SECRET>@<VM_INTERNAL_IP>:5432/giverun,JWT_SECRET=...,GEMINI_API_KEY=...
  ```
- [ ] 배포 후 헬스체크: `curl https://give-run-api-xxx.run.app/health`
- [ ] 배포 후 시드 데이터 실행: `python scripts/seed.py` (운영 DB 대상)

### 5. 데모 리허설 체크리스트

- [ ] 시나리오 A 전체 플로우 1회 실행 (막힘 없이)
- [ ] 시나리오 B 전체 플로우 1회 실행 (양방향 명확히 시연)
- [ ] 시나리오 C AI 태그 추천 1회 실행 (< 3초 확인)
- [ ] 네트워크 장애 대비: 로컬 빌드 백업 준비 (PRD §10.3)
- [ ] `/docs` 화면에서 주요 API 직접 호출 시연 가능 여부 확인

---

## 산출 파일 트리

```
Backend/
└── tests/
    ├── conftest.py
    ├── test_pricing.py
    ├── test_discover.py
    └── test_match_flow.py
```

---

## 최종 검증 기준 (DoD = 해커톤 P0 완료)

| PRD KPI | 검증 방법 | 목표 |
|---------|----------|------|
| P0 기능 작동률 | 5개 플로우 시연 | 100% |
| 양방향 탐색 데모 | 시나리오 A + B 모두 성공 | Giver/Taker 양쪽 능동 탐색 |
| AI 태그 추천 응답 | 실제 Gemini 호출 | < 3초 |
| 검색·필터 응답 | 시드 데이터 기준 | < 1초 |
| 가격 산정 정확도 | `pytest tests/test_pricing.py` | 5/5 통과 |

---

## 데모 Q&A 대비 (PRD §1.3)

| 예상 질문 | 답변 포인트 |
|----------|-----------|
| Cold Start 문제 | 신규 Giver 하한선 가격 + 검색 상위 부스팅 (`is_newbie` 컬럼) |
| 차별점 | 커뮤니티 운영 버티컬 특화 + 양방향 탐색 (코멘토·크몽은 단방향) |
| 수익 모델 | 매칭 수수료 (결제 금액의 10~15%), Giver 프리미엄 노출 |
| AI 역할 | 태그 추천 보조 도구만. 매칭 결정은 사람이 직접 (신뢰 설계) |
| 가격 산정 공정성 | 평점 60% + 활동 40% 자동 산정 → 신규 진입 장벽 낮춤 |
