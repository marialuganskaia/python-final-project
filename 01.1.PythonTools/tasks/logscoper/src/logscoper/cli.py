from __future__ import annotations
import argparse
import sys
from typing import Optional
import re


LOG_RE = re.compile(
    r'(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<ts>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<path>.*?)(?:\s+HTTP/\d\.\d)?"\s+'
    r'(?P<status>\d{3})\s+(?P<bytes>\S+)'
    r'(?:\s+"[^"]*"\s+"[^"]*")?'
    r'(?:\s+(?P<rt>\d+\.\d+)|\s+rt=(?P<rt_kv>\d+\.\d+))?'
)


RT_KV_RE = re.compile(r'(?:^|\s)rt=(?P<rt>\d+\.\d+)\b')


def cmd_stats(args: argparse.Namespace) -> int:
    # TODO: реализовать статистику по логу
    print("stats not implemented yet", file=sys.stderr)
    return 1


def cmd_filter(args: argparse.Namespace) -> int:
    # TODO: реализовать фильтрацию логов
    print("filter not implemented yet", file=sys.stderr)
    return 1


def cmd_hist(args: argparse.Namespace) -> int:
    # TODO: реализовать построение гистограммы
    print("hist not implemented yet", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logscoper",
        description="Simple access log analyzer",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # stats
    ps = sub.add_parser("stats", help="Show aggregated stats")
    ps.add_argument("--path", required=True)
    ps.add_argument("--top", type=int, default=10)
    ps.add_argument("--since")
    ps.add_argument("--until")
    ps.add_argument("--status")
    ps.add_argument("--grep")
    ps.add_argument("--json", action="store_true")
    ps.set_defaults(func=cmd_stats)

    # filter
    pf = sub.add_parser("filter", help="Filter and print normalized lines")
    pf.add_argument("--path", required=True)
    pf.add_argument("--since")
    pf.add_argument("--until")
    pf.add_argument("--status")
    pf.add_argument("--grep")
    pf.add_argument("--out")
    pf.set_defaults(func=cmd_filter)

    # hist
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
    args = parser.parse_args(argv)
    return args.func(args)
