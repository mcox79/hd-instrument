"""
v1 demo FastAPI app entry.

Mounts:
    /                       Landing page (v5 framing)
    /demo                   Cheap-decisive-test page (3 pre-cached Q/A)
    /playground             Interactive algebraic playground (AND/NOT/COUNT/counterfactual)
    /benchmark              30-query head-to-head (substrate vs gpt-4o-mini)
    /query/tier5a + family  Substrate-augmented Qwen-2.5-1.5B-Instruct + audit chain + baseline + algebraic ops
    /admin/warmup           Pre-warm Pythia + KB before customer demo

Run:
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"""
from __future__ import annotations
import faulthandler
import logging

# Per Research PRIORITY_RANKING_2026-06-09 acknowledgment 1: auto-diagnose native crashes
# so the next 0xC0000005 (or any future segfault) prints a Python-level traceback to stderr
# instead of dying silently. Cost: ~zero overhead; covers ALL backend processes from now on.
faulthandler.enable()
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
from backend.landing import landing_response
from backend.decisive_test import decisive_test_response
from backend.playground import playground_response
from backend.benchmark import benchmark_response
from backend.routes import converse, query_tier5a


# ============================================================
# App lifecycle
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Boot + shutdown hooks."""
    logger.info("v1 demo backend starting...")
    logger.info("openai key: %s | anthropic key: %s",
                "present" if config.OPENAI_API_KEY else "MISSING",
                "present" if config.ANTHROPIC_API_KEY else "MISSING")
    # Pre-load Tier 5a substrate-KV at startup. Skipped via TIER5_ENABLED=false.
    if config.TIER5_ENABLED:
        try:
            logger.info("pre-loading Tier 5a substrate-KV...")
            import threading

            def _bg_load():
                try:
                    from backend.routes.query_tier5a import _init_kv
                    kv = _init_kv()
                    logger.info("Tier 5a ready: %d facts loaded", len(kv))
                except Exception:
                    logger.exception("Tier 5a background load failed")

            threading.Thread(target=_bg_load, daemon=True, name="tier5a-loader").start()
            logger.info("Tier 5a load running in background; status: /query/tier5a/status")
        except Exception:
            logger.exception("Tier 5a loader spawn failed")
    yield
    logger.info("v1 demo backend shutting down")


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
# Tier 5 Sprint Panel A: substrate-KV + Qwen-2.5-1.5B-Instruct
# ============================================================
app.include_router(query_tier5a.router)
from backend.routes import converse_pp225
app.include_router(converse_pp225.router)

# Substrate-first /converse cascade routing (strategic reframe: substrate IS the AI)
app.include_router(converse.router)


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


@app.get("/playground")
async def playground():
    """Algebraic playground: interactive AND / NOT / COUNT / counterfactual against substrate KB."""
    return playground_response()


@app.get("/benchmark")
async def benchmark():
    """Head-to-head benchmark: 30 pre-cached queries; substrate vs gpt-4o-mini side-by-side."""
    return benchmark_response()


@app.get("/chat")
async def chat():
    """Substrate-first chat UI - frontend for the /converse cascade router."""
    return chat_response()


@app.get("/demo")
async def demo():
    """Decisive-test page: 3 pre-cached substrate-vs-bare-LLM side-by-side comparisons.

    Per Research's CHEAP_DECISIVE_TEST_FIRST note - validates 'same model, different
    substrate' framing on observers before more live infra is built.
    """
    return decisive_test_response()


@app.get("/demo/reasoning")
async def demo_reasoning():
    """Substrate-as-reasoning-substrate page (algebraic reasoning at L=3 composition).

    Per Research PRIORITY_RESPONSE 2026-06-10: focused on L=3 composition + algebra.
    Cognitive primitives (PP-315/317/318/304) moved to /demo/cognition. Lifecycle
    primitives (PP-319/320/322) moved to /demo/lifecycle.

    NOTE: this MUST be declared BEFORE /demo/{slug} or FastAPI's dynamic-route
    matcher dispatches /demo/reasoning to demo_vertical(slug="reasoning") and 404s.
    """
    from backend.reasoning_substrate import reasoning_response
    return reasoning_response()


@app.get("/demo/cognition")
async def demo_cognition():
    """Substrate cognitive primitives page (PP-304 / 315 / 317 / 318).

    Per Research PRIORITY_RESPONSE 2026-06-10: split out from /demo/reasoning.
    Embodied (PP-317 tool-extended REAL-DATA AUC=0.883), aesthetic (PP-318
    structural surprise signal), intrinsic motivation (PP-315 boredom), and
    meta-cognition (PP-304 confidence). PP-316 image-schema HELD as
    research-roadmap only (real-data 0.342 on polysemic concepts).
    """
    from backend.cognition_substrate import cognition_response
    return cognition_response()


@app.get("/demo/lifecycle")
async def demo_lifecycle():
    """Substrate lifecycle / continual-learning primitives page.

    Per Research PRIORITY_RESPONSE 2026-06-10: continual learning suite split
    out from /demo/reasoning. Frequency-selective decay (PP-319), intentional
    forgetting (PP-320), neurogenesis (PP-322), dual-CLS (d2_1 MIDDLE_BAND
    annotation). One of Research's defensible commercial-claim categories.
    """
    from backend.lifecycle_substrate import lifecycle_response
    return lifecycle_response()


@app.get("/demo/{slug}")
async def demo_vertical(slug: str):
    """Vertical demo landing pages per Research PRIORITY_RANKING_2026-06-09 P1 A1.

    Anchors a cycle-200 vertical proof per slug:
      /demo/legal       PP-208 PACER 99.9pct
      /demo/healthcare  PP-209 DDI 100pct
      /demo/finance     PP-211 SEC 10-K 100pct
      /demo/fda         PP-210 FDA audit 100pct
    """
    from backend.verticals import vertical_response
    return vertical_response(slug)


@app.get("/benchmark/fb15k-237")
async def benchmark_fb15k237():
    """FB15K-237 first public benchmark win page (PP-237 + PP-238 cycle 211).

    Showcase: substrate Hits@1 = 0.956 / Hits@10 = 0.992 / MRR = 0.974 on n=250
    2-hop ranking; first public KG benchmark win. Comparison to TransE / DistMult
    / RotatE / CompGCN baselines.
    """
    from backend.benchmark_fb15k237 import fb15k237_response
    return fb15k237_response()


@app.post("/admin/warmup")
async def admin_warmup():
    """Force Tier 5a substrate-KV to load NOW (eliminates cold-start 503 on first /query/tier5a).

    Operator hits this 30 sec before customer demos. Returns immediately with load status.
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


