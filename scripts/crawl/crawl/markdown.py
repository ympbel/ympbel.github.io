"""Markdown entry writer/reader and text helpers."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import yaml
from markdownify import markdownify


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


def html_to_markdown(html: str) -> str:
    text = markdownify(html, heading_style='ATX', strip=['span', 'font'])
    return re.sub(r'\n{3,}', '\n\n', text)
