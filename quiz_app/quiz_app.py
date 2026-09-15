"""
Streamlit Course Knowledge Quiz
===============================
Run from PowerShell with:
    python -m streamlit run quiz_app.py

This app demonstrates how st.session_state preserves quiz progress even though
Streamlit reruns the complete script after every button click.
"""

import streamlit as st


# Configure the browser tab before displaying any other Streamlit elements.
st.set_page_config(
    page_title="Course Knowledge Quiz",
    page_icon="🧠",
    layout="centered",
)


# ── Hardcoded quiz data ──────────────────────────────────────────────────────
# The answer value stores the index of the correct option in each options list.
questions = [
    {
        "topic": "HTML",
        "question": "What does HTML stand for?",
        "options": [
            "Hyper Text Markup Language",
            "High Tech Modern Language",
            "Hyper Transfer Markup Language",
            "Home Tool Markup Language",
        ],
        "answer": 0,
    },
    {
        "topic": "CSS",
        "question": "Which CSS property changes the color of text?",
        "options": [
            "font-color",
            "text-color",
            "color",
            "foreground-color",
        ],
        "answer": 2,
    },
    {
        "topic": "JavaScript",
        "question": "Which keyword declares a constant in JavaScript?",
        "options": [
            "let",
            "const",
            "var",
            "constant",
        ],
        "answer": 1,
    },
    {
        "topic": "Python",
        "question": "Which Python data type stores key-value pairs?",
        "options": [
            "List",
            "Tuple",
            "Set",
            "Dictionary",
        ],
        "answer": 3,
    },
    {
        "topic": "APIs",
        "question": "Which HTTP method is normally used to retrieve data?",
        "options": [
            "POST",
            "PATCH",
            "GET",
            "DELETE",
        ],
        "answer": 2,
    },
]


# ── Initialize session state ─────────────────────────────────────────────────
# These values are created only once per user session. On later reruns,
# Streamlit keeps the existing values instead of resetting them.
if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "answered" not in st.session_state:
    st.session_state.answered = False

# This extra value remembers which answer was submitted so feedback remains
# visible after the script reruns.
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None


# ── Page heading ─────────────────────────────────────────────────────────────
st.title("🧠 Course Knowledge Quiz")
st.write("Test your knowledge of HTML, CSS, JavaScript, Python, and APIs.")

total_questions = len(questions)


# ── Results screen ───────────────────────────────────────────────────────────
# current_question equals the list length only after the final Next click.
if st.session_state.current_question >= total_questions:
    final_score = st.session_state.score
    score_percent = round((final_score / total_questions) * 100)

    st.header("Quiz Complete!")
    st.progress(1.0)
    st.metric("Final Score", f"{final_score} / {total_questions}")

    # Display a different result message based on the final percentage.
    if score_percent == 100:
        st.success(f"Perfect score: {score_percent}%! Excellent work!")
        st.balloons()
    elif score_percent >= 80:
        st.success(f"Great job—you scored {score_percent}%!")
    elif score_percent >= 60:
        st.info(f"You scored {score_percent}%. Good progress—keep reviewing!")
    else:
        st.warning(f"You scored {score_percent}%. Review the topics and try again.")

    # Clearing session state also removes old radio-button selections.
    if st.button("Restart Quiz", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()


# ── Question screen ──────────────────────────────────────────────────────────
else:
    question_index = st.session_state.current_question
    current = questions[question_index]
    question_number = question_index + 1

    # Show both a written progress indicator and a visual progress bar.
    st.subheader(f"Question {question_number} of {total_questions}")
    st.progress(question_number / total_questions)
    st.caption(f"Topic: {current['topic']}")

    st.write(f"### {current['question']}")

    # Give every question a unique key so Streamlit keeps its radio selection
    # separate from the selections made on previous questions.
    selected_option = st.radio(
        "Choose one answer:",
        current["options"],
        index=None,
        key=f"answer_{question_index}",
        disabled=st.session_state.answered,
    )

    # Before submission, display only the Submit Answer button.
    if not st.session_state.answered:
        if st.button("Submit Answer", type="primary", use_container_width=True):
            # Require a selection before grading the question.
            if selected_option is None:
                st.warning("Please select an answer before submitting.")
            else:
                # Convert the selected option text back into its list index.
                selected_index = current["options"].index(selected_option)
                st.session_state.selected_answer = selected_index
                st.session_state.answered = True

                # Increase the score only during the first submission.
                if selected_index == current["answer"]:
                    st.session_state.score += 1

                # Rerun immediately to lock the radio widget and show feedback.
                st.rerun()

    # After submission, keep feedback visible and replace Submit with Next.
    else:
        correct_index = current["answer"]
        selected_index = st.session_state.selected_answer
        correct_answer = current["options"][correct_index]

        if selected_index == correct_index:
            st.success("Correct! Well done.")
        else:
            st.error("Incorrect.")
            st.info(f"The correct answer is: **{correct_answer}**")

        st.write(
            f"Current score: **{st.session_state.score} / "
            f"{question_number}**"
        )

        # Label the final Next button clearly before opening the results screen.
        next_label = (
            "View Results"
            if question_number == total_questions
            else "Next Question"
        )

        if st.button(next_label, type="primary", use_container_width=True):
            st.session_state.current_question += 1
            st.session_state.answered = False
            st.session_state.selected_answer = None
            st.rerun()

