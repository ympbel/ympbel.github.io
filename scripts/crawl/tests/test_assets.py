from crawl.assets import local_path_for_site_asset, site_asset_urls
from crawl.config import BASE_URL


def test_site_asset_urls_resolves_relative():
    html = '<p><img src="../images/main/slogan.png"></p>'
    css = (BASE_URL + '/css/design.css', '.next { background: url(../img/btn_next.gif) no-repeat; }')
    assert site_asset_urls([html], [css]) == {
        BASE_URL + '/images/main/slogan.png',
        BASE_URL + '/img/btn_next.gif',
    }


def test_css_refs_resolve_against_stylesheet_url():
    css = (BASE_URL + '/skin/board/Student/css/style.css', 'dt { background: url(../img/ico_sq.gif); }')
    assert site_asset_urls([], [css]) == {BASE_URL + '/skin/board/Student/img/ico_sq.gif'}


def test_site_asset_urls_skips_unmapped_paths():
    html = '<img src="http://mpbel.yonsei.ac.kr/plugin/kcaptcha/img/dot.gif"><img src="/images/a.png?ver=1">'
    css = (BASE_URL + '/css/default.css', 'a { background: url("/data/x.png") } b { background: url(https://fonts.example/x.png) }')
    assert site_asset_urls([html], [css]) == {BASE_URL + '/images/a.png'}


def test_local_path_for_site_asset():
    assert local_path_for_site_asset(BASE_URL + '/images/main/slogan.png') == '/images/site/main/slogan.png'
    assert local_path_for_site_asset(BASE_URL + '/img/btn_next.gif') == '/images/site/img/btn_next.gif'


def test_local_path_for_skin_asset():
    assert local_path_for_site_asset(BASE_URL + '/skin/board/Student/img/ico_sq.gif') == '/images/site/skin/Student/ico_sq.gif'
    assert local_path_for_site_asset(BASE_URL + '/skin/latest/basic/img/new.gif') == '/images/site/skin/latest-basic/new.gif'
    assert local_path_for_site_asset(BASE_URL + '/plugin/x.png') is None
