from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.db import Category
from app.schemas.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryRead])
def list_categories(session: Session = Depends(get_session)):
    categories = session.exec(select(Category)).all()
    return categories

@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategoryRead)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    db_category = Category(
        name=category.name,
        description=category.description
    )
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category
