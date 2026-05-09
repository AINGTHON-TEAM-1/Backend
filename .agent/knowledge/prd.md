# GIVE:RUN — Product Requirements Document (PRD)

| 항목 | 내용 |
|------|------|
| 문서 목적 | 해커톤 MVP 개발을 위한 기능·기술 명세 |
| 개발 기간 | 해커톤 1~3일 + 사전 설계 |
| 대상 독자 | 풀스택 개발자, 디자이너, PM |

---

## 0. Executive Summary

**GIVE:RUN은 커뮤니티를 만들고 싶은 대학생(Taker)과, 커뮤니티를 성공적으로 운영해본 사람(Giver)을 연결하는 양방향 매칭 플랫폼이다.**

### 핵심 설계 원칙
1. **양방향 탐색**: Taker가 Giver를 찾을 수도, Giver가 Taker 구인글을 찾을 수도 있다.
2. **AI는 보조 도구**: 글 작성 시 태그 추천에만 활용. 매칭 로직에는 개입하지 않는다.

### 해커톤 MVP 5가지 기능
1. 카카오 OAuth 로그인 / 역할 선택 (Giver/Taker)
2. Giver 프로필 등록 + **AI 태그 추천**
3. Taker 구인글 작성 + **AI 태그 추천**
4. **양방향 탐색 시스템** (Giver↔Taker 모두 검색·필터·정렬 가능)
5. 매칭 신청 → 수락 → 성사 플로우 (결제 Mock)

---

## 1. Product Vision

### 1.1 비전 선언문
> "운영하는 사람들의 첫 만남을 5분 안에 만든다."

### 1.2 미션
- 커뮤니티 운영의 **암묵지(tacit knowledge)** 를 1:1 매칭으로 전수
- 대학생의 시행착오 비용을 커피 한 잔 혹은 밥 한 끼 수준으로 낮춤
- Giver에게 운영 경험의 IP화·수익화 채널 제공

### 1.3 성공 정의 (해커톤 기준)
- 5개 핵심 플로우 막힘 없이 시연 가능
- **양방향 탐색** 데모가 명확하게 작동 (Giver/Taker 모두 능동적으로 상대를 찾는 모습)
- AI 태그 추천이 작성 보조 도구로 자연스럽게 녹아듦
- 심사위원 Q&A에서 Cold Start·차별점·수익모델에 자신 있게 답변

---

## 2. Problem Statement

### 2.1 사용자 페인포인트

| 페르소나 | Pain | 현재 해결 방식 | 한계 |
|----------|------|--------------|------|
| 동아리 회장 | "신입 모집·이벤트 기획 노하우 없음" | 선배에게 물어봄 | 운 좋게 그런 선배 있어야 함 |
| 디스코드 서버 운영자 | "활성율 떨어지는데 원인 모름" | 유튜브·블로그 검색 | 일반론, 내 상황에 안 맞음 |
| 스터디 그룹장 | "참여율이 점점 떨어짐" | 그냥 포기 | 학습 기회 상실 |
| 사이드 프로젝트 팀장 | "팀 분위기·생산성 관리 어려움" | 강의 결제 | 시간·비용 비대칭 |

### 2.2 시장 기회
- 대학생 동아리·소모임 시장 회복 (코로나 이후)
- MZ세대 취향 공동체 트렌드 (트레바리·문토·남의집 등 성장)
- 커뮤니티 호스팅 진입장벽 하락 → 만드는 사람 폭증, 살아남는 곳 드뭄

### 2.3 빈 시장 (Why Now)
- 코멘토·크몽 등 멘토링 플랫폼은 **직무·취업 카테고리 위주**
- 인프런·클래스101은 **일방향 강의**
- → **"커뮤니티 운영"이라는 버티컬은 비어있음**

---

## 3. Target Users & Personas

### 3.1 Primary Persona — Taker (MVP: 대학생 한정)

```
이름: 김인하 (가상 페르소나)
나이: 만 21세, 인하대 컴공 2학년
상황: 학과 알고리즘 스터디를 만들었는데 2주 후 활성율 급락
시도: 유튜브로 "스터디 운영법" 검색 → 너무 일반론
지불 의향: 1~2만원 / 1회 (점심 한 끼 값)
디지털 친숙도: 매우 높음 (디스코드, 노션, 토스 일상)
```

### 3.2 Primary Persona — Giver (제한 없음)

```
이름: 박운영 (가상 페르소나)
나이: 만 27세, 직장인 / GDGoC 인하 OB
경험: 100명 디스코드 서버 1.5년 운영, 정기 행사 12회 주최
동기: 부수입 + 본인 커뮤니티 홍보 + 이력서 한 줄
시간: 주 2~3건, 회당 1시간 가능
요구사항: 간편한 일정 조율, 신뢰할 만한 결제 시스템
```

### 3.3 사용자 여정 — **양방향 명시**

#### Taker 여정 (두 가지 경로)
```
경로 A: 게시 후 기다림형
  방문 → 카카오 로그인 → "Taker로 시작" → 구인글 작성 (AI 태그 추천)
  → 게시 → Giver들이 보고 신청 → 수락 결정 → 결제 → 매칭 완료

경로 B: 능동 탐색형
  방문 → 카카오 로그인 → "Taker로 시작" → Giver 탐색 페이지
  → 검색·필터로 Giver 찾기 → 직접 신청 → Giver 수락 → 결제 → 매칭 완료
```

#### Giver 여정 (두 가지 경로)
```
경로 A: 등록 후 기다림형
  방문 → 카카오 로그인 → "Giver로 시작" → 프로필 등록 (AI 태그 추천)
  → 등록 완료 → Taker로부터 신청 알림 → 수락/거절 → 매칭 완료

경로 B: 능동 탐색형
  방문 → 카카오 로그인 → "Giver로 시작" → 프로필 등록 → Taker 구인글 탐색
  → 검색·필터로 구인글 찾기 → 직접 신청 → Taker 수락 → 매칭 완료
```

