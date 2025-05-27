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

# create a new payment
@router.post("/park", response_model=schemas.PaymentResponse)
def park(
    spot_id: int = Query(..., description="Spot ID"),
    slot_id: int = Query(..., description="Slot ID"),
    db: Session = Depends(get_db),
):
    paymentCreate = payment.Payment(
        spot_id=spot_id,
        slot_id=slot_id,
        parked=True,
        paid=False
    )
    if crud.get_payment_by_spot_and_slot(db, spot_id, slot_id) is None:
        res = crud.create_payment(db, paymentCreate)
    else:
        res = crud.update_payment(db, spot_id=spot_id, slot_id=slot_id, parked=True, paid=False)
    
    response = schemas.PaymentResponse.model_validate(res)
    return response

@router.post("/pay", response_model=schemas.PaymentResponse)
def park_in(
    spot_id: int = Query(..., description="Spot ID"),
    slot_id: int = Query(..., description="Slot ID"),
    db: Session = Depends(get_db),
):
    res = crud.update_payment(db, spot_id=spot_id, slot_id=slot_id, parked=True, paid=True)
    
    response = schemas.PaymentResponse.model_validate(res)
    return response

@router.post("/leave", response_model=schemas.PaymentResponse)
def leave(
    spot_id: int = Query(..., description="Spot ID"),
    slot_id: int = Query(..., description="Slot ID"),
    db: Session = Depends(get_db),
):
    res = crud.update_payment(db, spot_id=spot_id, slot_id=slot_id, parked=False, paid=False)
    
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
