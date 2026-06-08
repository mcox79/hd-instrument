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
    """Lazy-init substrate-KV with seeded facts. First call loads Pythia + encodes."""
    global _kv, _kv_init_error
    if _kv is not None:
        return _kv
    if _kv_init_error is not None:
        raise HTTPException(status_code=503, detail=f"substrate-KV init failed earlier: {_kv_init_error}")
    try:
        from backend.llm.pythia_client import get_client
        client = get_client()
        kv = SubstrateKV(encoder=client, dim=client.hidden_size)
        facts = load_seed_facts()
        logger.info("seeding substrate-KV with %d facts...", len(facts))
        kv.add_facts(facts)
        _kv = kv
        return _kv
    except Exception as e:
        _kv_init_error = f"{type(e).__name__}: {e}"
        logger.exception("substrate-KV init failed")
        raise HTTPException(status_code=503, detail=_kv_init_error)


def _build_prompt(question: str, facts: list[tuple]) -> str:
    """Build the Pythia prompt with substrate-retrieved context."""
    facts_block = "\n".join(f"- {f}" for f, _s in facts)
    return (
        "You are a helpful assistant. Use ONLY the substrate-provided facts below to answer.\n"
        "If the facts do not cover the question, say you do not know.\n\n"
        f"Substrate facts:\n{facts_block}\n\n"
        f"Question: {question}\nAnswer:"
    )


@router.post("/tier5a", response_model=Tier5aResponse)
async def query_tier5a(req: Tier5aRequest):
    """Tier 5a: substrate-KV + Pythia-1.4B end-to-end. Demo-mode aware."""
    from backend.admin import demo_mode
    demo_mode.note_query_activity()

    kv = _init_kv()
    from backend.llm.pythia_client import get_client
    client = get_client()

    t_total0 = time.perf_counter()

    # 1. Substrate retrieve
    t0 = time.perf_counter()
    retrieved = kv.retrieve(req.question, top_k=req.top_k)
    substrate_ms = (time.perf_counter() - t0) * 1000

    # 2. Build prompt + generate
    prompt = _build_prompt(req.question, retrieved)
    gen = client.generate(
        prompt,
        max_new_tokens=req.max_new_tokens,
        temperature=req.temperature,
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