> **핵심**: 누가 먼저 신청하든 매칭이 성사된다. 플랫폼은 **양쪽 다 능동적 발견의 자유**를 보장한다.

---

## 4. Functional Requirements (기능 요구사항)

> 표기: **🔴 MVP** (해커톤 필수) / 🟡 v1.5 / 🟢 v2

### 4.1 🔴 회원가입 / 로그인 (FR-AUTH)

#### FR-AUTH-01: 카카오 OAuth 로그인
- 카카오 로그인 버튼 클릭 → 인증 → 자동 로그인
- 첫 로그인 시 닉네임·프로필사진 자동 가져옴
- JWT는 httpOnly 쿠키에 저장

#### FR-AUTH-02: 역할 선택
```
첫 로그인 → 역할 선택 화면
  ├── "도움이 필요해요 (Taker)"   → Taker 온보딩
  └── "노하우를 나누고 싶어요 (Giver)" → Giver 온보딩
```
> v1.5에서 한 사용자가 두 역할을 동시에 보유 가능하도록 확장

---

### 4.2 🔴 Giver 프로필 등록 (FR-GIVER)

#### FR-GIVER-01: 기본 프로필
| 항목 | 필수 | 비고 |
|------|------|------|
| 닉네임 | ✓ | 카카오에서 가져옴 |
| 한 줄 소개 | ✓ | 50자 이내 |
| 자기소개 | ✓ | 500자 이내 |
| 프로필 이미지 | - | 카카오 사진 기본값 |

#### FR-GIVER-02: 운영 경험 등록 (검색 핵심 데이터)
- 커뮤니티 이름
- **카테고리 다중 선택** (6종): 네트워크 / 리그 / 커뮤니티 / 크루 / 서클 / 파티
- 운영 기간 (개월)
- 최대 인원 규모
- 운영 인증 링크 (선택)
- 핵심 성과 (200자 이내)

> MVP에서는 1개 경험만 등록. v1.5에서 다중.

#### FR-GIVER-03: 만남 형식 활성화 + **가격 자동 책정**
Giver는 어떤 형식을 제공할지 **토글만** 한다. 가격은 입력 불가.

| 형식 | 시간 | 가격 결정 |
|------|------|----------|
| 프리챗 | 15~20분 | **무료 고정** (Giver 자율 토글) |
| 커피챗 | 30~60분 | **시스템 자동 산정 (5,000~25,000원)** |
| 밀챗 | 90~120분 | **시스템 자동 산정 (10,000~50,000원)** |

**산정 기준 (Pricing Score)**:
- 평점 (rating_avg) — 가중치 60%
- 활동 빈도 (match_count) — 가중치 40%
- 신규 Giver는 **하한선 가격**으로 시작 → 첫 진입 장벽 낮춰 매칭 기회 확보
- 인기·고평점 Giver는 **상한선에 가깝게** → 수요 분산 효과

**의도된 시장 효과**:
- 신규/저평점 Giver: 낮은 가격으로 Taker의 첫 선택을 받기 쉬움 → 활동 누적 → 가격 상승의 선순환
- 인기·고평점 Giver: 가격 상승으로 일부 수요 분산 → 다른 Giver에게 기회 분배
- → "잘 하는 사람만 다 가져가는 구조"가 아닌, **자정 기능 있는 시장**

**가격 갱신 주기**:
- 신규 Giver: 등록 즉시 하한선 가격 부여
- 매칭 완료 + 평가 등록 시점마다 재계산 → 다음 매칭부터 갱신된 가격 적용
- (v1.5) 일 1회 새벽 배치 처리로 변경 가능

**Giver 화면 표시 (읽기 전용)**:
```
당신의 현재 책정 가격
┌────────────────────────────────────┐
│ ✓ 프리챗 (무료)         [활성화 ●]  │
│ ✓ 커피챗 13,500원       [활성화 ●]  │
│   ↳ 평점 4.5/5 · 매칭 12회 기준     │
│ ✓ 밀챗   28,000원       [활성화 ●]  │
│   ↳ 평점 4.5/5 · 매칭 12회 기준     │
└────────────────────────────────────┘
* 가격은 활동에 따라 자동 조정됩니다
```

> ⚠️ **Cold Start 보호 장치**: 등록 후 첫 3건은 모든 신규 Giver에게 동일한 하한선 가격 + 검색 상위 노출 부스트.

#### FR-GIVER-04: 🤖 AI 태그 추천 (보조 도구)
- 자기소개·운영 경험 작성 후 → **"AI 태그 추천 받기"** 버튼 클릭
- Gemini가 5개 태그 후보 제시
- 사용자가 **수락/거절/추가/삭제** 자유롭게 (AI는 제안만, 결정은 사용자)
- 최종 태그는 검색·필터의 데이터로 사용됨

---

### 4.3 🔴 Taker 구인글 작성 (FR-TAKER)

#### FR-TAKER-01: 구인글 등록
| 항목 | 필수 | 비고 |
|------|------|------|
| 제목 | ✓ | 50자 이내 |
| 카테고리 | ✓ | 6종 중 1개 |
| 본문 | ✓ | 500자 이내 |
| 희망 만남 형식 | ✓ | 프리챗/커피챗/밀챗 |
| 희망 예산 범위 | - | 선택 |

#### FR-TAKER-02: 🤖 AI 태그 추천 (보조 도구)
- 본문 작성 후 → **"AI 태그 추천 받기"** 버튼 클릭
- Gemini API 호출 → 2초 이내 5개 태그 후보 응답
- 사용자가 수락/거절/추가/삭제
- **로딩 UX**: "AI가 글을 분석 중..." 스피너 (해커톤 데모 시 임팩트)

