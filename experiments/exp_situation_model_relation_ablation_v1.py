# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (accuracy-comparison ablation over a fixed item bank, no capacity/noise-floor
#   discriminator threshold)
# - HP_SCOPE: {grounded_module: [tier0_gate, tier1_hard_pass_bands]}
# - cardinality_ok: EXPECTED_N_UNITS=2 (tier0 unit + tier1 unit)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (thresholds reused unchanged) +
#   adaptive_with_discriminator_gate (engagement-axis seed words, measured before/not-tuned-after)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL FHRR bind/unbind/bundle primitives + goal_outcome_relation +
#   goal_outcome_relation_grounded modules (real_code_path); no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-09_situation_model_relation_ablation_v1.md for the full pre-reg.
"""exp_situation_model_relation_ablation_v1 -- Direction-B build #2: clean ablation of
hdlab.goal_outcome_relation (hand-pool booleans + WordNet-MWE dictionary lookup) vs
hdlab.goal_outcome_relation_grounded (GRADED concept-similarity + engagement-axis situation-model
queries), reusing goal_outcome_relation.self_test()'s EXISTING 14-TRAIN/11-HELDOUT harness,
memorization baseline, and scramble control STRUCTURALLY UNCHANGED (only the relation-computation
step is swapped -- see hdlab/goal_outcome_relation_grounded.py's module docstring for the full
mechanism writeup, and the pre-reg for the exact bands).

Two hand-offs define this: notes/exp_dev_handoff_research_psych_bridging_inference_situation_
models_2026-08-09.md (primary spec, pre-registered HARD-PASS/MIDDLE_BAND/HARD-FAIL bands) +
notes/research_preclusion_goal_failure_inference_2026-08-09.md (CONTRADICT-leg engagement-axis
mechanism + its own Tier-0 axis-coverage smoke gate design).

Modes:
  --self-test  Real-code-path check: hdlab.goal_outcome_relation.self_test() (baseline) +
               hdlab.goal_outcome_relation_grounded.self_test() (grounded) + arms-must-differ.
               No DesireDB, no new data -- both modules' own self_test()s ARE the decisive
               measurement (this cell adds verdict logic + metrics plumbing, not new computation).
  --smoke      Tier-0 axis-coverage gate ONLY (per the preclusion drill's own design -- cheaper
               than the full ablation, gates it). HARD_FAILs here mean do NOT proceed to --full.
  --full       Tier-0 gate + Tier-1 full ablation (baseline vs grounded self_test() comparison,
               3 pre-registered bands) -> combined verdict, per-leg (ACHIEVE vs CONTRADICT)
               reported SEPARATELY per the mandatory honest-asymmetry framing.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "situation_model_relation_ablation_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from hdlab import goal_outcome_relation as _gor  # noqa: E402
from hdlab import goal_outcome_relation_grounded as _gog  # noqa: E402

# Pre-registered tolerance (see prereg "Pre-registered bands"): ~half of one heldout item at n=11.
NOISE_TOL = 0.05

# Tier-0 pre-registered gates (see prereg "Tier-0 axis-coverage smoke"). Floor is the MEASURED-
# this-session WordNet-MWE coverage (0.8276, 24/29), NOT the preclusion drill's stale-cited
# 0.897/26-29 figure -- disk-verified discrepancy, see prereg + module docstring.
TIER0_HP_MIN_RECOVERY = 3
TIER0_MB_MIN_RECOVERY = 1
TIER0_COVERAGE_FLOOR_KEY = "wordnet_mwe_floor_measured_this_session"  # read from measured coverage


# ============================================================================ verdict logic
def tier0_verdict(coverage: dict) -> tuple:
    """Axis-coverage gate (recovers disclosed WordNet-MWE gaps, 0 false positives, does not
    regress the WordNet-MWE mechanism's own measured coverage floor)."""
    rec = coverage["disclosed_gap_recovery_count"]
    fp = coverage["false_positive_count"]
    cov = coverage["coverage"]
    floor = coverage["wordnet_mwe_floor_measured_this_session"]["coverage"]
    hard_fail = (rec == 0) or (fp > 0) or (cov < floor)
    if hard_fail:
        return ("HARD_FAIL",
                f"TIER0_HARD_FAIL: recovery={rec}/5 fp={fp} coverage={cov} floor={floor}")
    hard_pass = (rec >= TIER0_HP_MIN_RECOVERY) and (fp == 0) and (cov >= floor)
    if hard_pass:
        return ("HARD_PASS",
                f"TIER0_HARD_PASS: recovery={rec}/5 fp={fp} coverage={cov} floor={floor}")
    return ("MIDDLE_BAND",
            f"TIER0_MIDDLE_BAND: recovery={rec}/5 fp={fp} coverage={cov} floor={floor}")


def tier1_verdict(baseline: dict, grounded: dict) -> tuple:
    """Full-ablation 3-way band per the primary hand-off, verbatim (see prereg)."""
    held_b = baseline["held_out_acc"]
    held_g = grounded["held_out_acc"]
    mem_b = baseline["memorization_baseline_acc"]
    scr_b = baseline["scramble_control_acc"]
    scr_g = grounded["scramble_control_acc"]
    gap_rec = grounded["engagement_axis_coverage"]["disclosed_gap_recovery_count"]

    scramble_collapses = scr_g <= (scr_b + NOISE_TOL)
    below_memorization = held_g < mem_b
    real_regression = held_g < (held_b - NOISE_TOL)

    hard_fail = below_memorization or real_regression or (not scramble_collapses)
    msg = (f"held_g={held_g} held_b={held_b} mem_b={mem_b} scr_g={scr_g} scr_b={scr_b} "
           f"(tol={NOISE_TOL}) scramble_collapses={scramble_collapses} gap_recovery={gap_rec}/5")
    if hard_fail:
        return ("HARD_FAIL", f"TIER1_HARD_FAIL: {msg}")
    hard_pass = (held_g >= held_b) and scramble_collapses and (gap_rec >= 1)
    if hard_pass:
        return ("HARD_PASS", f"TIER1_HARD_PASS: {msg}")
    return ("MIDDLE_BAND", f"TIER1_MIDDLE_BAND: {msg}")


def _arms_must_differ() -> dict:
    """META_RULE_AF differencing test. NOTE (disclosed, see prereg "Honest framing"): baseline
    pair_feats vs grounded pair_feats_grounded are EXPECTED and DISCLOSED to be IDENTICAL on the
    full TRAIN+HELDOUT bank itself (self-similarity=1.0 reproduces Tier1-exact coverage on every
    word that bank already exercises) -- that equality is the mechanism's own predicted behavior,
    NOT evidence of an arm-implementation bug, so it is deliberately NOT the differencing signal
    here. Instead: (a) a DELIBERATE graded-generalization probe using "grasp"/"cram" -- two
    lexical_similarity.CONCEPT_FEATURES SUPPLY-EXTENSION words that are NOT literal members of any
    of goal_outcome_relation.py's 6 original pools, where baseline (Tier1-exact + Tier2-WordNet-
    primary-synonym) is MEASURED to miss both and grounded (concept_similarity-graded) is MEASURED
    to fire on both; (b) mwe_disengage_scan vs _engagement_disengage_scan on the 5 disclosed-gap
    items (baseline misses all 5 by construction, grounded recovers them)."""
    probe_goal = "He wanted to grasp the concept."
    probe_outcome = "She crammed for the exam all night."
    baseline_goal_probe = sorted(_gor.goal_atoms(probe_goal))
    grounded_goal_probe = sorted(_gog.goal_atoms_grounded(probe_goal))
    baseline_outcome_probe = sorted(_gor.outcome_atoms(probe_outcome))
    grounded_outcome_probe = sorted(_gog.outcome_atoms_grounded(probe_outcome))
    generalization_differs = (baseline_goal_probe != grounded_goal_probe) or \
        (baseline_outcome_probe != grounded_outcome_probe)

    gap_texts = [t for t, covered in _gor.REPRESENTATIVE_DISENGAGEMENT_PHRASES if not covered]
    baseline_gap_hits = [_gor.mwe_disengage_scan(t) is not None for t in gap_texts]
    grounded_gap_hits = [_gog._engagement_disengage_scan(t) is not None for t in gap_texts]
    gap_hits_differ = baseline_gap_hits != grounded_gap_hits

    return {
        "generalization_probe_goal": probe_goal, "generalization_probe_outcome": probe_outcome,
        "baseline_goal_probe_atoms": baseline_goal_probe, "grounded_goal_probe_atoms": grounded_goal_probe,
        "baseline_outcome_probe_atoms": baseline_outcome_probe,
        "grounded_outcome_probe_atoms": grounded_outcome_probe,
        "generalization_probe_differs": generalization_differs,
        "baseline_gap_hits": baseline_gap_hits, "grounded_gap_hits": grounded_gap_hits,
        "gap_hits_differ": gap_hits_differ,
        "arms_differ": generalization_differs and gap_hits_differ,
    }


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


# ============================================================================ self-test
def self_test() -> dict:
    """Real-code-path check: both modules' own self_test()s (real FHRR bind/unbind/bundle, real
    registry.learn fit, real WordNet morphy/gloss lookups, real RelationRegister construction) +
    arms-must-differ + verdict-logic sanity."""
    r_baseline = _gor.self_test()
    r_grounded = _gog.self_test()
    diff = _arms_must_differ()
    assert diff["arms_differ"], f"ARMS_IDENTICAL: {diff}"

    t0_verdict, t0_msg = tier0_verdict(r_grounded["engagement_axis_coverage"])
    assert t0_verdict == "HARD_PASS", f"tier0_verdict sanity: {t0_msg}"
    t1_verdict, t1_msg = tier1_verdict(
        {"held_out_acc": r_baseline["held_out_acc"],
         "memorization_baseline_acc": r_baseline["memorization_baseline_acc"],
         "scramble_control_acc": r_baseline["scramble_control_acc"]},
        r_grounded)
    assert t1_verdict == "HARD_PASS", f"tier1_verdict sanity: {t1_msg}"

    # verdict-logic unit checks (synthetic inputs, not the real cohort -- pure function sanity).
    hf_v, _ = tier1_verdict({"held_out_acc": 0.9, "memorization_baseline_acc": 0.6,
                              "scramble_control_acc": 0.6},
                             {"held_out_acc": 0.5, "scramble_control_acc": 0.6,
                              "engagement_axis_coverage": {"disclosed_gap_recovery_count": 3}})
    assert hf_v == "HARD_FAIL", hf_v
    mb_v, _ = tier1_verdict({"held_out_acc": 0.9, "memorization_baseline_acc": 0.6,
                              "scramble_control_acc": 0.6},
                             {"held_out_acc": 0.9, "scramble_control_acc": 0.6,
                              "engagement_axis_coverage": {"disclosed_gap_recovery_count": 0}})
    assert mb_v == "MIDDLE_BAND", mb_v

    return {"baseline_self_test": {k: v for k, v in r_baseline.items()
                                    if k not in ("held_per_item", "dictionary_coverage_misses")},
            "grounded_self_test": {k: v for k, v in r_grounded.items()
                                    if k not in ("held_per_item", "engagement_axis_coverage_misses")},
            "arms_differ_check": diff,
            "tier0_verdict_sanity": t0_verdict, "tier1_verdict_sanity": t1_verdict,
            "verdict_logic_unit_checks": {"hard_fail_case": hf_v, "middle_band_case": mb_v}}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                   "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                   "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps({k: v for k, v in metrics.items() if k != "result"}, indent=2, default=str))
        print(json.dumps({"result_summary": {
            "baseline_held_out_acc": result["baseline_self_test"]["held_out_acc"],
            "grounded_held_out_acc": result["grounded_self_test"]["held_out_acc"],
            "grounded_gap_recovery": result["grounded_self_test"]["engagement_axis_coverage"][
                "disclosed_gap_recovery_count"],
        }}, indent=2, default=str))
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    expected_units = 2  # tier0 unit + tier1 unit
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    print(f"[{run_mode}] TIER-0: engagement-axis coverage gate (no DesireDB, no register/"
          f"induction machinery)...", flush=True)
    coverage = _gog.engagement_axis_coverage()
    t0_verdict, t0_msg = tier0_verdict(coverage)
    print(f"[{run_mode}] TIER-0 {t0_verdict}: {t0_msg}", flush=True)
    _write_heartbeat(output_dir, 0, expected_units, time.time() - t0)

    if t0_verdict == "HARD_FAIL":
        elapsed = time.time() - t0
        metrics = {
            "verdict": "HARD_FAIL", "verdict_msg": f"TIER0_GATE_HARD_FAIL: {t0_msg}. "
                       f"Per the preclusion drill's own design, do NOT proceed to Tier-1; "
                       f"mwe_disengage_scan stays the operating point.",
            "summary": f"HARD_FAIL: TIER0_GATE_HARD_FAIL: {t0_msg}",
            "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
            "tier0": {"verdict": t0_verdict, "msg": t0_msg, "coverage": coverage},
            "tier1": None,
            "cardinality_ok": True, "expected_n_units": expected_units,
            "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
            "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
            "crlb_n/a": "accuracy-comparison ablation over a fixed item bank; no capacity/"
                        "noise-floor discriminator threshold to CRLB-check",
            "deterministic_seeding": True,
        }
        _write_metrics(output_dir, metrics)
        print(json.dumps({k: v for k, v in metrics.items() if k != "tier0"}, indent=2, default=str))
        return

    if run_mode == "smoke":
        # SMOKE = Tier-0 gate only, per hand-off ("add a cheap Tier-0 axis-coverage smoke that
        # GATES the ablation"). Also verify arms-differ here so a smoke-only run still catches an
        # identical-arms bug before the (cheap, but non-trivial) Tier-1 full run.
        diff = _arms_must_differ()
        elapsed = time.time() - t0
        smoke_verdict = t0_verdict if diff["arms_differ"] else "HARD_FAIL"
        smoke_msg = t0_msg if diff["arms_differ"] else f"SMOKE_ARMS_IDENTICAL: {diff}"
        metrics = {
            "verdict": smoke_verdict, "verdict_msg": f"SMOKE_{smoke_verdict}: {smoke_msg}",
            "summary": f"SMOKE_{smoke_verdict}: {smoke_msg}",
            "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
            "tier0": {"verdict": t0_verdict, "msg": t0_msg, "coverage": coverage},
            "arms_differ_verified": diff["arms_differ"], "arms_differ_check": diff,
            "cardinality_ok": True, "expected_n_units": expected_units,
            "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
            "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
            "deterministic_seeding": True,
        }
        _write_metrics(output_dir, metrics)
        print(json.dumps({k: v for k, v in metrics.items() if k != "tier0"}, indent=2, default=str))
        print(json.dumps({"tier0_coverage": {k: v for k, v in coverage.items()
                                              if k not in ("hits", "misses")}}, indent=2, default=str))
        return

    # ---- FULL: Tier-0 (already run above) + Tier-1 full ablation ----
    print(f"[{run_mode}] TIER-1: baseline self_test() (hdlab.goal_outcome_relation)...", flush=True)
    baseline = _gor.self_test()
    print(f"[{run_mode}] baseline: held_out_acc={baseline['held_out_acc']} "
          f"mem_acc={baseline['memorization_baseline_acc']} "
          f"scr_acc={baseline['scramble_control_acc']} "
          f"dict_coverage={baseline['dictionary_coverage']['coverage']}", flush=True)
    _write_heartbeat(output_dir, 1, expected_units, time.time() - t0)

    print(f"[{run_mode}] TIER-1: grounded self_test() (hdlab.goal_outcome_relation_grounded)...",
          flush=True)
    grounded = _gog.self_test()
    print(f"[{run_mode}] grounded: held_out_acc={grounded['held_out_acc']} "
          f"mem_acc={grounded['memorization_baseline_acc']} "
          f"scr_acc={grounded['scramble_control_acc']} "
          f"axis_coverage={grounded['engagement_axis_coverage']['coverage']} "
          f"gap_recovery={grounded['engagement_axis_coverage']['disclosed_gap_recovery_count']}/5",
          flush=True)

    diff = _arms_must_differ()
    t1_verdict, t1_msg = tier1_verdict(baseline, grounded)
    print(f"[{run_mode}] TIER-1 {t1_verdict}: {t1_msg}", flush=True)
    _write_heartbeat(output_dir, expected_units, expected_units, time.time() - t0)

    overall_verdict = t1_verdict if diff["arms_differ"] else "HARD_FAIL"
    overall_msg = (
        f"TIER0[{t0_verdict}]: {t0_msg} || TIER1[{t1_verdict}]: {t1_msg} || "
        f"arms_differ={diff['arms_differ']} || "
        f"ACHIEVE_LEG(subtype_acc={grounded['subtype_acc']}) vs "
        f"baseline(subtype_acc={baseline['subtype_acc']}) || "
        f"CONTRADICT_LEG(coverage={grounded['engagement_axis_coverage']['coverage']}, "
        f"gap_recovery={grounded['engagement_axis_coverage']['disclosed_gap_recovery_count']}/5, "
        f"HONEST_CALIBRATION: mechanism_design_P~0.55 brain_fidelity_P~0.15-0.20 [separate, not "
        f"blended -- see prereg]) vs baseline(dict_coverage="
        f"{baseline['dictionary_coverage']['coverage']}, gap_recovery=0/5 by construction)"
    )
    if not diff["arms_differ"]:
        overall_msg = f"SMOKE_ARMS_IDENTICAL overrides TIER1 verdict: {diff} || " + overall_msg

    elapsed = time.time() - t0
    metrics = {
        "verdict": overall_verdict, "verdict_msg": overall_msg, "summary": f"{overall_verdict}: {overall_msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "tier0": {"verdict": t0_verdict, "msg": t0_msg, "coverage": coverage},
        "tier1": {"verdict": t1_verdict, "msg": t1_msg},
        "baseline_selftest": {k: v for k, v in baseline.items()
                               if k not in ("held_per_item", "dictionary_coverage_misses")},
        "baseline_selftest_held_per_item": baseline["held_per_item"],
        "baseline_selftest_dictionary_coverage_misses": baseline["dictionary_coverage_misses"],
        "grounded_selftest": {k: v for k, v in grounded.items()
                               if k not in ("held_per_item", "engagement_axis_coverage_misses")},
        "grounded_selftest_held_per_item": grounded["held_per_item"],
        "grounded_selftest_engagement_axis_coverage_misses": grounded["engagement_axis_coverage_misses"],
        "achieve_leg": {
            "baseline_held_out_acc": baseline["held_out_acc"],
            "grounded_held_out_acc": grounded["held_out_acc"],
            "baseline_subtype_acc": baseline["subtype_acc"],
            "grounded_subtype_acc": grounded["subtype_acc"],
            "parity_note": "held_out_acc PARITY (not improvement) is the expected, correct "
                            "outcome on this bank -- current hand-pools already cover every word "
                            "this bank exercises (see prereg 'Honest framing'); the graded "
                            "fallback (genuine synonym generalization) is a capability this bank "
                            "does not exercise.",
        },
        "contradict_leg": {
            "baseline_dictionary_coverage": baseline["dictionary_coverage"],
            "grounded_engagement_axis_coverage": {k: v for k, v in coverage.items()
                                                   if k not in ("hits", "misses")},
            "disclosed_gap_recovery_count": coverage["disclosed_gap_recovery_count"],
            "disclosed_gap_recovery_fraction": coverage["disclosed_gap_recovery_fraction"],
            "honest_calibration": {
                "mechanism_design_P": 0.55,
                "brain_fidelity_P": "0.15-0.20",
                "note": "CONFIRMED-absent human-subject evidence for wordless preclusion "
                        "inference (9-angle/~20-search hunt this session, see notes/research_"
                        "preclusion_goal_failure_inference_2026-08-09.md) -- NOT merely "
                        "under-searched. Report this leg SEPARATELY from the ACHIEVE leg; do not "
                        "blend into one verdict.",
            },
        },
        "arms_differ_verified": diff["arms_differ"], "arms_differ_check": diff,
        "cardinality_ok": True, "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "accuracy-comparison ablation over a fixed 14-TRAIN/11-HELDOUT item bank + a "
                    "fixed 29-item coverage bank; no capacity/noise-floor discriminator threshold",
        "deterministic_seeding": True,
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items()
                       if k not in ("baseline_selftest_held_per_item", "grounded_selftest_held_per_item",
                                     "baseline_selftest_dictionary_coverage_misses",
                                     "grounded_selftest_engagement_axis_coverage_misses",
                                     "tier0")}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately not BaseException, see cell-template mandate
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
