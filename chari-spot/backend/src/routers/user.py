from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import user as schemas
from crud import user as crud
from app.database import get_db
from models import user as models

router = APIRouter()

@router.post("/user/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if the email is already registered
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db, user)

@router.get("/user/get/{id}", response_model=schemas.UserResponse)
def update_user(id: int, db: Session = Depends(get_db)):
    return crud.get_user(db, id)

@router.post("/user/update", response_model=schemas.UserResponse)
def update_user(user: schemas.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(db, user)

@router.delete("/user/delete/{id}")
def update_user(id: int, db: Session = Depends(get_db)):
    return crud.delete_user(db, id)
