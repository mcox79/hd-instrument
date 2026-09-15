"""Scaffold-free witness: fixing the ROOT upstream deviation (entity FRAGMENTATION) with a glass-box,
deployable name-aliaser is a SECOND brain-foundational win that composes with the pick.

  W1  glass-box name-aliasing (hdlab.build_merge_map, NO gold) lifts the graded pick CI-separated on the
      LIVE pooled coref, the shuffled-alias twin LOSES, and named coref does NOT regress.
  W2  the deployable brain-foundational stack (graded PICK + glass-box UNIFICATION) reaches ~0.62 live,
      +~0.15 over the deployed floor (0.4693) -- two composed glass-box wins.
  W3  recall-safe agreement + incremental gender REGRESS even on the ORACLE-unified pool -- a located
      negative (deployable-gender bootstrapping wall); the +0.28 gender CEILING is the follow-on prize.

Reads data/exp_coref_graded_unification_v1/metrics_full.json (+ the anatomy for the gender ceiling).
Run: .venv/Scripts/python.exe verification/test_coref_graded_unification.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
U = os.path.join(_REPO, "data", "exp_coref_graded_unification_v1", "metrics_full.json")
AN = os.path.join(_REPO, "data", "exp_coref_graded_residual_anatomy_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = json.load(open(U))["result"]
    A = r["arms"]; D = r["deltas"]
    gb = D["+glassbox_alias"]
    chk("W1 glass-box name-aliasing lifts the graded pick CI-sep; shuffled-alias twin LOSES; named no-regress",
        gb["CIsep"] and gb["ci"][0] > 0
        and A["twin (shuffled alias)"]["acc"] < A["GRADED (fragmented)"]["acc"] - 0.03
        and A["+glassbox_alias"]["named_acc"] >= A["GRADED (fragmented)"]["named_acc"] - 0.005,
        "graded %.4f -> +alias %.4f (%+.4f ci%s) | twin %.4f | named %.4f->%.4f" % (
            A["GRADED (fragmented)"]["acc"], A["+glassbox_alias"]["acc"], gb["delta"], gb["ci"],
            A["twin (shuffled alias)"]["acc"], A["GRADED (fragmented)"]["named_acc"], A["+glassbox_alias"]["named_acc"]))
    chk("W2 deployable stack (PICK + glass-box UNIFICATION) reaches ~0.62 live, +~0.15 over the 0.4693 floor",
        A["+glassbox_alias"]["acc"] >= 0.615 and A["+glassbox_alias"]["acc"] - 0.4693 >= 0.14,
        "deployed 0.4693 -> pick+unify %.4f (+%.4f)" % (A["+glassbox_alias"]["acc"], A["+glassbox_alias"]["acc"] - 0.4693))
    an = json.load(open(AN))["result"]
    gender_ceiling = an["acc"]["name+prior_pron"] - an["acc"]["name_only"]
    chk("W3 gender/recall-safe REGRESS even on the oracle-unified pool (bootstrapping wall); the +0.28 gender CEILING is the prize",
        D["+glassbox_alias+RS+gender"]["delta"] < 0 and D["+oracle_key+RS+gender"]["delta"] < 0 and gender_ceiling > 0.25,
        "live +alias+RS+gender %+.4f | +oracle+RS+gender %+.4f | cache gender ceiling +%.4f" % (
            D["+glassbox_alias+RS+gender"]["delta"], D["+oracle_key+RS+gender"]["delta"], gender_ceiling))
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
