from crawl.config import BOARDS, board_url


def test_all_boards_unique_tables():
    tables = [spec.table for spec in BOARDS]
    assert len(BOARDS) == 18
    assert len(set(tables)) == 18


def test_board_url_encodes_params():
    url = board_url('sub6_1', sca='연구실소식', page=2)
    assert url.endswith('bo_table=sub6_1&sca=%EC%97%B0%EA%B5%AC%EC%8B%A4%EC%86%8C%EC%8B%9D&page=2')
