"""
app.py — Streamlit UI entry point for the Student Productivity System.
Run with: streamlit run app.py
"""

import streamlit as st
from datetime import date

from storage import Storage
from task_manager import TaskManager
from ai_advisor import AIAdvisor
from utils import is_valid_title, is_valid_hours


# ------------------------------------------------------------------ #
# Bootstrap — initialise once per session                             #
# ------------------------------------------------------------------ #

def get_manager() -> TaskManager:
    if "task_manager" not in st.session_state:
        st.session_state["task_manager"] = TaskManager(Storage())
    return st.session_state["task_manager"]


# ------------------------------------------------------------------ #
# Page config                                                          #
# ------------------------------------------------------------------ #

st.set_page_config(page_title="Student Productivity System", page_icon="📚", layout="wide")
st.title("📚 Student Productivity & Time Management System")

tm = get_manager()
advisor = AIAdvisor()

PRIORITIES = ["Low", "Medium", "High"]

# ------------------------------------------------------------------ #
# Sidebar navigation                                                   #
# ------------------------------------------------------------------ #

page = st.sidebar.radio(
    "Navigate",
    ["➕ Add Task", "✏️ Edit Task", "📋 View Tasks", "📊 Statistics", "🤖 AI Tips"],
)

# ------------------------------------------------------------------ #
# Helper: render a single task card                                    #
# ------------------------------------------------------------------ #

def render_task_card(task, key_suffix: str):
    """Render one task as an expander with action buttons."""
    days = (task.due_date - date.today()).days
    if task.status == "Completed":
        due_label = "✅ Completed"
    elif days < 0:
        due_label = f"🔴 Overdue by {abs(days)} day(s)"
    elif days == 0:
        due_label = "🟡 Due today"
    else:
        due_label = f"🟢 Due in {days} day(s)"

    label = f"**{task.title}** — {task.subject} | {task.priority} priority | {due_label}"
    with st.expander(label):
        st.write(f"**Description:** {task.description or '—'}")
        st.write(f"**Due date:** {task.due_date.strftime('%d %b %Y')}")
        st.write(f"**Estimated time:** {task.estimated_hours} hour(s)")
        st.write(f"**Status:** {task.status}")
        st.write(f"**Created:** {task.created_at.strftime('%d %b %Y %H:%M')}")

        col1, col2 = st.columns(2)

        # Toggle status button
        with col1:
            new_status = "Completed" if task.status == "Pending" else "Pending"
            btn_label = "✅ Mark as Completed" if task.status == "Pending" else "↩️ Mark as Pending"
            if st.button(btn_label, key=f"status_{task.task_id}_{key_suffix}"):
                tm.update_status(task.task_id, new_status)
                st.rerun()

        # Delete with confirmation
        with col2:
            confirm_key = f"confirm_del_{task.task_id}_{key_suffix}"
            confirmed = st.checkbox("Confirm delete", key=confirm_key)
            if confirmed:
                if st.button("🗑️ Delete Task", key=f"delete_{task.task_id}_{key_suffix}"):
                    tm.delete_task(task.task_id)
                    st.rerun()


# ------------------------------------------------------------------ #
# ➕ Add Task                                                          #
# ------------------------------------------------------------------ #

if page == "➕ Add Task":
    st.header("➕ Add New Task")

    with st.form("add_task_form"):
        title = st.text_input("Task Title *", placeholder="e.g. Write Chapter 3 Summary")
        description = st.text_area("Description (optional)", placeholder="Short notes about this task")
        subject = st.text_input("Subject / Category *", placeholder="e.g. Mathematics")
        priority = st.selectbox("Priority *", PRIORITIES, index=1)
        due_date = st.date_input("Due Date *", min_value=date.today(), value=date.today())
        estimated_hours = st.number_input("Estimated Hours *", min_value=0.1, max_value=100.0, value=1.0, step=0.5)
        submitted = st.form_submit_button("Add Task")

    if submitted:
        errors = []
        if not is_valid_title(title):
            errors.append("Task title must be at least 3 characters.")
        if not subject.strip():
            errors.append("Subject / Category cannot be empty.")
        if not is_valid_hours(estimated_hours):
            errors.append("Estimated hours must be between 0.1 and 100.")

        if errors:
            for e in errors:
                st.warning(e)
        else:
            tm.add_task(
                title=title,
                subject=subject,
                priority=priority,
                due_date=due_date,
                estimated_hours=estimated_hours,
                description=description,
            )
            st.success(f"✅ Task **'{title}'** added successfully!")


# ------------------------------------------------------------------ #
# ✏️ Edit Task                                                         #
# ------------------------------------------------------------------ #

