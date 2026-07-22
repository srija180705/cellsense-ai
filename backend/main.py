"""
CellSense AI — FastAPI backend (Phase P2).

Serves the fleet overview and per-asset detail from the trained SoH/RUL models.
Run from the repo root:

    uvicorn backend.main:app --reload --port 8000

Endpoints:
    GET /api/health
    GET /api/fleet
    GET /api/assets/{asset_id}
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend import fleet_service
from agents.orchestrator import run as run_agents

app = FastAPI(title="CellSense AI API", version="0.1.0")

# Allow the React dev server (any origin) during the hackathon
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CellSense AI", "version": app.version}


@app.get("/api/fleet")
def fleet():
    assets = fleet_service.get_fleet()
    summary = {
        "total": len(assets),
        "critical": sum(a["risk"] == "Critical" for a in assets),
        "watch": sum(a["risk"] == "Watch" for a in assets),
        "healthy": sum(a["risk"] == "Healthy" for a in assets),
    }
    return {"summary": summary, "assets": assets}


@app.get("/api/assets/{asset_id}")
def asset(asset_id: str):
    detail = fleet_service.get_asset(asset_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="asset not found")
    return detail


@app.post("/api/assets/{asset_id}/recommend")
def recommend(asset_id: str):
    detail = fleet_service.get_asset(asset_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="asset not found")
    return run_agents(detail)
