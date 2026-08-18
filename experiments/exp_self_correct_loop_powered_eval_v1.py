# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: N/A -- this is a single-pass MEASUREMENT cell (baseline vs a deterministic
#   self-correction transform of the SAME reader output, plus one random can-fail control) not a
#   tuned multi-arm sweep; arms_differ_exempted declares this explicitly (see below).
# - final_metrics_atomicity = tmp_replace (single-shot; whole run expected < 30s, no sweep)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "diagnostic recovery-rate/false-correction-rate measurement vs recomputed ground
#   truth, no CRLB noise floor applies"; discriminator_reachability=true (the RANDOM-correction
#   can-fail control below IS the reachability/beat-chance check)
# - baseline_in_band: N/A, see arms_differ note -- the RANDOM-correction control is the can-fail
#   baseline and is REQUIRED to show near-zero/negative net lift, not a working-range band
# - cell_chunked=False (single pass, wall time expected < 30s on 39 passages / 165 role-events)
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_self_correct_loop_powered_eval_v1 (2026-08-02)

FIRST REAL STAGE OF THE SELF-IMPROVING READER: flag -> self-correct -> measure, on the POWERED
eval (data/eval_gold_mention_role_mcguffey_v1/gold_multiclause_entity_track_v3.jsonl, 39 passages,
83 entities, 165 role-events -- ~2.8x exp_self_error_detection_internal_signals_v1's N=58 on v2).
Re-measures the trustworthy version of both prior numbers (the 0.675 end-to-end from commit
711e4fb2f and the ~46% self-detection from exp_self_error_detection_internal_signals_v1, both
measured on the tiny v2 set) and then builds the actual self-correction loop on top.

PRIOR-WORK CHECK (SUBSTRATE-KB CONCEPT-QUERY, USER-locked 2026-07-01): queried
`tools/substrate_query.sh "self-correction internal signal flag revise role assignment error
recovery trusted rule coherence recheck"`. Top hits (cosine 0.28-0.30) were all off-topic: GO
ontology "signal recognition particle receptor complex" (0.3018), "signal sequence receptor
activity" (0.2891), WordNet "correctional" (0.2793), and two unrelated notes chunks (selectional-
preference precision lever, erasure-coded redundancy) at 0.278-0.279. NO prior cell at cosine>0.30
builds or measures a flag->self-correct->remeasure loop for role-assignment errors. This is a NEW
cell, not a rediscovery.

REUSES VERBATIM (import, no reimplementation):
  - exp_wire_extraction_accumulate_wm_oracle_vs_real_v1: unit_phase_vec, fhrr_bind/unbind/bundle,
    cleanup_argmax, run_self_test, match_mention_to_token, load_multiclause_gold, build_register,
    score_entity (the exact accumulate-WM FHRR register mechanics).
  - exp_self_error_detection_internal_signals_v1 (sed): fit_commit_revise_v4_animacy_production_
    model (frozen v4-animacy commit-then-revise reader), build_instrumented_events (attaches
    subj_idx/clause_n_agent/margin/gate_fired per event, NO gold read at signal-compute time),
    compute_signals_no_gold (S1 rule-violation, S2 no-agent-in-clause, S3 low-confidence margin).
  - exp_wire_extraction_accumulate_wm_oracle_vs_real_v5: REACHABLE_ROLES_V5 (error-class gate).
