"""
Streamlit Frontend for the FastAPI Task Manager
================================================
Start the provided backend first:
    python -m uvicorn backend:app --reload --port 8000

Then start this frontend in a second terminal:
    python -m streamlit run my_frontend.py
"""

import requests
import streamlit as st


# Configure the Streamlit page before displaying any other elements.
st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="wide",
)

# Change this value if the FastAPI backend uses a different host or port.
API_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 8


# ── Initialize authentication state ──────────────────────────────────────────
# Streamlit reruns the script after every interaction, so the access token and
# username must live in session state instead of ordinary variables.
if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = None

if "username" not in st.session_state:
    st.session_state.username = None


def clear_authentication(message=None):
    """Remove local login information and optionally save a login notice."""

    st.session_state.jwt_token = None
    st.session_state.username = None

    if message:
        st.session_state.auth_notice = message


def api_request(method, endpoint, requires_auth=True, **kwargs):
    """Send one API request with shared auth and connection-error handling."""

    # Copy any supplied headers so the original dictionary is not changed.
    headers = kwargs.pop("headers", {}).copy()

    # Protected backend routes expect the token in the Authorization header.
    if requires_auth and st.session_state.jwt_token:
        headers["Authorization"] = f"Bearer {st.session_state.jwt_token}"

    try:
        response = requests.request(
            method=method,
            url=f"{API_URL}{endpoint}",
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
    except requests.exceptions.ConnectionError:
        st.error("The FastAPI backend is unreachable.")
        st.info(
            "Start it with: `python -m uvicorn backend:app --reload --port 8000`"
        )
        return None
    except requests.exceptions.Timeout:
        st.error("The backend took too long to respond. Please try again.")
        return None
    except requests.exceptions.RequestException as error:
        st.error(f"The API request failed: {error}")
        return None

    # A 401 from a protected route means the saved token is missing or expired.
    # Clear it and rerun so the login screen becomes the active page again.
    if requires_auth and response.status_code == 401:
        clear_authentication("Your session expired. Please log in again.")
        st.rerun()

    return response


def show_login_page():
    """Display the authentication gate and process login submissions."""

    st.title("🔐 Task Manager Login")
    st.write("Sign in to view and manage your tasks.")

    # Display notices created by logout or an expired-token redirect.
    if "auth_notice" in st.session_state:
        st.warning(st.session_state.pop("auth_notice"))

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_submitted = st.form_submit_button(
            "Log In",
            type="primary",
            use_container_width=True,
        )

    if login_submitted:
        if not username.strip() or not password:
            st.warning("Enter both a username and password.")
            return

        # OAuth2PasswordRequestForm expects form data, not a JSON body.
        response = api_request(
            "POST",
            "/auth/token",
            requires_auth=False,
            data={
                "username": username.strip(),
                "password": password,
            },
        )

        # A connection error was already displayed inside api_request().
        if response is None:
            return

        if response.status_code == 200:
            try:
                token_data = response.json()
                access_token = token_data["access_token"]
            except (ValueError, KeyError):
                st.error("The backend returned an invalid login response.")
                return

            # Save the token and username so later reruns remain authenticated.
            st.session_state.jwt_token = access_token
            st.session_state.username = username.strip()
            st.rerun()
        elif response.status_code == 401:
            st.error("Invalid username or password.")
        else:
            st.error(
                f"Login failed with status code {response.status_code}."
            )


# ── Authentication gate ──────────────────────────────────────────────────────
# Stop here when no token exists so protected dashboard code cannot run.
if not st.session_state.jwt_token:
    show_login_page()
    st.stop()


# ── Authenticated sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.header("Account")
    st.success(f"Signed in as **{st.session_state.username}**")
    st.caption(f"Backend: {API_URL}")

    # A Streamlit button already causes a rerun; this extra rerun occurs after
    # clearing auth so the login gate appears immediately.
    if st.button("Log Out", use_container_width=True):
        clear_authentication("You have been logged out.")
        st.rerun()

    if st.button("Refresh Tasks", use_container_width=True):
        st.rerun()


# ── Load protected dashboard data ────────────────────────────────────────────
tasks_response = api_request("GET", "/tasks")
if tasks_response is None:
    st.stop()

stats_response = api_request("GET", "/stats")
if stats_response is None:
    st.stop()

# Handle unexpected non-401 errors from either endpoint.
if not tasks_response.ok:
    st.error(f"Could not load tasks (HTTP {tasks_response.status_code}).")
    st.stop()

if not stats_response.ok:
    st.error(f"Could not load task statistics (HTTP {stats_response.status_code}).")
    st.stop()

try:
    tasks = tasks_response.json()
    stats = stats_response.json()
except ValueError:
    st.error("The backend returned data that was not valid JSON.")
    st.stop()


# ── Main dashboard heading ───────────────────────────────────────────────────
st.title("✅ Task Manager Dashboard")
st.caption(f"Tasks belonging to {st.session_state.username}")

# Display success messages saved immediately before a previous st.rerun().
if "flash_message" in st.session_state:
    st.success(st.session_state.pop("flash_message"))


# ── Metrics row ──────────────────────────────────────────────────────────────
metric_1, metric_2, metric_3 = st.columns(3)

with metric_1:
    st.metric("Total Tasks", stats.get("total", len(tasks)))

with metric_2:
    completed_count = stats.get(
        "done",
        sum(1 for task in tasks if task.get("done")),
    )
    st.metric("Completed Tasks", completed_count)

with metric_3:
    pending_count = stats.get("pending", len(tasks) - completed_count)
    st.metric("Pending Tasks", pending_count)

st.divider()


# ── Add-task form ────────────────────────────────────────────────────────────
st.header("Add a Task")

with st.form("add_task_form", clear_on_submit=True):
    new_task_title = st.text_input(
        "Task title",
        placeholder="Enter a new task...",
        max_chars=200,
    )
    add_submitted = st.form_submit_button(
        "Add Task",
        type="primary",
    )

if add_submitted:
    clean_title = new_task_title.strip()

    if not clean_title:
        st.warning("Enter a task title before submitting.")
    else:
        create_response = api_request(
            "POST",
            "/tasks",
            json={"title": clean_title},
        )

        if create_response is not None:
            if create_response.status_code == 201:
                st.session_state.flash_message = "Task added successfully."
                st.rerun()
            else:
                st.error(
                    f"The task could not be added "
                    f"(HTTP {create_response.status_code})."
                )


# ── Task list ────────────────────────────────────────────────────────────────
st.header("Your Tasks")

if not tasks:
    st.info("You do not have any tasks yet. Add one above.")
else:
    for task in tasks:
        task_id = task.get("id")
        title = task.get("title", "Untitled task")
        is_done = task.get("done", False)

        # A bordered container keeps each task visually separate.
        with st.container(border=True):
            title_column, status_column, action_column = st.columns([5, 2, 2])

            with title_column:
                st.markdown(f"**Task #{task_id}**")
                st.write(title)

            with status_column:
                if is_done:
                    st.write("✅ Completed")
                else:
                    st.write("⏳ Pending")

            with action_column:
                action_label = "Mark Pending" if is_done else "Mark Complete"

                if st.button(
                    action_label,
                    key=f"toggle_task_{task_id}",
                    use_container_width=True,
                ):
                    toggle_response = api_request(
                        "PATCH",
                        f"/tasks/{task_id}",
                    )

                    if toggle_response is not None:
                        if toggle_response.ok:
                            st.session_state.flash_message = (
                                "Task status updated successfully."
                            )
                            st.rerun()
                        else:
                            st.error(
                                f"The task could not be updated "
                                f"(HTTP {toggle_response.status_code})."
                            )
