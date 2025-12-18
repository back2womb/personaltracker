from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.database import engine
from app.api.routes import tasks, logs, dashboard, auth, news
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
    if request.url.path in ["/", "/index.html"]:
        try:
            # Use a separate try/except for DB interaction so it doesn't affect the user response
            with Session(engine) as session:
                from app.models.analytics import AnalyticsEvent
                event = AnalyticsEvent(
                    event_type="APP_LOAD",
                    path=request.url.path
                )
                session.add(event)
                session.commit()
        except Exception as e:
            # Just log error, don't crash user experience
            print(f"ANALYTICS WARNING: Logging failed (DB Issue): {e}")

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

@app.get("/debug/migrate_time")
def debug_migrate_time():
    try:
        from sqlmodel import text
        with Session(engine) as session:
            # Add the missing column manually since we lack Alembic
            session.exec(text("ALTER TABLE task ADD COLUMN IF NOT EXISTS scheduled_time VARCHAR"))
            session.commit()
        return {"status": "success", "message": "Column 'scheduled_time' added to Task table."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tasks.router)
app.include_router(logs.router)
app.include_router(news.router)

from fastapi.staticfiles import StaticFiles
from os import path

# Mount the frontend 'dist' directory
# Check if directory exists (for robustness)
frontend_dist = path.join(path.dirname(__file__), "../frontend/dist")
if path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    print(f"WARNING: Frontend dist directory not found at {frontend_dist}")
