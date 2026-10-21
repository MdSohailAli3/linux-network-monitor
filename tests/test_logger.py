import csv
from netwatch.logger import FIELDS, append_result
from netwatch.models import CheckResult


def test_csv_header_and_rows(tmp_path):
    path = tmp_path / "nested" / "log.csv"
    result = CheckResult("2026-01-01T00:00:00+00:00", "localhost", "127.0.0.1", 443, "SUCCESS", 1.25)
    append_result(path, result)
    append_result(path, result)
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["status"] == "SUCCESS"
    assert rows[0]["latency_ms"] == "1.25"
    with path.open(newline="", encoding="utf-8") as handle:
        assert next(csv.reader(handle)) == FIELDS
