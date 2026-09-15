"""Scaffold-free witness: the implemented UPGRADES (P1 wired-reader landing prototype, P2 unified state_match
query, P4 scanner consolidation).

  U1 (P1) WIRED landing prototype: WiredPolarityReader is ADDITIVE + default-off byte-identical, attaches the
     polarity/quantity field on, and a DOWNSTREAM factuality-QA off the field beats the polarity-blind reading.
  U2 (P2) UNIFIED query: proposition_answer routes event polarity through hdlab.state_register.state_match --
     the SAME primitive as copular-state queries ('did she take?' and 'is she ill?' share one representation).
  U3 (P4) CONSOLIDATION: the operator matches the owned hdlab scanners on direct cases (3-way agreement 1.0) and
     STRICTLY subsumes them on extended cases (operator 1.0 vs each scanner < 1.0).

Re-derives live from experiments.exp_polarity_wired_reader_v1 + _polarity_operator + exp_negation_scanner_consolidation_v1.
Run: .venv/Scripts/python.exe verification/test_polarity_operator_upgrades.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_polarity_wired_reader_v1 import run as run_wired
from experiments.exp_negation_scanner_consolidation_v1 import run as run_cons
from experiments._polarity_operator import proposition_answer

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    w = run_wired()
    chk("U1 (P1) wired reader ADDITIVE + default-off byte-identical + downstream QA beats blind",
        w["W1_byte_identical_core_fields"] and w["W1_off_attaches_no_field"] and w["W2_on_attaches_field"]
        and w["W3_downstream_qa"]["polarity_aware_acc"] > w["W3_downstream_qa"]["polarity_blind_acc"],
        "aware %.2f vs blind %.2f, byte-identical=%s" % (
            w["W3_downstream_qa"]["polarity_aware_acc"], w["W3_downstream_qa"]["polarity_blind_acc"],
            w["W1_byte_identical_core_fields"]))

    # U2: unified state_match path -- event polarity answers through the copular-state primitive
    yes = proposition_answer("She took the key .".split(), 1, "take", "take")
    no = proposition_answer("She did not take the key .".split(), 3, "take", "take")
    imp = proposition_answer("He did not manage to escape .".split(), 5, "escape", "escape",
                             verb_lows={"manage", "escape"})
    chk("U2 (P2) unified query via state_register.state_match (YES/NO/implicative-NO)",
        yes == "YES" and no == "NO" and imp == "NO", "took=%s notake=%s escape=%s" % (yes, no, imp))

    c = run_cons()
    chk("U3 (P4) operator subsumes scattered scanners (direct agreement 1.0; extended op 1.0 > each scanner)",
        c["direct_three_way_agreement"] == 1.0 and c["extended_operator_accuracy"] == 1.0
        and c["extended_goal_typing_accuracy"] < 1.0 and c["extended_def_pred_accuracy"] < 1.0,
        "direct 3-way %.2f | extended op %.2f gt %.2f dp %.2f" % (
            c["direct_three_way_agreement"], c["extended_operator_accuracy"],
            c["extended_goal_typing_accuracy"], c["extended_def_pred_accuracy"]))
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
