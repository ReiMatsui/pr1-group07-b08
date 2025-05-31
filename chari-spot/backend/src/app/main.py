# coding: utf-8
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user
from routers import parking
from routers import payment
from routers import qr
from models import user as user_model
from models import parking as parking_model
from sqlalchemy.orm import Session
from app.database import engine, SQLALCHEMY_DATABASE_URL, SessionLocal

app = FastAPI()

import os

print("### FastAPI working directory:", os.getcwd())
print("### FastAPI using DB path:", SQLALCHEMY_DATABASE_URL)

# FlutterからアクセスできるようCORS許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番は制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build DB
user_model.Base.metadata.create_all(bind=engine)

# Include the user router
app.include_router(user.router)

# Include the parking router
app.include_router(parking.router)

# include the payment router
app.include_router(payment.router)

app.include_router(qr.router)

@app.get("/api/hello")
def read_root():
    return {"message": "Hello from FastAPI!"}
