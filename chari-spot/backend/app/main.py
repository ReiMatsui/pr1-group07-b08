# coding: utf-8
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# FlutterからアクセスできるようCORS許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番は制限する
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/hello")
def read_root():
    return {"message": "Hello from FastAPI!"}
