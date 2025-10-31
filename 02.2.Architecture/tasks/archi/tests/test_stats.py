from __future__ import annotations
import json
from ..src.logscoper.infra.cli import main


def test_stats_text(sample_log, capsys):
    assert main(["stats", "--path", str(sample_log), "--top", "3"]) == 0
    out = capsys.readouterr().out
    assert "Total:" in out
    assert "By status:" in out
    assert "Avg RT (ms):" in out
    assert "P95 RT (ms):" in out
    assert "P99 RT (ms):" in out
    assert "Top paths:" in out
    assert "200: 3" in out
    assert "/index.html" in out and "/style.css" in out and "/login" in out


def test_stats_json(sample_log, capsys):
    assert main(["stats", "--path", str(sample_log), "--top", "2", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 5
    assert (
        data["status"]["200"] == 3
        and data["status"]["302"] == 1
        and data["status"]["500"] == 1
    )
    assert isinstance(data["rt_p95_ms"], (int, float))
    assert isinstance(data["rt_p99_ms"], (int, float))
    assert isinstance(data["rt_avg_ms"], (int, float))
    assert len(data["top_paths"]) == 2
    assert isinstance(data["top_paths"][0][0], str) and isinstance(
        data["top_paths"][0][1], int
    )


def test_stats_filters_since_until_status_grep(sample_log, capsys):
    assert (
        main(
            [
                "stats",
                "--path",
                str(sample_log),
                "--since",
                "2000-10-10T13:55:39+00:00",
                "--status",
                "5xx",
                "--grep",
                "^/boom",
                "--json",
            ]
        )
        == 0
    )
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 1 and data["status"]["500"] == 1
    assert data["top_paths"] == [["/boom", 1]]


def test_stats_empty_after_filters(sample_log, capsys):
    assert (
        main(
            [
                "stats",
                "--path",
                str(sample_log),
                "--since",
                "2099-01-01T00:00:00+00:00",
                "--json",
            ]
        )
        == 0
    )
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 0
    assert data["status"] == {}
    assert data["top_paths"] == []
    assert (
        data["rt_avg_ms"] is None
        and data["rt_p95_ms"] is None
        and data["rt_p99_ms"] is None
    )


def test_stats_text_rounding(tmp_path, capsys):
    log = tmp_path / "round.log"
    log.write_text(
        """\
8.8.8.8 - - [10/Oct/2000:12:00:00 +0000] "GET /a HTTP/1.1" 200 1 "-" "UA" 0.100
8.8.8.8 - - [10/Oct/2000:12:00:01 +0000] "GET /b HTTP/1.1" 200 1 "-" "UA" 0.200
"""
    )
    assert main(["stats", "--path", str(log)]) == 0
    out = capsys.readouterr().out
    assert "Avg RT (ms): 150.00" in out


def test_stats_naive_iso_treated_as_utc(sample_log, capsys):
    assert (
        main(
            [
                "stats",
                "--path",
                str(sample_log),
                "--since",
                "2000-10-10T13:55:39",
                "--json",
            ]
        )
        == 0
    )  # без TZ
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 2
    assert data["status"]["200"] == 1
    assert data["status"]["500"] == 1


def test_stats_status_sorted_keys(status_log, capsys):
    assert main(["stats", "--path", str(status_log), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert list(data["status"].keys()) == ["200", "201", "302", "404", "500"]


def test_stats_top_n_and_percentiles(freq_log, capsys):
    assert main(["stats", "--path", str(freq_log), "--json", "--top", "2"]) == 0
    data = json.loads(capsys.readouterr().out)
    tp = data["top_paths"]
    assert tp[0][0] == "/a" and tp[0][1] == 3
    assert tp[1][0] == "/b" and tp[1][1] == 2
    # монотонность процентили
    if data["rt_p95_ms"] is not None and data["rt_p99_ms"] is not None:
        assert data["rt_p99_ms"] >= data["rt_p95_ms"]


def test_stats_rt_kv_and_trailing_float(rt_kv_mixed_log, capsys):
    assert main(["stats", "--path", str(rt_kv_mixed_log), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert abs(data["rt_avg_ms"] - 200.0) < 1e-6


def test_stats_big_log_sanity(tmp_path, capsys):
    # лёгкая проверка на большом объёме (2000 строк)
    random = __import__("random")
    base = dt = __import__("datetime").datetime(2000, 10, 10, 10, 0, 0)
    paths = [
        "/",
        "/api",
        "/api/items",
        "/login",
        "/search",
        "/health",
        "/static/app.js",
    ]
    statuses = [200, 200, 200, 201, 301, 302, 404, 500]
    lines = []
    for i in range(2000):
        ts = (base + __import__("datetime").timedelta(seconds=i)).strftime(
            "%d/%b/%Y:%H:%M:%S +0000"
        )
        path = random.choice(paths)
        st = random.choice(statuses)
        rt = f"{random.random():.3f}"
        lines.append(
            f'10.0.0.{i % 255} - - [{ts}] "GET {path} HTTP/1.1" {st} {random.randint(0, 999)} "-" "UA" {rt}'
        )
    p = tmp_path / "big.log"
    p.write_text("\n".join(lines) + "\n")

    assert main(["stats", "--path", str(p), "--json", "--top", "5"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 2000
    assert isinstance(data["status"], dict)
    assert len(data["top_paths"]) <= 5
    assert (data["rt_avg_ms"] is None) or isinstance(data["rt_avg_ms"], (int, float))
