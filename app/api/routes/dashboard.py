from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from datetime import date

from app.core.database import get_session
from app.api.deps import get_current_user
from app.models.task import Task
from app.models.daily_log import DailyLog
from app.models.streak import Streak
from app.models.reward import Reward
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def get_dashboard(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    today = date.today()

    total_tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
    active_tasks = session.exec(
        select(Task).where(Task.is_active == True, Task.user_id == current_user.id)
    ).all()

    # Join with Task to filter by user
    today_logs = session.exec(
        select(DailyLog).join(Task).where(
            DailyLog.log_date == today,
            DailyLog.completed == True,
            Task.user_id == current_user.id
        )
    ).all()

    streaks = session.exec(
        select(Streak).join(Task).where(Task.user_id == current_user.id)
    ).all()
    
    rewards = session.exec(
        select(Reward).join(Task).where(Task.user_id == current_user.id)
    ).all()

    longest_streak = max(
        [s.longest_streak for s in streaks],
        default=0
    )

    return {
        "tasks": {
            "total": len(total_tasks),
            "active": len(active_tasks),
            "completed_today": len(today_logs)
        },
        "streaks": {
            "active_streaks": len(streaks),
            "longest_streak": longest_streak
        },
        "rewards": {
            "total_rewards": len(rewards)
        }
    }
