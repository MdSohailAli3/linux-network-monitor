"""Shared data models for network checks."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Target:
    host: str
    port: int
    timeout: float = 3.0


@dataclass(frozen=True)
class CheckResult:
    timestamp: str
    host: str
    resolved_ip: str
    port: int
    status: str
    latency_ms: Optional[float]
    error: str = ""

    @property
    def successful(self) -> bool:
        return self.status == "SUCCESS"
