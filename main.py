"""main.py - TasteBridge FastAPI server."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.agent import TasteBridgeAgent

app = FastAPI(title="TasteBridge")
agent = TasteBridgeAgent()
STATIC = Path(__file__).resolve().parent / "static"


class TranslateRequest(BaseModel):
    taste: str
    city: str
    domains: list[str] | None = None


class NegotiateRequest(BaseModel):
    tastes: list[str]
    city: str
    domain: str = "dining"


class HeatmapRequest(BaseModel):
    taste: str
    city: str


@app.get("/")
def home():
    index = STATIC / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"status": "TasteBridge API", "hint": "static/index.html not built yet"}


@app.post("/api/translate")
def translate(req: TranslateRequest):
    return agent.translate(req.taste, req.city, req.domains)


@app.post("/api/negotiate")
def negotiate(req: NegotiateRequest):
    return agent.negotiate(req.tastes, req.city, req.domain)


@app.post("/api/heatmap")
def heatmap(req: HeatmapRequest):
    return agent.heatmap(req.taste, req.city)


@app.post("/api/plan")
def plan(req: HeatmapRequest):
    return agent.plan(req.taste, req.city)
