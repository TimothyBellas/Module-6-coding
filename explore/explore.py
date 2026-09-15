"""
Interactive Streamlit Widget Explorer
=====================================
Run this app from PowerShell with:
    streamlit run explore.py

Topic: Gaming Session Planner
"""

from datetime import date

import streamlit as st


# Configure the browser tab before displaying any other Streamlit content.
st.set_page_config(
    page_title="Gaming Session Planner",
    page_icon="🎮",
    layout="centered",
)


# ── Page introduction ────────────────────────────────────────────────────────
st.title("🎮 Gaming Session Planner")
st.write(
    "Customize a gaming session below. The recommendations, calculations, "
    "and summary update whenever you change a widget."
)


# ── Interactive widgets ─────────────────────────────────────────────────────
st.header("Build Your Session")

# Widget 1: text_input collects a short piece of text.
player_name = st.text_input(
    "Player name",
    placeholder="Enter your name",
)

# Widget 2: selectbox allows one choice from a drop-down list.
game_genre = st.selectbox(
    "Game genre",
    ["Role-Playing Game", "Action", "Strategy", "Sports", "Puzzle"],
)

# Widget 3: radio displays all choices while allowing only one selection.
difficulty = st.radio(
    "Session style",
    ["Relaxed", "Balanced", "Challenge Mode"],
    horizontal=True,
)

# Widget 4: slider selects a number by dragging along a range.
session_hours = st.slider(
    "Planned session length (hours)",
    min_value=1,
    max_value=10,
    value=3,
)

# Widget 5: number_input accepts a numeric value with optional step buttons.
snack_cost_per_hour = st.number_input(
    "Snack and drink budget per hour ($)",
    min_value=0.0,
    max_value=25.0,
    value=4.0,
    step=0.5,
)

# Widget 6: multiselect allows any number of choices, including none.
session_goals = st.multiselect(
    "Session goals",
    [
        "Main story",
        "Side quests",
        "Multiplayer",
        "Achievement hunting",
        "Practice skills",
    ],
    default=["Main story"],
)

# Widget 7: checkbox stores either True (checked) or False (unchecked).
include_breaks = st.checkbox(
    "Schedule a 10-minute break every 2 hours",
    value=True,
)

# Widget 8: date_input opens a calendar for choosing the session date.
session_date = st.date_input(
    "Session date",
    value=date.today(),
)

# Widget 9: text_area is useful for longer, optional text.
notes = st.text_area(
    "Optional notes",
    placeholder="Games to play, friends to invite, goals to remember...",
)


# ── Conditional recommendations ─────────────────────────────────────────────
st.header("Your Gaming Plan")

# Use a fallback label when the player leaves the name input empty.
display_name = player_name.strip() or "Player"

# The message changes according to the selected game genre.
if game_genre == "Role-Playing Game":
    st.info("RPG tip: Save before major decisions and leave time to explore.")
elif game_genre == "Action":
    st.info("Action tip: Start with a short warm-up round before harder levels.")
elif game_genre == "Strategy":
    st.info("Strategy tip: Review your resources and objectives before each match.")
elif game_genre == "Sports":
    st.info("Sports tip: Play a practice match before starting competitive games.")
else:
    st.info("Puzzle tip: Take a short break if you get stuck on the same problem.")


# ── Calculations that use widget values ─────────────────────────────────────
# Multiply two widget values to estimate the complete snack and drink budget.
total_snack_budget = session_hours * snack_cost_per_hour

# Calculate the number of breaks and how much active gaming time remains.
break_count = session_hours // 2 if include_breaks else 0
break_minutes = break_count * 10
total_minutes = session_hours * 60
active_play_minutes = total_minutes - break_minutes
active_hours, remaining_minutes = divmod(active_play_minutes, 60)

# Display the calculated results in three metric cards.
metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Estimated Budget", f"${total_snack_budget:.2f}")
metric_col2.metric("Scheduled Breaks", break_count)
metric_col3.metric(
    "Active Play Time",
    f"{active_hours}h {remaining_minutes}m",
)

# The progress bar compares the chosen length with an eight-hour maximum goal.
# min() prevents values over eight hours from exceeding 100%.
length_progress = min(session_hours / 8, 1.0)
st.write("**Session-length meter**")
st.progress(length_progress)


# ── More content that changes with widget values ────────────────────────────
# Show feedback based on the selected duration and difficulty.
if session_hours >= 6 and not include_breaks:
    st.warning("Long session planned: consider enabling scheduled breaks.")
elif difficulty == "Challenge Mode" and session_hours >= 5:
    st.warning("Challenge Mode plus a long session may become tiring—pace yourself.")
elif session_hours <= 3:
    st.success("This is a manageable session length. Have fun!")
else:
    st.success("Your session is planned. Remember to stretch and stay hydrated!")

# Create readable text from the multiselect choices.
if session_goals:
    goals_text = ", ".join(session_goals)
else:
    goals_text = "No specific goals selected"

# Summarize several widget values in one dynamically generated sentence.
st.subheader(f"{display_name}'s Session Summary")
st.write(
    f"On **{session_date.strftime('%B %d, %Y')}**, you plan to play a "
    f"**{game_genre}** in **{difficulty}** style for **{session_hours} "
    f"hour{'s' if session_hours != 1 else ''}**."
)
st.write(f"**Goals:** {goals_text}")

# Only display the notes section when the user entered some text.
if notes.strip():
    st.write("**Notes:**")
    st.write(notes.strip())

# A caption documents the nine widget types demonstrated in this app.
st.caption(
    "Widgets used: text input, selectbox, radio, slider, number input, "
    "multiselect, checkbox, date input, and text area."
)
