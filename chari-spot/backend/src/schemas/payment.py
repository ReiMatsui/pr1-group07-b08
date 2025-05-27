from pydantic import BaseModel, ConfigDict

# class PaymentCreate(BaseModel):
#     spot_id: int
#     slot_id: int
#     paid: bool = False

class PaymentResponse(BaseModel):
    id: int
    spot_id: int
    slot_id: int
    parked: bool
    paid: bool

    model_config = ConfigDict(from_attributes = True)
