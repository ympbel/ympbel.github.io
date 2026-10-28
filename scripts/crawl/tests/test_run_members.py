import io
import urllib.error
from pathlib import Path

from PIL import Image

from crawl.config import BASE_URL, board_url
from crawl.markdown import read_frontmatter, write_entry
from crawl.run import KIND_RUNNERS, Context
from crawl.run_members import download_photo, run_members


def png(color, size=(4, 3)):
    buffer = io.BytesIO()
    Image.new('RGB', size, color).save(buffer, 'PNG')
    return buffer.getvalue()


FIXTURES = Path(__file__).resolve().parent / 'fixtures'
ORIGINAL, THUMB = png('red'), png('blue')  # small enough to be saved unchanged
PHOTO_19 = BASE_URL + '/data/file/sub2_3/3024172423_ULcQMJ5Y_587355d9e11d22af8292ebe5489c2d6334c027d7.png'
THUMB_99 = BASE_URL + '/data/file/sub2_3/thumb-a_202x150.JPG'
FILE_15 = '14_copy_15_9_copy_14_8_copy_9_3_copy_8_2156318548_R0Lk6eBX_27fcc8761460bd3b36a0f8bd809dc964f36838d9'
# Old-site 302s (to its 404 page): 99's original, and every image of collaborator 15.
MISSING = {BASE_URL + '/data/file/sub2_3/a.JPG', BASE_URL + f'/data/file/sub2_2/{FILE_15}.png',
           BASE_URL + f'/data/file/sub2_2/{FILE_15}.PNG', BASE_URL + f'/data/file/sub2_2/thumb-{FILE_15}_202x150.png'}


def card(table, wr_id, name, photo):
    return (f'<div class="mb_peple"><div class="mb_img"><img src="{photo}"></div><div class="cnt">'
            f'<div class="mb_name"><h3><a href="{board_url(table, wr_id=wr_id)}">{name}</a></h3></div>'
            '<dl><dt>Grade</dt><dd>Intern</dd></dl></div></div>')


# Affiliate tab: a repeat of 19 (deduped) and one new member whose original photo is missing.
AFFILIATE = (card('sub2_3', 19, '양고운 Gowoon Yang', THUMB_99)
             + card('sub2_3', 99, '홍길동 Gildong Hong', THUMB_99))
# Alumni: tabs list A (201) and B (202); the unfiltered list also has C (203), in no tab.
ALUMNI_PHOTO = BASE_URL + '/data/file/sub2_4/thumb-x_202x150.jpg'
ALUMNI_TABS = ('<nav id="bo_cate"><ul class="class_area"><li><a href="#">Graduate</a></li>'
               '<li><a href="#">Former</a></li></ul></nav>')
ALUMNI_ALL = ALUMNI_TABS + ''.join(card('sub2_4', wr_id, name, ALUMNI_PHOTO)
                                   for wr_id, name in ((201, 'A'), (202, 'B'), (203, 'C')))
LIST_URLS = [board_url('sub2_3', page=1), board_url('sub2_3', sca='MPBEL', page=1),
             board_url('sub2_3', sca='MPBEL', page=2), board_url('sub2_3', sca='Affiliate', page=1),
             board_url('sub2_3', page=2),
             board_url('sub2_2', page=1),
             board_url('sub2_4', page=1), board_url('sub2_4', sca='Graduate', page=1),
             board_url('sub2_4', sca='Former', page=1),
             board_url('sub2_5', page=1)]
SYNTHETIC = {LIST_URLS[3]: AFFILIATE, LIST_URLS[6]: ALUMNI_ALL,
             LIST_URLS[7]: ALUMNI_TABS + card('sub2_4', 201, 'A', ALUMNI_PHOTO),
             LIST_URLS[8]: ALUMNI_TABS + card('sub2_4', 202, 'B', ALUMNI_PHOTO)}


class FakeFetcher:
    def __init__(self):
        self.pages = {LIST_URLS[0]: 'sub2_3_p1', LIST_URLS[1]: 'sub2_3_p1', LIST_URLS[2]: 'sub2_3_p2',
                      LIST_URLS[4]: 'sub2_3_p2', LIST_URLS[5]: 'sub2_2'}
        self.requested = []  # (url, refresh) of every get()
        self.bytes_requested = []

    def get(self, url, refresh=False):
        self.requested.append((url, refresh))
        if url in SYNTHETIC:
            return SYNTHETIC[url]
        name = self.pages.get(url)
        return (FIXTURES / f'{name}.html').read_text(encoding='utf-8') if name else '<html></html>'

    def get_bytes(self, url, refresh=False):
        self.bytes_requested.append(url)
        if url in MISSING:
            raise urllib.error.HTTPError(url, 302, 'Found', {}, None)
        return THUMB if '/thumb-' in url else ORIGINAL


def members_dir(root, board):
    return root / 'src' / 'content' / 'members' / 'ko' / board


def test_members_runner_is_registered():
    assert KIND_RUNNERS['members'] is run_members


