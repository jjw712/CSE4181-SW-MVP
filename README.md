# CSE4181-SW-MVP

## 1. 프로젝트 소개

**CSE4181-SW-MVP**는 vibe coder, indie de
veloper, solo builder를 위한 **앱 아이디어 검증 리포트 플랫폼**입니다.

사용자가 앱 아이디어를 입력하면 시스템은 아이디어를 구조화하고, 관련 keyword를 생성한 뒤, 검색 수요, 경쟁 앱, 리뷰, 수익화 가능성, MVP 구현 범위와 같은 시장 signal을 수집하여 일관된 형식의 validation report로 제공합니다.

이 프로젝트는 앱의 성공을 예측하거나 보장하는 서비스가 아닙니다. 핵심 목적은 사용자가 개발을 시작할지, 아이디어를 pivot할지, MVP scope를 줄일지, 추가 조사를 진행할지 판단할 수 있도록 관련 데이터를 정리해 주는 것입니다.

## 2. 문제 배경

개인 개발자나 소규모 팀은 앱을 만들기 전에 다음과 같은 질문을 자주 마주합니다.

- 이 아이디어와 관련된 검색 수요가 존재하는가?
- 이미 비슷한 앱이 있는가?
- 경쟁 앱 사용자들은 어떤 불만을 가지고 있는가?
- MVP로 시작하려면 어느 기능까지 구현해야 하는가?
- 지금 바로 개발을 시작해도 되는가, 아니면 더 조사해야 하는가?

하지만 이런 정보를 직접 수집하려면 Naver 검색, App Store, trend data, 리뷰, 경쟁 서비스 분석을 각각 따로 확인해야 합니다. 이 과정은 시간이 오래 걸리고, 조사 기준이 매번 달라져 결과를 비교하기 어렵습니다.

## 3. 서비스 목표

이 플랫폼의 목표는 앱 아이디어에 대해 반복 가능한 검증 절차를 제공하는 것입니다.

- 사용자의 rough idea를 구조화된 app concept로 변환
- 관련 keyword와 search intent를 도출
- 검색 수요와 seasonality를 확인
- 경쟁 앱의 category, rating, review count, price 정보를 수집
- 경쟁 앱의 수익화 구조와 feature pattern을 정리
- 1인 개발자가 구현 가능한 MVP scope를 제안
- 데이터가 부족한 부분을 명확히 표시
- 최종적으로 개발 시작, pivot, scope 축소, 추가 조사 중 하나의 추천 방향을 제공

## 4. 핵심 방향: 점수화가 아니라 데이터 기반 검증 리포트

이 서비스는 임의의 **0~100 성공 점수**를 중심으로 설계하지 않습니다.

앱 성공 여부는 시장 상황, 실행력, 출시 timing, distribution, pricing, retention, 경쟁 변화 등 다양한 요인에 의해 달라집니다. 따라서 단순 점수는 오히려 잘못된 확신을 줄 수 있습니다.

대신 본 프로젝트는 다음에 집중합니다.

- 관련 market, competition, search, review data를 수집
- 수집된 데이터를 동일한 report format으로 정리
- 사실 데이터와 LLM interpretation을 구분
- 데이터가 부족하거나 불확실한 영역을 confidence level로 표시
- 사용자가 다음 행동을 결정할 수 있게 실용적인 판단 근거 제공

## 5. 주요 기능

아래 기능은 첫 MVP의 목표 범위입니다. 실제 구현 여부는 repository의 코드와 issue 상태를 기준으로 확인해야 합니다.

- App idea input
- LLM 기반 아이디어 요약 및 구조화
- LLM 기반 관련 keyword 생성
- Naver DataLab 기반 검색 수요 및 seasonality 분석
- Apple iTunes Search API 기반 iOS 경쟁 앱 검색
- 경쟁 앱의 기본 metadata 수집
- 경쟁 앱 기반 기본 monetization structure 추정
- 1인 MVP 구현 범위 제안
- 주요 risk summary 생성
- data confidence 표시
- 표준화된 validation report 출력

## 6. 리포트 구성

