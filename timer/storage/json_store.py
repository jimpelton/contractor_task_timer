"""JSON file-based storage for timer data."""

import json
from pathlib import Path
from typing import Optional

from timer.config import get_data_path
from timer.core.task import Task
from timer.core.timer import ActiveTimer


def _get_entries_file() -> Path:
    """Get path to entries.json file."""
    return get_data_path() / "entries.json"


def _get_active_file() -> Path:
    """Get path to active.json file."""
    return get_data_path() / "active.json"


# --- Active Timer ---


def get_active_timer() -> Optional[ActiveTimer]:
    """Get the currently active timer, if any."""
    active_file = _get_active_file()
    if not active_file.exists():
        return None

    with open(active_file, "r") as f:
        data = json.load(f)

    return ActiveTimer.from_dict(data)


def save_active_timer(timer: ActiveTimer) -> None:
    """Save the active timer state."""
    active_file = _get_active_file()
    with open(active_file, "w") as f:
        json.dump(timer.to_dict(), f, indent=2)


def clear_active_timer() -> None:
    """Clear the active timer file."""
    active_file = _get_active_file()
    if active_file.exists():
        active_file.unlink()


# --- Task Entries ---


def get_entries() -> list[Task]:
    """Get all completed task entries."""
    entries_file = _get_entries_file()
    if not entries_file.exists():
        return []

    with open(entries_file, "r") as f:
        data = json.load(f)

    return [Task.from_dict(entry) for entry in data]


def save_entry(task: Task) -> None:
    """Save a completed task entry."""
    entries = get_entries()
    entries.append(task)
    _save_entries(entries)


def _save_entries(entries: list[Task]) -> None:
    """Save all entries to file."""
    entries_file = _get_entries_file()
    with open(entries_file, "w") as f:
        json.dump([e.to_dict() for e in entries], f, indent=2)


def delete_entry(entry_id: str) -> bool:
    """Delete an entry by ID. Returns True if found and deleted."""
    entries = get_entries()
    original_count = len(entries)
    entries = [e for e in entries if e.id != entry_id]

    if len(entries) == original_count:
        return False

    _save_entries(entries)
    return True


def get_entry_by_id(entry_id: str) -> Optional[Task]:
    """Get a single entry by ID."""
    entries = get_entries()
    for entry in entries:
        if entry.id == entry_id:
            return entry
    return None
