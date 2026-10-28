import urllib.error
from pathlib import Path

from crawl.config import BASE_URL, board_url
from crawl.markdown import read_frontmatter, write_entry
from crawl.run import KIND_RUNNERS, Context
from crawl.run_publications import run_publications

FIXTURES = Path(__file__).resolve().parent / 'fixtures'


def nav(table, *cats):
    links = ''.join(f'<li><a href="{board_url(table, sca=c)}">{c}</a></li>' for c in cats)
    return f'<nav id="bo_cate"><ul id="bo_cate_ul">{links}</ul></nav>'


def row(table, wr_id, title, link=False, pinned=False):
    num = '<strong>공지</strong>' if pinned else str(wr_id)
    href = board_url(table, wr_id=wr_id).replace('&', '&amp;')
    button = (f'<a class="btn_set01" href="{BASE_URL}/bbs/link.php?bo_table={table}&amp;wr_id={wr_id}'
              '&amp;no=1">LINK</a>' if link else '')
    return (f'<table class="tb_basic_s"><tr class="bg1"><td class="num">{num}</td><td class="name_title">'
            f'<span class="text_title"><a href="{href}">{title}</a></span><br>'
            f'<span class="text_author">Author {wr_id}</span><br><span class="text_journal">'
            f'<span class="text_vol">Venue {wr_id}</span><br></span></td></tr>'
            f'<tr><td class="btn_positon" colspan="3">{button}</td></tr></table>')


def pager(table, last):
    return f'<nav class="pg_wrap"><a class="pg_page" href="./board.php?bo_table={table}&amp;page={last}">{last}</a></nav>'


def link_php(table, wr_id, sca=None):
    return f'{BASE_URL}/bbs/link.php?bo_table={table}&wr_id={wr_id}&no=1' + (f'&sca={sca}' if sca else '')


YEARS = [str(y) for y in range(2023, 2004, -1)]  # category tabs of the sub4_3 and sub4_4 fixtures
PAGES = {
    # Papers: two year tabs and one that is not a year; 2025 has a second page (from page_count).
    # The unfiltered pages add 5 and 4, filed under a year without a tab: their year is on the detail page.
    board_url('sub4_1', page=1): nav('sub4_1', '2025', '2024', 'misc') + row('sub4_1', 5, 'Untabbed paper', link=True)
                                 + row('sub4_1', 197, 'Repeat of 197') + pager('sub4_1', 2),
    board_url('sub4_1', page=2): row('sub4_1', 4, 'Untabbed without year'),
    board_url('sub4_1', wr_id=5): ('<table><tr><th>Year of publication</th><td>2003</td></tr></table>'
                                   '<section id="bo_v_file"><a class="view_file_download" href="./download.php?'
                                   'bo_table=sub4_1&amp;wr_id=5&amp;no=0"><strong>slides.pdf</strong></a></section>'),
    board_url('sub4_1', sca='2025', page=1): 'sub4_1_2025',
    board_url('sub4_1', sca='2025', page=2): row('sub4_1', 182, 'Second page paper', link=True)
                                             + row('sub4_1', 183, 'Duplicate of 183'),
    board_url('sub4_1', sca='2024', page=1): row('sub4_1', 150, 'Old paper'),
    # Talks: like the old site, the notice 3 is marked 공지 only on the unfiltered list (the fixture)
    # and is a plain row in its tab; filed here under 2023, its detail page (2021) gives the year.
    board_url('sub4_3', page=1): 'sub4_3',
    board_url('sub4_3', sca='2023', page=1): row('sub4_3', 3, 'AI-Driven Research &amp; Clinic in Radiation Therapy',
                                                 link=True),
    board_url('sub4_3', sca='2014', page=1): row('sub4_3', 2, 'MIM talk'),
    board_url('sub4_3', sca='2013', page=1): row('sub4_3', 1, 'SABR talk'),
    board_url('sub4_3', wr_id=3): 'view_sub4_3_3',
    # Patents: every row of the unfiltered page is also in a tab; a pinned row whose detail has no year.
    board_url('sub4_4', page=1): 'sub4_4',
    board_url('sub4_4', sca='2020', page=1): 'sub4_4',
    board_url('sub4_4', sca='2019', page=1): row('sub4_4', 9, 'Pinned patent', pinned=True),
}
BROKEN_LINK, NO_REDIRECT = link_php('sub4_1', 196, '2025'), link_php('sub4_1', 195, '2025')


