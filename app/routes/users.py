from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.db import User, Comment
from app.schemas.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserRead])
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
