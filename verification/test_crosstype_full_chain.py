"""Witness for exp_crosstype_full_chain_gum_v1 -- the 100% brain-foundational FULL CHAIN, composed end-to-end.

  W1  the FULL CHAIN (cue-based clustering [Lewis-Vasishth ACT-R] + two-route CLS bridge [Garrod-Sanford in-text U
      deverbal U semantic-memory KB] + identity/bind) lifts the experiencer C3 CI-SEPARATED over the honest floor.
  W2  it COMPOSES WITHOUT REGRESSION: A3 (full chain) >= A1 (current sitpred-floor + in-text bridge) -- the
      brain-foundational stages do not hurt each other (the interdependence the owner flagged is net-positive).
  W3  the info-free twin (shuffled two-route licensing) LOSES (directional; the correct semantic-memory targeting
      is load-bearing, though coverage-bound so not CI-separated).

Run: .venv/Scripts/python.exe verification/test_crosstype_full_chain.py
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_crosstype_full_chain_gum_v1 as FC


def main():
    ok = 0
    r = FC.run(docs_limit=None, verbose=False)

    d0 = r["A3_vs_A0_floor"]
    assert d0["ci_sep"] and d0["delta"] > 0.03, "W1: full chain must lift the experiencer CI-sep over the floor: %s" % d0
    print("W1 PASS: FULL CHAIN A3=%.4f vs honest floor A0=%.4f = %+.4f CI[%+.4f,%+.4f] CI-sep (n=%d)"
          % (r["A3_FULL_CHAIN_cuebased_tworoute"], r["A0_sitpred_floor_nobridge"], d0["delta"], d0["ci"][0], d0["ci"][1], r["n"]))
    ok += 1

    assert r["A3_FULL_CHAIN_cuebased_tworoute"] >= r["A1_sitpred_floor_intext_bridge"] - 0.005, \
        "W2: full chain must compose without regression vs the current mechanism: A3 %.4f vs A1 %.4f" % (
            r["A3_FULL_CHAIN_cuebased_tworoute"], r["A1_sitpred_floor_intext_bridge"])
    print("W2 PASS: composes without regression -- A1 (current) %.4f -> A2 (cue-floor) %.4f -> A3 (full) %.4f (A3-vs-A1 %+.4f, directional)"
          % (r["A1_sitpred_floor_intext_bridge"], r["A2_cuebased_floor_intext_bridge"],
             r["A3_FULL_CHAIN_cuebased_tworoute"], r["A3_vs_A1_current"]["delta"]))
    ok += 1

    assert r["twin_shuffled_tworoute"] < r["A3_FULL_CHAIN_cuebased_tworoute"], \
        "W3: info-free twin must lose: twin %.4f vs A3 %.4f" % (r["twin_shuffled_tworoute"], r["A3_FULL_CHAIN_cuebased_tworoute"])
    print("W3 PASS: info-free twin %.4f < full chain %.4f (correct targeting load-bearing; coverage-bound so %s CI-sep)"
          % (r["twin_shuffled_tworoute"], r["A3_FULL_CHAIN_cuebased_tworoute"], "not" if not r["A3_vs_twin"]["ci_sep"] else ""))
    ok += 1

    # W4 -- the cue-clustering's experiencer contribution is STRUCTURE-DEPENDENT: real cue-floor beats a SHUFFLED-cue
    # floor CI-separated (not an over-merge artifact). This establishes the interdependence.
    ctl = r["A2_vs_A2t_cuefloor_control"]
    assert ctl["ci_sep"] and ctl["delta"] > 0, "W4: real cue-floor must beat the shuffled-cue floor CI-sep: %s" % ctl
    print("W4 PASS: cue-clustering is STRUCTURE-DEPENDENT -- real cue-floor %.4f vs shuffled-cue floor %.4f = %+.4f CI[%+.4f,%+.4f] CI-sep"
          % (r["A2_cuebased_floor_intext_bridge"], r["A2t_SHUFFLED_cue_floor_intext_bridge"], ctl["delta"], ctl["ci"][0], ctl["ci"][1]))
    ok += 1

    print("\nALL WITNESSES PASS (%d/%d)" % (ok, ok))
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
