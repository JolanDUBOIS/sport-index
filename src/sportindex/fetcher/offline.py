import hashlib
import json
import logging
import re
import urllib.parse
from pathlib import Path

from requests import Response

from .main import Fetcher

logger = logging.getLogger(__name__)


class RecordingFetcher(Fetcher):
    """
    A fetcher that can record API responses to disk and replay them later.
    Used for testing without hitting the real API.

    Modes:
    - "record": Always fetches from the API and overwrites existing fixtures.
    - "replay": Always loads from disk; raises FileNotFoundError if missing.
    - "auto":   Loads from disk if available; otherwise fetches and records.
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
        filename = self._generate_filename(url, params)
        file_path = self.cache_dir / filename

        if self.mode == "replay":
            if not file_path.exists():
                raise FileNotFoundError(f"Fixture not found for URL: {url} (Filename: {filename})")
            return self._load_fixture(file_path, url)

        if self.mode == "auto" and file_path.exists():
            return self._load_fixture(file_path, url)

        response = super().fetch_url(
            url,
            params=params,
            max_retries=max_retries,
            retry_delay=retry_delay,
            initial_delay=initial_delay
        )

        if self.mode in ("record", "auto") and response.status_code == 200:
            self._save_fixture(file_path, response)

        return response

    def _load_fixture(self, file_path: Path, url: str) -> Response:
        logger.info(f"Loading API response from fixture {file_path} for URL: {url}")
        with file_path.open("r", encoding="utf-8") as f:
            raw_json_text = f.read()

        response = Response()
        response.status_code = 200
        response._content = raw_json_text.encode("utf-8")
        response.encoding = "utf-8"
        response.url = url
        return response

    def _save_fixture(self, file_path: Path, response: Response) -> None:
        logger.info(f"Recording API response to {file_path} for URL: {response.url}")
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2)

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
