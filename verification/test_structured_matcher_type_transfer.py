"""Scaffold-free witness: the SAME structured organ TRANSFERS to the SPATIAL type consumer (type-membership).

TT1 STRUCTURED beats the hub baseline CI-separated on type-membership (is a kitchen a room?).
TT2 STRUCTURED beats the shuffled-KB twin CI-separated.
TT3 the organ gets BOTH slices: is-a positives AND co-hyponym negatives (the structured NOT-a-kind-of edge) --
    proving it is the shared SHAPE, not an OCC-only patch.

Re-derives live from experiments.exp_structured_matcher_type_transfer_v1.run(). Requires nltk WordNet + ConceptNet + hub.
Run: .venv/Scripts/python.exe verification/test_structured_matcher_type_transfer.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401  (pins PYTHONHASHSEED=0 -> reproducible WordNet/ConceptNet sampling)

from experiments.exp_structured_matcher_type_transfer_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = run()
    chk("TT1 structured beats hub baseline CI-separated (type-membership transfer)",
        r["margins"]["vs_hub"]["ci_sep"] and r["margins"]["vs_hub"]["delta"] > 0.2,
        "structured %.4f vs hub %.4f  +%.4f CI%s" % (r["acc"]["structured"], r["acc"]["hub_baseline"],
                                                     r["margins"]["vs_hub"]["delta"], r["margins"]["vs_hub"]["ci"]))
    chk("TT2 structured beats shuffled-KB twin CI-separated",
        r["margins"]["vs_twin"]["ci_sep"] and r["margins"]["vs_twin"]["delta"] > 0.2,
        "twin %.4f  +%.4f CI%s" % (r["acc"]["twin"], r["margins"]["vs_twin"]["delta"], r["margins"]["vs_twin"]["ci"]))
    isa, coh = r["by_slice"]["is_a"], r["by_slice"]["cohyponym_not_isa"]
    chk("TT3 organ gets BOTH is-a positives AND co-hyponym negatives (shared shape)",
        isa["structured"] >= 0.85 and coh["structured"] >= 0.75 and coh["structured"] > coh["hub_baseline"],
        "is-a %.3f | cohyponym-not-isa structured %.3f vs hub %.3f" % (
            isa["structured"], coh["structured"], coh["hub_baseline"]))
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
