# coding: utf-8
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user
from routers import parking
from models import user as user_model
from app.database import engine


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

# Include the parking router
app.include_router(parking.router)

@app.get("/api/hello")
def read_root():
    return {"message": "Hello from FastAPI!"}
