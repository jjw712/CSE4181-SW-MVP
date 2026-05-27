# 예상 아키텍처

현재 구조는 README에 정의한 Gemma 기반 검색어 보강 및 출처 요약을 목표로 합니다. 다만 아직 LLM 토큰을 확보하지 못한 상황을 고려해, 개발과 시연을 막지 않도록 임시 rule fallback을 둡니다.

## 전체 흐름

```text
User Input
  |
  v
Frontend (React + Vite)
  |
  v
Backend API (FastAPI)
  |
  +--> Query Generator
  |      +--> template/rule 기반 검색어 생성
  |      +--> Gemma query expansion
  |
  +--> Data Collectors
  |      +--> Apple iTunes Search API (key 불필요)
  |      +--> Hacker News Algolia API (key 불필요)
  |      +--> GitHub REST API (token 선택)
  |      +--> GDELT (key 불필요)
  |      +--> Naver Search / News / DataLab (key 필요)
  |
  +--> Source Normalizer
  |
  +--> Report Generator
  |      +--> Gemma source-grounded summary
  |      +--> temporary rule fallback
  |      +--> confidence level
  |
  v
JSON Report
```

## Backend 책임

- 사용자 app idea 입력을 API request로 수신
- template 기반 query set 생성
- 가능한 collector를 실행하고 실패한 collector는 report metadata에 기록
- 외부 collector는 병렬로 실행해 응답 지연을 줄임
- 서로 다른 API 응답을 공통 source schema로 정규화
- Gemma 기반 report section 생성을 목표로 하되, 현재는 임시 rule fallback으로 report section 생성
- data confidence를 High / Medium / Low로 표시

## Frontend 책임

- `idea`, `target_customer`, `region`, `service_type` 입력 form 제공
- `POST /api/reports` 호출
- generated queries, report sections, sources, confidence metadata 표시
- Gemma/LLM 사용 여부와 skipped/failed collector 상태를 사용자에게 노출

## 환경 변수 로딩

- Backend는 project root의 `.env`와 `backend/.env`를 읽습니다.
- 같은 변수가 두 파일에 모두 있으면 `backend/.env` 값이 우선됩니다.
- Frontend는 Vite 규칙에 따라 `frontend/.env`의 `VITE_*` 변수를 읽습니다.
- 실제 key가 없어도 기본 report flow는 동작해야 합니다.

## 중요한 설계 원칙

- 앱 성공을 예측하거나 보장하지 않습니다.
- 0~100 success score를 핵심 지표로 사용하지 않습니다.
- 현재 구현은 LLM 토큰 부재를 고려해 Gemma를 호출하지 않습니다. 이 동작은 임시 fallback이며, 앞으로는 README에 맞춰 Gemma 기반 보강과 요약을 구현합니다.
- factual data와 interpretation을 구분합니다.
- 데이터가 부족하면 `unverified` 또는 `unknowns`에 표시합니다.
- confidence level은 source 수, source type, category coverage, collector 실패 여부를 기준으로 계산합니다.
