"""Semantic emit helpers for connection-layer events.

Layer 2 of the trace bus. Operator events (binding.bind, learning.update, ...) tell you
WHAT computation happened; semantic events tell you WHY in terms of the connection logic:
which entity was cleaned up to, which relation activated, which edge carried the load,
which modulator gated which op.

All helpers inherit the active query_id from tracing.query_span automatically.
"""

from __future__ import annotations

import time
from typing import Any

from . import tracing


def hop(hop_idx: int, **state: Any) -> None:
    """Mark a hop boundary inside a query span."""
    tracing.emit("semantic.hop", {"hop_idx": hop_idx, **state}, None)


def cleanup_hit(
    target_name: str | None,
    score: float,
    threshold: float,
    hop_idx: int | None = None,
    accepted: bool | None = None,
) -> None:
    """Record the result of a cleanup-against-codebook step."""
    t0 = time.perf_counter_ns()
    decided = bool(score >= threshold) if accepted is None else bool(accepted)
    tracing.emit(
        "semantic.cleanup_hit",
        {
            "target_name": target_name,
            "score": float(score),
            "threshold": float(threshold),
            "hop_idx": hop_idx,
        },
        {"accepted": decided},
        elapsed_ns=time.perf_counter_ns() - t0,
    )


def relation_activated(
    relation: str,
    contribution: float,
    hop_idx: int | None = None,
    n_edges_fired: int | None = None,
) -> None:
    """Record that a relation channel fired during a hop."""
    tracing.emit(
        "semantic.relation_activated",
        {
            "relation": relation,
            "contribution": float(contribution),
            "hop_idx": hop_idx,
            "n_edges_fired": n_edges_fired,
        },
        None,
    )


def edge_traversed(
    relation: str,
    src: str,
    dst: str,
    weight: float,
    hop_idx: int | None = None,
) -> None:
    """Record a single edge traversal during graph spread."""
    tracing.emit(
        "semantic.edge_traversed",
        {
            "relation": relation,
            "src": src,
            "dst": dst,
            "weight": float(weight),
            "hop_idx": hop_idx,
        },
        None,
    )


def modulator_gate(
    name: str,
    before: float,
    after: float,
    gated_op: str,
) -> None:
    """Record a modulator-driven gate decision: which op was changed and how."""
    tracing.emit(
        "semantic.modulator_gate",
        {
            "name": name,
            "before": float(before),
            "after": float(after),
            "gated_op": gated_op,
        },
        None,
    )


def ablation_active(target_kind: str, target_id: str) -> None:
    """Record that an ablation is in force for this scope."""
    tracing.emit(
        "semantic.ablation_active",
        {"target_kind": target_kind, "target_id": target_id},
        None,
    )


def query_answer(answer: Any, confidence: float, hops_taken: int) -> None:
    """Record the final answer of a query span (in addition to query_end)."""
    tracing.emit(
        "semantic.query_answer",
        {"hops_taken": int(hops_taken), "confidence": float(confidence)},
        {"answer": answer},
    )
