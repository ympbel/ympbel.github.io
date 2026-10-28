"""Site design assets (logo, icons, backgrounds) and the reference copy of the old CSS."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from .config import BASE_URL
from .fetch import Fetcher

# Old-site CSS path -> file name under reference/css/ (the names Task 9 uses in src/styles/legacy/).
REFERENCE_CSS = {
    'css/default.css': 'default.css',
    'css/design.css': 'design.css',
    'skin/latest/basic/style.css': 'latest-basic.css',
    'skin/board/html/style.css': 'board-html.css',
    'skin/board/Student/css/style.css': 'board-student.css',
    'skin/board/collaborators/css/style.css': 'board-collaborators.css',
    'skin/board/alumni/css/style.css': 'board-alumni.css',
    'skin/board/patent/style.css': 'board-patent.css',
    'skin/board/patent2/style.css': 'board-patent2.css',
    'skin/board/patent3/style.css': 'board-patent3.css',
    'skin/board/lecture/style.css': 'board-lecture.css',
    'skin/board/basic/style.css': 'board-basic.css',
    'skin/board/gallery/style.css': 'board-gallery.css',
}

_CSS_URL = re.compile(r'url\(\s*([\'"]?)(.*?)\1\s*\)', re.IGNORECASE)
_SKIN_IMG = re.compile(r'/skin/board/([^/]+)/img/(.+)')


def download(fetcher: Fetcher, url: str, dest: Path) -> Path:
    if not dest.exists():
        data = fetcher.get_bytes(url)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return dest


def _site_asset(base: str, ref: str) -> str | None:
    """Absolute URL (query dropped) of `ref` if it is an old-site file with a local path."""
    parts = urlsplit(urljoin(base, ref.strip()))
    url = BASE_URL + parts.path
    if f'{parts.scheme}://{parts.netloc}' != BASE_URL or local_path_for_site_asset(url) is None:
        return None
    return url


def site_asset_urls(html_docs: list[str], css_docs: list[tuple[str, str]]) -> set[str]:
    """Design images used by the pages (`<img src>`, resolved against the site root) and by
    the stylesheets (`url(...)`, resolved against each stylesheet's own URL)."""
    refs = [(BASE_URL + '/', img['src']) for html in html_docs
            for img in BeautifulSoup(html, 'html.parser').find_all('img', src=True)]
    refs += [(css_url, match.group(2)) for css_url, css in css_docs
             for match in _CSS_URL.finditer(css)]
    return {url for url in (_site_asset(base, ref) for base, ref in refs) if url}



def local_path_for_site_asset(url: str) -> str | None:
    """Path under public/ for an old-site design image, or None if it is not one."""
    path = urlsplit(url).path
    if path.startswith('/images/'):
        return '/images/site/' + path.removeprefix('/images/')
    if path.startswith('/img/'):
        return '/images/site/img/' + path.removeprefix('/img/')
    if path.startswith('/skin/latest/basic/img/'):
        return '/images/site/skin/latest-basic/' + path.removeprefix('/skin/latest/basic/img/')
    if match := _SKIN_IMG.fullmatch(path):
        return f'/images/site/skin/{match.group(1)}/{match.group(2)}'
    return None


def copy_reference_css(fetcher: Fetcher, out_dir: Path) -> list[tuple[str, Path]]:
    """Download the old site's CSS into `out_dir/reference/css/`; returns (css_url, local file)."""
    css_dir = out_dir / 'reference' / 'css'
    result = []
    for src, name in REFERENCE_CSS.items():
        url = f'{BASE_URL}/{src}'
        result.append((url, download(fetcher, url, css_dir / name)))
    return result