class FakeFetcher:
    def __init__(self):
        self.requested = []  # (url, refresh) of every get()
        self.resolved = []

    def get(self, url, refresh=False):
        self.requested.append((url, refresh))
        page = PAGES.get(url, '<html></html>')
        return page if page.startswith('<') else (FIXTURES / f'{page}.html').read_text(encoding='utf-8')

    def resolve_redirect(self, url):
        self.resolved.append(url)
        if url == BROKEN_LINK:
            raise urllib.error.HTTPError(url, 404, 'Not Found', {}, None)
        if url == NO_REDIRECT:
            return None
        return f'https://doi.org/10.1/{url.split("wr_id=")[1].split("&")[0]}'


def requests(refresh):
    """Every get() of one run, in order: per board all list pages (the unfiltered first page once,
    before the tabs; its other pages after them), then the detail pages, which are never refreshed."""
    lists = lambda table, cats: [(board_url(table, sca=c, page=1), refresh) for c in cats]  # noqa: E731
    return ([(board_url('sub4_1', page=1), refresh), (board_url('sub4_1', sca='2025', page=1), refresh),
             (board_url('sub4_1', sca='2025', page=2), refresh), (board_url('sub4_1', sca='2024', page=1), refresh),
             (board_url('sub4_1', page=2), refresh), (board_url('sub4_1', wr_id=5), False),
             (board_url('sub4_1', wr_id=4), False),
             (board_url('sub4_2', page=1), refresh),
             (board_url('sub4_3', page=1), refresh)] + lists('sub4_3', YEARS)
            + ([(board_url('sub4_3', wr_id=3), False)] if not refresh else [])
            + [(board_url('sub4_4', page=1), refresh)] + lists('sub4_4', YEARS)
            + [(board_url('sub4_4', wr_id=9), False)])


def content(root, collection):
    return root / 'src' / 'content' / collection / 'ko'


def test_publications_runner_is_registered():
    assert KIND_RUNNERS['publications'] is run_publications


