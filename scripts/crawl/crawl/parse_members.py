"""Member boards (researchers, collaborators, alumni, internship): one card per person."""
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin

from .markdown import slugify
from .parse_common import PAGE_URL, clean_text, soup, wr_id_of

_THUMB_SIZE = re.compile(r'_\d+x\d+(\.[^.]+)$')


@dataclass
class Member:
    wr_id: int
    name: str
    photo_url: str | None
    fields: list[tuple[str, str]]
    category: str | None


def parse_member_list(html: str, category: str | None = None) -> list[Member]:
    """Every `div.mb_peple` card of a member list page, in page order.

    `fields` pairs each `dt` of the card's first `dl` with the `dd` after it; a `dd` without a
    `dt` gets label '' (collaborator cards leave the label empty), an empty value is dropped.
    clean_text flattens the Word-paste markup some values carry (`<dd><dd><p><span>`).
    """
    members = []
    for card in soup(html).select('div.mb_peple'):
        link = card.select_one('.mb_name h3 a[href]')
        wr_id = wr_id_of(link['href']) if link else None
        name = clean_text(link)
        if wr_id is None or not name:
            raise ValueError(f'member card without a name link to its post: {card.prettify()[:300]}')
        img = card.select_one('.mb_img img[src]')
        photo_url = urljoin(PAGE_URL, img['src'].strip()) if img else None
        fields: list[tuple[str, str]] = []
        dl = card.select_one('.cnt dl')
        label = ''
        for el in dl.find_all(['dt', 'dd'], recursive=False) if dl else []:
            if el.name == 'dt':
                label = clean_text(el)
                continue
            value = clean_text(el)
            if value:
                fields.append((label, value))
            label = ''
        members.append(Member(wr_id, name, photo_url, fields, category))
    return members


def original_photo_url(thumb_url: str) -> str:
    """`.../thumb-<file>_202x150.png` -> `.../<file>.png`; any other URL unchanged."""
    directory, _, name = thumb_url.rpartition('/')
    if not name.startswith('thumb-'):
        return thumb_url
    return f'{directory}/' + _THUMB_SIZE.sub(r'\1', name.removeprefix('thumb-'))


def member_filename(board: str, m: Member) -> str:
    return f'{slugify(m.name, 4)}-{m.wr_id}.md'
