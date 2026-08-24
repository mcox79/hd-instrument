"""Scaffold-free witness for the SOLVE of
`the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by`.

Independently reproduces the one-variable result: holding the entire downstream fixed (PPMI+SVD
consolidation, grounded-hub distillation, the licensed substitutability instrument, the random-hub
info-free twin), the STORE REPRESENTATION decides everything. The brain-foundational explicit-count
store beats its own info-free twin CI-separated and beats the twin's MAX; the live d=256 dense-bundle
store does not beat its own twin. Cross-checks the landed metrics.json. Exit 0 == all pass.

Run: .venv/Scripts/python.exe verification/test_store_representation_is_the_distributional_lever.py
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

METRICS = os.path.join(REPO, "data", "exp_distributional_channel_store_representation_v1", "metrics.json")
import experiments.exp_distributional_channel_store_representation_v1 as E
import experiments.exp_crossmodal_distillation_substitutability_v1 as X


def _load_ctx():
    mp, ms, cached, words, counts, vocab = E.load_population()
    M_B = E.true_count_matrix(words, counts, vocab)
    V = E.vocab_codes(vocab)
    row_idx = {w: i for i, w in enumerate(words)}
    freq = np.asarray(M_B.sum(1)).ravel()
    present = [(w1, w2, p) for (w1, w2, p) in mp + ms
               if row_idx.get(w1) is not None and row_idx.get(w2) is not None]
    gold = {" ".join(t[:2]): 1 for t in mp}
    y = np.array([gold.get(" ".join(t[:2]), 0) for t in present])
    i1s = np.array([row_idx[w1] for (w1, w2, _) in present])
    i2s = np.array([row_idx[w2] for (w1, w2, _) in present])
    inst_words = set(w for w1, w2, _ in present for w in (w1, w2))
    hubs = X.build_hubs(words, freq)
    ctx = {"row_idx": row_idx, "words_present": words, "present": present, "y": y,
           "i1s": i1s, "i2s": i2s, "inst_words": inst_words, "hubs": hubs}
    return ctx, M_B, V


def test_explicit_store_reproduces_the_landed_distributional_space():
    """phi built from the explicit counts here reproduces the landed 0.8388 cell's own phi -- so the
    space under test IS the licensed one, not a drifted copy."""
    ctx, M_B, V = test_explicit_store_reproduces_the_landed_distributional_space._ctx
    phi_B = E.ppmi_svd(M_B)
    D_land = X.load_everything()
    diff = float(np.max(np.abs(np.abs(phi_B) - np.abs(D_land["phi"]))))
    print("[phi_B] reproduces landed phi: abs-max abs-diff=%.2e" % diff)
    assert diff < 1e-3, "phi_B drifted from the landed space (%.2e)" % diff
    return phi_B


def test_explicit_store_beats_its_own_twin_and_bundle_does_not():
    """THE ONE-VARIABLE HEADLINE, reproduced live: only the explicit-count store clears its own info-
    free twin; the raw d=256 bundle store (the incumbent) does not."""
    ctx, M_B, V = test_explicit_store_beats_its_own_twin_and_bundle_does_not._ctx
    phi_B = E.ppmi_svd(M_B)
    SUMS = M_B @ V
    phi_A_raw = X.l2n(SUMS.copy())          # the live d=256 bundle store
    B = E.score_phi("B_EXPLICIT", phi_B, ctx, n_boot=2000, n_null=40, n_seed=4)
    A = E.score_phi("A_RAW_BUNDLE", phi_A_raw, ctx, n_boot=2000, n_null=40, n_seed=4)
    print("[B explicit ] auc=%.4f CI=%s  own null p95=%.4f MAX=%.4f" %
          (B["oriented_auc_mean"], B["seed0_ci95"], B["null_p95"], B["null_max"]))
    print("[A raw bundle] auc=%.4f CI=%s  own null p95=%.4f MAX=%.4f" %
          (A["oriented_auc_mean"], A["seed0_ci95"], A["null_p95"], A["null_max"]))
    assert B["seed0_ci95"][0] > B["null_p95"], "B does not clear its own twin p95 CI-separated"
    assert B["oriented_auc_mean"] > B["null_max"], "B does not beat its own twin MAX"
    assert A["oriented_auc_mean"] <= A["null_p95"] + 0.02, "raw bundle unexpectedly beats its own twin"
    assert B["oriented_auc_mean"] - A["oriented_auc_mean"] > 0.15, "store representation is not the lever"
    return {"B": B["oriented_auc_mean"], "A_raw": A["oriented_auc_mean"]}


def test_degeneracy_pipeline_does_not_manufacture_auc():
    """Empty and random phi must score at chance through the same distillation -- so the >0.5 is
    information in phi_B, not the scorer."""
    ctx, M_B, V = test_degeneracy_pipeline_does_not_manufacture_auc._ctx
    phi_empty = np.zeros((len(ctx["words_present"]), E.SVD_K))
    phi_rand = X.l2n(np.random.default_rng(E.MASTER_SEED + 777).standard_normal((len(ctx["words_present"]), E.SVD_K)))
    e = E.score_phi("EMPTY", phi_empty, ctx, n_boot=1500, n_null=10, n_seed=2)["oriented_auc_mean"]
    r = E.score_phi("RANDOM", phi_rand, ctx, n_boot=1500, n_null=10, n_seed=2)["oriented_auc_mean"]
    print("[degeneracy] empty=%.4f random=%.4f" % (e, r))
    assert e < 0.6 and r < 0.6, "pipeline manufactures AUC from a contentless phi (empty=%.3f random=%.3f)" % (e, r)
    return {"empty": e, "random": r}


def test_landed_metrics_agree():
    """Cross-check the landed artifact's own verdict."""
    d = json.load(open(METRICS))
    B = d["ARMS"]["B_EXPLICIT_STORE"]; Ad = d["ARMS"]["A_BUNDLE_DECODE"]; Ar = d["ARMS"]["A_RAW_BUNDLE"]
    print("[landed] B=%.4f CI=%s null_p95=%.4f MAX=%.4f | A_decode=%.4f (own p95 %.4f) | A_raw=%.4f (own p95 %.4f)"
          % (B["oriented_auc_mean"], B["seed0_ci95"], B["null_p95"], B["null_max"],
             Ad["oriented_auc_mean"], Ad["null_p95"], Ar["oriented_auc_mean"], Ar["null_p95"]))
    assert d["INSTRUMENT_LICENSED"]
    assert d["VERDICT"]["SOLVED"] is True
    assert d["VERDICT"]["store_representation_is_the_lever"] is True
    assert B["seed0_ci95"][0] > B["null_p95"], "landed: B CI_lo does not clear its twin p95"
    assert B["oriented_auc_mean"] > B["null_max"], "landed: B mean does not beat twin MAX"
    assert Ad["oriented_auc_mean"] <= Ad["null_p95"] + 0.02, "landed: A_decode beats its own twin"
    assert Ar["oriented_auc_mean"] <= Ar["null_p95"] + 0.02, "landed: A_raw beats its own twin"
    assert d["DEGENERACY"]["EMPTY_phi"] < 0.6 and d["DEGENERACY"]["RANDOM_phi"] < 0.6
    return d["VERDICT"]


def main():
    ctx = _load_ctx()
    for t in (test_explicit_store_reproduces_the_landed_distributional_space,
              test_explicit_store_beats_its_own_twin_and_bundle_does_not,
              test_degeneracy_pipeline_does_not_manufacture_auc):
        t._ctx = ctx
    tests = [
        test_explicit_store_reproduces_the_landed_distributional_space,
        test_explicit_store_beats_its_own_twin_and_bundle_does_not,
        test_degeneracy_pipeline_does_not_manufacture_auc,
        test_landed_metrics_agree,
    ]
    n = 0
    for t in tests:
        try:
            t()
            print("PASS  %s" % t.__name__)
            n += 1
        except Exception as e:
            print("FAIL  %s -> %s" % (t.__name__, e))
    print("\n%d/%d WITNESSES PASSED" % (n, len(tests)))
    return 0 if n == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())
