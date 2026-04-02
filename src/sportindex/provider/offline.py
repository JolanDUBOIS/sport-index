import re
import json
import hashlib
import urllib.parse
from pathlib import Path
from typing import Optional
from requests import Response

from .fetcher import Fetcher


class RecordingFetcher(Fetcher):
    """
    A fetcher that can record API responses to disk and replay them later.
    Used for testing without hitting the real API.

    Modes:
    - "record": Fetches from the API and saves successful responses to disk.
    - "replay": Loads responses from disk instead of making API calls.
    """

    def __init__(self, mode: str, cache_dir: str):
        super().__init__()
        self.mode = mode.lower()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_url(
            self, url: str, *, params: dict = None, max_retries: int = 3,
            retry_delay: int = 5, initial_delay: float = 5.0
        ) -> Response:
        filename = self._generate_filename(url, params)
        file_path = self.cache_dir / filename

        if self.mode == "replay":
            if not file_path.exists():
                raise FileNotFoundError(f"Fixture not found for URL: {url} (Filename: {filename})")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            response = Response()
            response.status_code = 200
            response._content = json.dumps(data).encode("utf-8")
            response.encoding = "utf-8"
            response.url = url
            return response

        response = super().fetch_url(
            url, 
            params=params, 
            max_retries=max_retries, 
            retry_delay=retry_delay, 
            initial_delay=initial_delay
        )

        if self.mode == "record" and response.status_code == 200:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(response.json(), f, indent=2)

        return response

    def _generate_filename(self, url: str, params: Optional[dict]) -> str:
        parsed_url = urllib.parse.urlparse(url)
        path_slug = parsed_url.path.strip("/").replace("/", "_")
        
        if path_slug.startswith("api_v1_"):
            path_slug = path_slug[7:]
            
        path_slug = re.sub(r'[^a-zA-Z0-9_]', '_', path_slug)[:100]

        full_url = url
        if params:
            sorted_params = sorted(params.items())
            full_url += "?" + urllib.parse.urlencode(sorted_params)
            
        short_hash = hashlib.md5(full_url.encode()).hexdigest()[:8]
        
        if not path_slug:
            path_slug = "root"
            
        return f"{path_slug}_{short_hash}.json"
