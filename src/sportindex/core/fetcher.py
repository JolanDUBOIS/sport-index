import time
import random
from requests import Response

import cloudscraper

from . import logger
from .exceptions import RateLimitError, FetchError


class Fetcher:
    """ HTTP transport with bot-mitigation, retries, and backoff. """
    def __init__(self, **kwargs):
        self._scraper = cloudscraper.create_scraper()

    def fetch_url(self, url: str, max_retries: int = 3, retry_delay: int = 5, initial_delay: int = 5) -> Response:
        """ TODO """
        last_status = None
        time.sleep(initial_delay + random.uniform(0, 1))

        for retry in range(max_retries):
            next_delay = self._get_delay(retry_delay, retry)

            try:
                response = self._scraper.get(url)
                last_status = response.status_code

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    logger.warning(f"Rate limit (429) for {url}, attempt {retry+1}/{max_retries}. Retrying in {next_delay:.1f}s...")
                elif response.status_code == 403:
                    logger.warning(f"Access forbidden (403) for {url}, attempt {retry+1}/{max_retries}. Retrying in {next_delay:.1f}s...")
                elif response.status_code >= 500:
                    logger.warning(f"Server error (HTTP {response.status_code}) for {url}, attempt {retry+1}/{max_retries}. Retrying in {next_delay:.1f}s...")
                else:
                    logger.error(f"Failed to fetch data for {url}. Status code: {response.status_code}")
                    raise FetchError(f"HTTP {response.status_code} for URL: {url}")

            except (cloudscraper.exceptions.CloudflareChallengeError, ConnectionError) as e:
                logger.warning(f"Network error: {e}. Retrying in {next_delay:.1f}s...")
                last_status = None

            except Exception:
                logger.exception(f"Failed to fetch data from URL: {url}.")
                raise

            time.sleep(next_delay)

        if last_status == 429:
            logger.error(f"Max retries exceeded for URL: {url}.")
            raise RateLimitError(f"Max retries exceeded for URL: {url}.")
        logger.error(f"Failed to fetch URL: {url} after {max_retries} attempts.")
        raise FetchError(f"Failed to fetch URL: {url} after {max_retries} attempts.")

    @staticmethod
    def _get_delay(retry_delay: int, retry: int, max_delay: int = 30) -> float:
        """ Calculate delay with exponential backoff and jitter. """
        exp_backoff = retry_delay * (2 ** retry)
        jitter = random.uniform(0, 1)
        return min(exp_backoff + jitter, max_delay)
