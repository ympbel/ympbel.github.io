"""Site constants and the board table -> content collection map."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import quote

BASE_URL = "http://mpbel.yonsei.ac.kr"

# scripts/crawl/crawl/config.py -> parents[3] is the repository root.
REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class BoardSpec:
    table: str
    kind: Literal['page', 'members', 'publication', 'posts']
    collection: str
    slug: str | None = None
    board: str | None = None
    name: str = ''  # board title shown in <title>, e.g. 'Seminar'


BOARDS: list[BoardSpec] = [
    BoardSpec('sub1_1', 'page', 'pages', slug='welcome', name='Welcome to MPBEL'),
    BoardSpec('sub1_2', 'page', 'pages', slug='contact', name='Contact us'),
    BoardSpec('sub2_1', 'page', 'pages', slug='professor', name='Professor'),
    BoardSpec('sub3_1', 'page', 'pages', slug='research-ct-reconstruction', name='Advanced CT Reconstruction'),
    BoardSpec('sub3_2', 'page', 'pages', slug='research-ai', name='Medical Artificial Intelligence'),
    BoardSpec('sub3_3', 'page', 'pages', slug='research-radiation-therapy', name='Radiation Therapy'),
    BoardSpec('sub3_4', 'page', 'pages', slug='research-particle-therapy', name='Particle Therapy'),
    BoardSpec('sub2_3', 'members', 'members', board='researchers', name='Researchers'),
    BoardSpec('sub2_2', 'members', 'members', board='collaborators', name='Collaborators'),
    BoardSpec('sub2_4', 'members', 'members', board='alumni', name='Alumni'),
    BoardSpec('sub2_5', 'members', 'members', board='internship', name='Short-term internship'),
    BoardSpec('sub4_1', 'publication', 'papers', name='Paper'),
    BoardSpec('sub4_2', 'publication', 'presentations', name='Presentation'),
    BoardSpec('sub4_3', 'publication', 'talks', name='Invited talk'),
    BoardSpec('sub4_4', 'publication', 'patents', name='Patent'),
    BoardSpec('sub6_1', 'posts', 'news', name='News'),
    BoardSpec('sub6_3', 'posts', 'seminars', name='Seminar'),
    BoardSpec('sub5_1', 'posts', 'lectures', name='Lecture'),
]

PAGE_SECTION = {
    'welcome': 'introduction',
    'contact': 'introduction',
    'professor': 'member',
    'research-ct-reconstruction': 'research',
    'research-ai': 'research',
    'research-radiation-therapy': 'research',
    'research-particle-therapy': 'research',
}


def board_url(table: str, **params) -> str:
    """Gnuboard list/view URL; extra params are appended in order, values URL-encoded."""
    query = ''.join(f'&{key}={quote(str(value), safe="")}' for key, value in params.items())
    return f"{BASE_URL}/bbs/board.php?bo_table={table}{query}"
