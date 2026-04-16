import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import require_api_key
from api.database import get_db
from api.models.call import CallRecord

router = APIRouter(prefix="/calls", tags=["calls"])

VALID_OUTCOMES = {"booked", "declined", "no_deal", "carrier_ineligible"}
VALID_SENTIMENTS = {"positive", "neutral", "negative"}


class CallCreate(BaseModel):
    load_id: Optional[str] = None
    carrier_mc: Optional[str] = None
    carrier_name: Optional[str] = None
    initial_offer: Optional[float] = None
    agreed_rate: Optional[float] = None
    loadboard_rate: Optional[float] = None
    num_negotiations: int = 0
    outcome: str = "no_deal"  # booked | declined | no_deal | carrier_ineligible
    sentiment: str = "neutral"  # positive | neutral | negative
    notes: Optional[str] = None


@router.post("/", status_code=201)
def create_call(
    payload: CallCreate,
    db: Session = Depends(get_db),
    _=Depends(require_api_key),
):
    """Record a completed call with its outcome and extracted data."""
    if payload.outcome not in VALID_OUTCOMES:
        raise HTTPException(
            status_code=422,
            detail=f"outcome must be one of {sorted(VALID_OUTCOMES)}",
        )
    if payload.sentiment not in VALID_SENTIMENTS:
        raise HTTPException(
            status_code=422,
            detail=f"sentiment must be one of {sorted(VALID_SENTIMENTS)}",
        )

    call = CallRecord(call_id=str(uuid.uuid4()), **payload.model_dump())
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


@router.get("/")
def list_calls(
    db: Session = Depends(get_db),
    _=Depends(require_api_key),
):
    """List all recorded calls, most recent first."""
    return db.query(CallRecord).order_by(CallRecord.created_at.desc()).all()


@router.get("/{call_id}")
def get_call(call_id: str, db: Session = Depends(get_db), _=Depends(require_api_key)):
    call = db.query(CallRecord).filter(CallRecord.call_id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call
