from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class AnalyticsEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str  # "VISIT", "LOGIN", "REGISTER"
    user_id: Optional[int] = None # Null for guests
    path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
