"""Scaffold-free witness: pattern-separated recollection is NOT self-certifying in our substrate.

Slug no_automatic_reliability_signal_reaches_the_source_oracle. Re-derives the decisive fact DIRECTLY
from the recall instrument (reads no experiment metrics.json): recollection's own confidence does not
certify its correctness -- at EVERY firing strictness, when recollection fires its pick is right LESS
often than plain familiarity (F_COUNT1) is on the SAME items. So the brain-foundational
"intrinsic reliability from a thresholded hippocampal completer" mechanism (which self-certifies on
synthetic data -- see the cell's --self-test) cannot be instantiated here: the episodic store lacks
distinctive, completable traces at reading scale.

  .venv/Scripts/python.exe verification/test_pattern_separated_recollection_not_self_certifying.py
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
import experiments.exp_pattern_separated_recollection_gate_v1 as PS


def main():
    sents, store, pmi, nb, rec = G._build(smoke=False)
    lemmas = store["lemmas"]
    n_lem = len(lemmas)
    cidx = pmi["cidx"]
    M_ppmi = pmi["M"]
    q_true = np.arange(n_lem, dtype=np.int64)
    q_ctx = [R._ctx_ids_for(store["held_cue"][L][0], L, cidx) for L in lemmas]

    E = rec["E"].tocsr()
    idf = rec["idf"]
    offsets = rec["offsets"]
    V = E.shape[1]
    dfreq = np.asarray(E.sum(axis=0)).ravel()
    dist_mask = PS._distinctive_mask(dfreq)
    Ebin = E.copy(); Ebin.data[:] = 1.0
    Eidf_dist = (Ebin @ sparse.diags(idf * dist_mask)).tocsr()

    scorers = G._scorers(nb, rec, M_ppmi, cidx, n_lem)
    hit_count1 = (scorers["COUNT1"](q_ctx).argmax(axis=1) == q_true).astype(float)

    # recollection winning idf-distinctive score + pick (the completer's own confidence)
    ps_pick = np.zeros(n_lem, np.int64)
    ps_score = np.zeros(n_lem)
    batch = 256
    for b0 in range(0, n_lem, batch):
        b1 = min(n_lem, b0 + batch)
        Qd = np.zeros((V, b1 - b0), np.float32)
        for r, i in enumerate(range(b0, b1)):
            for j in q_ctx[i]:
                if dist_mask[j] > 0:
                    Qd[j, r] = 1.0
        idf_score = np.maximum.reduceat((Eidf_dist @ Qd), offsets, axis=0)
        pick = idf_score.argmax(axis=0)
        for c, i in enumerate(range(b0, b1)):
            ps_pick[i] = pick[c]
            ps_score[i] = idf_score[pick[c], c]
    hit_ps = (ps_pick == q_true).astype(float)

    floor = float(hit_count1.mean())
    assert abs(floor - 0.3242) < 0.02, "F_COUNT1 %.4f != 0.3242 (instrument mismatch)" % floor

    # at EVERY strictness, recollection precision-when-fired must be BELOW familiarity on the same items
    order = np.argsort(-ps_score)
    worst_margin = -1.0
    for q in (0.02, 0.05, 0.10, 0.20, 0.30, 0.50):
        k = max(1, int(round(q * n_lem)))
        f = np.zeros(n_lem, bool); f[order[:k]] = True
        prec = float(hit_ps[f].mean())
        fam = float(hit_count1[f].mean())
        assert prec < fam, "recollection SELF-CERTIFIES at cov=%.2f (prec %.4f >= familiarity %.4f) -- rewrite the verdict" % (q, prec, fam)
        worst_margin = max(worst_margin, fam - prec)

    # even at the most confident 2%, recollection is clearly worse than familiarity
    k2 = max(1, int(round(0.02 * n_lem)))
    f2 = np.zeros(n_lem, bool); f2[order[:k2]] = True
    prec2 = float(hit_ps[f2].mean()); fam2 = float(hit_count1[f2].mean())
    assert fam2 - prec2 > 0.1, "the most-confident recollections should be clearly worse than familiarity"

    print("PASS: F_COUNT1=%.4f reproduced." % floor)
    print("      recollection is NOT self-certifying: at EVERY firing strictness its precision-when-fired")
    print("      is below familiarity on the same items (most-confident 2%%: rec %.4f vs familiarity %.4f)."
          % (prec2, fam2))
    print("      => the episodic store lacks separable, completable traces; no firing threshold recovers a")
    print("         trustworthy recollection subset. The reliability signal is unrecoverable because there")
    print("         is no reliable recollection to certify.")
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
