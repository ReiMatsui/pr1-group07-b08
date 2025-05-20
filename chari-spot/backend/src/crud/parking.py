from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import parking
from schemas.parking import ParkingCreate, ParkingUpdate

def create_parking(db: Session, parkingCreate: ParkingCreate, user_id: int):
    # Avoid got multiple values for argument 'owner_id'
    db_parking = parking.Parking(**parkingCreate.model_dump(exclude={"owner_id"}), owner_id=user_id)
    db.add(db_parking)
    db.commit()
    db.refresh(db_parking)
    return db_parking

def get_parking(db: Session, id: int) -> Optional[parking.Parking]:
    """Fetch a slot by its primary key."""
    return db.get(parking.Parking, id)

def get_parkings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(parking.Parking).offset(skip).limit(limit).all()

def get_parking_by_owner(db: Session, u_id: int) -> Optional[list[parking.Parking]]:
    """Fetch a list of slots by owner ID."""
    return db.query(parking.Parking).filter(parking.Parking.owner_id == u_id).all()

def update_slot(db: Session, slotUpdate: ParkingUpdate) -> Optional[parking.Parking]:
    """Update fields on a slot. Returns the updated slot, or None if not found."""
    slot = get_parking(db, slotUpdate.id)
    if not slot:
        raise HTTPException(status_code=400, detail="Slot id not found.")
    
    update_data = slotUpdate.model_dump(exclude_unset=True)  
    for key, value in update_data.items():
        setattr(slot, key, value)
    
    db.commit()
    db.refresh(slot)
    return slot

def delete_slot(db: Session, slot_id: int) -> bool:
    """Delete a slot by ID. Returns True if deleted, False if not found."""
    slot = get_parking(db, slot_id)
    if not slot:
        return False
    
    db.delete(slot)
    db.commit()
    
    return True
