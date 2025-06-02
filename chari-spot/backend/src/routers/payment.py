from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from crud import payment as crud
from schemas import payment as schemas
from app.auth import get_current_user
from models import payment

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=schemas.PaymentResponse)
def update(
    spot_id: int = Query(..., description="Spot ID"),
    slot_id: int = Query(..., description="Slot ID"),
    parked: Optional[bool] = Query(None, description="Parking status"),
    paid: Optional[bool] = Query(None, description="Payment status"),
    db: Session = Depends(get_db),
):
    if crud.get_payment_by_spot_and_slot(db, spot_id, slot_id) is None:
        paymentCreate = payment.Payment(
            spot_id=spot_id,
            slot_id=slot_id,
            parked=True,
            paid=False
        )
        res = crud.create_payment(db, paymentCreate)
    elif parked is None and paid is None:
        raise HTTPException(status_code=400, detail="Either 'parked' or 'paid' must be provided")
    else:
        res = crud.update_payment(db, spot_id=spot_id, slot_id=slot_id, parked=parked, paid=paid)
    
    response = schemas.PaymentResponse.model_validate(res)
    return response


# url/?spot_id=1&slot_id=2
@router.get("/", response_model=None)
def get_payment_by_spot_and_slot(
    spot_id: int = Query(..., description="Spot ID"),
    slot_id: int = Query(..., description="Slot ID"),
    db: Session = Depends(get_db),
):
    payment = crud.get_payment_by_spot_and_slot(db, spot_id, slot_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Data not found")
    
    return payment.paid
