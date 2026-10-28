from pathlib import Path

from crawl.config import BASE_URL
from crawl.parse_common import block_text, page_count, soup
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


def test_block_text_keeps_paragraphs():
    dd = soup('<dd><p>Particle Therapy</p><p>MS Student majoring in particle physics '
              '@Gangneung-Wonju National University</p></dd>').dd
    assert block_text(dd) == ('Particle Therapy\n'
                              'MS Student majoring in particle physics @Gangneung-Wonju National University')
    assert block_text(soup('<dd><p>Medical Physics<br>Radiologic  Technician&nbsp;@SNU<br/></p></dd>').dd) == (
        'Medical Physics\nRadiologic Technician @SNU')
    nested = soup(fixture('sub2_3_p1')).select_one('div.mb_peple .cnt dl').find_all('dd', recursive=False)[2]
    assert block_text(nested) == 'Medical Physics'
    assert block_text(None) == ''


def test_multi_paragraph_values_keep_line_breaks():
    alumni = {m.wr_id: dict(m.fields) for m in parse_member_list(fixture('sub2_4'))}
    assert alumni[33]['Research Interest'] == (
        'Particle Therapy\nMS Student majoring in particle physics @Gangneung-Wonju National University')
    interns = {m.wr_id: dict(m.fields) for m in parse_member_list(fixture('sub2_5'))}
    assert interns[12]['Research Interest'] == 'Neuroscience\nUndergraduate @Brown University'
    # A trailing <br> inside the paragraph adds no empty line.
    researchers = {m.wr_id: dict(m.fields) for m in parse_member_list(fixture('sub2_3_p1'))}
    assert researchers[55]['Research Interest'] == 'Monte Carlo simulation, Medical Physics'


def test_member_link_button():
    # Old-site markup after div.cnt: <div id="" class="link01"><a href='…/bbs/link.php?…' target=_blank
    # class='btn_set01' >LINK</a></div>; the block is empty on cards without a link.
    html = ('<div class="mb_peple"><div class="cntWrap"><div class="cnt"><div class="mb_name"><h3>'
            '<a href="./board.php?bo_table=sub2_3&amp;wr_id=7">A</a></h3></div><dl></dl></div>'
            '<div id="" class="link01"><a href=" ./link.php?bo_table=sub2_3&amp;wr_id=7&amp;no=1 "'
            " target=_blank class='btn_set01' >LINK</a><a href='/second'>x</a></div></div></div>")
    [m] = parse_member_list(html)
    assert m.link == BASE_URL + '/bbs/link.php?bo_table=sub2_3&wr_id=7&no=1'

    members = {m.wr_id: m for m in parse_member_list(fixture('sub2_3_p1'))}
    assert members[19].link is None
    assert members[55].link == BASE_URL + '/bbs/link.php?bo_table=sub2_3&wr_id=55&no=1&page=1'
    assert sum(m.link is not None for m in members.values()) == 5
    no_block = ('<div class="mb_peple"><div class="cnt"><div class="mb_name"><h3>'
                '<a href="./board.php?bo_table=sub2_2&amp;wr_id=5">B</a></h3></div></div></div>')
    assert parse_member_list(no_block)[0].link is None
