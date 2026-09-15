"""Scaffold-free witness: the PROVEN brain mechanism (the landed ACT-R graded cue-based retrieval)
LIFTS the LIVE reader's pooled pronoun coref when wired into the deployment path -- the "landed is
not live" gap for strengthen_the_cue_based_pronoun_coreference_resolver_the_shared_upstream_accuracy_cap.

  W1  FLOOR_deployed reproduces the KNOWN live deployment floor (pooled he/she coref_acc ~= 0.469,
      the exp_referent_coref_linking_v1 number) -- so the comparison is against the REAL live reader.
  W2  the graded ACT-R pick (landed hdlab.graded_coref_pick) beats the deployed pick CI-separated on
      the LIVE pooled instrument AND beats the info-free twin p95.
  W3  the info-free shuffled-history twin LOSES (well below the floor).
  W4  NO-REGRESS on named-antecedent coref (named slice does not drop -- it rises).
  W5  the binding cue is RECENCY: recency-only also clears CI-separated, and the deployed rolemass
      pick (NO recency term) + the event-centrality override are BELOW plain recency -- the mechanistic cap.

Reads data/exp_coref_graded_live_transfer_v1/metrics_full.json.
Run: .venv/Scripts/python.exe verification/test_coref_graded_live_transfer.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
METRICS = os.path.join(_REPO, "data", "exp_coref_graded_live_transfer_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = json.load(open(METRICS))["result"]
    arms = r["arms"]; dv = r["deltas_vs_floor"]
    floor = r["FLOOR_deployed"]
    chk("W1 FLOOR_deployed reproduces the known live deployment floor (~0.469 pooled he/she coref_acc)",
        abs(floor - 0.469) <= 0.01 and r["n_targets"] >= 5000,
        "floor=%.4f n=%d docs=%d" % (floor, r["n_targets"], r["n_docs"]))
    g = dv["GRADED"]
    chk("W2 graded ACT-R pick beats the deployed pick CI-separated AND beats the twin p95",
        g["ci_sep_above"] and g["lo"] > 0 and g["beats_twin_p95"],
        "graded %.4f delta %+.4f ci[%.4f,%.4f] twin_p95 %.4f" % (
            arms["GRADED"]["acc"], g["delta"], g["lo"], g["hi"], r["twin_null_p95"]))
    chk("W3 info-free shuffled-history twin LOSES (well below the floor)",
        r["twin_acc"] < floor - 0.10,
        "twin %.4f vs floor %.4f" % (r["twin_acc"], floor))
    chk("W4 NO-REGRESS on named-antecedent coref (named slice does not drop)",
        arms["GRADED"]["named_acc"] >= arms["FLOOR_deployed"]["named_acc"] - 0.005,
        "named: floor %.4f -> graded %.4f" % (arms["FLOOR_deployed"]["named_acc"], arms["GRADED"]["named_acc"]))
    chk("W5 the lever is RECENCY: recency-only clears CI-sep and the deployed rolemass/EC pick is BELOW it",
        dv["abl_RECENCY_only"]["ci_sep_above"] and arms["FLOOR_deployed"]["acc"] < arms["abl_RECENCY_only"]["acc"] - 0.10
        and arms["FLOOR_rolemass"]["acc"] < arms["abl_RECENCY_only"]["acc"],
        "recency_only %.4f | deployed(rolemass+EC) %.4f | rolemass-noEC %.4f" % (
            arms["abl_RECENCY_only"]["acc"], arms["FLOOR_deployed"]["acc"], arms["FLOOR_rolemass"]["acc"]))
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
