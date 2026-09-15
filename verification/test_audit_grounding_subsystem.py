"""Pure-disk witness for `audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins`.

Reproduces the catalog's LIVE / live-but-inert / DORMANT classification by RE-RUNNING the runtime
import+call trace on the current hdlab bytes (not by reading a cached JSON), and checks the two landed
numbers the localization rests on. Scaffold-free: `.venv/Scripts/python.exe verification/test_audit_grounding_subsystem.py`.

Runtime ~3-5 min (the trace spawns 5 subprocess import-closures + a settrace pass over Substrate.read).
"""
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_audit_grounding_subsystem_v1 import run as trace_run

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ok  " if cond else "FAIL  ") + name + (("  -- " + detail) if detail else ""))
    return cond


def _load(path):
    with open(os.path.join(_REPO, path), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    print("== RE-DERIVING the live import+call closure from disk (this runs the grounding path) ==")
    r = trace_run(verbose=False)
    pr = r["probes"]
    cls = r["classification"]

    # W1 positive control -- the tracer fired and caught the known-live decision function
    ok("W1 tracer positive control (caught process_sentence)", r["positive_control_tracer_fired"])

    # W2-W5 the LIVE stand-ins are LIVE-CALLED on the default path
    ok("W2 G1 bag read-out canonicalize LIVE", pr["canonicalize_live"])
    ok("W3 G1 bag encoder + schema gate LIVE",
       pr["context_vector_live"] and pr["context_vector_masked_live"] and pr["schema_consistency_split_half_live"])
    ok("W4 C7 attractor-as-ranker chain LIVE (gap_detector->iterative_attractor)",
       pr["gap_detector_ca3_match_live"] and pr["iterative_attractor_live"])
    ok("W5 C8 hd_fact_store LIVE", pr["hd_fact_store_live"])

    # W6-W8 the located-negative fixes are DORMANT (not live defects)
    ok("W6 N1 structured encoder + parser assets DORMANT",
       pr["structural_encoder_dormant"] and pr["parser_assets_dormant"])
    ok("W7 N2 VWFA form-code DORMANT in the meaning path", pr["vwfa_form_code_dormant"])
    ok("W8 N3 orchestrators (three_tier / gap_driven_reader) DORMANT on the live read path",
       pr["three_tier_loop_dormant"] and pr["gap_driven_reader_dormant"])

    # W9 G2 -- the grounded input channel is imported but INERT (funcs=0)
    ok("W9 G2 grounded_similarity LIVE-IMPORTED-INERT (grounded input imported, never called)",
       cls.get("grounded_similarity", {}).get("class") == "LIVE-IMPORTED-INERT",
       "class=%s" % cls.get("grounded_similarity", {}).get("class"))

    # W10 the DORMANT-ISLANDED set is exactly the six orchestrator organs
    dormant = {m for m, i in cls.items() if i["class"] == "DORMANT-ISLANDED-ONLY"}
    expect = {"gap_driven_reader", "gather_reason", "kg_traversal", "prelim_tier",
              "script_grain_acquisition_loop", "three_tier_loop"}
    ok("W10 DORMANT-ISLANDED set == the six orchestrator organs", dormant == expect,
       "got %s" % sorted(dormant))

    # W11 the core grounding organs are LIVE-CALLED
    core = ["reading_grounding_loop", "grounding_acquisition_loop", "gap_detector", "cleanup_family",
            "iterative_attractor", "hd_fact_store", "definitional_extraction"]
    live_called = {m for m, i in cls.items() if i["class"] == "LIVE-CALLED"}
    ok("W11 core grounding organs LIVE-CALLED", all(m in live_called for m in core),
       "missing=%s" % [m for m in core if m not in live_called])

    # W12 landed: the #1 bag read-out LOSES to counting on the loop's OWN metric
    om = _load("data/exp_meaning_readout_own_metric_v1/metrics.json")["landed_reference"]
    sub = sum(om["SUBSTRATE"]) / len(om["SUBSTRATE"])
    cooc = sum(om["TOP_COOCCURRENT"]) / len(om["TOP_COOCCURRENT"])
    ok("W12 G1 bag read-out < counting on own metric (landed)", sub < cooc,
       "SUBSTRATE %.4f < TOP_COOC %.4f" % (sub, cooc))

    # W13-W14 the localization DISSOCIATION (from the drill's landed metrics.json)
    loc_path = os.path.join(_REPO, "data", "exp_ground_readout_localization_v1", "metrics.json")
    if os.path.exists(loc_path):
        loc = _load("data/exp_ground_readout_localization_v1/metrics.json")
        f = loc["flags"]
        ok("W13 dissociation confirmed (meaning_win + twin_loses + rel_no_win + own_no_win)",
           all([f["meaning_win_ci_sep"], f["twin_loses_ci_sep"],
                f["conceptual_no_win_on_relatedness"], f["conceptual_no_win_on_own_metric"]]))
        d = loc["dissociation"]
        ok("W14 brain-faithful ATL > co-occurrence on grounded MEANING (SimLex)",
           d["SimLex_MEANING_CONCEPTUAL_rho"] > d["SimLex_MEANING_ASSOC_rho"],
           "CONCEPTUAL %.3f > ASSOC %.3f" % (d["SimLex_MEANING_CONCEPTUAL_rho"],
                                             d["SimLex_MEANING_ASSOC_rho"]))
    else:
        FAIL.append("W13/W14 localization metrics.json missing -- run exp_ground_readout_localization_v1 --run")
        print("FAIL  W13/W14 localization metrics.json missing")

    # W15 the #1 FIX prototype: SENTENCE-bag grounding ties/loses counting (grounding the sentence bag alone
    # is not the lever), and the info-free twin is valid. The paradigmatic (dependency) grounded read-out
    # flips to the best arm -- see exp_grounded_meaning_readout_structured_v1 (parse-data-limited, not asserted here).
    fix_path = os.path.join(_REPO, "data", "exp_grounded_meaning_readout_v1", "metrics.json")
    if os.path.exists(fix_path):
        fx = _load("data/exp_grounded_meaning_readout_v1/metrics.json")["meaning"]
        gm = fx["SimLex_GROUNDED_CTX_rho"]; cm = fx["SimLex_COUNTING_rho"]; tw = fx["SimLex_TWIN_rho"]
        ok("W15 sentence-bag grounding ties/loses counting on meaning; twin valid (structured flips it best)",
           gm <= cm and tw < 0.05,
           "GROUNDED_CTX %.3f <= COUNTING %.3f ; TWIN %.3f (valid)" % (gm, cm, tw))
    else:
        print("  --  W15 fix-prototype metrics.json absent (optional); skipping")

    print("\n%d/%d PASS" % (len(PASS), len(PASS) + len(FAIL)))
    if FAIL:
        print("FAILURES:", FAIL)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
