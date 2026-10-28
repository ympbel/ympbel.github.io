from crawl.assets import local_path_for_site_asset, site_asset_urls
from crawl.config import BASE_URL


def test_site_asset_urls_resolves_relative():
    html = '<p><img src="../images/main/slogan.png"></p>'
    css = '.next { background: url(../img/btn_next.gif) no-repeat; }'
    assert site_asset_urls([html], [css]) == {
        BASE_URL + '/images/main/slogan.png',
        BASE_URL + '/img/btn_next.gif',
    }


def test_local_path_for_site_asset():
    assert local_path_for_site_asset(BASE_URL + '/images/main/slogan.png') == '/images/site/main/slogan.png'
    assert local_path_for_site_asset(BASE_URL + '/img/btn_next.gif') == '/images/site/img/btn_next.gif'
