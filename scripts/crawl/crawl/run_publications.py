"""Publication boards runner: one entry per list row under src/content/<collection>/ko/, named
<year>-<wr_id>-<slug>.md, with the LINK button resolved to its target."""
from __future__ import annotations

import sys
from collections.abc import Iterator
from typing import TYPE_CHECKING

from .config import BOARDS, board_url
from .fetch import Fetcher
from .markdown import write_entry
from .parse_publications import (Publication, parse_detail_files, parse_publication_detail_year,
                                 parse_publication_rows, publication_filename)
from .run_common import known_ids, list_pages, resolve_link

if TYPE_CHECKING:
    from .run import Context


def year_pages(fetcher: Fetcher, table: str, refresh: bool) -> Iterator[tuple[int | None, str]]:
    """list_pages with the tab as a year: the unfiltered pages (year None) only add the posts filed
    under a year that has no tab (presentations of 2002-2004 on the old site). A tab that is not a
    year is skipped with a warning."""
    def is_year(category: str) -> bool:
        if not category.isdigit():
            print(f'warning: {table} category {category!r} is not a year, skipped', file=sys.stderr)
        return category.isdigit()

    for category, html in list_pages(fetcher, table, refresh, tabs=is_year):
        yield (None if category is None else int(category)), html


def run_publications(ctx: Context) -> dict[str, int]:
    """Full mode rewrites every entry; add mode re-fetches the lists and writes only rows whose
    wr_id is not a legacy_id in the collection folder yet. All list pages of a board are read first:
    a notice (`pinned`) is marked `공지` only on the unfiltered list, its year tab lists it as a plain
    row. `year` is the tab's, except for a pinned row and a row in no tab: those take it and their
    attachments from their detail page (a pinned row falls back to the tab's year, a row in no tab
    without one is skipped with a warning)."""
    refresh = ctx.mode == 'add'
    summary: dict[str, int] = {}
    for spec in BOARDS:
        if spec.kind != 'publication':
            continue
        rows: dict[int, tuple[Publication, int | None]] = {}  # wr_id -> (first listing, its tab's year)
        pinned: set[int] = set()
        for tab_year, html in year_pages(ctx.fetcher, spec.table, refresh):
            for p in parse_publication_rows(html):
                rows.setdefault(p.wr_id, (p, tab_year))
                if p.pinned:
                    pinned.add(p.wr_id)
        folder = ctx.out / 'src' / 'content' / spec.collection / 'ko'
        known = known_ids(folder) if ctx.mode == 'add' else set()
        written = skipped = 0
        for wr_id, (p, tab_year) in rows.items():
            if wr_id in known:
                skipped += 1
                continue
            year, files = tab_year, []
            if wr_id in pinned or tab_year is None:
                detail = ctx.fetcher.get(board_url(spec.table, wr_id=wr_id))
                year = parse_publication_detail_year(detail) or tab_year
                files = parse_detail_files(detail)
            if year is None:
                print(f'warning: no year for {spec.collection} {wr_id} ({p.title}), skipped', file=sys.stderr)
                continue
            frontmatter: dict = {'year': year, 'title': p.title, 'authors': p.authors, 'venue': p.venue}
            if link := resolve_link(ctx.fetcher, p.link_php, f'{spec.collection} {wr_id}'):
                frontmatter['link'] = link
            frontmatter['pinned'] = wr_id in pinned
            frontmatter['order'] = wr_id
            frontmatter['legacy_files'] = [{'name': name, 'url': url} for name, url in files]
            frontmatter['legacy_url'] = board_url(spec.table, wr_id=wr_id)
            frontmatter['legacy_id'] = wr_id
            write_entry(folder / publication_filename(year, p), frontmatter, '')
            written += 1
        summary[spec.collection] = written
        ctx.skipped[spec.collection] = skipped
    return summary
