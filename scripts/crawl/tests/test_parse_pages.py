from pathlib import Path

from crawl.config import BASE_URL
from crawl.parse_common import categories, full_title, page_count, path_of, soup, wr_id_of
from crawl.parse_pages import (local_image_paths, normalize_html, parse_home, parse_static_page,
                               rewrite_images)

FIXTURES = Path(__file__).resolve().parent / 'fixtures'


def fixture(name: str) -> str:
    return (FIXTURES / f'{name}.html').read_text(encoding='utf-8')


def test_full_title_strips_suffix():
    assert full_title(soup(fixture('view_sub6_3_471'))) == (
        '2025/12/29 [Research Seminar] Group Sparse Algorithm for RBE-Weighted Dose '
        'Optimization in Carbon Ion Radiotherapy')
    assert full_title(soup('<title>A &gt; B | C > Seminar | MPBEL | x</title>')) == 'A > B | C'


def test_page_count():
    assert page_count(soup(fixture('sub2_3_p1'))) == 2
    assert page_count(soup(fixture('sub1_1'))) == 1


def test_categories_cover_post_and_member_boards():
    assert categories(soup(fixture('sub2_3_p1'))) == ['MPBEL', 'Affiliate']
    assert categories(soup(fixture('sub6_3_p1')))[:2] == ['2025', '2024']
    assert categories(soup(fixture('sub1_1'))) == []


def test_path_of_and_wr_id_of():
    assert path_of('../images/x.png') == '/images/x.png'
    assert path_of(BASE_URL + '/data/editor/2006/a.PNG') == '/data/editor/2006/a.PNG'
    assert path_of(BASE_URL + '/bbs/view_image.php?fn=%2Fdata%2Feditor%2F2510%2Fb.JPG') == '/data/editor/2510/b.JPG'
    assert wr_id_of('./board.php?bo_table=sub6_3&wr_id=471&page=2') == 471
    assert wr_id_of('./board.php?bo_table=sub6_3&page=2') is None


def test_parse_welcome():
    page = parse_static_page(fixture('sub1_1'))
    assert 'class="welcome_wrap"' in page.body_html
    assert '<style' not in page.body_html
    assert '<form' not in page.body_html
    assert 'fboardlist' not in page.body_html
    assert page.image_urls == [BASE_URL + '/images/sub/welcomeVis.png']


def test_parse_professor_keeps_structure():
    page = parse_static_page(fixture('sub2_1'))
    assert 'class="prof_info"' in page.body_html
    assert '<h3>김진성' in page.body_html
    assert len(page.image_urls) == 1
    assert page.image_urls[0].startswith(BASE_URL + '/data/editor/1911/')
    assert page.image_urls[0].endswith('.png')


def test_parse_research_ct_images():
    page = parse_static_page(fixture('sub3_1'))
    assert len(page.image_urls) == 4
    assert page.image_urls[0] == BASE_URL + '/images/sub/r1.png'


def test_parse_static_page_serializes_like_the_source():
    body = parse_static_page(fixture('sub3_1')).body_html
    assert '<div style="text-align: justify;" align="justify"><b style="font-family: 나눔고딕, NanumGothic; font-size: 18pt;">개요&nbsp;</b></div>' in body
    assert '\xa0' not in body
    assert '<br>' in body and '<br/>' not in body


def test_parse_static_page_drops_editor_bookmarks():
    # Empty SmartEditor selection markers; left in front of the first block tag they would keep
    # markdown from reading the body as one HTML block (an inline tag line opens a paragraph).
    html = ('<div class="contents"><table class="board_list"><tr><td>\n\t<span id="husky_bookmark_start_1">'
            '</span><span id="husky_bookmark_end_1"></span><div class="research_02">x</div></td></tr></table></div>')
    assert normalize_html(parse_static_page(html).body_html) == '<div class="research_02">x</div>'


def test_parse_static_page_uses_original_of_view_image_thumbnail():
    html = ('<div class="contents"><table class="board_list"><tr><td><p>'
            '<a href="http://mpbel.yonsei.ac.kr/bbs/view_image.php?fn=%2Fdata%2Feditor%2F2510%2Fa.JPG" '
            'target="_blank" class="view_image"><img src="http://mpbel.yonsei.ac.kr/data/editor/2510/'
            'thumb-a_800x1067.jpg"></a><img src="/images/sub/r1.png?ver=2">'
            '<input type="hidden" name="x" value="y"><!-- note --></p></td></tr></table></div>')
    page = parse_static_page(html)
    assert page.image_urls == [BASE_URL + '/data/editor/2510/a.JPG', BASE_URL + '/images/sub/r1.png']
    assert 'view_image' not in page.body_html
    assert '<input' not in page.body_html
    assert 'note' not in page.body_html


def test_rewrite_images():
    body = '<p><img src="/images/sub/r1.png" alt="a"><img src="https://example.com/x.png"></p>'
    result = rewrite_images(body, {BASE_URL + '/images/sub/r1.png': '/images/pages/research-ct-reconstruction/r1.png'})
    assert result == ('<p><img src="/images/pages/research-ct-reconstruction/r1.png" alt="a">'
                      '<img src="https://example.com/x.png"></p>')


def test_local_image_paths_suffixes_duplicate_basenames():
    urls = [BASE_URL + '/images/sub/r1.png', BASE_URL + '/data/editor/r1.png', BASE_URL + '/data/r1.png']
    assert local_image_paths('research-ai', urls) == {
        urls[0]: '/images/pages/research-ai/r1.png',
        urls[1]: '/images/pages/research-ai/r1-2.png',
        urls[2]: '/images/pages/research-ai/r1-3.png',
    }


def test_normalize_html_has_no_blank_or_indented_lines():
    html = '<div class="a">\r\n\n    <p style="x">one  two</p>\n\t<span>three</span>\n   \n\t\t</div>\n'
    result = normalize_html(html)
    assert result == '<div class="a">\n<p style="x">one  two</p>\n<span>three</span>\n</div>'
    for line in result.split('\n'):
        assert line and not line[0].isspace()


def test_parse_home():
    home = parse_home(fixture('index'))
    assert '연세 의학물리 및 의공학 연구실' in home.about_html
    assert home.links[0] == ('김진성 교수님 블로그', 'http://mpjinsung.tistory.com/')
    assert len(home.links) == 4
    # The old labels' <br> is kept as a line break.
    assert home.links[1] == ('연세의료원 연세암병원\n의학물리팀 블로그', 'http://medphy.tistory.com/')
    assert home.links[3][0] == '연세의료원 연세암병원\n방사선종양학과'