def test_run_members_full_mode(tmp_path, capsys):
    researchers = members_dir(tmp_path, 'researchers')
    write_entry(researchers / 'gowoon-yang-19.md', {'name': 'stale', 'legacy_id': 19}, 'old body')
    fetcher = FakeFetcher()
    ctx = Context(fetcher, tmp_path, 'full')
    assert run_members(ctx) == {'members': 22 + 1 + 9 + 3}
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
    # A card with a LINK button: `link` right after `photo` (19 above has none, so no key).
    linked = read_frontmatter(researchers / 'gahee-son-55.md')
    assert linked['link'] == BASE_URL + '/bbs/link.php?bo_table=sub2_3&wr_id=55&no=1&page=1'
    assert list(linked) == ['board', 'category', 'name', 'photo', 'link', 'fields', 'order', 'legacy_url',
                            'legacy_id']
    images = tmp_path / 'public' / 'images' / 'members'
    assert (images / 'researchers' / '19.png').read_bytes() == ORIGINAL
    assert PHOTO_19 in fetcher.bytes_requested

    # Second tab: order continues, category known; missing original falls back to the thumbnail.
    new = read_frontmatter(researchers / 'gildong-hong-99.md')
    assert (new['category'], new['order'], new['photo']) == ('Affiliate', 23, '/images/members/researchers/99.jpg')
    assert (images / 'researchers' / '99.jpg').read_bytes() == THUMB
    assert read_frontmatter(researchers / 'dongyoung-jeong-66.md')['order'] == 22

    # No categories: no category key; both photos missing: no photo key and a warning.
    collaborator = read_frontmatter(members_dir(tmp_path, 'collaborators') / 'dong-wook-kim-ph-15.md')
    assert 'category' not in collaborator and 'photo' not in collaborator
    assert collaborator['fields'][0] == {'label': '', 'value': 'Clinical Professor'}
    assert collaborator['order'] == 1
    assert 'warning:' in capsys.readouterr().err
    assert len(list(members_dir(tmp_path, 'collaborators').glob('*.md'))) == 9

    # Members outside every tab come from the unfiltered sweep: no category, order after the tabs.
    alumni = members_dir(tmp_path, 'alumni')
    a, b = (read_frontmatter(alumni / name) for name in ('a-201.md', 'b-202.md'))
    assert (a['category'], a['order'], b['category'], b['order']) == ('Graduate', 1, 'Former', 2)
    swept = read_frontmatter(alumni / 'c-203.md')
    assert 'category' not in swept
    assert (swept['order'], swept['photo']) == (3, '/images/members/alumni/203.jpg')


def test_run_members_add_mode_skips_known_legacy_ids(tmp_path):
    researchers = members_dir(tmp_path, 'researchers')
    write_entry(researchers / 'renamed.md', {'name': 'kept', 'legacy_id': 19}, 'edited by hand')
    write_entry(researchers / '_draft.md', {'name': 'template', 'legacy_id': 23}, '')  # ignored
    before = (researchers / 'renamed.md').read_text(encoding='utf-8')
    fetcher = FakeFetcher()
    ctx = Context(fetcher, tmp_path, 'add')
    assert run_members(ctx) == {'members': 22 + 1 + 9 + 3 - 1}
    assert ctx.skipped == {'members': 1}
    assert fetcher.requested == [(url, True) for url in LIST_URLS]

    assert (researchers / 'renamed.md').read_text(encoding='utf-8') == before
    assert not (researchers / 'gowoon-yang-19.md').exists()
    assert PHOTO_19 not in fetcher.bytes_requested
    assert read_frontmatter(researchers / 'yongdo-yun-23.md')['order'] == 2


class PhotoFetcher:
    """Answers 302 for the URLs in `missing`, otherwise `data`."""

    def __init__(self, missing, data=ORIGINAL):
        self.missing, self.data, self.requested = missing, data, []

    def get_bytes(self, url, refresh=False):
        self.requested.append(url)
        if url in self.missing:
            raise urllib.error.HTTPError(url, 302, 'Found', {}, None)
        return self.data


PHOTO_DIR = BASE_URL + '/data/file/sub2_2/'


def test_download_photo_retries_upper_case_extension(tmp_path):
    fetcher = PhotoFetcher({PHOTO_DIR + 'x.jpg'})
    assert download_photo(fetcher, PHOTO_DIR + 'thumb-x_202x150.jpg', tmp_path / '13') == tmp_path / '13.jpg'
    assert fetcher.requested == [PHOTO_DIR + 'x.jpg', PHOTO_DIR + 'x.JPG']
    assert (tmp_path / '13.jpg').read_bytes() == ORIGINAL


def test_download_photo_falls_back_to_thumbnail_then_none(tmp_path):
    fetcher = PhotoFetcher({PHOTO_DIR + 'x.png', PHOTO_DIR + 'x.PNG'})
    assert download_photo(fetcher, PHOTO_DIR + 'thumb-x_202x150.png', tmp_path / '7') == tmp_path / '7.png'
    assert fetcher.requested == [PHOTO_DIR + 'x.png', PHOTO_DIR + 'x.PNG', PHOTO_DIR + 'thumb-x_202x150.png']

    fetcher = PhotoFetcher({PHOTO_DIR + 'y.png', PHOTO_DIR + 'y.PNG', PHOTO_DIR + 'thumb-y_202x150.png'})
    assert download_photo(fetcher, PHOTO_DIR + 'thumb-y_202x150.png', tmp_path / '8') is None
    assert len(fetcher.requested) == 3 and not (tmp_path / '8.png').exists()


def test_download_photo_shrinks_and_skips_existing(tmp_path):
    buffer = io.BytesIO()
    Image.new('RGB', (1600, 1000), 'green').save(buffer, 'JPEG')
    fetcher = PhotoFetcher(set(), buffer.getvalue())
    dest = download_photo(fetcher, PHOTO_DIR + 'thumb-z_202x150.jpg', tmp_path / '9')
    assert Image.open(dest).size == (800, 500)

    fetcher = PhotoFetcher(set())
    assert download_photo(fetcher, PHOTO_DIR + 'thumb-z_202x150.jpg', tmp_path / '9') == dest
    assert fetcher.requested == []
