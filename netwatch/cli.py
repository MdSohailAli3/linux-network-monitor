"""Command-line interface for netwatch."""
import argparse
import threading
import sys

from .config import ConfigError, load_config
from .models import Target
from .monitor import install_signal_handlers, run_monitor
from .network import check_target
from .logger import append_result
from .reports import build_report, format_report


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def _positive_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be a number") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="netwatch", description="Lightweight TCP connectivity monitor for Linux")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="perform one TCP connectivity check")
    check.add_argument("--host", required=True, help="hostname or IP address")
    check.add_argument("--port", required=True, type=_port, help="TCP port (1-65535)")
    check.add_argument("--timeout", type=_positive_float, default=3.0, help="connection timeout in seconds (default: 3)")
    check.add_argument("--log", help="optionally append the result to a CSV log")

    monitor = commands.add_parser("monitor", help="continuously monitor configured targets")
    monitor.add_argument("--config", required=True, help="JSON target configuration")
    monitor.add_argument("--interval", type=_positive_float, default=10.0, help="seconds between cycles (default: 10)")
    monitor.add_argument("--log", default="data/monitoring.csv", help="CSV output path (default: data/monitoring.csv)")

    report = commands.add_parser("report", help="summarize a CSV monitoring log")
    report.add_argument("--log", required=True, help="CSV log path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "check":
            result = check_target(Target(args.host, args.port, args.timeout))
            print(f"[{result.status}] {result.host}:{result.port} resolved_ip={result.resolved_ip or 'n/a'}")
            print(f"Latency: {result.latency_ms:.3f} ms" if result.latency_ms is not None else f"Error: {result.error}")
            if args.log:
                append_result(args.log, result)
            return 0 if result.successful else 1
        if args.command == "monitor":
            targets = load_config(args.config)
            stop_event = threading.Event()
            previous_handlers = install_signal_handlers(stop_event)
            try:
                print(f"Monitoring {len(targets)} target(s); interval={args.interval:g}s; log={args.log}. Press Ctrl+C to stop.", flush=True)
                run_monitor(targets, args.log, args.interval, stop_event=stop_event)
            finally:
                for signum, handler in previous_handlers.items():
                    import signal
                    signal.signal(signum, handler)
            return 0
        if args.command == "report":
            print(format_report(build_report(args.log)))
            return 0
    except (ConfigError, OSError, ValueError) as exc:
        print(f"netwatch: error: {exc}", file=sys.stderr)
        return 2
    return 2
