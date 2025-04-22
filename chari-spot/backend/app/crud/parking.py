from typing import Optional
from sqlalchemy.orm import Session
from app.models import parking
from app.schemas.parking import ParkingCreate

def create_parking(db: Session, parking: ParkingCreate):
    db_parking = parking.Parking(**parking.dict())
    db.add(db_parking)
    db.commit()
    db.refresh(db_parking)
    return db_parking

def get_parkings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(parking.Parking).offset(skip).limit(limit).all()

def update_slot(
    db: Session,
    slot_id: int,
    *,
    name: Optional[str] = None,
    addr: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    total_slots: Optional[int] = None,
    avail_slots: Optional[int] = None,
    owner_id: Optional[int] = None
) -> Optional[parking.Parking]:
    """Update fields on a slot. Returns the updated slot, or None if not found."""
    slot = get_parkings(db, slot_id)
    if not slot:
        return None
    if name is not None:
        slot.name = name
    if addr is not None:
        slot.email = addr
    if latitude is not None:
        slot.password = latitude
    if longitude is not None:
        slot.password = latitude
    if total_slots is not None:
        slot.password = latitude
    if avail_slots is not None:
        slot.password = latitude
    if owner_id is not None:
        slot.password = latitude
    
    db.commit()
    db.refresh(slot)
    return slot

def delete_slot(db: Session, slot_id: id) -> bool:
    """Delete a slot by ID. Returns True if deleted, False if not found."""
    slot = get_parkings(db, slot_id)
    if not slot:
        return False
    
    db.delete(slot)
    db.commit()
    
    return True

