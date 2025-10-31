from __future__ import annotations
import pytest
from src.logscoper.infra.cli import main
from .conftest import collect_lines


def test_cli_help_prints_and_exits():
    with pytest.raises(SystemExit) as ei:
        main(["-h"])
    assert ei.value.code == 0


def test_stats_text_shape(sample_log, capsys):
    assert main(["stats", "--path", str(sample_log), "--top", "3"]) == 0
    out = capsys.readouterr().out
    for header in (
        "Total:",
        "By status:",
        "Avg RT (ms):",
        "P95 RT (ms):",
        "P99 RT (ms):",
        "Top paths:",
    ):
        assert header in out


def test_filter_line_shape(sample_log, capsys):
    assert main(["filter", "--path", str(sample_log), "--status", "200"]) == 0
    lines = collect_lines(capsys)
    first = lines[0].split()
    assert first[0].startswith("2000-10-10T13:55:")
    assert first[2] in ("GET", "POST")
    assert ("rt=" in lines[0]) or lines[0].endswith(" -")
