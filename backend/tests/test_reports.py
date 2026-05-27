import unittest

from fastapi.testclient import TestClient

from app.main import app


class ReportApiTest(unittest.TestCase):
    def test_create_report_without_live_collectors(self) -> None:
        client = TestClient(app)

        response = client.post(
            "/api/reports",
            json={
                "idea": "자취생 냉장고 재고 관리 앱",
                "target_customer": "대학생 자취생",
                "region": "한국",
                "service_type": "모바일 앱",
                "use_live_collectors": False,
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["input"]["idea"], "자취생 냉장고 재고 관리 앱")
        self.assertEqual(data["meta"]["llm_used"], False)
        self.assertIn("live_collectors_disabled", data["meta"]["skipped_collectors"])
        self.assertIn("customer_problem", data["generated_queries"])


if __name__ == "__main__":
    unittest.main()
