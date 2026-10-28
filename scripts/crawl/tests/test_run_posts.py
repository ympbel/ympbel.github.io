from pathlib import Path

from crawl.config import BASE_URL, board_url
from crawl.markdown import read_frontmatter, write_entry
from crawl.parse_posts import parse_post_list
from crawl.run import KIND_RUNNERS, Context
from crawl.run_posts import run_posts

FIXTURES = Path(__file__).resolve().parent / 'fixtures'


def fixture(name: str) -> str:
    return (FIXTURES / f'{name}.html').read_text(encoding='utf-8')


def row(table, wr_id, category=None, pinned=False):
    cate = f'<a href="#" class="bo_cate_link">{category}</a>' if category else ''
    href = board_url(table, wr_id=wr_id).replace('&', '&amp;')
    return (f'<tr class="{"bo_notice" if pinned else ""}"><td class="td_subject">{cate}<div class="bo_tit">'
            f'<a href="{href}&amp;page=1">Post {wr_id}</a></div></td></tr>')


def rows(*trs):
    return f'<table><tbody>{"".join(trs)}</tbody></table>'


def view(title, posted='24-03-05 09:10', category=None, con='<p>Body</p>', files=''):
    cate = f'<span class="bo_v_cate">{category}</span>' if category else ''
    return (f'<html><head><title>{title} &gt; Board | MPBEL | x</title></head><body><article id="bo_v">'
            f'<h2 id="bo_v_title">{cate}<span class="bo_v_tit">{title}</span></h2><section id="bo_v_info">'
            f'<strong class="if_date">{posted}</strong></section><section id="bo_v_file">{files}</section>'
            f'<div id="bo_v_con">{con}</div></article></body></html>')


NEWS_P1, NEWS_P2 = parse_post_list(fixture('sub6_1_p1')), parse_post_list(fixture('sub6_1_p2'))
NEWS_IDS = [r.wr_id for r in NEWS_P1 + NEWS_P2] + [7]  # 5 (pinned) .. 92 .., then 7 from page 3
LECTURE_IDS = [1, 2]
SEMINAR_IDS = [471, 470]
DOWNLOAD = f'{BASE_URL}/bbs/download.php?bo_table=sub6_3&amp;wr_id=470&amp;no=0'
PAGES = {
    # News: the fixture's pager gives 4 pages; page 3 repeats the pinned 5 and adds 7 (no category), page 4 is empty.
    board_url('sub6_1', page=1): fixture('sub6_1_p1'),
    board_url('sub6_1', page=2): fixture('sub6_1_p2'),
    board_url('sub6_1', page=3): rows(row('sub6_1', 5, '연구실소식', pinned=True), row('sub6_1', 7)),
    board_url('sub6_1', wr_id=92): fixture('view_sub6_1_92'),
    board_url('sub6_1', wr_id=5): view('[YMPBEL 대학원생 모집]', '25-04-23 10:00', '연구실소식'),
    board_url('sub6_1', wr_id=7): view('Untagged', '19-01-02 08:00'),
    # Seminars: one page; 470 has a bare image, an attachment and neither category nor presenter.
    board_url('sub6_3', page=1): rows(row('sub6_3', 471, '2025'), row('sub6_3', 470)),
    board_url('sub6_3', wr_id=471): fixture('view_sub6_3_471'),
    board_url('sub6_3', wr_id=470): view('Green', '25-12-31 11:30', con='<p>Text</p><p><img src="/data/editor/2512/g.png"></p>',
                                         files=f'<a class="view_file_download" href="{DOWNLOAD}"><strong>g.pdf</strong></a>'),
    # Lectures: the fixture list (1 pinned, 2), 1 is the fixture view.
    board_url('sub5_1', page=1): fixture('sub5_1'),
    board_url('sub5_1', wr_id=1): fixture('view_sub5_1_1'),
}


class FakeFetcher:
    def __init__(self):
        self.requested = []  # (url, refresh) of every get()

    def get(self, url, refresh=False):
        self.requested.append((url, refresh))
        if url in PAGES:
            return PAGES[url]
        if 'wr_id=' in url:  # any other view
            return view(f'Post {url.split("wr_id=")[1]}')
        return '<html></html>'


def requests(refresh, news=NEWS_IDS, seminars=SEMINAR_IDS, lectures=LECTURE_IDS):
    """Every get() of one run: per board the unfiltered list pages only (never a category tab),
    then one view per new wr_id, never refreshed."""
    return ([(board_url('sub6_1', page=p), refresh) for p in (1, 2, 3, 4)]
            + [(board_url('sub6_1', wr_id=i), False) for i in news]
            + [(board_url('sub6_3', page=1), refresh)] + [(board_url('sub6_3', wr_id=i), False) for i in seminars]
            + [(board_url('sub5_1', page=1), refresh)] + [(board_url('sub5_1', wr_id=i), False) for i in lectures])


def content(root, collection):
    return root / 'src' / 'content' / collection / 'ko'


def test_posts_runner_is_registered():
    assert KIND_RUNNERS['posts'] is run_posts


