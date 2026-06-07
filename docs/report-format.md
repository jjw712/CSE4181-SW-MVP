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
    "idea_summary": {
      "summary": "",
      "evidence": [],
      "unverified": []
    },
    "target_users": {
      "summary": "",
      "evidence": [],
      "unverified": []
    },
    "related_keywords": {
      "summary": "",
      "keywords": [],
      "evidence": [],
      "unverified": []
    },
    "search_demand": {
      "summary": "",
      "evidence": [],
      "unverified": []
    },
    "competitors": {
      "items": [],
      "evidence": [],
      "unverified": []
    },
    "review_pain_points": {
      "summary": "",
      "evidence": [],
      "unverified": []
    },
    "monetization": {
      "summary": "",
      "evidence": [],
      "unverified": []
    },
    "mvp_scope": {
      "summary": "",
      "apis": [],
      "mvp_features": [],
      "technical_constraints": [],
      "evidence": [],
      "unverified": []
    },
    "risks": {
      "summary": "",
      "evidence": [],
      "unverified": []
    },
    "recommendation": {
      "summary": "",
      "evidence": [],
      "unverified": []
    },
    "data_confidence": {
      "summary": "",
      "evidence": [],
      "unverified": []
    },
    "unknowns": []
  },
  "sources": [],
  "meta": {
    "confidence_level": "Low",
    "confidence_reasons": [],
    "llm_used": false,
    "llm_provider": null,
    "llm_model": null,
    "llm_error": null,
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
- `ENABLE_LLM=true`와 `GEMINI_API_KEY`가 설정되면 Gemini 2.5 Flash 기반 검색어 보강과 출처 요약을 사용합니다.
- Gemini API key가 없거나 호출이 실패하면 rule fallback 결과를 반환하며, 실패 정보는 `llm_error` 또는 `skipped_collectors`에 표시합니다.
- Gemini 2.5 Flash가 사용되더라도 source가 없는 주장은 report 근거로 사용하지 않습니다.
- 외부 API collector가 실패하면 전체 요청을 실패시키지 않고 `failed_collectors`와 `collector_errors`에 기록합니다.
- 현재 MVP에서 공식 API 또는 정책 제약으로 제한되는 항목은 [limitations.md](limitations.md)에 정리합니다.

## Gemini 입력 제한

Gemini 2.5 Flash를 report summary에 사용할 때는 token 사용량을 줄이기 위해 다음 데이터만 전달합니다.

```json
{
  "input": {
    "idea": "",
    "target_customer": "",
    "region": "",
    "service_type": ""
  },
  "generated_queries": {},
  "sources": [
    {
      "source_id": "",
      "source_type": "",
      "category": "",
      "title": "",
      "snippet": "",
      "relevance_score": 0
    }
  ]
}
```

전달하지 않는 데이터:

- collector raw response 전체
- 긴 HTML 본문
- 중복 source
- UI 렌더링에 필요한 부가 metadata
