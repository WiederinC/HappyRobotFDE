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
        ├── GET  /loads/           Search available loads
        ├── GET  /loads/{id}       Fetch a specific load
        ├── PATCH /loads/{id}/book Mark a load as booked
        ├── GET  /carrier/verify   FMCSA carrier eligibility check
        ├── POST /calls/           Record a completed call
        ├── GET  /calls/           List all calls
        ├── GET  /metrics/         Aggregated dashboard metrics
        └── GET  /metrics/         Aggregated business metrics
  Streamlit Dashboard (port 8501)
        ├── Revenue Impact band (revenue booked vs at-risk)
        ├── Actionable Insights (auto-generated)
        ├── Lane Performance table
        ├── Carrier Value leaderboard
        └── Daily call volume trend
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
# Dashboard: http://localhost:8000/dashboard
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

## Environment Variables

| Variable        | Required | Default                        | Description                         |
|-----------------|----------|--------------------------------|-------------------------------------|
| `API_KEY`       | Yes      | `hr-dev-key-change-in-prod`    | Shared secret for all endpoints     |
| `DATABASE_URL`  | No       | `sqlite:///./carrier.db`       | SQLAlchemy DB URL                   |
| `FMCSA_WEB_KEY` | No       | *(empty — mock mode)*          | FMCSA API key for carrier lookup    |

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

### Record a call
```
POST /calls/
Content-Type: application/json
X-API-Key: <key>

{
  "load_id": "LD-001",
  "carrier_mc": "MC123456",
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

**Outcome values:** `booked` | `declined` | `no_deal` | `carrier_ineligible`
**Sentiment values:** `positive` | `neutral` | `negative`

---

## HappyRobot Workflow — Call Flow

The AI agent follows this sequence on every inbound call:

1. **Greet** the carrier and ask for their **MC number**
2. Call `GET /carrier/verify?mc_number=<mc>` → if `eligible: false`, politely decline and end the call
3. Ask for the carrier's **origin / destination / equipment type**
4. Call `GET /loads/?origin=<o>&destination=<d>&equipment_type=<e>` → pitch the best matching load
5. **Negotiate** — up to 3 counter-offers; accept if within 5% of loadboard rate
6. If deal agreed → call `PATCH /loads/{id}/book`, then say "Transfer was successful, the booking team will follow up within 30 minutes"
7. Post-call → call `POST /calls/` with the extracted data (MC, load, rates, outcome, sentiment)

---

## Cloud Deployment (Fly.io example)

```bash
# Install flyctl, then:
fly launch --name happyrobot-carrier --region ord
fly secrets set API_KEY=<strong-key> FMCSA_WEB_KEY=<your-key>
fly volumes create carrier_data --size 1
fly deploy
```

Add to `fly.toml`:
```toml
[mounts]
  source = "carrier_data"
  destination = "/data"
```

---

## Load Fields Reference

| Field              | Type    | Description                     |
|--------------------|---------|---------------------------------|
| `load_id`          | string  | Unique identifier                |
| `origin`           | string  | Starting location                |
| `destination`      | string  | Delivery location                |
| `pickup_datetime`  | string  | Date/time for pickup             |
| `delivery_datetime`| string  | Date/time for delivery           |
| `equipment_type`   | string  | Dry Van / Reefer / Flatbed       |
| `loadboard_rate`   | float   | Listed rate ($)                  |
| `notes`            | string  | Special instructions             |
| `weight`           | float   | Load weight (lbs)                |
| `commodity_type`   | string  | Type of goods                    |
| `num_of_pieces`    | int     | Number of items                  |
| `miles`            | float   | Distance                         |
| `dimensions`       | string  | Trailer size                     |
| `status`           | string  | `available` or `booked`          |
