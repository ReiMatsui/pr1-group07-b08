from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from crud import payment as crud
from schemas import payment as schemas
from app.auth import get_current_user
from models import user as models

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    dependencies=[Depends(get_current_user)]
)

# create a new payment
@router.post("/", response_model=schemas.PaymentOut)
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    payment_data = payment.model_dump()
    payment_data["user_id"] = user.id
    return crud.create_payment(db, schemas.PaymentCreate(**payment_data))

# search：by spot_id + slot_id
@router.get("/spot/{spot_id}/slot/{slot_id}", response_model=schemas.PaymentOut)
def get_payment_by_spot_and_slot(
    spot_id: int,
    slot_id: int,
    db: Session = Depends(get_db),
):
    payment = crud.get_payment_by_spot_and_slot(db, spot_id, slot_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
