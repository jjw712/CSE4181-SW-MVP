# CSE4181-SW-MVP

앱 아이디어를 입력하면 관련 검색어를 만들고, 외부 데이터 소스에서 근거를 모아 **출처 기반 조사 리포트**를 생성하는 MVP입니다.

이 프로젝트는 앱의 성공 가능성을 예측하지 않습니다. 점수도 매기지 않습니다. 대신 고객 문제, 시장 신호, 경쟁 앱, 가격/수익화, 구현 자료를 한곳에 모아 개발 전에 확인할 수 있게 정리합니다.

## 주요 기능

- 앱 아이디어 입력
- 타겟 고객, 지역, 서비스 유형 입력
- 검색어 템플릿 생성
- Naver Search API 기반 문서 검색
- Naver DataLab 기반 검색 관심도 확인
- Apple iTunes Search API 기반 iOS 경쟁 앱 후보 검색
- Naver News API, GDELT, Hacker News, GitHub 기반 PEST 신호 수집
- Gemma 기반 검색어 보강 및 출처 요약
- LLM 토큰이 없을 때 사용하는 임시 rule fallback
- JSON 리포트 반환
- 프론트엔드 카드 출력

## 입력 값

| 항목 | 설명 | 예시 |
| --- | --- | --- |
| 아이디어 | 만들고 싶은 앱 또는 서비스 | 자취생 냉장고 재고 관리 앱 |
| 타겟 고객 | 주요 사용자 그룹 | 대학생 자취생, 1인 가구 |
| 지역 | 조사 대상 시장 | 한국, 미국, 글로벌 |
| 서비스 유형 | 서비스 형태 | 모바일 앱, SaaS, 커뮤니티 |

## 검색어 생성

사용자 입력을 바탕으로 다음 유형의 검색어를 만듭니다.

| 유형 | 목적 |
| --- | --- |
| 고객 문제 | 사용자가 실제로 겪는 문제 확인 |
| 시장/수요 | 기사, 통계, 트렌드 자료 확인 |
| 경쟁자 | 유사 앱과 대체 서비스 확인 |
| 가격/수익화 | 유료 앱, 구독, freemium 사례 확인 |
| 구현/API | 구현에 필요한 API와 기술 문서 확인 |
| 대체재 | 사용자가 현재 쓰는 우회 방법 확인 |
| PEST | 정치, 경제, 사회, 기술 환경 신호 확인 |

검색어는 템플릿으로 먼저 만들고, 필요하면 Gemma로 동의어, 영문 표현, 서비스 유형별 표현을 보강합니다. 최종 검색어는 중복 제거와 카테고리별 개수 제한을 거칩니다.

MVP에서는 템플릿 기반 검색어 생성을 기본 구현으로 둡니다. Gemma 기반 보강은 검색 품질을 높이기 위한 선택 단계입니다.

현재는 LLM 토큰을 확보하지 못한 상황을 고려해 임시로 rule 기반 fallback을 둡니다. 이 fallback은 개발과 시연을 막지 않기 위한 장치이며, 프로젝트 방향은 README에 정의한 Gemma 기반 검색어 보강 및 출처 요약을 구현하는 것입니다. Gemma를 사용하는 경우에도 검색어 보강과 요약에만 사용합니다. 출처 없는 내용은 리포트 근거로 쓰지 않습니다.

## 데이터 소스

| 소스 | 용도 | 상태 |
| --- | --- | --- |
| Naver Search API | 웹, 블로그, 뉴스, 카페 문서 검색 | API key가 있으면 사용 |
| Naver News API | 국내 뉴스 기반 정책, 시장, 사회 이슈 확인 | API key가 있으면 사용 |
| Naver DataLab | 키워드별 상대 검색 관심도 확인 | API key가 있으면 사용 |
| Apple iTunes Search API | iOS 경쟁 앱 후보와 앱 메타데이터 수집 | 기본 사용 |
| GDELT | 글로벌 뉴스 기반 PEST 신호 수집 | 기본 사용 |
| Hacker News Algolia API | 개발자/스타트업 커뮤니티 반응 확인 | 기본 사용 |
| GitHub REST API | 관련 오픈소스, API, 기술 생태계 확인 | 기본 사용, token은 선택 |
| OpenAI web_search | 자동 심화 조사 | 선택 기능 |
| Google Trends | PEST의 사회/경제 신호 보완 | 추후 |
| Google Play 데이터 | Android 경쟁 앱 보완 | 추후 |
| 리뷰 수집 도구 | 사용자 불만 분석 | 추후 |
| SNS 데이터 | TikTok, Instagram, X, Reddit, YouTube 등 플랫폼별 반응 보완 | 추후 |

