"""Fetcher tests.

Every test here drives a fake session, so nothing reaches the network. That also lets the
replay cases assert something stronger than "it worked": a fetcher built with no canned
responses raises if anything asks it for one, so a passing replay test proves the call was
served from disk.
"""

import json
import threading
import time

import pytest
from curl_cffi.requests.exceptions import RequestException
from curl_cffi.requests.models import Response

from sportindex.exceptions import (
    ChallengeError,
    FetchError,
    NetworkError,
    ProviderNotFoundError,
    RateLimitError,
)
from sportindex.fetcher import RecordingFetcher

URL = "https://api.example.test/api/v1/team/44"

CHALLENGE_BODY = '{"error": {"code": 403, "reason": "challenge"}}'


def _response(status_code: int, body: str = "{}") -> Response:
    response = Response()
    response.status_code = status_code
    response.content = body.encode("utf-8")
    response.encoding = "utf-8"
    response.url = URL
    return response


class _FakeSession:
    """Stands in for the curl_cffi session. Replays canned responses, then repeats the last.

    A `RequestException` in place of a response is raised instead, as a transport failure.
    """

    def __init__(self, *responses: Response | RequestException) -> None:
        self._responses = list(responses)
        self.calls = 0

    def get(self, url: str, params: dict | None = None) -> Response:
        self.calls += 1
        response = self._responses[min(self.calls, len(self._responses)) - 1]
        if isinstance(response, RequestException):
            raise response
        return response


@pytest.fixture
def make_fetcher(tmp_path):
    def build(mode: str, *responses: Response) -> RecordingFetcher:
        fetcher = RecordingFetcher(mode=mode, cache_dir=str(tmp_path))
        # Sessions are thread-local, so assigning here binds the fake for this thread.
        fetcher._sessions.session = _FakeSession(*responses)
        return fetcher
    return build


def _record(make_fetcher, response: Response, expected_error: type[Exception] | None = None):
    """Run one recording pass, returning the fetcher that performed it.

    A single attempt with no backoff: these tests are about what lands on disk, not about
    the retry policy, and a retryable status would otherwise sleep out the real delays.
    """
    fetcher = make_fetcher("record", response)
    call = lambda: fetcher.fetch_url(URL, max_retries=1, retry_delay=0, initial_delay=0)  # noqa: E731

    if expected_error is None:
        call()
    else:
        with pytest.raises(expected_error):
            call()
    return fetcher


# ===== Recording =====

def test_successful_response_is_recorded_with_its_status(make_fetcher, tmp_path):
    _record(make_fetcher, _response(200, '{"team": {"id": 44}}'))

    fixture = json.loads(next(iter(tmp_path.glob("*.json"))).read_text(encoding="utf-8"))
    assert fixture["status_code"] == 200
    assert fixture["body"] == {"team": {"id": 44}}


def test_404_is_recorded_rather_than_skipped(make_fetcher, tmp_path):
    """The bug in #45: a 404 produced no fixture at all, so it could never be replayed."""
    _record(make_fetcher, _response(404, '{"error": {"code": 404}}'), ProviderNotFoundError)

    fixtures = list(tmp_path.glob("*.json"))
    assert len(fixtures) == 1
    assert json.loads(fixtures[0].read_text(encoding="utf-8"))["status_code"] == 404


def test_non_json_body_is_recorded_as_text(make_fetcher, tmp_path):
    _record(make_fetcher, _response(500, "<html>Server Error</html>"), FetchError)

    fixture = json.loads(next(iter(tmp_path.glob("*.json"))).read_text(encoding="utf-8"))
    assert fixture["status_code"] == 500
    assert fixture["text"] == "<html>Server Error</html>"
    assert "body" not in fixture


# ===== Replaying =====

def test_recorded_200_replays_as_its_body(make_fetcher):
    _record(make_fetcher, _response(200, '{"team": {"id": 44}}'))

    replayer = make_fetcher("replay")
    response = replayer.fetch_url(URL, initial_delay=0)

    assert response.status_code == 200
    assert response.json() == {"team": {"id": 44}}
    assert replayer._sessions.session.calls == 0


def test_recorded_404_replays_as_the_same_error(make_fetcher):
    _record(make_fetcher, _response(404), ProviderNotFoundError)

    replayer = make_fetcher("replay")
    with pytest.raises(ProviderNotFoundError):
        replayer.fetch_url(URL, initial_delay=0)

    assert replayer._sessions.session.calls == 0


