# 현재 MVP 제약 사항

이 문서는 README의 제품 방향을 유지하면서, 현재 MVP에서 현실적으로 완전히 구현하기 어렵거나 외부 API 정책상 제한되는 부분을 정리합니다.

## 공식 API 제약

- Google Play 경쟁 앱 검색은 이 프로젝트 목적에 맞는 깨끗한 official competitor search API가 없어 현재 MVP 기본 범위에서 제외합니다.
- App Store 경쟁 앱 데이터는 Apple iTunes Search API 기준이므로 국가, 언어, availability에 따라 결과가 달라질 수 있습니다.
- Naver DataLab은 상대 관심도 지표입니다. 절대 검색량, 사용자 수, 시장 규모로 해석하지 않습니다.
- GDELT는 public endpoint 특성상 429 rate limit이 발생할 수 있습니다. 현재는 실패 metadata에 기록하고 전체 report flow는 유지합니다.

## 리뷰 기반 사용자 불만 분석

- 현재 MVP는 app review text를 안정적으로 수집하지 않습니다.
- Apple iTunes Search API에서 rating/review count metadata는 일부 확인할 수 있지만, 리뷰 본문 complaint clustering은 별도 collector가 필요합니다.
- Google Play review 수집은 공식 API 제약과 정책 리스크가 있어 third-party 서비스 또는 제한적 public collection을 검토해야 합니다.

## LLM 사용 범위

- Gemini 2.5 Flash는 검색어 보강과 source 기반 요약에만 사용합니다.
- Gemini output은 사실 데이터가 아니며, source가 없는 내용은 `unverified` 또는 `unknowns`로 표시해야 합니다.
- Gemini 호출 실패, JSON 파싱 실패, API key 부재 상황에서는 rule fallback을 사용합니다.
- token 절약을 위해 raw API response, 긴 HTML, 중복 source는 Gemini에 전달하지 않습니다.

## 리포트 해석 제약

- 이 서비스는 앱 성공 가능성을 예측하지 않습니다.
- 0~100 success score를 제공하지 않습니다.
- report의 추천 방향은 start/pivot/scope-down/further investigation을 돕는 보조 판단이며, 시장 성공 보장이 아닙니다.
- source relevance는 rule 기반 보조 지표이므로 낮은 관련성을 완벽히 걸러내지는 못합니다.

## 향후 보완 후보

- source relevance scoring 고도화
- review collector와 complaint clustering
- Google Play 데이터 연동 방식 검토
- GDELT rate limit 대응 강화
- PDF export
- saved reports와 idea comparison
