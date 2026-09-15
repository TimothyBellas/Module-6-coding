Streamlit Task Manager Frontend

This project uses a Streamlit frontend (my_frontend.py) with the FastAPI demo
backend (backend.py). Users can log in, view task metrics, add tasks, update
task statuses, refresh the task list, and log out.

Demo Accounts

Username

Password

admin

password123

student

learn2026

These credentials are for the classroom demo only. Do not use them in a
production application.

Install Dependencies

Open PowerShell in the project folder and run:

python -m pip install fastapi uvicorn python-multipart streamlit requests

Start the FastAPI Backend

Run this command in the first PowerShell window:

python -m uvicorn backend:app --reload --port 8000

The backend will run at http://localhost:8000. Its interactive API
documentation is available at http://localhost:8000/docs.

Start the Streamlit Frontend

Keep the backend running. Open a second PowerShell window in the same project
folder and run:

python -m streamlit run my_frontend.py

Streamlit will display the local frontend address in the terminal, usually
http://localhost:8501.

Demo Notes

Tasks and login tokens are stored in memory by the demo backend.

Restarting the backend resets the in-memory data and invalidates old tokens.

The Streamlit frontend expects the backend at http://localhost:8000.

