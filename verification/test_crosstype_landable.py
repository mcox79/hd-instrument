"""Scaffold-free witness: the constructive cross-type bridge is LANDABLE-GRADE (both gaps closed).

LV1 LIVE PARSE -- on the reader's OWN glass-box parser (arc-eager heads + arc-labeler deprels, NOT gold UD), the
    bridge holds high precision (>= 0.80) and a real slice (>= 0.09), degraded but net-positive vs the gold ceiling.
LV2 DOWNSTREAM CONSUMER LIFT -- the live-parse bridge lifts the affect/goal EXPERIENCER consumer CI-separated over
    the situation_predict floor (delta > 0, CI excludes 0), and the entity-KB hard-link is up-or-flat.
LV3 INFO-FREE TWIN LOSES -- the same #merges bound to RANDOM named entities do NOT reproduce the lift; the bridge
    beats the twin CI-separated on the experiencer consumer -> the CORRECT cross-type targeting is load-bearing.

Re-derives live from experiments.exp_crosstype_landable_validation_gum_v1.run() on GUM.
Run: .venv/Scripts/python.exe verification/test_crosstype_landable.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("PYTHONHASHSEED", "0")

import experiments.exp_crosstype_landable_validation_gum_v1 as LV

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = LV.run(verbose=False)
    lv = r["GAP1_live_parse"]; gd = r["GAP1_gold_parse"]
    chk("LV1 the bridge SURVIVES the live parser (precision >= 0.80, coverage >= 0.09)",
        lv["precision"] >= 0.80 and lv["hit_rate"] >= 0.09,
        "live hit %.3f prec %.3f (gold ceiling %.3f/%.3f)" % (lv["hit_rate"], lv["precision"],
                                                              gd["hit_rate"], gd["precision"]))
    c3 = r["GAP2_consumers"]["C3_experiencer"]; c2 = r["GAP2_consumers"]["C2_hardlink"]
    chk("LV2 the live-parse bridge LIFTS the experiencer consumer CI-separated over the floor",
        c3["delta"]["ci_sep"] and c3["delta"]["delta"] > 0,
        "C3 floor %.4f -> bridge %.4f delta %+.4f CI%s" % (c3["floor"], c3["bridge"],
                                                           c3["delta"]["delta"], c3["delta"]["ci"]))
    chk("LV2b the entity-KB hard-link is up-or-flat (delta >= 0)",
        c2["delta"]["delta"] >= 0, "C2 delta %+.4f" % c2["delta"]["delta"])
    chk("LV3 the INFO-FREE TWIN (random targeting) LOSES -- bridge beats twin CI-sep on the experiencer",
        c3["bridge_vs_twin"]["ci_sep"] and c3["bridge_vs_twin"]["delta"] > 0,
        "C3 bridge-vs-twin delta %+.4f CI%s (twin %.4f)" % (c3["bridge_vs_twin"]["delta"],
                                                            c3["bridge_vs_twin"]["ci"], c3["twin"]))
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
