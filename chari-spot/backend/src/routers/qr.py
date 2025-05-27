from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.database import get_db
from paypayopa import Client                # 公式 SDK
from typing import Dict
from concurrent.futures import ThreadPoolExecutor
import uuid, time, asyncio, functools

router = APIRouter(
    tags=["qr"],
    prefix="/qr",
)

@router.get("/trigger")
async def trigger(req: Request):
    # 好きな処理を書く（DB 更新・バッチ起動など）
    return "成功！"