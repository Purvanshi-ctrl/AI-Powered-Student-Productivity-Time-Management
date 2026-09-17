"""
utils.py — Shared helper functions for validation and date calculations.
"""

from datetime import date


def is_valid_title(title: str) -> bool:
    """Return True if title is non-empty and at least 3 characters long."""
    return isinstance(title, str) and len(title.strip()) >= 3


def is_valid_hours(value) -> bool:
    """Return True if value is a positive number no greater than 100."""
    try:
        hours = float(value)
        return 0 < hours <= 100
    except (TypeError, ValueError):
        return False


def days_until_due(due_date: date) -> int:
    """Return the number of days from today until due_date.
    Negative means overdue; 0 means due today.
    """
    return (due_date - date.today()).days


def normalize_subject(subject: str) -> str:
    """Strip whitespace and convert to Title Case for consistent storage."""
    return subject.strip().title()
