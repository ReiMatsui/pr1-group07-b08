from sqlalchemy.orm import Session
from models.payment import Payment
from typing import Optional

def create_payment(db: Session, payment: Payment) -> Payment:
    """Create a new payment record."""
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def get_payment_by_spot_and_slot(db: Session, spot_id: int, slot_id: int) -> Optional[Payment]:
    """Get payment by spot_id and slot_id (unique pair)."""
    return db.query(Payment).filter(
        Payment.spot_id == spot_id,
        Payment.slot_id == slot_id
    ).first()

def update_payment(db: Session, spot_id: int, slot_id: int, paid: bool=None, parked: bool=None) -> Payment:
    query = db.query(Payment).filter(
                Payment.spot_id == spot_id,
                Payment.slot_id == slot_id
            )
    if paid is not None:
        query.update({
            Payment.paid: paid
        })
    if parked is not None:
        query.update({
            Payment.parked: parked
        })

    db.commit()

    return db.query(Payment).filter(
        Payment.spot_id == spot_id,
        Payment.slot_id == slot_id
    ).first()
