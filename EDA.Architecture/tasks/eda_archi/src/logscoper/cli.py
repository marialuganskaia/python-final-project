from __future__ import annotations
import argparse
import json
import sys
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Iterable, Iterator, Pattern
from collections import Counter
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class LogEntry:
    ip: str
    ts: datetime
    method: str
    path: str
    status: int
    bytes_sent: Optional[int]
    request_time_s: Optional[float]


# =====================
# Регулярки
# =====================

LOG_RE = re.compile(
    r"(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<ts>[^\]]+)\]\s+"
    r'"(?P<method>[A-Z]+)\s+(?P<path>.*?)(?:\s+HTTP/\d\.\d)?"\s+'
    r"(?P<status>\d{3})\s+(?P<bytes>\S+)"
    r'(?:\s+"[^"]*"\s+"[^"]*")?'
    r"(?:\s+(?P<rt>\d+\.\d+)|\s+rt=(?P<rt_kv>\d+\.\d+))?"
)

RT_KV_RE = re.compile(r"(?:^|\s)rt=(?P<rt>\d+\.\d+)\b")


def _parse_ts(ts_raw: str) -> datetime:
    return datetime.strptime(ts_raw, "%d/%b/%Y:%H:%M:%S %z").astimezone(timezone.utc)


def parse_line(line: str) -> Optional[LogEntry]:
    m = LOG_RE.search(line)
    if not m:
        return None
    gd = m.groupdict()
    try:
        ts = _parse_ts(gd["ts"])
    except Exception:
        return None

    if gd["bytes"] == "-":
        bytes_sent = None
    else:
        try:
            bytes_sent = int(gd["bytes"])
        except ValueError:
            bytes_sent = None

    rt = None
    srt = gd.get("rt") or gd.get("rt_kv")
    if srt:
        try:
            rt = float(srt)
        except ValueError:
            rt = None

    return LogEntry(
        ip=gd["ip"],
        ts=ts,
        method=gd["method"],
        path=gd["path"],
        status=int(gd["status"]),
        bytes_sent=bytes_sent,
        request_time_s=rt,
    )


