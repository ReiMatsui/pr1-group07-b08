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
async def qr_trigger(request: Request):
    spot_id = request.query_params.get("spot_id")
    slot_id = request.query_params.get("slot_id")
    # ここでspot_idやslot_idを使った処理が可能
    return {"spot_id": spot_id, "slot_id": slot_id}