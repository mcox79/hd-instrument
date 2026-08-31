"""Organ witness for the ANTI-DRIFT SLOW-ANCHOR primitive promoted into hdlab/cls_growth.py 2026-08-31
(Q111) from the integrated live-canary problem run_the_learner_on_live_and_evaluate_the_full_safety_and
_benefit_suite (owner-DONE). Proves, on synthetic vectors (fast, no reads, no LLM):

  1. procrustes_rotation is ORTHOGONAL (R R^T = I) -> norm-preserving (the shared-frame guarantee).
  2. align_and_fuse eta=0 (FROZEN) returns the L2-normalised ANCHOR on shared words (infinite inertia);
     eta=1 returns the aligned GROWN store; small eta sits between (the EMA slow anchor).
  3. do_align=True (shared frame) differs from do_align=False (unaligned control) when the grown store is
     in a ROTATED frame -- i.e. the Procrustes step is load-bearing, not decorative.
  4. UNION vocab semantics: anchor-only + grown-only words are both retained (keep-both, never discards).
  5. FAITHFUL PROMOTION: hdlab.cls_growth.align_and_fuse == the experiment's align_and_fuse BYTE-FOR-BYTE
     on random inputs (proves the promotion is verbatim; no drift at landing while the exp keeps its copy).

Reverify: .venv/Scripts/python.exe verification/test_cls_growth_anchor_primitive_organ.py
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.cls_growth import procrustes_rotation, align_and_fuse, _l2norm_rows


def _rand_store(rng, words, d):
    vecs = rng.standard_normal((len(words), d))
    idx = {w: i for i, w in enumerate(words)}
    return vecs, idx


def test_procrustes_is_orthogonal():
    rng = np.random.default_rng(0)
    A = rng.standard_normal((30, 8)); B = rng.standard_normal((30, 8))
    R = procrustes_rotation(A, B)
    I = R @ R.T
    assert np.allclose(I, np.eye(R.shape[0]), atol=1e-9), "procrustes R not orthogonal"
    print("PASS procrustes: R orthogonal (norm-preserving), R@R.T == I")


def test_frozen_vs_grown_endpoints_and_ema_between():
    rng = np.random.default_rng(1)
    words = [f"w{i}" for i in range(40)]
    d = 12
    ref, ridx = _rand_store(rng, words, d)
    new, nidx = _rand_store(rng, words, d)   # same vocab -> pure interpolation on shared frame
    # align_and_fuse returns UNION (lexicographically-sorted) row order -> compare PER WORD via the returned index
    frozen, fi = align_and_fuse(ref, ridx, new, nidx, alpha=0.0, do_align=True)
    grown, gi = align_and_fuse(ref, ridx, new, nidx, alpha=1.0, do_align=True)
    ema, ei = align_and_fuse(ref, ridx, new, nidx, alpha=0.1, do_align=True)
    refn = _l2norm_rows(np.asarray(ref, float))
    assert all(np.allclose(frozen[fi[w]], refn[ridx[w]], atol=1e-9) for w in ridx), \
        "eta=0 must return the L2-normalised anchor (frozen) per word"
    # small-eta EMA moves off the anchor but stays MUCH closer to it than the fully-grown store
    d_ema = float(sum(np.linalg.norm(ema[ei[w]] - refn[ridx[w]]) for w in ridx))
    d_grown = float(sum(np.linalg.norm(grown[gi[w]] - refn[ridx[w]]) for w in ridx))
    assert 0.0 < d_ema < d_grown, {"d_ema": d_ema, "d_grown": d_grown}
    print(f"PASS anchor: eta=0 == frozen anchor; eta=0.1 EMA between (|ema-anchor|={d_ema:.3f} < |grown-anchor|={d_grown:.3f})")


def test_alignment_is_load_bearing():
    rng = np.random.default_rng(2)
    words = [f"w{i}" for i in range(50)]
    d = 10
    ref, ridx = _rand_store(rng, words, d)
    # put the grown store in a ROTATED frame (a random orthogonal rotation) -> alignment should matter
    Q, _ = np.linalg.qr(rng.standard_normal((d, d)))
    new = np.asarray(ref, float) @ Q
    nidx = dict(ridx)
    aligned, _ = align_and_fuse(ref, ridx, new, nidx, alpha=0.5, do_align=True)
    unaligned, _ = align_and_fuse(ref, ridx, new, nidx, alpha=0.5, do_align=False)
    assert not np.allclose(aligned, unaligned, atol=1e-6), "Procrustes alignment made no difference (should)"
    print("PASS alignment: shared-frame (do_align=True) != unaligned control on a rotated grown store")


def test_union_keep_both():
    rng = np.random.default_rng(3)
    ref, ridx = _rand_store(rng, [f"a{i}" for i in range(20)] + ["shared"], 6)
    new, nidx = _rand_store(rng, [f"b{i}" for i in range(20)] + ["shared"], 6)
    fused, uidx = align_and_fuse(ref, ridx, new, nidx, alpha=0.3, do_align=True)
    assert "a0" in uidx and "b0" in uidx and "shared" in uidx, "union vocab must retain anchor-only + grown-only"
    assert fused.shape[0] == len(set(ridx) | set(nidx)), "fused rows != union size"
    print(f"PASS keep-both: union vocab retains anchor-only + grown-only (|union|={fused.shape[0]})")


def test_faithful_promotion_byte_for_byte():
    import experiments.exp_learner_growth_aligned_continual_v1 as AL
    rng = np.random.default_rng(4)
    words_r = [f"w{i}" for i in range(35)] + ["only_ref"]
    words_n = [f"w{i}" for i in range(35)] + ["only_new"]
    ref, ridx = _rand_store(rng, words_r, 9)
    new, nidx = _rand_store(rng, words_n, 9)
    for alpha in (0.0, 0.1, 0.5, 1.0):
        for do_align in (True, False):
            h_v, h_i = align_and_fuse(ref, ridx, new, nidx, alpha, do_align)
            e_v, e_i = AL.align_and_fuse(ref, ridx, new, nidx, alpha, do_align)
            assert h_i == e_i, (alpha, do_align, "index mismatch")
            assert np.array_equal(h_v, e_v), (alpha, do_align, "vecs not byte-identical to the experiment")
    print("PASS faithful-promotion: hdlab.align_and_fuse == experiment's align_and_fuse byte-for-byte (no drift)")


if __name__ == "__main__":
    tests = [test_procrustes_is_orthogonal, test_frozen_vs_grown_endpoints_and_ema_between,
             test_alignment_is_load_bearing, test_union_keep_both, test_faithful_promotion_byte_for_byte]
    for t in tests:
        t()
    print(f"\nALL {len(tests)} WITNESS TESTS PASSED")
