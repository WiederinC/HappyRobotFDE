from sqlalchemy import Column, String, Float, Integer, Text, DateTime
from sqlalchemy.sql import func
from api.database import Base


class CallRecord(Base):
    __tablename__ = "calls"

    call_id = Column(String, primary_key=True, index=True)
    load_id = Column(String, nullable=True)
    carrier_mc = Column(String, nullable=True)
    carrier_name = Column(String, nullable=True)
    initial_offer = Column(Float, nullable=True)
    agreed_rate = Column(Float, nullable=True)
    loadboard_rate = Column(Float, nullable=True)
    num_negotiations = Column(Integer, default=0)
    outcome = Column(String)  # booked, declined, no_deal, carrier_ineligible, rate_hold, waitlisted
    sentiment = Column(String)  # positive, neutral, negative
    created_at = Column(DateTime, server_default=func.now())
    notes = Column(Text, nullable=True)
