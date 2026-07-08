"""Scaffold-free witness for the peel/SIC bundle-set-recovery readout in hdlab.cleanup_family.

Reproduces the CG-certified phenomenon in miniature: flat top-J readout collapses under
high bundle load (cross-talk mis-ranks members) while confidence-ordered successive-
interference-cancellation (matching pursuit) recovers the member set. Also checks the
closed-form orthonormal oracle (exact recovery), an independent brute-force reference
(equivalence), input validation, and real (HRR) + complex (FHRR) codebooks.

Passes with tracing=False (numpy-only; no substrate tracing state involved).

Certified sources: exp_encoder_peel_sic_readout_realcodes_v1 (commit 916e6f7cb),
exp_bundling_slot_peel_sic_v1 (commit c2f65e53d).
"""
from __future__ import annotations

import numpy as np
import pytest

from hdlab.cleanup_family import (
    peel_sic_readout, flat_topk_readout, BUNDLE_READOUTS, _l2_normalize,
)
from verification import theory


def _real_codebook(m: int, d: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return _l2_normalize(rng.standard_normal((m, d)).astype(np.float32))


def _complex_codebook(m: int, d: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    ang = (rng.random((m, d)) * 2 - 1) * np.pi
    return np.exp(1j * ang).astype(np.complex64)


def _set_recall(pred_idx: np.ndarray, members: np.ndarray, j: int) -> float:
    return len(set(int(x) for x in pred_idx) & set(int(x) for x in members)) / j


def _reference_peel(bundle: np.ndarray, codebook: np.ndarray, j: int, mode: str) -> list:
    """Independent un-optimized brute-force matching pursuit (single vector). Oracle for equivalence."""
    resid = bundle.astype(codebook.dtype).copy()
    preds: list = []
    for _ in range(j):
        best_i, best_s = -1, -np.inf
        for i in range(codebook.shape[0]):
            if i in preds:
                continue
            s = float(np.real(np.vdot(codebook[i], resid)))  # Re(<c_i, resid>)
            if s > best_s:
                best_s, best_i = s, i
        preds.append(best_i)
        c = codebook[best_i]
        if mode == "unit":
            resid = resid - c
        else:
            coeff = np.vdot(c, resid) / (np.vdot(c, c) + 1e-12)
            resid = resid - coeff * c
    return preds


def test_orthonormal_exact_recovery_matches_oracle() -> None:
    """On an orthonormal codebook, peel/SIC recovers the member set exactly (recall == oracle 1.0)."""
    d, j = 64, 12
    cb = np.eye(d, dtype=np.float32)[: d]  # (d, d) orthonormal rows
    rng = np.random.default_rng(3)
    members = rng.choice(d, size=j, replace=False)
    bundle = cb[members].sum(axis=0)
    oracle = theory.peel_sic_orthonormal_recall()
    for mode in ("unit", "proj"):
        idx, _ = peel_sic_readout(bundle, cb, n_items=j, mode=mode)
        assert _set_recall(idx, members, j) == pytest.approx(oracle), f"mode={mode}"


def test_peel_beats_flat_at_high_load_real() -> None:
    """HRR (float32) near-orthogonal codes: flat top-J collapses, peel/SIC recovers (discriminator fires)."""
    d, m, j, n_trials = 128, 400, 20, 40
    cb = _real_codebook(m, d, seed=0)
    rng = np.random.default_rng(0)
    flat_r = peel_u_r = peel_p_r = 0.0
    for _ in range(n_trials):
        members = rng.choice(m, size=j, replace=False)
        bundle = cb[members].sum(axis=0).astype(np.float32)
        fi, _ = flat_topk_readout(bundle, cb, n_items=j)
        pu, _ = peel_sic_readout(bundle, cb, n_items=j, mode="unit")
        pp, _ = peel_sic_readout(bundle, cb, n_items=j, mode="proj")
        flat_r += _set_recall(fi, members, j)
        peel_u_r += _set_recall(pu, members, j)
        peel_p_r += _set_recall(pp, members, j)
    flat_r /= n_trials
    peel_u_r /= n_trials
    peel_p_r /= n_trials
    # discriminator fires: flat has collapsed (mis-ranks members under cross-talk)
    assert flat_r < 0.85, f"flat readout should collapse at high load, got {flat_r:.3f}"
    # peel/SIC recovers
    assert peel_u_r > 0.90, f"peel/SIC (unit) should recover, got {peel_u_r:.3f}"
    # material lift (the certified phenomenon)
    assert peel_u_r - flat_r > 0.15, f"peel lift over flat too small: {peel_u_r - flat_r:+.3f}"
    assert peel_p_r > flat_r, f"peel/SIC (proj) should also beat flat, got {peel_p_r:.3f} vs {flat_r:.3f}"


def test_peel_beats_flat_at_high_load_complex_fhrr() -> None:
    """FHRR (complex64) phasor codes: peel/SIC recovers near-perfectly, beats flat top-J."""
    d, m, j, n_trials = 128, 400, 24, 40
    cb = _complex_codebook(m, d, seed=20)
    rng = np.random.default_rng(20)
    flat_r = peel_r = 0.0
    for _ in range(n_trials):
        members = rng.choice(m, size=j, replace=False)
        bundle = cb[members].sum(axis=0)
        fi, _ = flat_topk_readout(bundle, cb, n_items=j)
        pu, _ = peel_sic_readout(bundle, cb, n_items=j, mode="unit")
        flat_r += _set_recall(fi, members, j)
        peel_r += _set_recall(pu, members, j)
    flat_r /= n_trials
    peel_r /= n_trials
    assert flat_r < 0.95, f"flat should not saturate at this load, got {flat_r:.3f}"
    assert peel_r > 0.95, f"peel/SIC should recover on FHRR codes, got {peel_r:.3f}"
    assert peel_r - flat_r > 0.05, f"peel lift too small on FHRR: {peel_r - flat_r:+.3f}"


def test_matches_bruteforce_reference() -> None:
    """hdlab peel/SIC == independent brute-force matching pursuit (same member set) on real + complex."""
    for cb, seed in ((_real_codebook(120, 96, 1), 5), (_complex_codebook(120, 96, 2), 6)):
        rng = np.random.default_rng(seed)
        j = 14
        members = rng.choice(cb.shape[0], size=j, replace=False)
        bundle = cb[members].sum(axis=0)
        for mode in ("unit", "proj"):
            idx, _ = peel_sic_readout(bundle, cb, n_items=j, mode=mode)
            ref = _reference_peel(bundle, cb, j, mode)
            assert set(int(x) for x in idx) == set(ref), f"mode={mode} dtype={cb.dtype}"


def test_batch_matches_single_and_registry() -> None:
    """Batched readout == per-row single readout; BUNDLE_READOUTS registry exposes all three."""
    assert set(BUNDLE_READOUTS) == {"flat_topk", "peel_sic_unit", "peel_sic_proj"}
    cb = _real_codebook(300, 96, seed=7)
    rng = np.random.default_rng(7)
    j, b = 16, 5
    bundles = np.stack([cb[rng.choice(300, size=j, replace=False)].sum(0) for _ in range(b)]).astype(np.float32)
    for name, fn in BUNDLE_READOUTS.items():
        batch_idx, _ = fn(bundles, cb, j)
        assert batch_idx.shape == (b, j), name
        for r in range(b):
            single_idx, _ = fn(bundles[r], cb, j)
            assert single_idx.shape == (j,)
            assert np.array_equal(np.sort(single_idx), np.sort(batch_idx[r])), f"{name} row {r}"


def test_input_validation() -> None:
    """n_items out of range and bad mode raise ValueError (no silent misuse)."""
    cb = _real_codebook(40, 32, seed=0)
    bundle = cb[[1, 2, 3]].sum(0)
    with pytest.raises(ValueError):
        peel_sic_readout(bundle, cb, n_items=0)
    with pytest.raises(ValueError):
        peel_sic_readout(bundle, cb, n_items=41)
    with pytest.raises(ValueError):
        peel_sic_readout(bundle, cb, n_items=3, mode="bogus")
    with pytest.raises(ValueError):
        flat_topk_readout(bundle, cb, n_items=41)
