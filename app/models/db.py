from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Status(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Role(str, Enum):
    USER = "user"
    SUPPORT = "support"
    ADMIN = "admin"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
    role: Role = Field(default=Role.USER)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    tickets: List["Ticket"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    
    tickets: List["Ticket"] = Relationship(back_populates="category")

class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.OPEN)
    author_id: int = Field(foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    author: User = Relationship(back_populates="tickets")
    category: Optional[Category] = Relationship(back_populates="tickets")
    comments: List["Comment"] = Relationship(back_populates="ticket")

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    ticket_id: int = Field(foreign_key="ticket.id")
    author_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    ticket: Ticket = Relationship(back_populates="comments")
    author: User = Relationship(back_populates="comments")
