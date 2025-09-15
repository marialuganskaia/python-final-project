from __future__ import annotations
import json, pytest
from src.logscoper.cli import main


@pytest.mark.parametrize(
    "bucket, expect_keys",
    [
        (100, {"100-200", "200-300"}),  # 199ms -> 100-200, 200ms -> 200-300
        (200, {"0-200", "200-400"}),
        (1000, {"0-1000"}),  # всё в одну корзину на маленьком логе
    ],
)
def test_hist_buckets(boundary_log, capsys, bucket, expect_keys):
    assert main(["hist", "--path", str(boundary_log), "--bucket-ms", str(bucket), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert set(data.keys()) == expect_keys


def test_hist_subset_by_regex(sample_log, capsys):
    assert main(["hist", "--path", str(sample_log), "--bucket-ms", "200", "--grep", "^/boom", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data == {"800-1000": 1}


def test_hist_text_contains_ranges(sample_log, capsys):
    assert main(["hist", "--path", str(sample_log), "--bucket-ms", "200"]) == 0
    out = capsys.readouterr().out
    assert "0-200" in out
    assert "800-1000" in out or "800-1000" in out.replace(" ", "")


def test_hist_large_bucket(sample_log, capsys):
    assert main(["hist", "--path", str(sample_log), "--bucket-ms", "1000", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data == {"0-1000": 5}


def test_hist_no_rt_non_strict(no_rt_log):
    assert main(["hist", "--path", str(no_rt_log), "--bucket-ms", "200"]) == 0
