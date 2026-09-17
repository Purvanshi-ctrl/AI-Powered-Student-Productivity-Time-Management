# AI-Powered Student Productivity & Time Management System — Plan

## Top-Level Overview

**Goal:** Build a small, beginner-friendly Streamlit web app that allows a single student to manage academic tasks, track study time, view productivity statistics, and receive simple rule-based AI suggestions.

**Scope:**
- Local single-user app (no login, no backend server)
- Data persisted in a local `tasks.json` file
- Five Python modules + one Streamlit UI entry point
- AI advisor is fully rule-based — no machine learning

**Non-Goals:**
- Multi-user support
- Authentication
- Cloud storage
- Sorting or filtering the task list
- Data export

**Stack:** Python 3.10+, Streamlit, standard library only (uuid, json, datetime, dataclasses)

---

## Sub-Task 1 — Define the Task Data Model

**Intent:** Create `task.py` with the `Task` class that represents a single student task. This is the foundation every other module depends on.

**Expected Outcomes:**
- A `Task` class with all required fields
- Fields: `task_id` (UUID str), `title`, `description`, `subject`, `priority`, `due_date` (date), `estimated_hours` (float), `status`, `created_at` (datetime)
- Priority values: `"Low"`, `"Medium"`, `"High"`
- Status values: `"Pending"`, `"Completed"`
- A method to convert a Task to a plain dict (for JSON serialization)
- A class method to rebuild a Task from a plain dict (for JSON deserialization)

**Todo List:**
1. Create `task.py`
2. Define the `Task` class using `@dataclass` or a plain class
3. Auto-generate `task_id` using `uuid.uuid4()` if not provided
4. Auto-set `created_at` to `datetime.now()` if not provided
5. Add `to_dict()` instance method that converts all fields to JSON-safe types (dates as ISO strings)
6. Add `from_dict(data)` class method that reconstructs a Task from a dict, parsing ISO date strings back to date/datetime

**Relevant Context:**
- `due_date` must be stored as a `datetime.date` object internally, serialized as `"YYYY-MM-DD"` string in JSON
- `created_at` stored as `datetime.datetime`, serialized as ISO string
- No external libraries needed

**Status:** [ ] pending

---

## Sub-Task 2 — Build the Storage Layer

**Intent:** Create `storage.py` with a `Storage` class that saves and loads the task list from a local `tasks.json` file. This decouples persistence from business logic.

**Expected Outcomes:**
- `Storage` class with `save(tasks)` and `load()` methods
- `save(tasks)` writes a list of Task objects as a JSON array to `tasks.json`
- `load()` reads `tasks.json` and returns a list of Task objects
- On first run (file missing): `load()` returns an empty list without crashing
- On corrupted JSON: `load()` shows a warning and returns an empty list

**Todo List:**
1. Create `storage.py`
2. Define `Storage` class with a configurable filename (default `"tasks.json"`)
3. Implement `save(tasks: list[Task]) -> None` — serialize each task with `task.to_dict()`, write with `json.dump`
4. Implement `load() -> list[Task]` — read file, parse JSON, reconstruct each task with `Task.from_dict()`
5. Wrap `load()` in try/except for `FileNotFoundError` (return `[]`) and `json.JSONDecodeError` (return `[]`, print warning)

**Relevant Context:**
- Depends on `Task.to_dict()` and `Task.from_dict()` from Sub-Task 1
- File is saved in the project root directory

**Status:** [ ] pending

---

## Sub-Task 3 — Build Utility Helpers

**Intent:** Create `utils.py` with small, reusable helper functions for input validation and date calculations used by the UI and TaskManager.

**Expected Outcomes:**
- `is_valid_title(title)` — returns False if title is empty or under 3 characters
- `is_valid_hours(value)` — returns False if value is not a positive number or exceeds 100
- `days_until_due(due_date)` — returns integer number of days from today to due_date (negative = overdue)
- `normalize_subject(subject)` — strips whitespace and applies title case

**Todo List:**
1. Create `utils.py`
2. Implement `is_valid_title(title: str) -> bool`
3. Implement `is_valid_hours(value) -> bool`
4. Implement `days_until_due(due_date: date) -> int`
5. Implement `normalize_subject(subject: str) -> str`

