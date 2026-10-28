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
