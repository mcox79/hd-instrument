"""Scaffold-free witness: the NEGATION operator on MoNLI (well-powered modern gold).

  M1 detection: the operator reads the negation context (positive vs negated) with high accuracy.
  M2 LOAD-BEARING on the negated subset: on NMoNLI the operator beats the POLARITY-BLIND floor CI-separated
     -- and the blind floor is CATASTROPHICALLY wrong (it INVERTS the monotonicity direction), the exact
     positive control the bar asks for (polarity-respecting answer OPPOSITE the polarity-blind one).
  M3 NO regression on positive: on PMoNLI the operator == the blind floor (it only fires where negation bites).
  M4 the info-free shuffled-polarity TWIN loses CI-separated (beats its own null p95) on the pooled set.

Requires data/corpora/monli (fetch: experiments/fetch_negation_quantifier_gold_v1.py --fetch).
Re-derives live from experiments.exp_polarity_operator_monli_v1.
Run: .venv/Scripts/python.exe verification/test_polarity_operator_monli.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_polarity_operator_monli_v1 import run, MONLI_DIR

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    if not os.path.isdir(MONLI_DIR):
        print("  SKIP: MoNLI not fetched", flush=True)
        return 0
    out = run()
    r = out["populations"]
    nm, pm = r["NMoNLI_negated"], r["PMoNLI_positive"]
    chk("M1 polarity detection accuracy >= 0.95", r["polarity_detection_accuracy"] >= 0.95,
        "detect=%.4f" % r["polarity_detection_accuracy"])
    chk("M2 NMoNLI: operator beats polarity-blind CI-sep AND blind inverts (<0.10)",
        nm["operator_minus_blind"]["ci_sep"] and nm["acc"]["operator"] > 0.9 and nm["acc"]["blind_floor"] < 0.10,
        "op %.4f vs blind %.4f (+%.4f CI%s)" % (nm["acc"]["operator"], nm["acc"]["blind_floor"],
                                                nm["operator_minus_blind"]["delta"], nm["operator_minus_blind"]["ci"]))
    chk("M3 PMoNLI: operator == blind (no regression on positive items)",
        abs(pm["acc"]["operator"] - pm["acc"]["blind_floor"]) < 1e-9,
        "op %.4f blind %.4f" % (pm["acc"]["operator"], pm["acc"]["blind_floor"]))
    chk("M4 shuffled-polarity twin loses CI-sep (beats null p95) on both populations",
        nm["operator_minus_twin"]["beats_twin"] and pm["operator_minus_twin"]["beats_twin"],
        "NMoNLI +%.4f>null %.4f ; PMoNLI +%.4f>null %.4f" % (
            nm["operator_minus_twin"]["delta"], nm["operator_minus_twin"]["null_p95"],
            pm["operator_minus_twin"]["delta"], pm["operator_minus_twin"]["null_p95"]))
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
