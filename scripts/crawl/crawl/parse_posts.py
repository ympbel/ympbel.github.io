"""Post boards (news, seminars, lectures): list rows and view pages."""
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

from bs4 import Tag

from .config import BASE_URL
from .parse_common import PAGE_URL, block_text, clean_text, full_title, path_of, soup, wr_id_of
from .parse_publications import parse_detail_files

# Hosts whose /data/ files the old site serves: its own and its former domain (images of 2018 posts
# are linked there; the same paths are on mpbel.yonsei.ac.kr).
SITE_HOSTS = frozenset({urlsplit(BASE_URL).hostname, 'ympbe.yonsei.ac.kr'})


@dataclass
class PostRow:
    wr_id: int
    category: str | None
    pinned: bool


@dataclass
class PostView:
    title: str
    date: str
    category: str | None
    body_html: str
    image_paths: list[str]
    files: list[tuple[str, str]]
    event_date: str | None
    presenter: str | None


def parse_post_list(html: str) -> list[PostRow]:
    """Rows of a list page in page order; a notice (`tr.bo_notice`) is pinned."""
    rows = []
    for tr in soup(html).select('tbody tr'):
        link = tr.select_one('.bo_tit a[href]')
        wr_id = wr_id_of(link['href']) if link else None
        if wr_id is None:
            continue
        rows.append(PostRow(wr_id, clean_text(tr.select_one('.bo_cate_link')) or None,
                            'bo_notice' in tr.get('class', [])))
    return rows


def _is_empty(p: Tag) -> bool:
    """Only whitespace, `&nbsp;` and `<br>` inside."""
    return not p.get_text().replace('\xa0', '').strip() and all(t.name == 'br' for t in p.find_all(True))


def _image_ref(url: str) -> str:
    """Site path of an absolute image URL on the old site; the URL itself on another host (posts
    copied from other sites), where the old site does not serve that path."""
    return path_of(url) if urlsplit(url).hostname in SITE_HOSTS else url


def _take_images(con: Tag) -> list[str]:
    """Remove every image from the body (with its `view_image.php` link) and the paragraphs left
    empty; return the images in body order: the original behind a `view_image.php` link (its `fn`,
    on the link's host when relative), else the `src`, as site paths (see _image_ref)."""
    paths = []
    for img in con.find_all('img'):
        parent = img.parent
        if parent.name == 'a' and 'view_image.php' in parent.get('href', ''):
            link = urljoin(PAGE_URL, parent['href'].strip())
            paths.append(_image_ref(urljoin(link, path_of(link))))
            parent.decompose()
        else:
            if img.get('src'):
                paths.append(_image_ref(urljoin(PAGE_URL, img['src'].strip())))
            img.decompose()
    for p in con.find_all('p'):
        if _is_empty(p):
            p.decompose()
    return paths


def _ymd(match: re.Match) -> str:
    year, month, day = match.groups()
    return f'{year}-{int(month):02d}-{int(day):02d}'


def parse_post_view(html: str) -> PostView:
    s = soup(html)
    title = full_title(s) or clean_text(s.select_one('.bo_v_tit'))
    posted = re.search(r'(\d{2})-(\d{2})-(\d{2})', clean_text(s.select_one('#bo_v_info .if_date')))
    if posted is None:
        raise ValueError(f'post view without a date: {title!r}')
    date = '20' + '-'.join(posted.groups())
    con = s.select_one('#bo_v_con') or soup('<div></div>').div
    image_paths = _take_images(con)
    lec_date = re.search(r'(\d{4})[./-](\d{1,2})[./-](\d{1,2})', clean_text(s.select_one('.lec_date')))
    title_date = re.match(r'^(\d{4})/(\d{2})/(\d{2})', title)
    event_date = _ymd(lec_date) if lec_date else _ymd(title_date) if title_date else None
    presenter = re.search(r'Presenter\s*:\s*(.+?)\s*$', block_text(con), re.MULTILINE | re.IGNORECASE)
    return PostView(title=title, date=date, category=clean_text(s.select_one('.bo_v_cate')) or None,
                    body_html=con.decode_contents(), image_paths=image_paths, files=parse_detail_files(html),
                    event_date=event_date, presenter=presenter.group(1) if presenter else None)


def post_filename(view: PostView, wr_id: int) -> str:
    return f'{view.date}-{wr_id}.md'
