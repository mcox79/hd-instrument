"""Witness -- the one open lead, POWERED and CONFIRMED. Pooling TellMeWhy train+validation+test to a large GOAL
non-adjacent set (n~935, test n~467) shows strategy's broad script-order cue (p_before), added to the
Competition-Model integrator, gives a CI-SEPARATED, LOAD-BEARING lift: the 5-cue integrator beats the 4-cue one
CI-sep AND beats a per-item shuffled-script twin CI-sep. (The earlier n=46 estimate was underpowered; the honest
powered effect is ~+0.06.) No leak: weights fit on train, scored on a disjoint test split; gold never touches
prediction. A brain-foundational win (Schank-Abelson script prior + Competition-Model cue integration) built
entirely from existing capabilities.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_script_order_power.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_script_order_power_v1 as P


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = P.run(cap=6000)
    if "error" in o:
        print("[FAIL] broad order store absent: %s" % o["path"]); return 1
    ev = o["TellMeWhy_pooled"]; oks = []

    oks.append(check(
        "W1 POWERED: the script-order cue gives a CI-separated lift over the 4-cue Competition-Model integrator "
        "on the large pooled TellMeWhy GOAL test split",
        ev["five_vs_four"]["ci_sep"] and ev["acc5"] > ev["acc4"],
        "test n=%d | 4cue %.3f 5cue %.3f (5v4 %+.4f CI%s)" % (
            ev["n_test"], ev["acc4"], ev["acc5"], ev["five_vs_four"]["delta"], ev["five_vs_four"]["ci"])))

    oks.append(check(
        "W2 LOAD-BEARING: the cue beats a per-item shuffled-script twin CI-separated (the p_before STRUCTURE "
        "carries real signal, not raw density)",
        ev["script_load_bearing"]["ci_sep"],
        "vs shuffled-script twin %+.4f CI%s" % (
            ev["script_load_bearing"]["delta"], ev["script_load_bearing"]["ci"])))

    oks.append(check(
        "W3 powered GOAL sample is large enough to trust (>=300 test items) and verdict confirms",
        ev["n_test"] >= 300 and o["verdict"] == "SCRIPT_ORDER_CONFIRMED_LOAD_BEARING_LIFT",
        "pooled n=%d test n=%d verdict=%s" % (o["n_goal_pooled"], ev["n_test"], o["verdict"])))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  verdict=%s" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), o["verdict"]))
    print("=" * 92)
    return 0 if n == len(oks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
