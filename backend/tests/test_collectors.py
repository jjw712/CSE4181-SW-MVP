import json
import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from app.collectors.gdelt import clear_gdelt_cache, collect_gdelt
from app.collectors.http import get_json


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.body = BytesIO(json.dumps(payload).encode("utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return self.body.read()


class HttpCollectorTest(unittest.TestCase):
    @patch("app.collectors.http.sleep")
    @patch("app.collectors.http.urllib.request.urlopen")
    def test_get_json_retries_with_exponential_backoff(self, urlopen, sleep) -> None:
        urlopen.side_effect = [
            HTTPError("https://example.com", 429, "Too Many Requests", {}, None),
            HTTPError("https://example.com", 503, "Unavailable", {}, None),
            FakeResponse({"status": "ok"}),
        ]

        result = get_json(
            "https://example.com",
            max_attempts=3,
            backoff_seconds=0.5,
        )

        self.assertEqual(result, {"status": "ok"})
        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.5, 1.0])

    @patch("app.collectors.http.sleep")
    @patch("app.collectors.http.urllib.request.urlopen")
    def test_get_json_can_retry_invalid_json_response(self, urlopen, sleep) -> None:
        invalid_json = FakeResponse({"status": "not used"})
        invalid_json.body = BytesIO(b"Please limit requests")
        urlopen.side_effect = [
            invalid_json,
            FakeResponse({"status": "ok"}),
        ]

        result = get_json(
            "https://example.com",
            max_attempts=2,
            backoff_seconds=5,
            retry_on_json_error=True,
        )

        self.assertEqual(result, {"status": "ok"})
        sleep.assert_called_once_with(5)

    @patch("app.collectors.gdelt.get_json")
    def test_gdelt_reuses_successful_response_from_cache(self, get_json_mock) -> None:
        clear_gdelt_cache()
        get_json_mock.return_value = {
            "articles": [
                {
                    "title": "Example",
                    "url": "https://example.com/article",
                }
            ]
        }

        first = collect_gdelt("inventory app", 3)
        second = collect_gdelt("inventory app", 3)

        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)
        self.assertEqual(get_json_mock.call_count, 1)

    @patch("app.collectors.gdelt.get_json")
    def test_gdelt_removes_single_character_query_terms(self, get_json_mock) -> None:
        clear_gdelt_cache()
        get_json_mock.return_value = {"articles": []}

        collect_gdelt("한국 재고 관리 앱 시장 동향", 3)

        self.assertEqual(get_json_mock.call_args.kwargs["params"]["query"], "한국 재고 관리 시장 동향")


if __name__ == "__main__":
    unittest.main()