> ⚠️ **중요**: AI는 작성 보조만 한다. 어떤 Giver와 매칭될지는 결정하지 않는다.

---

### 4.4 🔴 양방향 탐색 시스템 (FR-DISCOVER) ⭐ **핵심**

> Taker와 Giver 양쪽 모두 능동적으로 상대를 찾을 수 있도록 동등한 탐색 인터페이스를 제공한다.

#### FR-DISCOVER-01: Giver 탐색 페이지 (Taker가 사용)
**경로**: `/discover/givers`

**검색 / 필터 / 정렬 기능**:
| 항목 | 옵션 |
|------|------|
| 텍스트 검색 | 닉네임·자기소개·태그·커뮤니티명 통합 검색 |
| 카테고리 필터 | 6종 다중 선택 (체크박스) |
| 만남 형식 필터 | 프리챗·커피챗·밀챗 다중 선택 |
| 가격 범위 필터 | 슬라이더 (0~50,000원) |
| 평점 필터 | ★3.5+ / ★4.0+ / ★4.5+ |
| 태그 필터 | 인기 태그 클릭 또는 직접 입력 |
| 정렬 | 최신순 / 평점순 / 인기순(매칭 수) / 가격 낮은 순 |

**카드 UI** — 한 화면에 페이지네이션으로 12개씩:
```
┌─────────────────────────────────┐
│ [프로필]  박운영       ★4.5 (12) │
│ "디스코드 서버 1.5년 운영"        │
│ 🏷 #중규모 #장기 #리텐션          │
│ 💼 커뮤니티·서클                  │
│ [프리챗 무료] [커피챗 12,000원]   │
└─────────────────────────────────┘
```

#### FR-DISCOVER-02: Taker 구인글 탐색 페이지 (Giver가 사용)
**경로**: `/discover/posts`

**검색 / 필터 / 정렬 기능**:
| 항목 | 옵션 |
|------|------|
| 텍스트 검색 | 제목·본문·태그 통합 검색 |
| 카테고리 필터 | 6종 다중 선택 |
| 만남 형식 필터 | 프리챗·커피챗·밀챗 |
| 예산 범위 필터 | 슬라이더 |
| 상태 필터 | 진행 중인 글만 / 전체 |
| 태그 필터 | 인기 태그 또는 직접 입력 |
| 정렬 | 최신순 / 신청 적은 순(블루오션) / 예산 높은 순 |

**카드 UI**:
```
┌─────────────────────────────────┐
│ 김인하         3시간 전     [신청 2] │
│ ── 알고리즘 스터디 운영 도와주세요 ──│
│ 인하대 컴공 2학년, 학과 스터디...  │
│ 🏷 #소규모 #장기 #리텐션 #신입유치 │
│ 💰 ~15,000원   📅 커피챗 희망     │
└─────────────────────────────────┘
```

#### FR-DISCOVER-03: 인기 태그 위젯 (양쪽 페이지 공통)
- 사이드바에 "인기 태그 Top 10" 표시
- 클릭 시 해당 태그로 자동 필터링
- 데이터: 최근 30일 내 등록된 태그 사용 빈도 기준

> ❌ MVP에서 **하지 않는 것**: AI 기반 추천 알고리즘, 임베딩 매칭, 개인화 추천. 모든 탐색은 사용자가 명시적으로 입력한 검색어와 필터로만 작동.

---

### 4.5 🔴 매칭 신청 → 수락 → 성사 (FR-FLOW)

#### FR-FLOW-01: 신청 (양방향 가능)
**경로 1**: Taker가 Giver에게 신청
- Giver 카드 또는 상세 페이지 → "프리챗/커피챗/밀챗 신청" 버튼
- 신청 폼: 만남 희망 일시 3개 옵션 + 메시지 200자
- 신청 시 어떤 구인글에 연결되는지 선택 (또는 즉석 신청)

**경로 2**: Giver가 Taker 구인글에 신청
- 구인글 상세 → "도와드리겠습니다" 버튼
- 신청 폼: 가능 일시 3개 + 메시지 200자 + 제안 형식·가격
- Taker는 들어온 신청 중 마음에 드는 Giver 선택

#### FR-FLOW-02: 수락 / 거절
- 받은 신청은 마이페이지 "받은 신청" 탭에 노출
- 수락 시 → 매칭 성사 → 양측에 알림
- 거절 시 → 사유 선택 (시간 안 맞음 / 분야 안 맞음 / 기타)

#### FR-FLOW-03: 결제 (MVP는 Mock)
- 결제 페이지 UI만 구현 (토스페이먼츠 디자인 모방)
- 무료 프리챗은 결제 단계 스킵
- **결제 금액 = 매칭 시점의 Giver 자동 산정 가격** (Giver의 가격이 나중에 바뀌어도 매칭 당시 가격으로 결제)
- "결제하기" 버튼 → 2초 로딩 → "결제 완료" Mock 응답
- 매칭 상태 → "성사 완료"

#### FR-FLOW-04: 매칭 완료 후
- 화상회의 링크 또는 만남 장소 안내 (Mock 텍스트)
- "만남이 끝나면 평가해 주세요" 안내 (실제 평가는 v1.5)

---

### 4.6 🟡 v1.5 (해커톤 후 우선 추가)
- 평점·후기 시스템
- Giver 등급제 (Bronze/Silver/Gold)
- 토스페이먼츠 실 결제 연동
- 채팅 기능 (Supabase Realtime)
- 노쇼/취소 정책
- 한 사용자 두 역할 보유

### 4.7 🟢 v2 (향후 확장)
- Giver/Taker 라운지 (자체 커뮤니티)
- 화상회의 내장
- 개인화 추천 (선택적, 사용자가 켜야 작동)
- B2B 학교·동아리연합회 패키지

---

## 5. Non-Functional Requirements

