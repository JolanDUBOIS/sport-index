from __future__ import annotations

import hashlib
import json
import logging
import re
import urllib.parse
from pathlib import Path
from typing import Any

from curl_cffi.requests.models import Response

from .main import Fetcher

logger = logging.getLogger(__name__)

#: Marks a fixture written in the envelope format. Fixtures without it hold a bare body.
_FIXTURE_MARKER = "__sportindex_fixture__"
_FIXTURE_VERSION = 1


class RecordingFetcher(Fetcher):
    """
    A fetcher that can record API responses to disk and replay them later.
    Used for testing without hitting the real API.

    Modes:
    - "record": Always fetches from the API and overwrites existing fixtures.
    - "replay": Always loads from disk; raises FileNotFoundError if missing.
    - "auto":   Loads from disk if available; otherwise fetches and records.

    Fixtures record the status alongside the body, so a call that legitimately fails —
    a 404 for a resource the provider does not have — replays as that same failure
    instead of going back to the network on every run. Fixtures written before statuses
    were recorded hold a bare body and still replay as a 200.
    """

    def __init__(self, mode: str, cache_dir: str):
        super().__init__()
        self.mode = mode.lower()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        if self.mode not in ("record", "replay", "auto"):
            raise ValueError(f"Invalid mode '{mode}'. Must be 'record', 'replay', or 'auto'.")

    def fetch_url(
            self, url: str, *, params: dict | None = None, max_retries: int = 3,
            retry_delay: int = 5, initial_delay: float = 5.0
        ) -> Response:
        file_path = self._fixture_path(url, params)

        if self._can_replay(file_path):
            response = self._load_fixture(file_path, url)
            if response.status_code != 200:
                # A recorded failure replays as that failure. No retry or backoff: a file
                # returns the same status however many times it is read.
                raise self._error_for_status(url, response)
            return response

        if self.mode == "replay":
            raise FileNotFoundError(f"Fixture not found for URL: {url} (Filename: {file_path.name})")

        return super().fetch_url(
            url,
            params=params,
            max_retries=max_retries,
            retry_delay=retry_delay,
            initial_delay=initial_delay
        )

    def _record_response(self, url: str, params: dict | None, response: Response) -> None:
        """Persist every response the live fetcher receives, successful or not.

        Only reached in "record" mode, or in "auto" mode with no fixture on disk yet —
        the replay branch of `fetch_url` never reaches the network.
        """
        self._save_fixture(self._fixture_path(url, params), response)

    def _can_replay(self, file_path: Path) -> bool:
        """Whether this call should be served from disk rather than the network."""
        return self.mode in ("replay", "auto") and file_path.exists()

    def _fixture_path(self, url: str, params: dict | None) -> Path:
        return self.cache_dir / self._generate_filename(url, params)

    def _load_fixture(self, file_path: Path, url: str) -> Response:
        """Rebuild a response from a fixture, status included.

        Must produce the same response type `Fetcher` returns for a live call, so that
        replayed and live runs exercise one class rather than two that merely happen to
        share the attributes this codebase touches.
        """
        logger.info(f"Loading API response from fixture {file_path} for URL: {url}")
        status_code, body = self._unpack_fixture(json.loads(file_path.read_text(encoding="utf-8")))

        response = Response()
        response.status_code = status_code
        response.content = body.encode("utf-8")
        response.encoding = "utf-8"
        response.url = url
        return response

    @staticmethod
    def _unpack_fixture(raw: Any) -> tuple[int, str]:
        """Split a fixture into the status and body text to replay.

        Fixtures predating the envelope hold the response body alone. A bare body only
        ever came from a 200, since nothing else was recorded back then.
        """
        if isinstance(raw, dict) and _FIXTURE_MARKER in raw:
            if "text" in raw:
                return raw["status_code"], raw["text"]
            return raw["status_code"], json.dumps(raw["body"])
        return 200, json.dumps(raw)

    def _save_fixture(self, file_path: Path, response: Response) -> None:
        logger.info(f"Recording HTTP {response.status_code} to {file_path} for URL: {response.url}")

        fixture: dict[str, Any] = {
            _FIXTURE_MARKER: _FIXTURE_VERSION,
            "url": str(response.url),
            "status_code": response.status_code,
        }
        try:
            # Kept parsed rather than as raw text so fixtures stay readable on disk.
            fixture["body"] = response.json()
        except ValueError:
            # Not every response is JSON — a challenge page comes back as HTML.
            fixture["text"] = response.text

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(fixture, f, indent=2)

    def _generate_filename(self, url: str, params: dict | None) -> str:
        parsed_url = urllib.parse.urlparse(url)
        path_slug = parsed_url.path.strip("/").replace("/", "_")

        if path_slug.startswith("api_v1_"):
            path_slug = path_slug[7:]

        path_slug = re.sub(r'[^a-zA-Z0-9_]', '_', path_slug)[:100]

        full_url = url
        if params:
            sorted_params = sorted(params.items())
            full_url += "?" + urllib.parse.urlencode(sorted_params)

        short_hash = hashlib.md5(full_url.encode()).hexdigest()[:8]  # noqa: S324

        if not path_slug:
            path_slug = "root"

        return f"{path_slug}_{short_hash}.json"
