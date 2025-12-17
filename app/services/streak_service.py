from sqlmodel import Session, select
from datetime import date
from app.models.streak import Streak
from app.utils.date_utils import is_consecutive_day

def update_streak(session: Session, task_id: int, today: date):
    streak = session.exec(
        select(Streak).where(Streak.task_id == task_id)
    ).first()

    if not streak:
        streak = Streak(task_id=task_id, current_streak=1, longest_streak=1, last_completed_date=today)
        session.add(streak)
    else:
        if streak.last_completed_date and is_consecutive_day(streak.last_completed_date, today):
            streak.current_streak += 1
        else:
            streak.current_streak = 1

        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_completed_date = today

    session.commit()
    return streak
