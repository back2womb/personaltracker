from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class Streak(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    current_streak: int = 0
    longest_streak: int = 0
    last_completed_date: Optional[date] = None