| 항목 | 요구사항 |
|------|----------|
| **성능** | 페이지 로딩 < 2초 / 검색 응답 < 1초 / Gemini 태그 추천 < 3초 |
| **가용성** | 해커톤 데모 시간(약 1시간) 동안 무중단 |
| **보안** | JWT httpOnly 쿠키, HTTPS, ORM 사용으로 SQL Injection 방어 |
| **반응형** | 모바일·태블릿·데스크톱 대응 (Tailwind breakpoint) |
| **접근성** | 시맨틱 HTML, Alt 텍스트 (해커톤은 최소 수준) |
| **개인정보** | 매칭 성사 전까지 실명·연락처 비공개 |
| **검색 성능** | 태그·카테고리 인덱싱으로 1만 건까지 1초 이내 |

---

## 6. Information Architecture

### 6.1 화면 구조 (Sitemap) — **양방향 반영**

```
/                           랜딩 페이지
/auth/login                 카카오 로그인
/auth/onboarding            역할 선택
/auth/onboarding/giver      Giver 프로필 등록 (4단계)
/auth/onboarding/taker      Taker 첫 안내

/                           메인 (역할에 따라 다른 진입점 노출)
  ├── (Taker)               → /discover/givers 추천
  └── (Giver)               → /discover/posts 추천

/discover/givers            ⭐ Giver 탐색 페이지 (Taker 주 사용)
/discover/posts             ⭐ Taker 구인글 탐색 페이지 (Giver 주 사용)

/post/new                   구인글 작성 (Taker)
/post/:id                   구인글 상세

/giver/:id                  Giver 프로필 상세
/giver/:id/apply            매칭 신청 폼 (Taker→Giver)
/post/:id/apply             매칭 신청 폼 (Giver→Taker)

/me                         마이페이지
  ├── /me/profile           프로필 수정
  ├── /me/applications      내가 보낸 신청
  ├── /me/requests          내가 받은 신청
  └── /me/matches           성사된 매칭 목록

/match/:id                  매칭 상세
/match/:id/payment          결제 페이지 (Mock)
```

### 6.2 핵심 화면 와이어프레임

#### [화면 A] 메인 (역할별 진입)
```
┌────────────────────────────────────────────┐
│ GIVE:RUN                  [닉네임 ▼]        │
├────────────────────────────────────────────┤
│ 👋 박운영님, 오늘 어떤 활동을?              │
│                                            │
│ ┌──────────────┐  ┌──────────────┐        │
│ │ 📋 새 구인글  │  │ 🔍 Giver 찾기 │        │
│ │   작성하기    │  │              │        │
│ └──────────────┘  └──────────────┘        │
│                                            │
│ ▼ 추천 구인글 (Giver용 시점에서)             │
│ ... (탐색 페이지 미리보기) ...               │
└────────────────────────────────────────────┘
```

#### [화면 B] Giver 탐색 페이지 (Taker가 사용)
```
┌────────────────────────────────────────────┐
│ GIVE:RUN                  [닉네임 ▼]        │
├────────────────────────────────────────────┤
│ 🔍 [닉네임·태그·커뮤니티 검색...]   [검색]   │
├────────────────┬───────────────────────────┤
│ 📌 필터         │ 정렬: [최신순 ▼]   12건   │
│ ☐ 카테고리      │                            │
│   ☐ 네트워크    │ ┌──────────────────────┐  │
│   ☐ 커뮤니티    │ │박운영      ★4.5 (12) │  │
│   ☐ 서클       │ │"디스코드 1.5년 운영"   │  │
│   ...          │ │#중규모 #리텐션         │  │
│ 만남 형식       │ │[프리챗] [커피챗 12k] │  │
│   ☐ 프리챗     │ └──────────────────────┘  │
│   ☐ 커피챗     │ ┌──────────────────────┐  │
│ 가격: 0~25k    │ │... 다음 Giver ...     │  │
│ [━━●━━]       │ └──────────────────────┘  │
│                │                            │
│ 🏷 인기 태그    │ [더 보기]                 │
│ #리텐션 #신입  │                            │
│ #이벤트 #온라인 │                            │
└────────────────┴───────────────────────────┘
```

#### [화면 C] Taker 구인글 탐색 페이지 (Giver가 사용)
```
┌────────────────────────────────────────────┐
│ 🔍 [구인글 제목·본문·태그 검색...]  [검색]  │
├────────────────┬───────────────────────────┤
│ 📌 필터         │ 정렬: [신청 적은 순 ▼] 8건│
│ ☐ 카테고리      │                            │
│ 만남 형식       │ ┌──────────────────────┐  │
│ 예산: 0~30k    │ │김인하   3h전  [신청 2]│  │
│ ☐ 진행중만      │ │알고리즘 스터디 운영...│  │
│                │ │#소규모 #장기 #리텐션 │  │
│ 🏷 인기 태그    │ │~15,000원  커피챗 희망│  │
│ #스터디 #신입   │ └──────────────────────┘  │
│ #리텐션         │ ┌──────────────────────┐  │
│                │ │... 다음 글 ...        │  │
└────────────────┴───────────────────────────┘
```

#### [화면 D] AI 태그 추천 데모 (구인글 작성)
```
┌────────────────────────────────────────────┐
│ ← 새 구인글 작성                            │
├────────────────────────────────────────────┤
│ 제목 [________________________________]    │
│ 카테고리 [커뮤니티 ▼]                       │
│ 본문 ┌──────────────────────────────┐      │
│      │ 30명 보드게임 동아리 운영...    │      │
│      └──────────────────────────────┘      │
│                                            │
│ 🏷 태그                                    │
│ [🤖 AI 태그 추천 받기]                      │
│                                            │
│ ✨ AI 추천 (편집 가능)                      │
│ [#중규모 ✓] [#장기 ✓] [#오프라인 ✓]         │
│ [#신입유치 ✓] [#리텐션 ✓]                  │
│ [+ 직접 추가]                              │
│                                            │
│ * AI는 추천만 합니다. 매칭은 직접 탐색하세요│
│                                            │
│ [취소]                          [등록하기]  │
└────────────────────────────────────────────┘
```