| 섹션 | 의미 | 필요한 데이터 | 사용자에게 주는 가치 |
| --- | --- | --- | --- |
| 1. 아이디어 요약 | 사용자가 입력한 앱 아이디어를 문제, 대상, 핵심 기능 중심으로 정리합니다. | 사용자 입력, LLM 기반 idea structuring | 아이디어를 팀원이 같은 방식으로 이해하고 이후 분석 기준을 통일할 수 있습니다. |
| 2. 타깃 사용자 | 앱을 사용할 가능성이 높은 사용자 group과 사용 상황을 정의합니다. | 사용자 입력, LLM 기반 target user 추론, keyword context | 누구를 위해 만들 것인지 명확히 하여 feature scope와 경쟁 앱 기준을 좁힐 수 있습니다. |
| 3. 관련 키워드 | 검색과 경쟁 앱 탐색에 사용할 주요 keyword set을 생성합니다. | 사용자 입력, LLM keyword generation, Naver Search context | 조사할 keyword를 체계화하여 데이터 수집의 누락을 줄입니다. |
| 4. 검색 수요 분석 | 관련 keyword의 검색 trend, 증감, seasonality를 확인합니다. | Naver DataLab, optional Google Trends | 실제 관심이 존재하는지, 특정 시기에 수요가 집중되는지 판단할 수 있습니다. |
| 5. 경쟁 앱 분석 | 유사 앱의 이름, category, rating, review count, 가격 정보를 정리합니다. | Apple iTunes Search API, optional Google Play/third-party data | 이미 존재하는 solution과 시장 혼잡도를 파악하고 차별화 방향을 찾을 수 있습니다. |
| 6. 리뷰 기반 사용자 불만 | 경쟁 앱 review에서 반복되는 complaint와 unmet need를 정리합니다. | App Store review data, future Google Play/third-party review data, LLM complaint extraction | 사용자가 실제로 불편해하는 지점을 찾아 MVP feature와 positioning에 반영할 수 있습니다. |
| 7. 수익화 구조 | 경쟁 앱 또는 유사 서비스의 monetization model을 정리합니다. | App Store price/IAP signal, competitor metadata, web search, LLM interpretation | 무료, paid app, subscription, freemium 등 가능한 수익화 방향을 검토할 수 있습니다. |
| 8. 1인 MVP 구현 범위 | solo builder가 제한된 시간 안에 만들 수 있는 feature scope를 제안합니다. | 아이디어 구조, feature extraction, internal rule table, LLM scope suggestion | 처음부터 너무 큰 앱을 만들지 않도록 MVP 범위를 현실적으로 줄일 수 있습니다. |
| 9. 리스크 요약 | 데이터 부족, 경쟁 강도, 구현 난이도, API dependency 같은 주요 risk를 정리합니다. | 수집 데이터 전반, internal rule table, LLM risk summarization | 개발 전 확인해야 할 위험 요소를 한눈에 파악할 수 있습니다. |
| 10. 추천 방향 | 개발 시작, pivot, scope 축소, 추가 조사 등 다음 행동을 제안합니다. | 검색 수요, 경쟁 앱, review signal, MVP difficulty, data confidence | 사용자가 막연한 감이 아니라 수집된 근거를 바탕으로 다음 결정을 내릴 수 있습니다. |
| 11. 데이터 신뢰도 | 보고서의 근거가 얼마나 충분하고 최신이며 일관적인지 표시합니다. | data coverage, source reliability, freshness, signal agreement | 분석 결과를 과신하지 않고 불확실성을 함께 고려할 수 있습니다. |

## 7. 데이터 출처 계획

### User Input

- app idea
- target user
- rough concept
- problem statement
- optional feature description

### LLM

LLM은 다음 작업에 사용합니다.

- idea structuring
- keyword generation
- feature extraction
- MVP scope suggestion
- risk summarization
- report text generation

LLM은 unsupported claim이나 성공 예측을 위해 사용하지 않습니다. 수집된 데이터가 부족한 경우에는 부족하다고 표시해야 합니다.

### Naver DataLab

- Korean search trend 분석
- keyword별 상대적 관심도 확인
- seasonality 및 trend 변화 확인

Search trend data는 일반적으로 절대 검색량이 아니라 상대 지표이므로 해석에 주의해야 합니다.

