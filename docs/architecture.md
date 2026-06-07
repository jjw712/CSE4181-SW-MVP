# 예상 아키텍처

현재 구조는 README에 정의한 Gemini 2.5 Flash 기반 검색어 보강 및 출처 요약을 구현합니다. Gemini API key가 없거나 호출이 실패하면 개발과 시연을 막지 않도록 rule fallback으로 내려갑니다.

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
  |      +--> Gemini 2.5 Flash query expansion
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
  |      +--> Gemini 2.5 Flash source-grounded summary
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
- Gemini 2.5 Flash로 검색어를 보강하고 source-grounded report section을 요약
- Gemini API key가 없거나 호출이 실패하면 rule fallback으로 report section 생성
- data confidence를 High / Medium / Low로 표시

## Frontend 책임

- `idea`, `target_customer`, `region`, `service_type` 입력 form 제공
- `POST /api/reports` 호출
- generated queries, report sections, sources, confidence metadata 표시
- Gemini 2.5 Flash 사용 여부와 skipped/failed collector 상태를 사용자에게 노출

## 환경 변수 로딩

- Backend는 project root의 `.env`와 `backend/.env`를 읽습니다.
- 같은 변수가 두 파일에 모두 있으면 `backend/.env` 값이 우선됩니다.
- Frontend는 Vite 규칙에 따라 `frontend/.env`의 `VITE_*` 변수를 읽습니다.
- 실제 key가 없어도 기본 report flow는 동작해야 합니다.

## 중요한 설계 원칙

- 앱 성공을 예측하거나 보장하지 않습니다.
- 0~100 success score를 핵심 지표로 사용하지 않습니다.
- Gemini 2.5 Flash는 검색어 보강과 source 기반 요약에만 사용합니다.
- LLM 호출 결과가 없거나 검증에 실패하면 rule fallback 결과를 유지합니다.
- factual data와 interpretation을 구분합니다.
- 데이터가 부족하면 `unverified` 또는 `unknowns`에 표시합니다.
- confidence level은 source 수, source type, category coverage, collector 실패 여부를 기준으로 계산합니다.

## Gemini token 절약 설계

- 리포트 1개당 Gemini 호출은 검색어 보강 1회, 출처 요약 1회를 기본 상한으로 둡니다.
- collector별 원본 응답 전체를 보내지 않고, `SourceItem`의 핵심 필드만 보냅니다.
- `LLM_MAX_INPUT_SOURCES`로 Gemini에 전달할 source 수를 제한합니다.
- `LLM_MAX_CHARS_PER_SOURCE`로 source 1개당 snippet 길이를 제한합니다.
- `LLM_MAX_OUTPUT_TOKENS`로 응답 길이를 제한합니다.
- Gemini Google Search grounding은 `ENABLE_GOOGLE_SEARCH_GROUNDING=false`를 기본값으로 두고, collector 데이터가 부족할 때만 선택적으로 사용합니다.
