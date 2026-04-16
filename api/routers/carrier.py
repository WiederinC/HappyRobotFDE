import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from api.auth import require_api_key

router = APIRouter(prefix="/carrier", tags=["carrier"])

FMCSA_WEB_KEY = os.getenv("FMCSA_WEB_KEY", "")
FMCSA_BASE = "https://mobile.fmcsa.dot.gov/qc/services/carriers"


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
