from netwatch.cli import build_parser, main


def test_parser_rejects_invalid_port():
    import pytest
    from argparse import ArgumentTypeError
    with pytest.raises(SystemExit):
        build_parser().parse_args(["check", "--host", "localhost", "--port", "70000"])


def test_report_command(tmp_path, capsys):
    import csv
    from netwatch.logger import FIELDS
    path = tmp_path / "log.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerow(FIELDS)
    assert main(["report", "--log", str(path)]) == 0
    assert "Total attempts : 0" in capsys.readouterr().out
