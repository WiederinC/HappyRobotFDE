from sqlalchemy import Column, String, Float, Integer, Text
from api.database import Base


class Load(Base):
    __tablename__ = "loads"

    load_id = Column(String, primary_key=True, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    pickup_datetime = Column(String)
    delivery_datetime = Column(String)
    equipment_type = Column(String)
    loadboard_rate = Column(Float)
    notes = Column(Text)
    weight = Column(Float)
    commodity_type = Column(String)
    num_of_pieces = Column(Integer)
    miles = Column(Float)
    dimensions = Column(String)
    status = Column(String, default="available")  # available, booked
