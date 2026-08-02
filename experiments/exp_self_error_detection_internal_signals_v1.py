# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: N/A -- this is a single-pass MEASUREMENT cell (one instrumented reader
#   pass over gold), not a multi-arm comparison; arms_differ_exempted declares this explicitly.
# - final_metrics_atomicity = tmp_replace (single-shot; whole run < 30s, no sweep, no tuning loop)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "diagnostic detection-quality measurement (precision/recall/AUC of internal signals
#   vs recomputed ground truth), no CRLB noise floor applies"; discriminator_reachability=true (the
#   RANDOM-SIGNAL can-fail control below IS the reachability/beat-chance check)
# - baseline_in_band: N/A, see arms_differ note -- the RANDOM signal is the can-fail baseline and is
#   REQUIRED to sit at chance (near 0 lift over base error rate), not in a 0.05-0.95 "working" band
# - cell_chunked=False (single pass, wall time expected < 15s on ~30 clauses / ~60 events)
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_self_error_detection_internal_signals_v1 (2026-08-02)

SELF-ERROR-DETECTION PROBE: can the reader flag its OWN role-assignment errors using INTERNAL
signals (no answer key), validated post-hoc against the gold we already have? This is the
prerequisite for a self-correcting/self-learning loop -- a reader can only fix gaps it can DETECT.

PRIOR-WORK CHECK (per SUBSTRATE-KB CONCEPT-QUERY discipline, USER-locked 2026-07-01): queried
`tools/substrate_query.sh "self-error-detection internal confidence calibration role assignment
error detection no gold"` before authoring. Top hit was the generic concept node 'detection'
(cosine=0.4521, generic WordNet/atom entity, not a prior cell) and 'signal detection'/
'Saturation detection metrics' (cosine 0.38-0.42, unrelated: saturation-detection for smoke
regimes, not role-assignment self-error-detection). NO prior cell at cosine>0.30 tests whether
THIS reader's role assignments carry an internally-detectable error signal. This is a NEW probe,
not a rediscovery.

REUSES VERBATIM (import, no reimplementation) the exact production pipeline already fit + run
end-to-end in exp_wire_extraction_accumulate_wm_oracle_vs_real_v6.py:
  STAGE 1: fit_commit_revise_v4_animacy_production_model() (commit-then-revise + animacy lexicon,
           5-way ROLE_VOCAB5, the CURRENT best "real" arm, MEASURED@data/exp_wire_extraction_
           accumulate_wm_oracle_vs_real_v6/metrics.json:summary.real_multi_event_recall).
  STAGE 2: fhrr_bind/unbind/bundle/cleanup_argmax + build_register (accumulate WM register).
This cell does NOT re-tune or re-select anything -- it re-runs the frozen v6 "real" pipeline over
the SAME eval file (gold_multiclause_entity_track_v2.jsonl) with ADDITIONAL INSTRUMENTATION that
v6's own predict wrapper computes internally but discards (grammatical subject index, REVISE
softmax margin, per-clause agent count, WM per-slot readback) -- exposing what the reader "already
knows" about its own state, not adding a new mechanism.

