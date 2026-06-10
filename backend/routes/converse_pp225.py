"""
PP-225 substrate-projection demo endpoint.

Per Exp-Dev PP225_CHECKPOINT_REPLY 2026-06-09: substrate retrieves a fact, bge-large
encodes it (CLS pool; L2-normalized), and the trained linear projection head adds
that fact's contribution to the LLM's next-token logits. argmax(injected logits) =
fact-grounded next token; the substrate IS the LLM's knowledge.

This endpoint exposes the PP-225 plumbing for empirical inspection:
  - Top-K substrate retrieval given a query
  - bge-large encoding of the top-1 retrieved fact
  - Random-init or trained head injection
  - Top-N predicted next tokens after injection (vs the base LLM's argmax)

For plumbing-test mode (no Pythia loaded): we use zero-logits as the LLM base, so
the injected argmax is the head's pure projection. Useful for verifying the math.

For full demo: when Pythia-1.4B fp32 is loaded, we use its actual logits for the
query prompt and inject the fact's projection per generation step.
"""
from __future__ import annotations
import logging
import time
from typing import Optional

import numpy as np
import torch
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.llm.pp225 import get_head, head_source, pp225_logit_inject

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# Tokenizer (Pythia vocabulary needed to decode injected argmax)
# ============================================================

_TOKENIZER = None


def _get_tokenizer():
    """Lazy-load Pythia's tokenizer (small; cheap; no model weights yet)."""
    global _TOKENIZER
    if _TOKENIZER is not None:
        return _TOKENIZER
    try:
        from transformers import AutoTokenizer
        _TOKENIZER = AutoTokenizer.from_pretrained("EleutherAI/pythia-1.4b")
        logger.info("loaded Pythia-1.4b tokenizer (vocab=%d)", _TOKENIZER.vocab_size)
    except Exception:
        logger.exception("failed to load Pythia tokenizer")
        _TOKENIZER = None
    return _TOKENIZER


# ============================================================
# Request / response schemas
# ============================================================

class PP225Request(BaseModel):
    message: str
    top_k_facts: int = 3       # substrate retrieve top-K
    top_n_tokens: int = 5      # show top-N predicted next tokens


class PP225Response(BaseModel):
    query: str
    retrieved_facts: list      # [{text, score}]
    top_fact_text: Optional[str]
    head_source: str           # 'checkpoint:...' or 'random_init'
    top_n_next_tokens: list    # [{token, score}]
    latency_ms: float
    notes: str


# ============================================================
# Endpoint
# ============================================================

@router.post("/converse/pp225", response_model=PP225Response)
async def converse_pp225(req: PP225Request):
    """PP-225 substrate-projection demo: substrate retrieves a fact, the PP-225 head
    injects it into next-token logits, top-N tokens shown."""
    t0 = time.perf_counter()

    # Lazy import to avoid circular dep
    from backend.routes.query_tier5a import _init_kv
    from backend.llm.bge_encoder import get_encoder
    try:
        kv = _init_kv()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"substrate-KV not loaded: {e}")

    # Retrieve top-K facts
    retrieved = kv.retrieve(req.message, top_k=req.top_k_facts)
    if not retrieved:
        return PP225Response(
            query=req.message,
            retrieved_facts=[],
            top_fact_text=None,
            head_source=head_source(),
            top_n_next_tokens=[],
            latency_ms=(time.perf_counter() - t0) * 1000,
            notes="no facts retrieved; substrate KB may be empty",
        )

    # Top-1 fact -> bge encode (the encoder is the same one used at ingest;
    # SentenceTransformer wraps BAAI/bge-large-en-v1.5 which uses CLS pooling
    # by default per the model card, matching Exp-Dev's recipe)
    top_fact_text = retrieved[0][0]
    encoder = get_encoder()
    fact_vec = encoder.encode([top_fact_text])[0]   # (1024,) L2-normalized
    fact_emb = np.asarray(fact_vec, dtype=np.float32)

    # Load PP-225 head (cached on first call; random-init fallback if no checkpoint)
    tok = _get_tokenizer()
    # Tokenizer reports vocab_size (50254 for Pythia), but the trained head W is
    # sized to the model's PADDED output dim (50304). Use the head's authoritative
    # shape for base_logits + topk to avoid shape mismatch.
    fallback_vocab = tok.vocab_size if tok is not None else 50304
    ckpt = get_head(vocab_size=fallback_vocab, bge_dim=fact_emb.shape[0])
    vocab_size = int(ckpt["W"].shape[0])

    # For plumbing test: use zero base logits. argmax(injected) = head's pure
    # projection of the fact embedding into vocab space.
    # When Pythia-1.4B is loaded, replace with actual model logits.
    base_logits = torch.zeros(vocab_size, dtype=torch.float32)
    injected = pp225_logit_inject(fact_emb, base_logits, ckpt)

    # Top-N next tokens by injected logit
    top_n = min(req.top_n_tokens, vocab_size)
    top_vals, top_ids = torch.topk(injected, top_n)
    top_tokens = []
    for i in range(top_n):
        tid = int(top_ids[i].item())
        tok_str = tok.decode([tid]) if tok is not None else f"<id={tid}>"
        top_tokens.append({
            "token": tok_str,
            "token_id": tid,
            "logit": round(float(top_vals[i].item()), 4),
        })

    notes_lines = []
    notes_lines.append(f"top-{req.top_k_facts} substrate retrieve cosine = {[round(r[1], 3) for r in retrieved]}")
    notes_lines.append(f"head source: {head_source()}")
    if ckpt.get("_random_init"):
        notes_lines.append(
            "head is RANDOM-INIT; argmax is plumbing-only (no heldout fact recall). "
            "Real checkpoint lands at data/pp225_export/head_pythia14b_fp32.pt"
        )
    notes_lines.append("base logits = zeros (no Pythia loaded yet); argmax = head's pure projection of the fact")

    return PP225Response(
        query=req.message,
        retrieved_facts=[{"text": t, "score": round(s, 4)} for t, s in retrieved],
        top_fact_text=top_fact_text,
        head_source=head_source(),
        top_n_next_tokens=top_tokens,
        latency_ms=round((time.perf_counter() - t0) * 1000, 2),
        notes="; ".join(notes_lines),
    )
