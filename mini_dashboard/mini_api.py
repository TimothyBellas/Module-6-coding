"""
L6 — Mini Dashboard: FastAPI Backend
====================================
Run with:
    uvicorn mini_api:app --reload --port 8000

This API stores tasks in memory, so changes reset whenever the server restarts.
"""

# datetime supplies the creation time stored on each new task.
from datetime import datetime

# FastAPI creates the API, while HTTPException lets a route return errors such
# as a 404 response instead of allowing the program to crash.
from fastapi import FastAPI, HTTPException
# CORSMiddleware allows the browser-based dashboard to request API data.
from fastapi.middleware.cors import CORSMiddleware
# BaseModel validates incoming JSON; Field adds rules to individual values.
from pydantic import BaseModel, Field


# Create the main FastAPI application object. Uvicorn finds this object through
# the "mini_api:app" portion of the startup command.
app = FastAPI(title="Mini Task API")

# ── CORS configuration ──────────────────────────────────────────────────────
# Allow the dashboard to call the API when the two are served from different
# origins (for example, localhost ports 5500 and 8000). The wildcard values are
# acceptable for this classroom demo; production applications should normally
# list only the exact trusted origins, methods, and headers they need.
app.add_middleware(
    CORSMiddleware,
    # Permit requests from the origin that serves dashboard.html.
    allow_origins=["*"],
    # Permit GET, POST, PATCH, and browser preflight requests.
    allow_methods=["*"],
    # Permit headers such as Content-Type: application/json.
    allow_headers=["*"],
)


# ── In-memory data store ────────────────────────────────────────────────────
# This Python list acts as the database for the assignment. Every dictionary is
# one task. Because it lives only in memory, the data resets when Uvicorn stops.
tasks = [
    {
        "id": 1,
        "title": "Read the FastAPI docs",
        "done": True,
        "created_at": "2026-03-01",
    },
    {
        "id": 2,
        "title": "Build the task dashboard",
        "done": False,
        "created_at": "2026-03-02",
    },
    {
        "id": 3,
        "title": "Test every dashboard button",
        "done": False,
        "created_at": "2026-03-03",
    },
]

# Find the highest sample ID and add one so every new task gets a unique ID.
next_id = max(task["id"] for task in tasks) + 1


# ── Request-body schema ─────────────────────────────────────────────────────
class TaskCreate(BaseModel):
    """Describe and validate the JSON body required by POST /tasks."""

    # FastAPI rejects missing, empty, or overly long titles automatically.
    title: str = Field(min_length=1, max_length=200)


# ── API routes ──────────────────────────────────────────────────────────────
# The decorator connects an HTTP method and URL to the function below it.
@app.get("/tasks")
def get_tasks():
    """Return every task."""

    # FastAPI automatically converts this Python list into a JSON response.
    return tasks


@app.get("/stats")
def get_stats():
    """Return the task counts used by the dashboard stats bar."""

    # True acts like 1 and False acts like 0 when Python adds booleans.
    done_count = sum(task["done"] for task in tasks)

    # Calculate pending rather than looping through the tasks a second time.
    return {
        "total": len(tasks),
        "done": done_count,
        "pending": len(tasks) - done_count,
    }


# status_code=201 tells the browser that a new resource was created.
@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate):
    """Create a pending task and return it."""

    # "global" is required because this function changes next_id instead of
    # only reading its current value.
    global next_id

    # Remove accidental spaces from the beginning and end of the title.
    title = body.title.strip()

    # A title containing only spaces passes min_length before stripping, so
    # check it again and return a helpful validation error.
    if not title:
        raise HTTPException(status_code=422, detail="Task title cannot be blank")

    # All newly created tasks begin as pending (done=False).
    new_task = {
        "id": next_id,
        "title": title,
        "done": False,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    # Save the new dictionary, then reserve the following ID for the next task.
    tasks.append(new_task)
    next_id += 1

    # FastAPI converts the dictionary into JSON for the response body.
    return new_task


# {task_id} is a path parameter. FastAPI converts it to int because of the type
# hint in complete_task(task_id: int).
@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    """Mark one task as done, or return 404 when its ID does not exist."""

    # Search each stored task until its ID matches the ID from the URL.
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            return task

    # This line runs only if the loop finishes without finding a matching task.
    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/")
def root():
    """Provide a quick confirmation that the API server is running."""

    return {"message": "Mini Task API is running. Visit /docs for interactive docs."}
