"""Witness -- BAR #4 of the brief: feed the world-model's forward EXPECTATION top-down into who-did-what
extraction (the recurrent loop) and recover a two-valid case the feed-forward silo cannot. On the two-valid
ROLE_ERROR slice of UD-EWT (glass-box arc-eager parse -- NOT spaCy; the discourse-fixable slice the parser problem
named "routes to top-down expectation"). RIGOROUS LOCATED NEGATIVE (a full pass per the brief):
  (W1) the top-down expectation recovers SOME two-valid cases the silo gets wrong (the can-fail control fires).
  (W2) but it is NOT cleanly LOAD-BEARING -- it ties its SHUFFLED-expectation twin AND salience-only: the ~10%
       recovery is SALIENCE (position/givenness), NOT the generative verb->patient expectation (which adds ~1 case
       over the twin). The two-valid discriminator needs grounded STORY-SPECIFIC knowledge, not a generic
       expectation -- exactly the oracle-ceiling's 68% experience frontier, confirmed on the who-did-what consumer.
=> third independent solver-side lever (after path A 32% and the forward-model/meaning negatives) converging on
the SAME grounded-knowledge granularity wall; the ceiling-mover is the lifetime-learner program, not a cell.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_topdown_twovalid.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_topdown_twovalid_v1 as T


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = T.run(smoke=False)
    oks = []
    oks.append(check(
        "W1 the top-down expectation RECOVERS some two-valid cases the feed-forward silo gets wrong (can-fail "
        "control fires on the discourse-fixable ROLE_ERROR slice)",
        o["recovered_topdown"] > 0 and o["n_role_error_slice"] > 0,
        "recovered %d / %d role-error slice (rate %.3f CI%s)" % (
            o["recovered_topdown"], o["n_role_error_slice"], o["recovered_rate"], o["recovered_ci"])))
    oks.append(check(
        "W2 NOT cleanly LOAD-BEARING -- the generative verb->patient expectation ties its shuffle-twin AND "
        "salience-only: the recovery is SALIENCE, not the specific generative knowledge (the two-valid "
        "discriminator needs grounded story-specific knowledge = the oracle 68% frontier)",
        o["topdown_minus_twin"] < 0.05 and o["recovered_topdown"] <= o["recovered_salience_only"] + 1,
        "topdown %d (%.3f) vs shuffle-twin %d (%.3f) vs salience-only %d; topdown-twin %+.4f" % (
            o["recovered_topdown"], o["recovered_rate"], o["recovered_shuffle_twin"], o["twin_rate"],
            o["recovered_salience_only"], o["topdown_minus_twin"])))
    oks.append(check(
        "W3 verdict = recovers-some-not-load-bearing -> the residual is grounded story-specific knowledge (the "
        "lifetime-learner frontier), converging with path A (32%) and the forward-model/meaning negatives",
        o["verdict"] in ("BAR4_TOPDOWN_RECOVERS_SOME_NOT_CLEANLY_LOAD_BEARING",
                         "BAR4_TOPDOWN_NO_RECOVERY_RESIDUAL_IS_GROUNDED_KNOWLEDGE"),
        o["verdict"]))
    n = sum(oks)
    print("=" * 100)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 100)
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
