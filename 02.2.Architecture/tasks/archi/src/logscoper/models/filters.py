from __future__ import annotations
from datetime import datetime
from typing import Optional
import re
from .log_entry import LogEntry


def filter_by_status(log_entries: list[LogEntry], status_filter: str) -> list[LogEntry]:
    filtered = []
    status_patterns = [s.strip() for s in status_filter.split(',')]
    for log in log_entries:
        for pat in status_patterns:
            if pat.endswith('xx'):
                status_type = int(pat[0]) * 100
                if status_type <= log.status < status_type + 100:
                    filtered.append(log)
                    break
            else:
                if log.status == int(pat):
                    filtered.append(log)
                    break

    return filtered


def filter_by_time(
        log_entries: list[LogEntry],
        since: Optional[str] = None,
        until: Optional[str] = None) -> list[LogEntry]:
    filtered = []

    since_dt = parse_dt(since) if since else None
    until_dt = parse_dt(until) if until else None

    for log in log_entries:
        if_include = True

        if since_dt and log.ts < since_dt:
            if_include = False

        if if_include and until_dt and log.ts >= until_dt:
            if_include = False

        if if_include:
            filtered.append(log)

    return filtered


def filter_by_reg(log_entries: list[LogEntry], pattern: str) -> list[LogEntry]:
    reg = re.compile(pattern)
    return [log for log in log_entries if reg.search(log.path)]


def parse_dt(s_entry: str) -> datetime:
    if s_entry.endswith('Z'):
        s_entry = s_entry[:-1] + '+00:00'
    if '+' not in s_entry and (len(s_entry) < 6 or s_entry[-6] not in '+-'):
        s_entry += '+00:00'
    try:
        return datetime.fromisoformat(s_entry)
    except ValueError:
        raise ValueError("Error! Invalid date format")
