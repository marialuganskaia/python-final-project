from __future__ import annotations
from typing import Optional
from ..models.log_entry import LogEntry
from ..models.filters import filter_by_status, filter_by_time, filter_by_reg


def log_entries_to_txt(log_entries: list[LogEntry]) -> str:
    lines = []

    for log in log_entries:
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
        lines.append(line)

    return '\n'.join(lines)


def filter_log_entries(log_entries: list[LogEntry],
                       since: Optional[str] = None,
                       until: Optional[str] = None,
                       status: Optional[str] = None,
                       grep: Optional[str] = None) -> list[LogEntry]:

    if since or until:
        log_entries = filter_by_time(log_entries, since, until)

    if status:
        log_entries = filter_by_status(log_entries, status)

    if grep:
        log_entries = filter_by_reg(log_entries, grep)

    return log_entries
