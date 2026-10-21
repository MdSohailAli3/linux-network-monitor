"""CSV persistence for monitoring results."""
import csv
from pathlib import Path
from .models import CheckResult

FIELDS = ["timestamp", "host", "resolved_ip", "port", "status", "latency_ms", "error"]


def append_result(path: str | Path, result: CheckResult) -> None:
    """Append one result, creating parent directories and the CSV header as needed."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not destination.exists() or destination.stat().st_size == 0
    with destination.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if needs_header:
            writer.writeheader()
        writer.writerow({field: getattr(result, field) for field in FIELDS})
