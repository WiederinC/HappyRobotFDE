import os
from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.auth import require_api_key
from api.database import get_db
from api.models.call import CallRecord
from api.models.load import Load

router = APIRouter(prefix="/carrier", tags=["carrier"])

FMCSA_WEB_KEY = os.getenv("FMCSA_WEB_KEY", "")
FMCSA_BASE = "https://mobile.fmcsa.dot.gov/qc/services/carriers"


@router.get("/history")
def get_carrier_history(
    mc_number: str = Query(..., description="Carrier MC number"),
    db: Session = Depends(get_db),
    _=Depends(require_api_key),
):
    """
    Return call history for a returning carrier by MC number.
    Used by the agent to personalise the greeting and offer relevant loads.
    """
    mc_clean = mc_number.strip().lstrip("MC").lstrip("mc").strip()
    # Accept both "123456" and "MC123456" stored formats
    calls = (
        db.query(CallRecord)
        .filter(
            CallRecord.carrier_mc.in_([mc_clean, f"MC{mc_clean}"])
        )
        .order_by(CallRecord.created_at.desc())
        .all()
    )

    if not calls:
        return {"mc_number": mc_clean, "is_returning": False, "total_calls": 0}

    total = len(calls)
    bookings = [c for c in calls if c.outcome == "booked"]
    last = calls[0]

    # Build preferred lanes from booked calls
    lane_counts: dict[str, int] = {}
    for c in bookings:
        if c.load_id:
            lane_counts[c.load_id] = lane_counts.get(c.load_id, 0) + 1
    preferred_lanes = sorted(lane_counts, key=lane_counts.get, reverse=True)[:3]

    # Look up the load to get the lane name
    last_load = db.query(Load).filter(Load.load_id == last.load_id).first() if last.load_id else None
    last_lane = (
        f"{last_load.origin} → {last_load.destination}" if last_load else last.load_id
    )

    last_call_info = {
        "load_id": last.load_id,
        "lane": last_lane,
        "outcome": last.outcome,
        "agreed_rate": last.agreed_rate,
        "date": last.created_at.strftime("%Y-%m-%d") if last.created_at else None,
    }

    return {
        "mc_number": mc_clean,
        "carrier_name": last.carrier_name,
        "is_returning": True,
        "total_calls": total,
        "total_bookings": len(bookings),
        "booking_rate_pct": round(len(bookings) / total * 100, 1),
        "last_call": last_call_info,
        "preferred_load_ids": preferred_lanes,
    }


@router.get("/verify")
async def verify_carrier(
    mc_number: str = Query(..., description="Carrier MC number (digits only)"),
    _=Depends(require_api_key),
):
    """
    Verify a carrier's eligibility via the FMCSA API.
    Returns eligibility status, legal name, and authority details.
    If FMCSA_WEB_KEY is not configured, returns a mock response for development.
    """
    mc_clean = mc_number.strip().lstrip("MC").lstrip("mc").strip()

    if not FMCSA_WEB_KEY:
        return {
            "mc_number": mc_clean,
            "eligible": True,
            "legal_name": "Demo Carrier LLC",
            "dba_name": None,
            "status": "ACTIVE",
            "out_of_service": False,
            "allowed_to_operate": True,
            "note": "FMCSA_WEB_KEY not configured — mock response for development",
        }

    url = f"{FMCSA_BASE}/{mc_clean}?webKey={FMCSA_WEB_KEY}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 404:
                return {
                    "mc_number": mc_clean,
                    "eligible": False,
                    "status": "NOT_FOUND",
                    "legal_name": None,
                }
            if resp.status_code == 403:
                # Key not yet activated — fall back to mock so demos still work
                return {
                    "mc_number": mc_clean,
                    "eligible": True,
                    "legal_name": "Demo Carrier LLC",
                    "dba_name": None,
                    "status": "ACTIVE",
                    "out_of_service": False,
                    "allowed_to_operate": True,
                    "note": "FMCSA key pending activation — mock response",
                }
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=502, detail="FMCSA API returned an error")
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Could not reach FMCSA API")

    carrier = (data.get("content") or {}).get("carrier") or {}
    allowed = carrier.get("allowedToOperate", "N") == "Y"
    out_of_service = carrier.get("outOfServiceDate") is not None

    return {
        "mc_number": mc_clean,
        "eligible": allowed and not out_of_service,
        "legal_name": carrier.get("legalName"),
        "dba_name": carrier.get("dbaName"),
        "status": "ACTIVE" if allowed else "INACTIVE",
        "out_of_service": out_of_service,
        "allowed_to_operate": allowed,
        "phy_city": carrier.get("phyCity"),
        "phy_state": carrier.get("phyState"),
    }
