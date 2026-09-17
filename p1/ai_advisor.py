"""
ai_advisor.py — Rule-based AI suggestion engine.
Analyses the task list and returns plain-English productivity tips.
"""

from utils import days_until_due


class AIAdvisor:
    """Generates simple rule-based suggestions from the current task list."""

    def get_suggestions(self, tasks: list, stats: dict) -> list[str]:
        """
        Evaluate all rules against the task list and stats dict.
        Returns a list of suggestion strings (at least one is always returned).
        """
        suggestions = []

        suggestions.extend(self._rule_urgency_warning(tasks))
        suggestions.extend(self._rule_overdue_alert(tasks))
        suggestions.extend(self._rule_heavy_workload(stats))
        suggestions.extend(self._rule_easy_wins(tasks))
        suggestions.extend(self._rule_no_progress(stats))
        suggestions.extend(self._rule_great_progress(stats))

        if not suggestions:
            suggestions.append("✅ All looks good! Keep up the great work.")

        return suggestions

    # ------------------------------------------------------------------ #
    # Rules                                                                #
    # ------------------------------------------------------------------ #

    def _rule_urgency_warning(self, tasks: list) -> list[str]:
        """High priority + Pending + due within 2 days."""
        results = []
        for task in tasks:
            if (
                task.status == "Pending"
                and task.priority == "High"
                and 0 <= days_until_due(task.due_date) <= 2
            ):
                results.append(
                    f"⚠️ **{task.subject} — {task.title}** is high priority and due very soon. Start immediately!"
                )
        return results

    def _rule_overdue_alert(self, tasks: list) -> list[str]:
        """Pending task whose due date has already passed."""
        results = []
        for task in tasks:
            if task.status == "Pending" and days_until_due(task.due_date) < 0:
                results.append(
                    f"🔴 **{task.subject} — {task.title}** is overdue! Complete or reschedule it today."
                )
        return results

    def _rule_heavy_workload(self, stats: dict) -> list[str]:
        """Total pending hours exceed 20."""
        if stats["pending_hours"] > 20:
            return [
                f"📚 You have **{stats['pending_hours']} hours** of pending work. "
                "Try breaking tasks into shorter study sessions to avoid burnout."
            ]
        return []

    def _rule_easy_wins(self, tasks: list) -> list[str]:
        """Low priority + Pending + estimated time ≤ 1 hour."""
        results = []
        for task in tasks:
            if (
                task.status == "Pending"
                and task.priority == "Low"
                and task.estimated_hours <= 1
            ):
                results.append(
                    f"✅ **{task.subject} — {task.title}** only takes ~{task.estimated_hours}h. "
                    "Knock it out quickly to clear your list!"
                )
        return results

    def _rule_no_progress(self, stats: dict) -> list[str]:
        """No tasks completed yet but there are more than 3 total."""
        if stats["completed"] == 0 and stats["total"] > 3:
            return [
                "🚀 You haven't completed any tasks yet. "
                "Start with the shortest High priority task to build momentum!"
            ]
        return []

    def _rule_great_progress(self, stats: dict) -> list[str]:
        """Completion percentage is 80% or above."""
        if stats["total"] > 0 and stats["pct_done"] >= 80:
            return [
                f"🎉 You've completed **{stats['pct_done']}%** of your tasks. "
                "Excellent work — keep the momentum going!"
            ]
        return []
