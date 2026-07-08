"""Scaffold-free witness for compose-frequency routing in hdlab.compose_freq_routing.

Reproduces the CG-certified phenomenon in miniature: a next-item associator over frequency-
imbalanced, function-word-structured composition (high-frequency targets have high in-degree --
they are successors of many contexts). A single shared cf-RPE kernel is dominated by the high-
in-degree high-frequency targets and starves rare-target predictions; splitting into two
frequency-gated kernels with a routed readout (compose-frequency routing) recovers rare targets
and lowers next-item BPC. The discriminator fires against BOTH compose-frequency-ignoring controls:
the raw-Hebbian baseline (the certified cell's baseline arm) and, more tightly, a single-kernel
delta-rule that shares the exact iterative training but ignores frequency class.

Telemetry-sensitivity (not by-construction): the routing-specific advantage (routed vs single-
delta) is large only when the frequency-in-degree asymmetry is present; with a symmetric in-degree
corpus it collapses, matching the closed-form crosstalk oracle (advantage requires context
correlation and frequency-dominated gradient). Also checks the delta-contraction and single-kernel
crosstalk oracles (verification.theory) and a routed-readout reference equivalence.

Passes with tracing=False (torch-only; no substrate tracing state involved).

Certified source: substrate_compose_freq_routing v5 DEFINITIVE (5-seed cross-N
HARD_PASS_CHAIN_GRADE_DEFINITIVE 2026-06-25; math atom EXP_substrate_compose_freq_routing_v5_DEFINITIVE).
"""
from __future__ import annotations

import math

import numpy as np
import pytest
import torch

from hdlab.compose_freq_routing import (
    composition_frequency_ranks,
    high_frequency_mask,
    build_hebbian_kernel,
    build_single_kernel,
    build_freq_routed_kernels,
    single_kernel_logits,
    routed_logits,
)
from verification import theory


def _l2n(x, eps=1e-12):
    return x / (x.norm(dim=1, keepdim=True) + eps)


def _sparsify_bipolar(E, f):
    V, d = E.shape
    k = max(1, int(round(f * d)))
    _, idx = torch.topk(E.abs(), k=k, dim=1)
    out = torch.zeros_like(E)
    rows = torch.arange(V).unsqueeze(1).expand(-1, k)
    s = torch.sign(E.gather(1, idx))
    s = torch.where(s == 0, torch.ones_like(s), s)
    out[rows, idx] = s
    return out


def _bpc(logits, tgt):
    lp = torch.log_softmax(logits.double(), dim=1)
    return float(-lp[torch.arange(len(tgt)), tgt].mean() / math.log(2.0))


def _build_freq_indegree_corpus(seed, V, n_dim, n_high, hi_indeg, rare_indeg,
                                f=0.08, n_pairs=8000):
    """Frequency-imbalanced composition: high-freq targets have in-degree hi_indeg, rare rare_indeg."""
    gnp = np.random.default_rng(seed)
    E = _l2n(_sparsify_bipolar(
        _l2n(torch.from_numpy(gnp.standard_normal((V, n_dim)).astype(np.float32))), f))
    edges_ctx, edges_tgt = [], []
    for t in range(V):
        indeg = hi_indeg if t < n_high else rare_indeg
        for c in gnp.choice(V, size=indeg, replace=False):
            edges_ctx.append(int(c))
            edges_tgt.append(t)
    edges_ctx = np.array(edges_ctx, dtype=np.int64)
    edges_tgt = np.array(edges_tgt, dtype=np.int64)
    sel = gnp.integers(0, len(edges_ctx), size=n_pairs)
    ctx_idx = torch.from_numpy(edges_ctx[sel])
    tgt_idx = torch.from_numpy(edges_tgt[sel])
    ranks = composition_frequency_ranks(tgt_idx, n_items=V)
    hmask = high_frequency_mask(ranks, threshold=n_high)
    ev_ctx = torch.from_numpy(edges_ctx)
    ev_tgt = torch.from_numpy(edges_tgt)
    is_hi_ev = edges_tgt < n_high
    return E, ctx_idx, tgt_idx, hmask, ev_ctx, ev_tgt, is_hi_ev


