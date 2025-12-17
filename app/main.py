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
from app.models.analytics import AnalyticsEvent

app = FastAPI(title="Personal Execution Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from sqlmodel import Session

@app.middleware("http")
async def analytics_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Simple tracking for App Loads (Frontend)
    # We only care about the main page load, not every API call and static asset
    if request.url.path in ["/", "/index.html"]:
        try:
            with Session(engine) as session:
                from app.models.analytics import AnalyticsEvent
                event = AnalyticsEvent(
                    event_type="APP_LOAD",
                    path=request.url.path
                )
                session.add(event)
                session.commit()
        except Exception as e:
            print(f"Analytics Error: {e}")

    return response

@app.on_event("startup")
def on_startup():
    try:
        print("Attempting to connect to database...")
        SQLModel.metadata.create_all(engine)
        print("Database connected and tables created.")
    except Exception as e:
        print(f"CRITICAL: Database connection failed! {e}")
        # We don't raise here so the app can still start and show us logs
        pass

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is running"}

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
