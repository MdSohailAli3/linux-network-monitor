"""TCP connectivity checks using the unprivileged Python socket API."""
import socket
import time
from datetime import datetime, timezone
from typing import Callable

from .models import CheckResult, Target


def check_target(target: Target, *, socket_factory: Callable | None = None) -> CheckResult:
    """Attempt one TCP connection and classify common network failures.

    Latency measures TCP connection establishment only, not ICMP RTT or the
    response time of an application protocol.
    """
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    socket_factory = socket_factory or socket.create_connection
    resolved_ip = ""
    start = time.monotonic()
    try:
        # Resolve explicitly so DNS failures are distinguishable from connect failures.
        try:
            addresses = socket.getaddrinfo(target.host, target.port, type=socket.SOCK_STREAM)
            if addresses:
                resolved_ip = addresses[0][4][0]
        except socket.gaierror as exc:
            return CheckResult(timestamp, target.host, "", target.port, "DNS_ERROR", None, str(exc))

        start = time.monotonic()
        with socket_factory((target.host, target.port), timeout=target.timeout):
            latency = (time.monotonic() - start) * 1000.0
        return CheckResult(timestamp, target.host, resolved_ip, target.port, "SUCCESS", round(latency, 3))
    except (socket.timeout, TimeoutError) as exc:
        return CheckResult(timestamp, target.host, resolved_ip, target.port, "TIMEOUT", None, str(exc) or "connection timed out")
    except ConnectionRefusedError as exc:
        return CheckResult(timestamp, target.host, resolved_ip, target.port, "REFUSED", None, str(exc) or "connection refused")
    except OSError as exc:
        return CheckResult(timestamp, target.host, resolved_ip, target.port, "SOCKET_ERROR", None, str(exc))
