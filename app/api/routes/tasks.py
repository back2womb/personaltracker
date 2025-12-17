from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date
from sqlalchemy.exc import IntegrityError
from app.core.database import get_session
from app.api.deps import get_current_user
from app.models.task import Task, Category
from app.models.streak import Streak
from app.models.daily_log import DailyLog
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/tasks", tags=["Tasks"])

class TaskReadWithStatus(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: str
    current_streak: int
    longest_streak: int
    is_completed_today: bool

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

@router.get("/", response_model=List[TaskReadWithStatus])
def get_tasks(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    tasks = session.exec(
        select(Task).where(Task.is_active == True, Task.user_id == current_user.id)
    ).all()
    
    results = []
    for task in tasks:
        # Get Streak info
        streak = session.exec(select(Streak).where(Streak.task_id == task.id)).first()
        current_streak = streak.current_streak if streak else 0
        longest_streak = streak.longest_streak if streak else 0
        
        # Get Today's Log
        log = session.exec(select(DailyLog).where(
            DailyLog.task_id == task.id, 
            DailyLog.log_date == today
        )).first()
        is_completed_today = log is not None and log.completed
        
        results.append(TaskReadWithStatus(
            id=task.id,
            title=task.title,
            description=task.description,
            category=task.category or Category.OTHERS,
            current_streak=current_streak,
            longest_streak=longest_streak,
            is_completed_today=is_completed_today
        ))
    
    return results

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = "Others"

@router.post("/", response_model=Task)
def create_task(
    task_in: TaskCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        task = Task.from_orm(task_in)
        task.user_id = current_user.id
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Task with this title already exists")
    except Exception as e:
        session.rollback()
        print(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during task creation")

@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int, 
    task_update: TaskUpdate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task_update.title:
        task.title = task_update.title
    if task_update.category:
        task.category = task_update.category
    if task_update.description:
        task.description = task_update.description
    
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Task with this title already exists")
        
    return task
