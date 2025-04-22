### routers/parking.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import parking as schemas
from app.crud import parking as crud
from app.database import get_db

router = APIRouter()

@router.post("/parkings/register", response_model=schemas.ParkingResponse)
def create_parking(parking: schemas.ParkingCreate, db: Session = Depends(get_db)):
    return crud.create_parking(db, parking)

@router.get("/parkings", response_model=list[schemas.ParkingResponse])
def read_parkings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_parkings(db, skip=skip, limit=limit)

