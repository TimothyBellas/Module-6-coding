"""
JSONPlaceholder User Data Explorer
==================================
Run from PowerShell with:
    python -m streamlit run data_explorer.py

This app fetches user data from a public API, caches the response, and displays
the results with metrics, a filterable dataframe, and a city bar chart.
"""

import pandas as pd
import requests
import streamlit as st


# Configure the browser tab before displaying other Streamlit elements.
st.set_page_config(
    page_title="User Data Explorer",
    page_icon="🌐",
    layout="wide",
)

# Keep the endpoint in one constant so it is easy to update later.
API_URL = "https://jsonplaceholder.typicode.com/users"


# ── Fetch and cache API data ─────────────────────────────────────────────────
# st.cache_data stores the returned list for one hour. Widget interactions rerun
# this script, but they reuse the cached value instead of repeating the request.
@st.cache_data(ttl=3600, show_spinner="Fetching users from the API...")
def fetch_users():
    """Fetch and return the JSONPlaceholder users list."""

    # timeout prevents the app from waiting forever if the service is offline.
    response = requests.get(API_URL, timeout=10)

    # Raise a requests exception for unsuccessful status codes such as 404/500.
    response.raise_for_status()

    # Convert the JSON response body into Python lists and dictionaries.
    users = response.json()

    # Protect the rest of the app from an unexpected response structure.
    if not isinstance(users, list):
        raise ValueError("The API returned an unexpected data format.")

    return users


# ── Page heading ─────────────────────────────────────────────────────────────
st.title("🌐 JSONPlaceholder User Data Explorer")
st.write(
    "Explore user, city, and company information loaded from the "
    "JSONPlaceholder API."
)


# ── Load data with friendly error handling ──────────────────────────────────
try:
    users = fetch_users()
except (requests.RequestException, ValueError) as error:
    st.error("The user data could not be loaded.")
    st.info("Check your internet connection, then reload the app and try again.")
    st.code(str(error))
    st.stop()


# Extract the nested API fields into flat rows that work well in a DataFrame.
rows = []
for user in users:
    rows.append(
        {
            "ID": user["id"],
            "Name": user["name"],
            "Username": user["username"],
            "Email": user["email"],
            "City": user["address"]["city"],
            "Company": user["company"]["name"],
        }
    )

users_df = pd.DataFrame(rows)


# Clear both kinds of saved state used by this page. Streamlit runs button
# callbacks before rerunning the script, so the next run receives a fresh API
# response and an empty search box.
def clear_cache_and_filter():
    """Clear the cached API response and reset the name filter."""

    fetch_users.clear()
    st.session_state["name_filter"] = ""


# ── Sidebar controls ─────────────────────────────────────────────────────────
st.sidebar.header("Filter Users")

# This filter matches any part of a user's name and ignores capitalization.
name_filter = st.sidebar.text_input(
    "Search by name",
    placeholder="Example: Leanne",
    key="name_filter",
)

# The callback clears the API cache and the widget's session-state value.
st.sidebar.button(
    "Clear Cache and Reload",
    use_container_width=True,
    on_click=clear_cache_and_filter,
)

st.sidebar.caption(
    "API responses are cached for one hour. Clearing the cache also resets "
    "the name filter."
)


# Apply the sidebar filter to both the table and chart.
if name_filter.strip():
    filtered_df = users_df[
        users_df["Name"].str.contains(
            name_filter.strip(),
            case=False,
            na=False,
            regex=False,
        )
    ]
else:
    # copy() keeps filtered_df independent from the original DataFrame.
    filtered_df = users_df.copy()


# ── Metrics row ──────────────────────────────────────────────────────────────
# These metrics summarize the full API dataset, independent of the name filter.
total_users = len(users_df)
unique_cities = users_df["City"].nunique()
unique_companies = users_df["Company"].nunique()

metric_1, metric_2, metric_3 = st.columns(3)

with metric_1:
    st.metric("Total Users", total_users)

with metric_2:
    st.metric("Unique Cities", unique_cities)

with metric_3:
    st.metric("Unique Companies", unique_companies)

st.divider()


# ── Interactive dataframe and city chart ────────────────────────────────────
table_column, chart_column = st.columns([3, 2])

with table_column:
    st.subheader("User Directory")
    st.caption(f"Showing {len(filtered_df)} of {total_users} users")

    if filtered_df.empty:
        st.warning("No users match that name. Try a different search.")
    else:
        # st.dataframe provides built-in sorting, resizing, and scrolling.
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
        )

with chart_column:
    st.subheader("Users per City")
    st.caption("The chart updates to match the filtered table.")

    if filtered_df.empty:
        st.info("The chart will appear when the filter matches a user.")
    else:
        # Count the visible rows in each city and give the result clear labels.
        city_counts = (
            filtered_df["City"]
            .value_counts()
            .rename_axis("City")
            .reset_index(name="Users")
            .set_index("City")
        )

        st.bar_chart(city_counts)


# Explain exactly when the cached API function will run again.
with st.expander("How caching works in this app"):
    st.write(
        "`fetch_users()` runs on the first page load. Streamlit then reuses its "
        "cached return value during normal widget reruns. It fetches again after "
        "one hour, after the code changes, or when **Clear Cache and Reload** is "
        "clicked."
    )
