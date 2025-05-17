from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import parking
from schemas.parking import ParkingCreate, ParkingUpdate
import math


def create_parking(db: Session, parkingCreate: ParkingCreate):
    db_parking = parking.Parking(**parkingCreate.model_dump())
    db.add(db_parking)
    db.commit()
    db.refresh(db_parking)
    return db_parking

def get_parking(db: Session, id: int) -> Optional[parking.Parking]:
    """Fetch a slot by its primary key."""
    return db.get(parking.Parking, id)

def get_parkings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(parking.Parking).offset(skip).limit(limit).all()

def get_parking_by_owner(db: Session, owner_id: int):
    """Fetch all slots for a user."""
    return db.query(parking.Parking).filter(parking.Parking.owner_id == owner_id).all()

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

def delete_slot(db: Session, slot_id: id) -> bool:
    """Delete a slot by ID. Returns True if deleted, False if not found."""
    slot = get_parking(db, slot_id)
    if not slot:
        return False
    
    db.delete(slot)
    db.commit()
    
    return True

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # earth radius in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def get_nearby_parkings(db, latitude, longitude, radius_km):
    results = db.query(parking.Parking).all()
    nearby = []
    for park in results:
        if haversine(latitude, longitude, park.latitude, park.longitude) <= radius_km:
            nearby.append(park)
    return nearby


