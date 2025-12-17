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

from typing import List
from pydantic import BaseModel

class UserPublicStats(BaseModel):
    username: str
    tasks_completed: int
    active_streaks: int

@router.get("/community", response_model=List[UserPublicStats])
def get_community_leaderboard(session: Session = Depends(get_session)):
    """
    Returns a public leaderboard of all users and their progress.
    """
    users = session.exec(select(User)).all()
    leaderboard = []
    
    for user in users:
        # Count completed logs (Total impact)
        # Note: This is an expensive N+1 query loop, but fine for prototype scale < 100 users.
        completed_count = 0
        user_tasks = session.exec(select(Task).where(Task.user_id == user.id)).all()
        task_ids = [t.id for t in user_tasks]
        
        if task_ids:
            completed_count = session.exec(
                select(DailyLog).where(DailyLog.task_id.in_(task_ids), DailyLog.completed == True)
            ).all()
            completed_count = len(completed_count)
            
            # Count active streaks
            active_streaks_count = session.exec(
                select(Streak).where(Streak.task_id.in_(task_ids), Streak.current_streak > 0)
            ).all()
            active_streaks_count = len(active_streaks_count)
        else:
            active_streaks_count = 0

        leaderboard.append(UserPublicStats(
            username=user.username,
            tasks_completed=completed_count,
            active_streaks=active_streaks_count
        ))
    
    # Sort by tasks completed
    leaderboard.sort(key=lambda x: x.tasks_completed, reverse=True)
    return leaderboard

from app.models.analytics import AnalyticsEvent

@router.get("/admin/analytics")
def get_admin_analytics(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Admin only endpoint to see usage stats.
    """
    if current_user.id != 1:
         # Simple hardcoded admin check for prototype
         return {"error": "Unauthorized"}
    
    total_visits = session.query(AnalyticsEvent).filter(AnalyticsEvent.event_type == "APP_LOAD").count()
    total_logins = session.query(AnalyticsEvent).filter(AnalyticsEvent.event_type == "LOGIN").count()
    total_registrations = session.query(AnalyticsEvent).filter(AnalyticsEvent.event_type == "REGISTER").count()
    
    unique_users = session.query(User).count()

    return {
        "visits": total_visits,
        "logins": total_logins,
        "registrations": total_registrations,
        "total_users": unique_users
    }
