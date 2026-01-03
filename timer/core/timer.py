"""Timer logic for managing active timer state."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from timer.core.task import Task, Pause


@dataclass
class ActiveTimer:
    """Represents a currently running timer."""

    task_name: str
    start_time: datetime
    paused: bool = False
    pause_start: Optional[datetime] = None
    pauses: list[Pause] = field(default_factory=list)
    description: str = ""
    tags: list[str] = field(default_factory=list)

    @property
    def total_pause_seconds(self) -> int:
        """Get total paused time in seconds."""
        total = sum(p.duration_seconds for p in self.pauses)
        if self.paused and self.pause_start:
            total += int((datetime.now() - self.pause_start).total_seconds())
        return total

    @property
    def elapsed_seconds(self) -> int:
        """Get elapsed time in seconds, excluding pauses."""
        if self.paused and self.pause_start:
            # If paused, calculate up to pause start
            total = int((self.pause_start - self.start_time).total_seconds())
        else:
            total = int((datetime.now() - self.start_time).total_seconds())
        return total - sum(p.duration_seconds for p in self.pauses)

    @property
    def elapsed_formatted(self) -> str:
        """Get elapsed time as HH:MM:SS string."""
        secs = self.elapsed_seconds
        hours, remainder = divmod(secs, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def pause(self) -> bool:
        """Pause the timer. Returns False if already paused."""
        if self.paused:
            return False
        self.paused = True
        self.pause_start = datetime.now()
        return True

    def resume(self) -> bool:
        """Resume the timer. Returns False if not paused."""
        if not self.paused or not self.pause_start:
            return False
        self.pauses.append(Pause(start=self.pause_start, end=datetime.now()))
        self.paused = False
        self.pause_start = None
        return True

    def stop(self) -> Task:
        """Stop the timer and return a completed Task."""
        # If paused, resume first to finalize the pause
        if self.paused and self.pause_start:
            self.pauses.append(Pause(start=self.pause_start, end=datetime.now()))

        return Task(
            task_name=self.task_name,
            start_time=self.start_time,
            end_time=datetime.now(),
            description=self.description,
            pauses=self.pauses,
            tags=self.tags,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "task_name": self.task_name,
            "start_time": self.start_time.isoformat(),
            "paused": self.paused,
            "pause_start": self.pause_start.isoformat() if self.pause_start else None,
            "pauses": [p.to_dict() for p in self.pauses],
            "description": self.description,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActiveTimer":
        """Create from dictionary."""
        return cls(
            task_name=data["task_name"],
            start_time=datetime.fromisoformat(data["start_time"]),
            paused=data.get("paused", False),
            pause_start=datetime.fromisoformat(data["pause_start"])
            if data.get("pause_start")
            else None,
            pauses=[Pause.from_dict(p) for p in data.get("pauses", [])],
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )


def start_timer(
    task_name: str, description: str = "", tags: list[str] = None
) -> ActiveTimer:
    """Create and return a new active timer."""
    return ActiveTimer(
        task_name=task_name,
        start_time=datetime.now(),
        description=description,
        tags=tags or [],
    )