def test_run_publications_full_mode(tmp_path, capsys):
    fetcher = FakeFetcher()
    ctx = Context(fetcher, tmp_path, 'full')
    assert run_publications(ctx) == {'papers': 15 + 1 + 1 + 1, 'presentations': 0, 'talks': 3, 'patents': 7 + 1}
    assert ctx.skipped == {'papers': 0, 'presentations': 0, 'talks': 0, 'patents': 0}
    assert fetcher.requested == requests(refresh=False)
    err = capsys.readouterr().err
    assert "warning: sub4_1 category 'misc' is not a year" in err
    assert 'warning: no link for papers 196' in err and 'warning: no link for papers 195' in err
    assert 'warning: no year for papers 4' in err

    papers = content(tmp_path, 'papers')
    assert len(list(papers.glob('*.md'))) == 18
    path = papers / '2025-197-anatomical-position-guided-auto-segmentation.md'
    entry = read_frontmatter(path)
    assert entry == {
        'year': 2025,
        'title': 'Anatomical Position-Guided Auto-segmentation and Dosimetric Evaluation of Vestibular '
                 'Schwannomas in Gamma Knife Radiosurgery',
        'authors': 'Younghun Yoon ,Shanti Marasini ,Alex Macintyre ,Eunsu Kim ,Chanwoong Lee ,Jin Sung Kim ,Taeho Kim',
        'venue': 'Medical Physics\nVolume52, e70082\n26 November 2025',
        'link': 'https://doi.org/10.1/197', 'pinned': False, 'order': 197, 'legacy_files': [],
        'legacy_url': board_url('sub4_1', wr_id=197), 'legacy_id': 197}
    assert list(entry) == ['year', 'title', 'authors', 'venue', 'link', 'pinned', 'order', 'legacy_files',
                           'legacy_url', 'legacy_id']
    text = path.read_text(encoding='utf-8')
    assert 'venue: |-\n  Medical Physics\n  Volume52, e70082\n  26 November 2025\n' in text
    assert text.endswith('---\n\n\n')

    # A link that 404s or does not redirect, and a row without LINK: no link key.
    for name in ('2025-196-feasibility-of-improving-daily-mvct.md', '2025-195-dosimetric-impact-of-androgen-deprivation.md',
                 '2024-150-old-paper.md'):
        assert 'link' not in read_frontmatter(papers / name)
    # Second page of a tab; the repeat of 183 there is ignored.
    assert read_frontmatter(papers / '2025-182-second-page-paper.md')['link'] == 'https://doi.org/10.1/182'
    assert read_frontmatter(papers / '2025-183-algorithm-for-using-dual-energy.md')['order'] == 183
    assert len(fetcher.resolved) == 23 and len(set(fetcher.resolved)) == 23  # 17 papers, 1 talk, 5 patents

    # Outside every tab: year and files from the detail page; without a year it is not written.
    untabbed = read_frontmatter(papers / '2003-5-untabbed-paper.md')
    assert (untabbed['year'], untabbed['pinned'], untabbed['link']) == (2003, False, 'https://doi.org/10.1/5')
    assert untabbed['legacy_files'] == [{'name': 'slides.pdf', 'url': '/bbs/download.php?bo_table=sub4_1&wr_id=5&no=0'}]
    assert not list(papers.glob('*-4-*.md'))

    # Pinned talk (marked on the unfiltered list only): year and files from its detail page.
    talks = content(tmp_path, 'talks')
    assert sorted(p.name for p in talks.glob('*.md')) == [
        '2013-1-sabr-talk.md', '2014-2-mim-talk.md', '2021-3-ai-driven-research-clinic-in.md']
    pinned = read_frontmatter(talks / '2021-3-ai-driven-research-clinic-in.md')
    assert (pinned['year'], pinned['pinned'], pinned['order'], pinned['link']) == (2021, True, 3, 'https://doi.org/10.1/3')
    assert pinned['legacy_files'] == [{'name': 'KAMPINA.KSMP special session flyer.final - Google Docs.pdf',
                                       'url': '/bbs/download.php?bo_table=sub4_3&wr_id=3&no=0'}]
    assert read_frontmatter(talks / '2014-2-mim-talk.md')['pinned'] is False

    # Pinned patent whose detail page has no year: the tab's year.
    patent = read_frontmatter(content(tmp_path, 'patents') / '2019-9-pinned-patent.md')
    assert (patent['year'], patent['pinned'], patent['legacy_files']) == (2019, True, [])
    assert not (content(tmp_path, 'presentations')).exists()


def test_run_publications_add_mode_skips_known_legacy_ids(tmp_path):
    papers, talks = content(tmp_path, 'papers'), content(tmp_path, 'talks')
    write_entry(papers / 'renamed.md', {'title': 'kept', 'legacy_id': 197}, 'edited by hand')
    write_entry(papers / '_template.md', {'title': 'template', 'legacy_id': 196}, '')  # ignored
    write_entry(talks / 'pinned-talk.md', {'title': 'kept', 'legacy_id': 3}, '')
    before = (papers / 'renamed.md').read_text(encoding='utf-8')
    fetcher = FakeFetcher()
    ctx = Context(fetcher, tmp_path, 'add')
    assert run_publications(ctx) == {'papers': 17, 'presentations': 0, 'talks': 2, 'patents': 8}
    assert ctx.skipped == {'papers': 1, 'presentations': 0, 'talks': 1, 'patents': 0}
    # Lists refreshed; the known pinned talk's detail page is not fetched.
    assert fetcher.requested == requests(refresh=True)
    assert link_php('sub4_1', 197, '2025') not in fetcher.resolved
    assert not [url for url in fetcher.resolved if 'sub4_3' in url]
    assert len(fetcher.resolved) == 16 + 5  # papers, patents

    assert (papers / 'renamed.md').read_text(encoding='utf-8') == before
    assert not (papers / '2025-197-anatomical-position-guided-auto-segmentation.md').exists()
    assert (papers / '2025-196-feasibility-of-improving-daily-mvct.md').exists()
    assert not (talks / '2021-3-ai-driven-research-clinic-in.md').exists()
