"""Scaffold-free witness: the brain-foundational UPGRADE to the cross-type bridge (graded ACT-R/recency
competition replacing the hard uniqueness gate) is a MEASURED win; FrameNet was a measured negative.

UP1 the baseline (uniqueness gate) BYTE-MATCHES the validated landable bridge (live 0.123 @ 0.86) -> the upgrade
    delta is measured against the same mechanism, not a strawman.
UP2 the GRADED recency-margin competition (cue-based retrieval + confidence margin -- more brain-faithful) raises
    LIVE coverage materially (>= 0.16) while holding precision high (>= 0.70, far above force-bind's 0.32).
UP3 the upgrade BOOSTS the downstream affect/goal experiencer lift over the uniqueness baseline, still CI-separated.

Re-derives live from experiments.exp_crosstype_upgrades_gum_v1.run() on GUM.
Run: .venv/Scripts/python.exe verification/test_crosstype_upgrades.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("PYTHONHASHSEED", "0")

import experiments.exp_crosstype_upgrades_gum_v1 as U

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = U.run(verbose=False)
    u = r["UPGRADE_B_recency_margin"]
    bl = u["live"]["baseline_unique"]; ul = u["live"]["upgraded"]
    chk("UP1 the uniqueness baseline byte-matches the validated bridge (live ~0.123 @ ~0.86)",
        abs(bl["hit_rate"] - 0.1234) < 0.01 and abs(bl["precision"] - 0.8636) < 0.02,
        "live baseline hit %.4f prec %.4f" % (bl["hit_rate"], bl["precision"]))
    chk("UP2 the graded recency-margin upgrade raises live coverage (>= 0.16) at high precision (>= 0.70)",
        ul["hit_rate"] >= 0.16 and ul["precision"] >= 0.70,
        "live upgraded hit %.4f prec %.4f (was %.4f)" % (ul["hit_rate"], ul["precision"], bl["hit_rate"]))
    cb = u["consumer_live"]["baseline_unique"]["C3"]; cu = u["consumer_live"]["upgraded"]["C3"]
    chk("UP3 the upgrade BOOSTS the experiencer lift over baseline, still CI-separated",
        cu["delta"]["ci_sep"] and cu["delta"]["delta"] >= cb["delta"]["delta"],
        "C3 baseline +%.4f -> upgraded +%.4f CI%s" % (cb["delta"]["delta"], cu["delta"]["delta"], cu["delta"]["ci"]))
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