def test_auto_mode_serves_a_recorded_404_from_disk(make_fetcher):
    """The other half of #45: in `auto` a 404 used to re-hit the network on every run."""
    _record(make_fetcher, _response(404), ProviderNotFoundError)

    replayer = make_fetcher("auto")
    with pytest.raises(ProviderNotFoundError):
        replayer.fetch_url(URL, initial_delay=0)

    assert replayer._sessions.session.calls == 0


def test_recorded_429_replays_as_a_rate_limit(make_fetcher):
    fetcher = make_fetcher("record", _response(429))
    with pytest.raises(RateLimitError):
        fetcher.fetch_url(URL, max_retries=1, retry_delay=0, initial_delay=0)

    replayer = make_fetcher("replay")
    with pytest.raises(RateLimitError):
        replayer.fetch_url(URL, initial_delay=0)

    assert replayer._sessions.session.calls == 0


def test_legacy_fixture_without_a_status_replays_as_200(make_fetcher):
    """Fixtures recorded before statuses were saved hold a bare body, and still work."""
    fetcher = make_fetcher("replay")
    path = fetcher._fixture_path(URL, None)
    path.write_text(json.dumps({"team": {"id": 44}}), encoding="utf-8")

    response = fetcher.fetch_url(URL, initial_delay=0)

    assert response.status_code == 200
    assert response.json() == {"team": {"id": 44}}


def test_replay_without_a_fixture_reports_the_missing_file(make_fetcher):
    with pytest.raises(FileNotFoundError):
        make_fetcher("replay").fetch_url(URL, initial_delay=0)


# ===== Retry policy =====

def test_challenge_is_not_retried(make_fetcher):
    fetcher = make_fetcher("record", _response(403, CHALLENGE_BODY))

    with pytest.raises(ChallengeError):
        fetcher.fetch_url(URL, max_retries=3, retry_delay=0, initial_delay=0)

    assert fetcher._sessions.session.calls == 1


def test_plain_403_is_retried(make_fetcher):
    fetcher = make_fetcher("record", _response(403, "blocked"))

    with pytest.raises(FetchError):
        fetcher.fetch_url(URL, max_retries=2, retry_delay=0, initial_delay=0)

    assert fetcher._sessions.session.calls == 2


def test_retries_stop_backing_off_after_the_final_attempt(make_fetcher):
    """The loop used to sleep out the full backoff before raising, for nothing."""
    fetcher = make_fetcher("record", _response(500))

    started = time.monotonic()
    with pytest.raises(FetchError):
        fetcher.fetch_url(URL, max_retries=1, retry_delay=30, initial_delay=0)

    assert time.monotonic() - started < 1


def test_unreachable_provider_raises_a_network_error(make_fetcher):
    fetcher = make_fetcher("record", RequestException("Connection timed out"))

    with pytest.raises(NetworkError, match="Connection timed out"):
        fetcher.fetch_url(URL, max_retries=2, retry_delay=0, initial_delay=0)

    assert fetcher._sessions.session.calls == 2


def test_a_response_on_any_attempt_is_not_a_network_error(make_fetcher):
    fetcher = make_fetcher("record", _response(500), RequestException("Connection timed out"))

    with pytest.raises(FetchError) as caught:
        fetcher.fetch_url(URL, max_retries=2, retry_delay=0, initial_delay=0)

    assert not isinstance(caught.value, NetworkError)


# ===== Sessions =====

def test_each_thread_gets_its_own_session(tmp_path):
    """A curl_cffi session wraps a libcurl handle, and the sitemap provider fetches in a pool."""
    fetcher = RecordingFetcher(mode="auto", cache_dir=str(tmp_path))
    seen = []

    def collect() -> None:
        seen.append(fetcher._scraper)

    threads = [threading.Thread(target=collect) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len({id(session) for session in seen}) == len(threads)
    assert fetcher._scraper is fetcher._scraper  # stable within a thread


def test_session_impersonates_the_handshake_but_not_the_headers(tmp_path):
    """Chrome's headers draw a bot challenge even from a residential connection."""
    session = RecordingFetcher(mode="auto", cache_dir=str(tmp_path))._scraper

    assert session.impersonate == "chrome"
    assert session.default_headers is False
    assert dict(session.headers) == {}


def test_transient_error_then_success_records_the_success(make_fetcher, tmp_path):
    fetcher = make_fetcher("record", _response(500), _response(200, '{"ok": true}'))

    response = fetcher.fetch_url(URL, max_retries=2, retry_delay=0, initial_delay=0)

    assert response.json() == {"ok": True}
    fixture = json.loads(next(iter(tmp_path.glob("*.json"))).read_text(encoding="utf-8"))
    assert fixture["status_code"] == 200
