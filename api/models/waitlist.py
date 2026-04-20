from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from api.database import Base


class WaitlistEntry(Base):
    __tablename__ = "waitlist"

    id = Column(String, primary_key=True, index=True)
    entry_type = Column(String)          # "lane_unavailable" | "rate_hold"
    carrier_mc = Column(String, nullable=True)
    carrier_name = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    equipment_type = Column(String, nullable=True)
    availability_window = Column(String, nullable=True)  # e.g. "30 days from Apr 20"
    carrier_ask_rate = Column(String, nullable=True)     # for rate_hold entries
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