---

## 7. Data Model (DB 스키마) — **임베딩 제거**

> PostgreSQL + Supabase. **pgvector 불필요**. 일반 인덱싱으로 검색 처리.

```sql
-- 사용자
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  kakao_id BIGINT UNIQUE NOT NULL,
  nickname VARCHAR(30) NOT NULL,
  profile_image_url TEXT,
  email VARCHAR(100),
  role VARCHAR(10) CHECK (role IN ('giver', 'taker', 'both')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Giver 프로필
CREATE TABLE giver_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  bio_short VARCHAR(50),
  bio_long TEXT,
  -- 만남 형식 활성화 토글 (Giver가 직접 선택)
  freechat_enabled BOOLEAN DEFAULT TRUE,
  coffeechat_enabled BOOLEAN DEFAULT FALSE,
  mealchat_enabled BOOLEAN DEFAULT FALSE,
  -- 가격 (시스템 자동 산정, Giver는 입력 불가)
  coffeechat_price INT DEFAULT 5000,    -- 하한선으로 초기화
  mealchat_price INT DEFAULT 10000,     -- 하한선으로 초기화
  pricing_score DECIMAL(3,2) DEFAULT 0, -- 0.00 ~ 1.00 (산정 기준값)
  pricing_updated_at TIMESTAMPTZ DEFAULT NOW(),
  -- 평점·통계 (가격 산정 입력값)
  rating_avg DECIMAL(3,2) DEFAULT 0,
  rating_count INT DEFAULT 0,
  match_count INT DEFAULT 0,
  -- Cold Start 보호
  is_newbie BOOLEAN DEFAULT TRUE,       -- 첫 3건 매칭 전까지 TRUE
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Giver 운영 경험
CREATE TABLE giver_experiences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  giver_profile_id UUID REFERENCES giver_profiles(id) ON DELETE CASCADE,
  community_name VARCHAR(100),
  categories TEXT[] CHECK (categories <@ ARRAY['network','league','community','crew','circle','party']),
  duration_months INT,
  max_member_count INT,
  proof_url TEXT,
  achievement TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 카테고리 검색용 GIN 인덱스
CREATE INDEX idx_giver_categories ON giver_experiences USING GIN (categories);

-- Taker 구인글
CREATE TABLE taker_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(50) NOT NULL,
  body TEXT NOT NULL,
  category VARCHAR(20) CHECK (category IN ('network','league','community','crew','circle','party')),
  preferred_format VARCHAR(20) CHECK (preferred_format IN ('freechat','coffeechat','mealchat')),
  budget_min INT,
  budget_max INT,
  status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open','matched','closed')),
  application_count INT DEFAULT 0,  -- "신청 적은 순" 정렬용
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 텍스트 검색용 인덱스 (PostgreSQL Full Text Search)
CREATE INDEX idx_posts_text ON taker_posts 
  USING GIN (to_tsvector('simple', title || ' ' || body));
CREATE INDEX idx_posts_status_created ON taker_posts (status, created_at DESC);

-- 태그 (Giver/Taker 공통)
CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_type VARCHAR(20) CHECK (owner_type IN ('giver_profile','taker_post')),
  owner_id UUID NOT NULL,
  tag VARCHAR(30) NOT NULL,
  is_ai_suggested BOOLEAN DEFAULT FALSE,  -- AI 추천 출처 / 사용자 추가 구분
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 태그 검색용 인덱스
CREATE INDEX idx_tags_owner ON tags(owner_type, owner_id);
CREATE INDEX idx_tags_value ON tags(tag);

-- 매칭
CREATE TABLE matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  taker_id UUID REFERENCES users(id),
  giver_id UUID REFERENCES users(id),
  taker_post_id UUID REFERENCES taker_posts(id),  -- NULL 가능 (즉석 신청)
  initiated_by VARCHAR(10) CHECK (initiated_by IN ('taker','giver')),  -- ⭐ 누가 먼저 신청
  format VARCHAR(20) CHECK (format IN ('freechat','coffeechat','mealchat')),
  message TEXT,
  preferred_dates JSONB,
  status VARCHAR(20) DEFAULT 'pending' 
    CHECK (status IN ('pending','accepted','rejected','paid','completed','cancelled')),
  payment_amount INT,
  payment_id VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  accepted_at TIMESTAMPTZ,
  paid_at TIMESTAMPTZ
);

CREATE INDEX idx_matches_taker_status ON matches(taker_id, status);
CREATE INDEX idx_matches_giver_status ON matches(giver_id, status);
```

### 7.1 ER Diagram

```
users (1) ──── (1) giver_profiles
   │                   │
   │                   └─── (N) giver_experiences
   │
   ├──── (N) taker_posts
   │
   └──── (N) matches (taker_id 또는 giver_id)
              │
              └─ initiated_by 컬럼으로 양방향 추적

tags (polymorphic) ── giver_profiles 또는 taker_posts
```

---

## 8. API Specification

> Base URL: `/api/v1`. JWT 인증 필요한 엔드포인트는 `🔒` 표기.

