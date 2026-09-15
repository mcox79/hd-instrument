"""Scaffold-free witness for wire_the_curated_meaning_foundation_into_a_live_consumer_and_adopt_the_maxsim_usage.

The curated meaning foundation, wired as taxonomic sense signatures read against context (the live WiC / one live
meaning board metric), is the FIRST glass-box mechanism to achieve CI-separated REAL per-context sense
discrimination on gold WiC -- where the live PPR select_sense reader and the associative/gloss baseline fail.

C1  curated foundation CROSSES the per-context wall: curated_flat beats its mis-seeded-context twin CI-sep on
    BOTH held-out splits (dev n=638 AND test n=1400) -- real per-context discrimination.
C2  the CURATED KNOWLEDGE is the lever: gloss-only FAILS its twin on dev (reproduces the disk's negative) while
    curated crosses it on the SAME split.
C3  info-free knowledge control: curated beats its SHUFFLED-SIGNATURE twin CI-sep (correct sense<->signature
    binding, not machinery).
C4  the biased-competition readout is NOT the WiC lever (it is the a_s lever): DIAG does not CI-beat FLAT.
C5  leak discipline: the FROZEN asset (includes synset.examples(), which WiC was built from) is leak-INFLATED
    on WiC vs the leak-free curated rebuild -> the honest WiC number is the leak-free one.

Run: .venv/Scripts/python.exe verification/test_curated_foundation_wic.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: F401
import experiments.exp_curated_foundation_wic_v1 as E
from tools.load_wsd_benchmarks import load_wic


def _warm(pairs):
    for s in E._all_candidate_synsets(pairs):
        E._sig(s, "gloss"); E._sig(s, "curated")


def main():
    print("witness: curated meaning foundation crosses the WiC per-context sense-discrimination wall")
    dev = E._prep(load_wic("dev")); test = E._prep(load_wic("test"))
    _warm(dev + test)

    cur_dev = E._eval(dev, "curated", "flat", 0)
    cur_test = E._eval(test, "curated", "flat", 0)
    glo_dev = E._eval(dev, "gloss", "flat", 0)
    print("  dev  n=%d  curated_flat acc=%.4f  real_vs_twin d=%+.4f sep=%s | gloss_flat d=%+.4f sep=%s"
          % (cur_dev["n"], cur_dev["acc"], cur_dev["real_vs_twin"]["delta"], cur_dev["real_vs_twin"]["sep"],
             glo_dev["real_vs_twin"]["delta"], glo_dev["real_vs_twin"]["sep"]))
    print("  test n=%d  curated_flat acc=%.4f  real_vs_twin d=%+.4f sep=%s"
          % (cur_test["n"], cur_test["acc"], cur_test["real_vs_twin"]["delta"], cur_test["real_vs_twin"]["sep"]))
    assert cur_dev["real_vs_twin"]["sep"], "C1 FAIL: curated does not cross its mis-seeded twin on dev"
    assert cur_test["real_vs_twin"]["sep"], "C1 FAIL: curated does not cross its mis-seeded twin on test"
    print("  C1 PASS: curated crosses the mis-seeded-context wall CI-sep on BOTH held-out splits")

    assert not glo_dev["real_vs_twin"]["sep"], "C2 FAIL: gloss unexpectedly crosses its twin on dev"
    assert cur_dev["real_vs_twin"]["delta"] > glo_dev["real_vs_twin"]["delta"], "C2 FAIL: curated not > gloss margin"
    print("  C2 PASS: the CURATED knowledge is the lever (gloss FAILS its twin on dev; curated crosses it)")

    # C3 shuffled-signature twin (pooled for power)
    pool = dev + test
    cand = E._all_candidate_synsets(pool)
    rng = np.random.default_rng(9); perm = rng.permutation(len(cand))
    shuf = {cand[i]: E._sig(cand[perm[i]], "curated") for i in range(len(cand))}
    real = E._eval(pool, "curated", "flat", 0)
    shufa = E._eval(pool, "curated", "flat", 0, shuffled_sig_map=shuf)
    d = E._paired(real["_correct"] - shufa["_correct"], 13)
    print("  C3  curated_flat=%.4f vs shuffled-signature=%.4f  d=%+.4f sep=%s"
          % (real["acc"], shufa["acc"], d["delta"], d["sep"]))
    assert d["sep"], "C3 FAIL: does not beat the shuffled-signature info-free twin"
    print("  C3 PASS: beats the shuffled-signature info-free twin CI-sep (correct curated knowledge)")

    # C4 diagnostic readout is not the WiC lever
    diag = E._eval(pool, "curated", "diag", 0)
    dd = E._paired(diag["_correct"] - real["_correct"], 11)
    print("  C4  DIAG-FLAT d=%+.4f sep=%s (readout is the a_s lever, neutral on WiC)" % (dd["delta"], dd["sep"]))
    assert not (dd["sep"] and dd["delta"] > 0), "C4 note: diagnostic unexpectedly CI-beats flat on WiC"
    print("  C4 PASS: biased-competition readout does NOT CI-beat flat on WiC (honest: it is the a_s lever)")

    # C5 leak: frozen asset (with examples) is inflated over leak-free curated
    fro = E._eval(pool, "frozen", "flat", 0)
    print("  C5  frozen(leaky)=%.4f  leak-free curated=%.4f  (frozen includes synset.examples())"
          % (fro["acc"], real["acc"]))
    assert fro["acc"] > real["acc"] + 0.02, "C5 FAIL: expected the frozen asset to be leak-inflated on WiC"
    print("  C5 PASS: frozen asset is leak-INFLATED on WiC -> quote the leak-free number")

    # C6 the RECOMMENDED landing: shared-core COARSENING (same lexicographer-file/supersense) lifts WiC over
    # exact-synset equality -- the granularity fix the error analysis diagnosed. Measured on dev (CI-sep) + pooled.
    from nltk.corpus import wordnet as wn
    def _lexname(nm):
        try:
            return wn.synset(nm).lexname()
        except Exception:
            return nm
    def _eval_coarse(ppairs):
        cor_exact, cor_coarse, g = [], [], []
        for p in ppairs:
            tn = [s.name() for s in wn.synsets(p["lemma"], pos=E._WNPOS.get(p["pos"]))]
            if not tn:
                cor_exact.append(int(True == p["gold"])); cor_coarse.append(int(True == p["gold"])); continue
            s1 = E._pick(E._ctx_vecs(p["s1"], p["lemma"]), tn,
                         np.stack([E._sig(s, "curated") if E._sig(s, "curated") is not None
                                   else np.zeros(E._w2v()[1].shape[1]) for s in tn]), "flat")
            s2 = E._pick(E._ctx_vecs(p["s2"], p["lemma"]), tn,
                         np.stack([E._sig(s, "curated") if E._sig(s, "curated") is not None
                                   else np.zeros(E._w2v()[1].shape[1]) for s in tn]), "flat")
            cor_exact.append(int((s1 == s2) == p["gold"]))
            cs = (s1 == s2) or (_lexname(s1) == _lexname(s2))
            cor_coarse.append(int(cs == p["gold"]))
        return np.array(cor_exact), np.array(cor_coarse)
    ce, cc = _eval_coarse(dev)
    dd = E._paired(cc - ce, 17)
    print("  C6  dev curated-EXACT=%.4f -> curated+COARSEN=%.4f  d=%+.4f CI[%+.4f,%+.4f] sep=%s"
          % (ce.mean(), cc.mean(), dd["delta"], dd["lo"], dd["hi"], dd["sep"]))
    assert dd["delta"] > 0 and dd["sep"], "C6 FAIL: shared-core coarsening does not lift WiC CI-sep on dev"
    print("  C6 PASS: shared-core coarsening lifts WiC CI-sep (the granularity fix; recommended landing)")

    print("ALL CHECKS PASS (6/6)")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
