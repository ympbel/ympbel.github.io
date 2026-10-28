from crawl.markdown import html_to_markdown, read_frontmatter, slugify, write_entry


def test_write_entry_quotes_special_characters(tmp_path):
    path = tmp_path / 'entry.md'
    frontmatter = {'title': 'A: B "C" #1', 'authors': '* Kim, Lee'}
    write_entry(path, frontmatter, 'Body')
    assert path.read_text(encoding='utf-8').startswith('---\n')
    assert read_frontmatter(path) == frontmatter


def test_write_entry_keeps_date_string(tmp_path):
    path = tmp_path / 'entry.md'
    write_entry(path, {'date': '2025-10-22'}, '')
    assert "date: '2025-10-22'" in path.read_text(encoding='utf-8')
    fm = read_frontmatter(path)
    assert type(fm['date']) is str


def test_write_entry_writes_multiline_strings_as_literal_blocks(tmp_path):
    # Hand-editable: one line per line, instead of a quoted scalar where a blank line means a newline.
    path = tmp_path / 'entry.md'
    frontmatter = {'fields': [{'label': 'Research Interest',
                               'value': 'Neuroscience\nUndergraduate @Brown University'}]}
    write_entry(path, frontmatter, '')
    assert ('- label: Research Interest\n  value: |-\n    Neuroscience\n    Undergraduate @Brown University\n'
            in path.read_text(encoding='utf-8'))
    assert read_frontmatter(path) == frontmatter


def test_slugify():
    title = 'Anatomical Position-Guided Auto-segmentation and Dosimetric Evaluation'
    # The brief paired max_words=5 with this 6-word slug; that contradicts the rule and Task 6's
    # test_publication_filename (slugify(title, 5) -> '...-auto-segmentation'), so check both.
    assert slugify(title) == 'anatomical-position-guided-auto-segmentation-and'
    assert slugify(title, 5) == 'anatomical-position-guided-auto-segmentation'
    assert slugify('양고운') == 'entry'
    assert slugify('양고운 Gowoon Yang') == 'gowoon-yang'


def test_html_to_markdown_strips_spans():
    assert html_to_markdown('<p><span style="x">Hi</span> <b>there</b></p>') == 'Hi **there**'


def test_html_to_markdown_escapes_angle_brackets():
    assert html_to_markdown('<p>&lt;Juyoung Lee&gt;</p>') == '&lt;Juyoung Lee&gt;'
    assert html_to_markdown('<p>a &gt; b</p><p>&gt; not a quote</p>') == 'a &gt; b\n\n&gt; not a quote'
    # Autolinks keep their brackets; `-` and `#` are not escaped.
    assert html_to_markdown('<p><a href="http://x.kr/">http://x.kr/</a> - #1</p>') == '<http://x.kr/> - #1'


def test_html_to_markdown_merges_adjacent_bold():
    md = html_to_markdown('<p><b>PROs :</b><b>Hyo</b></p>')
    assert '****' not in md
    assert md == '**PROs :Hyo**'  # one run, the text unchanged
    # Bold inside bold is one run.
    assert html_to_markdown('<p><b><b>- Topic : X</b> </b></p><p><strong><b>Y</b></strong></p>') == '**- Topic : X**\n\n**Y**'


def test_html_to_markdown_drops_empty_bold():
    assert html_to_markdown('<p><b>​</b>★</p>') == '★'
    assert html_to_markdown('<p>a<b> </b>b<b>﻿ </b>c</p>') == 'a b c'
    # Zero-width characters are dropped from text.
    assert html_to_markdown('<p>A​B‌‍C</p>') == 'ABC'


def test_html_to_markdown_bold_across_line_breaks():
    # A bold run cannot span a blank line: one run per line (seminar 199).
    assert html_to_markdown('<p><b>- Presenter : Kim<br><br>- Topic :</b><b>Unfolding</b></p>') == (
        '**- Presenter : Kim**  \n  \n**- Topic :Unfolding**')