### 8.1 인증

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/auth/kakao` | 카카오 OAuth 시작 |
| GET | `/auth/kakao/callback` | 카카오 콜백 → JWT 발급 |
| 🔒 POST | `/auth/logout` | 로그아웃 |
| 🔒 POST | `/auth/role` | 역할 선택 |

### 8.2 Giver

| Method | Endpoint | 설명 |
|--------|----------|------|
| 🔒 POST | `/givers/profile` | Giver 프로필 등록 (가격 입력 불가, 형식 토글만) |
| GET | `/givers/:id` | Giver 상세 조회 (산정된 가격 포함 응답) |
| 🔒 PATCH | `/givers/profile` | 본인 프로필 수정 (가격 필드는 무시됨) |
| 🔒 POST | `/givers/experiences` | 운영 경험 추가 |
| (내부) | `recalculate_giver_pricing(user_id)` | 가격 재산정 함수 (매칭 평가 시 자동 호출) |

#### 가격 산정 로직 (의사코드)

```python
def recalculate_giver_pricing(giver_profile: GiverProfile) -> tuple[int, int]:
    """
    평점 + 활동 빈도를 기반으로 커피챗/밀챗 가격을 산정한다.
    Returns: (coffeechat_price, mealchat_price)
    """
    # 가격 범위
    COFFEE_MIN, COFFEE_MAX = 5000, 25000
    MEAL_MIN, MEAL_MAX = 10000, 50000
    
    # 신규 Giver(매칭 3건 미만)는 무조건 하한선
    if giver_profile.match_count < 3:
        return COFFEE_MIN, MEAL_MIN
    
    # 1. 평점 정규화 (0.0 ~ 1.0)
    #    평점 < 3.0이면 0, 평점 5.0이면 1.0
    rating_norm = max(0, (giver_profile.rating_avg - 3.0) / 2.0)
    
    # 2. 활동 빈도 정규화 (0.0 ~ 1.0)
    #    매칭 3건부터 시작, 30건+ 도달 시 만점
    activity_norm = min(1.0, (giver_profile.match_count - 3) / 27)
    
    # 3. 종합 점수 (평점 60% + 활동 40%)
    score = 0.6 * rating_norm + 0.4 * activity_norm
    
    # 4. 가격 산정
    coffee = int(COFFEE_MIN + (COFFEE_MAX - COFFEE_MIN) * score)
    meal = int(MEAL_MIN + (MEAL_MAX - MEAL_MIN) * score)
    
    # 5. 500원 단위로 라운딩 (UX)
    coffee = round(coffee / 500) * 500
    meal = round(meal / 500) * 500
    
    return coffee, meal


# 호출 시점:
# 1. 신규 Giver 등록 시 → 자동으로 (5000, 10000) 부여
# 2. 매칭 완료 + 평가 등록 시 → 해당 Giver 재산정
# 3. (v1.5) 매일 새벽 3시 배치 작업으로 일괄 재산정
```

**예시 시나리오**:

| Giver | 평점 | 매칭 수 | 종합 점수 | 커피챗 | 밀챗 |
|-------|------|--------|-----------|--------|------|
| A (신규) | - | 0건 | - | 5,000원 | 10,000원 |
| B (입문) | 4.0 | 5건 | 0.34 | 11,500원 | 23,500원 |
| C (활성) | 4.5 | 15건 | 0.63 | 17,500원 | 35,000원 |
| D (인기) | 4.8 | 30건 | 0.94 | 23,500원 | 47,500원 |
| E (저평점) | 3.2 | 20건 | 0.31 | 11,000원 | 22,500원 |

### 8.3 구인글

| Method | Endpoint | 설명 |
|--------|----------|------|
| 🔒 POST | `/posts` | 구인글 작성 |
| GET | `/posts/:id` | 구인글 상세 |
| 🔒 PATCH | `/posts/:id` | 구인글 수정 |
| 🔒 DELETE | `/posts/:id` | 구인글 삭제 |

### 8.4 ⭐ 양방향 탐색 (가장 중요)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/discover/givers` | Giver 목록 검색·필터·정렬 |
| GET | `/discover/posts` | Taker 구인글 목록 검색·필터·정렬 |
| GET | `/discover/popular-tags` | 인기 태그 Top 10 |

#### 핵심 API 상세 — `GET /discover/givers`

**Query Parameters**:
```
?q=리텐션              (텍스트 검색)
&categories=community,circle  (다중 선택)
&format=coffeechat,mealchat
&price_min=0&price_max=20000
&rating_min=4.0
&tag=신입유치          (태그 필터)
&sort=rating          (latest|rating|popular|price_asc)
&page=1&size=12
```

**Response**:
```json
{
  "total": 47,
  "page": 1,
  "items": [
    {
      "id": "uuid",
      "nickname": "박운영",
      "profile_image_url": "...",
      "bio_short": "디스코드 서버 1.5년 운영",
      "rating_avg": 4.5,
      "rating_count": 12,
      "match_count": 18,
      "tags": ["중규모", "장기", "리텐션"],
      "categories": ["community", "circle"],
      "freechat_enabled": true,
      "coffeechat_price": 12000,
      "mealchat_price": 30000
    }
  ]
}
```

**Backend Logic (FastAPI 의사코드)**:
```python
@router.get("/discover/givers")
async def discover_givers(
    q: str = None,
    categories: list[str] = Query(None),
    format: list[str] = Query(None),
    price_min: int = 0,
    price_max: int = 50000,
    rating_min: float = 0,
    tag: str = None,
    sort: str = "latest",
    page: int = 1,
    size: int = 12
):
    query = select(GiverProfile).join(User)
    
    # 텍스트 검색 (닉네임·자기소개·커뮤니티명)
    if q:
        query = query.where(or_(
            User.nickname.ilike(f"%{q}%"),
            GiverProfile.bio_long.ilike(f"%{q}%"),
            GiverExperience.community_name.ilike(f"%{q}%")
        ))
    
    # 카테고리 필터 (배열 교집합)
    if categories:
        query = query.where(GiverExperience.categories.overlap(categories))
    
    # 평점 필터
    if rating_min > 0:
        query = query.where(GiverProfile.rating_avg >= rating_min)
    
    # 태그 필터 (조인)
    if tag:
        query = query.join(Tag, ...).where(Tag.tag == tag)
    
    # 정렬
    sort_map = {
        "latest": GiverProfile.created_at.desc(),
        "rating": GiverProfile.rating_avg.desc(),
        "popular": GiverProfile.match_count.desc(),
        "price_asc": GiverProfile.coffeechat_price.asc(),
    }
    query = query.order_by(sort_map.get(sort, sort_map["latest"]))
    
    # 페이지네이션
    return await paginate(query, page=page, size=size)
```

