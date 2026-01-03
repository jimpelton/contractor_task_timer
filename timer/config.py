"""Configuration management for timer app.

Config is stored in ~/.timer/config.json and contains:
- data_path: Location for timer data files (entries.json, active.json)
"""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".timer"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_DATA_PATH = CONFIG_DIR / "data"


def _ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _load_config() -> dict:
    """Load config from file, returning empty dict if not found."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_config(config: dict) -> None:
    """Save config to file."""
    _ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_data_path() -> Path:
    """Get the configured data path, creating it if needed."""
    config = _load_config()
    data_path = Path(config.get("data_path", str(DEFAULT_DATA_PATH)))
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path


def set_data_path(path: str) -> Path:
    """Set the data path in config."""
    data_path = Path(path).expanduser().resolve()
    config = _load_config()
    config["data_path"] = str(data_path)
    _save_config(config)
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path


def get_config() -> dict:
    """Get full config with defaults applied."""
    config = _load_config()
    return {
        "data_path": config.get("data_path", str(DEFAULT_DATA_PATH)),
    }
