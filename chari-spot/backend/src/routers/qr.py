from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from crud import payment as crud
from models.payment import Payment

router = APIRouter(
    tags=["qr"],
    prefix="/qr",
)

@router.get("/trigger")
async def qr_trigger(
    request: Request,
    db: Session = Depends(get_db)
):
    spot_id = request.query_params.get("spot_id")
    slot_id = request.query_params.get("slot_id")

    # パラメータの存在チェック
    if spot_id is None or slot_id is None:
        raise HTTPException(status_code=400, detail="spot_id and slot_id are required")
    
    # int型に変換
    try:
        spot_id = int(spot_id)
        slot_id = int(slot_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="spot_id and slot_id must be integers")

    # paymentレコードの存在チェック
    payment_obj = crud.get_payment_by_spot_and_slot(db, spot_id, slot_id)
    if not payment_obj:
        new_payment = Payment(
            spot_id = spot_id,
            slot_id = slot_id,
            parked = True,
            paid = True
        )
        crud.create_payment(db, new_payment)
    
    # paidをTrueに更新
    updated_payment = crud.update_payment(db, spot_id, slot_id, paid=True)

    return {"spot_id": spot_id, "slot_id": slot_id, "paid": updated_payment.paid}