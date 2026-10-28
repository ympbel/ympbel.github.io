from pathlib import Path

from crawl.parse_posts import PostRow, PostView, parse_post_list, parse_post_view, post_filename

FIXTURES = Path(__file__).resolve().parent / 'fixtures'


def fixture(name: str) -> str:
    return (FIXTURES / f'{name}.html').read_text(encoding='utf-8')


def view_html(title_tag, tit='', cate='', lec_date='', con='', files=''):
    cate_span = f'<span class="bo_v_cate">{cate}</span>' if cate else ''
    lec = f'<div class="lec_date">{lec_date}</div>' if lec_date else ''
    return (f'<html><head><title>{title_tag}</title></head><body><article id="bo_v"><header>'
            f'<h2 id="bo_v_title">{cate_span}<span class="bo_v_tit">{tit}</span></h2>{lec}</header>'
            '<section id="bo_v_info"><strong class="if_date"><span class="sound_only">작성일</span>'
            f' 24-03-05 09:10</strong></section><section id="bo_v_file">{files}</section>'
            f'<section id="bo_v_atc"><div id="bo_v_con">{con}</div></section></article></body></html>')


def test_parse_news_list_rows():
    rows = parse_post_list(fixture('sub6_1_p1'))
    assert rows[0] == PostRow(5, '연구실소식', True)
    assert rows[1] == PostRow(92, '2025', False)


def test_pinned_row_deduplicated():
    rows = parse_post_list(fixture('sub6_1_p1')) + parse_post_list(fixture('sub6_1_p2'))
    deduped = list({r.wr_id: r for r in rows}.values())
    assert [r.wr_id for r in deduped].count(5) == 1
    assert len(deduped) >= 30


def test_lecture_list_rows_have_no_category():
    assert parse_post_list(fixture('sub5_1')) == [PostRow(1, None, True), PostRow(2, None, False)]


def test_seminar_view():
    v = parse_post_view(fixture('view_sub6_3_471'))
    assert v.title.endswith('Carbon Ion Radiotherapy')
    assert v.title == ('2025/12/29 [Research Seminar] Group Sparse Algorithm for RBE-Weighted Dose '
                       'Optimization in Carbon Ion Radiotherapy')
    assert v.date == '2025-12-31'
    assert v.category == '2025'
    assert v.presenter == '이혜진'
    assert v.event_date == '2025-12-29'
    assert v.image_paths == ['/data/editor/2512/9d39b5b8da291607cba002ff2d25bc82_1767148425_8757.png']
    assert '<img' not in v.body_html
    assert v.body_html == '<p>Presenter: 이혜진\xa0</p>'  # the image's paragraph is gone
    assert v.files == []


def test_title_from_title_tag_with_separators():
    html = view_html('Why A &gt; B | matters &gt; News | MPBEL | x', tit='Why A &gt; B | mat…')
    assert parse_post_view(html).title == 'Why A > B | matters'


def test_news_view_keeps_text():
    v = parse_post_view(fixture('view_sub6_1_92'))
    assert 'Congratulations to Dong Min Jung!' in v.body_html
    assert len(v.image_paths) == 2
    assert all(p.startswith('/data/editor/2510/') for p in v.image_paths)
    assert not any('thumb-' in p for p in v.image_paths)
    assert (v.title, v.date, v.category, v.presenter, v.event_date) == (
        '2025 KOSRO Autumn Conference Award !!', '2025-10-22', '2025', None, None)


def test_lecture_view():
    v = parse_post_view(fixture('view_sub5_1_1'))
    assert v.event_date == '2018-09-01'
    assert v.title == '[2학기] 의료영상개론'
    assert v.date == '2018-04-19'
    assert v.category is None
    assert v.image_paths == []


def test_view_bare_image_files_and_dotted_lec_date():
    con = ('<p>Intro&nbsp;text</p><p><img src="../data/editor/1904/a.jpg" alt=""></p><p>&nbsp;<br></p>'
           '<p><iframe src="https://www.youtube.com/embed/x"></iframe></p>')
    files = ('<a class="view_file_download" href="http://mpbel.yonsei.ac.kr/bbs/download.php?bo_table=sub5_1'
             '&amp;wr_id=3&amp;no=0"><strong>syllabus.pdf</strong> (10K)</a>')
    v = parse_post_view(view_html('Course &gt; Lecture | MPBEL | x', tit='Course', lec_date='강의날짜 : 2018.4.9',
                                  con=con, files=files))
    assert v.image_paths == ['/data/editor/1904/a.jpg']
    assert v.body_html == '<p>Intro\xa0text</p><p><iframe src="https://www.youtube.com/embed/x"></iframe></p>'
    assert v.files == [('syllabus.pdf', '/bbs/download.php?bo_table=sub5_1&wr_id=3&no=0')]
    assert (v.category, v.event_date, v.date) == (None, '2018-04-09', '2024-03-05')


def test_view_images_on_other_hosts():
    """The former domain ympbe.yonsei.ac.kr serves the same /data/ files: a host-less path. An image
    on any other host (a post copied from another site) keeps its URL; a relative `fn` is on the
    host of its view_image.php link."""
    con = ('<p><a class="view_image" href="http://mpbel.yonsei.ac.kr/bbs/view_image.php?fn=http%3A%2F%2Fympbe.yonsei.ac.kr'
           '%2Fdata%2Feditor%2F1804%2Fa.JPG"><img src="http://ympbe.yonsei.ac.kr/data/editor/1804/thumb-a_800x600.jpg"></a></p>'
           '<p><img src="http://smart.yonsei.ac.kr/data/editor/2105/b.png"></p>'
           '<p><a class="view_image" href="http://smart.yonsei.ac.kr/bbs/view_image.php?fn=%2Fdata%2Feditor%2F2105%2Fc.png">'
           '<img src="http://smart.yonsei.ac.kr/data/editor/2105/thumb-c_600x900.png"></a></p>'
           '<p><img src="https://ci3.googleusercontent.com/proxy/x=s0-d-e1-ft"></p>')
    v = parse_post_view(view_html('News &gt; News | MPBEL | x', con=con))
    assert v.image_paths == ['/data/editor/1804/a.JPG', 'http://smart.yonsei.ac.kr/data/editor/2105/b.png',
                             'http://smart.yonsei.ac.kr/data/editor/2105/c.png',
                             'https://ci3.googleusercontent.com/proxy/x=s0-d-e1-ft']
    assert v.body_html == ''


def test_presenter_label_in_any_case():
    v = parse_post_view(view_html('2025/04/21 [Research Seminar] X &gt; Seminar | MPBEL | x',
                                  con='<p>presenter: 이석호</p><p>Abstract</p>'))
    assert (v.presenter, v.event_date) == ('이석호', '2025-04-21')


def test_post_filename():
    v = PostView('t', '2025-12-31', None, '', [], [], None, None)
    assert post_filename(v, 471) == '2025-12-31-471.md'
