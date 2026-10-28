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
