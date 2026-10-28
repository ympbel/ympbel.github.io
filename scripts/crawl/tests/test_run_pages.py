import urllib.error
from pathlib import Path

import pytest

from crawl.config import BASE_URL, board_url
from crawl.markdown import read_frontmatter
from crawl.run import Context, run_pages

FIXTURES = Path(__file__).resolve().parent / 'fixtures'
PLAIN_PAGE = '<div class="contents"><table class="board_list"><tr><td><p>x</p></td></tr></table></div>'
MISSING_IMAGE = BASE_URL + '/images/sub/welcomeVis.png'  # answered like the old site's 302 to its 404 page


class FakeFetcher:
    def __init__(self):
        self.pages = {BASE_URL + '/index.php': 'index', board_url('sub1_1'): 'sub1_1',
                      board_url('sub3_1'): 'sub3_1'}
        self.refresh_flags = []

    def get(self, url, refresh=False):
        self.refresh_flags.append(refresh)
        name = self.pages.get(url)
        return (FIXTURES / f'{name}.html').read_text(encoding='utf-8') if name else PLAIN_PAGE

    def get_bytes(self, url, refresh=False):
        if url == MISSING_IMAGE:
            raise urllib.error.HTTPError(url, 302, 'Found', {}, None)
        return b'image'


@pytest.mark.parametrize('mode', ['full', 'add'])
def test_run_pages_writes_all_and_refreshes_only_in_add_mode(tmp_path, capsys, mode):
    fetcher = FakeFetcher()
    assert run_pages(Context(fetcher, tmp_path, mode)) == {'pages': 8}
    assert fetcher.refresh_flags == [mode == 'add'] * 8

    pages = tmp_path / 'src' / 'content' / 'pages' / 'ko'
    assert sorted(p.stem for p in pages.glob('*.md')) == [
        'contact', 'home', 'professor', 'research-ai', 'research-ct-reconstruction',
        'research-particle-therapy', 'research-radiation-therapy', 'welcome']
    home = read_frontmatter(pages / 'home.md')
    assert (home['title'], home['section'], len(home['links'])) == ('MPBEL', 'home', 4)

    ct = read_frontmatter(pages / 'research-ct-reconstruction.md')
    assert ct['title'] == 'Advanced CT Reconstruction' and ct['section'] == 'research'
    assert ct['legacy_url'] == board_url('sub3_1')
    assert ct['images'][0] == '/images/pages/research-ct-reconstruction/r1.png'
    assert (tmp_path / 'public' / 'images' / 'pages' / 'research-ct-reconstruction' / 'r1.png').read_bytes() == b'image'
    assert 'src="/images/pages/research-ct-reconstruction/r1.png"' in (pages / 'research-ct-reconstruction.md').read_text(encoding='utf-8')

    # A failed download keeps the original absolute URL and warns.
    assert read_frontmatter(pages / 'welcome.md')['images'] == []
    assert f'src="{MISSING_IMAGE}"' in (pages / 'welcome.md').read_text(encoding='utf-8')
    assert f'warning: {MISSING_IMAGE}' in capsys.readouterr().err
