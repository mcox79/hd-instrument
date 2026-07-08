"""Verification: discrete-budget CLS consolidation reproduces the CHAIN_GRADE
integrate-new-knowledge-without-forgetting result, scaffold-free.

Promotes cert cell exp_cls_ca3complete_consolidation_v1 (commit 92e01cf3f;
math::CHAIN_GRADE_cls_ca3complete_consolidation_v1_INTEGRATE_NEW_KNOWLEDGE_WITHOUT
_FORGETTING) into hdlab.hippocampal_encoder.cls_discrete_budget_consolidate.

MAIN claim (CHAIN_GRADE): a DISCRETE offline phase with a FIXED per-cycle replay
budget migrates OLD fast-buffer traces to a slow store while NEW items are acquired.
Discriminator fires: the NAIVE no-consolidation control MUST forget OLD; the
positive control (CONSOLIDATE_FULL) retains OLD and acquires NEW.

CA3-completion (via the certified iterative_cleanup operator) is the MEASURED_MECHANISM
refinement only (small lift; not load-bearing) -- the NO_CLEANUP arm (discrete-budget
migration alone) already carries the bulk of the gap. Asserted below.

Numbers are numpy-deterministic (fully seeded). No tracing; pure numpy. Bands sit
below the measured small-regime values with margin (MEASURED@ this discriminator).
Full-regime anchor reproduces the certified magnitude
(MEASURED@data/exp_cls_ca3complete_consolidation_v1/metrics.json: FULL old=0.933,
NAIVE old=0.020, gap=0.913).
"""

from __future__ import annotations

from hdlab.hippocampal_encoder import (
    _cls_consolidation_discriminator,
    cls_discrete_budget_consolidate,
    run_all_selftests,
)

import numpy as np
import pytest


SEEDS = (7, 13, 19)


def test_discriminator_fires_naive_forgets_across_seeds() -> None:
    """NAIVE no-consolidation control forgets OLD (retention <= 0.20) at every seed."""
    for seed in SEEDS:
        r = _cls_consolidation_discriminator(seed)
        assert r["naive_old"] <= 0.20, (
            f"seed {seed}: discriminator did not fire, NAIVE retained OLD ({r})")


def test_consolidate_full_retains_old_and_acquires_new() -> None:
    """CONSOLIDATE_FULL (positive control) retains OLD and acquires NEW across seeds."""
    for seed in SEEDS:
        r = _cls_consolidation_discriminator(seed)
        assert r["full_old"] >= 0.70, f"seed {seed}: OLD not retained ({r})"
        assert r["full_new"] >= 0.70, f"seed {seed}: NEW not acquired ({r})"


def test_integrate_without_forgetting_gap_is_chain_grade() -> None:
    """The CG signal: FULL old-retention minus NAIVE old-retention gap is large."""
    gaps = [_cls_consolidation_discriminator(s)["gap_full_minus_naive_old"] for s in SEEDS]
    for seed, gap in zip(SEEDS, gaps):
        assert gap >= 0.40, f"seed {seed}: integrate-without-forgetting gap too small ({gap:.3f})"
    assert float(np.mean(gaps)) >= 0.60, f"mean gap below expectation: {gaps}"


def test_ca3_completion_is_mm_refinement_not_load_bearing() -> None:
    """CA3-completion is the MM refinement only: the discrete-budget migration alone
    (NO_CLEANUP arm) already carries the bulk of the gap vs NAIVE at every seed.
    """
    for seed in SEEDS:
        r = _cls_consolidation_discriminator(seed)
        assert r["nc_old"] - r["naive_old"] >= 0.40, (
            f"seed {seed}: discrete-budget migration alone should carry the CG gap ({r})")


def test_discrete_fixed_budget_respected() -> None:
    """The fixed per-phase replay budget is respected (discrete-budget gate)."""
    for seed in SEEDS:
        assert _cls_consolidation_discriminator(seed)["budget_respected"], (
            f"seed {seed}: discrete budget not respected")


def test_budget_gate_caps_replayed_items() -> None:
    """cls_discrete_budget_consolidate replays at most `budget` items regardless of m."""
    d, v = 64, 16
    g = np.random.default_rng(3)
    fast = g.standard_normal((d, d)).astype(np.float32)
    slow = np.zeros((d, d), dtype=np.float32)
    cb = g.standard_normal((v, d)).astype(np.float32)
    keys = g.standard_normal((40, d)).astype(np.float32)  # 40 eligible items
    res = cls_discrete_budget_consolidate(fast, keys, cb, slow, budget=10, seed=1)
    assert res["n_replayed"] == 10, f"budget gate not enforced: {res}"
    assert res["budget_respected"] is True
    # fewer eligible than budget -> replays all eligible, still respected
    res2 = cls_discrete_budget_consolidate(fast, keys[:5], cb, slow, budget=10, seed=1)
    assert res2["n_replayed"] == 5 and res2["budget_respected"] is True


def test_full_regime_anchor_reproduces_certified_magnitude() -> None:
    """Full certified regime (D=1024, T=600, E=12) reproduces CG magnitude on seed 7.

    Cert MEASURED@data/exp_cls_ca3complete_consolidation_v1/metrics.json:
    FULL old=0.933, NAIVE old=0.020, gap=0.913 (3-seed mean). Single seed here.
    """
    r = _cls_consolidation_discriminator(7, d=1024, t_stream=600, n_epoch=12,
                                         decay=0.94, v=64, budget=50)
    assert r["naive_old"] <= 0.10, f"NAIVE should catastrophically forget at full regime ({r})"
    assert r["full_old"] >= 0.90, f"FULL should strongly retain at full regime ({r})"
    assert r["gap_full_minus_naive_old"] >= 0.85, f"gap below certified magnitude ({r})"


def test_slow_store_mutated_in_place_and_returned() -> None:
    """Slow store is accumulated in place and returned (continual.replay_cycle convention)."""
    d, v = 32, 8
    g = np.random.default_rng(5)
    fast = g.standard_normal((d, d)).astype(np.float32)
    slow = np.zeros((d, d), dtype=np.float32)
    cb = g.standard_normal((v, d)).astype(np.float32)
    keys = g.standard_normal((6, d)).astype(np.float32)
    out = cls_discrete_budget_consolidate(fast, keys, cb, slow, budget=6, seed=2)
    assert out["slow_store"] is slow, "slow_store must be mutated in place and returned"
    assert np.any(slow != 0.0), "slow store should have accumulated a write"


def test_module_selftests_still_green() -> None:
    """All hippocampal_encoder module selftests (existing + new) still pass -> no regression."""
    assert run_all_selftests() == 0
