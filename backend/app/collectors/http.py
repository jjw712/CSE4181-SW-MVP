import json
import urllib.parse
import urllib.request
from time import sleep
from typing import Any
from urllib.error import HTTPError, URLError


DEFAULT_TIMEOUT_SECONDS = 5
DEFAULT_RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})


def get_json(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    max_attempts: int = 1,
    backoff_seconds: float = 0,
    retry_statuses: frozenset[int] = DEFAULT_RETRY_STATUSES,
    retry_on_url_error: bool = False,
    retry_on_json_error: bool = False,
) -> dict[str, Any]:
    target = _with_params(url, params or {})
    request = urllib.request.Request(
        target,
        headers={
            "Accept": "application/json",
            "User-Agent": "CSE4181-SW-MVP/0.1",
            **(headers or {}),
        },
    )

    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code not in retry_statuses or attempt == max_attempts - 1:
                raise
        except URLError:
            if not retry_on_url_error or attempt == max_attempts - 1:
                raise
        except json.JSONDecodeError:
            if not retry_on_json_error or attempt == max_attempts - 1:
                raise

        sleep(backoff_seconds * (2**attempt))

    raise RuntimeError("HTTP request retry loop exited unexpectedly")


def post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "CSE4181-SW-MVP/0.1",
            **(headers or {}),
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _with_params(url: str, params: dict[str, Any]) -> str:
    if not params:
        return url

    query = urllib.parse.urlencode(params, doseq=True)
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{query}"
