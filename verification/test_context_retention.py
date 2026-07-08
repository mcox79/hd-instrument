"""Verification: M1.5 TwoTierContext reproduces Atom 18 CG-anchored numbers."""

from __future__ import annotations

import pytest
import torch

from hdlab.context_retention import (
    AMIT_GUTFREUND_ALPHA_WALL,
    COARSE_PROJ_DIM_DEFAULT,
    K_PER_BANK_TARGET_DEFAULT,
    LTM_ALPHA_CG_ANCHOR,
    TwoTierContext,
    _bipolar_random,
    _coarse_to_fine_discriminator,
    _run_all_selftests,
    coarse_to_fine_read_cost_ratio,
)
from verification.theory import selective_depth_read_cost_ratio


def test_run_all_selftests_pass() -> None:
    """All module selftests reproduce Atom 18 v2 seed_7/13/19 CG (2026-07-01)."""
    result = _run_all_selftests()
    assert result["ltm_alpha_cg_anchor"] == pytest.approx(1200 / 8192)
    assert result["amit_gutfreund_wall"] == 0.138
    assert result["k_per_bank_target"] == 64


def test_ltm_alpha_above_amit_gutfreund_wall() -> None:
    """CG anchor LTM alpha (1200/8192=0.1465) sits above 0.138 dense-Hopfield wall."""
    assert LTM_ALPHA_CG_ANCHOR > AMIT_GUTFREUND_ALPHA_WALL
    assert LTM_ALPHA_CG_ANCHOR == pytest.approx(0.14648, abs=1e-4)


def test_k_per_bank_default_matches_working_memory_cg() -> None:
    """Default per-bank target of 64 matches multi-bank WM chain-grade envelope."""
    assert K_PER_BANK_TARGET_DEFAULT == 64


def test_reject_n_dim_below_cg_threshold() -> None:
    """Constructor refuses n_dim below THRESHOLD_ANCHORED_AT_N_DIM=8192."""
    with pytest.raises(ValueError):
        TwoTierContext(n_dim=4096, stm_k=100, ltm_k=1200)


def test_reject_ltm_alpha_below_wall() -> None:
    """Constructor refuses ltm_k such that alpha < Amit-Gutfreund 0.138."""
    with pytest.raises(ValueError):
        TwoTierContext(n_dim=8192, stm_k=100, ltm_k=100)


def test_two_tier_read_reproduces_k100_at_load50() -> None:
    """Reproduce Atom 18 v2 K100@load50 CG: STM-path exact-query recovers val identity.

    MEASURED@data/exp_cortex_context_retention_v2_seed_7_smoke/metrics.json
    verdict_msg 'K100@load50=1.000'. Reproduces single-trial variant of 8-trial CG.
    """
    ctx = TwoTierContext(n_dim=8192, stm_k=100, ltm_k=1200, v_cb=1024, seed=7)
    gen = torch.Generator().manual_seed(29)
    role_key_target = _bipolar_random((8192,), gen)
    val_idx_target = int(torch.randint(0, 1024, (1,), generator=gen).item())
    ctx.write(role_key_target, val_idx_target)
    for _ in range(50):
        rk = _bipolar_random((8192,), gen)
        vi = int(torch.randint(0, 1024, (1,), generator=gen).item())
        ctx.write(rk, vi)
    pred = ctx.read(role_key_target, target_cos_noise=1.0)
    assert pred == val_idx_target


def test_value_codebook_shape_and_bipolar() -> None:
    """value_codebook() returns (V_CB, N_DIM) bipolar tensor."""
    ctx = TwoTierContext(n_dim=8192, stm_k=100, ltm_k=1200, v_cb=1024, seed=3)
    cb = ctx.value_codebook()
    assert cb.shape == (1024, 8192)
    assert set(cb.unique().tolist()) <= {-1.0, 1.0}


# ----- Energy-scaled selective-depth read (retained-trace re-query, 2026-07-08) -----
# Scaffold-free witnesses: the retained DENSE trace recovers fine fidelity to the
# full-read ceiling at lower analytical coarse cost, where a sparse (destroyed) trace
# CANNOT. Promotes cert cell exp_encoder_retained_trace_requery_coarse_to_fine_v1
# (commit 5d711c2e5) into hdlab.context_retention. All tests pass with tracing=False.