### Naver Search API

- 관련 web/blog/news/cafe document signal 수집
- keyword context 확인
- 관련 문제, 제품, 경쟁 서비스 언급 탐색

### Apple iTunes Search API

- iOS competitor app search
- app name
- category
- rating
- review count
- price information
- store URL

국가, platform, availability에 따라 결과가 달라질 수 있습니다.

### Google Trends

- optional global 또는 regional relative search interest 확인
- Naver DataLab과 함께 trend signal 비교

### Google Play Public Data

Google Play는 본 프로젝트 목적에 맞는 clean official competitor-search API가 제한적입니다. 따라서 Google Play competitor data는 MVP 필수 범위가 아니라 future extension으로 다루며, public collection이나 third-party tool 사용 시 reliability와 policy risk를 명확히 표시해야 합니다.

### Third-Party Services

다음 서비스는 future extension 후보이며 MVP 필수 요소가 아닙니다.

- Sensor Tower
- FoxData
- Similarweb
- AppFollow
- Apify

### Internal Rule Table

MVP 구현 난이도는 internal rule table로 보조 판단합니다.

예시 feature type:

- CRUD
- login
- push notification
- real-time chat
- payment
- calendar integration
- external API dependency

이 rule table은 절대적인 난이도 판단이 아니라 MVP scope를 줄이기 위한 참고 기준입니다.

## 8. 데이터 신뢰도 처리 방식

각 report에는 **High / Medium / Low** 형태의 confidence level을 표시합니다.

Confidence는 다음 기준을 함께 고려합니다.

- Data coverage: 검색, 경쟁 앱, 리뷰, 수익화 데이터가 충분히 수집되었는가
- Source reliability: 공식 API 또는 신뢰 가능한 source인가
- Freshness: 데이터가 충분히 최신인가
- Signal agreement: 여러 signal이 서로 비슷한 방향을 가리키는가
- Data amount: competitor, review, search data의 양이 충분한가

Confidence 예시:

- High: 검색 trend, competitor app, review, monetization data가 충분히 존재하고 signal이 대체로 일관적입니다.
- Medium: 주요 데이터는 존재하지만 review 또는 monetization data 일부가 제한적입니다.
- Low: 검색량, competitor app, review data가 부족하여 결론을 강하게 내리기 어렵습니다.

이 프로젝트는 모든 결론이 확실한 것처럼 표현하지 않습니다. 데이터가 부족한 경우에는 report에서 그 한계를 명확히 보여주어야 합니다.

## 9. MVP 범위

첫 MVP는 아이디어 검증 report를 생성하는 최소 흐름에 집중합니다.

포함 범위:

- App idea 입력 화면
- LLM 기반 idea summary 생성
- LLM 기반 related keyword 생성
- Naver DataLab 기반 search demand analysis
- Apple iTunes Search API 기반 competitor app search
- 경쟁 앱의 기본 monetization structure 추출
- MVP feature scope suggestion
- risk summary
- data confidence display
- standardized report output

MVP에서 제외하거나 제한적으로 다룰 항목:

- 정확한 시장 규모 추정
- 앱 성공 확률 예측
- 임의의 0~100 success score
- 완전 자동화된 Google Play competitor analysis
- 대규모 review crawling
- user account 및 saved report
- paid report 또는 subscription 결제

## 10. 향후 확장 기능

- Google Play competitor data support
- review text collection 및 complaint analysis
- PDF report export
- 여러 아이디어를 비교하는 idea comparison feature
- user accounts
- saved reports
- paid report 또는 subscription model
- Sensor Tower / FoxData / Similarweb integration
- AppFollow 또는 Apify 기반 review/competitor collector
- 더 정교한 confidence calculation
- report history 및 versioning
- team collaboration 기능

## 11. 기술 스택

권장 기술 스택은 다음과 같습니다.

- Frontend: React + Vite
- Backend: FastAPI
- Database: PostgreSQL 또는 early MVP용 SQLite
- Cache / Background Jobs: Redis + Celery 또는 RQ, future extension
- LLM API: idea structuring 및 report generation
- Data Collectors:
  - Naver DataLab collector
  - Naver Search collector
  - Apple App Store collector
  - optional trend/review collectors