Naver News API는 Naver Search API의 news endpoint를 사용합니다.

## PEST 수집 기준

| 구분 | 확인할 내용 | 주요 소스 |
| --- | --- | --- |
| Political | 규제, 정책, 공공기관 발표, 법적 이슈 | Naver News API, GDELT |
| Economic | 시장 기사, 투자, 가격, 소비 지출, 산업 동향 | Naver News API, GDELT |
| Social | 사용자 행동 변화, 커뮤니티 반응, 사회적 이슈, 가벼운 트렌드 신호 | Naver News API, GDELT, Hacker News Algolia |
| Technological | 관련 API, 오픈소스, 개발 난이도, 기술 채택 흐름 | GitHub REST API, Hacker News Algolia |

가벼운 트렌드 감지는 별도 기능으로 분리하지 않고 PEST 내부의 `signals`로 다룹니다. PEST 결과도 다른 리포트 항목과 마찬가지로 출처가 있는 내용만 요약합니다.

OpenAI `web_search`는 호출 비용이 발생하므로 기본 기능에서 제외합니다. 필요한 경우에만 옵션으로 켜고, 호출 횟수 제한과 캐싱을 둡니다.

## 처리 흐름

```text
User Input
  -> Query Generator
  -> Data Collectors (parallel)
  -> Source Normalizer
  -> Gemma Summary
  -> Temporary Rule Fallback
  -> JSON Report
  -> Frontend Cards
```

## 리포트 구성

리포트는 JSON으로 반환됩니다.

```json
{
  "input": {
    "idea": "",
    "target_customer": "",
    "region": "",
    "service_type": ""
  },
  "generated_queries": {
    "customer_problem": [],
    "market": [],
    "competitors": [],
    "pricing": [],
    "implementation": [],
    "alternatives": [],
    "pest": []
  },
  "report": {
    "customer_problem": {
      "summary": "",
      "evidence": [],
      "unverified": []
    },
    "market_signals": {
      "summary": "",
      "evidence": [],
      "unverified": []
    },
    "competitors": {
      "items": [],
      "evidence": [],
      "unverified": []
    },
    "pricing": {
      "summary": "",
      "evidence": [],
      "unverified": []
    },
    "implementation": {
      "apis": [],
      "technical_constraints": [],
      "evidence": [],
      "unverified": []
    },
    "pest": {
      "political": {
        "summary": "",
        "signals": [],
        "evidence": [],
        "unverified": []
      },
      "economic": {
        "summary": "",
        "signals": [],
        "evidence": [],
        "unverified": []
      },
      "social": {
        "summary": "",
        "signals": [],
        "evidence": [],
        "unverified": []
      },
      "technological": {
        "summary": "",
        "signals": [],
        "evidence": [],
        "unverified": []
      }
    },
    "unknowns": []
  },
  "sources": []
}
```

각 요약은 가능한 한 `source_id`와 연결합니다. 확인되지 않은 내용은 `unverified` 또는 `unknowns`에 넣습니다.

## 하지 않는 것

- 앱 성공 가능성 예측
- 0~100점 점수화
- 출처 없는 시장 규모 추정
- LLM만으로 경쟁 우위 판단
- LLM에만 의존하는 검색어 생성
- 대규모 리뷰 크롤링
- 완전 자동화된 Google Play 분석
- TikTok, Instagram, X 등 SNS 직접 수집

## 기술 스택

