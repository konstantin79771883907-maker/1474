from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.db import Priority, Status, Role

# User schemas
class UserBase(BaseModel):
    name: str
    email: str
    role: Role = Role.USER

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    created_at: datetime

# Category schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int

# Ticket schemas
class TicketBase(BaseModel):
    title: str
    description: str
    priority: Priority = Priority.MEDIUM
    category_id: Optional[int] = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    category_id: Optional[int] = None

class TicketRead(TicketBase):
    id: int
    status: Status
    author_id: int
    category_id: Optional[int]
    created_at: datetime
    updated_at: datetime

# Comment schemas
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    ticket_id: int

class CommentRead(CommentBase):
    id: int
    ticket_id: int
    author_id: int
    created_at: datetime
