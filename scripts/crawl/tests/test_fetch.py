import threading
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from crawl.fetch import Fetcher, cache_name


def test_cache_name():
    url = 'http://mpbel.yonsei.ac.kr/bbs/board.php?bo_table=sub6_3&page=2'
    assert cache_name(url) == 'bbs_board.php_bo_table=sub6_3&page=2.html'


def test_offline_reads_cache_and_misses_raise(tmp_path):
    url = 'http://mpbel.yonsei.ac.kr/bbs/board.php?bo_table=sub6_3&page=2'
    (tmp_path / cache_name(url)).write_text('<html>세미나</html>', encoding='utf-8')
    fetcher = Fetcher(tmp_path, offline=True)
    assert fetcher.get(url) == '<html>세미나</html>'
    with pytest.raises(FileNotFoundError):
        fetcher.get('http://mpbel.yonsei.ac.kr/bbs/board.php?bo_table=sub6_3&page=99')


@pytest.fixture
def redirect_server():
    """Local server: /moved answers 302 -> /target (like the old site's 302 to an off-site 404 page)."""
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            if self.path == '/moved':
                self.send_response(302)
                self.send_header('Location', '/target')
                self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'target page')

    server = HTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.05}, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}'
    server.shutdown()
    server.server_close()


def test_redirects_are_not_followed(tmp_path, redirect_server):
    fetcher = Fetcher(tmp_path, delay=0)
    with pytest.raises(urllib.error.HTTPError) as excinfo:
        fetcher.get_bytes(redirect_server + '/moved')
    assert excinfo.value.code == 302
    assert not (tmp_path / cache_name(redirect_server + '/moved')).exists()
    assert fetcher.resolve_redirect(redirect_server + '/moved') == redirect_server + '/target'
    assert Fetcher(tmp_path, offline=True).resolve_redirect(redirect_server + '/moved') == redirect_server + '/target'
