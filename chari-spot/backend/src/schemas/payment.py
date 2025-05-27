from pydantic import BaseModel

class PaymentCreate(BaseModel):
    spot_id: int
    slot_id: int
    paid: bool = False

class PaymentOut(PaymentCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True
