"""
PP-225 linear projection head: substrate retrieval -> LLM logit injection.

Per Exp-Dev PP225_CHECKPOINT_REPLY 2026-06-09:

Config (v2.0 demo):
  LLM: Pythia-1.4B fp32 projection (bf16 head HARD_FAILs above 160M; fp32 REQUIRED)
  Anchor: exp_t5c_pp225_pythia14b_fp32proj_v1 (cycle 207 HARD_PASS)
  Head shape: W = (vocab=50304 for Pythia, 1024 bge-large dim) + scalar scale
  Recipe: gate-lr 1e-3 / main-lr 3e-4 + wd 0.01 / warmup 500 + cosine
  Encoder: frozen BAAI/bge-large-en-v1.5; CLS/pooler pooling (bidirectional encoder;
           do NOT last-token-pool which is only for causal LMs)

Usage:
    ckpt = load_pp225_head("data/pp225_export/head_pythia14b_fp32.pt")
    # OR for plumbing test:
    ckpt = get_random_init_head(vocab_size=50304, bge_dim=1024)

    new_logits = pp225_logit_inject(retrieved_fact_emb, query_logits, ckpt)
    # argmax over new_logits = fact-injected next token
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import torch

logger = logging.getLogger(__name__)


def pp225_logit_inject(
    retrieved_fact_emb: np.ndarray,
    query_logits: torch.Tensor,
    ckpt: dict,
) -> torch.Tensor:
    """Inject a retrieved-fact embedding into the LLM's next-token logits.

    retrieved_fact_emb: (bge_dim,) L2-normalized bge-large(fact) embedding
    query_logits: (vocab,) base LLM logits at this generation step
    ckpt: {"W": fp32 (vocab, bge_dim), "scale": float}

    Returns (vocab,) logits with the fact's projection added; argmax = next token.

    From Exp-Dev PP225_CHECKPOINT_REPLY 2026-06-09:
        e = torch.as_tensor(retrieved_fact_emb, dtype=torch.float32)
        add = ckpt["scale"] * (e @ ckpt["W"].t())   # (vocab,)
        return query_logits.float() + add           # argmax over this = injected next token
    """
    e = torch.as_tensor(retrieved_fact_emb, dtype=torch.float32)
    add = ckpt["scale"] * (e @ ckpt["W"].t())  # (vocab,)
    return query_logits.float() + add


def get_random_init_head(vocab_size: int = 50304, bge_dim: int = 1024,
                         seed: int = 42) -> dict:
    """Build a random-init PP-225 head for plumbing-test purposes only.

    Per Exp-Dev: 'If you want to start wiring NOW: use the snippet + a randomly-init
    head to validate the plumbing, then swap in the real .pt when it lands.'

    A randomly-init head DOES NOT have heldout=1.000 fact recall; it's only useful
    for verifying that the inject -> argmax pipeline runs end-to-end without errors.
    """
    g = torch.Generator().manual_seed(seed)
    return {
        "W": torch.randn(vocab_size, bge_dim, generator=g) / np.sqrt(bge_dim),
        "scale": 1.0,
        "_random_init": True,  # marker so callers know recall != 1.0 here
    }


def load_pp225_head(checkpoint_path: Path) -> dict:
    """Load the trained PP-225 head from Exp-Dev's GPU export cell.

    Expected file structure: torch.save({"W": fp32 (vocab, bge_dim), "scale": float}, path)
    """
    checkpoint_path = Path(checkpoint_path)
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"PP-225 head not found at {checkpoint_path}. Either await the GPU "
            "export cell (t5c_pp225_export_ckpt; ~30-60 min) OR use "
            "get_random_init_head() for a plumbing-test fallback."
        )
    ckpt = torch.load(checkpoint_path, map_location="cpu")
    if "W" not in ckpt or "scale" not in ckpt:
        raise ValueError(f"PP-225 head at {checkpoint_path} missing 'W' or 'scale'")
    if ckpt["W"].dtype != torch.float32:
        logger.warning("PP-225 head W is %s; casting to fp32 per Exp-Dev recipe "
                       "(bf16 hard-fails above 160M)", ckpt["W"].dtype)
        ckpt["W"] = ckpt["W"].float()
    ckpt["_random_init"] = False
    return ckpt


# ============================================================
# Module-level cache (single head per process)
# ============================================================

_HEAD: Optional[dict] = None
_HEAD_SOURCE: Optional[str] = None


def get_head(
    checkpoint_path: Path = Path("data/pp225_export/head_pythia14b_fp32.pt"),
    vocab_size: int = 50304,
    bge_dim: int = 1024,
) -> dict:
    """Return the active PP-225 head, loading from disk if available else random-init.

    First call performs the load + caches; subsequent calls return the cached head.
    """
    global _HEAD, _HEAD_SOURCE
    if _HEAD is not None:
        return _HEAD

    if Path(checkpoint_path).exists():
        try:
            _HEAD = load_pp225_head(checkpoint_path)
            _HEAD_SOURCE = f"checkpoint:{checkpoint_path}"
            logger.info("loaded PP-225 head from %s (W shape=%s; scale=%s)",
                        checkpoint_path, tuple(_HEAD["W"].shape), _HEAD["scale"])
            return _HEAD
        except Exception:
            logger.exception("failed to load PP-225 head from %s; falling back to random-init",
                             checkpoint_path)

    _HEAD = get_random_init_head(vocab_size=vocab_size, bge_dim=bge_dim)
    _HEAD_SOURCE = "random_init"
    logger.warning("PP-225 head: using random-init fallback (vocab=%d bge_dim=%d). "
                   "Plumbing-test only. Heldout fact recall != 1.0 until real "
                   "checkpoint replaces this.", vocab_size, bge_dim)
    return _HEAD


def head_source() -> str:
    """Return 'checkpoint:<path>' or 'random_init' indicating which head is loaded."""
    return _HEAD_SOURCE or "unloaded"
