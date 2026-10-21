import json
import pytest
from netwatch.config import ConfigError, load_config


def test_loads_valid_config(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"timeout": 2, "targets": [{"host": "localhost", "port": 443}]}))
    targets = load_config(path)
    assert len(targets) == 1
    assert targets[0].host == "localhost"
    assert targets[0].timeout == 2.0


@pytest.mark.parametrize("payload", [
    {}, {"targets": []}, {"targets": [{"host": "localhost", "port": 0}]},
    {"targets": [{"host": "localhost", "port": 65536}]},
    {"targets": [{"host": "bad host", "port": 80}]},
    {"targets": [{"host": "localhost", "port": True}]},
])
def test_rejects_invalid_config(tmp_path, payload):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ConfigError):
        load_config(path)


def test_invalid_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{")
    with pytest.raises(ConfigError, match="invalid JSON"):
        load_config(path)
