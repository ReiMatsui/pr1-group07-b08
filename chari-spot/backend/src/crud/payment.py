from sqlalchemy.orm import Session
from models.payment import Payment
from schemas.payment import PaymentCreate
from typing import Optional

def create_payment(db: Session, paymentCreate: PaymentCreate) -> Payment:
    """Create a new payment record."""
    db_payment = Payment(**paymentCreate.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_payment_by_spot_and_slot(db: Session, spot_id: int, slot_id: int) -> Optional[Payment]:
    """Get payment by spot_id and slot_id (unique pair)."""
    return db.query(Payment).filter(
        Payment.spot_id == spot_id,
        Payment.slot_id == slot_id
    ).first()
