"""CLI: python -m crawl [--mode full|add] [--only pages,members,...] [--out REPO] [--offline]."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import assets, parse_pages
from .config import BASE_URL, BOARDS, PAGE_SECTION, REPO_ROOT, board_url
from .fetch import Fetcher
from .markdown import write_entry
from .run_members import run_members
from .run_posts import run_posts
from .run_publications import run_publications

KINDS = ('pages', 'members', 'publications', 'posts', 'assets')
FIXTURES_DIR = Path(__file__).resolve().parents[1] / 'tests' / 'fixtures'

Summary = dict[str, int]  # collection -> files written


@dataclass
class Context:
    fetcher: Fetcher
    out: Path
    mode: str
    skipped: dict[str, int] = field(default_factory=dict)  # collection -> files left untouched


def run_pages(ctx: Context) -> Summary:
    """home.md and the 7 static pages, always rewritten (singletons); add mode re-fetches them
    so edits on the old site are picked up. Page images go to public/images/pages/<slug>/."""
    refresh = ctx.mode == 'add'
    pages_dir = ctx.out / 'src' / 'content' / 'pages' / 'ko'
    home = parse_pages.parse_home(ctx.fetcher.get(f'{BASE_URL}/index.php', refresh=refresh))
    links = [{'label': label, 'url': url} for label, url in home.links]
    write_entry(pages_dir / 'home.md', {'title': 'MPBEL', 'section': 'home', 'links': links},
                parse_pages.normalize_html(home.about_html))
    written = 1
    for spec in BOARDS:
        if spec.kind != 'page':
            continue
        url = board_url(spec.table)
        page = parse_pages.parse_static_page(ctx.fetcher.get(url, refresh=refresh))
        mapping = {}
        for image_url, local in parse_pages.local_image_paths(spec.slug, page.image_urls).items():
            try:
                assets.download(ctx.fetcher, image_url, ctx.out / 'public' / local.lstrip('/'))
            except (urllib.error.HTTPError, FileNotFoundError) as err:
                print(f'warning: {image_url} not downloaded, kept remote in {spec.slug}: {err}',
                      file=sys.stderr)
                continue
            mapping[image_url] = local
        body = parse_pages.normalize_html(parse_pages.rewrite_images(page.body_html, mapping))
        frontmatter = {'title': spec.name, 'section': PAGE_SECTION[spec.slug],
                       'images': list(mapping.values()), 'legacy_url': url}
        write_entry(pages_dir / f'{spec.slug}.md', frontmatter, body)
        written += 1
    return {'pages': written}


def run_assets(ctx: Context) -> Summary:
    """Old-site CSS into reference/css/, every design image it or the fixture pages use into
    public/images/site/."""
    css_files = assets.copy_reference_css(ctx.fetcher, ctx.out)
    html_docs = [p.read_text(encoding='utf-8') for p in sorted(FIXTURES_DIR.glob('*.html'))]
    css_docs = [(url, path.read_text(encoding='utf-8')) for url, path in css_files]
    written = skipped = 0
    for url in sorted(assets.site_asset_urls(html_docs, css_docs)):
        dest = ctx.out / 'public' / assets.local_path_for_site_asset(url).lstrip('/')
        if dest.exists():
            skipped += 1
            continue
        try:
            assets.download(ctx.fetcher, url, dest)
        except (urllib.error.HTTPError, FileNotFoundError) as err:
            # The old site 302-redirects missing files; offline mode raises for uncached ones.
            print(f'warning: {url} not downloaded: {err}', file=sys.stderr)
            continue
        written += 1
    ctx.skipped['assets'] = skipped
    return {'assets': written}


KIND_RUNNERS: dict[str, Callable[[Context], Summary]] = {
    'pages': run_pages,
    'members': run_members,
    'publications': run_publications,
    'posts': run_posts,
    'assets': run_assets,
}


def write_summary(path: Path, summary: dict[str, dict[str, int]]) -> None:
    """`summary` (collection -> {'written': n, 'skipped': m}) as JSON, collections sorted, then
    `generated_at` (ISO 8601, UTC)."""
    data: dict = {collection: summary[collection] for collection in sorted(summary)}
    data['generated_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _kinds(value: str) -> list[str]:
    kinds = [k.strip() for k in value.split(',') if k.strip()]
    unknown = sorted(set(kinds) - set(KINDS))
    if unknown or not kinds:
        raise argparse.ArgumentTypeError(f'choose from {",".join(KINDS)}; got {value!r}')
    return kinds


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog='python -m crawl', description=__doc__)
    parser.add_argument('--mode', choices=('full', 'add'), default='full',
                        help='full: overwrite everything; add: only entries that do not exist yet')
    parser.add_argument('--only', type=_kinds, default=list(KINDS),
                        help=f'comma list of {",".join(KINDS)} (default: all)')
    parser.add_argument('--out', type=Path, default=REPO_ROOT,
                        help='repository root to write into (default: this repository)')
    parser.add_argument('--offline', action='store_true',
                        help='use only reference/html/ cache, never the network')
    args = parser.parse_args(argv)

    out = args.out.resolve()
    ctx = Context(Fetcher(out / 'reference' / 'html', offline=args.offline), out, args.mode)
    written: Summary = {}
    for kind in KINDS:
        if kind in args.only:
            written.update(KIND_RUNNERS[kind](ctx))

    summary = {c: {'written': written.get(c, 0), 'skipped': ctx.skipped.get(c, 0)}
               for c in sorted(written.keys() | ctx.skipped.keys())}
    print('collection  written  skipped')
    for collection, counts in summary.items():
        print(f'{collection}  {counts["written"]}  {counts["skipped"]}')
    write_summary(out / 'reference' / 'crawl-summary.json', summary)
    return 0
