# 리포트 형식

Backend는 `POST /api/reports` 요청에 대해 아래 구조의 JSON report를 반환합니다.

## Request

```json
{
  "idea": "자취생 냉장고 재고 관리 앱",
  "target_customer": "대학생 자취생, 1인 가구",
  "region": "한국",
  "service_type": "모바일 앱",
  "max_results_per_source": 3,
  "use_live_collectors": true
}
```

## Response

```json
{
  "input": {},
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
      "political": {},
      "economic": {},
      "social": {},
      "technological": {}
    },
    "unknowns": []
  },
  "sources": [],
  "meta": {
    "confidence_level": "Low",
    "confidence_reasons": [],
    "llm_used": false,
    "live_collectors_used": true,
    "skipped_collectors": [],
    "failed_collectors": [],
    "collector_errors": {}
  }
}
```

## Source Schema

```json
{
  "source_id": "apple_itunes_1",
  "source_type": "apple_itunes",
  "category": "competitors",
  "title": "",
  "url": "",
  "snippet": "",
  "query": "",
  "published_at": null,
  "raw": {}
}
```

## 원칙

- `evidence`에는 가능한 한 `source_id`를 연결합니다.
- 확인되지 않은 내용은 `unverified` 또는 `unknowns`에 넣습니다.
- 현재 구현은 LLM 토큰 부재를 고려해 Gemma를 호출하지 않으며 `llm_used`는 `false`로 반환됩니다.
- 이 동작은 임시 fallback입니다. 프로젝트 목표는 README에 맞춰 Gemma 기반 검색어 보강과 출처 요약을 구현하는 것입니다.
- 향후 Gemma/LLM이 사용되더라도 source가 없는 주장은 report 근거로 사용하지 않습니다.
- 외부 API collector가 실패하면 전체 요청을 실패시키지 않고 `failed_collectors`와 `collector_errors`에 기록합니다.