# Global load-progress state (read by /admin/load_status; written by background thread)
_load_progress: dict = {"in_progress": False, "source": None, "started_at": None,
                        "completed_at": None, "before": None, "after": None,
                        "added": None, "error": None}


def _do_admin_load(source: str):
    """Background-thread worker for /admin/load. Per Research KILL_LOAD_PROFILE_PREFIT
    (2026-06-09): /admin/load returns 202 immediately; this runs in a daemon thread.
    Pre-fit substrate state (scripts/prefit_substrate_state.py) means the load is
    fast (mmap path); legacy path also works (fit at load) but blocks longer.
    """
    from pathlib import Path as _Path
    import time as _t
    from backend.routes.query_tier5a import _init_kv
    global _load_progress
    _load_progress.update({"in_progress": True, "source": source,
                           "started_at": _t.time(), "completed_at": None,
                           "before": None, "after": None, "added": None, "error": None})
    try:
        state_dir = _Path("data/substrate_state") / source
        if not state_dir.exists() or not state_dir.is_dir():
            raise FileNotFoundError(f"no such source dir: {state_dir}")
        facts_p = state_dir / "facts.jsonl"
        keys_p = state_dir / "keys.npy"
        if not (facts_p.exists() and keys_p.exists()):
            raise FileNotFoundError(f"{source} missing facts.jsonl or keys.npy")
        kv = _init_kv()
        pre = len(kv)
        total = kv.load_from_disk(facts_p, keys_p)
        _load_progress.update({"in_progress": False, "completed_at": _t.time(),
                               "before": pre, "after": total, "added": total - pre})
        logger.info("/admin/load %s DONE: %d -> %d (+%d)", source, pre, total, total - pre)
    except Exception as e:
        logger.exception("/admin/load %s FAILED", source)
        _load_progress.update({"in_progress": False, "completed_at": _t.time(),
                               "error": str(e)})


@app.post("/admin/load")
async def admin_load(source: str):
    """Incrementally load a single substrate-state KB source from disk (NON-BLOCKING).

    Per Research KILL_LOAD_PROFILE_PREFIT (2026-06-09): runs the actual load in a
    background daemon thread + returns immediately. Poll /admin/load_status for
    completion. Inflight /converse never blocks.

    `source` is the subdir name under data/substrate_state/ (e.g. wikipedia_100k).
    """
    import threading
    if _load_progress.get("in_progress"):
        return {"status": "busy", "current_source": _load_progress["source"]}
    threading.Thread(target=_do_admin_load, args=(source,), daemon=True,
                     name=f"admin-load-{source}").start()
    return {"status": "accepted", "source": source, "poll": "/admin/load_status"}


@app.get("/admin/load_status")
async def admin_load_status():
    """Current state of /admin/load background work."""
    import time as _t
    p = dict(_load_progress)
    if p.get("started_at") and not p.get("completed_at"):
        p["elapsed_s"] = round(_t.time() - p["started_at"], 1)
    elif p.get("started_at") and p.get("completed_at"):
        p["wall_s"] = round(p["completed_at"] - p["started_at"], 1)
    return p


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
            "POST /admin/warmup",
        ],
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