def read_lines(path: str | Path) -> Iterable[str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    with p.open("rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            yield line.rstrip("\n")


def _iter_entries(path: str) -> Iterator[LogEntry]:
    for line in read_lines(path):
        e = parse_line(line)
        if e:
            yield e


def _status_matches(code: int, selector: Optional[str]) -> bool:
    if selector is None:
        return True
    filters = [part.strip().lower() for part in selector.split(",") if part.strip()]
    for f in filters:
        if len(f) == 3 and f.endswith("xx") and f[0].isdigit():
            base = int(f[0]) * 100
            if base <= code < base + 100:
                return True
        else:
            try:
                if int(f) == code:
                    return True
            except ValueError:
                continue
    return False


def apply_filters(
    entries: Iterable[LogEntry],
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    status: Optional[str] = None,
    grep: Optional[str] = None,
) -> Iterator[LogEntry]:
    regex: Optional[Pattern[str]] = re.compile(grep) if grep else None
    for e in entries:
        if since and e.ts < since:
            continue
        if until and e.ts >= until:
            continue
        if not _status_matches(e.status, status):
            continue
        if regex and not regex.search(e.path):
            continue
        yield e


def cast_to_percentile(values: list[float], p: float) -> Optional[float]:
    if not values:
        return None
    values = sorted(values)
    k = (len(values) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values[int(k)]
    return values[f] * (c - k) + values[c] * (k - f)


def collect_request_times_ms(entries: Iterable[LogEntry]) -> list[float]:
    return [e.request_time_s * 1000.0 for e in entries if e.request_time_s is not None]


def histogram_ms(values_ms: Iterable[float], bucket_ms: int) -> dict[str, int]:
    buckets: dict[str, int] = {}
    for v in values_ms:
        b = int(v // bucket_ms) * bucket_ms
        key = f"{b}-{b + bucket_ms}"
        buckets[key] = buckets.get(key, 0) + 1
    return dict(sorted(buckets.items(), key=lambda kv: int(kv[0].split("-")[0])))


def cast_to_aggregate(entries: Iterable[LogEntry]) -> dict[str, object]:
    total = 0
    by_status: Counter[int] = Counter()
    by_path: Counter[str] = Counter()
    rts_ms: list[float] = []
    for e in entries:
        total += 1
        by_status[e.status] += 1
        by_path[e.path] += 1
        if e.request_time_s is not None:
            rts_ms.append(e.request_time_s * 1000.0)
    avg_ms = sum(rts_ms) / len(rts_ms) if rts_ms else None
    p95 = cast_to_percentile(rts_ms, 95.0)
    p99 = cast_to_percentile(rts_ms, 99.0)
    return {
        "total": total,
        "status": dict(sorted(by_status.items())),
        "top_paths": by_path.most_common(),
        "rt_avg_ms": avg_ms,
        "rt_p95_ms": p95,
        "rt_p99_ms": p99,
    }


def _parse_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as e:
        raise SystemExit(f"Invalid datetime: {s}") from e
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _fmt_num(x: Optional[float]) -> str:
    return f"{x:.2f}" if x is not None else "n/a"


def cmd_stats(args: argparse.Namespace) -> int:
    since = _parse_iso(args.since)
    until = _parse_iso(args.until)
    entries = apply_filters(
        _iter_entries(args.path), since, until, args.status, args.grep
    )
    data = cast_to_aggregate(entries)
    top_n = args.top or 10
    if args.json:
        ser = dict(data)
        ser["status"] = {str(k): v for k, v in ser["status"].items()}  # type: ignore
        ser["top_paths"] = [[p, n] for p, n in data["top_paths"][:top_n]]  # type: ignore
        print(json.dumps(ser, indent=2, ensure_ascii=False))
    else:
        print(f"Total: {data['total']}")
        print("By status:")
        for k, v in data["status"].items():  # type: ignore
            print(f"  {k}: {v}")
        print(f"Avg RT (ms): {_fmt_num(data['rt_avg_ms'])}")  # type: ignore
        print(f"P95 RT (ms): {_fmt_num(data['rt_p95_ms'])}")  # type: ignore
        print(f"P99 RT (ms): {_fmt_num(data['rt_p99_ms'])}")  # type: ignore
        print("Top paths:")
        for path, cnt in data["top_paths"][:top_n]:  # type: ignore
            print(f"{cnt:>7}  {path}")
    return 0


def cmd_filter(args: argparse.Namespace) -> int:
    since = _parse_iso(args.since)
    until = _parse_iso(args.until)
    entries = apply_filters(
        _iter_entries(args.path), since, until, args.status, args.grep
    )
    out = sys.stdout
    if args.out:
        out = open(args.out, "w", encoding="utf-8")
    try:
        for e in entries:
            bytes_str = str(e.bytes_sent) if e.bytes_sent is not None else "-"
            rt_str = "" if e.request_time_s is None else f" rt={e.request_time_s}"
            print(
                f"{e.ts.isoformat()} {e.ip} {e.method} {e.path} {e.status} {bytes_str}{rt_str}",
                file=out,
            )
    finally:
        if out is not sys.stdout:
            out.close()
    return 0


def cmd_hist(args: argparse.Namespace) -> int:
    since = _parse_iso(args.since)
    until = _parse_iso(args.until)
    entries = apply_filters(
        _iter_entries(args.path), since, until, args.status, args.grep
    )
    values = collect_request_times_ms(entries)
    if not values:
        print("No request_time data found.", file=sys.stderr)
        return 1 if args.strict else 0
    hist = histogram_ms(values, args.bucket_ms)
    if args.json:
        print(json.dumps(hist, indent=2, ensure_ascii=False))
    else:
        for k, v in hist.items():
            hashes = "#" * min(v, 60)
            print(f"{k:>12}: {hashes} {v}")
    return 0


# =====================
# CLI Bootstrap
# =====================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logscoper",
        description="Simple access log analyzer",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("stats", help="Show aggregated stats")
    ps.add_argument("--path", required=True)
    ps.add_argument("--top", type=int, default=10)
    ps.add_argument("--since")
    ps.add_argument("--until")
    ps.add_argument("--status")
    ps.add_argument("--grep")
    ps.add_argument("--json", action="store_true")
    ps.set_defaults(func=cmd_stats)

    pf = sub.add_parser("filter", help="Filter and print normalized lines")
    pf.add_argument("--path", required=True)
    pf.add_argument("--since")
    pf.add_argument("--until")
    pf.add_argument("--status")
    pf.add_argument("--grep")
    pf.add_argument("--out")
    pf.set_defaults(func=cmd_filter)

    ph = sub.add_parser("hist", help="Request time histogram")
    ph.add_argument("--path", required=True)
    ph.add_argument("--bucket-ms", type=int, default=100, dest="bucket_ms")
    ph.add_argument("--since")
    ph.add_argument("--until")
    ph.add_argument("--status")
    ph.add_argument("--grep")
    ph.add_argument("--json", action="store_true")
    ph.add_argument("--strict", action="store_true")
    ph.set_defaults(func=cmd_hist)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        return args.func(args)
    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
