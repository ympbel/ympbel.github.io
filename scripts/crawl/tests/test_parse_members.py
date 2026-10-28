from pathlib import Path

from crawl.config import BASE_URL
from crawl.parse_common import page_count, soup
from crawl.parse_members import Member, member_filename, original_photo_url, parse_member_list

FIXTURES = Path(__file__).resolve().parent / 'fixtures'


def fixture(name: str) -> str:
    return (FIXTURES / f'{name}.html').read_text(encoding='utf-8')


def test_parse_researchers_page1():
    m = parse_member_list(fixture('sub2_3_p1'))[0]
    assert m.name == '양고운 Gowoon Yang'
    assert m.wr_id == 19
    assert m.photo_url.endswith('_202x150.png')
    assert m.photo_url.startswith(BASE_URL + '/data/file/sub2_3/thumb-')
    assert m.fields[0] == ('Grade', 'M.D., Ph.D. Candidate')
    assert ('E-mail', 'gowoon1988@gmail.com') in m.fields
    assert m.category is None
    assert parse_member_list(fixture('sub2_3_p1'), 'MPBEL')[0].category == 'MPBEL'


def test_fields_flatten_nested_html():
    m = parse_member_list(fixture('sub2_3_p1'))[0]
    assert dict(m.fields)['Research Interest'] == 'Medical Physics'


def test_collaborator_empty_labels():
    m = parse_member_list(fixture('sub2_2'))[0]
    assert m.name == 'Dong Wook Kim, Ph.D'
    assert m.fields[0] == ('', 'Clinical Professor')


def test_fields_pairing_rules():
    html = ('<div class="mb_peple"><div class="cnt"><div class="mb_name"><h3>'
            '<a href="./board.php?bo_table=sub2_2&amp;wr_id=5">A  B </a></h3></div>'
            '<dl><dd>Lone</dd><dt>Empty</dt><dd> &nbsp; </dd><dt>X</dt><dd>Y</dd><dd>Z</dd></dl>'
            '<dl><dt>Second</dt><dd>list</dd></dl></div></div>')
    [m] = parse_member_list(html)
    assert (m.wr_id, m.name, m.photo_url) == (5, 'A B', None)
    assert m.fields == [('', 'Lone'), ('X', 'Y'), ('', 'Z')]


def test_original_photo_url():
    base = BASE_URL + '/data/file/sub2_3/'
    assert original_photo_url(base + 'thumb-3024172423_ULcQMJ5Y_5873_202x150.png') == (
        base + '3024172423_ULcQMJ5Y_5873.png')
    assert original_photo_url(base + '3024172423_ULcQMJ5Y_5873.png') == base + '3024172423_ULcQMJ5Y_5873.png'


def test_member_filename():
    assert member_filename('researchers', Member(19, '양고운 Gowoon Yang', None, [], None)) == 'gowoon-yang-19.md'
    assert member_filename('researchers', Member(19, '양고운', None, [], None)) == 'entry-19.md'


def test_page_count_members():
    assert page_count(soup(fixture('sub2_3_p1'))) == 2
    assert len(parse_member_list(fixture('sub2_3_p1'))) + len(parse_member_list(fixture('sub2_3_p2'))) >= 16
