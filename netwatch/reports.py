"""Summary reporting from CSV monitoring logs."""
import csv
from pathlib import Path
from typing import Any

from .logger import FIELDS


def build_report(path: str | Path) -> dict[str, Any]:
    """Return totals, success rate, and successful-connection latency statistics."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"log file not found: {source}")
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            rows = []
        else:
            missing = set(FIELDS) - set(reader.fieldnames)
            if missing:
                raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
            rows = list(reader)
    total = len(rows)
    successes = [float(row["latency_ms"]) for row in rows if row["status"] == "SUCCESS" and row.get("latency_ms") not in (None, "")]
    successful_count = sum(row["status"] == "SUCCESS" for row in rows)
    failures = total - successful_count
    return {
        "total_attempts": total,
        "successes": successful_count,
        "failures": failures,
        "success_rate_pct": round(successful_count * 100.0 / total, 2) if total else 0.0,
        "latency_min_ms": round(min(successes), 3) if successes else None,
        "latency_max_ms": round(max(successes), 3) if successes else None,
        "latency_avg_ms": round(sum(successes) / len(successes), 3) if successes else None,
    }


def format_report(report: dict[str, Any]) -> str:
    """Format a report as readable terminal text."""
    lines = [
        "Network Monitoring Summary",
        "--------------------------",
        f"Total attempts : {report['total_attempts']}",
        f"Successes      : {report['successes']}",
        f"Failures       : {report['failures']}",
        f"Success rate   : {report['success_rate_pct']:.2f}%",
    ]
    if report["latency_avg_ms"] is None:
        lines.append("Latency (ms)   : no successful connections")
    else:
        lines.extend([
            f"Latency min    : {report['latency_min_ms']:.3f} ms",
            f"Latency max    : {report['latency_max_ms']:.3f} ms",
            f"Latency avg    : {report['latency_avg_ms']:.3f} ms",
        ])
    return "\n".join(lines)
