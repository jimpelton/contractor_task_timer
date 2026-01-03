"""Task model representing a time entry."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Pause:
    """Represents a pause period within a task."""

    start: datetime
    end: Optional[datetime] = None

    @property
    def duration_seconds(self) -> int:
        """Get pause duration in seconds."""
        if self.end is None:
            return 0
        return int((self.end - self.start).total_seconds())

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat() if self.end else None,
            "duration_seconds": self.duration_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pause":
        """Create from dictionary."""
        return cls(
            start=datetime.fromisoformat(data["start"]),
            end=datetime.fromisoformat(data["end"]) if data.get("end") else None,
        )


@dataclass
class Task:
    """Represents a completed time entry."""

    task_name: str
    start_time: datetime
    end_time: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    pauses: list[Pause] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> int:
        """Get total duration in seconds, excluding pauses."""
        total = int((self.end_time - self.start_time).total_seconds())
        pause_time = sum(p.duration_seconds for p in self.pauses)
        return total - pause_time

    @property
    def duration_formatted(self) -> str:
        """Get duration as HH:MM:SS string."""
        secs = self.duration_seconds
        hours, remainder = divmod(secs, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "task_name": self.task_name,
            "description": self.description,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "pauses": [p.to_dict() for p in self.pauses],
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            task_name=data["task_name"],
            description=data.get("description", ""),
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            pauses=[Pause.from_dict(p) for p in data.get("pauses", [])],
            tags=data.get("tags", []),
        )
