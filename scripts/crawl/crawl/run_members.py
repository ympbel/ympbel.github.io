"""Member boards runner: one entry per card under src/content/members/ko/<board>/, the photo
under public/images/members/<board>/<wr_id>.<ext>."""
from __future__ import annotations

import posixpath
import sys
import urllib.error
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlsplit

from .config import BOARDS, board_url
from .fetch import Fetcher
from .images import shrink_image
from .markdown import read_frontmatter, write_entry
from .parse_members import Member, member_filename, original_photo_url, parse_member_list
from .run_common import list_pages, resolve_link

if TYPE_CHECKING:
    from .run import Context


def download_photo(fetcher: Fetcher, thumb_url: str, dest_stem: Path) -> Path | None:
    """Save the first image that exists of: the original behind the thumbnail, the same URL with
    the extension upper-cased (a thumbnail's extension is lower case, the original keeps the
    uploader's, e.g. `.JPG`), the thumbnail itself. Written shrunk to 800 px as `dest_stem` +
    the lower-cased extension; an existing file is kept without a request. None if all fail."""
    original = original_photo_url(thumb_url)
    stem, ext = posixpath.splitext(original)
    for url in dict.fromkeys([original, stem + ext.upper(), thumb_url]):
        dest = dest_stem.with_name(dest_stem.name + posixpath.splitext(urlsplit(url).path)[1].lower())
        if dest.exists():
            return dest
        try:
            data = fetcher.get_bytes(url)
        except (urllib.error.HTTPError, FileNotFoundError):
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(shrink_image(data))
        return dest
    return None


def _photo(ctx: Context, board: str, m: Member) -> str | None:
    """Site path of the member's photo, or None (with a warning if the card has one)."""
    if not m.photo_url:
        return None
    public = ctx.out / 'public'
    dest = download_photo(ctx.fetcher, m.photo_url, public / 'images' / 'members' / board / str(m.wr_id))
    if dest is None:
        print(f'warning: no photo for {board} {m.wr_id} ({m.name}): {m.photo_url}', file=sys.stderr)
        return None
    return '/' + dest.relative_to(public).as_posix()


def _link(ctx: Context, board: str, m: Member) -> str | None:
    """The card's LINK button: a `bbs/link.php` href resolved to its target (None, with a warning,
    if it does not redirect), any other href as is."""
    if m.link is None or not urlsplit(m.link).path.endswith('/link.php'):
        return m.link
    return resolve_link(ctx.fetcher, m.link, f'{board} {m.wr_id}')


def known_members(members_root: Path) -> set[tuple[str, int]]:
    """(old board table, legacy_id) of every entry in every board folder under `members_root`
    (`_*.md` templates excluded). The table is the `bo_table` of the entry's legacy_url, so a card
    moved by hand to another board (a graduate moved from researchers/ to alumni/) still counts for
    the board it was crawled from; an entry without one counts for its folder's board. The old
    boards number their posts separately (collaborators 13 and internship 13 are different people),
    so a bare legacy_id would match the wrong board."""
    known: set[tuple[str, int]] = set()
    for spec in BOARDS:
        if spec.kind != 'members':
            continue
        for path in (members_root / spec.board).glob('*.md'):
            if path.name.startswith('_'):
                continue
            data = read_frontmatter(path)
            if data.get('legacy_id') is None:
                continue
            table = parse_qs(urlsplit(data.get('legacy_url') or '').query).get('bo_table', [spec.table])[0]
            known.add((table, data['legacy_id']))
    return known


def run_members(ctx: Context) -> dict[str, int]:
    """Full mode rewrites every card; add mode re-fetches the lists and writes only cards that no
    member file in any board folder has crawled yet (`known_members`). `order` follows the old list
    (tabs in order)."""
    refresh = ctx.mode == 'add'
    written = skipped = 0
    members_root = ctx.out / 'src' / 'content' / 'members' / 'ko'
    known = known_members(members_root) if ctx.mode == 'add' else set()
    for spec in BOARDS:
        if spec.kind != 'members':
            continue
        folder = members_root / spec.board
        seen: set[int] = set()
        for category, html in list_pages(ctx.fetcher, spec.table, refresh):
            for m in parse_member_list(html, category):
                if m.wr_id in seen:
                    continue
                seen.add(m.wr_id)
                if (spec.table, m.wr_id) in known:
                    skipped += 1
                    continue
                frontmatter: dict = {'board': spec.board}
                if m.category is not None:
                    frontmatter['category'] = m.category
                frontmatter['name'] = m.name
                if photo := _photo(ctx, spec.board, m):
                    frontmatter['photo'] = photo
                if link := _link(ctx, spec.board, m):
                    frontmatter['link'] = link
                frontmatter['fields'] = [{'label': label, 'value': value} for label, value in m.fields]
                frontmatter['order'] = len(seen)
                frontmatter['legacy_url'] = board_url(spec.table, wr_id=m.wr_id)
                frontmatter['legacy_id'] = m.wr_id
                write_entry(folder / member_filename(spec.board, m), frontmatter, '')
                written += 1
    ctx.skipped['members'] = skipped
    return {'members': written}
