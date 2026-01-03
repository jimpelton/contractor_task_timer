"""Export functionality for timer entries."""

import csv
import json
import io
from datetime import datetime, timedelta
from typing import Optional

from timer.core.task import Task
from timer.storage.json_store import get_entries


def filter_entries(
    entries: list[Task],
    today: bool = False,
    week: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[Task]:
    """Filter entries by date range."""
    if today:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return [e for e in entries if e.start_time >= today_start]

    if week:
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        return [e for e in entries if e.start_time >= week_start]

    if start_date and end_date:
        return [e for e in entries if start_date <= e.start_time <= end_date]

    return entries


def export_to_csv(entries: list[Task]) -> str:
    """Export entries to CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "ID",
            "Task Name",
            "Description",
            "Start Time",
            "End Time",
            "Duration (seconds)",
            "Duration (formatted)",
            "Tags",
        ]
    )

    # Data rows
    for entry in entries:
        writer.writerow(
            [
                entry.id,
                entry.task_name,
                entry.description,
                entry.start_time.isoformat(),
                entry.end_time.isoformat(),
                entry.duration_seconds,
                entry.duration_formatted,
                ",".join(entry.tags),
            ]
        )

    return output.getvalue()


def export_to_json(entries: list[Task]) -> str:
    """Export entries to JSON format."""
    return json.dumps([e.to_dict() for e in entries], indent=2)


def generate_summary(entries: list[Task]) -> dict:
    """Generate a summary of time entries."""
    if not entries:
        return {
            "total_entries": 0,
            "total_seconds": 0,
            "total_formatted": "00:00:00",
            "by_task": {},
        }

    total_seconds = sum(e.duration_seconds for e in entries)

    # Group by task name
    by_task = {}
    for entry in entries:
        if entry.task_name not in by_task:
            by_task[entry.task_name] = {"count": 0, "seconds": 0}
        by_task[entry.task_name]["count"] += 1
        by_task[entry.task_name]["seconds"] += entry.duration_seconds

    # Format totals
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    for task_name, data in by_task.items():
        h, r = divmod(data["seconds"], 3600)
        m, s = divmod(r, 60)
        data["formatted"] = f"{h:02d}:{m:02d}:{s:02d}"

    return {
        "total_entries": len(entries),
        "total_seconds": total_seconds,
        "total_formatted": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
        "by_task": by_task,
    }
