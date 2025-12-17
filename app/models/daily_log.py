from sqlmodel import SQLModel, Field
from datetime import date
from typing import Optional
from sqlalchemy import UniqueConstraint

class DailyLog(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("task_id", "log_date", name="uix_task_day"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    log_date: date
    completed: bool
