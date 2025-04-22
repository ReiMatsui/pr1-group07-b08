from sqlalchemy.orm import Session
from app.models.parking import Parking
from app.schemas.parking import ParkingCreate

def create_parking(db: Session, parking: ParkingCreate):
    db_parking = Parking(**parking.dict())
    db.add(db_parking)
    db.commit()
    db.refresh(db_parking)
    return db_parking

def get_parkings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Parking).offset(skip).limit(limit).all()