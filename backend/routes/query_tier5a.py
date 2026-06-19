"""
/query/tier5a -- Tier 5 Sprint Panel A endpoint.

Pipeline:
  1. Receive user question.
  2. Encode question via Pythia-1.4B last-token hidden state.
  3. Retrieve top-K relevant facts from substrate-KV (ZCA-whitened cosine).
  4. Inject retrieved facts into a prompt for Pythia-1.4B.
  5. Generate answer via Pythia.
  6. Return JSON with answer + audit chain (retrieval + generation) + facts used + latency.

Substrate is the LLM's memory; Pythia is the interface that talks back.
"""
from __future__ import annotations
import logging
import time
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from substrate.audit import AuditChain
from substrate.kv_memory import SubstrateKV
from backend.kb.seed_facts import load_seed_facts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["query"])

# Singleton state -- lazy-init on first request so backend boots fast.
_kv: Optional[SubstrateKV] = None
_kv_init_error: Optional[str] = None

# Audit chain store: query_id -> chain dict (in-memory; persists for backend session)
_audit_chain_store: dict = {}
_MAX_STORED_CHAINS = 1000


class Tier5aRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(5, ge=1, le=20, description="number of substrate-KV facts to retrieve")
    max_new_tokens: int = Field(80, ge=8, le=200)
    temperature: float = Field(0.3, ge=0.0, le=1.5)


class RetrievedFact(BaseModel):
    fact: str
    score: float


class Tier5aResponse(BaseModel):
    query_id: str
    question: str
    answer: str
    facts_used: list[RetrievedFact]
    audit_chain_root: str
    audit_chain: dict
    substrate_latency_ms: float
    llm_latency_ms: float
    total_latency_ms: float
    llm_model: str
    llm_input_tokens: int
    llm_output_tokens: int
    cost_usd: float = 0.0


def _init_kv() -> SubstrateKV:
    """Lazy-init substrate-KV with seeded facts.

    Per Research VERIFY Q1: uses bge-large (CPU) for retrieval encoding (production
    encoder per cycle 187 PP-144). Qwen-2.5-1.5B-Instruct stays as the LLM generator
    (separately loaded by pythia_client).
    """
    global _kv, _kv_init_error
    if _kv is not None:
        return _kv
    if _kv_init_error is not None:
        raise HTTPException(status_code=503, detail=f"substrate-KV init failed earlier: {_kv_init_error}")
    import time as _t_init
    _t_init_start = _t_init.perf_counter()
    _ts = {}

    def _stamp(name):
        _ts[name] = _t_init.perf_counter() - _t_init_start
        logger.info("[_init_kv timing] %s: %.2fs", name, _ts[name])

    try:
        from backend.llm.bge_encoder import get_encoder
        encoder = get_encoder()
        _stamp("bge_encoder_loaded")
        kv = SubstrateKV(encoder=encoder, dim=encoder.hidden_size)
        facts = load_seed_facts()
        logger.info("seeding substrate-KV with %d facts via %s on %s ...",
                    len(facts), encoder.model_name, encoder.device)
        kv.add_facts(facts)
        _stamp("seed_facts_added")

        # Q2+POST: auto-load ANY available pre-encoded substrate-state dirs from disk.
        # Each dir holds (facts.jsonl, keys.npy) pair produced by backend/kb/*_ingest.py.
        # In-flight ingests don't have keys.npy yet (only written at end of run) so they're
        # skipped naturally.
        # Per Research BACKEND_GREENLIGHT_AND_MONITOR (2026-06-09): SKIP_KB_AUTOLOAD=1
        # boots backend with seed facts only; KB sources are loaded later via /admin/load
        # endpoint. De-risks restart in case any latent issue remains after pyarrow fix.
        import os as _os
        if _os.environ.get("SKIP_KB_AUTOLOAD", "0") == "1":
            logger.info("SKIP_KB_AUTOLOAD=1: backend booting with seed facts only; "
                        "use /admin/load to load KB sources incrementally")
        else:
            from pathlib import Path as _Path
            import time as _t
            state_root = _Path("data/substrate_state")
            if state_root.exists():
                for state_dir in sorted(state_root.iterdir()):
                    if not state_dir.is_dir():
                        continue
                    facts_p = state_dir / "facts.jsonl"
                    keys_p = state_dir / "keys.npy"
                    if not (facts_p.exists() and keys_p.exists()):
                        logger.info("%s: skip (no keys.npy yet; ingest in flight)", state_dir.name)
                        continue
                    try:
                        t0 = _t.perf_counter()
                        pre = len(kv)
                        total = kv.load_from_disk(facts_p, keys_p)
                        logger.info("loaded %s: %d -> %d facts (+%d) in %.1fs",
                                    state_dir.name, pre, total, total - pre, _t.perf_counter() - t0)
                    except Exception:
                        logger.exception("%s: disk load failed (continuing)", state_dir.name)

        # Pre-load Qwen generator too so first /query/tier5a has zero LLM cold-start
        from backend.llm.pythia_client import get_client
        get_client()
        _stamp("qwen_loaded")
        _kv = kv
        logger.info("[_init_kv done] total %.2fs; phases=%s",
                    _t_init.perf_counter() - _t_init_start, _ts)
        return _kv
    except Exception as e:
        _kv_init_error = f"{type(e).__name__}: {e}"
        logger.exception("substrate-KV init failed")
        raise HTTPException(status_code=503, detail=_kv_init_error)


