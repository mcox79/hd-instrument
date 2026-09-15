"""Witness -- strategy's broad script-order store (temporal_script_schema over chains_broad.json, 454k
p_before verb-pairs) added as a DIRECTED cue to the Competition-Model integrator. HONEST result, matching
strategy's own scope caveat: the context-free SCRIPT PRIOR does NOT give a CI-separated load-bearing accuracy
lift for cause-selection. On GLUCOSE (position-dominant) it is flat; on TellMeWhy the point estimate is
encouraging (0.391->0.500) but NOT CI-separated (n=46 test, underpowered) and not load-bearing vs a shuffled-
script twin. COVERAGE is high (>0.85 both) -> the limit is per-pair CORRECTNESS / story-specific context, not
store coverage. Closing it needs reading the specific story's context (a categorically deeper mechanism, per
strategy), not another store.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_script_order_cue.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_script_order_cue_v1 as SC


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = SC.run(n_glu=3000, n_tmw=1500)
    if "error" in o:
        print("[FAIL] broad order store absent: %s" % o["path"]); return 1
    glu = o["GLUCOSE"]; tmw = o["TellMeWhy"]
    oks = []

    oks.append(check(
        "W1 no CI-separated integrator lift on GLUCOSE (adding the script-order cue does not beat the 4-cue "
        "integrator on the position-dominant corpus)",
        not glu["five_vs_four"]["ci_sep"],
        "GLUCOSE 4cue %.3f 5cue %.3f (5v4 %+.4f CI%s)" % (
            glu["acc4"], glu["acc5"], glu["five_vs_four"]["delta"], glu["five_vs_four"]["ci"])))

    oks.append(check(
        "W2 the script-order cue is NOT load-bearing vs a per-item SHUFFLED-script twin on either corpus",
        not glu["script_load_bearing"]["ci_sep"] and not tmw["script_load_bearing"]["ci_sep"],
        "GLUCOSE LB %+.4f CI%s | TellMeWhy LB %+.4f CI%s (TMW 5cue %.3f pt-est vs 4cue %.3f, CI%s)" % (
            glu["script_load_bearing"]["delta"], glu["script_load_bearing"]["ci"],
            tmw["script_load_bearing"]["delta"], tmw["script_load_bearing"]["ci"],
            tmw["acc5"], tmw["acc4"], tmw["five_vs_four"]["ci"])))

    oks.append(check(
        "W3 the store COVERAGE is high on both corpora (>0.85) -> the limit is per-pair correctness / "
        "story-specific context, NOT store coverage (strategy's scope confirmed)",
        glu["script_coverage"] > 0.85 and tmw["script_coverage"] > 0.85,
        "GLUCOSE cov %.2f script_alone %.3f | TellMeWhy cov %.2f script_alone %.3f" % (
            glu["script_coverage"], glu["script_alone_acc"], tmw["script_coverage"], tmw["script_alone_acc"])))

    oks.append(check(
        "W4 verdict = script-order cue gives no CI-separated load-bearing lift",
        o["verdict"] == "SCRIPT_ORDER_CUE_NO_LIFT", o["verdict"]))

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
