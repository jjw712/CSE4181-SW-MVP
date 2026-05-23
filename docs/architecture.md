# 예상 아키텍처

이 문서는 README의 프로젝트 방향을 기준으로 한 초기 architecture draft입니다. 현재 구조는 MVP 구현을 시작하기 위한 skeleton이며, 실제 collector와 report generator는 이후 단계에서 구현합니다.

## 전체 흐름

```text
User
  |
  v
Frontend (React + Vite)
  |
  v
Backend API (FastAPI)
  |
  +--> LLM Services
  |      +--> idea structuring
  |      +--> keyword generation
  |      +--> report text generation
  |
  +--> Data Collectors
  |      +--> Naver DataLab
  |      +--> Naver Search API
  |      +--> Apple iTunes Search API
  |
  +--> Report Generator
  |      +--> factual data
  |      +--> interpretation
  |      +--> confidence level
  |
  +--> Database
```

## Backend 책임

- 사용자 app idea 입력을 API request로 수신
- LLM service를 통해 idea summary, target user, keyword 후보 생성
- collector를 통해 search, competition, review, monetization signal 수집
- report generator에서 factual data와 interpretation을 분리해 report 생성
- data confidence를 High / Medium / Low로 표시

## Frontend 책임

- app idea 입력 form 제공
- report 생성 요청
- standardized report section 표시
- confidence level과 data limitation을 사용자에게 명확히 표시

## Collector 책임

초기 MVP에서는 다음 collector를 우선 고려합니다.

- Naver DataLab collector: 한국 검색 trend와 seasonality 확인
- Naver Search collector: web/blog/news/cafe document signal 확인
- Apple App Store collector: iOS competitor app metadata 확인

Google Play, review crawling, Sensor Tower, FoxData, Similarweb, AppFollow, Apify 연동은 MVP 이후 확장 후보입니다.

## 중요한 설계 원칙

- 앱 성공을 예측하거나 보장하지 않습니다.
- 0~100 success score를 핵심 지표로 사용하지 않습니다.
- factual data와 LLM interpretation을 구분합니다.
- 데이터가 부족하면 부족하다고 표시합니다.
- confidence level은 data coverage, source reliability, freshness, signal agreement, data amount를 기준으로 계산합니다.
