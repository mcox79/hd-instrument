"""Scaffold-free witness: DG/CA3 pattern-separated recollection SELF-CERTIFIES and beats the counting
floor -- the brain-foundational solution to slug no_automatic_reliability_signal_reaches_the_source_oracle.

Re-derives the headline DIRECTLY from the recall instrument (reads no experiment metrics.json):
  * F_COUNT1 (counting floor) reproduces at 0.3242.
  * DG/CA3 recollection SELF-CERTIFIES: its top-5% most-confident firings are right >> familiarity on
    the SAME items (word-overlap recollection does NOT -- its firings are wrong).
  * Intrinsic dual-process routing (recollection when CA3 fires confidently, else familiarity) BEATS the
    counting floor's upper bound.
  * SCRAMBLE control: on cues from a deranged donor lemma the confident firings collapse to ~0 -- the
    confidence reflects genuine cue<->target completion, not an artifact.

  .venv/Scripts/python.exe verification/test_dg_ca3_recollection_self_certifies.py
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("HD_GRADED_COMPARATOR", "1")

import sys
import numpy as np
from scipy import sparse

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_recognition_store_calibrated_familiarity_recollection_v1 as R
import experiments.exp_reliability_geometry_gate_v1 as G
import experiments.exp_dg_ca3_recollection_gate_v1 as DGC


def _top_prec(score, hit, q=0.05):
    k = max(1, int(round(q * len(score))))
    return float(hit[np.argsort(-score)[:k]].mean())


def main():
    sents, store, pmi, nb, rec = G._build(smoke=False)
    lemmas = store["lemmas"]; n_lem = len(lemmas)
    cidx = pmi["cidx"]; M_ppmi = pmi["M"]
    q_true = np.arange(n_lem, dtype=np.int64)
    q_ctx = [R._ctx_ids_for(store["held_cue"][L][0], L, cidx) for L in lemmas]
    E = rec["E"].tocsr(); idf = rec["idf"]; offsets = rec["offsets"]; V = E.shape[1]

    scorers = G._scorers(nb, rec, M_ppmi, cidx, n_lem)
    pred_c1 = scorers["COUNT1"](q_ctx).argmax(axis=1)
    hit_c1 = (pred_c1 == q_true).astype(float)
    floor = float(hit_c1.mean())
    assert abs(floor - 0.3242) < 0.02, "F_COUNT1 %.4f != 0.3242" % floor

    Ssoft = scorers["REC"](q_ctx)
    hit_soft = (Ssoft.argmax(axis=1) == q_true).astype(float)
    soft_top5 = _top_prec(Ssoft.max(axis=1), hit_soft)

    # DG / CA3
    Dp = min(DGC.D_DG, max(256, V // 4))
    P = np.random.default_rng(DGC.PROJ_SEED).standard_normal((V, Dp)).astype(np.float32) / np.sqrt(Dp)
    Ebin = E.copy(); Ebin.data[:] = 1.0
    Eidf = (Ebin @ sparse.diags(idf.astype(np.float32))).tocsr()
    Ccode = DGC._build_codes(Eidf, P, DGC.K_WTA)

    def recollect(ctx_lists):
        rows, cols, vals = [], [], []
        for i, cl in enumerate(ctx_lists):
            for j in cl:
                rows.append(i); cols.append(j); vals.append(idf[j])
        Q = sparse.csr_matrix((vals, (rows, cols)), shape=(len(ctx_lists), V), dtype=np.float32)
        pick = np.zeros(len(ctx_lists), np.int64); score = np.zeros(len(ctx_lists))
        for b0 in range(0, len(ctx_lists), 256):
            b1 = min(len(ctx_lists), b0 + 256)
            seg = np.maximum.reduceat((Ccode @ DGC._dg_encode(Q[b0:b1], P, DGC.K_WTA).T).toarray(), offsets, axis=0)
            pk = seg.argmax(axis=0)
            for c, i in enumerate(range(b0, b1)):
                pick[i] = pk[c]; score[i] = seg[pk[c], c]
        return pick, score

    ps_pick, ps_score = recollect(q_ctx)
    hit_ps = (ps_pick == q_true).astype(float)
    dg_top5 = _top_prec(ps_score, hit_ps)

    # self-certification: DG/CA3 top-5% precision >> familiarity on same items; word-overlap does NOT
    order = np.argsort(-ps_score); k5 = max(1, int(round(0.05 * n_lem)))
    fam_on_top5 = float(hit_c1[order[:k5]].mean())
    assert dg_top5 > fam_on_top5 + 0.3, "DG/CA3 must self-certify: top5 %.4f vs familiarity %.4f" % (dg_top5, fam_on_top5)
    assert soft_top5 < fam_on_top5, "word-overlap recollection must NOT self-certify: %.4f" % soft_top5

    # routing beats the floor upper bound
    rng = np.random.default_rng(R.MASTER_SEED + 5)
    def ub(x):
        return float(np.percentile([x[rng.integers(0, len(x), len(x))].mean() for _ in range(3000)], 97.5))
    c1_ub = ub(hit_c1)
    best_route = 0.0
    for q in (0.05, 0.10, 0.20):
        k = max(1, int(round(q * n_lem)))
        f = np.zeros(n_lem, bool); f[order[:k]] = True
        route = np.where(f, ps_pick, pred_c1)
        best_route = max(best_route, float((route == q_true).mean()))
    assert best_route > c1_ub, "routing must beat the floor UB %.4f, got %.4f" % (c1_ub, best_route)

    # scramble: deranged donor cues -> confident firings collapse
    donors = R.C3._derangement(n_lem, lambda i, j: i == j)
    scr_pick, scr_score = recollect([q_ctx[donors[i]] for i in range(n_lem)])
    hit_scr = (scr_pick == q_true).astype(float)
    scr_top5 = _top_prec(scr_score, hit_scr)
    assert scr_top5 < 0.05, "scramble must collapse the confident firings: %.4f" % scr_top5

    print("PASS: F_COUNT1=%.4f floor UB=%.4f." % (floor, c1_ub))
    print("      DG/CA3 SELF-CERTIFIES: top-5%% precision=%.4f vs familiarity %.4f on same items"
          % (dg_top5, fam_on_top5))
    print("      word-overlap recollection does NOT (top-5%% precision=%.4f)." % soft_top5)
    print("      dual-process routing beats floor: best route=%.4f > UB %.4f." % (best_route, c1_ub))
    print("      SCRAMBLE collapses: confident firings on wrong cues right %.4f (=> genuine completion)." % scr_top5)
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
