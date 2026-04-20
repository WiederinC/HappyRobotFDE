import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

from api.database import Base, engine
from api.routers import calls, carrier, loads, matches, metrics, waitlist


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="HappyRobot Carrier API",
    description=(
        "Inbound carrier sales automation API — "
        "load search, FMCSA carrier verification, call recording & analytics."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loads.router)
app.include_router(carrier.router)
app.include_router(calls.router)
app.include_router(metrics.router)
app.include_router(waitlist.router)
app.include_router(matches.router)

# Serve the analytics dashboard as static files
dashboard_dir = Path(__file__).parent.parent / "dashboard"
if dashboard_dir.exists():
    app.mount(
        "/dashboard",
        StaticFiles(directory=str(dashboard_dir), html=True),
        name="dashboard",
    )


@app.get("/", tags=["health"])
def root():
    return {
        "service": "HappyRobot Carrier API",
        "version": "1.0.0",
        "docs": "/docs",
        "dashboard": "/dashboard",
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
