from sqlalchemy import Column, Integer, Boolean, ForeignKey
from models import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(Integer, ForeignKey("parkings.id"), nullable=False)
    slot_id = Column(Integer, nullable=False)  
    parked = Column(Boolean, default=False)  # parking status: True for parked, False for not parked
    paid = Column(Boolean, default=False)   # payment staus: True for paid, False for unpaid
    