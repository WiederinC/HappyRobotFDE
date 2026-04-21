from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import require_api_key
from api.database import get_db
from api.models.load import Load

router = APIRouter(prefix="/loads", tags=["loads"])


class BookLoadBody(BaseModel):
    load_id: str


def _parse_pickup_date(pickup_date: str) -> Optional[tuple[datetime, datetime]]:
    """
    Parse a flexible pickup date string into a (start, end) window.
    Accepts: 'YYYY-MM-DD', 'Monday', 'Tuesday', 'next week', 'this week', 'today', 'tomorrow'
    Returns a 1-day window (start of day to end of day).
    """
    if not pickup_date:
        return None

    val = pickup_date.strip().lower()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Named days of week
    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if val in day_names:
        target_dow = day_names.index(val)
        current_dow = today.weekday()
        days_ahead = (target_dow - current_dow) % 7
        if days_ahead == 0:
            days_ahead = 7  # next occurrence
        start = today + timedelta(days=days_ahead)
        return (start, start + timedelta(days=1))

    if val == "today":
        return (today, today + timedelta(days=1))
    if val == "tomorrow":
        start = today + timedelta(days=1)
        return (start, start + timedelta(days=1))
    if val in ("this week", "this_week"):
        return (today, today + timedelta(days=7))
    if val in ("next week", "next_week"):
        start = today + timedelta(days=7)
        return (start, start + timedelta(days=7))

    # ISO date YYYY-MM-DD
    try:
        start = datetime.strptime(pickup_date.strip(), "%Y-%m-%d")
        return (start, start + timedelta(days=1))
    except ValueError:
        pass

    return None


@router.get("/")
def search_loads(
    origin: Optional[str] = Query(None, description="Filter by origin city/state"),
    destination: Optional[str] = Query(None, description="Filter by destination city/state"),
    equipment_type: Optional[str] = Query(None, description="Filter by equipment type"),
    pickup_date: Optional[str] = Query(None, description="Preferred pickup date. Accepts: YYYY-MM-DD, Monday, Tuesday … Sunday, today, tomorrow, this week, next week"),
    db: Session = Depends(get_db),
    _=Depends(require_api_key),
):
    """
    Search available loads. Supports flexible pickup date filtering.
    Falls back to relaxed matching when no exact results are found.
    """
    base = db.query(Load).filter(Load.status == "available")
    date_window = _parse_pickup_date(pickup_date) if pickup_date else None

    def apply_filters(q, use_equipment=True, use_date=True):
        if origin:
            q = q.filter(Load.origin.ilike(f"%{origin}%"))
        if destination:
            q = q.filter(Load.destination.ilike(f"%{destination}%"))
        if use_equipment and equipment_type:
            q = q.filter(Load.equipment_type.ilike(f"%{equipment_type}%"))
        if use_date and date_window:
            q = q.filter(
                Load.pickup_datetime >= date_window[0].strftime("%Y-%m-%d"),
                Load.pickup_datetime < date_window[1].strftime("%Y-%m-%d"),
            )
        return q

    # 1. Exact match (route + equipment + date)
    results = apply_filters(base).all()
    if results:
        return results

    # 2. Relax date — maybe carrier is flexible on day
    if date_window:
        results = apply_filters(base, use_date=False).all()
        if results:
            for r in results:
                r.match_note = "Pickup date differs from requested — confirm availability"
            return results

    # 3. Relax equipment type
    if equipment_type:
        results = apply_filters(base, use_equipment=False).all()
        if results:
            return results

    return []


@router.post("/book")
def book_load(
    body: BookLoadBody,
    db: Session = Depends(get_db),
    _=Depends(require_api_key),
):
    """Book a load. Accepts load_id in the request body."""
    load = db.query(Load).filter(Load.load_id == body.load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    if load.status != "available":
        raise HTTPException(status_code=409, detail="Load is not available")
    load.status = "booked"
    db.commit()
    db.refresh(load)
    return load



@router.get("/{load_id}")
def get_load(load_id: str, db: Session = Depends(get_db), _=Depends(require_api_key)):
    """Get a specific load by ID."""
    load = db.query(Load).filter(Load.load_id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    return load