SYSTEM_PROMPT = (
    "You are a helpful assistant. You will be given a list of substrate-provided facts and "
    "a question. Answer the question using ONLY the facts. If the facts do not cover the "
    "question, say 'I do not know based on the substrate facts.' Cite the relevant facts "
    "verbatim when you can."
)


def _build_user_prompt(question: str, facts: list[tuple]) -> str:
    """User-message body for instruct models. System prompt is supplied separately."""
    facts_block = "\n".join(f"{i + 1}. {f}" for i, (f, _s) in enumerate(facts))
    return f"Substrate facts:\n{facts_block}\n\nQuestion: {question}"


@router.post("/tier5a", response_model=Tier5aResponse)
async def query_tier5a(req: Tier5aRequest):
    """Tier 5a: substrate-KV + Qwen-2.5-1.5B-Instruct end-to-end."""
    kv = _init_kv()
    from backend.llm.pythia_client import get_client
    client = get_client()

    t_total0 = time.perf_counter()

    # 1. Substrate retrieve
    t0 = time.perf_counter()
    retrieved = kv.retrieve(req.question, top_k=req.top_k)
    substrate_ms = (time.perf_counter() - t0) * 1000

    # 2. Build prompt + generate (chat-template path for instruct models)
    user_prompt = _build_user_prompt(req.question, retrieved)
    gen = client.generate(
        user_prompt,
        max_new_tokens=req.max_new_tokens,
        temperature=req.temperature,
        system=SYSTEM_PROMPT,
    )

    total_ms = (time.perf_counter() - t_total0) * 1000

    # 3. Audit chain
    query_id = f"t5a_{int(time.time() * 1e6)}"
    chain = AuditChain(chain_id=f"tier5a:{query_id}")
    chain.append("substrate_retrieve", {
        "top_k": req.top_k,
        "retrieved": [{"fact": f[:100], "score": round(s, 4)} for f, s in retrieved],
        "substrate_latency_ms": round(substrate_ms, 3),
        "kb_size": len(kv),
    })
    chain.append("llm_generate", {
        "model": gen.model,
        "input_tokens": gen.input_tokens,
        "output_tokens": gen.output_tokens,
        "latency_ms": round(gen.latency_ms, 1),
    })
    chain.append("answer", {"text": gen.text[:200]})

    # Store audit chain so /query/tier5a/audit_chain/{query_id} can retrieve it
    _audit_chain_store[query_id] = chain.to_dict()
    if len(_audit_chain_store) > _MAX_STORED_CHAINS:
        # Drop the oldest by lexicographic query_id (timestamp-prefixed, so chronological)
        oldest = min(_audit_chain_store.keys())
        _audit_chain_store.pop(oldest, None)

    return Tier5aResponse(
        query_id=query_id,
        question=req.question,
        answer=gen.text,
        facts_used=[RetrievedFact(fact=f, score=s) for f, s in retrieved],
        audit_chain_root=chain.root,
        audit_chain=chain.to_dict(),
        substrate_latency_ms=substrate_ms,
        llm_latency_ms=gen.latency_ms,
        total_latency_ms=total_ms,
        llm_model=gen.model,
        llm_input_tokens=gen.input_tokens,
        llm_output_tokens=gen.output_tokens,
        cost_usd=0.0,  # local inference
    )


