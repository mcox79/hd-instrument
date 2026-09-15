#!/usr/bin/env python3
"""Scaffold-free witness for the v2 reading-induced category organ (closed-class separation + token-level posterior).

Runs the cell in its own bounded smoke universe (20k Simple-Wiki lines, gold UD-EWT test as the measuring instrument only --
never in acquisition); touches no landed metrics.json. Asserts the mechanism, not a tuned number:

  A  BEATS FLOORS      type-level and token-level many-to-one both beat the majority floor, and the shuffled-cluster TWIN
                       loses (CI lower bound > 0) -> the lift is real category structure, not coverage or label-count.
  B  SEPARATES CLOSED  >= 4 of the closed classes {ADP,AUX,CCONJ,SCONJ,PART,DET,PRON,ADV} reach recall > 0.4 at the type
                       level -- including CCONJ, which v1's round-0 merges into ADP (recall ~0). This is the brief's gap.
  C  TOKEN 100% COVER  the token-level readout covers every token (coverage == 1.0).
  D  ORACLE >= LEARNED the gold-closed-membership oracle is not worse than the learned stratum -> the residual (whatever
                       does not separate) is a membership/granularity limit, faithfully bounded, not a broken mechanism.

Run: .venv/Scripts/python.exe verification/test_reading_induced_categories_v2.py
"""
import os
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
os.environ.setdefault("HDLAB_EXP_NAME", "reading_induced_categories_v2_selftest")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_reading_induced_categories_v2 as V2
from experiments.exp_reading_induced_categories_v1 import ud_test_tokens


def main():
    test = ud_test_tokens(V2.UD_TEST)
    logs = []
    r, _w2c, _model, _final, _vocab = V2.run(20000, 34, 500, 8000, 60, 120, 12, 4.0, 40, V2.SEED, test, logs.append,
                                             oracle=True, Lmax=4, frame_weight=0.4)
    # A -- floors + twin
    assert r["type_m2o"] > r["majority"], ("type must beat majority", r["type_m2o"], r["majority"])
    assert r["token_m2o"] > r["majority"], ("token must beat majority", r["token_m2o"], r["majority"])
    assert r["type_minus_twin"][1] > 0, ("shuffled twin must LOSE (CI lower>0)", r["type_minus_twin"])
    # B -- closed-class separation, CCONJ specifically un-merged
    sep = {k: v for k, v in r["closed_recall_type"].items() if v > 0.4}
    assert len(sep) >= 4, ("at least 4 closed classes must separate at recall>0.4", r["closed_recall_type"])
    assert r["closed_recall_type"]["CCONJ"] > 0.4, ("CCONJ (the ADP-merge the brief names) must separate",
                                                    r["closed_recall_type"])
    # C -- token coverage
    assert r["token_cov"] == 1.0, ("token readout must be 100% coverage", r["token_cov"])
    # D -- oracle not worse than learned (bounds the residual honestly)
    assert "oracle_stratum" in r and r["oracle_stratum"]["type_m2o"] >= r["type_m2o"] - 1e-9, \
        ("gold-membership oracle should upper-bound the learned stratum", r.get("oracle_stratum"), r["type_m2o"])

    print("WITNESS PASS")
    print("  A floors+twin : type=%.4f token=%.4f > majority=%.4f ; type-twin=%+.4f [%+.4f,%+.4f] (twin loses)"
          % (r["type_m2o"], r["token_m2o"], r["majority"], r["type_minus_twin"][0], r["type_minus_twin"][1],
             r["type_minus_twin"][2]))
    print("  B closed sep  : " + " ".join("%s=%.2f" % (k, v) for k, v in r["closed_recall_type"].items())
          + "  (>=4 at >0.4, CCONJ un-merged)")
    print("  C token cover : %.2f" % r["token_cov"])
    print("  D oracle bound: oracle type=%.4f >= learned type=%.4f" % (r["oracle_stratum"]["type_m2o"], r["type_m2o"]))
    print("  => the function-word stratum + second-order directional frames separate the closed classes v1 merged, at "
          "100%% token coverage, twin-controlled; the oracle bounds the residual.")
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
