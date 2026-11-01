"""Loopback API: synthetic replay plus a separate, sanitized local coverage report."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query

from .engine import replay
from .loader import load_dataset, parse_timestamp
from .coverage_api import data_coverage

REPLAY_TIMES = [f"2026-10-30T09:{minute}:00+05:30" for minute in ("30", "35", "40")]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail startup with file/row diagnostics if fixtures are invalid.
    app.state.dataset = load_dataset()
    yield


app = FastAPI(title="Trade research — synthetic demo", version="0.1.0", lifespan=lifespan)


@app.get("/api/data-coverage")
def coverage_endpoint():
    return data_coverage()


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "synthetic_demo", "orders_enabled": False}


@app.get("/api/demo")
def demo():
    return {"mode": "synthetic_demo", "label": "Synthetic demo data — not current market data",
            "source": "Bundled synthetic fixtures", "replay_times": REPLAY_TIMES,
            "default_as_of": REPLAY_TIMES[1]}


@app.get("/api/replay")
def replay_endpoint(as_of: str = Query(..., description="ISO8601 with timezone offset")):
    try:
        parsed = parse_timestamp(as_of, "as_of")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return replay(app.state.dataset, parsed)
