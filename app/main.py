from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.database import engine
from app.api.routes import tasks, logs, dashboard, auth
from fastapi.middleware.cors import CORSMiddleware

# Explicitly import models to ensure they are registered with SQLModel.metadata
from app.models.user import User
from app.models.task import Task
from app.models.streak import Streak
from app.models.daily_log import DailyLog
from app.models.reward import Reward

app = FastAPI(title="Personal Execution Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tasks.router)
app.include_router(logs.router)

from fastapi.staticfiles import StaticFiles
from os import path

# Mount the frontend 'dist' directory
# Check if directory exists (for robustness)
frontend_dist = path.join(path.dirname(__file__), "../frontend/dist")
if path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    print(f"WARNING: Frontend dist directory not found at {frontend_dist}")
