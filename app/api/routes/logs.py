from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlmodel import Session, select
from app.core.database import get_session
from app.api.deps import get_current_user
from app.models.daily_log import DailyLog
from app.models.task import Task
from app.models.user import User
from app.services.streak_service import update_streak
from app.services.reward_service import issue_reward
from pydantic import BaseModel

class LogCreate(BaseModel):
    task_id: int
    completed: bool

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.post("/")
def log_task(
    log_in: LogCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Verify Task Ownership
    task = session.exec(select(Task).where(Task.id == log_in.task_id, Task.user_id == current_user.id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or access denied")

    task_id = log_in.task_id
    completed = log_in.completed
    today = date.today()

    existing_log = session.exec(
        select(DailyLog).where(
            DailyLog.task_id == task_id,
            DailyLog.log_date == today
        )
    ).first()

    if existing_log:
        raise HTTPException(
            status_code=400,
            detail="Task already logged for today"
        )

    log = DailyLog(task_id=task_id, log_date=today, completed=completed)
    session.add(log)
    session.commit()
    session.refresh(log)

    if completed:
        streak = update_streak(session, task_id, today)
        reward = issue_reward(session, task_id, streak.current_streak)
        return {"log": log, "streak": streak, "reward": reward}

    return {"log": log}
