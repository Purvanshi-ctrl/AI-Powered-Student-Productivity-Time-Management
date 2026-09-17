"""
task_manager.py — Core business logic: CRUD operations and task queries.
"""

from datetime import date
from task import Task
from storage import Storage
from utils import normalize_subject


class TaskManager:
    """Manages the in-memory task list and coordinates with Storage."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.tasks: list[Task] = self.storage.load()

    # ------------------------------------------------------------------ #
    # Mutations                                                            #
    # ------------------------------------------------------------------ #

    def add_task(
        self,
        title: str,
        subject: str,
        priority: str,
        due_date: date,
        estimated_hours: float,
        description: str = "",
    ) -> Task:
        """Create a new Task, append it to the list, and persist."""
        task = Task(
            title=title.strip(),
            description=description.strip(),
            subject=normalize_subject(subject),
            priority=priority,
            due_date=due_date,
            estimated_hours=float(estimated_hours),
        )
        self.tasks.append(task)
        self.storage.save(self.tasks)
        return task

    def update_task(self, task_id: str, **fields) -> bool:
        """Update editable fields of a task by ID. Returns True if found."""
        task = self._find(task_id)
        if task is None:
            return False

        allowed = ("title", "description", "subject", "priority", "due_date", "estimated_hours")
        for key, value in fields.items():
            if key not in allowed:
                continue
            if key == "subject":
                value = normalize_subject(value)
            if key == "title":
                value = value.strip()
            if key == "description":
                value = value.strip()
            if key == "estimated_hours":
                value = float(value)
            setattr(task, key, value)

        self.storage.save(self.tasks)
        return True

    def update_status(self, task_id: str, status: str) -> bool:
        """Set a task's status to 'Pending' or 'Completed'. Returns True if found."""
        task = self._find(task_id)
        if task is None:
            return False
        task.status = status
        self.storage.save(self.tasks)
        return True

    def delete_task(self, task_id: str) -> bool:
        """Remove a task by ID. Returns True if it was found and removed."""
        task = self._find(task_id)
        if task is None:
            return False
        self.tasks.remove(task)
        self.storage.save(self.tasks)
        return True

    # ------------------------------------------------------------------ #
    # Queries                                                              #
    # ------------------------------------------------------------------ #

    def get_all_tasks(self) -> list[Task]:
        return list(self.tasks)

    def get_pending_tasks(self) -> list[Task]:
        return [t for t in self.tasks if t.status == "Pending"]

    def get_completed_tasks(self) -> list[Task]:
        return [t for t in self.tasks if t.status == "Completed"]

    def get_overdue_tasks(self) -> list[Task]:
        today = date.today()
        return [t for t in self.tasks if t.status == "Pending" and t.due_date < today]

    def get_upcoming_tasks(self) -> list[Task]:
        today = date.today()
        return [t for t in self.tasks if t.status == "Pending" and t.due_date >= today]

    def get_tasks_by_subject(self, subject: str) -> list[Task]:
        normalized = subject.strip().lower()
        return [t for t in self.tasks if t.subject.lower() == normalized]

    def total_pending_hours(self) -> float:
        return sum(t.estimated_hours for t in self.get_pending_tasks())

    def get_subjects(self) -> list[str]:
        """Return a sorted, deduplicated list of all subject names."""
        return sorted(set(t.subject for t in self.tasks))

    def get_stats(self) -> dict:
        """Return a summary dictionary of productivity statistics."""
        total = len(self.tasks)
        completed = len(self.get_completed_tasks())
        pending = total - completed
        pct_done = round((completed / total * 100), 1) if total > 0 else 0.0
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "pct_done": pct_done,
            "pending_hours": round(self.total_pending_hours(), 2),
            "subjects": self.get_subjects(),
        }

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _find(self, task_id: str):
        """Return the Task with the given ID, or None if not found."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
