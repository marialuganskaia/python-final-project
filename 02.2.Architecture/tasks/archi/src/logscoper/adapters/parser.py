from __future__ import annotations
from datetime import datetime
from typing import Optional
import re
from ..models.log_entry import LogEntry

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
