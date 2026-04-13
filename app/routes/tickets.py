from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.db import Ticket, User, Category, Comment, Status, Priority
from app.schemas.schemas import TicketCreate, TicketRead, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get("/", response_model=List[TicketRead])
def list_tickets(
    status: Status = None,
    priority: Priority = None,
    session: Session = Depends(get_session)
):
    query = select(Ticket)
    if status:
        query = query.where(Ticket.status == status)
    if priority:
        query = query.where(Ticket.priority == priority)
    query = query.order_by(Ticket.created_at.desc())
    tickets = session.exec(query).all()
    return tickets

@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: int, session: Session = Depends(get_session)):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/", response_model=TicketRead)
def create_ticket(ticket: TicketCreate, session: Session = Depends(get_session)):
    # Get first user as default author (in real app, use authenticated user)
    user = session.exec(select(User).limit(1)).first()
    if not user:
        raise HTTPException(status_code=400, detail="No users available")
    
    db_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        category_id=ticket.category_id,
        author_id=user.id
    )
    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)
    return db_ticket

@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(ticket_id: int, ticket_update: TicketUpdate, session: Session = Depends(get_session)):
    db_ticket = session.get(Ticket, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    update_data = ticket_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ticket, key, value)
    
    session.add(db_ticket)
    session.commit()
    session.refresh(db_ticket)
    return db_ticket

@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, session: Session = Depends(get_session)):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    session.delete(ticket)
    session.commit()
    return {"message": "Ticket deleted"}
