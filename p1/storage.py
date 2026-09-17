"""
storage.py — Handles saving and loading tasks from a local JSON file.
"""

import json
from task import Task


class Storage:
    """Persists the task list to a JSON file on disk."""

    def __init__(self, filename: str = "tasks.json"):
        self.filename = filename

    def save(self, tasks: list) -> None:
        """Serialize and write all tasks to the JSON file."""
        data = [task.to_dict() for task in tasks]
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self) -> list:
        """Read tasks from the JSON file. Returns an empty list if unavailable."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Task.from_dict(item) for item in data]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"Warning: '{self.filename}' is corrupted. Starting with an empty task list.")
            return []
