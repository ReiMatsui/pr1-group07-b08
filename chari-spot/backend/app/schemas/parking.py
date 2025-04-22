from pydantic import BaseModel
from typing import Optional

class ParkingCreate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    available_slots: int
    total_slots: int
    owner_id: int

class ParkingResponse(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    available_slots: int
    total_slots: int
    owner_id: int

    class Config:
        orm_mode = True