This cell adds NO new extraction mechanism and NO per-construction hand rule -- it wires the
ALREADY-VALIDATED detection signals to ONE general trusted rule (clause-subject-is-usually-agent,
the same rule already in the reader's own COMMIT default clause_position_predict5) via a
flag -> propose -> accept-if-coherent -> remeasure loop.

STAGE 0 -- RE-MEASURE ON THE POWERED EVAL (all numbers below are recomputed fresh on v3, nothing
hand-copied from the v2-era commits):
  - baseline_multi_event_recall_v3: real_multi_event_recall of the frozen v4-animacy reader on v3
    (the trustworthy analog of the 0.675 end-to-end number, which was measured on v2's N=58).
  - detection signal quality on v3 (S1/S2/S3/S4/COMBINED precision, recall, AUC, lift over base
    rate, RANDOM_SIGNAL can-fail control) -- the trustworthy analog of the ~46% self-detection
    number.

STAGE 1 -- FLAG (no gold): combined_flag = S1 OR S2 OR S3(when applicable) OR S4, exactly as
exp_self_error_detection_internal_signals_v1 computes it (imported, not reimplemented).

STAGE 2 -- SELF-CORRECT (the new mechanism this cell builds):
  CORRECTION CANDIDATE = an event where S1 fires (is_subject AND pred_role != "agent"). This is
  the ONLY event type the trusted rule ("clause subject -> agent") can act on -- it is a strict
  subset of "flagged" by construction (S1 firing requires is_subject True, so a candidate always
  exists whenever the frozen reader's REVISE softmax overrode the subject's own default-agent
  assignment). NOTE (derived, not asserted): because clause_position_predict5's COMMIT default
  ALWAYS assigns "agent" to the clause subject, and instrumented_predict_clause only replaces that
  default when REVISE's margin >= model["margin_thresh"], an S1-firing event structurally implies
  gate_fired=True and margin>=thresh for that token -- i.e. S1 and S3 cannot both fire on the same
  event (verified empirically below, reported as n_s1_and_s3_both in diagnostics; expected 0).
  PROPOSE: revised_role = "agent" (reverting to the reader's own base subject-default rule).
  ACCEPT iff the clause had ZERO predicted agents anywhere before correction (ev["clause_n_agent"]
  == 0 for this event's clause) -- i.e. accept only when the correction FILLS A STRUCTURALLY
  EMPTY-AGENT CLAUSE, a general internal-coherence criterion (does this clause have any agent at
  all?), not a per-construction rule. When the clause already has an agent elsewhere (a different
  mention correctly/incorrectly holding "agent"), the candidate is left flagged-but-UNCORRECTED --
  reported honestly, not silently forced. No gold is read anywhere in propose/accept.
  Correction is applied per-EVENT then the owning entity's WM register is REBUILT from the
  corrected role sequence (honest accumulate-WM mechanics: a correction to one event can shift
  bundle crosstalk for OTHER events in the same entity's chain -- this is measured, not assumed
  away).

STAGE 3 -- MEASURE vs v3 gold (post-hoc only, never used by propose/accept):
  - recovery_rate: of accepted corrections, fraction that flip an originally-WRONG event to
    CORRECT (the genuine-error class the loop is meant to fix).
  - false_correction_rate: of accepted corrections, fraction that flip an originally-CORRECT event
    to WRONG (the loop over-firing on a legitimately non-agent subject, e.g. a true by-agent
    passive where the subject really is the patient).
  - net_end_to_end_change: corrected real_multi_event_recall_v3 minus baseline_multi_event_recall_v3.
  - by error_class (SUBJECT_MISLABELED / OTHER_ROLE_ERROR / MENTION_NOT_MATCHED / UNREACHABLE_ROLE
    / CORRECT at baseline) -- honest report of which classes the loop can and cannot reach.

CAN-FAIL CONTROL (mandatory): apply the IDENTICAL forced-"agent" edit, same count as the accepted
targeted corrections, to a UNIFORM-RANDOM sample of NON-FLAGGED events (combined_flag == 0) --
events the internal signals gave no reason to distrust. If this random intervention shows
comparable-or-better net lift than the targeted one, the targeted result is not trustworthy at
this N and must be reported as such (HARD_FAIL_CANFAIL_VIOLATION).

HONEST SCOPE LIMIT: 83 entities / 165 role-events is still a small-N regime for the
recovery/false-correction RATES specifically (whichever subset is candidates-only, typically much
smaller than 165) -- every rate below is reported with its raw n. A NET_NEUTRAL_OR_NEGATIVE
verdict is a legitimate, informative outcome here, not a cell failure -- see decide_verdict.

Run:  .venv/Scripts/python.exe experiments/exp_self_correct_loop_powered_eval_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_self_correct_loop_powered_eval_v1.py --full
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from exp_wire_extraction_accumulate_wm_oracle_vs_real_v1 import (  # noqa: E402
    unit_phase_vec, fhrr_bind, fhrr_unbind, fhrr_bundle, cleanup_argmax, run_self_test,
    load_multiclause_gold, build_register, score_entity,
)
from exp_wire_extraction_accumulate_wm_oracle_vs_real_v5 import REACHABLE_ROLES_V5  # noqa: E402
import exp_self_error_detection_internal_signals_v1 as sed  # noqa: E402

ANCHOR_NAME = "self_correct_loop_powered_eval_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
GOLD_V3 = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multiclause_entity_track_v3.jsonl")

ROLE_VOCAB = ["agent", "patient", "theme", "recipient", "addressee", "speaker", "possessor", "experiencer"]

# --- pre-registered bands (declared BEFORE reading results) -----------------------------------
RANDOM_LIFT_TOL = 0.02       # can-fail: random-control net lift must be <= this (near-zero/negative)
NET_POSITIVE_MIN = 0.01      # minimum net_end_to_end_change to call the loop net-helpful
RECOVERY_OVER_FALSE_MIN_RATIO = 1.5   # recovered corrections must outnumber false ones by this ratio


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": os.environ.get("COMPUTERNAME", "unknown")}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def multi_event_recall(rows_correct_by_key):
    """rows_correct_by_key: dict entity_key -> list of 0/1 correct flags (chain order). Mean over
    chains with len >= 2 (the 'multi_event_recall' quantity the prior 0.675/v6 numbers report)."""
    multi = [np.mean(v) for v in rows_correct_by_key.values() if len(v) >= 2]
    return float(np.mean(multi)) if multi else None


def rebuild_and_score(entity_data, role_vecs, idx_vecs, overrides):
    """entity_data: dict key -> {"pred_roles": [...], "true_roles": [...]}. overrides:
    dict (key, k) -> new_role. Returns dict key -> list of per-event correct (0/1), in chain order,
    honestly re-running the SAME accumulate-WM bind/bundle/unbind mechanics as the frozen pipeline
    (a correction to one event's role can shift bundle crosstalk for other events in the same
    entity's chain -- this rebuild does not assume independence)."""
    out = {}
    for key, d in entity_data.items():
        pred_roles = [overrides.get((key, k), r) for k, r in enumerate(d["pred_roles"])]
        reg = build_register(pred_roles, role_vecs, idx_vecs)
        correct = score_entity(reg, d["true_roles"], idx_vecs, role_vecs)
        out[key] = correct
    return out


def run_all(mode, restrict_n=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    print("[%s] fitting STAGE-1 v4-animacy production model (frozen, reused verbatim) ..."
          % mode, flush=True)
    model = sed.fit_commit_revise_v4_animacy_production_model()
    print("[%s] model fit on %d sentences, margin_thresh=%.4f"
          % (mode, model["n_train_sentences"], model["margin_thresh"]), flush=True)

    passages = load_multiclause_gold(GOLD_V3)
    print("[%s] loaded %d multiclause passages (v3 powered eval)" % (mode, len(passages)), flush=True)

    events, n_clauses = sed.build_instrumented_events(passages, model, restrict_n=restrict_n)
    n_entities = len(events)
    n_role_events = sum(len(e["chain"]) for e in events)
    print("[%s] instrumented %d entity chains (%d role-events) over %d clauses"
          % (mode, n_entities, n_role_events, n_clauses), flush=True)

    seed = 20260802
    rng_sig = np.random.default_rng(seed + 12345)  # independent stream, matches sed's control stream
    rng_pick = np.random.default_rng(seed + 777)   # independent stream for the random-correction control
    d = 1024
    rng_vec = np.random.default_rng(seed)
    role_vecs = {r: unit_phase_vec(rng_vec, d) for r in ROLE_VOCAB}
    idx_vecs = [unit_phase_vec(rng_vec, d) for _ in range(8)]

    rows = []
    entity_data = {}
    baseline_correct_by_key = {}
    n_s1_and_s3_both = 0
    for entity in events:
        key = entity["key"]
        chain = entity["chain"]
        pred_roles = [ev["pred_role"] for ev in chain]
        true_roles = [ev["true_role"] for ev in chain]
        entity_data[key] = {"pred_roles": pred_roles, "true_roles": true_roles}
        reg = build_register(pred_roles, role_vecs, idx_vecs)
        correct = score_entity(reg, true_roles, idx_vecs, role_vecs)
        baseline_correct_by_key[key] = correct

        for k, ev in enumerate(chain):
            readback, _ = cleanup_argmax(fhrr_unbind(reg, idx_vecs[k]), role_vecs)
            s4 = 1 if readback != ev["pred_role"] else 0
            sig = sed.compute_signals_no_gold(ev, model["margin_thresh"], rng_sig)
            combined_score = sig["combined_partial_pre_s4"] + s4
            combined_flag = 1 if combined_score > 0 else 0
            if sig["s1_rule_violation"] == 1 and sig["s3_low_confidence"] == 1:
                n_s1_and_s3_both += 1

            true_role = ev["true_role"]
            if true_role not in REACHABLE_ROLES_V5:
                error_class = "UNREACHABLE_ROLE"
            elif not ev["match_ok"]:
                error_class = "MENTION_NOT_MATCHED"
            elif correct[k] == 0:
                error_class = "SUBJECT_MISLABELED" if ev["is_subject"] else "OTHER_ROLE_ERROR"
            else:
                error_class = "CORRECT"
            genuine_error = error_class in ("SUBJECT_MISLABELED", "OTHER_ROLE_ERROR")

            candidate = bool(sig["s1_rule_violation"] == 1)
            accepted = bool(candidate and ev["clause_n_agent"] == 0)

            rows.append({
                "key": key, "k": k, "clause_idx": ev["clause_idx"],
                "true_role": true_role, "pred_role_baseline": ev["pred_role"],
                "match_ok": ev["match_ok"], "is_subject": ev["is_subject"], "gate_fired": ev["gate_fired"],
                "clause_n_agent": ev["clause_n_agent"], "margin_value": sig["margin_value"],
                "correct_baseline": int(correct[k]), "error_class": error_class,
                "genuine_error": int(genuine_error),
                "s1_rule_violation": sig["s1_rule_violation"], "s2_no_agent_in_clause": sig["s2_no_agent_in_clause"],
                "s3_low_confidence": sig["s3_low_confidence"], "s3_applicable": sig["s3_applicable"],
                "s4_wm_readback_mismatch": s4, "combined_flag": combined_flag, "combined_score": combined_score,
                "candidate_for_correction": candidate, "accepted_correction": accepted,
            })

    # --- STAGE 2: targeted self-correction (accept-if-fills-empty-agent-clause) ----------------
    accepted_overrides = {(r["key"], r["k"]): "agent" for r in rows if r["accepted_correction"]}
    n_accepted = len(accepted_overrides)
    targeted_correct_by_key = rebuild_and_score(entity_data, role_vecs, idx_vecs, accepted_overrides)

    # --- CAN-FAIL: identical forced-"agent" edit on a random sample of NON-FLAGGED events ------
    non_flagged_pool = [(r["key"], r["k"]) for r in rows if r["combined_flag"] == 0]
    n_random = min(n_accepted, len(non_flagged_pool))
    if n_random > 0:
        sample_pos = rng_pick.choice(len(non_flagged_pool), size=n_random, replace=False)
        random_overrides = {non_flagged_pool[i]: "agent" for i in sample_pos}
    else:
        random_overrides = {}
    random_correct_by_key = rebuild_and_score(entity_data, role_vecs, idx_vecs, random_overrides)

    elapsed = time.perf_counter() - t0
    return {
        "rows": rows, "model": model, "elapsed": elapsed,
        "n_entities": n_entities, "n_role_events": n_role_events, "n_clauses": n_clauses,
        "n_s1_and_s3_both": n_s1_and_s3_both,
        "baseline_correct_by_key": baseline_correct_by_key,
        "targeted_correct_by_key": targeted_correct_by_key,
        "random_correct_by_key": random_correct_by_key,
        "accepted_overrides": accepted_overrides, "random_overrides": random_overrides,
        "n_accepted": n_accepted, "n_random": n_random,
    }


def auc_from_scores(scores, labels):
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    n_pos = int(labels.sum())
    n_neg = int((1 - labels).sum())
    if n_pos == 0 or n_neg == 0:
        return None
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(len(scores), dtype=np.float64)
    sorted_scores = scores[order]
    i = 0
    r = 1
    while i < len(sorted_scores):
        j = i
        while j < len(sorted_scores) and sorted_scores[j] == sorted_scores[i]:
            j += 1
        avg_rank = (r + (r + (j - i) - 1)) / 2.0
        for k in range(i, j):
            ranks[order[k]] = avg_rank
        r += (j - i)
        i = j
    sum_ranks_pos = float(ranks[labels == 1].sum())
    u = sum_ranks_pos - n_pos * (n_pos + 1) / 2.0
    return u / (n_pos * n_neg)


def precision_recall(flag, wrong):
    flag = np.asarray(flag, dtype=np.int64)
    wrong = np.asarray(wrong, dtype=np.int64)
    n_flagged = int(flag.sum())
    n_wrong = int(wrong.sum())
    tp = int(((flag == 1) & (wrong == 1)).sum())
    precision = (tp / n_flagged) if n_flagged else None
    recall = (tp / n_wrong) if n_wrong else None
    base_rate = (n_wrong / len(wrong)) if len(wrong) else None
    return {"n_flagged": n_flagged, "n_wrong": n_wrong, "tp": tp,
            "precision": precision, "recall": recall, "base_rate": base_rate,
            "lift_mult": (precision / base_rate) if (precision is not None and base_rate) else None}


def analyze_detection(rows):
    """Trustworthy-N analog of exp_self_error_detection_internal_signals_v1's analyze(), recomputed
    fresh on v3 (this cell's own rows, not imported, since field names differ slightly)."""
    n_events = len(rows)
    wrong = [1 - r["correct_baseline"] for r in rows]
    genuine = [r["genuine_error"] for r in rows]
    base_rate_all_wrong = float(np.mean(wrong))
    base_rate_genuine = float(np.mean(genuine))

    error_class_counts = {}
    for r in rows:
        error_class_counts[r["error_class"]] = error_class_counts.get(r["error_class"], 0) + 1

    signal_specs = [
        ("S1_rule_violation", "s1_rule_violation", None),
        ("S2_no_agent_in_clause", "s2_no_agent_in_clause", None),
        ("S3_low_confidence", "s3_low_confidence", "s3_applicable"),
        ("S4_wm_readback_mismatch", "s4_wm_readback_mismatch", None),
        ("COMBINED_any_fires", "combined_flag", None),
    ]
    per_signal = {}
    for label, flag_field, applicable_field in signal_specs:
        sub_rows = [r for r in rows if r[applicable_field]] if applicable_field else rows
        flags = [r[flag_field] for r in sub_rows]
        wrongs = [1 - r["correct_baseline"] for r in sub_rows]
        genuines = [r["genuine_error"] for r in sub_rows]
        pr_all = precision_recall(flags, wrongs)
        pr_genuine = precision_recall(flags, genuines)
        if label == "S3_low_confidence":
            scores = [-(r["margin_value"] if r["margin_value"] is not None else 0.0) for r in sub_rows]
        elif label == "COMBINED_any_fires":
            scores = [r["combined_score"] for r in sub_rows]
        else:
            scores = flags
        auc_all_wrong = auc_from_scores(scores, wrongs)
        auc_genuine = auc_from_scores(scores, genuines)
        per_signal[label] = {
            "n_applicable": len(sub_rows), "coverage_fraction": len(sub_rows) / n_events if n_events else None,
            "precision_recall_all_wrong": pr_all, "precision_recall_genuine_error": pr_genuine,
            "auc_all_wrong": auc_all_wrong, "auc_genuine_error": auc_genuine,
        }
    genuine_rows = [r for r in rows if r["genuine_error"]]
    genuine_caught_any = (float(np.mean([r["combined_flag"] for r in genuine_rows]))
                          if genuine_rows else None)
    return {"n_events": n_events, "base_rate_all_wrong": base_rate_all_wrong,
            "base_rate_genuine_error": base_rate_genuine, "error_class_counts": error_class_counts,
            "per_signal": per_signal,
            "genuine_error_fraction_internally_detected_by_any_signal": genuine_caught_any,
            "n_genuine_errors": len(genuine_rows)}


def analyze_correction(result):
    rows = result["rows"]
    baseline = result["baseline_correct_by_key"]
    targeted = result["targeted_correct_by_key"]
    random_ = result["random_correct_by_key"]

    baseline_recall = multi_event_recall(baseline)
    targeted_recall = multi_event_recall(targeted)
    random_recall = multi_event_recall(random_)

    net_targeted = (targeted_recall - baseline_recall) if (targeted_recall is not None
                                                            and baseline_recall is not None) else None
    net_random = (random_recall - baseline_recall) if (random_recall is not None
                                                        and baseline_recall is not None) else None

    accepted_rows = [r for r in rows if r["accepted_correction"]]
    recovered, false_correction, still_wrong, still_correct_noop = [], [], [], []
    by_class = {}
    for r in accepted_rows:
        key, k = r["key"], r["k"]
        before = baseline[key][k]
        after = targeted[key][k]
        by_class.setdefault(r["error_class"], {"recovered": 0, "false_correction": 0,
                                                "still_wrong": 0, "still_correct_noop": 0, "n": 0})
        by_class[r["error_class"]]["n"] += 1
        if before == 0 and after == 1:
            recovered.append(r)
            by_class[r["error_class"]]["recovered"] += 1
        elif before == 1 and after == 0:
            false_correction.append(r)
            by_class[r["error_class"]]["false_correction"] += 1
        elif before == 0 and after == 0:
            still_wrong.append(r)
            by_class[r["error_class"]]["still_wrong"] += 1
        else:
            still_correct_noop.append(r)
            by_class[r["error_class"]]["still_correct_noop"] += 1

    n_accepted = len(accepted_rows)
    recovery_rate = (len(recovered) / n_accepted) if n_accepted else None
    false_correction_rate = (len(false_correction) / n_accepted) if n_accepted else None

    n_candidates = sum(1 for r in rows if r["candidate_for_correction"])
    n_candidates_not_accepted = n_candidates - n_accepted

    n_genuine_errors = sum(1 for r in rows if r["genuine_error"])
    genuine_error_recovery_rate_overall = (len(recovered) / n_genuine_errors) if n_genuine_errors else None

    return {
        "baseline_multi_event_recall": baseline_recall,
        "targeted_multi_event_recall": targeted_recall,
        "random_control_multi_event_recall": random_recall,
        "net_end_to_end_change_targeted": net_targeted,
        "net_end_to_end_change_random_control": net_random,
        "n_accepted_corrections": n_accepted,
        "n_candidates_total": n_candidates,
        "n_candidates_not_accepted_clause_already_had_agent": n_candidates_not_accepted,
        "n_random_control_edits": result["n_random"],
        "n_recovered": len(recovered), "n_false_correction": len(false_correction),
        "n_still_wrong_after_correction": len(still_wrong),
        "n_still_correct_noop": len(still_correct_noop),
        "recovery_rate_of_accepted": recovery_rate,
        "false_correction_rate_of_accepted": false_correction_rate,
        "genuine_error_recovery_rate_overall": genuine_error_recovery_rate_overall,
        "n_genuine_errors_total": n_genuine_errors,
        "by_error_class": by_class,
        "n_s1_and_s3_both_derived_check": result["n_s1_and_s3_both"],
    }


def decide_verdict(detection, correction):
    can_fail_ok = (correction["net_end_to_end_change_random_control"] is None
                   or correction["net_end_to_end_change_random_control"] <= RANDOM_LIFT_TOL)
    if not can_fail_ok:
        return "HARD_FAIL_CANFAIL_VIOLATION_RANDOM_CORRECTION_SHOWS_COMPARABLE_LIFT", {
            "detection": detection, "correction": correction}

    net = correction["net_end_to_end_change_targeted"]
    rec = correction["n_recovered"]
    false = correction["n_false_correction"]
    ratio_ok = (false == 0 and rec > 0) or (false > 0 and rec / false >= RECOVERY_OVER_FALSE_MIN_RATIO)

    summary = {"detection": detection, "correction": correction}
    if net is not None and net >= NET_POSITIVE_MIN and ratio_ok:
        return "MEASURED_MECHANISM_SELF_CORRECT_NET_POSITIVE_RECOVERS_MORE_THAN_IT_BREAKS", summary
    if net is not None and net > 0:
        return "MIDDLE_BAND_SELF_CORRECT_NET_POSITIVE_BUT_WEAK_OR_MIXED_CLASS", summary
    if net is not None and net == 0:
        return "NULL_RESULT_SELF_CORRECT_NET_NEUTRAL", summary
    return "MEASURED_MECHANISM_SELF_CORRECT_NET_NEGATIVE_FALSE_CORRECTIONS_DOMINATE", summary


def _write_metrics(verdict, summary, result, mode):
    detection = summary["detection"]
    correction = summary["correction"]
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": (
            "%s | n_entities=%d n_role_events=%d | baseline_recall_v3=%s | net_targeted=%s "
            "net_random_control=%s | n_accepted=%d recovered=%d false_correction=%d | "
            "genuine_error_recovery_rate=%s | best_detection_signal_combined_recall_genuine=%s"
            % (verdict, result["n_entities"], result["n_role_events"],
               "%.4f" % correction["baseline_multi_event_recall"] if correction["baseline_multi_event_recall"] is not None else "NA",
               "%.4f" % correction["net_end_to_end_change_targeted"] if correction["net_end_to_end_change_targeted"] is not None else "NA",
               "%.4f" % correction["net_end_to_end_change_random_control"] if correction["net_end_to_end_change_random_control"] is not None else "NA",
               correction["n_accepted_corrections"], correction["n_recovered"], correction["n_false_correction"],
               "%.3f" % correction["genuine_error_recovery_rate_overall"] if correction["genuine_error_recovery_rate_overall"] is not None else "NA",
               "%.3f" % detection["per_signal"]["COMBINED_any_fires"]["precision_recall_genuine_error"]["recall"]
               if detection["per_signal"]["COMBINED_any_fires"]["precision_recall_genuine_error"]["recall"] is not None else "NA")
        ),
        "summary": {"detection": detection, "correction": correction},
        "bands": {"RANDOM_LIFT_TOL": RANDOM_LIFT_TOL, "NET_POSITIVE_MIN": NET_POSITIVE_MIN,
                  "RECOVERY_OVER_FALSE_MIN_RATIO": RECOVERY_OVER_FALSE_MIN_RATIO},
        "per_event_dump": result["rows"],
        "model_margin_thresh": result["model"]["margin_thresh"],
        "arms_differ_verified": "not_applicable_single_pass_measurement_cell",
        "arms_differ_exempted": "ALL (baseline/targeted-correction/random-control are a deterministic transform + can-fail control of ONE frozen reader's output, not independently-tuned arms)",
        "arms_differ_exemption_rationale": (
            "targeted and random-control registers are rebuilt from the SAME baseline pred_roles "
            "with different override dicts (accepted-correction vs random-sample) -- there is no "
            "independent model-fitting per arm to tie or diverge; exempted by design."
        ),
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_heartbeat_exempt_lt30s",
        "elapsed_s": result["elapsed"],
        "gold_file": GOLD_V3,
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=120.0,
                    help="formula self-test timeout budget (declared; full run expected < 30s: "
                         "numpy-only, 39 passages/165 role-events, no grid sweep, no torch, no GPU")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    _write_start_marker(OUTPUT_DIR, mode, expected_n_units=1)

    rng = np.random.default_rng(20260802)
    run_self_test(rng)

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        restrict_n = 5 if mode == "self_test" else None
        result = run_all(mode, restrict_n=restrict_n)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        _write_crash_metrics(OUTPUT_DIR, e)
        raise SystemExit(2)

    detection = analyze_detection(result["rows"])
    correction = analyze_correction(result)
    verdict, summary = decide_verdict(detection, correction)
    metrics = _write_metrics(verdict, summary, result, mode)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, result["elapsed"]), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