#### 핵심 API 상세 — `GET /discover/posts`
구조 동일. Taker 구인글 검색·필터·정렬. Giver가 주 사용자.

### 8.5 🤖 AI 태그 추천 (보조 도구)

| Method | Endpoint | 설명 |
|--------|----------|------|
| 🔒 POST | `/ai/suggest-tags` | Gemini가 태그 5개 후보 제안 (사용자가 채택) |

**Request**:
```json
POST /api/v1/ai/suggest-tags
{
  "text": "30명 규모 보드게임 동아리를 1년째 운영 중인데..."
}
```

**Response**:
```json
{
  "success": true,
  "suggested_tags": ["중규모", "장기", "오프라인", "신입유치", "리텐션"],
  "processing_time_ms": 1820,
  "note": "AI 추천입니다. 자유롭게 편집하세요."
}
```

**Backend Logic**:
```python
@router.post("/ai/suggest-tags")
async def suggest_tags(req: TagSuggestRequest, user=Depends(get_current_user)):
    prompt = f"""
다음 텍스트에서 커뮤니티 운영 관련 핵심 키워드 5개를 추출해줘.
규칙:
- 한글 명사 또는 짧은 구
- # 없이 단어만, 콤마 구분

텍스트: {req.text}
"""
    response = gemini_model.generate_content(prompt)
    tags = [t.strip() for t in response.text.split(",")][:5]
    return {
        "success": True, 
        "suggested_tags": tags,
        "note": "AI 추천입니다. 자유롭게 편집하세요."
    }
```

### 8.6 매칭 플로우

| Method | Endpoint | 설명 |
|--------|----------|------|
| 🔒 POST | `/matches` | 매칭 신청 (Taker→Giver 또는 Giver→Taker) |
| 🔒 GET | `/matches/me` | 내 매칭 목록 |
| 🔒 PATCH | `/matches/:id/accept` | 수락 |
| 🔒 PATCH | `/matches/:id/reject` | 거절 |
| 🔒 POST | `/matches/:id/pay` | 결제 (Mock) |

**`POST /matches` Request**:
```json
{
  "target_type": "giver",      // "giver" or "taker_post"
  "target_id": "uuid",
  "post_id": "uuid",            // 연결할 구인글 (선택, Taker 입장)
  "format": "coffeechat",
  "message": "스터디 운영 도와주실 수 있나요?",
  "preferred_dates": ["2026-05-15T14:00", "2026-05-16T18:00"]
}
```
- 백엔드가 자동으로 `initiated_by` 컬럼 설정 (현재 사용자 역할 기반)

---

## 9. Tech Stack & Architecture

### 9.1 기술 스택 — **간소화**

| 레이어 | 선택 | 비고 |
|--------|------|------|
| Frontend | Next.js 14 (App Router) | SEO 필수 |
| UI | TailwindCSS + shadcn/ui | 해커톤 속도 |
| State | Zustand | 가벼움 |
| Form | react-hook-form + zod | 검증 일관성 |
| Backend | FastAPI (Python 3.11) | Gemini API 연동 + 빠른 프로토타이핑 |
| ORM | SQLAlchemy 2.0 + asyncpg | async 지원 |
| DB | PostgreSQL (Supabase) | **pgvector 불필요** |
| Auth | Supabase Auth (Kakao OAuth) | - |
| AI | google-generativeai (Gemini 1.5 Flash) | **태그 추천 단일 용도** |
| 결제 | (MVP) Mock / (v1.5) 토스페이먼츠 | - |
| FE 배포 | Vercel | - |
| BE 배포 | GCP Cloud Run | 서버리스 |

### 9.2 시스템 아키텍처

```
┌──────────┐         ┌─────────────────┐         ┌─────────────┐
│ 사용자    │◄────────►│ Next.js (Vercel)│◄────────►│ FastAPI (GCP│
│ (브라우저)│  HTTPS  │   - SSR/CSR     │  REST   │  Cloud Run) │
└──────────┘         │   - 카카오 OAuth │         └──────┬──────┘
                     └─────────────────┘                │
                                                        ▼
                                              ┌────────────────┐
                                              │ Supabase       │
                                              │  - PostgreSQL  │
                                              │  - 일반 인덱싱  │
                                              │  - Auth        │
                                              └────────────────┘
                                                        │
                                              ┌─────────▼────────┐
                                              │ Gemini API       │
                                              │  (태그 추천만)   │
                                              └──────────────────┘
```

### 9.3 환경변수

```bash
# Backend
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET=...
KAKAO_CLIENT_ID=...
KAKAO_CLIENT_SECRET=...
GEMINI_API_KEY=...

# Frontend
NEXT_PUBLIC_API_URL=https://api.give-run.app
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

---

## 10. Development Plan & Milestones

### 10.1 해커톤 일정 (2박 3일 기준)

| Day | 시간대 | 작업 |
|-----|--------|------|
| **Day 1 AM** | 0~4h | 디자인 합의 + DB 스키마 + 프로젝트 셋업 + 카카오 사전 등록 |
| Day 1 PM | 4~10h | 카카오 OAuth + Giver 프로필 등록 + Taker 구인글 작성 |
| **Day 2 AM** | 10~16h | ⭐ **양방향 탐색 페이지 (Giver 탐색 / Posts 탐색)** + 검색·필터 API |
| Day 2 PM | 16~22h | AI 태그 추천 통합 + 매칭 신청 플로우 (양방향) |
| **Day 3 AM** | 22~28h | 결제 Mock + 마이페이지 + 버그 수정 |
| Day 3 PM | 28~30h | 데모 시나리오 리허설 + 발표 자료 |

### 10.2 우선순위

```
🔴 P0 (없으면 데모 불가)
  - 카카오 로그인 / 역할 선택
  - Giver 프로필 등록 (최소 5명 시드 데이터)
  - Taker 구인글 작성 (최소 5건 시드 데이터)
  - ⭐ Giver 탐색 페이지 (검색·필터·정렬)
  - ⭐ Posts 탐색 페이지 (검색·필터·정렬)
  - AI 태그 추천 (작성 시점에 한 번 호출)

