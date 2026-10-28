"""Post boards runner (news, seminars, lectures): one entry per post under
src/content/<collection>/ko/, named <date>-<wr_id>.md, from its view page."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .config import BOARDS, board_url
from .markdown import html_to_markdown, write_entry
from .parse_posts import PostRow, parse_post_list, parse_post_view, post_filename
from .run_common import known_ids, list_pages

if TYPE_CHECKING:
    from .run import Context, Summary


def run_posts(ctx: Context) -> Summary:
    """Full mode rewrites every post; add mode re-fetches the lists and fetches the view only of
    rows whose wr_id is not a legacy_id in the collection folder yet. Only the unfiltered list pages
    are read (a row's category is on the row and its view); a notice (`pinned`) is listed again on
    later pages and written once. The body images are not downloaded: their paths go to
    `legacy_images`, the attachments to `legacy_files`."""
    refresh = ctx.mode == 'add'
    summary: Summary = {}
    for spec in BOARDS:
        if spec.kind != 'posts':
            continue
        rows: dict[int, PostRow] = {}
        pinned: set[int] = set()
        for _, html in list_pages(ctx.fetcher, spec.table, refresh, tabs=None):
            for row in parse_post_list(html):
                rows.setdefault(row.wr_id, row)
                if row.pinned:
                    pinned.add(row.wr_id)
        folder = ctx.out / 'src' / 'content' / spec.collection / 'ko'
        known = known_ids(folder) if ctx.mode == 'add' else set()
        written = skipped = 0
        for wr_id, row in rows.items():
            if wr_id in known:
                skipped += 1
                continue
            url = board_url(spec.table, wr_id=wr_id)
            view = parse_post_view(ctx.fetcher.get(url))
            frontmatter: dict = {'title': view.title, 'date': view.date}
            if category := view.category or row.category:
                frontmatter['category'] = category
            frontmatter['pinned'] = wr_id in pinned
            if view.presenter is not None:
                frontmatter['presenter'] = view.presenter
            if view.event_date is not None:
                frontmatter['event_date'] = view.event_date
            frontmatter['legacy_images'] = view.image_paths
            frontmatter['legacy_files'] = [{'name': name, 'url': path} for name, path in view.files]
            frontmatter['legacy_url'] = url
            frontmatter['legacy_id'] = wr_id
            write_entry(folder / post_filename(view, wr_id), frontmatter, html_to_markdown(view.body_html))
            written += 1
        summary[spec.collection] = written
        ctx.skipped[spec.collection] = skipped
    return summary
