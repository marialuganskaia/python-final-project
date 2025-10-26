from __future__ import annotations
from pathlib import Path
import textwrap
import pytest


@pytest.fixture
def sample_log(tmp_path: Path) -> Path:
    content = textwrap.dedent(
        """\
        127.0.0.1 - - [10/Oct/2000:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 - "-" "UA" 0.120
        127.0.0.1 - - [10/Oct/2000:13:55:37 +0000] "GET /style.css HTTP/1.1" 200 123 "-" "UA" 0.050
        127.0.0.1 - - [10/Oct/2000:13:55:38 +0000] "POST /login HTTP/1.1" 302 0 "-" "UA" 0.200
        127.0.0.1 - - [10/Oct/2000:13:55:39 +0000] "GET /dashboard HTTP/1.1" 200 800 "-" "UA" 0.400
        127.0.0.1 - - [10/Oct/2000:13:55:40 +0000] "GET /boom HTTP/1.1" 500 0 "-" "UA" 0.900
    """
    )
    p = tmp_path / "access.log"
    p.write_text(content)
    return p


@pytest.fixture
def no_rt_log(tmp_path: Path) -> Path:
    content = textwrap.dedent(
        """\
        127.0.0.1 - - [10/Oct/2000:13:55:36 +0000] "GET /a HTTP/1.1" 200 100 "-" "UA"
        127.0.0.1 - - [10/Oct/2000:13:55:37 +0000] "GET /b HTTP/1.1" 404 0 "-" "UA"
        127.0.0.1 - - [10/Oct/2000:13:55:38 +0000] "POST /c HTTP/1.1" 500 10 "-" "UA"
    """
    )
    p = tmp_path / "access_no_rt.log"
    p.write_text(content)
    return p


@pytest.fixture
def regex_edge_log(tmp_path: Path) -> Path:
    content = textwrap.dedent(
        """\
        1.1.1.1 - - [10/Oct/2000:09:00:00 +0000] "GET /dots.v1.2/index.html HTTP/1.1" 200 1 "-" "UA" 0.010
        1.1.1.1 - - [10/Oct/2000:09:00:01 +0000] "GET /api/v1/users?sort=asc HTTP/1.1" 200 1 "-" "UA" 0.020
        1.1.1.1 - - [10/Oct/2000:09:00:02 +0000] "GET /api/v1/Users HTTP/1.1" 404 1 "-" "UA" 0.030
        1.1.1.1 - - [10/Oct/2000:09:00:03 +0000] "GET /regex-specials.^$+*?[](){}| HTTP/1.1" 500 1 "-" "UA" 0.040
        1.1.1.1 - - [10/Oct/2000:09:00:04 +0000] "GET /spaces and tabs HTTP/1.1" 200 1 "-" "UA" 0.050
    """
    )
    p = tmp_path / "regex_edge.log"
    p.write_text(content)
    return p


@pytest.fixture
def status_log(tmp_path: Path) -> Path:
    content = textwrap.dedent(
        """\
        1.1.1.1 - - [10/Oct/2000:10:00:00 +0000] "GET /ok HTTP/1.1" 200 1 "-" "UA" 0.100
        1.1.1.1 - - [10/Oct/2000:10:00:01 +0000] "GET /ok2 HTTP/1.1" 201 1 "-" "UA" 0.110
        1.1.1.1 - - [10/Oct/2000:10:00:02 +0000] "GET /redir HTTP/1.1" 302 1 "-" "UA" 0.050
        1.1.1.1 - - [10/Oct/2000:10:00:03 +0000] "GET /notfound HTTP/1.1" 404 1 "-" "UA" 0.020
        1.1.1.1 - - [10/Oct/2000:10:00:04 +0000] "GET /boom HTTP/1.1" 500 1 "-" "UA" 0.900
    """
    )
    p = tmp_path / "status.log"
    p.write_text(content)
    return p


@pytest.fixture
def boundary_tz_log(tmp_path: Path) -> Path:
    content = textwrap.dedent(
        """\
        9.9.9.9 - - [10/Oct/2000:13:59:59 +0000] "GET /a HTTP/1.1" 200 1 "-" "UA" 0.100
        9.9.9.9 - - [10/Oct/2000:14:00:00 +0000] "GET /b HTTP/1.1" 404 1 "-" "UA" 0.200
        9.9.9.9 - - [10/Oct/2000:14:00:01 +0000] "GET /c HTTP/1.1" 500 1 "-" "UA" 0.300
    """
    )
    p = tmp_path / "boundary_tz.log"
    p.write_text(content)
    return p


@pytest.fixture
def freq_log(tmp_path: Path) -> Path:
    content = textwrap.dedent(
        """\
        1.1.1.1 - - [10/Oct/2000:10:00:00 +0000] "GET /a HTTP/1.1" 200 1 "-" "UA" 0.010
        1.1.1.1 - - [10/Oct/2000:10:00:01 +0000] "GET /a HTTP/1.1" 200 1 "-" "UA" 0.020
        1.1.1.1 - - [10/Oct/2000:10:00:02 +0000] "GET /a HTTP/1.1" 200 1 "-" "UA" 0.030
        1.1.1.1 - - [10/Oct/2000:10:00:03 +0000] "GET /b HTTP/1.1" 404 1 "-" "UA" 0.040
        1.1.1.1 - - [10/Oct/2000:10:00:04 +0000] "GET /b HTTP/1.1" 404 1 "-" "UA" 0.050
        1.1.1.1 - - [10/Oct/2000:10:00:05 +0000] "GET /c HTTP/1.1" 500 1 "-" "UA" 0.500
    """
    )
    p = tmp_path / "freq.log"
    p.write_text(content)
    return p


@pytest.fixture
def boundary_log(tmp_path: Path) -> Path:
    content = textwrap.dedent(
        """\
        3.3.3.3 - - [10/Oct/2000:10:20:00 +0000] "GET /t1 HTTP/1.1" 200 1 "-" "UA" 0.199
        3.3.3.3 - - [10/Oct/2000:10:20:01 +0000] "GET /t2 HTTP/1.1" 200 1 "-" "UA" 0.200
    """
    )
    p = tmp_path / "boundary.log"
    p.write_text(content)
    return p


@pytest.fixture
def rt_kv_mixed_log(tmp_path: Path) -> Path:
    content = textwrap.dedent(
        """\
        2.2.2.2 - - [10/Oct/2000:11:00:00 +0000] "GET /x HTTP/1.1" 200 1 "-" "UA" 0.150
        2.2.2.2 - - [10/Oct/2000:11:00:01 +0000] "GET /y HTTP/1.1" 200 1 "-" "UA" rt=0.250
        2.2.2.2 - - [10/Oct/2000:11:00:02 +0000] "GET /z HTTP/1.1" 200 1 "-" "UA"
    """
    )
    p = tmp_path / "rt_kv_mixed.log"
    p.write_text(content)
    return p


def collect_lines(capsys):
    return [l for l in capsys.readouterr().out.splitlines() if l.strip()]
