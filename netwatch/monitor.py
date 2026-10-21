"""Continuous monitoring loop with graceful signal-aware shutdown."""
import signal
import time
from collections.abc import Callable, Iterable
from pathlib import Path

from .logger import append_result
from .models import CheckResult, Target
from .network import check_target


def run_monitor(
    targets: Iterable[Target], log_path: str | Path, interval: float = 10.0,
    *, stop_event=None, check: Callable[[Target], CheckResult] = check_target,
    max_cycles: int | None = None,
) -> None:
    """Monitor targets until a signal/stop event or optional cycle limit.

    `max_cycles` and `stop_event` make the loop straightforward to test.
    """
    if interval <= 0:
        raise ValueError("interval must be positive")
    target_list = list(targets)
    if not target_list:
        raise ValueError("at least one target is required")
    cycles = 0
    while True:
        for target in target_list:
            result = check(target)
            append_result(log_path, result)
            latency = f"{result.latency_ms:.3f} ms" if result.latency_ms is not None else "n/a"
            detail = f" — {result.error}" if result.error else ""
            print(f"[{result.status}] {result.host}:{result.port} latency={latency}{detail}", flush=True)
        cycles += 1
        if (max_cycles is not None and cycles >= max_cycles) or (stop_event is not None and stop_event.is_set()):
            break
        if stop_event is not None:
            if stop_event.wait(interval):
                break
        else:
            time.sleep(interval)


def install_signal_handlers(stop_event) -> dict[int, object]:
    """Install SIGINT/SIGTERM handlers that request a clean stop; return old handlers."""
    previous = {}
    def request_stop(signum, frame):  # noqa: ARG001 - signal handler signature
        stop_event.set()
    for signum in (signal.SIGINT, signal.SIGTERM):
        previous[signum] = signal.signal(signum, request_stop)
    return previous
