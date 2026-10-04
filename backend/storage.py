"""Small JSON-file persistence helpers shared by the API and consumers."""

import json
import os
from pathlib import Path
from typing import Any


def data_directory() -> Path:
    """Return the configured data directory, creating it when needed."""
    configured = os.environ.get("DATA_DIR")
    directory = Path(configured) if configured else Path(__file__).resolve().parent.parent / "data"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_json(path: Path, default: Any) -> Any:
    """Read JSON from path, returning a fresh default for missing/invalid files."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: Path, value: Any) -> None:
    """Write JSON atomically so readers never observe a partially written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(value, file, indent=2)
        file.write("\n")
    os.replace(temporary_path, path)