def _run_arms(E, ctx_idx, tgt_idx, hmask, ev_ctx, seed, n_steps=1400,
              batch=64, lr=0.5, lr_rare=0.2, stdp_w=0.5):
    g1 = torch.Generator().manual_seed(seed * 101 + 7)
    g2 = torch.Generator().manual_seed(seed * 101 + 7)
    W_heb = build_hebbian_kernel(E, ctx_idx, tgt_idx)
    W_single = build_single_kernel(E, ctx_idx, tgt_idx, n_steps, batch, lr, generator=g1)
    W_freq, W_rare = build_freq_routed_kernels(
        E, ctx_idx, tgt_idx, hmask, n_steps, batch, lr, lr_rare, stdp_w, generator=g2)
    l_heb = single_kernel_logits(E, ev_ctx, W_heb)
    l_single = single_kernel_logits(E, ev_ctx, W_single)
    l_routed = routed_logits(E, ev_ctx, W_freq, W_rare, hmask)
    return l_heb, l_single, l_routed


def test_routing_beats_both_controls_under_frequency_indegree_asymmetry() -> None:
    """Discriminator fires: routed beats single-delta AND raw-Hebbian; rare-target recall lifts."""
    for seed in (7, 13):
        E, ci, ti, hm, ec, et, is_hi = _build_freq_indegree_corpus(
            seed, V=200, n_dim=128, n_high=15, hi_indeg=40, rare_indeg=1)
        l_heb, l_single, l_routed = _run_arms(E, ci, ti, hm, ec, seed)
        bpc_heb, bpc_single, bpc_routed = _bpc(l_heb, et), _bpc(l_single, et), _bpc(l_routed, et)
        # routed beats the tight compose-freq-ignoring control (single-kernel delta-rule)
        assert bpc_single - bpc_routed > 0.05, (
            f"seed {seed}: routing did not beat single-delta "
            f"(single={bpc_single:.4f} routed={bpc_routed:.4f})")
        # routed beats the certified cell's baseline (raw Hebbian)
        assert bpc_heb - bpc_routed > 0.12, (
            f"seed {seed}: routing did not beat Hebbian "
            f"(heb={bpc_heb:.4f} routed={bpc_routed:.4f})")
        # mechanism telemetry: routing lifts rare-target recall
        pred_single = l_single.argmax(1).numpy()
        pred_routed = l_routed.argmax(1).numpy()
        etn = et.numpy()
        rare_single = float((pred_single[~is_hi] == etn[~is_hi]).mean())
        rare_routed = float((pred_routed[~is_hi] == etn[~is_hi]).mean())
        assert rare_routed - rare_single > 0.08, (
            f"seed {seed}: rare-target recall did not lift "
            f"(single={rare_single:.3f} routed={rare_routed:.3f})")


def test_routing_advantage_collapses_without_indegree_asymmetry() -> None:
    """Telemetry-sensitive: with symmetric in-degree the routing-specific advantage largely vanishes."""
    seed = 7
    E, ci, ti, hm, ec, et, _ = _build_freq_indegree_corpus(
        seed, V=200, n_dim=128, n_high=15, hi_indeg=8, rare_indeg=8)
    _, l_single, l_routed = _run_arms(E, ci, ti, hm, ec, seed)
    routing_gain_symmetric = _bpc(l_single, et) - _bpc(l_routed, et)
    # asymmetric reference from the same builder
    E2, ci2, ti2, hm2, ec2, et2, _ = _build_freq_indegree_corpus(
        seed, V=200, n_dim=128, n_high=15, hi_indeg=40, rare_indeg=1)
    _, ls2, lr2 = _run_arms(E2, ci2, ti2, hm2, ec2, seed)
    routing_gain_asymmetric = _bpc(ls2, et2) - _bpc(lr2, et2)
    assert routing_gain_symmetric < 0.06, (
        f"symmetric routing gain should be small; got {routing_gain_symmetric:.4f}")
    assert routing_gain_asymmetric > 2.0 * routing_gain_symmetric, (
        f"advantage should scale with in-degree asymmetry: "
        f"asym={routing_gain_asymmetric:.4f} sym={routing_gain_symmetric:.4f}")


