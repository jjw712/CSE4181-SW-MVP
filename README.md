# WTBH - What To Build Helper

WTBH는 앱 또는 서비스 아이디어를 입력하면 공개 데이터 소스에서 근거를 수집하고, 고객 문제·시장 신호·경쟁 앱·가격/수익화·구현 가능성·PEST 리스크를 한 번에 정리하는 아이디어 검증 MVP입니다.

이 프로젝트는 "성공 가능성 점수"를 임의로 계산하지 않습니다. 대신 출처가 있는 자료와 아직 검증되지 않은 가정을 분리해, 개발 전에 무엇을 더 확인해야 하는지 보여주는 데 초점을 둡니다.

## Why

초기 아이디어 검증은 보통 검색, 경쟁 앱 확인, 뉴스 조사, 구현 자료 탐색이 흩어져 진행됩니다. WTBH는 이 과정을 하나의 리포트 흐름으로 묶어 다음 질문에 답하도록 설계했습니다.

- 이 아이디어와 관련된 사용자 문제 근거가 있는가?
- 비슷한 앱이나 서비스가 이미 존재하는가?
- 가격, 구독, freemium 같은 수익화 단서가 보이는가?
- 구현에 필요한 API, 오픈소스, 기술 생태계가 있는가?
- 정책, 경제, 사회, 기술 관점에서 주의할 신호가 있는가?

## Features

- 앱/서비스 아이디어, 타겟 고객, 지역, 서비스 유형 입력
- 카테고리별 검색어 자동 생성
- 공개 collector를 통한 source 수집
- 서로 다른 API 응답을 공통 source schema로 정규화
- source 수, source type, collector 실패 여부를 반영한 confidence 표시
- 고객 문제, 시장 신호, 경쟁 앱, 가격/수익화, 구현/API, PEST 리포트 생성
- 외부 API 또는 LLM이 없어도 시연 가능한 rule 기반 fallback
- React/Vite 프론트엔드에서 리포트 카드와 source 목록 확인

## Data Sources

| Source | Purpose | Key Required |
| --- | --- | --- |
| Apple iTunes Search API | iOS 경쟁 앱 후보와 앱 메타데이터 수집 | No |
| Hacker News Algolia API | 개발자/스타트업 커뮤니티 반응 확인 | No |
| GitHub REST API | 구현 자료, 오픈소스, 기술 생태계 확인 | Optional |
| GDELT | 글로벌 뉴스 기반 PEST 신호 수집 | No |
| Naver Search API | 웹/뉴스 기반 국내 자료 검색 | Yes |
| Naver DataLab | 키워드 검색 관심도 확인 | Yes |

## Architecture

```text
User Input
  -> Frontend (React + Vite)
  -> Backend API (FastAPI)
  -> Query Generator
  -> Data Collectors
  -> Source Normalizer
  -> Report Generator
  -> Confidence Calculator
  -> JSON Report
  -> Frontend Report Cards
```

자세한 설계는 [docs/architecture.md](docs/architecture.md)를 참고하세요.

## Tech Stack

- Frontend: React, Vite
- Backend: FastAPI, Pydantic
- HTTP integration: urllib 기반 lightweight collector
- Testing: unittest, FastAPI TestClient
- External APIs: Apple iTunes, Hacker News Algolia, GitHub REST, GDELT, Naver Search/DataLab

## Repository Structure

```text
backend/
  app/
    api/          # FastAPI routes
    collectors/   # external data collectors
    core/         # settings
    report/       # report body and confidence generation
    schemas/      # request/response models
    services/     # orchestration and normalization
  tests/
frontend/
  src/
docs/
scripts/
```

## Getting Started

### Backend

```powershell
.\scripts\dev-backend.cmd
```

Backend health check:

```text
http://127.0.0.1:8000/api/health
```

### Frontend

```powershell
.\scripts\dev-frontend.cmd
```

Frontend URL:

```text
http://localhost:5173
```

### Skip Dependency Install

이미 dependency가 설치되어 있으면 다음처럼 실행할 수 있습니다.

```powershell
.\scripts\dev-backend.cmd -SkipInstall
.\scripts\dev-frontend.cmd -SkipInstall
```

## Tests

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Frontend build:

```powershell
cd frontend
npm run build
```

## Environment Variables

Backend는 project root의 `.env`와 `backend/.env`를 읽습니다. 같은 변수가 두 파일에 모두 있으면 `backend/.env` 값이 우선됩니다. Frontend는 Vite 규칙에 따라 `frontend/.env`의 `VITE_*` 변수를 읽습니다.

| Variable | Required | Description |
| --- | --- | --- |
| `NAVER_CLIENT_ID` | Optional | Naver Search/DataLab 호출 |
| `NAVER_CLIENT_SECRET` | Optional | Naver Search/DataLab 호출 |
| `GITHUB_TOKEN` | Optional | GitHub REST API rate limit 완화 |
| `DATABASE_URL` | Optional | 향후 persistence 확장용 |
| `ENABLE_LLM` | Optional | 향후 LLM 기반 검색어 보강/요약 사용 여부 |
| `OPENAI_API_KEY` or `LLM_API_KEY` | Optional | 향후 LLM provider 연동 |
| `VITE_API_BASE_URL` | Optional | Frontend에서 호출할 backend URL |

실제 secret은 commit하지 않습니다. 필요한 변수 이름만 `.env.example`, `backend/.env.example`, `frontend/.env.example`에 둡니다.

## Current Limitations

- 현재 리포트 본문은 source-grounded LLM 요약이 아니라 rule 기반 fallback으로 생성됩니다.
- 외부 API 응답 품질과 네트워크 상태에 따라 source 수집 결과가 달라질 수 있습니다.
- GDELT, GitHub, Naver 등 일부 API는 rate limit 또는 timeout이 발생할 수 있습니다.
- 경쟁 앱 분석은 App Store metadata 중심이며, 리뷰 본문 분석은 아직 포함하지 않았습니다.
- 로그인, 저장된 리포트 관리, 사용자별 히스토리는 아직 구현하지 않았습니다.

## Roadmap

- React 코드를 TypeScript로 전환
- sample report 모드 추가로 데모 안정성 개선
- source-grounded LLM summary 구현
- 리포트 저장 기능과 이전 리포트 조회 기능 추가
- Dockerfile과 배포 설정 추가
- README에 실제 데모 화면과 배포 URL 추가

## Portfolio Summary

WTBH는 단순 CRUD 앱이 아니라, 여러 외부 데이터를 수집하고 정규화한 뒤 사용자가 의사결정에 쓸 수 있는 리포트로 재구성하는 프로젝트입니다. 포트폴리오에서는 다음 역량을 보여줄 수 있습니다.

- API integration과 장애 처리
- 데이터 정규화와 리포트 schema 설계
- FastAPI 기반 backend orchestration
- React 기반 결과 시각화
- 테스트 가능한 collector/reporter 구조
- 출처 기반 정보와 미검증 가정을 분리하는 제품 설계
