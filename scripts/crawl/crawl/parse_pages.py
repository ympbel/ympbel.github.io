"""Static pages (welcome, contact, professor, research) and the home page."""
from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import Comment
from bs4.dammit import EntitySubstitution
from bs4.formatter import HTMLFormatter

from .parse_common import PAGE_URL, clean_text, path_of, soup


@dataclass
class StaticPage:
    body_html: str
    image_urls: list[str]


@dataclass
class HomePage:
    about_html: str
    links: list[tuple[str, str]]


class _SourceFormatter(HTMLFormatter):
    """Serialize like the old site wrote it: attributes in source order (BeautifulSoup sorts
    them by default), U+00A0 back to `&nbsp;`, void elements as `<br>`."""

    def __init__(self):
        super().__init__(entity_substitution=lambda text: EntitySubstitution.substitute_xml(text)
                         .replace('\xa0', '&nbsp;'), void_element_close_prefix='')

    def attributes(self, tag):
        return list(tag.attrs.items()) if tag.attrs else []


_FORMATTER = _SourceFormatter()


def _image_url(ref: str) -> str:
    """Absolute URL of an image reference, query and fragment dropped."""
    parts = urlsplit(urljoin(PAGE_URL, ref.strip()))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))


def parse_static_page(html: str) -> StaticPage:
    """Body of an html-skin board page: the cells of `div.contents table.board_list`.

    The skin renders every post of the board as one row; the pages have one post, except
    sub3_1 whose first row is an old `<p>test</p>` post. Rows are joined in order so the body
    shows what the old page shows. Each `img[src]` is set to the absolute URL of the original
    image (a `view_image.php?fn=` thumbnail link is replaced by the image it points to).
    """
    s = soup(html)
    contents = s.select_one('div.contents')
    table = contents.select_one('table.board_list') if contents else None
    if table is None:
        raise ValueError('no div.contents table.board_list')
    for el in contents.find_all(['script', 'style']) + contents.select('input[type=hidden]'):
        el.decompose()
    # Empty selection markers the old editor (SmartEditor "husky") saved into the content. Never
    # visible; in front of the first block tag they keep markdown from seeing one HTML block.
    for span in contents.select('span[id^=husky_bookmark]'):
        if not span.contents:
            span.decompose()
    for comment in contents.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    for form in contents.select('form#fboardlist'):
        form.unwrap()

    cells = [td for td in table.find_all('td') if td.find_parent('table') is table]
    image_urls: list[str] = []
    for cell in cells:
        for img in cell.find_all('img', src=True):
            anchor = img.parent
            if not (anchor.name == 'a' and 'view_image' in anchor.get('class', [])
                    and 'fn=' in anchor.get('href', '')):
                anchor = None
            url = _image_url(path_of(anchor['href']) if anchor else img['src'])
            img['src'] = url
            if anchor:
                anchor.unwrap()
            if url not in image_urls:
                image_urls.append(url)
    body = '\n'.join(cell.decode_contents(formatter=_FORMATTER) for cell in cells)
    return StaticPage(body, image_urls)


def local_image_paths(slug: str, urls: list[str]) -> dict[str, str]:
    """Image URL -> `/images/pages/<slug>/<basename>`; a repeated basename gets `-2`, `-3`."""
    paths: dict[str, str] = {}
    used: set[str] = set()  # lower-cased: macOS file systems ignore case
    for url in urls:
        if url in paths:
            continue
        name = posixpath.basename(urlsplit(url).path)
        stem, ext = posixpath.splitext(name)
        candidate, n = name, 1
        while candidate.lower() in used:
            n += 1
            candidate = f'{stem}-{n}{ext}'
        used.add(candidate.lower())
        paths[url] = f'/images/pages/{slug}/{candidate}'
    return paths


def rewrite_images(body_html: str, mapping: dict[str, str]) -> str:
    """Replace every `img[src]` whose absolute URL is a key of `mapping` with its value."""
    s = soup(body_html)
    for img in s.find_all('img', src=True):
        local = mapping.get(_image_url(img['src']))
        if local:
            img['src'] = local
    return s.decode(formatter=_FORMATTER)


def normalize_html(html: str) -> str:
    """Strip each line's leading spaces/tabs and drop blank lines.

    In markdown a blank line ends a raw HTML block and a 4-space indent starts a code block,
    so the body must have neither to stay one HTML block.
    """
    lines = (line.lstrip(' \t') for line in re.split(r'\r\n?|\n', html))
    return '\n'.join(line for line in lines if line.strip(' \t'))


def parse_home(html: str) -> HomePage:
    s = soup(html)
    txt = s.select_one('div.about div.txt')
    if txt is None:
        raise ValueError('no div.about div.txt')
    links = [(clean_text(a), a['href']) for a in s.select('div.link ul li a[href]')]
    return HomePage(txt.decode_contents(formatter=_FORMATTER), links)