# ============================================================
# Audit chain retrieval (Day 1-2 hardening per Research VERIFY)
# ============================================================

@router.get("/tier5a/audit_chain/{query_id}")
async def get_audit_chain(query_id: str):
    """Return the full Merkle-committed audit chain for a previous query.

    Audit chains are stored in-memory for the backend session (FIFO to MAX_STORED).
    Persistent audit storage is a v1.1 upgrade (write to disk per query_id).
    """
    if query_id not in _audit_chain_store:
        raise HTTPException(status_code=404, detail=f"audit chain for {query_id} not found")
    return _audit_chain_store[query_id]


@router.get("/tier5a/audit_chain")
async def list_audit_chains():
    """List recent query_ids whose audit chains are still in memory."""
    return {
        "stored_count": len(_audit_chain_store),
        "max_stored": _MAX_STORED_CHAINS,
        "recent_query_ids": sorted(_audit_chain_store.keys())[-20:],
    }


# ============================================================
# Baseline endpoint: same question, bare gpt-4o-mini (head-to-head comparison)
# ============================================================

class BaselineResponse(BaseModel):
    query_id: str
    question: str
    substrate: Tier5aResponse
    bare_llm: dict


@router.post("/tier5a/baseline", response_model=BaselineResponse)
async def query_tier5a_baseline(req: Tier5aRequest):
    """Side-by-side: substrate-augmented Qwen vs bare gpt-4o-mini answer for the SAME question.

    Returns BOTH responses + relative cost / latency / provenance for the demo head-to-head panel.
    Uses gpt-4o-mini API (costs ~$0.0001-0.001 per call; OPENAI_API_KEY required).
    """
    # 1. Substrate-augmented response
    substrate_resp = await query_tier5a(req)

    # 2. Bare gpt-4o-mini baseline (SAME question; no substrate context; same instruction profile)
    from backend.llm.openai_client import ask_bare
    bare_system = (
        "You are a helpful assistant. Answer the user's question directly and concisely. "
        "If you do not know, say 'I don't know' rather than guessing."
    )
    try:
        bare = ask_bare(req.question, system=bare_system, max_tokens=req.max_new_tokens, temperature=req.temperature)
        bare_resp = {
            "answer": bare.text,
            "model": bare.model,
            "input_tokens": bare.input_tokens,
            "output_tokens": bare.output_tokens,
            "cost_usd": bare.cost_usd,
            "latency_ms": bare.latency_ms,
            "finish_reason": bare.finish_reason,
            "provenance": "training data (unverifiable)",
        }
    except Exception as e:
        bare_resp = {"error": f"{type(e).__name__}: {e}", "model": "gpt-4o-mini (unavailable)"}

    return BaselineResponse(
        query_id=substrate_resp.query_id,
        question=req.question,
        substrate=substrate_resp,
        bare_llm=bare_resp,
    )


# ============================================================
# Algebraic ops -- categorical operations no vector DB has (per SPEC v5)
# AND / NOT / COUNT compose over the substrate's fact set with deterministic,
# auditable semantics. A pure-cosine vector DB cannot express these directly.
# ============================================================


class AndRequest(BaseModel):
    terms: list[str] = Field(..., min_length=2, description="2+ terms; facts must contain ALL")
    case_sensitive: bool = False
    limit: int = Field(20, ge=1, le=200)


class NotRequest(BaseModel):
    include: list[str] = Field(..., min_length=1, description="facts must contain ALL these terms")
    exclude: list[str] = Field(..., min_length=1, description="facts must contain NONE of these")
    case_sensitive: bool = False
    limit: int = Field(20, ge=1, le=200)


class CountRequest(BaseModel):
    term: str = Field(..., min_length=1)
    case_sensitive: bool = False


def _normalize(s: str, case_sensitive: bool) -> str:
    return s if case_sensitive else s.lower()


