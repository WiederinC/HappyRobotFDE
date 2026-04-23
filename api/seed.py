"""
Seed the database with sample loads and demo call records.
Run from the project root:  python -m api.seed
"""

import os
import random
import uuid
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()

from api.database import Base, SessionLocal, engine
from api.models.call import CallRecord
from api.models.load import Load

Base.metadata.create_all(bind=engine)

LOADS = [
    {
        "load_id": "LD-001",
        "origin": "Chicago, IL",
        "destination": "Dallas, TX",
        "pickup_datetime": "2026-04-28 08:00",
        "delivery_datetime": "2026-04-30 14:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 2800.0,
        "notes": "No touch freight. Dock to dock. Driver must have TWIC card.",
        "weight": 42000,
        "commodity_type": "Electronics",
        "num_of_pieces": 24,
        "miles": 921,
        "dimensions": "53ft",
        "status": "available",
    },
    {
        "load_id": "LD-002",
        "origin": "Los Angeles, CA",
        "destination": "Phoenix, AZ",
        "pickup_datetime": "2026-04-29 06:00",
        "delivery_datetime": "2026-04-29 18:00",
        "equipment_type": "Reefer",
        "loadboard_rate": 1450.0,
        "notes": "Temperature controlled: 34-38F. Perishable cargo.",
        "weight": 38000,
        "commodity_type": "Fresh Produce",
        "num_of_pieces": 44,
        "miles": 372,
        "dimensions": "53ft",
        "status": "available",
    },
    {
        "load_id": "LD-003",
        "origin": "Atlanta, GA",
        "destination": "Miami, FL",
        "pickup_datetime": "2026-04-27 09:00",
        "delivery_datetime": "2026-04-28 15:00",
        "equipment_type": "Flatbed",
        "loadboard_rate": 1950.0,
        "notes": "Steel coils. Tarps required. Oversize permit needed.",
        "weight": 47000,
        "commodity_type": "Steel",
        "num_of_pieces": 6,
        "miles": 662,
        "dimensions": "48ft x 102in",
        "status": "available",
    },
    {
        "load_id": "LD-004",
        "origin": "Houston, TX",
        "destination": "Nashville, TN",
        "pickup_datetime": "2026-04-26 07:00",
        "delivery_datetime": "2026-04-27 16:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 2200.0,
        "notes": "Automotive parts. Liftgate required at delivery.",
        "weight": 35000,
        "commodity_type": "Auto Parts",
        "num_of_pieces": 80,
        "miles": 788,
        "dimensions": "53ft",
        "status": "available",
    },
    {
        "load_id": "LD-005",
        "origin": "Seattle, WA",
        "destination": "Denver, CO",
        "pickup_datetime": "2026-04-28 10:00",
        "delivery_datetime": "2026-04-30 08:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 3100.0,
        "notes": "Hazmat Class 3. Driver must have Hazmat endorsement.",
        "weight": 40000,
        "commodity_type": "Industrial Chemicals",
        "num_of_pieces": 200,
        "miles": 1321,
        "dimensions": "53ft",
        "status": "available",
    },
    {
        "load_id": "LD-006",
        "origin": "New York, NY",
        "destination": "Boston, MA",
        "pickup_datetime": "2026-04-25 14:00",
        "delivery_datetime": "2026-04-25 20:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 850.0,
        "notes": "Short haul. Residential delivery. 24hr notice required.",
        "weight": 18000,
        "commodity_type": "Furniture",
        "num_of_pieces": 30,
        "miles": 215,
        "dimensions": "26ft",
        "status": "available",
    },
    {
        "load_id": "LD-007",
        "origin": "Memphis, TN",
        "destination": "Chicago, IL",
        "pickup_datetime": "2026-04-26 05:00",
        "delivery_datetime": "2026-04-26 17:00",
        "equipment_type": "Reefer",
        "loadboard_rate": 1700.0,
        "notes": "Frozen goods. Temp: 0F. Continuous monitoring required.",
        "weight": 43000,
        "commodity_type": "Frozen Food",
        "num_of_pieces": 900,
        "miles": 531,
        "dimensions": "53ft",
        "status": "available",
    },
    {
        "load_id": "LD-008",
        "origin": "Kansas City, MO",
        "destination": "Indianapolis, IN",
        "pickup_datetime": "2026-04-27 08:00",
        "delivery_datetime": "2026-04-28 10:00",
        "equipment_type": "Flatbed",
        "loadboard_rate": 1600.0,
        "notes": "Construction equipment. Pilot car required. Over-dimensional.",
        "weight": 52000,
        "commodity_type": "Heavy Machinery",
        "num_of_pieces": 2,
        "miles": 484,
        "dimensions": "55ft x 14ft wide",
        "status": "available",
    },
    {
        "load_id": "LD-009",
        "origin": "Phoenix, AZ",
        "destination": "Las Vegas, NV",
        "pickup_datetime": "2026-04-30 12:00",
        "delivery_datetime": "2026-04-30 18:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 700.0,
        "notes": "Retail merchandise. No appointment needed at origin.",
        "weight": 22000,
        "commodity_type": "Consumer Goods",
        "num_of_pieces": 300,
        "miles": 297,
        "dimensions": "48ft",
        "status": "available",
    },
    {
        "load_id": "LD-010",
        "origin": "Charlotte, NC",
        "destination": "Philadelphia, PA",
        "pickup_datetime": "2026-04-25 06:00",
        "delivery_datetime": "2026-04-26 09:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 1750.0,
        "notes": "Medical supplies. Priority delivery. Secure facility.",
        "weight": 28000,
        "commodity_type": "Medical Supplies",
        "num_of_pieces": 150,
        "miles": 628,
        "dimensions": "53ft",
        "status": "available",
    },
    # --- Return loads (Chicago back toward Memphis corridor) ---
    {
        "load_id": "LD-011",
        "origin": "Chicago, IL",
        "destination": "Memphis, TN",
        "pickup_datetime": "2026-04-27 08:00",
        "delivery_datetime": "2026-04-27 20:00",
        "equipment_type": "Reefer",
        "loadboard_rate": 1600.0,
        "notes": "Frozen dairy. Temp: 34F. Tail-gate delivery.",
        "weight": 40000,
        "commodity_type": "Dairy",
        "num_of_pieces": 600,
        "miles": 531,
        "dimensions": "53ft",
        "status": "available",
    },
    {
        "load_id": "LD-012",
        "origin": "Chicago, IL",
        "destination": "Nashville, TN",
        "pickup_datetime": "2026-04-28 06:00",
        "delivery_datetime": "2026-04-28 18:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 1400.0,
        "notes": "General merchandise. No touch freight.",
        "weight": 32000,
        "commodity_type": "General Merchandise",
        "num_of_pieces": 120,
        "miles": 470,
        "dimensions": "53ft",
        "status": "available",
    },
    # --- Nearby loads (Indianapolis — 180 miles from Chicago) ---
    {
        "load_id": "LD-013",
        "origin": "Indianapolis, IN",
        "destination": "Dallas, TX",
        "pickup_datetime": "2026-04-26 07:00",
        "delivery_datetime": "2026-04-27 18:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 2400.0,
        "notes": "Auto parts. No liftgate. Dock high only.",
        "weight": 36000,
        "commodity_type": "Auto Parts",
        "num_of_pieces": 90,
        "miles": 950,
        "dimensions": "53ft",
        "status": "available",
    },
    # --- Nearby loads (Nashville — 210 miles from Memphis) ---
    {
        "load_id": "LD-014",
        "origin": "Nashville, TN",
        "destination": "Chicago, IL",
        "pickup_datetime": "2026-04-27 06:00",
        "delivery_datetime": "2026-04-27 20:00",
        "equipment_type": "Reefer",
        "loadboard_rate": 1850.0,
        "notes": "Fresh produce. Temp: 36F. Time sensitive.",
        "weight": 41000,
        "commodity_type": "Fresh Produce",
        "num_of_pieces": 500,
        "miles": 470,
        "dimensions": "53ft",
        "status": "available",
    },
    # --- Same lane future loads ---
    {
        "load_id": "LD-015",
        "origin": "Memphis, TN",
        "destination": "Chicago, IL",
        "pickup_datetime": "2026-04-28 05:00",
        "delivery_datetime": "2026-04-28 17:00",
        "equipment_type": "Reefer",
        "loadboard_rate": 1720.0,
        "notes": "Frozen poultry. Temp: 0F. Lumper service available.",
        "weight": 44000,
        "commodity_type": "Frozen Poultry",
        "num_of_pieces": 800,
        "miles": 531,
        "dimensions": "53ft",
        "status": "available",
    },
    # --- Midwest / Open Availability circuit loads ---
    {
        "load_id": "LD-016",
        "origin": "Minneapolis, MN",
        "destination": "Chicago, IL",
        "pickup_datetime": "2026-04-26 07:00",
        "delivery_datetime": "2026-04-26 19:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 1850.0,
        "notes": "Packaged goods. No touch freight. Dock high only.",
        "weight": 38000,
        "commodity_type": "Packaged Goods",
        "num_of_pieces": 240,
        "miles": 410,
        "dimensions": "53ft",
        "status": "available",
    },
    {
        "load_id": "LD-017",
        "origin": "Chicago, IL",
        "destination": "Indianapolis, IN",
        "pickup_datetime": "2026-04-27 08:00",
        "delivery_datetime": "2026-04-27 14:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 1100.0,
        "notes": "Auto components. Liftgate at delivery. Standard dock hours.",
        "weight": 33000,
        "commodity_type": "Auto Parts",
        "num_of_pieces": 60,
        "miles": 182,
        "dimensions": "53ft",
        "status": "available",
    },
    {
        "load_id": "LD-018",
        "origin": "Indianapolis, IN",
        "destination": "Nashville, TN",
        "pickup_datetime": "2026-04-28 06:00",
        "delivery_datetime": "2026-04-28 16:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 1300.0,
        "notes": "Retail merchandise. Floor loaded. No hazmat.",
        "weight": 29000,
        "commodity_type": "Retail Goods",
        "num_of_pieces": 180,
        "miles": 278,
        "dimensions": "53ft",
        "status": "available",
    },
    {
        "load_id": "LD-019",
        "origin": "Nashville, TN",
        "destination": "Memphis, TN",
        "pickup_datetime": "2026-04-25 07:00",
        "delivery_datetime": "2026-04-25 13:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 900.0,
        "notes": "General freight. Drop and hook. 24hr facility.",
        "weight": 26000,
        "commodity_type": "General Freight",
        "num_of_pieces": 100,
        "miles": 210,
        "dimensions": "53ft",
        "status": "available",
    },
    {
        "load_id": "LD-020",
        "origin": "Memphis, TN",
        "destination": "Dallas, TX",
        "pickup_datetime": "2026-04-26 06:00",
        "delivery_datetime": "2026-04-27 10:00",
        "equipment_type": "Dry Van",
        "loadboard_rate": 2100.0,
        "notes": "Electronics. No touch. Driver assist available at destination.",
        "weight": 31000,
        "commodity_type": "Electronics",
        "num_of_pieces": 50,
        "miles": 452,
        "dimensions": "53ft",
        "status": "available",
    },
]

