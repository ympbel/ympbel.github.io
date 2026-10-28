"""Markdown entry writer/reader and text helpers."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import yaml
from markdownify import MarkdownConverter


class _Dumper(yaml.SafeDumper):
    """SafeDumper that writes a multi-line string as a literal block (`|-`, one line per line)
    instead of a quoted scalar where a blank line stands for a newline."""


def _represent_str(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    return dumper.represent_scalar('tag:yaml.org,2002:str', value, style='|' if '\n' in value else None)


_Dumper.add_representer(str, _represent_str)


def write_entry(path: Path, frontmatter: dict, body: str) -> None:
    # The safe dumper quotes strings that YAML would otherwise read as dates/numbers/booleans,
    # so '2025-10-22' stays a string for Astro's schema.
    text = yaml.dump(frontmatter, Dumper=_Dumper, allow_unicode=True, sort_keys=False,
                     default_flow_style=False, width=1000)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\n{text}---\n\n{body}\n', encoding='utf-8')


def read_frontmatter(path: Path) -> dict:
    lines = path.read_text(encoding='utf-8').split('\n')
    if not lines or lines[0] != '---':
        raise ValueError(f'no frontmatter: {path}')
    end = lines.index('---', 1)
    return yaml.safe_load('\n'.join(lines[1:end])) or {}


def slugify(text: str, max_words: int = 6) -> str:
    ascii_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    words = re.findall(r'[a-z0-9]+', ascii_text.lower())
    return '-'.join(words[:max_words]) or 'entry'


ZERO_WIDTH = re.compile('[\u200b\u200c\u200d\ufeff]')


def strip_zero_width(text: str) -> str:
    """`text` without zero-width spaces, joiners and BOMs (invisible, they break label matching)."""
    return ZERO_WIDTH.sub('', text)


class _Converter(MarkdownConverter):
    """markdownify with: `<` and `>` of text written as `&lt;`/`&gt;` (a literal `<Name>` would be
    read as an HTML tag and vanish; the entities render as the characters), zero-width characters
    dropped, and a bold element written as its plain text when it has no visible text or is inside
    another bold element (else `****` would show), else as one run per line."""

    def process_text(self, el, parent_tags=None):
        return strip_zero_width(super().process_text(el, parent_tags))

    def escape(self, text, parent_tags):
        return super().escape(text, parent_tags).replace('<', '&lt;').replace('>', '&gt;')

    def convert_b(self, el, text, parent_tags):
        if not strip_zero_width(text).strip() or parent_tags & {'b', 'strong'}:
            return text
        # One run per line: a run cannot span the blank line that `<br><br>` makes.
        lines = []
        for line in text.split('\n'):
            content = line.rstrip()
            lines.append(super().convert_b(el, content, parent_tags) + line[len(content):] if content.strip() else line)
        return '\n'.join(lines)

    convert_strong = convert_b


def html_to_markdown(html: str) -> str:
    text = _Converter(heading_style='ATX', strip=['span', 'font']).convert(html)
    # Two bold runs side by side (`**a****b**`) render as literal asterisks: close, space, open.
    text = re.sub(r'(?<=[^\s*])\*{4}(?=[^\s*])', '** **', text)
    return re.sub(r'\n{3,}', '\n\n', text)
