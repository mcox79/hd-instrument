"""Scaffold-free witness for validate_the_ppmi_svd_means_end_bridge_on_real_narrative_marker_less_goal_attachment.

The headline is a LOCATED result: the marker-less goal-attachment wall is an UPSTREAM PARSE gap, and the
means-end bridge's signal separates from the info-free twin ONLY when the upstream is brain-foundational.

  W1  the glass-box upstream purpose-vs-complement fix IMPROVES extraction precision (0.27 -> higher)
  W2  THE LOCATED NEGATIVE (robust): the info-free shuffled-map TWIN does NOT lose on real narrative
      purposes -- NOT on contaminated raw extractions AND NOT on upstream-CLEAN (advcl) purposes. The
      bridge's apparent discrimination is a goal-frequency artifact the twin reproduces. (Cleaning the
      upstream LIFTS absolute accuracy -- CLEAN raw > CONTAMINATED raw -- so the parse matters, but it
      does not rescue the context-free means-end bridge.)
  W3  from-source units (spaCy-free): glass-box keep_purpose rejects 'had to' + keeps 'went..to';
      ATL backoff covers a verb absent from ATOMIC ('entreat'); means-end fit cook->eat > cook->sleep
  W4  NO-REGRESS: the gated inverse-planning attachment leaves the explicit-chain arm byte-identical

Reads the landed metrics (data/exp_meansend_realtext_validate_v1/metrics_full.json) + a from-source unit.
Run: .venv/Scripts/python.exe verification/test_meansend_realtext_validate.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

METRICS = os.path.join(_REPO, "data", "exp_meansend_realtext_validate_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = json.load(open(METRICS))["result"]
    a1 = r["ARM1_upstream_purpose_precision"]
    a2 = r["ARM2_chain_thesis"]
    a4 = r["ARM4_no_regress"]

    chk("W1 glass-box upstream purpose precision improves over the raw extractor",
        a1["precision_after"] > a1["precision_before"],
        "precision %.3f -> %.3f (recall %.2f)" % (a1["precision_before"], a1["precision_after"],
                                                  a1["genuine_recall_after"]))

    clean = a2["CLEAN_advcl"]["K1"]
    cont = a2["CONTAMINATED_all"]["K1"]
    chk("W2a LOCATED NEGATIVE: the info-free twin does NOT lose on CONTAMINATED real extractions (K1)",
        not cont["beats_twin_ci_sep"],
        "contaminated full %.3f ci_lo %.3f vs twin p95 %.3f" % (
            cont["full_stack"]["acc"], cont["full_stack"]["ci"][0], cont["twin_null"]["p95"]))
    chk("W2b LOCATED NEGATIVE holds even on upstream-CLEAN (advcl) purposes -> not a mere parse artifact",
        not clean["beats_twin_ci_sep"],
        "clean full %.3f ci_lo %.3f vs twin p95 %.3f" % (
            clean["full_stack"]["acc"], clean["full_stack"]["ci"][0], clean["twin_null"]["p95"]))
    chk("W2c cleaning the upstream LIFTS absolute accuracy (CLEAN raw > CONTAMINATED raw) -> the parse matters",
        clean["raw_bridge_acc"] > cont["raw_bridge_acc"],
        "CLEAN raw %.3f > CONTAMINATED raw %.3f" % (clean["raw_bridge_acc"], cont["raw_bridge_acc"]))

    # W3 from-source units (spaCy-free)
    import experiments.exp_meansend_realtext_validate_v1 as T
    import experiments.exp_goal_hierarchy_markerless_bridge_v1 as PoC
    chk("W3a glass-box keep_purpose rejects 'had to' (obligation modal, not a purpose)",
        T.keep_purpose({"source_verb": "had", "verb_tok": 2, "to_tok": 3}) is False)
    chk("W3b glass-box keep_purpose keeps 'went ... to' (motion + intervening = purpose adjunct)",
        T.keep_purpose({"source_verb": "went", "verb_tok": 2, "to_tok": 5}) is True)
    idx = PoC.load_atomic_index()
    meb = T.MeansEndBridge(idx)
    chk("W3c ATL backoff covers a verb ABSENT from ATOMIC ('entreat') via WordNet neighbours",
        meb.covered_any("entreat") and not meb.covered_direct("entreat"))
    chk("W3d means-end fit cook->eat > cook->sleep (bridge sanity)",
        meb.fit("cook", "eat") > meb.fit("cook", "sleep"))

    chk("W4 NO-REGRESS: gated attachment leaves connected-node chains byte-identical",
        a4["byte_identical"],
        "connected %d identical %d" % (a4["connected_nodes"], a4["identical"]))

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
