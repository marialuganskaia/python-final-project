from __future__ import annotations
import pytest
from src.logscoper.infra.cli import main
from .conftest import collect_lines
import re

STATUS_CASES = [
    ("200", {"200"}),
    ("200,404", {"200", "404"}),
    (" 200 , 404 ", {"200", "404"}),  # пробелы
    ("2xx", {"200"}),  # мягкая проверка: найдём хотя бы один 2xx
    ("5xx,404", {"404", "500"}),  # микс классов и точных
]


@pytest.mark.parametrize("selector, expect_subset", STATUS_CASES)
def test_filter_status_param(selector, status_log, capsys, expect_subset):
    assert main(["filter", "--path", str(status_log), "--status", selector]) == 0
    lines = collect_lines(capsys)
    found_codes = set(
        tok for ln in lines for tok in ln.split() if tok.isdigit() and len(tok) == 3
    )
    assert expect_subset.issubset(found_codes)


def test_filter_5xx_on_sample(sample_log, capsys):
    assert main(["filter", "--path", str(sample_log), "--status", "5xx"]) == 0
    lines = collect_lines(capsys)
    assert len(lines) == 1 and " /boom " in lines[0] and " 500 " in lines[0]


REGEX_CASES = [
    (r"^/api/", 2, ["/api/v1/users", "/api/v1/Users"]),  # якорь ^
    (r"/api/v1/users\?sort=asc$", 1, ["/api/v1/users?sort=asc"]),  # экранирование ? и $
    (r"\.html$", 1, ["/dots.v1.2/index.html"]),  # конец строки
    (r"\.v1\.2/", 1, ["/dots.v1.2/index.html"]),  # экранирование точки
    (r"regex\-specials\.\^\$\+\*\?\[\]\(\)\{\}\|", 1, ["/regex-specials.^$+*?[](){}|"]),
    (r"spaces and tabs", 1, ["/spaces and tabs"]),
]


@pytest.mark.parametrize("pattern, expected_count, must_contain", REGEX_CASES)
def test_filter_regex_edges(
    regex_edge_log, capsys, pattern, expected_count, must_contain
):
    assert main(["filter", "--path", str(regex_edge_log), "--grep", pattern]) == 0
    lines = collect_lines(capsys)
    assert len(lines) == expected_count
    joined = "\n".join(lines)
    for frag in must_contain:
        assert re.search(rf"\s{re.escape(frag)}(\s|\?|$)", joined)


TIME_CASES = [
    ("2000-10-10T13:59:59+00:00", None, 3),  # включает первую
    ("2000-10-10T14:00:00+00:00", None, 2),  # включает вторую и третью
    (None, "2000-10-10T14:00:00+00:00", 1),  # исключает вторую ровно на until
    ("2000-10-10T14:00:01", None, 1),  # по-тупому -> UTC
    (None, "2000-10-10T14:00:01", 2),  # по-тупому -> UTC
]


@pytest.mark.parametrize("since, until, expected_total", TIME_CASES)
def test_filter_time(boundary_tz_log, capsys, since, until, expected_total):
    args = ["filter", "--path", str(boundary_tz_log)]
    if since:
        args += ["--since", since]
    if until:
        args += ["--until", until]
    assert main(args) == 0
    lines = collect_lines(capsys)
    assert len(lines) == expected_total


def test_filter_bytes_dash_and_rt(sample_log, capsys):
    assert main(["filter", "--path", str(sample_log), "--grep", "^/index"]) == 0
    line = collect_lines(capsys)[0]
    assert (
        line.endswith(" - rt=0.12")
        or line.endswith(" - rt=0.120")
        or " - rt=0.12" in line
    )


def test_filter_out_file(sample_log, tmp_path, capsys):
    out_file = tmp_path / "filtered.txt"
    assert (
        main(
            [
                "filter",
                "--path",
                str(sample_log),
                "--status",
                "5xx",
                "--out",
                str(out_file),
            ]
        )
        == 0
    )
    # stdout пустой
    assert capsys.readouterr().out.strip() == ""
    content = out_file.read_text().strip()
    assert "/boom" in content and " 500 " in content
