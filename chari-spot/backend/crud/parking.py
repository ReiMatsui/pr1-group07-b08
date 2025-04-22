from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import parking
from schemas.parking import ParkingCreate, ParkingUpdate

def create_parking(db: Session, parkingCreate: ParkingCreate):
    db_parking = parking.Parking(**parkingCreate.dict())
    db.add(db_parking)
    db.commit()
    db.refresh(db_parking)
    return db_parking

def get_parking(db: Session, id: int) -> Optional[parking.Parking]:
    """Fetch a user by its primary key."""
    return db.get(parking.Parking, id)

def get_parkings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(parking.Parking).offset(skip).limit(limit).all()

def update_slot(db: Session, slotUpdate: ParkingUpdate) -> Optional[parking.Parking]:
    """Update fields on a slot. Returns the updated slot, or None if not found."""
    slot = get_parking(db, slotUpdate.id)
    if not slot:
        raise HTTPException(status_code=400, detail="Slot id not found.")
    if slotUpdate.name is not None:
        slot.name = slotUpdate.name
    if slotUpdate.address is not None:
        slot.address = slotUpdate.address
    if slotUpdate.latitude is not None:
        slot.latitude = slotUpdate.latitude
    if slotUpdate.longitude is not None:
        slot.longitude = slotUpdate.longitude
    if slotUpdate.total_slots is not None:
        slot.total_slots = slotUpdate.total_slots
    if slotUpdate.avail_slots is not None:
        slot.avail_slots = slotUpdate.avail_slots
    if slotUpdate.owner_id is not None:
        slot.owner_id = slotUpdate.owner_id
    
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

