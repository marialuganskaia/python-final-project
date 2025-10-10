from __future__ import annotations
from .log_entry import LogEntry


def calculate_stats(log_entries: list[LogEntry], top_number: int = 10) -> dict:
    if not log_entries:
        return {
            "total": 0,
            "status": {},
            "rt_avg_ms": None,
            "rt_p95_ms": None,
            "rt_p99_ms": None,
            "top_paths": []
        }

    total_log_entries = len(log_entries)

    dist_status: dict[int, int] = {}
    for log in log_entries:
        dist_status[log.status] = dist_status.get(log.status, 0) + 1

    req_time = [log.request_time_s * 1000 for log in log_entries if log.request_time_s is not None]

    if req_time:
        avg_req_time = round(sum(req_time) / len(req_time), 2)
        sorted_time = sorted(req_time)
        p95_ind = min(len(sorted_time) - 1, int(len(sorted_time) * 0.95))
        p99_ind = min(len(sorted_time) - 1, int(len(sorted_time) * 0.99))
        p95_req_time = sorted_time[p95_ind]
        p99_req_time = sorted_time[p99_ind]
    else:
        avg_req_time = None
        p95_req_time = None
        p99_req_time = None

    path_counts: dict[str, int] = {}
    for log in log_entries:
        path_counts[log.path] = path_counts.get(log.path, 0) + 1

    top_paths = sorted(path_counts.items(), key=lambda i: i[1], reverse=True)[:top_number]

    return {
        "total": total_log_entries,
        "status": dist_status,
        "rt_avg_ms": avg_req_time,
        "rt_p95_ms": p95_req_time,
        "rt_p99_ms": p99_req_time,
        "top_paths": top_paths
    }


def calculate_hist(log_entries: list[LogEntry], bucket_ms: int) -> dict:

    req_time = [log.request_time_s * 1000 for log in log_entries if log.request_time_s is not None]
    hist: dict[str, float] = {}

    for rt in req_time:
        buck_start = (rt // bucket_ms) * bucket_ms
        buck_end = buck_start + bucket_ms
        buck_key = f"{int(buck_start)}-{int(buck_end)}"
        hist[buck_key] = hist.get(buck_key, 0) + 1

    return dict(sorted(hist.items()))
