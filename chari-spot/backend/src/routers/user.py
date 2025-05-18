from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schemas import user
from crud import user as crud
from app import auth
from app.database import get_db
from models import user as models

router = APIRouter()


@router.post("/user/register", response_model=user.UserResponse)
def register_user(user: user.UserCreate, db: Session = Depends(get_db)):
    # Check if the email is already registered
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db, user)


@router.post("/user/login", response_model=user.Token)
async def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/user/get/{id}", response_model=user.UserResponse)
def update_user(id: int, db: Session = Depends(get_db)):
    return crud.get_user(db, id)


@router.post("/user/update", response_model=user.UserResponse)
def update_user(user: user.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(db, user)


@router.delete("/user/delete/{id}")
def update_user(id: int, db: Session = Depends(get_db)):
    return crud.delete_user(db, id)
