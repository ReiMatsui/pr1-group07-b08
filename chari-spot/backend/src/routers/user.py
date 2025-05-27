from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse  # ✅ 追加
from sqlalchemy.orm import Session
from schemas import user
from crud import user as crud
from app import auth
from app.database import get_db
from models import user as models

router = APIRouter(tags=["user"])


@router.post("/user/register", response_model=user.UserResponse)
def register_user(user: user.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    created_user = crud.create_user(db, user)
    return JSONResponse(
        content={
            "id": created_user.id,
            "username": created_user.username,
            "email": created_user.email,
        },
        media_type="application/json; charset=utf-8"
    )


@router.post("/user/login", response_model=user.Token)
async def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user_obj = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user_obj:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"user_id": user_obj.id},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"},
        media_type="application/json; charset=utf-8"
    )


@router.get("/user/get")
def get_user(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    user_obj = crud.get_user(db, user.id)
    return JSONResponse(
        content={
            "id": user_obj.id,
            "username": user_obj.username,
            "email": user_obj.email,
        },
        media_type="application/json; charset=utf-8"
    )


@router.post("/user/update")
def update_user(
    user_up: user.UserUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)
):
    user_up.id = user.id
    user_up.password = auth.get_password_hash(user_up.password)
    updated_user = crud.update_user(db, user_up)
    return JSONResponse(
        content={
            "id": updated_user.id,
            "username": updated_user.username,
            "email": updated_user.email,
        },
        media_type="application/json; charset=utf-8"
    )


@router.delete("/user/delete")
def delete_user(db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    crud.delete_user(db, user.id)
    return JSONResponse(
        content={"message": "ユーザーを削除しました"},
        media_type="application/json; charset=utf-8"
    )