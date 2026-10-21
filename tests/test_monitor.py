from netwatch.models import CheckResult, Target
from netwatch.monitor import run_monitor


def test_monitor_logs_each_target_each_cycle(tmp_path):
    path = tmp_path / "monitor.csv"
    calls = []
    def fake_check(target):
        calls.append(target)
        return CheckResult("t", target.host, "127.0.0.1", target.port, "SUCCESS", 1.0)
    run_monitor([Target("localhost", 80), Target("localhost", 443)], path, interval=0.01, check=fake_check, max_cycles=2)
    assert len(calls) == 4
    assert len(path.read_text().splitlines()) == 5  # header + four attempts


def test_monitor_rejects_empty_targets(tmp_path):
    import pytest
    with pytest.raises(ValueError, match="at least one target"):
        run_monitor([], tmp_path / "log.csv")
