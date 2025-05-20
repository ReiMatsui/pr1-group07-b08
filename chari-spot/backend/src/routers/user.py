from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schemas import user
from crud import user as crud
from app import auth
from app.database import get_db
from models import user as models

router = APIRouter(tags=["user"])


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
        data={"user_id": user.id},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/user/get", response_model=user.UserResponse)
def get_user(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    return crud.get_user(db, user.id)


@router.post("/user/update", response_model=user.UserResponse)
def update_user(
    user_up: user.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # create a new UserUpdate object with the current user's ID
    user_update_data = user.UserUpdate(**user_up.model_dump())
    return crud.update_user(db, user_update_data, user_id=current_user.id)



@router.delete("/user/delete")
def delete_user(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    return crud.delete_user(db, user.id)
