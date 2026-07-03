"""Verification: M1.8 ClarifyGate reproduces 3-outcome semantics + CG-anchored taus."""

from __future__ import annotations

import numpy as np
import pytest

from hdlab.clarify_gate import (
    CG_CLARIFY_FP_SMOKE_SEED7,
    CG_CLARIFY_RECALL_SMOKE_SEED7,
    CG_CLARIFY_TAU,
    CG_CM_SMOKE_SEED7,
    CG_REFUSE_TAU,
    ClarifyGate,
    GateOutcome,
    _run_all_selftests,
)


def test_run_all_selftests_pass() -> None:
    """All module selftests reproduce M1.8 v1 seed_7/13/19 CG (2026-07-02)."""
    result = _run_all_selftests()
    assert result["cg_clarify_tau"] == 0.35
    assert result["cg_refuse_tau"] == 0.55
    assert result["cg_clarify_recall_smoke_seed7"] == 0.75
    assert result["cg_clarify_fp_smoke_seed7"] == 0.0
    assert result["cg_cm_smoke_seed7"] == 0.875


def test_cg_anchored_taus() -> None:
    """CG-anchored thresholds match adaptive-calibration output for M1.6 v2 router."""
    assert CG_CLARIFY_TAU == 0.35
    assert CG_REFUSE_TAU == 0.55
    assert CG_CLARIFY_RECALL_SMOKE_SEED7 == 0.75
    assert CG_CLARIFY_FP_SMOKE_SEED7 == 0.0
    assert CG_CM_SMOKE_SEED7 == 0.875


def test_three_band_semantics() -> None:
    """Score < clarify_tau -> REFUSE; middle -> CLARIFY; >= refuse_tau -> ACCEPT."""
    gate = ClarifyGate()
    assert gate.evaluate(0.10) == GateOutcome.REFUSE
    assert gate.evaluate(0.45) == GateOutcome.CLARIFY
    assert gate.evaluate(0.80) == GateOutcome.ACCEPT


def test_boundary_semantics_inclusive_lower() -> None:
    """clarify_tau boundary is inclusive lower; refuse_tau boundary is inclusive upper."""
    gate = ClarifyGate()
    assert gate.evaluate(0.35) == GateOutcome.CLARIFY
    assert gate.evaluate(0.55) == GateOutcome.ACCEPT
    assert gate.evaluate(0.349999) == GateOutcome.REFUSE
    assert gate.evaluate(0.549999) == GateOutcome.CLARIFY


def test_threshold_ordering_enforced() -> None:
    """Constructor refuses clarify_tau >= refuse_tau."""
    with pytest.raises(ValueError):
        ClarifyGate(clarify_tau=0.7, refuse_tau=0.5)


def test_clarify_recall_reproduces_smoke_seed7() -> None:
    """Reproduce B_clarify_recall=0.75 on synthetic ambiguous distribution matching source cell.

    MEASURED@data/exp_stage3_m3_stack_5_primitive_clarify_v1_seed_7_smoke/metrics.json:
      B_clarify_recall=0.75, B_clarify_fp=0.00.
    """
    gate = ClarifyGate()
    rng = np.random.default_rng(7)
    # ambient means from cell line 208-211 (clear vs ambiguous per 4-class router).
    clear_means = [0.632, 0.759, 0.634, 0.630]
    amb_means = [0.476, 0.763, 0.457, 0.387]
    n = 5
    clear = np.clip(np.concatenate([rng.normal(m, 0.05, n) for m in clear_means]), 0.0, 1.0)
    amb = np.clip(np.concatenate([rng.normal(m, 0.05, n) for m in amb_means]), 0.0, 1.0)
    recall = gate.clarify_recall(amb)
    fp = gate.clarify_precision_fp(clear)
    assert abs(recall - 0.75) < 0.10
    assert fp <= 0.15


def test_batch_matches_scalar() -> None:
    """Vectorized evaluate_batch matches scalar evaluate elementwise."""
    gate = ClarifyGate()
    scores = [0.1, 0.35, 0.44, 0.55, 0.9]
    batch = list(gate.evaluate_batch(scores))
    scalar = [gate.evaluate(s).value for s in scores]
    assert batch == scalar


def test_calibrate_returns_valid_gate() -> None:
    """calibrate() returns gate with valid threshold ordering."""
    rng = np.random.default_rng(11)
    clear = rng.normal(0.70, 0.05, 50)
    ambiguous = rng.normal(0.40, 0.05, 50)
    gate = ClarifyGate.calibrate(clear, ambiguous)
    assert 0.0 <= gate.clarify_tau < gate.refuse_tau <= 1.0