**Relevant Context:**
- All functions are pure (no side effects, no imports of other project modules)
- Use `datetime.date.today()` for date comparisons

**Status:** [ ] pending

---

## Sub-Task 4 — Build the Task Manager

**Intent:** Create `task_manager.py` with a `TaskManager` class that holds the in-memory list of tasks and exposes all CRUD and query operations. This is the core business logic layer.

**Expected Outcomes:**
- `TaskManager` is initialized with a `Storage` instance; loads tasks from storage on init
- `add_task(...)` creates a Task, appends it, saves — returns the new Task
- `update_task(task_id, **fields)` updates any editable field on a task by ID, saves — returns True/False
- `update_status(task_id, status)` toggles status between Pending/Completed, saves
- `delete_task(task_id)` removes a task by ID, saves — returns True/False
- `get_all_tasks()` returns the full list
- `get_pending_tasks()` returns tasks with status == "Pending"
- `get_completed_tasks()` returns tasks with status == "Completed"
- `get_overdue_tasks()` returns Pending tasks where due_date < today
- `get_upcoming_tasks()` returns Pending tasks where due_date >= today
- `get_tasks_by_subject(subject)` returns tasks matching a subject (case-insensitive)
- `total_pending_hours()` sums estimated_hours for Pending tasks
- `get_stats()` returns a dict: total_tasks, completed_count, pending_count, completion_pct, total_pending_hours, subjects list

**Todo List:**
1. Create `task_manager.py`
2. Define `TaskManager.__init__(storage: Storage)` — load tasks from storage
3. Implement `add_task(title, description, subject, priority, due_date, estimated_hours)` — normalize subject via utils, create Task, save
4. Implement `update_task(task_id, **fields)` — find task by ID, update allowed fields, save
5. Implement `update_status(task_id, status)` — find task by ID, set status, save
6. Implement `delete_task(task_id)` — find and remove, save
7. Implement all `get_*` query methods using list comprehensions
8. Implement `total_pending_hours()` and `get_stats()`

**Relevant Context:**
- Depends on `task.py`, `storage.py`, `utils.py`
- All mutations must call `self.storage.save(self.tasks)` after modifying the list
- `get_stats()` output shape: `{"total": int, "completed": int, "pending": int, "pct_done": float, "pending_hours": float, "subjects": list[str]}`

**Status:** [ ] pending

---

## Sub-Task 5 — Build the AI Advisor

**Intent:** Create `ai_advisor.py` with an `AIAdvisor` class that reads the task list and returns a list of human-readable suggestion strings using simple rule-based logic. No ML required.

**Expected Outcomes:**
- `AIAdvisor.get_suggestions(tasks, stats)` returns a list of 0 or more suggestion strings
- Six rules are implemented (see rules below)
- Each rule contributes at most one suggestion string
- If no rules fire, returns a single "All looks good!" message

**Rules to implement:**

| Rule | Condition | Suggestion text |
|---|---|---|
| Urgency Warning | High priority + Pending + due within 2 days | "⚠️ [Title] is high priority and due very soon. Start immediately." |
| Overdue Alert | Pending + due_date < today | "🔴 [Title] is overdue! Complete or reschedule it today." |
| Heavy Workload | total_pending_hours > 20 | "📚 You have X hours of pending work. Try breaking tasks into shorter study sessions." |
| Easy Wins | Low priority + Pending + estimated_hours <= 1 | "✅ [Title] only takes about 1 hour. Knock it out quickly to clear your list." |
| No Progress | completed_count == 0 AND total_tasks > 3 | "🚀 You haven't completed any tasks yet. Start with the shortest High priority task." |
| Great Progress | completion_pct >= 80 | "🎉 You've completed X% of your tasks. Excellent work — keep the momentum going!" |

**Todo List:**
1. Create `ai_advisor.py`
2. Define `AIAdvisor` class with `get_suggestions(tasks: list[Task], stats: dict) -> list[str]`
3. Implement each of the six rules as private helper methods or inline logic
4. Collect all triggered suggestion strings into a result list
5. Return `["✅ All looks good! Keep up the great work."]` if result list is empty

