"""Helpers shared by the board runners."""
from __future__ import annotations

import sys
import urllib.error
from collections.abc import Callable, Iterator
from pathlib import Path

from .config import board_url
from .fetch import Fetcher
from .markdown import read_frontmatter
from .parse_common import categories, page_count, soup


def _every_tab(category: str) -> bool:
    return True


def list_pages(fetcher: Fetcher, table: str, refresh: bool,
               tabs: Callable[[str], bool] | None = _every_tab) -> Iterator[tuple[str | None, str]]:
    """(category, html) of every list page: each category tab (`sca=`) that `tabs` accepts, in tab
    order with its own page count, then the unfiltered pages (category None). On a board with tabs
    the unfiltered pages only add the posts whose category is in no tab. `tabs=None` reads only the
    unfiltered pages. The unfiltered first page is fetched once, before the tabs."""
    def get(**params) -> str:
        return fetcher.get(board_url(table, **params), refresh=refresh)

    first = get(page=1)
    if tabs is not None:
        for category in categories(soup(first)):
            if not tabs(category):
                continue
            html = get(sca=category, page=1)
            yield category, html
            for page in range(2, page_count(soup(html)) + 1):
                yield category, get(sca=category, page=page)
    yield None, first
    for page in range(2, page_count(soup(first)) + 1):
        yield None, get(page=page)


def resolve_link(fetcher: Fetcher, link_php: str | None, what: str) -> str | None:
    """Target of a LINK button (`bbs/link.php?...`, not followed: Fetcher.resolve_redirect), or None,
    with a warning naming `what`, if the request fails or does not redirect."""
    if link_php is None:
        return None
    try:
        location = fetcher.resolve_redirect(link_php)
    except urllib.error.HTTPError as err:
        print(f'warning: no link for {what} ({link_php}): {err}', file=sys.stderr)
        return None
    if location is None:
        print(f'warning: no link for {what} ({link_php}): no redirect', file=sys.stderr)
    return location


def known_ids(folder: Path) -> set[int]:
    """legacy_id of every entry in a content folder (`_*.md` templates excluded)."""
    ids = (read_frontmatter(p).get('legacy_id') for p in folder.glob('*.md') if not p.name.startswith('_'))
    return {i for i in ids if i is not None}