elif page == "✏️ Edit Task":
    st.header("✏️ Edit Existing Task")

    all_tasks = tm.get_all_tasks()
    if not all_tasks:
        st.info("No tasks yet. Add a task first.")
    else:
        task_options = {f"{t.title} ({t.subject})": t.task_id for t in all_tasks}
        selected_label = st.selectbox("Select a task to edit", list(task_options.keys()))
        selected_id = task_options[selected_label]
        task = tm._find(selected_id)

        if task:
            with st.form("edit_task_form"):
                new_title = st.text_input("Task Title *", value=task.title)
                new_description = st.text_area("Description", value=task.description)
                new_subject = st.text_input("Subject / Category *", value=task.subject)
                new_priority = st.selectbox("Priority *", PRIORITIES, index=PRIORITIES.index(task.priority))
                new_due_date = st.date_input("Due Date *", value=task.due_date)
                new_hours = st.number_input("Estimated Hours *", min_value=0.1, max_value=100.0, value=task.estimated_hours, step=0.5)
                save = st.form_submit_button("Save Changes")

            if save:
                errors = []
                if not is_valid_title(new_title):
                    errors.append("Task title must be at least 3 characters.")
                if not new_subject.strip():
                    errors.append("Subject / Category cannot be empty.")
                if not is_valid_hours(new_hours):
                    errors.append("Estimated hours must be between 0.1 and 100.")

                if errors:
                    for e in errors:
                        st.warning(e)
                else:
                    tm.update_task(
                        selected_id,
                        title=new_title,
                        description=new_description,
                        subject=new_subject,
                        priority=new_priority,
                        due_date=new_due_date,
                        estimated_hours=new_hours,
                    )
                    st.success("✅ Task updated successfully!")


# ------------------------------------------------------------------ #
# 📋 View Tasks                                                        #
# ------------------------------------------------------------------ #

elif page == "📋 View Tasks":
    st.header("📋 View Tasks")

    tab_all, tab_upcoming, tab_overdue, tab_completed, tab_subject = st.tabs(
        ["All Tasks", "⏰ Upcoming", "🔴 Overdue", "✅ Completed", "📁 By Subject"]
    )

    def show_task_list(tasks, tab_name):
        if not tasks:
            st.info("No tasks found in this category.")
        else:
            for task in tasks:
                render_task_card(task, key_suffix=tab_name)

    with tab_all:
        show_task_list(tm.get_all_tasks(), "all")

    with tab_upcoming:
        show_task_list(tm.get_upcoming_tasks(), "upcoming")

    with tab_overdue:
        tasks = tm.get_overdue_tasks()
        if not tasks:
            st.success("🎉 No overdue tasks! Great job staying on top of things.")
        else:
            for task in tasks:
                render_task_card(task, key_suffix="overdue")

    with tab_completed:
        tasks = tm.get_completed_tasks()
        if not tasks:
            st.info("No completed tasks yet. Keep working!")
        else:
            st.write(f"You have completed **{len(tasks)}** task(s). Well done! 🎉")
            for task in tasks:
                render_task_card(task, key_suffix="completed")

    with tab_subject:
        subjects = tm.get_subjects()
        if not subjects:
            st.info("No subjects found. Add some tasks first.")
        else:
            chosen = st.selectbox("Choose a subject", subjects)
            show_task_list(tm.get_tasks_by_subject(chosen), "subject")


# ------------------------------------------------------------------ #
# 📊 Statistics                                                        #
# ------------------------------------------------------------------ #

elif page == "📊 Statistics":
    st.header("📊 Productivity Statistics")

    stats = tm.get_stats()

    if stats["total"] == 0:
        st.info("No tasks yet. Start by adding some tasks!")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Tasks", stats["total"])
        col2.metric("Completed", stats["completed"])
        col3.metric("Pending", stats["pending"])
        col4.metric("% Complete", f"{stats['pct_done']}%")

        st.metric("⏱️ Total Pending Study Hours", f"{stats['pending_hours']} hr(s)")

        if stats["pct_done"] == 100:
            st.balloons()
            st.success("🎉 You've completed ALL your tasks! Amazing work!")
        elif stats["pending_hours"] == 0 and stats["pending"] == 0:
            st.success("🎉 Nothing pending — great job!")

        if stats["subjects"]:
            st.subheader("Tasks by Subject")
            for subj in stats["subjects"]:
                subj_tasks = tm.get_tasks_by_subject(subj)
                done = sum(1 for t in subj_tasks if t.status == "Completed")
                st.write(f"**{subj}** — {len(subj_tasks)} task(s), {done} completed")


# ------------------------------------------------------------------ #
# 🤖 AI Tips                                                           #
# ------------------------------------------------------------------ #

elif page == "🤖 AI Tips":
    st.header("🤖 AI-Powered Study Tips")
    st.caption("Smart suggestions based on your current tasks, priorities, and deadlines.")

    all_tasks = tm.get_all_tasks()
    if not all_tasks:
        st.info("Add some tasks first to get personalised suggestions.")
    else:
        stats = tm.get_stats()
        suggestions = advisor.get_suggestions(all_tasks, stats)
        for tip in suggestions:
            st.markdown(f"- {tip}")
