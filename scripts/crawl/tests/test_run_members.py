import urllib.error
from pathlib import Path

from crawl.config import BASE_URL, board_url
from crawl.markdown import read_frontmatter, write_entry
from crawl.run import KIND_RUNNERS, Context
from crawl.run_members import run_members

FIXTURES = Path(__file__).resolve().parent / 'fixtures'
PHOTO_19 = BASE_URL + '/data/file/sub2_3/3024172423_ULcQMJ5Y_587355d9e11d22af8292ebe5489c2d6334c027d7.png'
THUMB_99 = BASE_URL + '/data/file/sub2_3/thumb-a_202x150.JPG'
FILE_15 = '14_copy_15_9_copy_14_8_copy_9_3_copy_8_2156318548_R0Lk6eBX_27fcc8761460bd3b36a0f8bd809dc964f36838d9'
# Old-site 302s (to its 404 page): 99's original, and both images of collaborator 15.
MISSING = {BASE_URL + '/data/file/sub2_3/a.JPG', BASE_URL + f'/data/file/sub2_2/{FILE_15}.png',
           BASE_URL + f'/data/file/sub2_2/thumb-{FILE_15}_202x150.png'}


def card(table, wr_id, name, photo):
    return (f'<div class="mb_peple"><div class="mb_img"><img src="{photo}"></div><div class="cnt">'
            f'<div class="mb_name"><h3><a href="{board_url(table, wr_id=wr_id)}">{name}</a></h3></div>'
            '<dl><dt>Grade</dt><dd>Intern</dd></dl></div></div>')


# Affiliate tab: a repeat of 19 (deduped) and one new member whose original photo is missing.
AFFILIATE = (card('sub2_3', 19, '양고운 Gowoon Yang', THUMB_99)
             + card('sub2_3', 99, '홍길동 Gildong Hong', THUMB_99))
LIST_URLS = [board_url('sub2_3', page=1), board_url('sub2_3', sca='MPBEL', page=1),
             board_url('sub2_3', sca='MPBEL', page=2), board_url('sub2_3', sca='Affiliate', page=1),
             board_url('sub2_2', page=1), board_url('sub2_4', page=1), board_url('sub2_5', page=1)]


class FakeFetcher:
    def __init__(self):
        self.pages = {LIST_URLS[0]: 'sub2_3_p1', LIST_URLS[1]: 'sub2_3_p1', LIST_URLS[2]: 'sub2_3_p2',
                      LIST_URLS[4]: 'sub2_2'}
        self.requested = []  # (url, refresh) of every get()
        self.bytes_requested = []

    def get(self, url, refresh=False):
        self.requested.append((url, refresh))
        if url == LIST_URLS[3]:
            return AFFILIATE
        name = self.pages.get(url)
        return (FIXTURES / f'{name}.html').read_text(encoding='utf-8') if name else '<html></html>'

    def get_bytes(self, url, refresh=False):
        self.bytes_requested.append(url)
        if url in MISSING:
            raise urllib.error.HTTPError(url, 302, 'Found', {}, None)
        return b'thumb' if '/thumb-' in url else b'original'


def members_dir(root, board):
    return root / 'src' / 'content' / 'members' / 'ko' / board


def test_members_runner_is_registered():
    assert KIND_RUNNERS['members'] is run_members


def test_run_members_full_mode(tmp_path, capsys):
    researchers = members_dir(tmp_path, 'researchers')
    write_entry(researchers / 'gowoon-yang-19.md', {'name': 'stale', 'legacy_id': 19}, 'old body')
    fetcher = FakeFetcher()
    ctx = Context(fetcher, tmp_path, 'full')
    assert run_members(ctx) == {'members': 22 + 1 + 9}
    assert ctx.skipped == {'members': 0}
    assert fetcher.requested == [(url, False) for url in LIST_URLS]

    assert len(list(researchers.glob('*.md'))) == 23
    first = read_frontmatter(researchers / 'gowoon-yang-19.md')
    assert first == {
        'board': 'researchers', 'category': 'MPBEL', 'name': '양고운 Gowoon Yang',
        'photo': '/images/members/researchers/19.png',
        'fields': [{'label': 'Grade', 'value': 'M.D., Ph.D. Candidate'},
                   {'label': 'E-mail', 'value': 'gowoon1988@gmail.com'},
                   {'label': 'Research Interest', 'value': 'Medical Physics'}],
        'order': 1, 'legacy_url': board_url('sub2_3', wr_id=19), 'legacy_id': 19}
    assert list(first) == ['board', 'category', 'name', 'photo', 'fields', 'order', 'legacy_url', 'legacy_id']
    assert (researchers / 'gowoon-yang-19.md').read_text(encoding='utf-8').endswith('---\n\n\n')
    images = tmp_path / 'public' / 'images' / 'members'
    assert (images / 'researchers' / '19.png').read_bytes() == b'original'
    assert PHOTO_19 in fetcher.bytes_requested

    # Second tab: order continues, category known; missing original falls back to the thumbnail.
    new = read_frontmatter(researchers / 'gildong-hong-99.md')
    assert (new['category'], new['order'], new['photo']) == ('Affiliate', 23, '/images/members/researchers/99.jpg')
    assert (images / 'researchers' / '99.jpg').read_bytes() == b'thumb'
    assert read_frontmatter(researchers / 'dongyoung-jeong-66.md')['order'] == 22

    # No categories: no category key; both photos missing: no photo key and a warning.
    collaborator = read_frontmatter(members_dir(tmp_path, 'collaborators') / 'dong-wook-kim-ph-15.md')
    assert 'category' not in collaborator and 'photo' not in collaborator
    assert collaborator['fields'][0] == {'label': '', 'value': 'Clinical Professor'}
    assert collaborator['order'] == 1
    assert 'warning:' in capsys.readouterr().err
    assert len(list(members_dir(tmp_path, 'collaborators').glob('*.md'))) == 9
    assert not members_dir(tmp_path, 'alumni').exists()


def test_run_members_add_mode_skips_known_legacy_ids(tmp_path):
    researchers = members_dir(tmp_path, 'researchers')
    write_entry(researchers / 'renamed.md', {'name': 'kept', 'legacy_id': 19}, 'edited by hand')
    write_entry(researchers / '_draft.md', {'name': 'template', 'legacy_id': 23}, '')  # ignored
    before = (researchers / 'renamed.md').read_text(encoding='utf-8')
    fetcher = FakeFetcher()
    ctx = Context(fetcher, tmp_path, 'add')
    assert run_members(ctx) == {'members': 22 + 1 + 9 - 1}
    assert ctx.skipped == {'members': 1}
    assert fetcher.requested == [(url, True) for url in LIST_URLS]

    assert (researchers / 'renamed.md').read_text(encoding='utf-8') == before
    assert not (researchers / 'gowoon-yang-19.md').exists()
    assert PHOTO_19 not in fetcher.bytes_requested
    assert read_frontmatter(researchers / 'yongdo-yun-23.md')['order'] == 2
