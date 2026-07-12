import logging
import random
import threading
import time

import cloudscraper
from requests import ConnectionError, RequestException, Response

from sportindex.exceptions import FetchError, ProviderNotFoundError, RateLimitError

logger = logging.getLogger(__name__)


class Fetcher:
    """
    Internal HTTP client with retries, backoff, and bot-mitigation.

    Uses cloudscraper to handle requests, rate limits, server errors, and transient network issues.
    All methods are for internal use; not part of the public API.
    """

    def __init__(self):
        self._scraper = cloudscraper.create_scraper()
        self._lock = threading.Lock()
        self._last_request_time = 0.0

    def fetch_url(
        self, url: str, *, params: dict | None = None, max_retries: int = 3,
        retry_delay: int = 5, initial_delay: float = 5.0
    ) -> Response:
        """ Fetch a URL with retries, backoff, and bot-mitigation. """
        if initial_delay > 0:
            with self._lock:
                now = time.time()
                elapsed = now - self._last_request_time
                target_delay = initial_delay + random.uniform(0, 1)  # noqa: S311

                if elapsed < target_delay:
                    time.sleep(target_delay - elapsed)

                self._last_request_time = time.time()

        last_status = None
        logger.info(f"Fetching URL: {url}")

        for retry in range(max_retries):
            next_delay = self._get_delay(retry_delay, retry)

            try:
                response = self._scraper.get(url, params=params)
                last_status = response.status_code

                if response.status_code == 200:
                    return response
                if response.status_code == 429:
                    logger.warning(f"Rate limit (429) for {url}, attempt {retry+1}/{max_retries}. Retrying in {next_delay:.1f}s...")
                elif response.status_code == 403:
                    logger.warning(f"Access forbidden (403) for {url}, attempt {retry+1}/{max_retries}. Retrying in {next_delay:.1f}s...")
                elif response.status_code >= 500:
                    logger.warning(f"Server error (HTTP {response.status_code}) for {url}, attempt {retry+1}/{max_retries}. Retrying in {next_delay:.1f}s...")
                elif response.status_code == 404:
                    logger.warning(f"Resource not found (404) for {url}. Not retrying.")
                    raise ProviderNotFoundError(f"Resource not found (404) for URL: {url}")
                else:
                    logger.error(f"Failed to fetch data for {url}. Status code: {response.status_code}")
                    raise FetchError(f"HTTP {response.status_code} for URL: {url}")

            except (cloudscraper.exceptions.CloudflareChallengeError, ConnectionError, RequestException) as e:
                logger.warning(f"Network error: {e}. Retrying in {next_delay:.1f}s...")
                last_status = None

            time.sleep(next_delay)

        if last_status == 429:
            logger.error(f"Max retries exceeded for URL: {url}.")
            raise RateLimitError(f"Max retries exceeded for URL: {url}.")
        logger.error(f"Failed to fetch URL: {url} after {max_retries} attempts.")
        raise FetchError(f"Failed to fetch URL: {url} after {max_retries} attempts.")

    @staticmethod
    def _get_delay(retry_delay: int, retry: int, max_delay: int = 30) -> float:
        """ Return retry delay with exponential backoff and small random jitter. """
        exp_backoff = retry_delay * (2 ** retry)
        jitter = random.uniform(0, 1)  # noqa: S311
        return min(exp_backoff + jitter, max_delay)
