"""Scaffold-free witness: the common-noun located negative, understood to 100% brain-foundational -- a MIXED wall
(a small glass-box FIDELITY GAP, now built; the bulk a GENUINE no-LLM world-knowledge LIMIT, quantified).

  W1  DECOMPOSITION: the majority of anaphoric common-noun mentions are SAME-HEAD -> blind head-identity is the
      ceiling, which is why the salience/gender unification cannot beat it there.
  W2  name_bridge (common->named-entity) coverage: a GLASS-BOX bridge (text-stated is-a via apposition/copula
      [Heim file-card familiarity; Stanford Precise-Constructs sieve] PLUS head-in-name string containment
      "American College of Pediatricians"->"the college") recovers a MINORITY; the MAJORITY needs WORLD KNOWLEDGE
      (Argentina->"the country", Frontiers->"the publisher") the discourse never states -> no-LLM barred.
  W3  the glass-box bridge gives only a SMALL CI-separated lift on common-noun resolution (the bulk is
      world-knowledge) -> the located negative is a genuine, quantified limit, not an implementation miss.
      (register note: on biography/news the appositive convention is stronger -- lit estimate 65-80%; GUM's
      academic-heavy multi-genre mix carries it weakly, exactly the research's <20% HARD-FAIL boundary.)

Reads data/exp_commonnoun_wall_gum_v1/metrics_full.json.
Run: .venv/Scripts/python.exe verification/test_commonnoun_wall.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
M = os.path.join(_REPO, "data", "exp_commonnoun_wall_gum_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = json.load(open(M))["result"]
    d = r["diagnostic"]
    chk("W1 majority of anaphoric common-noun mentions are SAME-HEAD (blind head-identity is the ceiling)",
        d["same_head_frac"] > 0.55,
        "same_head %.3f / name_bridge %.3f / variant %.3f (n=%d)" % (
            d["same_head_frac"], d["name_bridge_frac"], d["variant_frac"], d["n_anaphoric_common"]))
    chk("W2 name_bridge is mostly WORLD KNOWLEDGE: glass-box (appos/copula+head-in-name) recovers a minority",
        d["cov_world_knowledge_frac"] > 0.5 and d["cov_either_frac"] < 0.5,
        "glass-box %.3f (appos %.3f + head-in-name %.3f) vs world-knowledge %.3f" % (
            d["cov_either_frac"], d["cov_appos_frac"], d["cov_headname_frac"], d["cov_world_knowledge_frac"]))
    chk("W3 the glass-box bridge gives only a SMALL CI-sep lift (bulk is world-knowledge -> genuine no-LLM limit)",
        r["CIsep"] and r["bridge_minus_blind"] < 0.03,
        "blind %.4f -> +glass-box bridge %.4f (%+.4f ci%s)" % (
            r["common_blind"], r["common_bridge"], r["bridge_minus_blind"], r["ci"]))
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
