from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from datetime import date, timedelta, datetime

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
    
    # Total Completed All Time
    completed_all_time = session.exec(
        select(DailyLog).join(Task).where(
            DailyLog.completed == True,
            Task.user_id == current_user.id
        )
    ).all()

    # Calculate Global Streak (User Level)
    # Get all unique dates where user completed at least one task
    completed_dates = session.exec(
        select(DailyLog.log_date)
        .join(Task)
        .where(
            Task.user_id == current_user.id,
            DailyLog.completed == True
        )
        .distinct()
    ).all()
    
    # Sort dates descending
    sorted_dates = sorted([d for d in completed_dates], reverse=True)
    
    current_streak = 0
    if sorted_dates:
        # Check if the most recent completion was today or yesterday
        last_completion = sorted_dates[0]
        today_date = date.today()
        yesterday = today_date - timedelta(days=1)
        
        if last_completion == today_date or last_completion == yesterday:
            current_streak = 1
            # Check previous dates
            check_date = last_completion - timedelta(days=1)
            for d in sorted_dates[1:]:
                if d == check_date:
                    current_streak += 1
                    check_date -= timedelta(days=1)
                else:
                    break
        else:
            # Streak broken
            current_streak = 0
            
    rewards = session.exec(
        select(Reward).join(Task).where(Task.user_id == current_user.id)
    ).all()

    return {
        "tasks": {
            "total": len(total_tasks),
            "active": len(active_tasks),
            "completed_today": len(today_logs),
            "unfinished_today": max(0, len(active_tasks) - len(today_logs)),
            "completed_all_time": len(completed_all_time)
        },
        "streaks": {
            "active_streaks": current_streak, # Using global streak here
            "longest_streak": current_streak  # Simplified for now
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

@router.get("/admin/export_data")
def export_admin_data(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Exports all database data as JSON for the admin.
    """
    if current_user.id != 1:
         return {"error": "Unauthorized"}
    
    users = session.exec(select(User)).all()
    tasks = session.exec(select(Task)).all()
    logs = session.exec(select(DailyLog)).all()
    analytics = session.exec(select(AnalyticsEvent)).all()
    
    # helper to safely dump
    def safe_dump(objs):
        data = []
        for o in objs:
            d = o.dict()
            if "hashed_password" in d:
                del d["hashed_password"]
            # Convert datetime to string
            for k, v in d.items():
                if isinstance(v, (date, datetime)):
                    d[k] = v.isoformat()
            data.append(d)
        return data

    return {
        "users": safe_dump(users),
        "tasks": safe_dump(tasks),
        "logs": safe_dump(logs),
        "analytics": safe_dump(analytics)
    }

from app.ml.predictor import train_predictor_model, predict_task_success

@router.post("/ml/train")
def trigger_training(current_user: User = Depends(get_current_user)):
    # Simple auth check
    return train_predictor_model()

@router.get("/ml/predict")
def get_prediction(
    category: str,
    scheduled_minutes: int = 0,
    title: str = "New Task",
    current_user: User = Depends(get_current_user)
):
    prob = predict_task_success(category, scheduled_minutes, title)
    if prob is None:
        return {"error": "Model not trained yet"}
    
    # Interpretation
    msg = "This seems manageable! 🟢"
    if prob < 40: msg = "This might be tough today. 🔴"
    elif prob < 70: msg = "Challenging but doable. 🟡"
    
    return {
        "probability": prob,
        "message": msg
    }

@router.get("/insights")
def get_insights(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Returns statistical analysis of user behavior for visualization.
    """
    # Fetch all completed tasks history
    logs = session.exec(
        select(DailyLog).join(Task).where(
            Task.user_id == current_user.id,
            DailyLog.completed == True
        )
    ).all()

    # 1. Weekly Pattern (Productivity by Day of Week)
    week_stats = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0} # 0=Mon
    for log in logs:
        week_stats[log.log_date.weekday()] += 1
    
    weekly_chart = [
        {"day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][k], "tasks": v} 
        for k, v in week_stats.items()
    ]

    # 2. Category Distribution
    tasks = session.exec(select(Task).where(Task.user_id == current_user.id)).all()
    task_map = {t.id: t.category for t in tasks}
    
    cat_counts = {}
    for log in logs:
        cat = task_map.get(log.task_id, "Unknown")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        
    category_chart = [{"name": k, "value": v} for k, v in cat_counts.items()]

    # 3. Trend Analysis (Last 7 days)
    today = date.today()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    daily_counts = []
    
    for d in dates:
        cnt = len([l for l in logs if l.log_date == d])
        daily_counts.append(cnt)
    
    # Simple Heuristic Trend
    recent = sum(daily_counts[-3:])
    prev = sum(daily_counts[:3])
    
    trend_label = "Stable ➡️"
    if recent > prev: trend_label = "Improving 📈"
    elif recent < prev: trend_label = "Declining 📉"
    
    return {
        "weekly_pattern": weekly_chart,
        "category_distribution": category_chart,
        "trend": trend_label,
        "last_7_days": [{"date": d.strftime("%m-%d"), "completed": c} for d, c in zip(dates, daily_counts)]
    }
