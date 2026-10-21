import csv
from netwatch.logger import FIELDS, append_result
from netwatch.models import CheckResult
from netwatch.reports import build_report, format_report


def test_report_with_success_and_failure(tmp_path):
    path = tmp_path / "monitor.csv"
    append_result(path, CheckResult("t1", "a", "1.1.1.1", 443, "SUCCESS", 10.0))
    append_result(path, CheckResult("t2", "b", "", 443, "TIMEOUT", None, "timeout"))
    append_result(path, CheckResult("t3", "c", "1.1.1.2", 443, "SUCCESS", 20.0))
    report = build_report(path)
    assert report["total_attempts"] == 3
    assert report["successes"] == 2
    assert report["failures"] == 1
    assert report["success_rate_pct"] == 66.67
    assert report["latency_avg_ms"] == 15.0
    assert "Latency avg" in format_report(report)


def test_empty_report(tmp_path):
    path = tmp_path / "empty.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerow(FIELDS)
    report = build_report(path)
    assert report["total_attempts"] == 0
    assert report["latency_avg_ms"] is None
    assert "no successful connections" in format_report(report)
