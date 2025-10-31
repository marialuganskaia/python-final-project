from __future__ import annotations
import json


def hist_to_txt(hist: dict) -> str:
    lines = []

    if hist:
        max_count = max(count for _, count in hist.items())
        for buck, count in hist.items():
            bar_length = max(1, int(count / max_count * 10))
            bar = '#' * bar_length
            print(f"{buck}: {bar} {count}")
    else:
        lines.append("No data for histogram:(")

    return "\n".join(lines)


def hist_to_json(hist: dict) -> str:
    return (json.dumps(hist,
                       indent=2))