🟠 P1 (있으면 좋음)
  - 양방향 매칭 신청 → 수락 플로우
  - 결제 Mock 화면
  - 마이페이지

🟡 P2 (시간 남으면)
  - 인기 태그 위젯
  - 다중 운영 경험 등록
  - 디자인 폴리싱
```

### 10.3 위험 요소 & 대응

| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| Gemini API 응답 지연/에러 | 중 | 타임아웃 3초 + fallback 빈 배열 반환 |
| 카카오 OAuth 설정 시간 소요 | 중 | Day 0 사전 등록 |
| 검색 성능 저하 | 하 | 시드 데이터 100건 미만이라 인덱싱만으로 충분 |
| 디자인 합의 지연 | 상 | shadcn/ui 컴포넌트 그대로 활용 |
| 시연 중 네트워크 장애 | 중 | 데모용 로컬 빌드 백업 |

---

## 11. Success Metrics (KPI)

### 11.1 해커톤 자체 평가

| 지표 | 목표 |
|------|------|
| P0 기능 작동률 | 100% |
| **양방향 탐색 데모 명확성** | Giver/Taker 양쪽 시연 모두 성공 |
| AI 태그 추천 응답 시간 | < 3초 |
| 검색·필터 응답 시간 | < 1초 |
| 발표 시간 준수 | 5~7분 |

### 11.2 출시 후 KPI (3개월)

| 카테고리 | 지표 | 목표 |
|---------|------|------|
| 사용자 | 등록 Giver | 100명 |
| 사용자 | 등록 Taker | 500명 |
| 매칭 | 누적 매칭 성사 | 200건 |
| 매칭 | **Giver→Taker 능동 신청 비율** | 30% (양방향성 검증) |
| 만족도 | 평균 평점 | ★4.2+ |
| 리텐션 | Taker 재이용률 | 30% |

> ⭐ **핵심 KPI**: "Giver→Taker 능동 신청 비율"이 20%를 넘어야 양방향 시스템이 작동한다고 본다.

---

## 12. Out of Scope (해커톤에서 다루지 않음)

- 실 결제 처리
- 화상회의 내장
- 채팅 / 실시간 알림
- **AI 기반 매칭 추천 (의도적으로 제외)** — 매칭은 사용자 손으로
- 임베딩·코사인 유사도 검색
- 평점·후기 시스템 (UI는 mock)
- Giver 등급 자동 산정
- 분쟁 조정 시스템
- Giver/Taker 자체 커뮤니티
- 푸시 알림
- 어드민 대시보드
- 다국어 지원

---

## 13. Open Questions

- [ ] **서비스명 최종 확정** (GIVE:RUN / CrewMate / 무리다 / PartyUp)
- [ ] 메인 컬러 — 신뢰감(파란계열) vs 활기(주황계열)
- [ ] 로고 — 사전 디자인 vs 텍스트 로고로 시작
- [ ] Giver 카테고리 다중 선택 시 최대 몇 개까지 (PRD는 무제한, UI는 3개 권장)
- [ ] **메인 페이지 설계**: 역할별 다른 화면 vs 동일 화면 (현재 PRD는 역할별)
- [ ] 시드 데이터 (가짜 Giver 5명, 구인글 5건) 누가 작성?
- [ ] 카카오 비즈니스 계정 보유 여부 사전 확인
- [ ] **가격 산정 가중치 검토**: 평점 60% + 활동 40% 조합이 적절한가? (실 데이터 누적 후 조정 필요)
- [ ] **신규 Giver 부스팅 기간**: 첫 3건 기준이 적절한가? (5건? 1주일? 등 대안 검토)

---

## 14. Appendix

### 14.1 명칭 정의 (검색·매칭 필터)

| 규모 | 지속 | 명칭 | DB enum |
|------|------|------|---------|
| 대규모(100+) | 장기 | 네트워크 | `network` |
| 대규모(100+) | 단기 | 리그 | `league` |
| 중규모(16~99) | 장기 | 커뮤니티 | `community` |
| 중규모(16~99) | 단기 | 크루 | `crew` |
| 소규모(<16) | 장기 | 서클 | `circle` |
| 소규모(<16) | 단기 | 파티 | `party` |

### 14.2 Gemini 호출 예시 (참고)

```python
import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

prompt = """
다음 텍스트에서 커뮤니티 운영 관련 핵심 키워드 5개를 추출해줘.
규칙: 한글 명사 또는 짧은 구, # 없이 단어만, 콤마 구분.

텍스트: {text}
"""

response = model.generate_content(prompt.format(text=user_text))
tags = [t.strip() for t in response.text.split(",")][:5]
```

> **AI는 추천만, 결정은 사용자.** 이게 GIVE:RUN의 설계 철학이다.

### 14.3 참고 자료
- Gemini API 공식 문서: https://ai.google.dev/
- Supabase: https://supabase.com/docs
- 카카오 OAuth: https://developers.kakao.com/docs/latest/ko/kakaologin/common
- shadcn/ui: https://ui.shadcn.com/

---

> **GIVE:RUN — 운영하는 사람들의 첫 만남.**
> *문서 끝. 변경 사항은 v1.2... 로 버저닝.*
