"""
Matches endpoint — cross-references open loads with waitlist entries.
Returns opportunities where a carrier is waiting for a lane that now has an available load.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.auth import require_api_key
from api.database import get_db
from api.models.load import Load
from api.models.waitlist import WaitlistEntry

router = APIRouter(prefix="/matches", tags=["matches"])


def _city(location: str) -> str:
    """Extract city name from 'City, ST' format."""
    if not location:
        return ""
    return location.split(",")[0].strip().lower()


def _lanes_match(load_origin: str, load_dest: str, entry_origin: str, entry_dest: str) -> bool:
    """Return True if the waitlist entry lane overlaps with the load lane."""
    lo = _city(load_origin)
    ld = _city(load_dest)
    eo = _city(entry_origin or "")
    ed = _city(entry_dest or "")

    # Origin must match if entry has one
    origin_ok = (not eo) or (eo in lo) or (lo in eo)
    # Destination must match if entry has one
    dest_ok = (not ed) or (ed in ld) or (ld in ed)

    return origin_ok and dest_ok


@router.get("/", dependencies=[Depends(require_api_key)])
def get_matches(db: Session = Depends(get_db)):
    """
    Returns a list of match opportunities:
    - Available loads that have at least one waitlist or rate-hold carrier waiting on that lane.
    """
    available_loads = (
        db.query(Load)
        .filter(Load.status == "available")
        .order_by(Load.pickup_datetime)
        .all()
    )

    waitlist_entries = db.query(WaitlistEntry).all()

    matches = []
    for load in available_loads:
        waiting_carriers = []
        for entry in waitlist_entries:
            if _lanes_match(load.origin, load.destination, entry.origin, entry.destination):
                waiting_carriers.append({
                    "entry_id":           entry.id,
                    "entry_type":         entry.entry_type,
                    "carrier_mc":         entry.carrier_mc,
                    "carrier_name":       entry.carrier_name or entry.carrier_mc,
                    "availability_window": entry.availability_window,
                    "carrier_ask_rate":   entry.carrier_ask_rate,
                    "notes":              entry.notes,
                    "added":              entry.created_at.isoformat() if entry.created_at else None,
                    # Flag if carrier's ask is now within budget (loadboard_rate + 10%)
                    "rate_match": (
                        entry.entry_type == "rate_hold"
                        and entry.carrier_ask_rate is not None
                        and float(entry.carrier_ask_rate) <= load.loadboard_rate * 1.10
                    ),
                })

        if waiting_carriers:
            matches.append({
                "load_id":         load.load_id,
                "origin":          load.origin,
                "destination":     load.destination,
                "equipment_type":  load.equipment_type,
                "loadboard_rate":  load.loadboard_rate,
                "pickup_datetime": str(load.pickup_datetime),
                "waiting_count":   len(waiting_carriers),
                "waiting_carriers": waiting_carriers,
            })

    return {
        "total_matches": len(matches),
        "matches": matches,
    }
