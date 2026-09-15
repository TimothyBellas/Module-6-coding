"""
Personal Study Progress Dashboard
=================================
Run from PowerShell with:
    python -m streamlit run my_dashboard.py

The data is intentionally hardcoded because this assignment focuses on
Streamlit's professional layout tools rather than external data fetching.
"""

from math import ceil

import pandas as pd
import streamlit as st


# set_page_config() must be the first Streamlit command in the file.
st.set_page_config(
    page_title="AI Software Engineering Dashboard",
    page_icon="📚",
    layout="wide",
)


# ── Hardcoded sample data ────────────────────────────────────────────────────
# Each module contains the values used by the metrics and charts.
MODULE_DATA = {
    "Python Foundations": {
        "completed": 20,
        "total": 20,
        "study_hours": 32,
        "last_week_hours": 7,
        "quiz_average": 94,
        "quiz_delta": 3,
        "completed_this_week": 2,
    },
    "SQL & Databases": {
        "completed": 17,
        "total": 20,
        "study_hours": 27,
        "last_week_hours": 6,
        "quiz_average": 89,
        "quiz_delta": 5,
        "completed_this_week": 3,
    },
    "FastAPI & APIs": {
        "completed": 16,
        "total": 24,
        "study_hours": 31,
        "last_week_hours": 8,
        "quiz_average": 91,
        "quiz_delta": 4,
        "completed_this_week": 4,
    },
    "Streamlit": {
        "completed": 7,
        "total": 14,
        "study_hours": 12,
        "last_week_hours": 5,
        "quiz_average": 87,
        "quiz_delta": 6,
        "completed_this_week": 3,
    },
}

# Weekly history supplies a second visual in the Overview tab.
WEEKLY_HOURS = {
    "Week 1": 5,
    "Week 2": 7,
    "Week 3": 6,
    "Week 4": 8,
    "Week 5": 9,
    "Week 6": 10,
}


# ── Sidebar controls ────────────────────────────────────────────────────────
# All four controls affect something displayed in the main dashboard.
with st.sidebar:
    st.header("Dashboard Controls")

    selected_module = st.selectbox(
        "Choose a module",
        list(MODULE_DATA.keys()),
        index=3,
    )

    weekly_goal = st.slider(
        "Weekly study goal (hours)",
        min_value=2,
        max_value=20,
        value=10,
    )

    study_pace = st.radio(
        "Study pace",
        ["Review-focused", "Steady", "Accelerated"],
        index=1,
    )

    show_completed = st.checkbox(
        "Show completed lessons in Details",
        value=True,
    )

    st.divider()
    st.caption("Adjust the controls to update the dashboard instantly.")


# ── Calculations based on the selected controls ─────────────────────────────
module = MODULE_DATA[selected_module]
completed = module["completed"]
total = module["total"]
remaining = total - completed
progress_percent = round((completed / total) * 100)

# The selected pace changes how many lessons are expected per study hour.
pace_rates = {
    "Review-focused": 0.75,
    "Steady": 1.0,
    "Accelerated": 1.25,
}
lessons_per_week = max(1, round(weekly_goal * pace_rates[study_pace]))
projected_weeks = ceil(remaining / lessons_per_week) if remaining else 0
goal_delta = weekly_goal - module["last_week_hours"]


# ── Dashboard title and metric cards ────────────────────────────────────────
st.title("📚 AI Software Engineering Study Dashboard")
st.caption(
    f"Viewing **{selected_module}** • {study_pace} pace • "
    f"{weekly_goal}-hour weekly goal"
)

# Place four metrics in one horizontal row. Each metric includes a delta.
metric_1, metric_2, metric_3, metric_4 = st.columns(4)

with metric_1:
    st.metric(
        "Module Progress",
        f"{progress_percent}%",
        delta=f"+{module['completed_this_week']} lessons this week",
    )

with metric_2:
    st.metric(
        "Lessons Completed",
        f"{completed} / {total}",
        delta=f"{remaining} remaining",
        delta_color="off",
    )

with metric_3:
    st.metric(
        "Weekly Study Goal",
        f"{weekly_goal} hrs",
        delta=f"{goal_delta:+} hrs vs. last week",
    )