def test_run_posts_full_mode(tmp_path):
    fetcher = FakeFetcher()
    ctx = Context(fetcher, tmp_path, 'full')
    assert run_posts(ctx) == {'news': 31, 'seminars': 2, 'lectures': 2}
    assert ctx.skipped == {'news': 0, 'seminars': 0, 'lectures': 0}
    assert len(NEWS_IDS) == 31 and NEWS_IDS[:2] == [5, 92]
    assert fetcher.requested == requests(refresh=False)

    news = content(tmp_path, 'news')
    assert len(list(news.glob('*.md'))) == 31
    entry = read_frontmatter(news / '2025-10-22-92.md')
    assert entry == {
        'title': '2025 KOSRO Autumn Conference Award !!', 'date': '2025-10-22', 'category': '2025', 'pinned': False,
        'legacy_images': ['/data/editor/2510/50fcfa4867d5ab599069dfced62058c0_1761105130_3586.JPG',
                          '/data/editor/2510/50fcfa4867d5ab599069dfced62058c0_1761105128_5783.JPG'],
        'legacy_files': [], 'legacy_url': board_url('sub6_1', wr_id=92), 'legacy_id': 92}
    assert list(entry) == ['title', 'date', 'category', 'pinned', 'legacy_images', 'legacy_files',
                           'legacy_url', 'legacy_id']
    text = (news / '2025-10-22-92.md').read_text(encoding='utf-8')
    assert text.endswith('---\n\n2025 KOSRO (The Korean Society for Radiation Oncology) Autumn Conference (10.17).\n\n'
                         '**Congratulations to Dong Min Jung!**\n')
    # The pinned row, listed on pages 1 and 3, is written once and stays pinned.
    assert read_frontmatter(news / '2025-04-23-5.md')['pinned'] is True
    assert sum(read_frontmatter(p)['pinned'] for p in news.glob('*.md')) == 1
    assert 'category' not in read_frontmatter(news / '2019-01-02-7.md')

    seminars = content(tmp_path, 'seminars')
    seminar = read_frontmatter(seminars / '2025-12-31-471.md')
    assert seminar == {
        'title': '2025/12/29 [Research Seminar] Group Sparse Algorithm for RBE-Weighted Dose Optimization in '
                 'Carbon Ion Radiotherapy',
        'date': '2025-12-31', 'category': '2025', 'pinned': False, 'presenter': '이혜진', 'event_date': '2025-12-29',
        'legacy_images': ['/data/editor/2512/9d39b5b8da291607cba002ff2d25bc82_1767148425_8757.png'],
        'legacy_files': [], 'legacy_url': board_url('sub6_3', wr_id=471), 'legacy_id': 471}
    assert list(seminar) == ['title', 'date', 'category', 'pinned', 'presenter', 'event_date', 'legacy_images',
                             'legacy_files', 'legacy_url', 'legacy_id']
    assert (seminars / '2025-12-31-471.md').read_text(encoding='utf-8').endswith('---\n\nPresenter: 이혜진\n')
    # No category, presenter or event date: no such keys.
    bare = read_frontmatter(seminars / '2025-12-31-470.md')
    assert bare == {'title': 'Green', 'date': '2025-12-31', 'pinned': False, 'legacy_images': ['/data/editor/2512/g.png'],
                    'legacy_files': [{'name': 'g.pdf', 'url': '/bbs/download.php?bo_table=sub6_3&wr_id=470&no=0'}],
                    'legacy_url': board_url('sub6_3', wr_id=470), 'legacy_id': 470}
    assert '<img' not in (seminars / '2025-12-31-470.md').read_text(encoding='utf-8')

    lectures = content(tmp_path, 'lectures')
    assert sorted(p.name for p in lectures.glob('*.md')) == ['2018-04-19-1.md', '2024-03-05-2.md']
    lecture = read_frontmatter(lectures / '2018-04-19-1.md')
    assert (lecture['title'], lecture['pinned'], lecture['event_date']) == ('[2학기] 의료영상개론', True, '2018-09-01')
    assert 'category' not in lecture and 'presenter' not in lecture


def test_run_posts_add_mode_skips_known_legacy_ids(tmp_path):
    news, seminars = content(tmp_path, 'news'), content(tmp_path, 'seminars')
    write_entry(news / 'renamed.md', {'title': 'kept', 'legacy_id': 92}, 'edited by hand')
    write_entry(news / '_template.md', {'title': 'template', 'legacy_id': 5}, '')  # ignored
    write_entry(seminars / '2025-12-31-471.md', {'title': 'kept', 'legacy_id': 471}, '')
    before = (news / 'renamed.md').read_text(encoding='utf-8')
    fetcher = FakeFetcher()
    ctx = Context(fetcher, tmp_path, 'add')
    assert run_posts(ctx) == {'news': 30, 'seminars': 1, 'lectures': 2}
    assert ctx.skipped == {'news': 1, 'seminars': 1, 'lectures': 0}
    # Lists refreshed; no view fetched for a known wr_id.
    assert fetcher.requested == requests(refresh=True, news=[i for i in NEWS_IDS if i != 92], seminars=[470])

    assert (news / 'renamed.md').read_text(encoding='utf-8') == before
    assert not (news / '2025-10-22-92.md').exists()
    assert read_frontmatter(news / '2025-04-23-5.md')['pinned'] is True
    assert read_frontmatter(seminars / '2025-12-31-471.md') == {'title': 'kept', 'legacy_id': 471}
