"""Witness -- the POSITION FLOOR on TellMeWhy (the same floor GLUCOSE was dominated by). OPPOSITE result:
TellMeWhy non-adjacent cause-ID is POSITION-USELESS (earliest/nearest/before_nearest ~ 0.00; causes are NOT
positionally predictable), so the result-state rollout GOAL-subset win is NOT a position artifact -- rs_refine
CI-beats the strongest position floor by ~+0.30 AND CI-beats base by ~+0.087 (reproducing the original win).
=> the result-state rollout is a GENUINE win over the strongest floor on TellMeWhy; the dominant simple signal is
DATASET-DEPENDENT (position on GLUCOSE, semantic/result-state on TellMeWhy).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_tellmewhy_position_floor.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_tellmewhy_position_floor_v1 as T


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = T.run(n=1500)
    g = o["GOAL"]; gv = g["overall"]
    oks = []

    oks.append(check(
        "W1 TellMeWhy is POSITION-USELESS on the GOAL subset: the best position floor is CI-sep BELOW base "
        "(opposite of GLUCOSE)",
        g["pos_best_vs_base"]["ci"][1] < 0,
        "pos_best=%s %.3f vs base %.3f (%+.4f CI%s)" % (
            g["pos_best"], gv[g["pos_best"]], gv["base"], g["pos_best_vs_base"]["delta"],
            g["pos_best_vs_base"]["ci"])))

    oks.append(check(
        "W2 the result-state rollout CI-beats the strongest POSITION floor (the win is NOT a position artifact)",
        g["rs_refine_vs_pos_best"]["ci_sep"] and gv["rs_refine"] > gv[g["pos_best"]],
        "rs_refine %.3f vs pos_best %.3f (%+.4f CI%s)" % (
            gv["rs_refine"], gv[g["pos_best"]], g["rs_refine_vs_pos_best"]["delta"],
            g["rs_refine_vs_pos_best"]["ci"])))

    oks.append(check(
        "W3 the original win reproduces: rs_refine CI-beats base on the GOAL subset",
        g["rs_refine_vs_base"]["ci_sep"] and gv["rs_refine"] > gv["base"],
        "rs_refine %.3f vs base %.3f (%+.4f CI%s)" % (
            gv["rs_refine"], gv["base"], g["rs_refine_vs_base"]["delta"], g["rs_refine_vs_base"]["ci"])))

    oks.append(check(
        "W4 verdict = RESULTSTATE_BEATS_POSITION_FLOOR", o["verdict"] == "RESULTSTATE_BEATS_POSITION_FLOOR",
        o["verdict"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  GOAL n=%d" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), g["n"]))
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