with metric_4:
    st.metric(
        "Quiz Average",
        f"{module['quiz_average']}%",
        delta=f"+{module['quiz_delta']} points",
    )

st.divider()


# ── Tabbed dashboard content ────────────────────────────────────────────────
overview_tab, details_tab = st.tabs(["📊 Overview", "📝 Details"])


with overview_tab:
    st.header("Progress Overview")

    # Use nested columns to place a chart beside the selected-module summary.
    chart_column, summary_column = st.columns([2, 1])

    with chart_column:
        st.subheader("Progress Across All Modules")

        # Build a DataFrame containing one completion percentage per module.
        progress_rows = []
        for module_name, values in MODULE_DATA.items():
            module_progress = round(
                (values["completed"] / values["total"]) * 100
            )
            progress_rows.append(
                {
                    "Module": module_name,
                    "Progress (%)": module_progress,
                }
            )

        progress_df = pd.DataFrame(progress_rows).set_index("Module")
        st.bar_chart(progress_df)

    with summary_column:
        st.subheader("Selected Module")
        st.write(f"**{selected_module}**")
        st.progress(progress_percent / 100)
        st.write(f"{completed} of {total} lessons completed")
        st.write(f"{module['study_hours']} total study hours recorded")

        # The message changes when the sidebar values change.
        if remaining == 0:
            st.success("Module complete! Choose another module to keep going.")
        elif projected_weeks == 1:
            st.success("You are projected to finish this module within one week.")
        elif weekly_goal < module["last_week_hours"]:
            st.warning(
                "Your selected goal is below last week's study time. "
                "Increase it if you want a faster finish."
            )
        else:
            st.info(
                f"At this pace, you could finish in about "
                f"{projected_weeks} weeks."
            )

    st.subheader("Weekly Study Hours")
    weekly_df = pd.DataFrame(
        {
            "Week": list(WEEKLY_HOURS.keys()),
            "Hours": list(WEEKLY_HOURS.values()),
        }
    ).set_index("Week")
    st.line_chart(weekly_df)


with details_tab:
    st.header(f"{selected_module} Lesson Details")
    st.write(
        "Use the sidebar checkbox to include or hide lessons that are already "
        "complete."
    )

    # Generate sample lesson rows for the selected module.
    lesson_rows = []
    for lesson_number in range(1, total + 1):
        is_complete = lesson_number <= completed
        lesson_rows.append(
            {
                "Lesson": f"{selected_module} — Lesson {lesson_number}",
                "Status": "Complete" if is_complete else "Pending",
                "Estimated Time": f"{40 + (lesson_number % 3) * 10} minutes",
                "Priority": (
                    "Review"
                    if is_complete
                    else "High" if lesson_number == completed + 1 else "Normal"
                ),
            }
        )

    # Apply the checkbox filter before sending the rows to the table.
    if show_completed:
        visible_lessons = lesson_rows
    else:
        visible_lessons = [
            lesson for lesson in lesson_rows if lesson["Status"] == "Pending"
        ]

    st.dataframe(
        pd.DataFrame(
            visible_lessons,
            columns=["Lesson", "Status", "Estimated Time", "Priority"],
        ),
        use_container_width=True,
        hide_index=True,
    )

    detail_1, detail_2 = st.columns(2)
    with detail_1:
        st.subheader("Next Goal")
        if remaining:
            st.write(
                f"Complete **Lesson {completed + 1}** and stay near your "
                f"**{weekly_goal}-hour** weekly target."
            )
        else:
            st.write("Review the completed lessons or begin another module.")

    with detail_2:
        st.subheader("Pace Estimate")
        st.write(f"Estimated lessons per week: **{lessons_per_week}**")
        st.write(f"Projected weeks remaining: **{projected_weeks}**")


# ── Supplementary information expander ─────────────────────────────────────
with st.expander("ℹ️ How the dashboard calculates its projections"):
    st.write(
        "The module progress is the number of completed lessons divided by "
        "the total number of lessons."
    )
    st.code("progress = completed_lessons / total_lessons * 100")
    st.write(
        "The finish estimate combines the weekly-hours slider with the selected "
        "study pace. Review-focused uses 0.75 lessons per hour, Steady uses "
        "1.0, and Accelerated uses 1.25. All values are demonstration data."
    )
