"""Publication boards (papers, presentations, invited talks, patents): one table row per entry."""
from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urljoin

from bs4 import Tag

from .markdown import slugify
from .parse_common import PAGE_URL, clean_text, path_of, soup, wr_id_of


@dataclass
class Publication:
    wr_id: int
    title: str
    authors: str
    venue: str
    link_php: str | None  # the list's LINK button (`bbs/link.php?...`), resolved by the runner
    pinned: bool
    # The list's DOWNLOAD buttons: (button text, site-root `/bbs/download.php?...` path).
    files: list[tuple[str, str]] = field(default_factory=list)


def _venue(journal: Tag | None) -> str:
    """`.text_journal` as lines: each `<span class="text_vol">` is a value, a class-less `<span>`
    before it on the same line its label (`label: value`), `<br>` ends a line. Text between the
    spans (`, `) and comments are ignored. An empty line (an empty field: two `<br>` in a row, or an
    empty `text_vol`) is kept as '', except after the last non-empty line."""
    if journal is None:
        return ''
    lines: list[str] = []
    line: list[str] = []
    label = ''
    for child in journal.children:
        if not isinstance(child, Tag):
            continue
        if child.name == 'br':
            lines.append(' '.join(line))
            line, label = [], ''
        elif child.name == 'span' and 'text_vol' in child.get('class', []):
            value = clean_text(child)
            if value:
                line.append(f'{label}: {value}' if label else value)
            label = ''
        elif child.name == 'span' and not child.get('class'):
            label = clean_text(child)
    lines.append(' '.join(line))
    while lines and not lines[-1]:
        lines.pop()
    return '\n'.join(lines)


def parse_publication_rows(html: str) -> list[Publication]:
    """Every `tr.bg0` / `tr.bg1` row of the `table.tb_basic_s` tables of a list page, in page order.
    The LINK and DOWNLOAD buttons sit in the next `tr` of the row's table; `pinned` marks a `공지`
    (notice) row."""
    rows = []
    for row in soup(html).select('table.tb_basic_s tr.bg0, table.tb_basic_s tr.bg1'):
        link = row.select_one('.text_title a[href]')
        wr_id = wr_id_of(link['href']) if link else None
        title = clean_text(link)
        if wr_id is None or not title:
            raise ValueError(f'publication row without a title link to its post: {row.prettify()[:300]}')
        following = row.find_next_sibling('tr')
        button = following.select_one('td.btn_positon a[href*="link.php"]') if following else None
        downloads = following.select('td.btn_positon a[href*="download.php"]') if following else []
        rows.append(Publication(
            wr_id=wr_id,
            title=title,
            authors=clean_text(row.select_one('.text_author')),
            venue=_venue(row.select_one('.text_journal')),
            link_php=urljoin(PAGE_URL, button['href'].strip()) if button else None,
            pinned='공지' in clean_text(row.select_one('td.num')),
            files=[(clean_text(a), path_of(a['href'])) for a in downloads],
        ))
    return rows


def parse_publication_detail_year(html: str) -> int | None:
    """The `Year of publication` value of a detail page, None if missing or not a number."""
    for th in soup(html).find_all('th'):
        if clean_text(th) == 'Year of publication':
            text = clean_text(th.find_next_sibling('td'))
            return int(text) if text.isdigit() else None
    return None


def parse_detail_files(html: str) -> list[tuple[str, str]]:
    """(file name, site-root download path) of every attachment of a detail page."""
    return [(clean_text(a.select_one('strong')), path_of(a['href']))
            for a in soup(html).select('#bo_v_file a.view_file_download[href]')]


def publication_filename(year: int, p: Publication) -> str:
    return f'{year}-{p.wr_id}-{slugify(p.title, 5)}.md'
