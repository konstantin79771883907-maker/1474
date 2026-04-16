from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.db import Comment, Ticket, User
from app.schemas.schemas import CommentCreate, CommentRead

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/ticket/{ticket_id}", response_model=List[CommentRead])
def list_comments(ticket_id: int, session: Session = Depends(get_session)):
    comments = session.exec(
        select(Comment).where(Comment.ticket_id == ticket_id).order_by(Comment.created_at)
    ).all()
    return comments

@router.post("/", response_model=CommentRead)
def create_comment(comment: CommentCreate, session: Session = Depends(get_session)):
    # Verify ticket exists
    ticket = session.get(Ticket, comment.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Get first user as default author (in real app, use authenticated user)
    user = session.exec(select(User).limit(1)).first()
    if not user:
        raise HTTPException(status_code=400, detail="No users available")
    
    db_comment = Comment(
        content=comment.content,
        ticket_id=comment.ticket_id,
        author_id=user.id
    )
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment
