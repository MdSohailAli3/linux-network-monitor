import socket
import threading
from unittest.mock import patch

from netwatch.models import Target
from netwatch.network import check_target


def test_successful_tcp_connection_and_latency():
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]
        thread = threading.Thread(target=lambda: server.accept()[0].close(), daemon=True)
        thread.start()
        result = check_target(Target("127.0.0.1", port, 1))
    assert result.status == "SUCCESS"
    assert result.resolved_ip == "127.0.0.1"
    assert result.latency_ms is not None and result.latency_ms >= 0


def test_dns_failure_is_classified():
    with patch("netwatch.network.socket.getaddrinfo", side_effect=socket.gaierror("not found")):
        result = check_target(Target("invalid.invalid", 80))
    assert result.status == "DNS_ERROR"
    assert result.latency_ms is None


def test_timeout_is_classified():
    with patch("netwatch.network.socket.getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.1", 80))]), \
         patch("netwatch.network.socket.create_connection", side_effect=socket.timeout("late")):
        result = check_target(Target("example.test", 80))
    assert result.status == "TIMEOUT"


def test_refused_is_classified():
    with patch("netwatch.network.socket.getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))]), \
         patch("netwatch.network.socket.create_connection", side_effect=ConnectionRefusedError("refused")):
        result = check_target(Target("localhost", 80))
    assert result.status == "REFUSED"
