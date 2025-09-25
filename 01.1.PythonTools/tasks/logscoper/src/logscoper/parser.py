from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
import re
import sys

from .model import LogEntry

LOG_RE = re.compile(
    r'(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<ts>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<path>.*?)(?:\s+HTTP/\d\.\d)?"\s+'
    r'(?P<status>\d{3})\s+(?P<bytes>\S+)'
    r'(?:\s+"[^"]*"\s+"[^"]*")?'
    r'(?:\s+(?P<rt>\d+\.\d+)|\s+rt=(?P<rt_kv>\d+\.\d+))?'
)


RT_KV_RE = re.compile(r'(?:^|\s)rt=(?P<rt>\d+\.\d+)\b')


def parse_log_line(line: str) -> Optional[LogEntry]:
    line = line.strip()
    if not line:
        return None

    match = LOG_RE.match(line)
    if not match:
        return None

    data = match.groupdict()

    try:
        timestamp = datetime.strptime(data['ts'], '%d/%b/%Y:%H:%M:%S %z')

        if data['bytes'] == '-':
            bytes_s = None
        else:
            bytes_s = int(data['bytes'])

        req_time_s = data.get('rt') or data.get('rt_kv')
        if req_time_s:
            req_time = float(req_time_s)
        else:
            req_time = None

        return LogEntry(
            ip=data['ip'],
            ts=timestamp,
            method=data['method'],
            path=data['path'],
            status=int(data['status']),
            bytes_sent=bytes_s,
            request_time_s=req_time
        )
    except (ValueError, KeyError):
        return None


def read_log_file(path: str) -> list[LogEntry]:
    with open(path, 'r') as f:
        parsed_lines = []
        for line in f:
            parsed_line = parse_log_line(line)
            if parsed_line:
                parsed_lines.append(parsed_line)
        return parsed_lines

def filter_log_entries(log_entries: list[LogEntry],
                       since: str = None,
                       until: str = None,
                       status: str = None,
                       grep: str = None) -> list[LogEntry]:

    if since or until:
        log_entries = filter_by_time(log_entries, since, until)

    if status:
        log_entries = filter_by_status(log_entries, status)

    if grep:
        log_entries = filter_by_reg(log_entries, grep)

    return log_entries



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


def filter_by_time(log_entries: list[LogEntry], since: str = None, until: str = None) -> list[LogEntry]:
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


def parse_dt(s_entry: str) -> datetime:
    if s_entry.endswith('Z'):
        s_entry = s_entry[:-1] + '+00:00'
    if '+' not in s_entry and (len(s_entry) < 6 or s_entry[-6] not in '+-'):
        s_entry += '+00:00'
    try:
        return datetime.fromisoformat(s_entry)
    except ValueError:
        print("Error! Invalid date format", file=sys.stderr)
        sys.exit(1)


def filter_by_reg(log_entries: list[LogEntry], pattern: str) -> list[LogEntry]:
    reg = re.compile(pattern)
    return [log for log in log_entries if reg.search(log.path)]

