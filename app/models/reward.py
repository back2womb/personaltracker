from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Reward(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    reward_type: str
    value: int
    issued_at: datetime = Field(default_factory=datetime.utcnow)

