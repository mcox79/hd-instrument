"""Scaffold-free witness: the QUANTITY/SCOPE operator (reader-native HEADLINE + MED companion).

  Q1 reader-native quantifier QA: the cardinality operator beats the QUANTITY-BLIND floor (every fact stored
     positive+singular) CI-separated, over sm.events (reader verb-extraction 1.0).
  Q2 the positive control: on the specific-EXCEPTION items ('everyone but Mary -> did Mary?') the blind floor
     is 0.0 (it says yes to everyone) and the operator is 1.0 -- the cardinality answer is the OPPOSITE.
  Q3 the info-free shuffled-determiner TWIN loses (beats null p95).
  Q4 MED (well-powered naturalistic companion): on the DOWNWARD-monotone subset (no/few/every-restrictor) the
     quantifier operator beats the monotone-blind floor CI-separated, and the blind floor INVERTS (<0.30).

Requires data/corpora/med for Q4 (fetch: experiments/fetch_negation_quantifier_gold_v1.py --fetch).
Re-derives live from experiments.exp_quantifier_operator_v1 + _med_v1.
Run: .venv/Scripts/python.exe verification/test_quantifier_operator.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_quantifier_operator_v1 import run as run_native

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    out = run_native()
    chk("Q1 reader-native: cardinality operator beats quantity-blind CI-sep (verb-extraction 1.0)",
        out["operator_minus_blind"]["ci_sep"] and out["acc"]["operator"] > 0.9
        and out["reader_verb_extraction_rate"] >= 0.99,
        "op %.4f vs blind %.4f (+%.4f CI%s)" % (out["acc"]["operator"], out["acc"]["quantity_blind"],
                                                out["operator_minus_blind"]["delta"], out["operator_minus_blind"]["ci"]))
    exc = out["by_question_type"].get("specific_exception", {})
    chk("Q2 positive control: 'everyone but X -> did X?' blind 0.0, operator 1.0 (opposite answer)",
        exc.get("operator", 0) > 0.99 and exc.get("blind", 1) < 0.01,
        "operator %.4f blind %.4f n=%d" % (exc.get("operator", -1), exc.get("blind", -1), exc.get("n", 0)))
    chk("Q3 info-free shuffled-determiner twin loses (beats null p95)",
        out["operator_minus_twin"]["beats_twin"],
        "op-twin +%.4f > null_p95 %.4f" % (out["operator_minus_twin"]["delta"], out["operator_minus_twin"]["null_p95"]))

    from experiments.exp_quantifier_operator_med_v1 import run as run_med, MED_PATH
    if os.path.exists(MED_PATH):
        m = run_med()
        d = m["operator_minus_blind_DOWNWARD"]
        chk("Q4 MED downward-monotone: quantifier operator beats monotone-blind CI-sep (blind inverts <0.30)",
            d["ci_sep"] and m["acc_downward"]["operator"] > 0.7 and m["acc_downward"]["monotone_blind"] < 0.30,
            "op %.4f vs blind %.4f (+%.4f CI%s) cover %.3f" % (
                m["acc_downward"]["operator"], m["acc_downward"]["monotone_blind"], d["delta"], d["ci"],
                m["coverage"]))
        npi = m["npi_upgrade"]
        chk("Q5 UPGRADE B (NPI/negation licensing): NPI subset recovered + full-operator coverage & accuracy up",
            npi["npi_operator_full"] > npi["npi_operator_base"] + 0.2
            and npi["full_operator_coverage"] > m["coverage"]
            and npi["full_operator_acc_all"] > m["acc_all"]["operator"] + 0.1,
            "NPI %.4f->%.4f | full-op cover %.3f (was %.3f) acc %.4f (was %.4f)" % (
                npi["npi_operator_base"], npi["npi_operator_full"], npi["full_operator_coverage"],
                m["coverage"], npi["full_operator_acc_all"], m["acc_all"]["operator"]))
        u = m["restrictor_upgrade_universal_subset"]
        chk("Q6 UPGRADE C (restrictor monotonicity): every/all restrictor edits lift the universal subset",
            u["lift"] > 0, "universal subset %.4f -> %.4f (+%.4f)" % (
                u["operator_base"], u["operator_restrictor_aware"], u["lift"]))
        fb, ft = m["full_operator_vs_blind_ALL"], m["full_operator_vs_twin_ALL"]
        chk("Q7 FULL unified operator: well-powered aggregate CI-sep over blind AND info-free twin",
            fb["ci_sep"] and fb["delta"] > 0.4 and ft["ci_sep"],
            "n=%d | vs blind %.4f vs %.4f (+%.4f CI%s) | vs twin +%.4f CI%s" % (
                fb["n"], fb["a"], fb["b"], fb["delta"], fb["ci"], ft["delta"], ft["ci"]))
    else:
        print("  SKIP Q4-Q7: MED not fetched", flush=True)

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
