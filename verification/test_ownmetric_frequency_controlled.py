"""Scaffold-free witness for notes/problems/the_own_metric_may_reward_frequency_not_meaning.

Reproduces the HEADLINE from the cached reading WITHOUT re-running the landed cell in place:
  PHASE (a) -- the own metric is frequency-scored: on the full metric, raw co-occurrence COUNTING
    (TOP_COOC) is many-fold above PMI-normalised counting (TOP_PPMI); and on the frequency-matched
    (EXACT count) pool, COUNTING collapses to EXACTLY chance -- its advantage is pure frequency.
  PHASE (b) -- meaning wins on the fair metric: the concreteness-stripped grounded sensorimotor
    read-out (GROUNDED_NO_CONC) beats the STRONGEST frequency floor CI-separated over its upper bound,
    while both info-free twins (SHUFFLED grounding, RANDOM pick) do NOT beat the floor.

Run:  .venv/Scripts/python.exe verification/test_ownmetric_frequency_controlled.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_meaning_readout_own_metric_v1 as B
import experiments.exp_ownmetric_frequency_controlled_v1 as V1

V1.N_BOOT = 2000            # witness speed; headline is a wide margin, not boundary


def main() -> int:
    from hdlab import distributional_meaning_channel as DMC
    from hdlab import meaning_fusion as MF
    from hdlab.grounded_similarity import grounded_vector

    V1.self_test()
    nb = B.load_gold()
    seeds = (B.SEEDS[0], B.SEEDS[1])       # two seeds is enough for a wide-margin headline
    ctxs = []
    for s in seeds:
        c = V1.build_ctx(s, nb, grounded_vector, DMC, MF)
        assert c is not None, "missing cache for seed %d -- run the base cell --phase build" % s
        ctxs.append(c)

    ok = True

    # -- PHASE (a) i: raw-vs-PMI collapse on the FULL metric (first-hand) --
    for c in ctxs:
        fm = V1.full_metric_floors(c, nb)
        print("[full-metric seed %d] TOP_COOC=%.4f TOP_PPMI=%.4f (collapse x%.1f)"
              % (c.seed, fm["TOP_COOC"], fm["TOP_PPMI"], fm["TOP_COOC"] / max(fm["TOP_PPMI"], 1e-9)),
              flush=True)
        if not (fm["TOP_COOC"] > 3.0 * fm["TOP_PPMI"]):
            print("FAIL: raw counting is not many-fold above PMI-normalised counting")
            ok = False

    # -- build frequency-matched (EXACT) pools, aggregate --
    units = []
    for c in ctxs:
        for K in (1, 4):
            units.append(V1.trials_for(c, nb, "exact", K))
    for K in (1, 4):
        a = V1.aggregate(units, "exact", K)
        fl = a["strongest_freq_floor"]
        ar = a["arms"]
        gnoc = a["comparisons"]["GROUNDED_NO_CONC_vs_%s" % fl]
        print("[exact K=%d] n_trials=%d chance=%.3f | COUNT=%.4f[%.4f,%.4f] | strongest_floor=%s=%.3f "
              "| GNOC=%.3f beats_floor_upper=%s | SHUF=%.3f RAND=%.3f"
              % (K, a["n_trials"], a["chance"], ar["COUNT"]["acc"], ar["COUNT"]["ci_lo"],
                 ar["COUNT"]["ci_hi"], fl, ar[fl]["acc"], ar["GROUNDED_NO_CONC"]["acc"],
                 gnoc["beats_floor_upper_bound"], ar["GROUNDED_SHUF"]["acc"], ar["RANDOM"]["acc"]),
              flush=True)

        # PHASE (a) ii: EXACT-match COUNT is exactly chance -> counting's advantage is pure frequency
        if abs(ar["COUNT"]["acc"] - a["chance"]) > 1e-9:
            print("FAIL: exact-match COUNT is not exactly chance (%.6f vs %.6f)"
                  % (ar["COUNT"]["acc"], a["chance"]))
            ok = False
        # powered
        if a["n_trials"] < V1.MIN_TRIALS:
            print("FAIL: underpowered (n=%d < %d)" % (a["n_trials"], V1.MIN_TRIALS))
            ok = False
        # PHASE (b): concreteness-stripped grounded meaning beats the STRONGEST frequency floor
        if not gnoc["beats_floor_upper_bound"]:
            print("FAIL: GROUNDED_NO_CONC does not beat the strongest frequency floor over its upper bound")
            ok = False
        # twins must NOT beat the floor
        for t in ("GROUNDED_SHUF", "RANDOM"):
            if a["comparisons"]["%s_vs_%s" % (t, fl)]["separated"]:
                print("FAIL: info-free twin %s beats the floor" % t)
                ok = False

    print("WITNESS PASS" if ok else "WITNESS FAIL", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
