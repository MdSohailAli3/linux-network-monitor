"""Load and validate JSON target configuration."""
import json
from pathlib import Path
from typing import Any

from .models import Target


class ConfigError(ValueError):
    """Raised when a configuration file is malformed or invalid."""


def _positive_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ConfigError(f"{name} must be a positive number")
    return float(value)


def load_config(path: str | Path) -> list[Target]:
    """Read a JSON file containing a non-empty `targets` list."""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"cannot read configuration: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON: {exc}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("targets"), list) or not raw["targets"]:
        raise ConfigError("configuration must contain a non-empty 'targets' list")

    default_timeout = _positive_number(raw.get("timeout", 3), "timeout")
    targets: list[Target] = []
    for index, item in enumerate(raw["targets"], start=1):
        if not isinstance(item, dict):
            raise ConfigError(f"target #{index} must be an object")
        host = item.get("host")
        port = item.get("port")
        if not isinstance(host, str) or not host.strip() or any(ch.isspace() for ch in host):
            raise ConfigError(f"target #{index}: host must be a non-empty hostname or IP address")
        if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
            raise ConfigError(f"target #{index}: port must be an integer from 1 to 65535")
        timeout = _positive_number(item.get("timeout", default_timeout), f"target #{index} timeout")
        targets.append(Target(host.strip(), port, timeout))
    return targets
