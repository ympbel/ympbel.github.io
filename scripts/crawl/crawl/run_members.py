"""Member boards runner: one entry per card under src/content/members/ko/<board>/, the photo
under public/images/members/<board>/<wr_id>.<ext>."""
from __future__ import annotations

import posixpath
import sys
import urllib.error
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from . import assets
from .config import BOARDS, board_url
from .fetch import Fetcher
from .markdown import read_frontmatter, write_entry
from .parse_common import categories, page_count, soup
from .parse_members import Member, member_filename, original_photo_url, parse_member_list

if TYPE_CHECKING:
    from .run import Context


def list_pages(fetcher: Fetcher, table: str, refresh: bool) -> Iterator[tuple[str | None, str]]:
    """(category, html) of every list page: each category tab (`sca=`) in tab order with its own
    page count, or the plain pages when the board has no tabs."""
    first = fetcher.get(board_url(table, page=1), refresh=refresh)
    for category in categories(soup(first)) or [None]:
        scope = {'sca': category} if category else {}
        html = fetcher.get(board_url(table, **scope, page=1), refresh=refresh) if category else first
        yield category, html
        for page in range(2, page_count(soup(html)) + 1):
            yield category, fetcher.get(board_url(table, **scope, page=page), refresh=refresh)


def _known_ids(folder: Path) -> set[int]:
    """legacy_id of every entry in a board folder (`_*.md` templates excluded)."""
    ids = (read_frontmatter(p).get('legacy_id') for p in folder.glob('*.md') if not p.name.startswith('_'))
    return {i for i in ids if i is not None}


def _photo(ctx: Context, board: str, m: Member) -> str | None:
    """Download the original photo (the thumbnail if the original is missing); site path or None."""
    if not m.photo_url:
        return None
    error = None
    for url in dict.fromkeys([original_photo_url(m.photo_url), m.photo_url]):
        local = f'/images/members/{board}/{m.wr_id}{posixpath.splitext(urlsplit(url).path)[1].lower()}'
        try:
            assets.download(ctx.fetcher, url, ctx.out / 'public' / local.lstrip('/'))
            return local
        except (urllib.error.HTTPError, FileNotFoundError) as err:
            error = err
    print(f'warning: no photo for {board} {m.wr_id} ({m.name}): {m.photo_url}: {error}', file=sys.stderr)
    return None


def run_members(ctx: Context) -> dict[str, int]:
    """Full mode rewrites every card; add mode re-fetches the lists and writes only cards whose
    wr_id is not a legacy_id in the board folder yet. `order` follows the old list (tabs in order)."""
    refresh = ctx.mode == 'add'
    written = skipped = 0
    for spec in BOARDS:
        if spec.kind != 'members':
            continue
        folder = ctx.out / 'src' / 'content' / 'members' / 'ko' / spec.board
        known = _known_ids(folder) if ctx.mode == 'add' else set()
        seen: set[int] = set()
        for category, html in list_pages(ctx.fetcher, spec.table, refresh):
            for m in parse_member_list(html, category):
                if m.wr_id in seen:
                    continue
                seen.add(m.wr_id)
                if m.wr_id in known:
                    skipped += 1
                    continue
                frontmatter: dict = {'board': spec.board}
                if m.category is not None:
                    frontmatter['category'] = m.category
                frontmatter['name'] = m.name
                if photo := _photo(ctx, spec.board, m):
                    frontmatter['photo'] = photo
                frontmatter['fields'] = [{'label': label, 'value': value} for label, value in m.fields]
                frontmatter['order'] = len(seen)
                frontmatter['legacy_url'] = board_url(spec.table, wr_id=m.wr_id)
                frontmatter['legacy_id'] = m.wr_id
                write_entry(folder / member_filename(spec.board, m), frontmatter, '')
                written += 1
    ctx.skipped['members'] = skipped
    return {'members': written}
