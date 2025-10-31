from __future__ import annotations
import json


def stats_to_txt(stats: dict) -> str:
    lines = []

    lines.append(f"Total: {stats["total"]}")

    lines.append("By status:")
    for status, count in sorted(stats["status"].items()):
        lines.append(f" {status}: {count}")

    if stats["rt_avg_ms"] is not None:
        lines.append(f"Avg RT (ms): {stats["rt_avg_ms"]:.2f}")
        lines.append(f"P95 RT (ms): {stats["rt_p95_ms"]:.2f}")
        lines.append(f"P99 RT (ms): {stats["rt_p99_ms"]:.2f}")
    else:
        lines.append("Avg RT (ms): n/a")
        lines.append("P95 RT (ms): n/a")
        lines.append("P99 RT (ms): n/a")

    lines.append("Top paths: ")
    for path, count in stats["top_paths"]:
        lines.append(f"{count} {path}")

    return "\n".join(lines)


def stats_to_json(stats: dict) -> str:
    return (json.dumps(stats,
                       indent=2))