- Report Generator:
  - 수집 데이터를 일관된 report format으로 결합
  - factual data와 interpretation을 구분

## 12. 예상 아키텍처

```text
User
  |
  v
Frontend (React + Vite)
  |
  v
Backend API (FastAPI)
  |
  +--> Idea Structuring Service (LLM)
  |
  +--> Keyword Generation Service (LLM)
  |
  +--> Collectors
  |      +--> Naver DataLab
  |      +--> Naver Search API
  |      +--> Apple iTunes Search API
  |      +--> Optional Trend/Review Collectors
  |
  +--> Report Generator
  |      +--> factual data
  |      +--> LLM interpretation
  |      +--> confidence calculation
  |
  +--> Database (PostgreSQL or SQLite)
```

제안 folder structure:

```text
backend/
  app/
    api/
    collectors/
    services/
    report/
    schemas/
    core/
frontend/
  src/
docs/
  report-format.md
  architecture.md
```

## 13. 실행 방법

현재 프로젝트는 backend/frontend의 최소 skeleton을 제공합니다. Windows PowerShell 환경에서 Python 또는 Node.js PATH가 터미널마다 다르게 잡힐 수 있으므로, repository의 실행 script를 사용하는 방식을 권장합니다.

Backend 실행:

```powershell
cd C:\Users\jiwon\source\repos\CSE4181-SW-MVP
.\scripts\dev-backend.cmd
```

Backend 확인:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/api/health
```

Frontend 실행:

```powershell
cd C:\Users\jiwon\source\repos\CSE4181-SW-MVP
.\scripts\dev-frontend.cmd
```

Frontend 확인:

```text
http://localhost:5173
```

Dependency가 이미 설치되어 있으면 다음처럼 install 단계를 건너뛸 수 있습니다.

```powershell
.\scripts\dev-backend.cmd -SkipInstall
.\scripts\dev-frontend.cmd -SkipInstall
```

## 14. 환경 변수 관리

API key와 private credential은 repository에 commit하지 않습니다.

사용 예정 환경 변수 예시:

```env
LLM_API_KEY=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
DATABASE_URL=
```

관리 원칙:

- `.env` 파일은 commit하지 않습니다.
- 필요한 환경 변수는 `.env.example`에 이름만 문서화합니다.
- API key, access token, private credential은 issue, PR, commit message에 포함하지 않습니다.
- local, staging, production 환경의 값을 분리합니다.

## 15. 협업 규칙

- main branch에 직접 push하지 않습니다.
- feature branch를 사용합니다.
- 변경 사항은 pull request로 공유합니다.
- commit은 작고 의미 있게 나눕니다.
- source code 변경과 문서 변경은 가능한 한 분리합니다.
- `.env` 파일을 commit하지 않습니다.
- large dataset, API key, private credential을 repository에 업로드하지 않습니다.
- 구현되지 않은 기능을 README나 발표 자료에서 이미 완성된 것처럼 설명하지 않습니다.
- 데이터 출처와 한계를 report 및 문서에 명확히 표시합니다.

## 16. 커밋 메시지 규칙

Commit message는 다음 convention을 따릅니다.

```text
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 변경
refactor: 코드 구조 개선
chore: 설정 또는 유지보수 작업
test: 테스트 추가 또는 수정
```

예시:

```text
docs: update project README
feat: add idea input form
fix: handle empty keyword response
```

## 17. 주의사항

- 이 시스템은 앱 성공을 예측하거나 보장하지 않습니다.
- 임의의 0~100 success score를 핵심 지표로 사용하지 않습니다.
- 검색 trend data는 대체로 상대 지표이며 절대 검색량이 아닙니다.
- App Store data는 국가, platform, availability에 따라 달라질 수 있습니다.
- Review data는 안정적으로 수집하기 어려울 수 있습니다.
- Google Play competitor data는 공식 API 제약으로 인해 third-party tool 또는 제한적 public collection이 필요할 수 있습니다.
- LLM output은 해석과 요약에 사용하며, factual data처럼 표시하지 않습니다.
- Report는 conclusion보다 evidence와 confidence를 함께 보여주는 방식으로 작성해야 합니다.
