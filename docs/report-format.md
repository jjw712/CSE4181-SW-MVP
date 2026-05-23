# 리포트 형식

이 문서는 validation report의 기본 section과 각 section에서 필요한 데이터를 정리합니다. 실제 report generator 구현 시 이 문서를 기준으로 schema와 response format을 구체화합니다.

## 1. 아이디어 요약

- 의미: 사용자가 입력한 앱 아이디어를 문제, 대상, 핵심 기능 중심으로 정리합니다.
- 필요한 데이터: user input, LLM idea structuring 결과
- 사용자 가치: 팀원이 같은 기준으로 아이디어를 이해하고 분석 범위를 통일할 수 있습니다.

## 2. 타깃 사용자

- 의미: 앱을 사용할 가능성이 높은 사용자 group과 사용 상황을 정의합니다.
- 필요한 데이터: user input, LLM target user 추론, keyword context
- 사용자 가치: feature scope와 competitor search 기준을 좁힐 수 있습니다.

## 3. 관련 키워드

- 의미: 검색 수요와 경쟁 앱 탐색에 사용할 keyword set을 정의합니다.
- 필요한 데이터: user input, LLM keyword generation, Naver Search context
- 사용자 가치: 조사 keyword를 일관되게 관리할 수 있습니다.

## 4. 검색 수요 분석

- 의미: keyword별 search trend, 증감, seasonality를 확인합니다.
- 필요한 데이터: Naver DataLab, optional Google Trends
- 사용자 가치: 실제 관심 signal이 존재하는지 판단할 수 있습니다.

## 5. 경쟁 앱 분석

- 의미: 유사 앱의 이름, category, rating, review count, price 정보를 정리합니다.
- 필요한 데이터: Apple iTunes Search API, optional Google Play/third-party data
- 사용자 가치: 기존 solution과 차별화 가능성을 확인할 수 있습니다.

## 6. 리뷰 기반 사용자 불만

- 의미: competitor review에서 반복되는 complaint와 unmet need를 정리합니다.
- 필요한 데이터: App Store review data, future Google Play/third-party review data, LLM complaint extraction
- 사용자 가치: MVP feature와 positioning에 반영할 불편 지점을 찾을 수 있습니다.

## 7. 수익화 구조

- 의미: competitor 또는 유사 서비스의 monetization model을 정리합니다.
- 필요한 데이터: App Store price/IAP signal, competitor metadata, web search, LLM interpretation
- 사용자 가치: paid app, subscription, freemium 등 가능한 수익화 방향을 검토할 수 있습니다.

## 8. 1인 MVP 구현 범위

- 의미: solo builder가 제한된 시간 안에 구현 가능한 feature scope를 제안합니다.
- 필요한 데이터: idea structure, feature extraction, internal rule table, LLM scope suggestion
- 사용자 가치: 처음부터 너무 큰 scope로 시작하는 위험을 줄일 수 있습니다.

## 9. 리스크 요약

- 의미: data limitation, competition, implementation difficulty, API dependency를 정리합니다.
- 필요한 데이터: collected data, internal rule table, LLM risk summarization
- 사용자 가치: 개발 전 확인해야 할 위험 요소를 빠르게 파악할 수 있습니다.

## 10. 추천 방향

- 의미: 개발 시작, pivot, scope 축소, 추가 조사 중 다음 행동을 제안합니다.
- 필요한 데이터: search demand, competitor data, review signal, MVP difficulty, confidence level
- 사용자 가치: 수집된 근거를 바탕으로 다음 결정을 내릴 수 있습니다.

## 11. 데이터 신뢰도

- 의미: report 근거가 얼마나 충분하고 최신이며 일관적인지 표시합니다.
- 필요한 데이터: data coverage, source reliability, freshness, signal agreement, data amount
- 사용자 가치: 분석 결과를 과신하지 않고 불확실성을 함께 고려할 수 있습니다.