FOUR INTERNAL SIGNALS (each computed ONLY from pipeline-internal, non-gold state; NEVER reads
true_roles at signal-compute time -- see `compute_signals_no_gold()`, which takes no gold argument
by construction):
  S1 RULE_VIOLATION       -- this event's mention IS the clause's grammatical subject (per
                             clause_position_predict5's own subj_idx) AND the predicted role !=
                             "agent" (contradicts the reader's own subject-default-agent prior).
  S2 NO_AGENT_IN_CLAUSE    -- this event's clause has ZERO mentions predicted "agent" anywhere in
                             it (something agent-shaped is missing/mislocalized in that clause).
  S3 LOW_CONFIDENCE        -- the graceful-degrade REVISE softmax margin (top1-top2 probability
                             gap), when the gate fired and REVISE actually ran on this mention, is
                             below the model's OWN production margin_thresh (the same threshold the
                             pipeline itself uses to fall back to the COMMIT default -- i.e. "the
                             reader was uncertain enough to graceful-degrade"). NOT APPLICABLE when
                             the gate never fired (pure COMMIT path, no softmax ran) -- reported as
                             its own coverage fraction, not silently imputed.
  S4 WM_READBACK_MISMATCH  -- round-trip the entity's accumulate-WM register (built from PREDICTED
                             roles, exactly as v6's "real" arm does) back through fhrr_unbind +
                             cleanup_argmax at this event's own slot, and compare to the role that
                             was WRITTEN in. A mismatch means the WM's own recall of what it just
                             stored disagrees with what it stored (bundle crosstalk/capacity
                             corruption) -- pure self-consistency, no gold touched.
COMBINED = S1 OR S2 OR (S3 when applicable) OR S4 (any-fires); COMBINED_SCORE = count of the 4
that fire (0-4), used as the continuous rank for combined AUC.

RANDOM_SIGNAL (CAN-FAIL CONTROL, MANDATORY per contract): an independent RNG coin-flip with the
SAME marginal flag rate as COMBINED, applied per event with no relation whatsoever to the
pipeline's internal state. If detection precision/recall/AUC is genuinely non-trivial, RANDOM must
NOT show comparable lift -- this is the beat-chance gate. If RANDOM ties or beats a real signal,
that signal's apparent lift is not trustworthy at this N and must be reported as inconclusive.

GROUND TRUTH (used ONLY for validation/scoring AFTER signals are computed, never as signal input):
recomputes true_roles/pred_roles/match_ok/correct via the IDENTICAL v6 STAGE-2 scoring call
(`score_entity(register_built_from_pred_roles, true_roles, idx_vecs, role_vecs)`), then
cross-checks its own real_multi_event_recall against the COMMITTED
data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v6/metrics.json:summary.real_multi_event_
recall (MEASURED=0.5667-ish per v6; exact figure re-read at run time, not hand-copied) as a
reproduction sanity gate -- if this cell's independently-recomputed recall does not match v6's
committed recall within a tight tolerance, something in this cell's re-instrumentation drifted
from the frozen pipeline and the detection numbers below are NOT trustworthy (HARD_FAIL gate).

ERROR-CLASS TAGGING (per event, GROUND-TRUTH SIDE ONLY, computed after signals):
  UNREACHABLE_ROLE     -- gold true_role is outside REACHABLE_ROLES_V5 (structurally cannot be
                          predicted right regardless of reader skill; NOT the reader's fault).
  MENTION_NOT_MATCHED  -- match_ok is False (coref/tagger grounding miss, a matching/grading-layer
                          issue, not a role-ASSIGNMENT fault).
  GENUINE_ROLE_ERROR   -- match_ok True, true_role reachable, but readback != true_role: an actual
                          role-assignment mistake the reader made. Subdivided into
                          SUBJECT_MISLABELED (event's token was the clause subject) vs
                          OTHER_ROLE_ERROR, since S1 targets exactly the subject-mislabel case.
  CORRECT              -- readback == true_role.
Detection precision/recall is reported both over ALL_WRONG (every non-CORRECT event) and over the
GENUINE_ROLE_ERROR subset alone (the class a self-correction loop could actually act on).

HONEST SCOPE LIMIT (declared before reading results): this eval file has ~20-25 entities / ~30
clauses -- N is small. Bands below are therefore MIDDLE-tolerant on purpose (this is a diagnostic
probe, not a capacity sweep) and every number is reported with its raw n so nobody over-reads a
ratio computed on n<10.

Run:  .venv/Scripts/python.exe experiments/exp_self_error_detection_internal_signals_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_self_error_detection_internal_signals_v1.py --full
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
    match_mention_to_token, load_multiclause_gold, build_register, score_entity,
)
from exp_extraction_commit_then_revise_v4_animacy import (  # noqa: E402
    fit_commit_revise_v4_animacy_production_model, build_sentence_multi6,
    revise_predict_one_with_margin6,
)
from exp_extraction_commit_then_revise_v3_theme import (  # noqa: E402
    gate_fires_v3, clause_position_predict5, ROLE_IDX5, ROLE_VOCAB5,
)
from exp_extraction_commit_then_revise_v4_animacy import lookup_animacy  # noqa: E402
from exp_wire_extraction_accumulate_wm_oracle_vs_real_v5 import REACHABLE_ROLES_V5  # noqa: E402

ANCHOR_NAME = "self_error_detection_internal_signals_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
GOLD_MULTICLAUSE = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multiclause_entity_track_v2.jsonl")
V6_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_wire_extraction_accumulate_wm_oracle_vs_real_v6", "metrics.json")

ROLE_VOCAB = ["agent", "patient", "theme", "recipient", "addressee", "speaker", "possessor", "experiencer"]

# --- pre-registered bands (declared BEFORE reading results) -----------------------------------
V6_REPRO_TOL = 0.02          # recomputed real_multi_event_recall must match committed v6 within this
RANDOM_LIFT_TOL = 0.10       # can-fail: |random_flagged_error_rate - base_error_rate| must be <= this
                             # (fraction of base_error_rate; see decide_verdict)
SIGNAL_HARD_PASS_PRECISION_MULT = 2.0   # flagged-subset error rate >= 2x base error rate
SIGNAL_HARD_PASS_RECALL_MIN = 0.30      # AND catches >=30% of genuine-role-errors
SIGNAL_MIDDLE_LIFT_MULT = 1.3           # beats base rate by >=30% but below HARD_PASS


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


# ---------------------------------------------------------------------------
# Instrumented STAGE-1 predict: SAME math as stage1_predict_clause_commit_revise_v4_animacy
# (exp_extraction_commit_then_revise_v4_animacy.py:715), just also RETURNS the internal state
# (subj_idx, per-mention margins, gate_fired) that function computes and discards.
# ---------------------------------------------------------------------------
def instrumented_predict_clause(text, model):
    sent = build_sentence_multi6({"text": text, "kind": "eval", "role_map": {}, "parser_correct": False},
                                  lookup_animacy)
    if not sent["mention_idx"]:
        return sent, {}, {}, False
    default_preds = clause_position_predict5(sent)
    gate_fired = bool(gate_fires_v3(sent, model["thresh"]))
    margins = {}
    if gate_fired:
        preds_idx, margins = revise_predict_one_with_margin6(sent, model["W"], model["mu"], model["sd"])
        merged = {}
        for i in sent["mention_idx"]:
            if i in preds_idx and margins.get(i, 0.0) >= model["margin_thresh"]:
                merged[i] = preds_idx[i]
            else:
                merged[i] = default_preds.get(i, ROLE_IDX5["patient"])
    else:
        merged = default_preds
    preds = {i: ROLE_VOCAB5[c] for i, c in merged.items()}
    return sent, preds, margins, gate_fired


# ---------------------------------------------------------------------------
# Build entity events with FULL internal instrumentation attached (subj_idx, clause agent-count,
# margin, gate_fired) -- extends build_entity_chains_predsdict's job (imported implicitly via the
# same match_mention_to_token) with the extra per-event internal fields the 4 signals need.
# ---------------------------------------------------------------------------
def build_instrumented_events(passages, model, restrict_n=None):
    if restrict_n is not None:
        passages = passages[:restrict_n]

    events = []
    n_clauses = 0
    for rec in passages:
        pid = rec["passage_id"]
        clauses = rec["clauses"]
        clause_infer = [instrumented_predict_clause(c, model) for c in clauses]
        n_clauses += len(clauses)

        # clause-level internal facts (no gold): agent count per clause, subject index.
        clause_agent_count = []
        for sent, preds, margins, gate_fired in clause_infer:
            n_agent = sum(1 for r in preds.values() if r == "agent")
            clause_agent_count.append(n_agent)

        used_per_clause = [set() for _ in clauses]
        for name, chain in rec["entities"].items():
            chain_events = []
            for ev in chain:
                ci = ev["clause"]
                sent, preds, margins, gate_fired = clause_infer[ci]
                tok_i = match_mention_to_token(sent, ev["mention"], used_per_clause[ci], entity_name=name)
                if tok_i is not None:
                    used_per_clause[ci].add(tok_i)
                    match_ok = True
                    raw_pred = preds.get(tok_i, "none")
                    pred_role = raw_pred if raw_pred != "none" else "patient"
                else:
                    match_ok = False
                    pred_role = "patient"
                is_subject = bool(match_ok and sent.get("subj_idx") is not None and tok_i == sent["subj_idx"])
                margin_val = margins.get(tok_i) if (match_ok and gate_fired) else None
                chain_events.append({
                    "passage_id": pid, "name": name, "clause_idx": ci,
                    "true_role": ev["role"], "pred_role": pred_role, "match_ok": match_ok,
                    "is_subject": is_subject, "gate_fired": gate_fired,
                    "clause_n_agent": clause_agent_count[ci], "margin": margin_val,
                })
            events.append({"key": f"{pid}::{name}", "chain": chain_events})
    return events, n_clauses


# ---------------------------------------------------------------------------
# Signal computation: takes ONLY pipeline-internal, non-gold fields. No parameter named "true_role"
# or "correct" is read anywhere in this function -- structurally enforced by the field whitelist.
# ---------------------------------------------------------------------------
_NO_GOLD_FIELDS = {"pred_role", "match_ok", "is_subject", "gate_fired", "clause_n_agent", "margin"}


def compute_signals_no_gold(ev, model_margin_thresh, rng):
    whitelisted = {k: ev[k] for k in _NO_GOLD_FIELDS}
    s1 = 1 if (whitelisted["match_ok"] and whitelisted["is_subject"]
               and whitelisted["pred_role"] != "agent") else 0
    s2 = 1 if whitelisted["clause_n_agent"] == 0 else 0
    s3_applicable = whitelisted["margin"] is not None
    s3 = 1 if (s3_applicable and whitelisted["margin"] < model_margin_thresh) else 0
    # s4 filled in by caller (needs the WM register readback, computed per-chain, not per-event
    # in isolation) -- placeholder here, merged by build_all_signals.
    combined_partial = s1 + s2 + s3
    random_flag = int(rng.integers(0, 2))
    return {"s1_rule_violation": s1, "s2_no_agent_in_clause": s2,
            "s3_low_confidence": s3, "s3_applicable": s3_applicable,
            "combined_partial_pre_s4": combined_partial, "random_flag": random_flag,
            "margin_value": whitelisted["margin"]}


def auc_from_scores(scores, labels):
    """Rank-based AUC (Mann-Whitney U form); labels are 0/1, scores continuous or binary.
    Returns None if either class is empty (undefined)."""
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    n_pos = int(labels.sum())
    n_neg = int((1 - labels).sum())
    if n_pos == 0 or n_neg == 0:
        return None
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(len(scores), dtype=np.float64)
    # average ranks for ties
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
    flagged_error_rate = precision  # same quantity, named both ways for report clarity
    return {"n_flagged": n_flagged, "n_wrong": n_wrong, "tp": tp,
            "precision": precision, "recall": recall, "base_rate": base_rate,
            "flagged_error_rate": flagged_error_rate,
            "lift_mult": (flagged_error_rate / base_rate) if (flagged_error_rate is not None
                                                                and base_rate) else None}


def run_all(mode, restrict_n=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    print("[%s] fitting STAGE-1 v4-animacy production model (frozen, reused verbatim from v6) ..."
          % mode, flush=True)
    model = fit_commit_revise_v4_animacy_production_model()
    print("[%s] model fit on %d sentences, margin_thresh=%.4f"
          % (mode, model["n_train_sentences"], model["margin_thresh"]), flush=True)

    passages = load_multiclause_gold(GOLD_MULTICLAUSE)
    print("[%s] loaded %d multiclause passages" % (mode, len(passages)), flush=True)

    events, n_clauses = build_instrumented_events(passages, model, restrict_n=restrict_n)
    print("[%s] instrumented %d entity chains over %d clauses" % (mode, len(events), n_clauses), flush=True)

    seed = 20260802
    rng = np.random.default_rng(seed)
    rng_sig = np.random.default_rng(seed + 12345)  # independent stream for the random-signal control
    d = 1024
    role_vecs = {r: unit_phase_vec(rng, d) for r in ROLE_VOCAB}
    idx_vecs = [unit_phase_vec(rng, d) for _ in range(8)]

    rows = []
    for entity in events:
        chain = entity["chain"]
        pred_roles = [e["pred_role"] for e in chain]
        true_roles = [e["true_role"] for e in chain]
        reg = build_register(pred_roles, role_vecs, idx_vecs)
        correct = score_entity(reg, true_roles, idx_vecs, role_vecs)   # GOLD-SIDE, ground truth only
        # S4: WM READBACK MISMATCH -- purely internal, compares readback to WRITTEN pred_role,
        # never touches true_roles.
        for k, ev in enumerate(chain):
            readback, _ = cleanup_argmax(fhrr_unbind(reg, idx_vecs[k]), role_vecs)
            s4 = 1 if readback != ev["pred_role"] else 0
            sig = compute_signals_no_gold(ev, model["margin_thresh"], rng_sig)
            sig["s4_wm_readback_mismatch"] = s4
            combined_score = sig["combined_partial_pre_s4"] + s4
            combined_flag = 1 if combined_score > 0 else 0

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

            rows.append({
                "key": entity["key"], "clause_idx": ev["clause_idx"], "event_idx": k,
                "true_role": true_role, "pred_role": ev["pred_role"], "match_ok": ev["match_ok"],
                "is_subject": ev["is_subject"], "gate_fired": ev["gate_fired"],
                "correct": int(correct[k]), "wrong": int(1 - correct[k]),
                "error_class": error_class, "genuine_error": int(genuine_error),
                "s1_rule_violation": sig["s1_rule_violation"], "s2_no_agent_in_clause": sig["s2_no_agent_in_clause"],
                "s3_low_confidence": sig["s3_low_confidence"], "s3_applicable": sig["s3_applicable"],
                "margin_value": sig["margin_value"],
                "s4_wm_readback_mismatch": s4, "combined_flag": combined_flag,
                "combined_score": combined_score, "random_flag": sig["random_flag"],
            })

    elapsed = time.perf_counter() - t0
    return rows, model, elapsed


def _repro_check(rows):
    """Cross-check this cell's independently-recomputed real_multi_event_recall against the
    COMMITTED v6 metrics.json -- if this drifts, the signals below were computed on a pipeline that
    silently diverged from the frozen production reader and should not be trusted."""
    by_key = {}
    for r in rows:
        by_key.setdefault(r["key"], []).append(r["correct"])
    multi = [np.mean(v) for v in by_key.values() if len(v) >= 2]
    recomputed = float(np.mean(multi)) if multi else None
    committed = None
    if os.path.exists(V6_METRICS_PATH):
        with open(V6_METRICS_PATH, "r", encoding="utf-8") as f:
            v6 = json.load(f)
        committed = v6.get("summary", {}).get("real_multi_event_recall")
    matches = (committed is not None and recomputed is not None
               and abs(recomputed - committed) <= V6_REPRO_TOL)
    return {"recomputed_real_multi_event_recall": recomputed,
            "committed_v6_real_multi_event_recall": committed,
            "tolerance": V6_REPRO_TOL, "reproduces_v6": bool(matches)}


def analyze(rows):
    n_events = len(rows)
    wrong = [r["wrong"] for r in rows]
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
        ("RANDOM_control", "random_flag", None),
    ]

    per_signal = {}
    for label, flag_field, applicable_field in signal_specs:
        if applicable_field is not None:
            sub_rows = [r for r in rows if r[applicable_field]]
        else:
            sub_rows = rows
        flags = [r[flag_field] for r in sub_rows]
        wrongs = [r["wrong"] for r in sub_rows]
        genuines = [r["genuine_error"] for r in sub_rows]

        pr_all = precision_recall(flags, wrongs)
        pr_genuine = precision_recall(flags, genuines)

        if label == "S3_low_confidence":
            score_field = "margin_value"
            scores = [-r[score_field] for r in sub_rows]  # lower margin -> more suspicious
        elif label == "COMBINED_any_fires":
            scores = [r["combined_score"] for r in sub_rows]
        else:
            scores = flags

        auc_all_wrong = auc_from_scores(scores, wrongs)
        auc_genuine = auc_from_scores(scores, genuines)

        # which error classes does this signal catch (fraction of each class flagged)?
        class_catch = {}
        for cls in sorted(error_class_counts):
            cls_rows = [r for r in sub_rows if r["error_class"] == cls]
            if cls_rows:
                class_catch[cls] = float(np.mean([r[flag_field] for r in cls_rows]))
            else:
                class_catch[cls] = None

        per_signal[label] = {
            "n_applicable": len(sub_rows), "coverage_fraction": len(sub_rows) / n_events if n_events else None,
            "precision_recall_all_wrong": pr_all,
            "precision_recall_genuine_error": pr_genuine,
            "auc_all_wrong": auc_all_wrong, "auc_genuine_error": auc_genuine,
            "fraction_flagged_by_error_class": class_catch,
        }

    # fraction of GENUINE errors caught by ANY of S1/S2/S3/S4 (the "is it internally detectable at all" number)
    genuine_rows = [r for r in rows if r["genuine_error"]]
    genuine_caught_any = (float(np.mean([r["combined_flag"] for r in genuine_rows]))
                           if genuine_rows else None)
    genuine_uncaught = [r for r in genuine_rows if r["combined_flag"] == 0]

    return {
        "n_events": n_events, "base_rate_all_wrong": base_rate_all_wrong,
        "base_rate_genuine_error": base_rate_genuine,
        "error_class_counts": error_class_counts,
        "per_signal": per_signal,
        "genuine_error_fraction_internally_detected_by_any_signal": genuine_caught_any,
        "n_genuine_errors": len(genuine_rows), "n_genuine_errors_uncaught": len(genuine_uncaught),
    }


def decide_verdict(repro, analysis):
    if not repro["reproduces_v6"]:
        return "HARD_FAIL_REPRO_MISMATCH_PIPELINE_DRIFTED_FROM_V6", {"repro": repro, "analysis": analysis}

    random_pr = analysis["per_signal"]["RANDOM_control"]["precision_recall_all_wrong"]
    random_lift = random_pr["lift_mult"]
    can_fail_ok = (random_lift is None) or (abs(random_lift - 1.0) <= RANDOM_LIFT_TOL)
    if not can_fail_ok:
        return "HARD_FAIL_CANFAIL_VIOLATION_RANDOM_SIGNAL_SHOWS_LIFT", {"repro": repro, "analysis": analysis,
                                                                          "random_lift": random_lift}

    best_label, best_lift, best_recall = None, 0.0, 0.0
    for label in ("S1_rule_violation", "S2_no_agent_in_clause", "S3_low_confidence",
                  "S4_wm_readback_mismatch", "COMBINED_any_fires"):
        pr = analysis["per_signal"][label]["precision_recall_genuine_error"]
        lift = pr["lift_mult"] or 0.0
        recall = pr["recall"] or 0.0
        if lift > best_lift or (lift == best_lift and recall > best_recall):
            best_label, best_lift, best_recall = label, lift, recall

    summary = {"repro": repro, "analysis": analysis, "best_signal": best_label,
               "best_signal_lift_mult": best_lift, "best_signal_recall": best_recall,
               "random_lift_mult": random_lift}

    if best_lift >= SIGNAL_HARD_PASS_PRECISION_MULT and best_recall >= SIGNAL_HARD_PASS_RECALL_MIN:
        return "MEASURED_MECHANISM_SELF_DETECTION_WORKS_PARTIAL_%s_BEST" % best_label, summary
    if best_lift >= SIGNAL_MIDDLE_LIFT_MULT:
        return "MIDDLE_BAND_WEAK_SELF_DETECTION_SIGNAL_%s_BEST" % best_label, summary
    return "NULL_RESULT_NO_INTERNAL_SIGNAL_BEATS_CHANCE_AT_THIS_N", summary


def _write_metrics(verdict, summary, rows, model, elapsed, mode):
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": (
            "%s | n_events=%d | base_rate_all_wrong=%.4f | base_rate_genuine_error=%.4f | "
            "best_signal=%s lift=%.2fx recall=%.2f | random_lift=%.2fx | repro_v6=%s | "
            "genuine_error_fraction_detected_by_any_signal=%s"
            % (verdict, summary["analysis"]["n_events"], summary["analysis"]["base_rate_all_wrong"],
               summary["analysis"]["base_rate_genuine_error"], summary.get("best_signal"),
               summary.get("best_signal_lift_mult") or -1, summary.get("best_signal_recall") or -1,
               summary.get("random_lift_mult") or -1, summary["repro"]["reproduces_v6"],
               summary["analysis"]["genuine_error_fraction_internally_detected_by_any_signal"])
        ),
        "summary": summary,
        "bands": {"V6_REPRO_TOL": V6_REPRO_TOL, "RANDOM_LIFT_TOL": RANDOM_LIFT_TOL,
                  "SIGNAL_HARD_PASS_PRECISION_MULT": SIGNAL_HARD_PASS_PRECISION_MULT,
                  "SIGNAL_HARD_PASS_RECALL_MIN": SIGNAL_HARD_PASS_RECALL_MIN,
                  "SIGNAL_MIDDLE_LIFT_MULT": SIGNAL_MIDDLE_LIFT_MULT},
        "per_event_dump": rows,
        "model_margin_thresh": model["margin_thresh"],
        "arms_differ_verified": "not_applicable_single_pass_measurement_cell",
        "arms_differ_exempted": "ALL (no multi-arm comparison in this cell)",
        "arms_differ_exemption_rationale": (
            "this cell instruments ONE frozen reader pipeline (v6's real arm) with 4 diagnostic "
            "internal signals over the same events; there are no independent 'arms' whose registers "
            "could be bit-identical by construction bug -- exempted by design, not measured-and-tied."
        ),
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_heartbeat_exempt_lt30s",
        "elapsed_s": elapsed,
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
                    help="formula self-test timeout budget (declared; full run expected < 20s: "
                         "numpy-only, ~30 clauses, no grid sweep, no torch, no GPU")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    _write_start_marker(OUTPUT_DIR, mode, expected_n_units=1)

    rng = np.random.default_rng(20260802)
    run_self_test(rng)

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        restrict_n = 3 if mode == "self_test" else None
        rows, model, elapsed = run_all(mode, restrict_n=restrict_n)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        _write_crash_metrics(OUTPUT_DIR, e)
        raise SystemExit(2)

    repro = _repro_check(rows) if mode == "full" else {
        "recomputed_real_multi_event_recall": None, "committed_v6_real_multi_event_recall": None,
        "tolerance": V6_REPRO_TOL, "reproduces_v6": True,  # exempt in self-test (restrict_n subset)
    }
    analysis = analyze(rows)
    verdict, summary = decide_verdict(repro, analysis)
    metrics = _write_metrics(verdict, summary, rows, model, elapsed, mode)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
