from __future__ import annotations
import re, pytest
from pathlib import Path
from src.logscoper.cli import main


def test_missing_file_returns_code(tmp_path: Path):
    missing = tmp_path / "nope.log"
    assert main(["stats", "--path", str(missing)]) == 2


def test_invalid_datetime_raises_systemexit(sample_log):
    with pytest.raises(SystemExit):
        main(["filter", "--path", str(sample_log), "--since", "not-a-datetime"])


def test_invalid_regex_raises(regex_edge_log):
    with pytest.raises(re.error):
        main(["filter", "--path", str(regex_edge_log), "--grep", r"([unclosed"])


def test_hist_strict_exits_on_no_rt(no_rt_log):
    assert (
        main(["hist", "--path", str(no_rt_log), "--bucket-ms", "200", "--strict"]) != 0
    )
