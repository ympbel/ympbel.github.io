"""Fetch the parser fixtures once from the live site (through the cache in reference/html/).

Run from scripts/crawl:  .venv/bin/python tests/make_fixtures.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crawl.config import BASE_URL, REPO_ROOT, board_url  # noqa: E402
from crawl.fetch import Fetcher  # noqa: E402

FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures'

FIXTURES = {
    'index': f'{BASE_URL}/index.php',
    'sub1_1': board_url('sub1_1'),
    'sub2_1': board_url('sub2_1'),
    'sub3_1': board_url('sub3_1'),
    'sub2_3_p1': board_url('sub2_3', page=1),
    'sub2_3_p2': board_url('sub2_3', page=2),
    'sub2_2': board_url('sub2_2'),
    'sub2_4': board_url('sub2_4'),
    'sub2_5': board_url('sub2_5'),
    'sub4_1_2025': board_url('sub4_1', sca='2025'),
    'sub4_3': board_url('sub4_3'),
    'sub4_4': board_url('sub4_4'),
    'sub6_1_p1': board_url('sub6_1', page=1),
    'sub6_1_p2': board_url('sub6_1', page=2),
    'sub6_3_p1': board_url('sub6_3', page=1),
    'sub5_1': board_url('sub5_1'),
    'view_sub6_1_92': board_url('sub6_1', wr_id=92),
    'view_sub6_3_471': board_url('sub6_3', wr_id=471),
    'view_sub5_1_1': board_url('sub5_1', wr_id=1),
    'view_sub4_3_3': board_url('sub4_3', wr_id=3),
}


def main() -> None:
    fetcher = Fetcher(REPO_ROOT / 'reference' / 'html')
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in FIXTURES.items():
        data = fetcher.get_bytes(url)
        (FIXTURES_DIR / f'{name}.html').write_bytes(data)
        print(f'{name:18} {len(data):>7}  {url}')


if __name__ == '__main__':
    main()
