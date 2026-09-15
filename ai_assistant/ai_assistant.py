"""
Customizable Streamlit AI Assistant
===================================
Run from PowerShell with:
    python -m streamlit run ai_assistant.py

This version uses a meaningful local mock response, so it works without an API
key. The mock response streams one small piece at a time and demonstrates how a
system prompt and optional context areas can shape an AI assistant.
"""

import time

import streamlit as st


# Configure the browser tab before displaying any other Streamlit elements.
st.set_page_config(
    page_title="Custom AI Assistant",
    page_icon="🤖",
    layout="wide",
)


# The user can edit this starting personality in the sidebar.
DEFAULT_SYSTEM_PROMPT = (
    "You are a patient and encouraging coding tutor. Explain ideas in plain "
    "language, give practical examples, and avoid unnecessary jargon."
)

# Each selected checkbox appends one of these instructions to the base prompt.
CONTEXT_INSTRUCTIONS = {
    "Python expertise": (
        "Use Python best practices, small functions, clear variable names, "
        "type hints when helpful, and safe exception handling."
    ),
    "Web development context": (
        "Consider HTML, CSS, JavaScript, frontend/backend communication, HTTP, "
        "accessibility, and responsive design when relevant."
    ),
    "AI/ML context": (
        "Consider data quality, model inputs and outputs, evaluation, bias, "
        "privacy, and responsible AI practices when relevant."
    ),
}


# ── Session-state setup ──────────────────────────────────────────────────────
# Chat messages must live in session state because Streamlit reruns this entire
# script whenever the user sends a message or changes a sidebar control.
if "messages" not in st.session_state:
    st.session_state.messages = []


def clear_chat():
    """Remove the saved conversation while keeping sidebar preferences."""

    st.session_state.messages = []


def mock_response(prompt, selected_contexts, effective_system_prompt):
    """Yield a contextual mock response in small chunks for visible streaming."""

    # Create a short, readable version of the current system prompt.
    prompt_preview = " ".join(effective_system_prompt.split())
    if len(prompt_preview) > 180:
        prompt_preview = f"{prompt_preview[:177]}..."

    context_label = (
        ", ".join(selected_contexts)
        if selected_contexts
        else "general knowledge"
    )

    # Add practical guidance for every context checkbox that is active.
    guidance = []

    if "Python expertise" in selected_contexts:
        guidance.append(
            "- **Python:** Break the solution into small functions, use clear "
            "names, and handle likely errors explicitly."
        )

    if "Web development context" in selected_contexts:
        guidance.append(
            "- **Web development:** Separate the interface from the data logic "
            "and verify the full request-and-response flow."
        )

    if "AI/ML context" in selected_contexts:
        guidance.append(
            "- **AI/ML:** Define the input, expected output, and a way to evaluate "
            "whether the result is useful and responsible."
        )

    if not guidance:
        guidance.append(
            "- **General approach:** Clarify the goal, divide it into smaller "
            "steps, and test one step at a time."
        )

    guidance_text = "\n".join(guidance)

    response = (
        f"**Mock assistant response**\n\n"
        f"You asked: _{prompt.strip()}_\n\n"
        f"I am answering with **{context_label}** as my active context. Here is "
        f"the approach I would emphasize:\n\n"
        f"{guidance_text}\n\n"
        f"The active system prompt begins: _{prompt_preview}_\n\n"
        f"This local mock demonstrates how the system prompt and "
        f"{len(selected_contexts)} selected context area"
        f"{'s' if len(selected_contexts) != 1 else ''} shape the response. "
        f"A production version could send the same conversation and effective "
        f"system prompt to an AI API."
    )

    # Yield one word at a time so st.write_stream() displays a streaming reply.
    for word in response.split(" "):
        yield f"{word} "
        time.sleep(0.02)


# ── Customization sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.header("Assistant Settings")

    system_prompt = st.text_area(
        "System prompt",
        value=DEFAULT_SYSTEM_PROMPT,
        height=180,
        help="Describe the AI's personality, tone, and general behavior.",
    )

    st.subheader("Additional Context")

    include_python = st.checkbox("Include Python expertise")
    include_web = st.checkbox("Include web development context")
    include_ai = st.checkbox("Include AI/ML context")

    # Build a list from the currently selected checkboxes.
    selected_contexts = []
    if include_python:
        selected_contexts.append("Python expertise")
    if include_web:
        selected_contexts.append("Web development context")
    if include_ai:
        selected_contexts.append("AI/ML context")

    # Start with the editable personality and append the selected instructions.
    effective_system_prompt = system_prompt.strip() or DEFAULT_SYSTEM_PROMPT

    if selected_contexts:
        appended_context = "\n".join(
            f"- {CONTEXT_INSTRUCTIONS[context]}"
            for context in selected_contexts
        )
        effective_system_prompt += (
            "\n\nAdditional context instructions:\n" + appended_context
        )

    # This preview makes it clear that the checkboxes alter the final prompt.
    with st.expander("Preview effective system prompt"):
        st.code(effective_system_prompt, language="text")

    st.button(
        "Clear Chat",
        type="secondary",
        use_container_width=True,
        on_click=clear_chat,
    )

    st.caption(
        f"Mock mode • {len(selected_contexts)} context area"
        f"{'s' if len(selected_contexts) != 1 else ''} selected"
    )


# ── Main chat interface ──────────────────────────────────────────────────────
st.title("🤖 Custom AI Assistant")
st.caption(
    "Edit the assistant personality, select context areas, and start chatting."
)

if not st.session_state.messages:
    st.info("No messages yet. Ask something in the chat box below.")

# Re-render every saved message from oldest to newest on each script run.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# st.chat_input() returns the submitted text and triggers a complete script run.
user_prompt = st.chat_input("Ask the assistant something...")

if user_prompt:
    # Save and immediately display the new user message.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate, stream, and then save the complete assistant response.
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            assistant_response = st.write_stream(
                mock_response(
                    user_prompt,
                    selected_contexts,
                    effective_system_prompt,
                )
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_response,
        }
    )
