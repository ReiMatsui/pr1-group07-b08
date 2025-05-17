### routers/parking.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import parking as schemas
from crud import parking as crud
from app.database import get_db
from schemas.parking import NearbySearchRequest #refactoring needed

router = APIRouter()

@router.post("/parkings/register", response_model=schemas.ParkingResponse,summary="Create a new parking spot",)
def create_parking(parking: schemas.ParkingCreate, db: Session = Depends(get_db)):
    return crud.create_parking(db, parking)

@router.get("/parkings", response_model=list[schemas.ParkingResponse],summary="Get all parkings",)
def read_all_parkings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_parkings(db, skip=skip, limit=limit)

@router.get("/parkings/owner/{owner_id}", response_model=list[schemas.ParkingResponse],summary="Find parking by owner's id",)
def read_owner_parkings(owner_id: int, db: Session = Depends(get_db)):
    return crud.get_parking_by_owner(db, owner_id)

@router.delete("/parkings/delete/{id}")
def delete_parkings(id: int, db: Session = Depends(get_db)):
    return crud.delete_slot(db, id)


@router.post("/parkings/nearby", response_model=list[schemas.ParkingResponse],summary="Find nearby parkings",)
def search_nearby_parkings(request: NearbySearchRequest, db: Session = Depends(get_db)):
    return crud.get_nearby_parkings(db, request.latitude, request.longitude, request.radius_km)
