"""Standard metric suite: substrate health, composition fidelity, capacity, calibration."""

from __future__ import annotations

from collections.abc import Iterable

import torch

from .tracing import TraceEvent


def pairwise_similarity_stats(vectors: torch.Tensor) -> dict[str, float]:
    """Mean, std, max abs of off-diagonal pairwise similarities. Shape (k, n)."""
    k = vectors.shape[0]
    if k < 2:
        return {"mean": 0.0, "std": 0.0, "max_abs": 0.0}
    n = vectors.shape[-1]
    if vectors.is_complex():
        sims = (vectors @ vectors.conj().T).real / n
    else:
        norms = vectors.norm(dim=-1, keepdim=True)
        normed = vectors / torch.where(norms > 0, norms, torch.ones_like(norms))
        sims = normed @ normed.T
    mask = ~torch.eye(k, dtype=torch.bool)
    off_diag = sims[mask]
    return {
        "mean": float(off_diag.mean()),
        "std": float(off_diag.std()),
        "max_abs": float(off_diag.abs().max()),
    }


def capacity_curve(n: int, k_values: list[int], trials: int) -> dict[int, float]:
    """Recovery accuracy as a function of bundle size k. Implemented in Week 7."""
    raise NotImplementedError("Week 7")


def event_summary(events: Iterable[TraceEvent]) -> dict[str, float | int]:
    """High-level counts and timings over a sequence of events."""
    events = list(events)
    ops: dict[str, int] = {}
    total_ns = 0
    for e in events:
        ops[e.op] = ops.get(e.op, 0) + 1
        total_ns += e.elapsed_ns
    return {
        "total_events": len(events),
        "distinct_ops": len(ops),
        "total_wall_ns": total_ns,
        "total_wall_us": total_ns / 1000.0,
    }


def hebbian_final_weights(events: Iterable[TraceEvent]) -> dict[tuple[str, str], float]:
    """Reduce learning.update events to the final recorded weight per pair (canonical order)."""
    weights: dict[tuple[str, str], float] = {}
    for e in events:
        if e.op != "learning.update":
            continue
        a = e.inputs.get("a")
        b = e.inputs.get("b")
        if a is None or b is None:
            continue
        key = (a, b) if a <= b else (b, a)
        w = e.output.get("weight") if isinstance(e.output, dict) else None
        if w is not None:
            weights[key] = float(w)
    return weights


def cleanup_outcomes(events: Iterable[TraceEvent]) -> dict[str, int | float]:
    """Aggregate accept / reject counts across memory.lookup events."""
    accepted = 0
    rejected = 0
    score_sum = 0.0
    n = 0
    for e in events:
        if e.op != "memory.lookup":
            continue
        if not isinstance(e.output, dict):
            continue
        score = e.output.get("score", 0.0)
        score_sum += float(score)
        n += 1
        if e.output.get("name") is None:
            rejected += 1
        else:
            accepted += 1
    return {
        "lookups": n,
        "accepted": accepted,
        "rejected": rejected,
        "mean_score": (score_sum / n) if n else 0.0,
    }
