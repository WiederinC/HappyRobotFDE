# HappyRobot Inbound Carrier Sales — Backend API

Proof-of-concept backend for HappyRobot's inbound carrier sales automation.
Carriers call in via the HappyRobot web-call trigger; this API handles load search,
FMCSA carrier verification, call data recording, and analytics.

---

## Architecture

```
HappyRobot Platform (voice AI)
        │
        │  HTTP + X-API-Key
        ▼
  FastAPI Backend  ──── SQLite / Postgres
        │
        ├── GET  /loads/                Search available loads
        ├── GET  /loads/{id}            Fetch a specific load
        ├── POST /loads/book            Mark a load as booked
        ├── GET  /carrier/verify        FMCSA carrier eligibility check
        ├── GET  /carrier/history       Returning carrier call history
        ├── POST /calls/                Record a completed call
        ├── GET  /calls/                List all calls
        ├── POST /waitlist/             Add carrier to waitlist or rate hold
        ├── GET  /waitlist/             List waitlist entries
        ├── GET  /matches/              Cross-reference open loads with waitlist
        └── GET  /metrics/             Aggregated business metrics

  Streamlit Dashboard (port 8501)
        ├── Overview tab: KPIs, charts, lane performance, carrier value
        └── Operations tab: open loads, waitlist, callback opportunities
```

---

## Quick Start (local)

```bash
# 1. Clone & enter directory
git clone <repo-url> && cd happyrobot-carrier

# 2. Create virtual environment
python -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install -r api/requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — set API_KEY and optionally FMCSA_WEB_KEY

# 5. Seed the database with sample loads + demo calls
python -m api.seed

# 6. Run the server
uvicorn api.main:app --reload

# API docs:  http://localhost:8000/docs
```

---

## Docker

```bash
# Build & run both services (API + Streamlit dashboard)
docker compose up --build

# API:            http://localhost:8000
# API Docs:       http://localhost:8000/docs
# Dashboard:      http://localhost:8501
```

The API service seeds the database automatically on first start.
SQLite data is persisted in a named Docker volume (`carrier-data`).

---

## Cloud Deployment (Railway)

Both services are deployed on Railway:

| Service   | URL                                                        |
|-----------|------------------------------------------------------------|
| API       | https://happyrobot-carrier-production.up.railway.app       |
| Dashboard | https://dashboard-production-332e.up.railway.app           |

To redeploy:
```bash
railway login
railway up                          # redeploy API
railway up --service dashboard      # redeploy dashboard
```

---

## Environment Variables

| Variable        | Required | Default                     | Description                      |
|-----------------|----------|-----------------------------|----------------------------------|
| `API_KEY`       | Yes      | `hr-dev-key-change-in-prod` | Shared secret for all endpoints  |
| `DATABASE_URL`  | No       | `sqlite:///./carrier.db`    | SQLAlchemy DB URL                |
| `FMCSA_WEB_KEY` | No       | *(empty — mock mode)*       | FMCSA API key for carrier lookup |

---

## API Authentication

All endpoints require the `X-API-Key` header:

```
X-API-Key: hr-dev-key-change-in-prod
```

---

## Key Endpoints

### Search loads
```
GET /loads/?origin=Chicago&equipment_type=Dry+Van
```

### Verify carrier (FMCSA)
```
GET /carrier/verify?mc_number=123456
```
Returns `eligible: true/false` plus carrier details.
Without `FMCSA_WEB_KEY`, returns a mock active response for development.

### Carrier history
```
GET /carrier/history?mc_number=123456
```
Returns returning carrier info: total calls, bookings, last lane, booking rate.

### Record a call
```
POST /calls/
Content-Type: application/json
X-API-Key: <key>

{
  "load_id": "LD-001",
  "carrier_mc": "123456",
  "carrier_name": "Swift Transport LLC",
  "initial_offer": 2600,
  "agreed_rate": 2750,
  "loadboard_rate": 2800,
  "num_negotiations": 2,
  "outcome": "booked",
  "sentiment": "positive",
  "notes": "Carrier was flexible after second counter-offer"
}
```

**Outcome values:** `booked` | `declined` | `no_deal` | `carrier_ineligible` | `rate_hold` | `waitlisted`
**Sentiment values:** `positive` | `neutral` | `negative`

### Add to waitlist
```
POST /waitlist/
{
  "entry_type": "lane_unavailable",
  "carrier_mc": "123456",
  "carrier_name": "Swift Transport LLC",
  "origin": "Chicago, IL",
  "destination": "Dallas, TX",
  "equipment_type": "Dry Van",
  "availability_window": "next week"
}
```

**Entry types:** `lane_unavailable` | `rate_hold`

---

## HappyRobot Workflow — Call Flow

1. **Greet** the carrier and ask for their **MC number**
2. Call `GET /carrier/verify` → if `eligible: false`, decline and end
3. Call `GET /carrier/history` → personalise greeting for returning carriers
4. Ask for origin / equipment type / availability
5. Call `GET /loads/` → pitch the best matching load (RPM, fuel estimate)
6. **Negotiate** — up to 3 rounds; accept if within 10% of loadboard rate
7. If deal agreed → call `POST /loads/book`, send confirmation email
8. Offer circuit load from delivery city (search origin = destination)
9. If no loads → offer waitlist via `POST /waitlist/`
10. Post-call AI node → extracts data → `POST /calls/`
