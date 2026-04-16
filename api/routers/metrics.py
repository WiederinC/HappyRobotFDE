import os

from fastapi import APIRouter, Depends
from sqlalchemy import cast, case, Date, func, Integer
from sqlalchemy.orm import Session

from api.auth import require_api_key
from api.database import get_db
from api.models.call import CallRecord

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/")
def get_metrics(db: Session = Depends(get_db), _=Depends(require_api_key)):
    """
    Full business metrics for the analytics dashboard.
    Covers activity, revenue impact, lane performance, carrier value,
    and negotiation efficiency.
    """
    total = db.query(func.count(CallRecord.call_id)).scalar() or 0

    # ── Outcomes & sentiment ──────────────────────────────────────────────────
    outcome_rows = (
        db.query(CallRecord.outcome, func.count(CallRecord.call_id))
        .group_by(CallRecord.outcome).all()
    )
    sentiment_rows = (
        db.query(CallRecord.sentiment, func.count(CallRecord.call_id))
        .group_by(CallRecord.sentiment).all()
    )
    outcomes   = {k: v for k, v in outcome_rows}
    sentiments = {k: v for k, v in sentiment_rows}
    booked     = outcomes.get("booked", 0)
    booking_rate = round(booked / total * 100, 1) if total else 0.0

    # ── Rate averages ─────────────────────────────────────────────────────────
    avg_negotiations = float(
        db.query(func.avg(CallRecord.num_negotiations)).scalar() or 0
    )
    avg_agreed = float(
        db.query(func.avg(CallRecord.agreed_rate))
        .filter(CallRecord.agreed_rate.isnot(None)).scalar() or 0
    )
    avg_loadboard = float(
        db.query(func.avg(CallRecord.loadboard_rate))
        .filter(CallRecord.loadboard_rate.isnot(None)).scalar() or 0
    )
    avg_savings = round(avg_loadboard - avg_agreed, 2) if avg_agreed and avg_loadboard else 0.0

    # ── Revenue impact ────────────────────────────────────────────────────────
    revenue_booked = float(
        db.query(func.sum(CallRecord.agreed_rate))
        .filter(CallRecord.outcome == "booked",
                CallRecord.agreed_rate.isnot(None))
        .scalar() or 0
    )
    # Revenue at risk = loadboard rates on calls that didn't convert
    revenue_at_risk = float(
        db.query(func.sum(CallRecord.loadboard_rate))
        .filter(CallRecord.outcome.in_(["no_deal", "declined"]),
                CallRecord.loadboard_rate.isnot(None))
        .scalar() or 0
    )
    revenue_per_call = round(revenue_booked / total, 2) if total else 0.0

    # Rate compression: how much below loadboard the agent closes (%)
    rate_compression_pct = round(
        (avg_savings / avg_loadboard * 100), 1
    ) if avg_loadboard else 0.0

    # ── Negotiations distribution ─────────────────────────────────────────────
    neg_rows = (
        db.query(CallRecord.num_negotiations, func.count(CallRecord.call_id))
        .group_by(CallRecord.num_negotiations).all()
    )
    neg_dist = {str(k): v for k, v in sorted(neg_rows, key=lambda x: x[0])}

    # ── Lane performance ──────────────────────────────────────────────────────
    lane_rows = (
        db.query(
            CallRecord.load_id,
            func.count(CallRecord.call_id).label("calls"),
            func.sum(
                case((CallRecord.outcome == "booked", 1), else_=0)
            ).label("bookings"),
            func.avg(CallRecord.agreed_rate).label("avg_rate"),
            func.avg(CallRecord.loadboard_rate).label("avg_board"),
        )
        .filter(CallRecord.load_id.isnot(None))
        .group_by(CallRecord.load_id)
        .order_by(func.count(CallRecord.call_id).desc())
        .limit(10)
        .all()
    )
    lane_performance = [
        {
            "load_id":      row.load_id,
            "calls":        row.calls,
            "bookings":     int(row.bookings or 0),
            "booking_rate": round((row.bookings or 0) / row.calls * 100, 1),
            "avg_rate":     round(float(row.avg_rate or 0), 0),
            "avg_board":    round(float(row.avg_board or 0), 0),
        }
        for row in lane_rows
    ]

    # ── Carrier value ─────────────────────────────────────────────────────────
    carrier_rows = (
        db.query(
            CallRecord.carrier_mc,
            CallRecord.carrier_name,
            func.count(CallRecord.call_id).label("calls"),
            func.sum(
                case((CallRecord.outcome == "booked", 1), else_=0)
            ).label("bookings"),
            func.sum(CallRecord.agreed_rate).label("total_revenue"),
        )
        .filter(CallRecord.carrier_mc.isnot(None))
        .group_by(CallRecord.carrier_mc, CallRecord.carrier_name)
        .order_by(func.sum(CallRecord.agreed_rate).desc())
        .limit(10)
        .all()
    )
    carrier_value = [
        {
            "carrier_mc":    row.carrier_mc,
            "carrier_name":  row.carrier_name or row.carrier_mc,
            "calls":         row.calls,
            "bookings":      int(row.bookings or 0),
            "booking_rate":  round((row.bookings or 0) / row.calls * 100, 1),
            "total_revenue": round(float(row.total_revenue or 0), 0),
        }
        for row in carrier_rows
    ]

    # ── Daily call volume ─────────────────────────────────────────────────────
    db_url = os.getenv("DATABASE_URL", "sqlite")
    if "postgresql" in db_url or "postgres" in db_url:
        day_expr = cast(CallRecord.created_at, Date).label("day")
    else:
        day_expr = func.strftime("%Y-%m-%d", CallRecord.created_at).label("day")

    daily_rows = (
        db.query(day_expr, func.count(CallRecord.call_id).label("count"))
        .group_by("day").order_by("day").all()
    )

    # ── Actionable insights ───────────────────────────────────────────────────
    insights = []

    if booking_rate < 40:
        insights.append({
            "type":    "warning",
            "title":   "Low Booking Rate",
            "message": f"Booking rate is {booking_rate}% — below the 40% target. "
                       f"Review agent negotiation strategy and carrier objection handling.",
        })
    elif booking_rate >= 60:
        insights.append({
            "type":    "success",
            "title":   "Strong Conversion",
            "message": f"Booking rate of {booking_rate}% is above target. "
                       f"Agent is converting well — consider scaling call volume.",
        })

    if revenue_at_risk > revenue_booked * 0.5:
        insights.append({
            "type":    "warning",
            "title":   "High Revenue at Risk",
            "message": f"${revenue_at_risk:,.0f} in potential revenue lost to no-deals. "
                       f"Focus on improving negotiation closing on 2nd and 3rd round offers.",
        })

    if avg_savings < 0:
        insights.append({
            "type":    "warning",
            "title":   "Overpaying on Agreed Rates",
            "message": f"Average agreed rate (${avg_agreed:,.0f}) exceeds "
                       f"loadboard rate (${avg_loadboard:,.0f}). "
                       f"Tighten agent negotiation ceiling.",
        })
    elif rate_compression_pct > 8:
        insights.append({
            "type":    "info",
            "title":   "Strong Rate Discipline",
            "message": f"Agent is closing {rate_compression_pct}% below board rate on average — "
                       f"protecting margin effectively.",
        })

    if lane_performance:
        best = max(lane_performance, key=lambda x: x["booking_rate"])
        if best["booking_rate"] >= 60:
            insights.append({
                "type":    "success",
                "title":   "Top Performing Lane",
                "message": f"Load {best['load_id']} converts at {best['booking_rate']}% — "
                           f"prioritise this lane for inbound volume.",
            })

    if carrier_value:
        top = carrier_value[0]
        insights.append({
            "type":    "info",
            "title":   "Top Carrier by Revenue",
            "message": f"{top['carrier_name']} (MC {top['carrier_mc']}) has generated "
                       f"${top['total_revenue']:,.0f} across {top['bookings']} bookings — "
                       f"high-value relationship to nurture.",
        })

    return {
        # Activity
        "total_calls":          total,
        "booking_rate":         booking_rate,
        "booked":               booked,
        "outcomes":             outcomes,
        "sentiments":           sentiments,
        "avg_negotiations":     round(avg_negotiations, 2),
        "negotiations_distribution": neg_dist,
        # Rates
        "avg_agreed_rate":      round(avg_agreed, 2),
        "avg_loadboard_rate":   round(avg_loadboard, 2),
        "avg_savings_per_load": avg_savings,
        "rate_compression_pct": rate_compression_pct,
        # Revenue
        "revenue_booked":       round(revenue_booked, 0),
        "revenue_at_risk":      round(revenue_at_risk, 0),
        "revenue_per_call":     revenue_per_call,
        # Intelligence
        "lane_performance":     lane_performance,
        "carrier_value":        carrier_value,
        "insights":             insights,
        # Trend
        "daily_calls":          [{"date": str(d), "count": c} for d, c in daily_rows],
    }
