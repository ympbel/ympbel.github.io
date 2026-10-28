"""HTTP fetcher with an on-disk cache (the cache doubles as the archive of the old site)."""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlsplit

TIMEOUT = 30
RETRY_DELAYS = (1, 2, 4)  # seconds to wait before retry 1, 2 and 3
REDIRECT_CODES = (301, 302, 303, 307, 308)

_UNSAFE = re.compile(r'[^A-Za-z0-9._=&%-]')
_HAS_EXTENSION = re.compile(r'\.[A-Za-z0-9]+$')


def cache_name(url: str) -> str:
    """Flat cache file name for a URL.

    `bbs/board.php?bo_table=sub6_3&page=2` -> `bbs_board.php_bo_table=sub6_3&page=2.html`.
    Pages (a query string, a `.php` script or no extension) get `.html` appended;
    static files such as `images/logo.png` keep their own extension.
    """
    parts = urlsplit(url)
    path = parts.path.lstrip('/') or 'index'
    name = path + (f'?{parts.query}' if parts.query else '')
    name = _UNSAFE.sub('_', name)
    if parts.query or path.endswith('.php') or not _HAS_EXTENSION.search(path):
        name += '.html'
    return name


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Turns a 3xx response into an HTTPError instead of following it.

    The old site answers a missing file with 302 -> an off-site 404 page, so following
    redirects would cache that page as if it were the file.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Fetcher:
    def __init__(self, cache_dir: Path, delay: float = 0.5, offline: bool = False,
                 user_agent: str = 'mpbel-migration-crawler/1.0'):
        self.cache_dir = Path(cache_dir)
        self.delay = delay
        self.offline = offline
        self.user_agent = user_agent
        self._opener = urllib.request.build_opener(_NoRedirect)

    def get(self, url: str) -> str:
        return self.get_bytes(url).decode('utf-8', errors='replace')

    def get_bytes(self, url: str) -> bytes:
        """Cached body of `url`; a 3xx/4xx answer raises HTTPError and is not cached."""
        path = self.cache_dir / cache_name(url)
        if path.exists():
            return path.read_bytes()
        if self.offline:
            raise FileNotFoundError(f'not cached (offline): {url}')
        data = self._request(url)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return data

    def resolve_redirect(self, url: str) -> str | None:
        """Absolute `Location` of a single non-followed request, or None if it did not redirect."""
        store = self.cache_dir / 'redirects.json'
        known = json.loads(store.read_text(encoding='utf-8')) if store.exists() else {}
        if url in known:
            return known[url]
        if self.offline:
            raise FileNotFoundError(f'redirect not cached (offline): {url}')
        try:
            self._request(url)
            location = None
        except urllib.error.HTTPError as err:
            if err.code not in REDIRECT_CODES:
                raise
            header = err.headers.get('Location')
            location = urljoin(url, header) if header else None
        known[url] = location
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        store.write_text(json.dumps(known, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                         encoding='utf-8')
        return location

    def _request(self, url: str) -> bytes:
        """GET `url` politely: sleep before every request, retry network errors and 5xx."""
        request = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
        for backoff in (*RETRY_DELAYS, None):
            time.sleep(self.delay)
            try:
                with self._opener.open(request, timeout=TIMEOUT) as response:
                    return response.read()
            except urllib.error.HTTPError as err:
                err.close()
                if err.code < 500 or backoff is None:
                    raise
            except (urllib.error.URLError, TimeoutError):
                if backoff is None:
                    raise
            time.sleep(backoff)
        raise AssertionError('unreachable')
