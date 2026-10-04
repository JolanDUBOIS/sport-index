import logging
import random
import threading
import time

from curl_cffi import requests as curl_requests
from curl_cffi.requests.exceptions import RequestException

from sportindex.exceptions import (
    ChallengeError,
    FetchError,
    ProviderError,
    ProviderNotFoundError,
    RateLimitError,
)

logger = logging.getLogger(__name__)

# The provider blocks non-browser TLS fingerprints outright, so requests must go out over a
# handshake that matches a real browser. "chrome" resolves to the newest fingerprint the
# installed curl_cffi ships, rather than pinning one: a pinned version only grows more
# conspicuous as the real browser moves on.
_IMPERSONATE = "chrome"

# The handshake is impersonated, the headers are not. A request carrying Chrome's headers
# is challenged even from a residential connection, page-load and API-call headers alike,
# while the same request without them is answered.
_BROWSER_HEADERS = False

_CHALLENGE_HELP = (
    "This is usually caused by a VPN or proxy: the provider challenges traffic from "
    "VPN and datacenter IP ranges far more readily than traffic from residential "
    "connections. Disable the VPN and retry."
)

#: How each retryable status is described in the retry log line.
_RETRY_REASONS = {
    403: "Access forbidden (403)",
    429: "Rate limit (429)",
}


class Fetcher:
    """
    Internal HTTP client with retries, backoff, and bot-mitigation.

    Impersonates a browser TLS fingerprint, and handles rate limits, server errors,
    and transient network issues. All methods are for internal use; not part of the
    public API.
    """

    def __init__(self):
        self._sessions = threading.local()
        self._lock = threading.Lock()
        self._last_request_time = 0.0

    @property
    def _scraper(self) -> curl_requests.Session:
        """The session bound to the calling thread.

        A curl_cffi session wraps a libcurl handle and cannot be shared between threads,
        and the sitemap provider fetches through a thread pool. One session per thread
        keeps those fetches parallel without handing the same handle to two of them.
        """
        session = getattr(self._sessions, "session", None)
        if session is None:
            session = curl_requests.Session(impersonate=_IMPERSONATE, default_headers=_BROWSER_HEADERS)
            self._sessions.session = session
        return session

    def fetch_url(
        self, url: str, *, params: dict | None = None, max_retries: int = 3,
        retry_delay: int = 5, initial_delay: float = 5.0
    ) -> curl_requests.Response:
        """ Fetch a URL with retries, backoff, and bot-mitigation. """
        self._throttle(initial_delay)

        last_status = None
        last_body = ""
        logger.info(f"Fetching URL: {url}")

        for retry in range(max_retries):
            next_delay = self._get_delay(retry_delay, retry)

            try:
                response = self._scraper.get(url, params=params)
                self._record_response(url, params, response)
                last_status = response.status_code
                last_body = response.text[:200]

                if last_status == 200:
                    return response

                if not self._is_retryable(response):
                    error = self._error_for_status(url, response)
                    # A 404 is an ordinary answer ("no such data"), which callers handle.
                    level = logging.DEBUG if last_status == 404 else logging.ERROR
                    logger.log(level, f"Not retrying {url}: {error}")
                    raise error

                reason = _RETRY_REASONS.get(last_status, f"Server error (HTTP {last_status})")
                logger.warning(f"{reason} for {url}, attempt {retry+1}/{max_retries}. Retrying in {next_delay:.1f}s...")

            except RequestException as e:
                logger.warning(f"Network error: {e}. Retrying in {next_delay:.1f}s...")
                last_status = None

            # Once the last attempt is spent there is nothing left to back off for.
            if retry < max_retries - 1:
                time.sleep(next_delay)

        logger.error(f"Failed to fetch URL: {url} after {max_retries} attempts (last status: {last_status}).")
        if last_status == 429:
            raise RateLimitError(f"Rate limited (429) after {max_retries} attempts for URL: {url}.")
        raise FetchError(
            f"Failed to fetch URL: {url} after {max_retries} attempts. "
            f"Last status: {last_status}. Last body: {last_body}"
        )

    def _throttle(self, initial_delay: float) -> None:
        """Space requests out across threads so bursts do not trip the provider."""
        if initial_delay <= 0:
            return

        with self._lock:
            elapsed = time.time() - self._last_request_time
            target_delay = initial_delay + random.uniform(0, 1)  # noqa: S311

            if elapsed < target_delay:
                time.sleep(target_delay - elapsed)

            self._last_request_time = time.time()

    def _record_response(self, url: str, params: dict | None, response: curl_requests.Response) -> None:
        """Hook for subclasses that persist responses. The live fetcher keeps nothing."""

    @staticmethod
    def _error_for_status(url: str, response: curl_requests.Response) -> ProviderError:
        """The error a non-200 response ends in, once no further attempt will be made.

        Shared by the live loop and by replayed fixtures, so a recorded failure surfaces as
        the same exception the live call raised when it was recorded.
        """
        status = response.status_code

        if status == 404:
            return ProviderNotFoundError(f"Resource not found (404) for URL: {url}")
        if status == 403 and Fetcher._is_challenge(response):
            return ChallengeError(f"Provider issued a bot challenge for URL: {url}. {_CHALLENGE_HELP}")
        if status == 429:
            return RateLimitError(f"Rate limited (429) for URL: {url}.")
        return FetchError(f"HTTP {status} for URL: {url}. Body: {response.text[:200]}")

    @staticmethod
    def _is_retryable(response: curl_requests.Response) -> bool:
        """Whether another attempt could plausibly clear this status."""
        status = response.status_code

        if status == 403:
            # A challenge is a hard gate, not a transient failure: retrying burns the whole
            # backoff budget and still ends in the same 403.
            return not Fetcher._is_challenge(response)
        return status == 429 or status >= 500

    @staticmethod
    def _is_challenge(response: curl_requests.Response) -> bool:
        """Whether a 403 carries the provider's bot-challenge marker rather than a plain block."""
        try:
            payload = response.json()
        except ValueError:
            return False

        error = payload.get("error") if isinstance(payload, dict) else None
        return isinstance(error, dict) and error.get("reason") == "challenge"

    @staticmethod
    def _get_delay(retry_delay: int, retry: int, max_delay: int = 30) -> float:
        """ Return retry delay with exponential backoff and small random jitter. """
        exp_backoff = retry_delay * (2 ** retry)
        jitter = random.uniform(0, 1)  # noqa: S311
        return min(exp_backoff + jitter, max_delay)