- Frontend: React + Vite
- Backend: FastAPI
- Database: SQLite 또는 PostgreSQL
- LLM API: Gemma 기반 검색어 보강, 요약, JSON 구조화
- External APIs:
  - Naver Search API
  - Naver News API
  - Naver DataLab
  - Apple iTunes Search API
  - GDELT
  - Hacker News Algolia API
  - GitHub REST API
  - optional OpenAI web_search

## 폴더 구조

```text
backend/
  app/
    api/
    collectors/
    services/
    schemas/
    core/
frontend/
  src/
docs/
scripts/
```

## 실행 방법

Backend:

```powershell
.\scripts\dev-backend.cmd
```

Frontend:

```powershell
.\scripts\dev-frontend.cmd
```

확인 URL:

```text
http://127.0.0.1:8000/api/health
http://localhost:5173
```

Backend 테스트:

```powershell
cd backend
.\.venv\Scripts\python.exe -m unittest
```

이미 dependency가 설치되어 있으면 install 단계를 건너뛸 수 있습니다.

```powershell
.\scripts\dev-backend.cmd -SkipInstall
.\scripts\dev-frontend.cmd -SkipInstall
```

## 환경 변수

현재 구현은 LLM 토큰이 없어도 개발과 시연이 가능하도록 임시 fallback을 제공합니다. 다만 프로젝트 목표는 Gemma 기반 검색어 보강과 출처 요약을 구현하는 것입니다. API key를 설정하면 더 많은 collector와 Gemma 보강 기능을 사용할 수 있도록 확장합니다.

Backend는 project root의 `.env`와 `backend/.env`를 모두 읽습니다. 같은 변수가 둘 다 있으면 `backend/.env` 값이 우선됩니다. Frontend의 `VITE_API_BASE_URL`은 `frontend/.env`에 둘 수 있습니다.

| 변수 | 필수 여부 | 설명 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 선택 | Gemma 또는 LLM provider 연동 시 검색어 보강, 요약에 사용 |
| `ENABLE_LLM` | 선택 | Gemma/LLM 사용 여부. 현재 기본값은 `false` |
| `NAVER_CLIENT_ID` | 선택 | Naver Search API와 Naver DataLab 호출에 사용 |
| `NAVER_CLIENT_SECRET` | 선택 | Naver Search API와 Naver DataLab 호출에 사용 |
| `DATABASE_URL` | 선택 | 데이터베이스 연결 문자열. 없으면 로컬 SQLite 사용 |
| `GITHUB_TOKEN` | 선택 | GitHub REST API rate limit 완화에 사용 |
| `ENABLE_OPENAI_WEB_SEARCH` | 선택 | OpenAI `web_search` 사용 여부. 기본값은 `false` |
| `WEB_SEARCH_MAX_CALLS_PER_REPORT` | 선택 | 리포트 1개당 OpenAI `web_search` 최대 호출 수 |
| `VITE_API_BASE_URL` | 선택 | Frontend에서 호출할 backend URL. 기본값은 `http://127.0.0.1:8000` |

`.env` 파일은 commit하지 않습니다. 필요한 변수 이름만 `.env.example`, `backend/.env.example`, `frontend/.env.example`에 적습니다.

## 주의사항

- Naver DataLab은 상대 검색 관심도 지표이며 절대 검색량이 아닙니다.
- App Store 결과는 국가, 언어, availability에 따라 달라질 수 있습니다.
- GDELT와 뉴스 데이터는 기사량과 보도 편향의 영향을 받을 수 있습니다.
- Hacker News와 GitHub 데이터는 개발자/기술 커뮤니티 신호이며 일반 소비자 수요와 다를 수 있습니다.
- SNS 데이터는 API 비용, 권한 승인, 정책 제약이 크므로 MVP 기본 수집 대상에서 제외합니다.
- Google Play와 리뷰 데이터는 공식 API 제약과 정책 리스크가 있을 수 있습니다.
- Gemma/LLM 출력은 요약과 구조화 용도입니다. 사실 데이터처럼 표시하지 않습니다.
- 리포트는 결론보다 출처, 근거, 확인 안 된 부분을 함께 보여주는 데 초점을 둡니다.

## 커밋 메시지

```text
feat: add query generator
fix: handle empty collector response
docs: update README
refactor: simplify report schema
chore: update config
test: add collector tests
```
