import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from api.auth import require_api_key
from api.database import get_db
from api.models.waitlist import WaitlistEntry

router = APIRouter(prefix="/waitlist", tags=["waitlist"])


class WaitlistRequest(BaseModel):
    entry_type: str = "lane_unavailable"   # "lane_unavailable" | "rate_hold"
    carrier_mc: Optional[str] = None
    carrier_name: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    equipment_type: Optional[str] = None
    availability_window: Optional[str] = None
    carrier_ask_rate: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("carrier_mc", "carrier_ask_rate", "availability_window", mode="before")
    @classmethod
    def coerce_to_str(cls, v: Any) -> Optional[str]:
        """Accept numbers from HappyRobot and convert to string."""
        if v is None:
            return None
        return str(v)


VALID_TYPES = {"lane_unavailable", "rate_hold"}


@router.post("/", dependencies=[Depends(require_api_key)])
def add_to_waitlist(payload: WaitlistRequest, db: Session = Depends(get_db)):
    if payload.entry_type not in VALID_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"entry_type must be one of: {', '.join(VALID_TYPES)}",
        )

    entry = WaitlistEntry(
        id=str(uuid.uuid4()),
        entry_type=payload.entry_type,
        carrier_mc=payload.carrier_mc,
        carrier_name=payload.carrier_name,
        origin=payload.origin,
        destination=payload.destination,
        equipment_type=payload.equipment_type,
        availability_window=payload.availability_window,
        carrier_ask_rate=payload.carrier_ask_rate,
        notes=payload.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    if payload.entry_type == "rate_hold":
        message = (
            f"Saved as rate hold — {payload.carrier_name or payload.carrier_mc} "
            f"asking {payload.carrier_ask_rate}. Will contact if budget increases."
        )
    else:
        message = (
            f"Added to waitlist for {payload.origin} → {payload.destination}. "
            f"Will contact {payload.carrier_name or payload.carrier_mc} when a load becomes available."
        )

    return {"status": "saved", "id": entry.id, "message": message}


@router.get("/", dependencies=[Depends(require_api_key)])
def get_waitlist(
    entry_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(WaitlistEntry)
    if entry_type:
        query = query.filter(WaitlistEntry.entry_type == entry_type)
    entries = query.order_by(WaitlistEntry.created_at.desc()).all()

    return {
        "total": len(entries),
        "entries": [
            {
                "id": e.id,
                "entry_type": e.entry_type,
                "carrier_mc": e.carrier_mc,
                "carrier_name": e.carrier_name,
                "origin": e.origin,
                "destination": e.destination,
                "equipment_type": e.equipment_type,
                "availability_window": e.availability_window,
                "carrier_ask_rate": e.carrier_ask_rate,
                "notes": e.notes,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ],
    }