@router.post("/tier5a/and")
async def query_tier5a_and(req: AndRequest):
    """AND: facts containing ALL terms. Vector DBs only do AND via re-ranking; we do
    it exactly over the structured fact set."""
    kv = _init_kv()
    terms = [_normalize(t, req.case_sensitive) for t in req.terms]
    hits = []
    for f in kv.facts:
        h = _normalize(f, req.case_sensitive)
        if all(t in h for t in terms):
            hits.append(f)
            if len(hits) >= req.limit:
                break
    return {
        "operation": "AND",
        "terms": req.terms,
        "match_count": len(hits),
        "facts": hits,
        "kb_size": len(kv),
    }


@router.post("/tier5a/not")
async def query_tier5a_not(req: NotRequest):
    """NOT: facts including ALL `include` terms but NONE of `exclude`. Algebraic set
    difference - categorical operation no vector DB expresses cleanly."""
    kv = _init_kv()
    inc = [_normalize(t, req.case_sensitive) for t in req.include]
    exc = [_normalize(t, req.case_sensitive) for t in req.exclude]
    hits = []
    for f in kv.facts:
        h = _normalize(f, req.case_sensitive)
        if all(t in h for t in inc) and not any(t in h for t in exc):
            hits.append(f)
            if len(hits) >= req.limit:
                break
    return {
        "operation": "NOT (include AND NOT exclude)",
        "include": req.include,
        "exclude": req.exclude,
        "match_count": len(hits),
        "facts": hits,
        "kb_size": len(kv),
    }


@router.post("/tier5a/count")
async def query_tier5a_count(req: CountRequest):
    """COUNT: cardinality of facts containing `term`. Substrate exposes set sizes
    natively; vector DBs only do top-K retrieval."""
    kv = _init_kv()
    t = _normalize(req.term, req.case_sensitive)
    n = sum(1 for f in kv.facts if t in _normalize(f, req.case_sensitive))
    return {
        "operation": "COUNT",
        "term": req.term,
        "count": n,
        "kb_size": len(kv),
        "fraction_of_kb": round(n / max(1, len(kv)), 4),
    }


# ============================================================
# Counterfactual algebraic op (per SPEC v5: "categorical operations no vector DB has")
# ============================================================

class CounterfactualRequest(BaseModel):
    base_facts: dict = Field(..., description="{name: value} for base facts")
    derived: list = Field(..., description="list of {name, formula, parents}; formula is a Python lambda string")
    intervention: dict = Field(..., description="{name: new_value} for do() override")


@router.post("/tier5a/counterfactual")
async def query_tier5a_counterfactual(req: CounterfactualRequest):
    """Pearl-style do() operator on a small DAG. Returns factual + counterfactual + audit chain.

    This is a *visible* example of substrate's algebraic capabilities: a real counterfactual
    operation that bare LLMs and vector DBs cannot offer. The audit chain Merkle-commits
    to the intervention + every recomputed value (tamper-evident).
    """
    from substrate.counterfactual import CausalDAG, do

    dag = CausalDAG()
    for name, value in req.base_facts.items():
        dag.add_base(name, value)

    # Parse "formula" strings as Python expressions over `parents` dict values
    for d in req.derived:
        name = d["name"]
        parents = d["parents"]
        formula = d["formula"]  # e.g. "p['x'] + p['y']" with p being parents dict
        # Build a closure that evaluates the formula with parents dict
        def make_fn(form: str):
            def _fn(p):
                return eval(form, {"__builtins__": {}}, {"p": p})
            return _fn
        dag.add_derived(name, make_fn(formula), parents=parents)

    import time
    qid = f"t5a_cf_{int(time.time() * 1e6)}"
    result = do(dag, intervention=req.intervention, query_id=qid)
    _audit_chain_store[qid] = result.audit_chain.to_dict()

    return {
        "query_id": qid,
        "intervention": result.intervention,
        "factual": result.factual_values,
        "counterfactual": result.counterfactual_values,
        "differences": result.differences,
        "audit_chain_root": result.chain_root,
        "audit_chain": result.audit_chain.to_dict(),
    }


@router.get("/tier5a/status")
async def tier5a_status():
    """Report substrate-KV init state without forcing init."""
    global _kv, _kv_init_error
    return {
        "kv_loaded": _kv is not None,
        "kv_init_error": _kv_init_error,
        "kb_size": len(_kv) if _kv is not None else 0,
        "encoder_dim": _kv.dim if _kv is not None else None,
        "first_facts": _kv.facts[:3] if _kv is not None else [],
    }
