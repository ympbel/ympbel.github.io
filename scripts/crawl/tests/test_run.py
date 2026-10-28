import json
from datetime import datetime, timezone

from crawl.run import write_summary


def test_summary_json_written(tmp_path):
    path = tmp_path / 'reference' / 'crawl-summary.json'
    write_summary(path, {'seminars': {'written': 431, 'skipped': 0},
                         'assets': {'written': 0, 'skipped': 63}})

    data = json.loads(path.read_text(encoding='utf-8'))
    assert list(data) == ['assets', 'seminars', 'generated_at']
    assert data['assets'] == {'written': 0, 'skipped': 63}
    assert data['seminars'] == {'written': 431, 'skipped': 0}
    generated = datetime.fromisoformat(data['generated_at'])
    assert generated.utcoffset() == timezone.utc.utcoffset(None)
    assert abs((datetime.now(timezone.utc) - generated).total_seconds()) < 60
