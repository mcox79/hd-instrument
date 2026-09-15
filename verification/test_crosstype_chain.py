"""Scaffold-free witness: the FULL brain-foundational chain (parse->role->Cf-salience->cue-based retrieval) and
its measured DEPENDENCY on the upstream anaphoricity gate.

CH1 the UNIFIED cue-based ACT-R retrieval, dropped in UNGATED, OVER-MERGES: its entity-layer (C1) delta is WORSE
    (more negative) than the anaphoricity-GATED version -> the faithful retrieval cannot be installed without the
    upstream familiarity gate ("all the way up the chain").
CH2 the GATED cue-retrieval (the deployable, most-faithful config) is SAFE + net-positive: C1 not materially
    regressed (>= -0.003) AND the affect/goal experiencer consumer lifts CI-separated.

Re-derives live from experiments.exp_crosstype_upgrades_gum_v1._consumer_effect on GUM (live parse, 275 docs).
Run: .venv/Scripts/python.exe verification/test_crosstype_chain.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("PYTHONHASHSEED", "0")

import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
from experiments.exp_crosstype_upgrades_gum_v1 import _consumer_effect

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, name_gazetteer=gaz)
    ungated = _consumer_effect(docs, gaz, "cue_retrieval", 0.5, "live")
    gated = _consumer_effect(docs, gaz, "cue_gated", 0.5, "live")
    uc1 = ungated["C1"]["delta"]["delta"]; gc1 = gated["C1"]["delta"]["delta"]
    gc3 = gated["C3"]["delta"]
    chk("CH1 UNGATED cue-retrieval over-merges: its C1 delta is WORSE than the anaphoricity-GATED version",
        uc1 < gc1, "ungated C1 %+.4f vs gated C1 %+.4f" % (uc1, gc1))
    chk("CH2 the GATED cue-retrieval is SAFE (C1 >= -0.003) and lifts the experiencer CI-separated",
        gc1 >= -0.003 and gc3["ci_sep"] and gc3["delta"] > 0,
        "gated C1 %+.4f | C3 %+.4f CI%s" % (gc1, gc3["delta"], gc3["ci"]))
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