**Relevant Context:**
- Depends on `task.py` and `utils.py` (for `days_until_due`)
- Receives the pre-computed `stats` dict from `TaskManager.get_stats()` to avoid recomputing
- Rules for Urgency Warning and Easy Wins may produce multiple suggestions (one per matching task)

**Status:** [ ] pending

---

## Sub-Task 6 — Build the Streamlit UI

**Intent:** Create `app.py` as the Streamlit entry point that wires all modules together and renders the full user interface across logical sections.

**Expected Outcomes:**
- App loads with `TaskManager` and `Storage` initialized in `st.session_state` (survives reruns)
- Sidebar navigation or tabs for: Add Task, View Tasks, Statistics, AI Suggestions
- **Add Task section:** form with all fields, validation messages shown inline, saves on submit
- **Edit Task section:** select a task by title, pre-fill form with existing values, save changes
- **View Tasks section:** shows All Tasks, Upcoming Tasks, Overdue Tasks, Completed Tasks as separate sub-views or tabs; each shows a table/card with key fields
- **By Subject section:** dropdown of known subjects, shows matching tasks
- **Statistics section:** displays total tasks, completed count, % done, total pending hours
- **AI Suggestions section:** calls `AIAdvisor.get_suggestions()` and renders results as bullet points
- Friendly empty-state messages when no tasks exist
- Delete button per task with a confirmation checkbox

**UI Sections / Layout:**

```
Sidebar: App title + navigation selector
Main area (selected section):
  [Add Task]    — form: title, description, subject, priority, due date, hours
  [Edit Task]   — select task + same form pre-filled
  [View Tasks]  — tabs: All | Upcoming | Overdue | Completed | By Subject
  [Statistics]  — metrics: total, done, pending hours, % complete
  [AI Tips]     — bulleted suggestion list from AIAdvisor
```

**Todo List:**
1. Create `app.py`
2. Initialize `Storage` and `TaskManager` in `st.session_state` on first load
3. Build sidebar navigation using `st.sidebar.radio`
4. Build **Add Task** section with `st.form`, all field widgets, validation on submit
5. Build **Edit Task** section — selectbox of task titles, pre-filled form, update on submit
6. Build **View Tasks** section — use `st.tabs` for All/Upcoming/Overdue/Completed/By Subject
7. Build per-task display with status toggle button and delete button (with confirm checkbox)
8. Build **Statistics** section using `st.metric` widgets
9. Build **AI Tips** section calling `AIAdvisor` and rendering suggestions

**Relevant Context:**
- Use `st.session_state["task_manager"]` to hold the single `TaskManager` instance
- All Streamlit form submissions trigger a page rerun — task list in session_state will be up to date automatically after each save
- Due date field uses `st.date_input` with `min_value=date.today()` to prevent past dates on create
- Priority uses `st.selectbox(options=["Low", "Medium", "High"])`
- Subject field uses `st.text_input` (free text)

**Status:** [ ] pending

---

## Data Flow Summary

```
app.py (Streamlit UI)
  └─ TaskManager (task_manager.py)
       ├─ Task objects (task.py)
       ├─ Storage (storage.py) ──► tasks.json
       └─ utils.py (validation + date helpers)

app.py
  └─ AIAdvisor (ai_advisor.py)
       ├─ Task objects
       └─ stats dict from TaskManager.get_stats()
```

## File Checklist

| File | Sub-Task | Purpose |
|---|---|---|
| `task.py` | 1 | Task data model |
| `storage.py` | 2 | JSON persistence |
| `utils.py` | 3 | Validation + date helpers |
| `task_manager.py` | 4 | Business logic / CRUD |
| `ai_advisor.py` | 5 | Rule-based AI suggestions |
| `app.py` | 6 | Streamlit UI entry point |
| `tasks.json` | auto | Created at runtime, not committed |

## Implementation Notes

- All modules are independent of Streamlit — only `app.py` imports Streamlit. This makes the logic easy to test or reuse.
- No third-party libraries beyond Streamlit are needed.
- Run the app with: `streamlit run app.py`
