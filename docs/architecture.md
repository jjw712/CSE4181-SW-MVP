# Architecture

WTBH는 앱 아이디어 검증을 위한 source-based report pipeline입니다. 핵심 목표는 외부 데이터를 무리하게 하나의 점수로 압축하는 것이 아니라, 근거가 있는 정보와 아직 검증되지 않은 가정을 분리해 보여주는 것입니다.

## System Flow

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
  |
  +--> Data Collectors
  |      +--> Apple iTunes Search API
  |      +--> Hacker News Algolia API
  |      +--> GitHub REST API
  |      +--> GDELT
  |      +--> Naver Search API
  |      +--> Naver DataLab API
  |
  +--> Source Normalizer
  |
  +--> Report Generator
  |
  +--> Confidence Calculator
  |
  v
JSON Report
```

## Backend Responsibilities

- 사용자 입력을 `IdeaRequest` schema로 검증합니다.
- 입력값을 기반으로 고객 문제, 시장, 경쟁자, 가격, 구현, 대체재, PEST 검색어를 생성합니다.
- 사용 가능한 collector를 병렬로 실행해 응답 시간을 줄입니다.
- API key가 없거나 비활성화된 collector는 `skipped_collectors`에 기록합니다.
- timeout, rate limit, network error 등 collector 실패는 전체 리포트 생성을 막지 않고 `collector_errors`에 기록합니다.
- 서로 다른 외부 API 응답을 `SourceItem` schema로 정규화합니다.
- source 수, source type 수, category coverage, 실패 collector 여부를 이용해 confidence를 계산합니다.
- 현재는 rule 기반 fallback으로 리포트 본문을 생성합니다.

## Frontend Responsibilities

- 아이디어, 타겟 고객, 지역, 서비스 유형, source 수, live collector 사용 여부를 입력받습니다.
- `POST /api/reports`를 호출합니다.
- 생성된 검색어와 리포트 섹션을 카드 형태로 표시합니다.
- source 목록, confidence, skipped/failed collector 상태를 함께 표시합니다.

## Key Schemas

### Request

```json
{
  "idea": "자취생 냉장고 재고 관리 앱",
  "target_customer": "대학생 자취생",
  "region": "한국",
  "service_type": "모바일 앱",
  "max_results_per_source": 3,
  "use_live_collectors": true
}
```

### Source Item

```json
{
  "source_id": "apple_itunes_1",
  "source_type": "apple_itunes",
  "category": "competitors",
  "title": "Example App",
  "url": "https://example.com",
  "snippet": "Productivity / Free",
  "query": "냉장고 재고 관리 앱",
  "published_at": null,
  "raw": {}
}
```

### Report Meta

```json
{
  "confidence_level": "Medium",
  "confidence_reasons": [
    "수집된 source 10개",
    "source type 4종",
    "경쟁 앱 후보 데이터가 포함됨"
  ],
  "llm_used": false,
  "live_collectors_used": true,
  "skipped_collectors": ["llm"],
  "failed_collectors": ["gdelt"],
  "collector_errors": {
    "gdelt": "URLError: timeout"
  }
}
```

## Confidence Calculation

현재 confidence는 다음 신호를 기반으로 계산합니다.

- 수집된 source 개수
- source type 다양성
- 경쟁 앱 데이터 포함 여부
- 시장/검색 관심도 데이터 포함 여부
- 실패 collector 존재 여부
- live collector 사용 여부

기준은 보수적으로 잡습니다. source가 많아도 실패 collector가 있거나 category coverage가 부족하면 High로 올리지 않습니다.

## Fallback Strategy

LLM 또는 일부 외부 API가 없어도 기본 흐름은 동작해야 합니다. 이 프로젝트는 다음 fallback을 둡니다.

- LLM token이 없으면 rule 기반 리포트 문구를 생성합니다.
- Naver key가 없으면 Naver collector를 건너뜁니다.
- 특정 collector가 실패해도 전체 API 응답은 200으로 유지하고 실패 정보를 meta에 기록합니다.
- source가 부족한 섹션은 `unverified` 또는 `unknowns`에 추가 검증 항목을 남깁니다.

## Design Principles

- 성공 가능성을 임의 점수로 예측하지 않습니다.
- 출처가 있는 정보와 추론을 구분합니다.
- 데이터가 부족하면 부족하다고 표시합니다.
- 외부 API 실패를 사용자와 개발자가 확인할 수 있게 드러냅니다.
- 시연 안정성을 위해 collector 실패가 전체 리포트 실패로 번지지 않게 합니다.

## Planned Improvements

- TypeScript 기반 frontend type safety
- deterministic sample report mode
- source-grounded LLM summary
- persisted reports with database storage
- Docker-based local execution
- deployment-ready configuration
