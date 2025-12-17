from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from sqlalchemy import UniqueConstraint

class Category(str, Enum):
    PERSONAL_DEVELOPMENT = "Personal Development"
    HOBBIES = "Hobbies"
    CAREER_DEVELOPMENT = "Career Development"
    ACADEMICS = "Academics"
    OTHERS = "Others"

class Task(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("title", "user_id", name="uix_task_user_title"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    category: Optional[str] = Field(default=Category.OTHERS)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    scheduled_time: Optional[str] = Field(default=None) # Format "HH:MM" 24h or "HH:MM AM/PM"
