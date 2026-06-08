"""
v1 demo FastAPI app entry.

Mounts:
    /admin/demo-mode-on, /admin/demo-mode-off, /admin/demo-mode-status  (control plane)
    /query                                                                (main endpoint)
    /add_fact, /delete_facts, /scale_stats, /audit_chain/{id}            (stubs for W1+W2)
    /                                                                     (health probe + cards)

Run:
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"""
from __future__ import annotations
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError:
    raise SystemExit("FastAPI not installed; pip install fastapi 'uvicorn[standard]' pydantic")

# Load .env.local before anything else so config.py sees the values
try:
    from dotenv import load_dotenv
    from pathlib import Path
    env_path = Path(__file__).resolve().parents[1] / ".env.local"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from backend import config
from backend.admin import demo_mode
from backend.landing import landing_response
from backend.decisive_test import decisive_test_response
from backend.routes import query_tier5a


# ============================================================
# App lifecycle
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Boot + shutdown hooks."""
    logger.info("v1 demo backend starting; reconciling demo-mode state...")
    boot = demo_mode.reconcile_on_boot()
    logger.info("demo-mode boot: %s", boot)
    logger.info("openai key: %s | anthropic key: %s",
                "present" if config.OPENAI_API_KEY else "MISSING",
                "present" if config.ANTHROPIC_API_KEY else "MISSING")
    # Pre-load Tier 5a substrate-KV at startup. Skipped in tests via TIER5_ENABLED=false.
    if config.TIER5_ENABLED:
        try:
            logger.info("pre-loading Tier 5a substrate-KV (Pythia + 50 facts)...")
            import threading

            def _bg_load():
                try:
                    from backend.routes.query_tier5a import _init_kv
                    kv = _init_kv()
                    logger.info("Tier 5a ready: %d facts loaded", len(kv))
                except Exception:
                    logger.exception("Tier 5a background load failed")

            # Non-blocking: server accepts requests immediately; tier5a returns 503 until loaded.
            threading.Thread(target=_bg_load, daemon=True, name="tier5a-loader").start()
            logger.info("Tier 5a load running in background; status: /query/tier5a/status")
        except Exception:
            logger.exception("Tier 5a loader spawn failed")
    yield
    logger.info("v1 demo backend shutting down; resuming any suspended procs as a courtesy")
    if demo_mode.get_status().get("active"):
        demo_mode.deactivate(reason="auto:backend-shutdown")


app = FastAPI(
    title="Substrate v1 Demo",
    version="0.1.0",
    description="Substrate-augmented LLM demo (gpt-4o-mini + substrate vs bare gpt-4o-mini)",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Admin (mounted from backend/admin/demo_mode.py)
# ============================================================

if demo_mode.router is not None:
    app.include_router(demo_mode.router)

# Tier 5 Sprint Panel A: substrate-KV + Pythia-1.4B
app.include_router(query_tier5a.router)


# ============================================================
# Request / response models
# ============================================================

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    kb: str = Field("hybrid", description="wikipedia / corporate / hybrid")
    llm: str = Field("gpt-4o-mini", description="gpt-4o-mini / claude-haiku")
    show_audit: bool = Field(False)


class AnswerPanel(BaseModel):
    answer: str
    cost_usd: float
    latency_ms: float
    confidence: Optional[float] = None
    facts_used: Optional[list] = None
    audit_chain: Optional[list] = None


class QueryResponse(BaseModel):
    query_id: str
    bare: AnswerPanel
    substrate: AnswerPanel
    winner: Optional[str] = None  # "substrate" / "bare" / "tie"
    substrate_stats: dict = Field(default_factory=dict)


class AddFactRequest(BaseModel):
    fact: Optional[str] = None       # NL form, e.g. "Anthropic released Claude 4.6 in June 2026"
    subject: Optional[str] = None    # OR structured triple form
    relation: Optional[str] = None
    object: Optional[str] = None


class DeleteFactsRequest(BaseModel):
    entity: str


# ============================================================
# Routes (W1: query stub; W2: implement)
# ============================================================

@app.get("/")
async def root():
    """Browser-friendly landing page."""
    return landing_response()


@app.get("/demo")
async def demo():
    """Decisive-test page: 3 pre-cached substrate-vs-bare-LLM side-by-side comparisons.

    Per Research's CHEAP_DECISIVE_TEST_FIRST note - validates 'same model, different
    substrate' framing on observers before more live infra is built.
    """
    return decisive_test_response()


@app.post("/admin/warmup")
async def admin_warmup():
    """Force Tier 5a substrate-KV to load NOW (eliminates cold-start 503 on first /query/tier5a).

    Demo operators hit this 30 sec before customer demos to ensure Pythia + KB are ready.
    Returns immediately with the current load status; load continues in background if needed.
    """
    from backend.routes.query_tier5a import _kv, _init_kv
    if _kv is not None:
        return {"status": "already_loaded", "kb_size": len(_kv)}
    import threading

    def _bg():
        try:
            _init_kv()
        except Exception:
            logger.exception("warmup background init failed")
    threading.Thread(target=_bg, daemon=True, name="admin-warmup").start()
    return {"status": "loading_in_background", "poll": "/query/tier5a/status"}


@app.get("/api")
async def api_root():
    """JSON service description (programmatic use)."""
    return {
        "service": "substrate v1 demo",
        "version": app.version,
        "endpoints": [
            "POST /query",
            "POST /add_fact",
            "POST /delete_facts",
            "GET /scale_stats",
            "GET /audit_chain/{query_id}",
            "POST /admin/demo-mode-on",
            "POST /admin/demo-mode-off",
            "GET /admin/demo-mode-status",
        ],
        "demo_mode": demo_mode.get_status(),
        "llm": {
            "openai_configured": bool(config.OPENAI_API_KEY),
            "anthropic_configured": bool(config.ANTHROPIC_API_KEY),
            "openai_model": config.OPENAI_MODEL,
            "anthropic_model": config.ANTHROPIC_MODEL,
        },
    }


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """Main query endpoint -- W1 implementation pending."""
    demo_mode.note_query_activity()
    t0 = time.perf_counter()
    query_id = f"q_{int(t0 * 1e6)}"
    # Stub: returns placeholder data until W1 wires the substrate + LLM clients
    return QueryResponse(
        query_id=query_id,
        bare=AnswerPanel(
            answer="(W1 stub: bare LLM call will be wired in backend/llm/openai_client.py)",
            cost_usd=0.0,
            latency_ms=(time.perf_counter() - t0) * 1000,
        ),
        substrate=AnswerPanel(
            answer="(W1 stub: substrate K-hop retrieval will be wired in substrate/khop.py)",
            cost_usd=0.0,
            latency_ms=(time.perf_counter() - t0) * 1000,
            confidence=None,
            facts_used=[],
            audit_chain=None,
        ),
        winner=None,
        substrate_stats={
            "total_facts": 0,
            "shard_count": 0,
            "last_sleep_defrag_age_s": None,
            "kb_selected": req.kb,
        },
    )


@app.post("/add_fact")
async def add_fact(req: AddFactRequest):
    """W1 stub. Live substrate.write() to be wired in substrate/shards.py."""
    raise HTTPException(status_code=501, detail="W1 stub; add_fact will be wired in Week 1 Day 4")


@app.post("/delete_facts")
async def delete_facts(req: DeleteFactsRequest):
    """W1 stub. Live substrate.surgical_erase() to be wired in substrate/gdpr.py."""
    raise HTTPException(status_code=501, detail="W1 stub; delete_facts will be wired in Week 1 Day 4")


@app.get("/scale_stats")
async def scale_stats():
    """W1 stub. Returns substrate scale metadata (facts, shards, sleep-defrag time)."""
    return {
        "total_facts": 0,
        "shard_count": 0,
        "avg_facts_per_shard": 0,
        "llm_context_limit_tokens": 128000,  # gpt-4o-mini
        "substrate_capacity_ratio": "n/a (no KB loaded yet)",
        "last_sleep_defrag_at": None,
    }


@app.get("/audit_chain/{query_id}")
async def audit_chain(query_id: str):
    """W1 stub. Returns per-step K-hop chain + Merkle proof for a query."""
    raise HTTPException(status_code=404, detail=f"audit chain for {query_id} not found (W1 stub)")


# ============================================================
# Local entry (for `python -m backend.main`)
# ============================================================

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    uvicorn.run(
        "backend.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
    )