def test_delta_rule_contraction_matches_theory() -> None:
    """One cf-RPE update on a unit-norm context contracts the residual by theory (1 - lr)."""
    gen = torch.Generator().manual_seed(11)
    n_dim = 128
    ctx = _l2n(torch.randn(1, n_dim, generator=gen))
    tgt = _l2n(torch.randn(1, n_dim, generator=gen))
    for lr in (0.3, 0.5, 0.9):
        W = torch.zeros((n_dim, n_dim))
        err0 = float((tgt - ctx @ W.T).norm())
        W = W + lr * ((tgt - ctx @ W.T).T @ ctx)
        err1 = float((tgt - ctx @ W.T).norm())
        assert err1 == pytest.approx(theory.compose_freq_delta_touch_contraction(lr) * err0, abs=1e-4)


def test_single_kernel_crosstalk_matches_oracle() -> None:
    """One high-freq update perturbs a correlated rare prediction by ~lr*rho; routing sets it to 0."""
    n_dim = 256
    gen = torch.Generator().manual_seed(3)
    c_high = _l2n(torch.randn(1, n_dim, generator=gen))[0]
    c_rare = _l2n((0.4 * c_high + 0.6 * _l2n(torch.randn(1, n_dim, generator=gen))[0]).unsqueeze(0))[0]
    t_high = _l2n(torch.randn(1, n_dim, generator=gen))[0]
    lr = 0.5
    W = torch.zeros((n_dim, n_dim))
    before = W @ c_rare
    W = W + lr * torch.outer(t_high - W @ c_high, c_high)
    actual = float((W @ c_rare - before).norm())
    rho = float(c_high @ c_rare)
    assert actual == pytest.approx(theory.compose_freq_single_kernel_crosstalk(rho, lr), abs=1e-3)
    # routing removes the cross-talk entirely (dedicated kernel never sees the high-freq update)
    assert theory.compose_freq_single_kernel_crosstalk(0.0, lr) == 0.0


def test_routed_readout_reference_equivalence() -> None:
    """routed_logits equals an explicit per-candidate manual routing of the two kernels' logits."""
    gen = torch.Generator().manual_seed(1)
    V, n_dim = 20, 64
    E = _l2n(torch.randn(V, n_dim, generator=gen))
    ctx_idx = torch.arange(V, dtype=torch.long)
    W_freq = torch.randn(n_dim, n_dim, generator=gen)
    W_rare = torch.randn(n_dim, n_dim, generator=gen)
    hmask = torch.zeros(V, dtype=torch.bool)
    hmask[:6] = True
    fast = routed_logits(E, ctx_idx, W_freq, W_rare, hmask)
    lf = _l2n(E[ctx_idx] @ W_freq.T) @ E.T
    lr_ = _l2n(E[ctx_idx] @ W_rare.T) @ E.T
    slow = torch.where(hmask.unsqueeze(0), lf, lr_)
    assert torch.allclose(fast, slow, atol=1e-5)


def test_input_validation() -> None:
    """Bad shapes / mismatched pair lengths / wrong mask length raise ValueError (no silent misuse)."""
    E = torch.randn(10, 16)
    with pytest.raises(ValueError):
        composition_frequency_ranks(torch.randn(2, 3), n_items=5)  # not 1-D
    with pytest.raises(ValueError):
        high_frequency_mask(torch.arange(5), threshold=-1)
    with pytest.raises(ValueError):
        build_single_kernel(E, torch.arange(4), torch.arange(3), n_steps=1, batch=2, lr=0.5)  # length mismatch
    with pytest.raises(ValueError):
        routed_logits(E, torch.arange(4), torch.randn(16, 16), torch.randn(16, 16),
                      torch.zeros(3, dtype=torch.bool))  # mask length != n_items