OUTCOMES = ["booked", "declined", "no_deal", "carrier_ineligible"]
SENTIMENTS = ["positive", "neutral", "negative"]
OUTCOME_WEIGHTS = [0.55, 0.20, 0.15, 0.10]
SENTIMENT_WEIGHTS = [0.50, 0.30, 0.20]
CARRIERS = [
    ("MC123456", "Swift Transport LLC"),
    ("MC789012", "Reliable Freight Co."),
    ("MC345678", "Eagle Logistics Inc."),
    ("MC901234", "Blue Star Carriers"),
    ("MC567890", "Horizon Trucking"),
    ("MC112233", "Atlas Freight"),
    ("MC445566", "Pioneer Hauling"),
    ("MC778899", "Summit Transport"),
]

random.seed(42)

now = datetime.utcnow()
load_rates = {l["load_id"]: l["loadboard_rate"] for l in LOADS}
load_ids = list(load_rates.keys())

DEMO_CALLS = []
for _ in range(40):
    outcome = random.choices(OUTCOMES, weights=OUTCOME_WEIGHTS)[0]
    sentiment = random.choices(SENTIMENTS, weights=SENTIMENT_WEIGHTS)[0]
    load_id = random.choice(load_ids)
    carrier_mc, carrier_name = random.choice(CARRIERS)
    loadboard_rate = load_rates[load_id]
    num_neg = random.randint(0, 3)
    initial_offer = (
        round(loadboard_rate * random.uniform(0.75, 0.95), 2)
        if outcome != "carrier_ineligible"
        else None
    )
    agreed_rate = (
        round(loadboard_rate * random.uniform(0.82, 0.97), 2)
        if outcome == "booked"
        else None
    )
    days_ago = random.randint(0, 29)
    created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))
    DEMO_CALLS.append(
        CallRecord(
            call_id=str(uuid.uuid4()),
            load_id=load_id,
            carrier_mc=carrier_mc,
            carrier_name=carrier_name,
            initial_offer=initial_offer,
            agreed_rate=agreed_rate,
            loadboard_rate=loadboard_rate,
            num_negotiations=num_neg,
            outcome=outcome,
            sentiment=sentiment,
            created_at=created_at,
            notes=None,
        )
    )


def seed():
    db = SessionLocal()
    try:
        if db.query(Load).count() == 0:
            for data in LOADS:
                db.add(Load(**data))
            db.commit()
            print(f"Seeded {len(LOADS)} loads.")
        else:
            print("Loads already present. Skipping.")

        if db.query(CallRecord).count() == 0:
            for record in DEMO_CALLS:
                db.add(record)
            db.commit()
            print(f"Seeded {len(DEMO_CALLS)} demo call records.")
        else:
            print("Call records already present. Skipping.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Done.")
