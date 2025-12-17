from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.core.database import get_session
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    user = session.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    new_user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Track Registration
    from app.models.analytics import AnalyticsEvent
    session.add(AnalyticsEvent(event_type="REGISTER", user_id=new_user.id, path="/auth/register"))
    session.commit()
    
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Track Login
    from app.models.analytics import AnalyticsEvent
    session.add(AnalyticsEvent(event_type="LOGIN", user_id=user.id, path="/auth/login"))
    session.commit()

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

from typing import List
class UserRead(BaseModel):
    id: int
    username: str

@router.get("/users", response_model=List[UserRead])
def get_users(session: Session = Depends(get_session)):
    users = session.query(User).all()
    return users
