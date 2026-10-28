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
_SITE_PREFIXES = ('/images/', '/img/')


def download(fetcher: Fetcher, url: str, dest: Path) -> Path:
    if not dest.exists():
        data = fetcher.get_bytes(url)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return dest


def _site_asset(ref: str) -> str | None:
    """Absolute URL (query dropped) if `ref` resolves under /images/ or /img/ on the old site."""
    parts = urlsplit(urljoin(BASE_URL + '/', ref.strip()))
    if f'{parts.scheme}://{parts.netloc}' != BASE_URL or not parts.path.startswith(_SITE_PREFIXES):
        return None
    return BASE_URL + parts.path


def site_asset_urls(html_docs: list[str], css_docs: list[str]) -> set[str]:
    refs = [img['src'] for html in html_docs
            for img in BeautifulSoup(html, 'html.parser').find_all('img', src=True)]
    refs += [match.group(2) for css in css_docs for match in _CSS_URL.finditer(css)]
    return {url for url in map(_site_asset, refs) if url}


def local_path_for_site_asset(url: str) -> str:
    path = urlsplit(url).path
    if path.startswith('/images/'):
        return '/images/site/' + path.removeprefix('/images/')
    if path.startswith('/img/'):
        return '/images/site/img/' + path.removeprefix('/img/')
    raise ValueError(f'not a site asset: {url}')


def copy_reference_css(fetcher: Fetcher, out_dir: Path) -> list[Path]:
    """Download the old site's CSS into `out_dir/reference/css/`; returns the local files."""
    css_dir = out_dir / 'reference' / 'css'
    return [download(fetcher, f'{BASE_URL}/{src}', css_dir / name)
            for src, name in REFERENCE_CSS.items()]
