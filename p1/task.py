"""
task.py — Task data model for the Student Productivity System.
"""

import uuid
from datetime import date, datetime


class Task:
    """Represents a single student academic task."""

    VALID_PRIORITIES = ("Low", "Medium", "High")
    VALID_STATUSES = ("Pending", "Completed")

    def __init__(
        self,
        title: str,
        subject: str,
        priority: str,
        due_date: date,
        estimated_hours: float,
        description: str = "",
        status: str = "Pending",
        task_id: str = None,
        created_at: datetime = None,
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.subject = subject
        self.priority = priority
        self.due_date = due_date
        self.estimated_hours = estimated_hours
        self.status = status
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """Serialize the Task to a JSON-safe dictionary."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "subject": self.subject,
            "priority": self.priority,
            "due_date": self.due_date.isoformat(),
            "estimated_hours": self.estimated_hours,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Reconstruct a Task from a dictionary (e.g. loaded from JSON)."""
        return cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data.get("description", ""),
            subject=data["subject"],
            priority=data["priority"],
            due_date=date.fromisoformat(data["due_date"]),
            estimated_hours=float(data["estimated_hours"]),
            status=data.get("status", "Pending"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    def __repr__(self) -> str:
        return (
            f"Task(id={self.task_id[:8]}..., title={self.title!r}, "
            f"priority={self.priority}, due={self.due_date}, status={self.status})"
        )
