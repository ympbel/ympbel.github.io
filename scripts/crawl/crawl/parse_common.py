"""Helpers shared by the board parsers."""
from __future__ import annotations

import re
from urllib.parse import parse_qs, urljoin, urlsplit

from bs4 import BeautifulSoup, NavigableString, Tag
from bs4.element import PreformattedString

from .config import BASE_URL

# Every board page is served from /bbs/board.php, so relative links resolve against it
# (`../images/x` -> `/images/x`, `./board.php?...` -> `/bbs/board.php?...`).
PAGE_URL = BASE_URL + '/bbs/board.php'


def soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')


def page_count(s: BeautifulSoup) -> int:
    """Highest `page=` among the pagination links, 1 if the board has a single page."""
    pages = [int(value) for a in s.select('.pg_wrap a.pg_page[href]')
             for value in parse_qs(urlsplit(a['href']).query).get('page', []) if value.isdigit()]
    return max(pages, default=1)


def categories(s: BeautifulSoup) -> list[str]:
    """Category tab names in page order: `ul#bo_cate_ul` on post and publication boards,
    `ul.class_area` on member boards; empty if the board has no category nav."""
    return [a.get_text(strip=True) for a in s.select('nav#bo_cate a')]


def wr_id_of(href: str) -> int | None:
    values = parse_qs(urlsplit(href).query).get('wr_id', [])
    return int(values[0]) if values and values[0].isdigit() else None


def path_of(url: str) -> str:
    """Site-root path (with query) of an old-site URL; a `view_image.php?fn=...` link gives
    the decoded `fn` (the original image behind a thumbnail), or `/data/file/<bo_table>/<fn>`
    when `fn` is a bare file name (an attachment, `view_image.php?bo_table=...&fn=...`)."""
    parts = urlsplit(urljoin(PAGE_URL, url.strip()))
    if parts.path.endswith('/view_image.php'):
        query = parse_qs(parts.query)
        fn = query.get('fn')
        if fn:
            if '/' not in fn[0] and query.get('bo_table'):
                return f"/data/file/{query['bo_table'][0]}/{fn[0]}"
            return fn[0]
    return parts.path + (f'?{parts.query}' if parts.query else '')


_THUMBNAIL = re.compile(r'thumb-(.+)_\d+x\d+(\.[^./]+)')


def original_image_path(path: str) -> str:
    """`.../thumb-<file>_<w>x<h>.<ext>` -> `.../<file>.<ext>`: the original behind a Gnuboard
    thumbnail (a path or a URL); anything else unchanged."""
    directory, slash, name = path.rpartition('/')
    match = _THUMBNAIL.fullmatch(name)
    return f'{directory}{slash}{match[1]}{match[2]}' if match else path


def clean_text(el: Tag | None) -> str:
    """Visible text of `el` on one line ('' for a missing element)."""
    if el is None:
        return ''
    return re.sub(r'\s+', ' ', el.get_text(' ', strip=True).replace('\xa0', ' ')).strip()


BLOCK_TAGS = frozenset({'p', 'div', 'li', 'dd', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'})


def block_text(el: Tag | None) -> str:
    """Visible text of `el`, one line per block (`p`, `div`, `li`, `dd`, `tr`, `h1`-`h6`) and per
    `<br>`; each line collapsed like clean_text, empty lines dropped ('' for a missing element)."""
    if el is None:
        return ''
    lines: list[list[str]] = [[]]

    def walk(node: Tag) -> None:
        for child in node.children:
            if isinstance(child, PreformattedString):  # comments, CDATA, doctype
                continue
            if isinstance(child, NavigableString):
                lines[-1].append(child)
            elif child.name == 'br':
                lines.append([])
            elif child.name in BLOCK_TAGS:
                lines.append([])
                walk(child)
                lines.append([])
            else:
                walk(child)

    walk(el)
    joined = (' '.join(part.strip() for part in parts if part.strip()) for parts in lines)
    cleaned = (re.sub(r'\s+', ' ', line.replace('\xa0', ' ')).strip() for line in joined)
    return '\n'.join(line for line in cleaned if line)


def full_title(s: BeautifulSoup) -> str:
    """`<title>` without the ` > <board> | MPBEL | ...` suffix (or just ` | MPBEL | ...`)."""
    title = s.title.get_text() if s.title else ''
    stripped, count = re.subn(r'\s*>\s*[^>|]+\s*\|\s*MPBEL.*$', '', title)
    if not count:
        stripped = re.sub(r'\s*\|\s*MPBEL.*$', '', title)
    return stripped.strip()
