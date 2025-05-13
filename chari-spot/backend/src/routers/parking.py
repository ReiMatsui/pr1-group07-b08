### routers/parking.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import parking as schemas
from app.auth import get_current_user
from crud import parking as crud
from app.database import get_db

router = APIRouter(
    prefix="/parkings",
    tags=["parking"],
    dependencies=[Depends(get_current_user)],   # ← apply to all routes here
)

@router.post("/register", response_model=schemas.ParkingResponse)
def create_parking(parking: schemas.ParkingCreate, db: Session = Depends(get_db)):
    return crud.create_parking(db, parking)

@router.get("", response_model=list[schemas.ParkingResponse])
def read_parkings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_parkings(db, skip=skip, limit=limit)

@router.post("/update", response_model=schemas.ParkingResponse)
def read_parkings(slot: schemas.ParkingUpdate, db: Session = Depends(get_db)):
    return crud.update_slot(db, slot)

@router.delete("/delete/{id}")
def read_parkings(id: int, db: Session = Depends(get_db)):
    return crud.delete_slot(db, id)
