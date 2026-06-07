import json
import unittest
from unittest.mock import patch

from app.core.config import Settings
from app.report.generator import generate_report_body
from app.schemas.report import GeneratedQueries, IdeaRequest, SourceItem
from app.services.llm import expand_queries_with_gemini, summarize_report_with_gemini
from app.services.query_generator import generate_queries
from app.services.report_service import build_report


def _settings() -> Settings:
    return Settings(
        enable_llm=True,
        llm_provider="gemini",
        gemini_api_key="test-api-key",
        gemini_model="gemini-2.5-flash",
        llm_max_input_sources=2,
        llm_max_chars_per_source=40,
        llm_max_output_tokens=800,
    )


def _gemini_response(payload: dict) -> dict:
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(payload, ensure_ascii=False),
                        }
                    ]
                }
            }
        ]
    }


def _report_payload() -> dict:
    return {
        "idea_summary": {"summary": "냉장고 재고 관리 앱 아이디어입니다.", "evidence": [], "unverified": []},
        "target_users": {"summary": "대학생 자취생이 주요 타깃입니다.", "evidence": [], "unverified": []},
        "related_keywords": {
            "summary": "관련 키워드 후보입니다.",
            "keywords": ["냉장고 재고", "식재료 관리"],
            "evidence": [],
            "unverified": [],
        },
        "search_demand": {
            "summary": "검색/시장 신호는 제한적으로 확인되었습니다.",
            "evidence": [],
            "unverified": ["Naver DataLab 보강이 필요합니다."],
        },
        "competitors": {
            "items": [],
            "evidence": ["apple_itunes_1", "made_up_source"],
            "unverified": [],
        },
        "review_pain_points": {
            "summary": "리뷰 기반 불만 데이터는 아직 없습니다.",
            "evidence": ["unknown_source"],
            "unverified": ["리뷰나 인터뷰 데이터가 필요합니다."],
        },
        "monetization": {
            "summary": "경쟁 앱 metadata에서 무료 가격 단서가 확인됩니다.",
            "evidence": ["apple_itunes_1"],
            "unverified": ["구독 여부는 추가 확인이 필요합니다."],
        },
        "mvp_scope": {
            "summary": "작은 MVP로 검증합니다.",
            "apis": ["GitHub API"],
            "mvp_features": ["아이디어 입력", "검색어 생성", "리포트 출력"],
            "technical_constraints": ["외부 API 연동과 데이터 정규화가 필요합니다."],
            "evidence": ["github_1"],
            "unverified": [],
        },
        "risks": {"summary": "리뷰 데이터 부족이 리스크입니다.", "evidence": ["github_1"], "unverified": []},
        "recommendation": {"summary": "작은 MVP로 먼저 검증합니다.", "evidence": [], "unverified": []},
        "data_confidence": {"summary": "source 2개 기반입니다.", "evidence": ["apple_itunes_1"], "unverified": []},
        "unknowns": ["실제 사용자 불만과 검색 수요는 추가 확인이 필요합니다."],
    }


class GeminiLlmTest(unittest.TestCase):
    @patch("app.services.llm.post_json")
    def test_expand_queries_with_gemini_merges_with_rule_queries(self, post_json_mock) -> None:
        post_json_mock.return_value = _gemini_response(
            {
                "generated_queries": {
                    "market": ["냉장고 재고 관리 시장"],
                    "competitors": ["냉장고 재고 앱"],
                }
            }
        )
        payload = IdeaRequest(
            idea="자취생 냉장고 재고 관리 앱",
            target_customer="대학생 자취생",
        )
        base_queries = generate_queries(payload)

        queries, used, error = expand_queries_with_gemini(payload, base_queries, _settings())

        self.assertTrue(used)
        self.assertIsNone(error)
        self.assertIn(base_queries.market[0], queries.market)
        self.assertIn("냉장고 재고 관리 시장", queries.market)
        self.assertIn("냉장고 재고 앱", queries.competitors)

        request_payload = post_json_mock.call_args.args[1]
        self.assertEqual(
            request_payload["generationConfig"]["thinkingConfig"]["thinkingBudget"],
            0,
        )
        self.assertEqual(post_json_mock.call_args.kwargs["headers"]["x-goog-api-key"], "test-api-key")

    @patch("app.services.llm.post_json")
    def test_summarize_report_with_gemini_keeps_fallback_competitor_items(self, post_json_mock) -> None:
        post_json_mock.return_value = _gemini_response(_report_payload())
        payload = IdeaRequest(
            idea="자취생 냉장고 재고 관리 앱",
            target_customer="대학생 자취생",
        )
        queries = generate_queries(payload)
        sources = [
            SourceItem(
                source_id="apple_itunes_1",
                source_type="apple_itunes",
                category="competitors",
                title="Fridge Inventory",
                url="https://apps.apple.com/example",
                snippet="Utilities / Free / 4.4 rating",
                raw={
                    "app_name": "Fridge Inventory",
                    "category": "Utilities",
                    "rating": 4.4,
                    "review_count": 120,
                    "price": "Free",
                },
            ),
            SourceItem(
                source_id="github_1",
                source_type="github",
                category="implementation",
                title="inventory api repository",
                url="https://github.com/example/inventory",
                snippet="Open source inventory API example",
            ),
        ]
        fallback_report = generate_report_body(payload, queries, sources)

        report, used, error = summarize_report_with_gemini(
            payload,
            queries,
            sources,
            fallback_report,
            _settings(),
        )

        self.assertTrue(used)
        self.assertIsNone(error)
        self.assertEqual(len(report.competitors.items), 1)
        self.assertEqual(report.competitors.items[0].source_id, "apple_itunes_1")
        self.assertEqual(report.competitors.evidence, ["apple_itunes_1"])
        self.assertEqual(report.review_pain_points.evidence, [])

        text_payload = post_json_mock.call_args.args[1]["contents"][0]["parts"][0]["text"]
        self.assertNotIn("raw", text_payload)
        self.assertNotIn("https://apps.apple.com/example", text_payload)

    @patch("app.services.report_service.summarize_report_with_gemini")
    @patch("app.services.report_service.expand_queries_with_gemini")
    @patch("app.services.report_service._run_collectors_parallel")
    def test_build_report_marks_gemini_meta(
        self,
        run_collectors_mock,
        expand_queries_mock,
        summarize_mock,
    ) -> None:
        run_collectors_mock.return_value = ([], {})
        expand_queries_mock.side_effect = lambda _payload, queries, _settings: (queries, True, None)
        summarize_mock.side_effect = (
            lambda _payload, _queries, _sources, fallback_report, _settings: (
                fallback_report,
                False,
                "invalid json",
            )
        )
        payload = IdeaRequest(
            idea="자취생 냉장고 재고 관리 앱",
            target_customer="대학생 자취생",
        )

        response = build_report(payload, _settings())

        self.assertTrue(response.meta.llm_used)
        self.assertEqual(response.meta.llm_provider, "gemini")
        self.assertEqual(response.meta.llm_model, "gemini-2.5-flash")
        self.assertIn("summary: invalid json", response.meta.llm_error or "")
        self.assertNotIn("llm", response.meta.skipped_collectors)


if __name__ == "__main__":
    unittest.main()
