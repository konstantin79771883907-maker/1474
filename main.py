from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List
import uvicorn

from app.database import engine, create_db_and_tables, init_db, get_session
from app.models.db import Ticket, User, Category, Comment, Status, Priority
from app.routes import tickets, users, categories, comments

# Initialize FastAPI app
app = FastAPI(title="School Support CRM", description="Minimalist CRM for school support team")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include API routers
app.include_router(tickets.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(comments.router, prefix="/api")

# Startup event
@app.on_event("startup")
async def startup():
    create_db_and_tables()
    init_db()

# Web routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: Session = Depends(get_session)):
    # Get statistics
    all_tickets = session.exec(select(Ticket)).all()
    stats = {
        "total": len(all_tickets),
        "open": len([t for t in all_tickets if t.status == Status.OPEN]),
        "in_progress": len([t for t in all_tickets if t.status == Status.IN_PROGRESS]),
        "resolved": len([t for t in all_tickets if t.status == Status.RESOLVED])
    }
    
    # Get recent tickets
    recent_tickets = session.exec(
        select(Ticket).order_by(Ticket.created_at.desc()).limit(10)
    ).all()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
        "recent_tickets": recent_tickets
    })

@app.get("/tickets", response_class=HTMLResponse)
async def tickets_page(request: Request, session: Session = Depends(get_session)):
    tickets_list = session.exec(select(Ticket).order_by(Ticket.created_at.desc())).all()
    return templates.TemplateResponse("tickets.html", {
        "request": request,
        "tickets": tickets_list
    })

@app.get("/tickets/new", response_class=HTMLResponse)
async def new_ticket_page(request: Request, session: Session = Depends(get_session)):
    categories_list = session.exec(select(Category)).all()
    return templates.TemplateResponse("ticket_form.html", {
        "request": request,
        "title": "Create New Ticket",
        "action": "/tickets/create",
        "categories": categories_list,
        "ticket": None,
        "edit_mode": False
    })

@app.post("/tickets/create")
async def create_ticket(
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form("medium"),
    category_id: int = Form(None),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).limit(1)).first()
    ticket = Ticket(
        title=title,
        description=description,
        priority=Priority(priority),
        category_id=category_id if category_id else None,
        author_id=user.id
    )
    session.add(ticket)
    session.commit()
    return RedirectResponse(url="/tickets", status_code=303)

@app.get("/tickets/{ticket_id}", response_class=HTMLResponse)
async def ticket_detail(request: Request, ticket_id: int, session: Session = Depends(get_session)):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        return RedirectResponse(url="/tickets")
    
    comments_list = session.exec(
        select(Comment).where(Comment.ticket_id == ticket_id).order_by(Comment.created_at)
    ).all()
    
    return templates.TemplateResponse("ticket_detail.html", {
        "request": request,
        "ticket": ticket,
        "comments": comments_list
    })

@app.get("/tickets/{ticket_id}/edit", response_class=HTMLResponse)
async def edit_ticket_page(request: Request, ticket_id: int, session: Session = Depends(get_session)):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        return RedirectResponse(url="/tickets")
    
    categories_list = session.exec(select(Category)).all()
    return templates.TemplateResponse("ticket_form.html", {
        "request": request,
        "title": f"Edit Ticket #{ticket_id}",
        "action": f"/tickets/{ticket_id}/update",
        "categories": categories_list,
        "ticket": ticket,
        "edit_mode": True
    })

@app.post("/tickets/{ticket_id}/update")
async def update_ticket(
    ticket_id: int,
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form("medium"),
    status: str = Form("open"),
    category_id: int = Form(None),
    session: Session = Depends(get_session)
):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        return RedirectResponse(url="/tickets")
    
    ticket.title = title
    ticket.description = description
    ticket.priority = Priority(priority)
    ticket.status = Status(status)
    ticket.category_id = category_id if category_id else None
    
    session.add(ticket)
    session.commit()
    return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=303)

@app.get("/categories", response_class=HTMLResponse)
async def categories_page(request: Request, session: Session = Depends(get_session)):
    categories_list = session.exec(select(Category)).all()
    return templates.TemplateResponse("categories.html", {
        "request": request,
        "categories": categories_list
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