def test_coarse_to_fine_discriminator_fires_across_seeds() -> None:
    """Retained-dense coarse->fine RECOVERS to ceiling; sparse-destroyed trace FAILS.

    Reproduces the mechanism-A discriminator: keys share a strong common component so
    WTA-sparsifying the coarse code discards the discriminating fine detail. The dense
    trace is what recovers (sparse path is the confirmed negative).
    """
    for seed in (7, 13, 19):
        r = _coarse_to_fine_discriminator(seed)
        assert r["full_fine"] >= 0.90, f"seed {seed}: ceiling not high ({r})"
        assert r["retained_dense_c2f"] >= 0.90, f"seed {seed}: dense c2f did not recover ({r})"
        assert r["retained_dense_c2f"] >= r["full_fine"] - 0.05, f"seed {seed}: below ceiling ({r})"
        assert r["sparse_destroyed"] <= 0.70, f"seed {seed}: sparse did not fail ({r})"
        assert r["retained_dense_c2f"] - r["sparse_destroyed"] >= 0.20, f"seed {seed}: no gap ({r})"
        assert r["shortlist_hit"] >= 0.65, f"seed {seed}: shortlist misses answer ({r})"
        assert r["cost_ratio"] <= 0.50, f"seed {seed}: coarse cost not below half ({r})"


def test_coarse_to_fine_sparse_trace_is_the_confirmed_negative() -> None:
    """The DENSE trace is load-bearing: at matched shortlist geometry, sparse strictly loses."""
    r = _coarse_to_fine_discriminator(7)
    assert r["retained_dense_c2f"] > r["sparse_destroyed"]


def test_coarse_to_fine_cost_ratio_matches_theory_oracle() -> None:
    """Module analytical cost ratio equals the independent closed-form oracle (flop model)."""
    for m, n, dc, k in [(200, 1024, 128, 20), (1200, 8192, 128, 120), (50, 4096, 64, 5)]:
        assert coarse_to_fine_read_cost_ratio(m, n, dc, k) == pytest.approx(
            selective_depth_read_cost_ratio(m, n, dc, k))
        # sanity: full shortlist over the whole tape is never cheaper than ~D_COARSE/N + 1.
        assert coarse_to_fine_read_cost_ratio(m, n, dc, m) == pytest.approx(dc / n + 1.0)


def test_read_coarse_to_fine_matches_default_read_when_shortlist_covers_tape() -> None:
    """read_coarse_to_fine falls back to the exact default read() when k_shortlist >= LTM size.

    Also confirms the default read() path is unchanged (same object, same result).
    """
    ctx = TwoTierContext(n_dim=8192, stm_k=4, ltm_k=1200, v_cb=1024, seed=11)
    gen = torch.Generator().manual_seed(41)
    targets = []
    for _ in range(20):  # overflow STM (k=4) -> populate LTM tape
        rk = _bipolar_random((8192,), gen)
        vi = int(torch.randint(0, 1024, (1,), generator=gen).item())
        ctx.write(rk, vi)
        targets.append((rk, vi))
    probe_rk, _ = targets[0]
    default = ctx.read(probe_rk, target_cos_noise=1.0)
    # k_shortlist covering the whole LTM tape -> identical LTM read as default.
    covered = ctx.read_coarse_to_fine(probe_rk, k_shortlist=10_000)
    assert covered == default


def test_read_coarse_to_fine_default_read_still_reproduces_k100_at_load50() -> None:
    """Adding the new read mode does not perturb the CG-anchored default read() behavior."""
    ctx = TwoTierContext(n_dim=8192, stm_k=100, ltm_k=1200, v_cb=1024, seed=7)
    gen = torch.Generator().manual_seed(29)
    role_key_target = _bipolar_random((8192,), gen)
    val_idx_target = int(torch.randint(0, 1024, (1,), generator=gen).item())
    ctx.write(role_key_target, val_idx_target)
    for _ in range(50):
        rk = _bipolar_random((8192,), gen)
        vi = int(torch.randint(0, 1024, (1,), generator=gen).item())
        ctx.write(rk, vi)
    assert ctx.read(role_key_target, target_cos_noise=1.0) == val_idx_target


def test_coarse_proj_dim_default_exposed() -> None:
    """D_COARSE default is exported for callers dialing the energy/resolution knob."""
    assert COARSE_PROJ_DIM_DEFAULT == 128
