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
def local_server():
    """Loopback server; yields (base_url, hits). /moved answers 302 -> /target (like the old
    site's 302 to an off-site 404 page); every other path answers 200 'fresh <path>'."""
    hits: dict[str, int] = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            hits[self.path] = hits.get(self.path, 0) + 1
            if self.path == '/moved':
                self.send_response(302)
                self.send_header('Location', '/target')
                self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(f'fresh {self.path}'.encode())

    server = HTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.05}, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}', hits
    server.shutdown()
    server.server_close()


def test_redirects_are_not_followed(tmp_path, local_server):
    base, _ = local_server
    fetcher = Fetcher(tmp_path, delay=0)
    with pytest.raises(urllib.error.HTTPError) as excinfo:
        fetcher.get_bytes(base + '/moved')
    assert excinfo.value.code == 302
    assert not (tmp_path / cache_name(base + '/moved')).exists()
    assert fetcher.resolve_redirect(base + '/moved') == base + '/target'
    assert Fetcher(tmp_path, offline=True).resolve_redirect(base + '/moved') == base + '/target'


def test_get_refresh_bypasses_cache(tmp_path, local_server):
    base, hits = local_server
    url = base + '/list?page=1'
    cache_file = tmp_path / cache_name(url)
    cache_file.write_text('stale list', encoding='utf-8')
    fetcher = Fetcher(tmp_path, delay=0)

    assert fetcher.get(url) == 'stale list'
    assert hits.get('/list?page=1', 0) == 0

    assert fetcher.get(url, refresh=True) == 'fresh /list?page=1'
    assert cache_file.read_text(encoding='utf-8') == 'fresh /list?page=1'
    assert hits['/list?page=1'] == 1

    assert fetcher.get_bytes(url, refresh=True) == b'fresh /list?page=1'
    assert hits['/list?page=1'] == 2

    offline = Fetcher(tmp_path, offline=True)
    assert offline.get(url, refresh=True) == 'fresh /list?page=1'
    with pytest.raises(FileNotFoundError):
        offline.get(base + '/never-cached', refresh=True)
    assert hits['/list?page=1'] == 2
