from __future__ import annotations
import argparse
import sys
from typing import Optional
import json
import re

# from Cython.Shadow import nonecheck

from .parser import filter_log_entries, read_log_file



def cmd_stats(args: argparse.Namespace) -> int:
    all_log_entries = read_log_file(args.path)
    # if all_log_entries is None:
    #     return 2
    filtered_log_entries = filter_log_entries(
        all_log_entries,
        since=args.since,
        until=args.until,
        status=args.status,
        grep=args.grep
    )
    if not filtered_log_entries:
        if args.json:
            print(
                '{"total": 0, "status": {}, "rt_avg_ms": null, "rt_p95_ms": null, "rt_p99_ms": null, "top_paths": []}')
        else:
            print("Total: 0")
            print("By status:")
            print("Avg RT (ms): n/a")
            print("P95 RT (ms): n/a")
            print("P99 RT (ms): n/a")
            print("Top paths:")
        return 0
    total_log_entries = len(filtered_log_entries)

    dist_status = {}
    for log in filtered_log_entries:
        dist_status[log.status] = dist_status.get(log.status, 0) + 1

    req_time = [log.request_time_s * 1000 for log in filtered_log_entries if log.request_time_s is not None]

    if req_time:
        avg_req_time = round(sum(req_time) / len(req_time), 2)
        sorted_time = sorted(req_time)
        p95_ind = min(len(sorted_time) - 1, int(len(sorted_time) * 0.95))
        p99_ind = min(len(sorted_time) - 1, int(len(sorted_time) * 0.99))
        p95_rt = sorted_time[p95_ind]
        p99_rt = sorted_time[p99_ind]
    else:
        avg_req_time = None
        p95_rt = None
        p99_rt = None

    path_counts = {}
    for log in filtered_log_entries:
        path_counts[log.path] = path_counts.get(log.path, 0) + 1

    top_paths = sorted(path_counts.items(), key=lambda i: i[1], reverse=True)[:args.top]
    top_paths_format = [[path, count] for path, count in top_paths]

    if args.json:
        result = {
            "total": total_log_entries,
            "status": dist_status,
            "rt_avg_ms": avg_req_time,
            "rt_p95_ms": p95_rt,
            "rt_p99_ms": p99_rt,
            "top_paths": top_paths_format
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Total: {total_log_entries}")
        print("By status:")
        for status, count in sorted(dist_status.items()):
            print(f" {status}: {count}")

        if avg_req_time is not None:
            print(f"Avg RT (ms): {avg_req_time:.2f}")
            print(f"P95 RT (ms): {p95_rt:.2f}")
            print(f"P99 RT (ms): {p99_rt:.2f}")
        else:
            print("Avg RT (ms): n/a")
            print("P95 RT (ms): n/a")
            print("P99 RT (ms): n/a")

        print("Top paths: ")
        for path, count in top_paths_format:
            print(f"{count} {path}")
    return 0


def cmd_filter(args: argparse.Namespace) -> int:

    all_log_entries = read_log_file(args.path)
    # if all_log_entries is None:
    #     return 2
    filtered_log_entries = filter_log_entries(
        all_log_entries,
        since=args.since,
        until=args.until,
        status=args.status,
        grep=args.grep
    )

    output_lines = []
    for log in filtered_log_entries:
        ts_iso_output = log.ts.isoformat()

        if log.bytes_sent is not None:
            bytes_output = str(log.bytes_sent)
        else:
            bytes_output = "-"

        if log.request_time_s:
            rt_output = f"rt={log.request_time_s}"
        else:
            rt_output = ""

        line = f"{ts_iso_output} {log.ip} {log.method} {log.path} {log.status} {bytes_output} {rt_output}".strip()
        output_lines.append(line)

    output_text = '\n'.join(output_lines)

    if args.out:
        with open(args.out, 'w') as f:
            f.write(output_text + '\n')
    else:
        print(output_text)
    return 0

def cmd_hist(args: argparse.Namespace) -> int:
    all_log_entries = read_log_file(args.path)
    # if all_log_entries is None:
    #     return 2
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

    req_time = [log.request_time_s * 1000 for log in filtered_log_entries if log.request_time_s is not None]


    bucket_ms = args.bucket_ms
    hist = {}

    for rt in req_time:
        buck_start = (rt // bucket_ms) * bucket_ms
        buck_end = buck_start + bucket_ms
        buck_key = f"{int(buck_start)}-{int(buck_end)}"

        hist[buck_key] = hist.get(buck_key, 0) + 1

    sorted_buck = sorted(hist.items())

    if args.json:
        result = {buck: count for buck, count in sorted_buck}
        print(json.dumps(result, indent=2))
    else:
        if sorted_buck:
            max_count = max(count for _, count in sorted_buck)
            for buck, count in sorted_buck:
                bar_length = max(1, int(count / max_count * 10))
                bar = '#' * bar_length
                print(f"{buck}: {bar} {count}")
        else:
            print("No data for histogram:(")

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
        return 1
