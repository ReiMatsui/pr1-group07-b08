# coding: utf-8
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.routers import user
from app.models import user as user_model
from app.database import engine, get_db
from app import crud, schemas
from app.models import Base


app = FastAPI()

# FlutterからアクセスできるようCORS許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番は制限する
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build DB
user_model.Base.metadata.create_all(bind=engine)

# Include the user router
app.include_router(user.router)


@app.get("/api/hello")
def read_root():
    return {"message": "Hello from FastAPI!"}
