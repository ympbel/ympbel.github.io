from pathlib import Path

from crawl.parse_publications import (Publication, parse_detail_files, parse_publication_detail_year,
                                      parse_publication_rows, publication_filename)

FIXTURES = Path(__file__).resolve().parent / 'fixtures'


def fixture(name: str) -> str:
    return (FIXTURES / f'{name}.html').read_text(encoding='utf-8')


def test_paper_rows_2025():
    rows = parse_publication_rows(fixture('sub4_1_2025'))
    assert len(rows) == 15
    first = rows[0]
    assert first.wr_id == 197
    assert first.title.startswith('Anatomical Position-Guided')
    assert first.authors.startswith('Younghun Yoon')
    assert first.venue == 'Medical Physics\nVolume52, e70082\n26 November 2025'
    assert 'link.php?bo_table=sub4_1&wr_id=197' in first.link_php
    assert first.pinned is False


def test_row_without_link():
    html = ('<table class="tb_basic_s"><tr class="bg1"><td class="num">3</td><td class="name_title">'
            '<span class="text_title"><a href="./board.php?bo_table=sub4_4&amp;wr_id=12">A patent</a></span><br>'
            '<span class="text_author">Kim</span><br><span class="text_journal"><span class="text_vol">X</span>'
            '</span></td></tr></table>')
    assert parse_publication_rows(html) == [Publication(12, 'A patent', 'Kim', 'X', None, False)]


def journal_row(wr_id, journal, buttons=''):
    """One `tb_basic_s` list row as the old skin printed it: a title, an author, the `.text_journal`
    span left open, then the button row."""
    return ('<table class="tb_basic_s"><tr class="bg1"><td class="num">1</td><td class="name_title">'
            f'<span class="text_title"><a href="./board.php?bo_table=sub4_2&amp;wr_id={wr_id}">Title</a></span><br>'
            f'<span class="text_author">Kim</span><br><span class="text_journal">{journal}</tr>'
            f'<tr><td colspan="3" class="btn_positon">{buttons}</tr></table>')


def test_download_button_recorded_with_link():
    # No row of the fixtures has a DOWNLOAD button (only 29 rows of older years do): markup of
    # presentation 98 / paper 84, the relative `download.php` with raw `&` before the LINK.
    assert not [r for r in parse_publication_rows(fixture('sub4_1_2025')) if r.files]
    buttons = ("&nbsp;<a href='download.php?bo_table=sub4_2&wr_id=94&no=0' class='btn_set01' target='_blanked'>"
               "DOWNLOAD</a>\t<a href='http://mpbel.yonsei.ac.kr/bbs/link.php?bo_table=sub4_2&amp;wr_id=94&amp;no=1"
               "&amp;page=13' target=_blank  class='btn_set01' >LINK</a>")
    [row] = parse_publication_rows(journal_row(94, '<span class="text_vol">X</span><br>', buttons))
    assert row.files == [('DOWNLOAD', '/bbs/download.php?bo_table=sub4_2&wr_id=94&no=0')]
    assert row.link_php == 'http://mpbel.yonsei.ac.kr/bbs/link.php?bo_table=sub4_2&wr_id=94&no=1&page=13'


def test_rows_without_download_have_no_files():
    assert all(r.files == [] for r in parse_publication_rows(fixture('sub4_4')))


def test_blank_venue_lines_kept_inside_trailing_dropped():
    # Paper 195 (fixture): `SSRN, <br> <br>31 Mar 2025 <br>`, the year field empty between the two <br>.
    rows = {r.wr_id: r for r in parse_publication_rows(fixture('sub4_1_2025'))}
    assert rows[195].venue == 'SSRN\n\n31 Mar 2025'
    # An empty text_vol on its own line is a blank line too; the empty lines after the last value are not.
    journal = ('<span class="text_vol">A</span> <br><span class="text_vol"></span> <br>'
               '<span class="text_vol">C</span> <br><span class="text_vol"></span> <br><br>')
    assert parse_publication_rows(journal_row(1, journal))[0].venue == 'A\n\nC'


def test_link_comes_from_the_same_table_only():
    # sub4_4: 8 and 7 have an empty btn_positon cell; the next table's LINK must not leak into them.
    rows = parse_publication_rows(fixture('sub4_4'))
    assert [(r.wr_id, r.link_php is None) for r in rows] == [
        (8, True), (7, True), (6, False), (5, False), (3, False), (2, False), (4, False)]
    assert 'wr_id=6&no=1' in rows[2].link_php


def test_pinned_row_detected():
    rows = parse_publication_rows(fixture('sub4_3'))
    pinned = [r for r in rows if r.pinned]
    assert [r.title for r in pinned] == ['AI-Driven Research & Clinic in Radiation Therapy']
    assert pinned[0].wr_id == 3
    assert pinned[0].venue == '2021 AAPM Annual Meeting\nVirtual\nJuly 25, 2021'


def test_patent_venue_labels():
    first = parse_publication_rows(fixture('sub4_4'))[0]
    assert first.venue == '등록국가: 대한민국\n등록번호: 10-2020-0106825\n등록일: 2020-08-25'


def test_detail_year_and_files():
    html = fixture('view_sub4_3_3')
    assert parse_publication_detail_year(html) == 2021
    assert parse_detail_files(html) == [
        ('KAMPINA.KSMP special session flyer.final - Google Docs.pdf',
         '/bbs/download.php?bo_table=sub4_3&wr_id=3&no=0')]


def test_detail_year_missing():
    assert parse_publication_detail_year('<table><tr><th>Title</th><td>x</td></tr></table>') is None
    assert parse_publication_detail_year('<table><tr><th>Year of publication</th><td></td></tr></table>') is None
    assert parse_detail_files('<html></html>') == []


def test_publication_filename():
    p = Publication(197, 'Anatomical Position-Guided Auto-segmentation and Dosimetric Evaluation of …',
                    '', '', None, False)
    assert publication_filename(2025, p) == '2025-197-anatomical-position-guided-auto-segmentation.md'
