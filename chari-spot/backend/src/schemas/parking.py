from pydantic import BaseModel, ConfigDict
from typing import Optional

class ParkingCreate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    avail_slots: int
    total_slots: int
    owner_id: int

class ParkingUpdate(BaseModel):
    id: int
    name:         Optional[str]     = None
    address:      Optional[str]     = None
    latitude:     Optional[float]   = None
    longitude:    Optional[float]   = None
    avail_slots:  Optional[int]     = None
    total_slots:  Optional[int]     = None
    owner_id:     Optional[int]     = None

class ParkingResponse(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    avail_slots: int
    total_slots: int
    owner_id: int

    model_config = ConfigDict(from_attributes = True)