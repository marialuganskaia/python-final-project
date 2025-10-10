from __future__ import annotations
import argparse
import sys
from typing import Optional
from ..adapters.parser import read_log_file
from ..commands.filter import filter_log_entries


def cmd_stats(args: argparse.Namespace) -> int:
    from ..models.calculations import calculate_stats
    from ..commands.stats import stats_to_txt, stats_to_json

    all_log_entries = read_log_file(args.path)
    filtered_log_entries = filter_log_entries(
        all_log_entries,
        since=args.since,
        until=args.until,
        status=args.status,
        grep=args.grep
    )

    stats = calculate_stats(filtered_log_entries, args.top)

    if args.json:
        print(stats_to_json(stats))
    else:
        print(stats_to_txt(stats))

    return 0


def cmd_filter(args: argparse.Namespace) -> int:
    from ..commands.filter import log_entries_to_txt

    all_log_entries = read_log_file(args.path)
    filtered_log_entries = filter_log_entries(
        all_log_entries,
        since=args.since,
        until=args.until,
        status=args.status,
        grep=args.grep
    )

    output_text = log_entries_to_txt(filtered_log_entries)

    if args.out:
        with open(args.out, 'w') as f:
            f.write(output_text + '\n')
    else:
        print(output_text)

    return 0


def cmd_hist(args: argparse.Namespace) -> int:
    from ..models.calculations import calculate_hist
    from ..commands.hist import hist_to_txt, hist_to_json

    all_log_entries = read_log_file(args.path)
    if args.strict:
        all_req_time = [log.request_time_s for log in all_log_entries if log.request_time_s is not None]
        if len(all_req_time) == 0:
            print("Error! No request time data found while --strict flag", file=sys.stderr)
            return 1

    filtered_log_entries = filter_log_entries(
        all_log_entries,
        since=args.since,
        until=args.until,
        status=args.status,
        grep=args.grep
    )

    hist = calculate_hist(filtered_log_entries, args.bucket_ms)

    if args.json:
        print(hist_to_json(hist))
    else:
        print(hist_to_txt(hist))

    return 0


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
    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(f"Error! File '{e.filename}' is not found", file=sys.stderr)
        return 2
    except ValueError:
        print("Error! Invalid date format", file=sys.stderr)
        sys.exit(1)
