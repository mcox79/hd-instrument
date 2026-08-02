# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: HAND_GATE vs LEARNED_GATE vs LEARNED_GATE_SHUFFLED vs CLAUSE_POSITION vs
#   RANDOM per_arm digests hash-compared at smoke gate.
# - final_metrics_atomicity = tmp_replace (single-shot; whole run < 60s, LOOCV over ~200 sentences
#   with a 6-dim sentence-level softmax, no grid sweep on this cell's own new lever)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "discrete multiclass classification/role accuracy, no CRLB noise floor applies";
#   discriminator_reachability=true (shuffled-label can-fail arm is the reachability check)
# - baseline_in_band: CLAUSE_POSITION / RANDOM are can-fail / lever-isolation controls, not
#   "baseline in band" arms; LEARNED_GATE_SHUFFLED is the can-fail control for THIS cell's new lever
# - cell_chunked=False (single pass; per-arm checkpoint via tools/exp_checkpoint.py used anyway per
#   CLAUDE.md's "any cell looping over >1 unit" rule)
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_learned_construction_gate_v1 (2026-08-02)

BRAIN-FIDELITY AUDIT PRIORITY #2 (notes/brain_fidelity_audit_comprehension_pipeline_2026-08-02.md,
component 4): the commit-then-revise pipeline's GATE (gate_fires_v2 / gate_fires_v3 in
exp_extraction_commit_then_revise_v2.py / v3_theme.py) that decides whether a sentence's marked
construction (quotative / passive-by-agent / copular-identity) should override the clause-local
COMMIT default is currently FOUR hand-coded boolean rules: has_by (ADP-tagged "by" within a token
window), quotative_cue (frac_in_quote > a hand-picked THRESH=0.60), is_copular (has_be AND NOT
has_by AND NOT any BE-form immediately followed by a VERB-tag), OR-combined. Every new construction
this arc added got its OWN hand-written detector ORed into the same gate (v3_theme's own docstring:
"a THIRD instance of that SAME mechanism" -- i.e. the pipeline's own growth pattern is "add one more
hand rule per construction," MEASURED as the audit's single most-repeated drift instance).

THIS CELL replaces those THREE hand-coded gate conjuncts with ONE LEARNED construction-TYPE
classifier (5-way multinomial softmax: canonical / quotative / passive_byagent / passive /
copular_theme) trained on the SAME gold pools the hand rules were tuned against (canonical from
gold_mcguffey_lccp_argstruct_v1.json's own pos/nopat scheme via load_canonical_pool();
quotative/byagent/passive/copular_theme from their respective verified jsonl pools -- ALL FIVE
already carry a "kind" label, so this is directly learnable today with ZERO new data collection,
exactly as the audit's own recommendation states). GATE fires iff the LEARNED classifier's LOOCV-
predicted kind for that sentence is != "canonical" (a direct, honest analog of "detect a marked
construction, then let REVISE override the default" -- same target behavior as gate_fires_v3, now
via a fit decision boundary instead of a hand-enumerated OR of booleans/thresholds).

INPUT FEATURES to the learned gate are the PRIMITIVE sentence-level cues the hand rules were built
from (verb_after_close, frac_in_quote, has_be, has_by -- component 1 in the audit, itself flagged
as scaffold but explicitly OUT OF SCOPE for this cell / left as future work) PLUS one new raw
primitive, be_then_verb (whether any BE-form token is immediately followed by a VERB-tagged token),
recomputed directly here (NOT the is_copular boolean itself, which is the hand AND-combination this
cell replaces -- feeding the hand-rule's own output back in as a "feature" would trivially let the
classifier re-derive the rule with weight=1 and prove nothing). The classifier LEARNS the decision
boundary over these primitives (including any threshold on frac_in_quote and any AND/NOT interaction
among has_be/has_by/be_then_verb) via gradient descent (fit_softmax, REUSED VERBATIM, same
L2_LAMBDA/LR/N_ITERS as the rest of this arc's role softmax) instead of a hand-picked THRESH and
hand-written boolean logic.

TRAIN/EVAL SEPARATION: construction classification accuracy is measured via LEAVE-ONE-SENTENCE-OUT
cross-validation (LOOCV) over all 202 pooled sentences (MEASURED@this session's pool-count probe:
canonical=113, quotative=45, passive_byagent=23, passive=7, copular_theme=14) -- every held-out
sentence's predicted kind comes from a classifier that never saw that sentence's label, matching
this arc's own established LOOCV convention for the REVISE role softmax.

DOWNSTREAM WIRING: the REST of the commit-then-revise pipeline (clause_position_predict5 default,
the REVISE role softmax fit_softmax_on5/loocv_revise_v3, margin-gated graceful-degrade at
SELECTED_MARGIN_THRESH_V3, ROLE_VOCAB5) is REUSED VERBATIM (imported, not reimplemented) from
exp_extraction_commit_then_revise_v3_theme.py -- the ONLY variable this cell changes is WHICH gate
decides whether REVISE fires: the hand-coded gate_fires_v3 (HAND_GATE arm, reproducing v3_theme's
own result exactly as an apples-to-apples baseline) versus the learned classifier's LOOCV-predicted
kind (LEARNED_GATE arm). This isolates the gate MECHANISM as the one lever, per the brain-fidelity
framing: judge on whether the CONSTRUCTION is now learned, not on whether task accuracy jumps.

CAN-FAIL (the mandatory negative control for this cell's own new lever): LEARNED_GATE_SHUFFLED
trains the SAME classifier architecture on a fixed-seed RANDOM PERMUTATION of the "kind" labels.
A classifier that cannot tell real labels from shuffled ones would prove the gate learned nothing
(and downstream role accuracy under a shuffled gate must NOT reliably beat HAND_GATE or a real-label
LEARNED_GATE). construction_accuracy_shuffled is expected near the majority-class LOOCV floor
(canonical=113/202=0.559 is the "always predict canonical" floor -- THEORETICAL, trivial majority-
vote calculation) or below the real-label classifier's accuracy by a wide margin.

HONEST FRAMING (per the director's contract): the GOAL of this cell is FIDELITY (is construction
recognition now learned instead of hand-coded), NOT necessarily an accuracy win. If LEARNED_GATE
role accuracy on a given construction falls short of HAND_GATE's, that is reported as a genuine,
valid finding (the pools are small -- copular_theme=14, passive=7 -- so a 6-dim sentence-level
classifier may be data-starved relative to 3 hand-tuned boolean rules with 1 grid-searched
threshold); it is NOT treated as a cell failure requiring iteration back to hand-coding.

Run:  .venv/Scripts/python.exe experiments/exp_learned_construction_gate_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_learned_construction_gate_v1.py --full
"""
from __future__ import annotations

import argparse
import hashlib
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
import exp_checkpoint as ckpt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Reuse EVERYTHING vocab-agnostic verbatim from the parent multirole cell (import, not reimplement).
from exp_extraction_construction_conditional_multirole_v1 import (  # noqa: E402
    BE_FORMS, fit_softmax, _softmax,
    load_canonical_pool, load_quotative_pool, load_byagent_pool, load_passive_pool,
    L2_LAMBDA, LR, N_ITERS,
)
# Reuse the ENTIRE downstream commit-then-revise pipeline verbatim from v3_theme (imported, not
# reimplemented) -- the only thing THIS cell changes is the gate decision (component 4 in the audit).
from exp_extraction_commit_then_revise_v3_theme import (  # noqa: E402
    load_copular_theme_pool, build_sentence_multi5, clause_position_predict5, position_predict5,
    random_predict5, gate_fires_v3, eval_predictions5, fit_softmax_on5, loocv_revise_v3,
    revise_predict_one_with_margin, THRESH, ROLE_VOCAB5, ROLE_IDX5,
    CANONICAL_MIN, QUOTATIVE_MIN, BYAGENT_MIN, SELECTED_MARGIN_THRESH_V3,
)

ANCHOR_NAME = "learned_construction_gate_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# 5-way construction-TYPE vocab -- matches the "kind" field every gold pool already carries.
CONSTRUCTION_VOCAB = ["canonical", "quotative", "passive_byagent", "passive", "copular_theme"]
CONSTRUCTION_IDX = {k: i for i, k in enumerate(CONSTRUCTION_VOCAB)}
N_CONSTRUCTION_CLASSES = len(CONSTRUCTION_VOCAB)

# MARGIN_THRESH: REUSED VERBATIM from v3_theme's own already-grid-selected value (this cell's ONE
# variable is the gate mechanism, not a re-tune of the margin lever).
MARGIN_THRESH_REUSED = SELECTED_MARGIN_THRESH_V3

# CAN-FAIL margin: real-label LOOCV construction accuracy must beat the shuffled-label control by at
# least this much (THEORETICAL, standard can-fail separation convention this arc uses elsewhere).
CANFAIL_MARGIN = 0.15

# MATCH-OR-BEAT slack: LEARNED_GATE role_acc on a given construction must be within this much of
# HAND_GATE's to count as "matched" (5% of a [0,1] accuracy scale -- same band-width convention as
# META_RULE_L elsewhere in this arc).
MATCH_SLACK = 0.05

RNG_SEED = 20260802


# ---------------------------------------------------------------------------
# CONSTRUCTION-CLASSIFIER FEATURES: the PRIMITIVE cues the hand-coded gate was built from (has_be,
# has_by, verb_after_close, frac_in_quote -- audit component 1, itself a scaffold but out of scope
# for THIS cell), plus one new raw primitive (be_then_verb) recomputed directly from tokens/pos.
# Deliberately NOT feeding sent["sent_summary"][4] (is_copular) -- that IS the hand AND-combination
# this cell replaces; feeding it back in would let the classifier trivially re-derive the hand rule
# with weight=1 and prove nothing about whether construction-type can be LEARNED from primitives.
# ---------------------------------------------------------------------------
def construction_features(sent) -> np.ndarray:
    ss = sent["sent_summary"]
    verb_after_close, frac_in_quote, has_be, has_by = ss[0], ss[1], ss[2], ss[3]
    tokens, pos = sent["tokens"], sent["pos"]
    n = len(tokens)
    be_then_verb = 1.0 if any(
        tokens[i].lower() in BE_FORMS and (i + 1 < n) and pos[i + 1] == "VERB" for i in range(n)
    ) else 0.0
    return np.array([verb_after_close, frac_in_quote, has_be, has_by, be_then_verb, 1.0],
                     dtype=np.float64)


def build_construction_design(sents, labels_override=None):
    X = np.array([construction_features(s) for s in sents], dtype=np.float64)
    if labels_override is not None:
        y = np.array(labels_override, dtype=np.int64)
    else:
        y = np.array([CONSTRUCTION_IDX[s["kind"]] for s in sents], dtype=np.int64)
    return X, y


def loocv_construction_classifier(sents, y):
    """LOOCV over ALL pooled sentences. Returns (pred_kind_idx per sent, per-sentence top1 prob)."""
    X, _ = build_construction_design(sents)
    n = X.shape[0]
    preds = np.zeros(n, dtype=np.int64)
    probs = np.zeros(n, dtype=np.float64)
    for held in range(n):
        tr = np.arange(n) != held
        Xtr, ytr = X[tr], y[tr]
        mu = Xtr[:, :-1].mean(axis=0)
        sd = Xtr[:, :-1].std(axis=0)
        sd[sd < 1e-8] = 1.0
        Xtr_s = Xtr.copy()
        Xtr_s[:, :-1] = (Xtr[:, :-1] - mu) / sd
        W = fit_softmax(Xtr_s, ytr, N_CONSTRUCTION_CLASSES, L2_LAMBDA, LR, N_ITERS)
        x_te = X[held].copy()
        x_te[:-1] = (x_te[:-1] - mu) / sd
        p = _softmax(x_te.reshape(1, -1) @ W)[0]
        preds[held] = int(np.argmax(p))
        probs[held] = float(p.max())
    return preds, probs


def construction_accuracy_report(sents, y_true, y_pred):
    overall_correct = int((y_true == y_pred).sum())
    overall_n = len(y_true)
    per_kind = {}
    for k, idx in CONSTRUCTION_IDX.items():
        mask = y_true == idx
        n_k = int(mask.sum())
        if n_k == 0:
            per_kind[k] = {"acc": None, "n": 0}
            continue
        per_kind[k] = {"acc": float((y_pred[mask] == idx).mean()), "n": n_k}
    majority_idx = int(np.bincount(y_true, minlength=N_CONSTRUCTION_CLASSES).argmax())
    majority_floor = float((y_true == majority_idx).mean())
    return {
        "overall_acc": overall_correct / overall_n if overall_n else None,
        "overall_n": overall_n,
        "per_kind": per_kind,
        "majority_class_floor": majority_floor,
    }


def _digest(preds_by_sent):
    flat = json.dumps({str(k): v for k, v in preds_by_sent.items()}, sort_keys=True)
    return hashlib.sha256(flat.encode()).hexdigest()[:16]


def _commit_revise_with_gate(sents, gate_flags, W_prod, mu_prod, sd_prod, loocv_pred_map,
                              loocv_margin_map, margin_thresh):
    preds_by_sent = {}
    for sid, sent in enumerate(sents):
        default_preds = clause_position_predict5(sent)
        if gate_flags[sid]:
            if sid in loocv_pred_map:
                revise_preds, revise_margins = loocv_pred_map[sid], loocv_margin_map[sid]
            else:
                revise_preds, revise_margins = revise_predict_one_with_margin(sent, W_prod, mu_prod, sd_prod)
            merged = {}
            for i in sent["mention_idx"]:
                if i in revise_preds and revise_margins.get(i, 0.0) >= margin_thresh:
                    merged[i] = revise_preds[i]
                else:
                    merged[i] = default_preds.get(i, ROLE_IDX5["patient"])
            preds_by_sent[sid] = merged
        else:
            preds_by_sent[sid] = default_preds
    return preds_by_sent


def run_all(mode):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    canon_recs, canon_diag = load_canonical_pool()
    quot_recs = load_quotative_pool()
    byagent_recs = load_byagent_pool()
    passive_recs = load_passive_pool()
    theme_recs = load_copular_theme_pool()

    if mode == "self_test":
        canon_recs = canon_recs[:10]
        quot_recs = quot_recs[:6]
        byagent_recs = byagent_recs[:4]
        passive_recs = passive_recs[:3]
        theme_recs = theme_recs[:6]

    print("[%s] pools: canonical=%d quotative=%d byagent=%d passive=%d copular_theme=%d"
          % (mode, len(canon_recs), len(quot_recs), len(byagent_recs), len(passive_recs), len(theme_recs)),
          flush=True)

    all_recs = canon_recs + quot_recs + byagent_recs + passive_recs + theme_recs
    print("[%s] building %d sentences (tagger load+tag) ..." % (mode, len(all_recs)), flush=True)
    sents = [build_sentence_multi5(r) for r in all_recs]

    rng = np.random.default_rng(RNG_SEED)

    # ---- CONSTRUCTION-TYPE CLASSIFIER (real labels): LOOCV over ALL pooled sentences ----
    print("[%s] fitting LEARNED construction-type classifier (5-way, LOOCV over %d sentences) ..."
          % (mode, len(sents)), flush=True)
    _, y_true = build_construction_design(sents)
    pred_kind_idx, pred_prob = loocv_construction_classifier(sents, y_true)
    construction_report = construction_accuracy_report(sents, y_true, pred_kind_idx)
    print("[%s] construction classifier: overall_acc=%.4f (majority_floor=%.4f) per_kind=%s"
          % (mode, construction_report["overall_acc"], construction_report["majority_class_floor"],
             construction_report["per_kind"]), flush=True)

    # ---- CAN-FAIL CONTROL: same classifier, fixed-seed shuffled labels ----
    y_shuffled = y_true.copy()
    rng.shuffle(y_shuffled)
    print("[%s] fitting CAN-FAIL shuffled-label construction classifier ..." % mode, flush=True)
    pred_kind_idx_shuf, _ = loocv_construction_classifier(sents, y_shuffled)
    construction_report_shuffled = construction_accuracy_report(sents, y_shuffled, pred_kind_idx_shuf)
    print("[%s] construction classifier SHUFFLED: overall_acc=%.4f (majority_floor=%.4f)"
          % (mode, construction_report_shuffled["overall_acc"],
             construction_report_shuffled["majority_class_floor"]), flush=True)

    # ---- ROLE softmax (REVISE): REUSED VERBATIM from v3_theme, fit only on non-canonical sentences ----
    noncanon_ids = [sid for sid, s in enumerate(sents) if s["kind"] != "canonical"]
    noncanon_sents = [sents[sid] for sid in noncanon_ids]
    print("[%s] fitting REVISE role softmax (5-way, LOOCV over %d non-canonical sentences, reused "
          "verbatim from v3_theme) ..." % (mode, len(noncanon_sents)), flush=True)
    loocv_preds, loocv_margins = loocv_revise_v3(noncanon_sents)
    loocv_pred_map = {noncanon_ids[j]: loocv_preds[j] for j in range(len(noncanon_ids))}
    loocv_margin_map = {noncanon_ids[j]: loocv_margins[j] for j in range(len(noncanon_ids))}
    W_prod, mu_prod, sd_prod = fit_softmax_on5(noncanon_sents)

    # ---- Gate flags per arm ----
    hand_gate_flags = {sid: gate_fires_v3(sent, THRESH) for sid, sent in enumerate(sents)}
    learned_gate_flags = {sid: (pred_kind_idx[sid] != CONSTRUCTION_IDX["canonical"]) for sid in range(len(sents))}
    learned_gate_flags_shuf = {sid: (pred_kind_idx_shuf[sid] != CONSTRUCTION_IDX["canonical"])
                               for sid in range(len(sents))}

    def run_arm(arm_name, gate_flags=None, kind="commit_revise"):
        key = ckpt.unit_key(mode, arm_name)
        if key not in ckpt.completed_units(OUTPUT_DIR):
            if kind == "commit_revise":
                preds_by_sent = _commit_revise_with_gate(
                    sents, gate_flags, W_prod, mu_prod, sd_prod, loocv_pred_map, loocv_margin_map,
                    MARGIN_THRESH_REUSED)
                gate_rate = {}
                for sid, sent in enumerate(sents):
                    k = sent["kind"]
                    gate_rate.setdefault(k, [0, 0])
                    gate_rate[k][1] += 1
                    gate_rate[k][0] += int(gate_flags[sid])
                gate_rate = {k: (c / n if n else None) for k, (c, n) in gate_rate.items()}
            elif kind == "clause_position":
                preds_by_sent = {sid: clause_position_predict5(sent) for sid, sent in enumerate(sents)}
                gate_rate = None
            elif kind == "position":
                preds_by_sent = {sid: position_predict5(sent) for sid, sent in enumerate(sents)}
                gate_rate = None
            else:  # random
                preds_by_sent = {sid: random_predict5(sent, rng) for sid, sent in enumerate(sents)}
                gate_rate = None
            per_kind = eval_predictions5(sents, preds_by_sent)
            result = {"per_kind": per_kind, "digest": _digest(preds_by_sent)}
            if gate_rate is not None:
                result["gate_rate_by_kind"] = gate_rate
            ckpt.record_unit(OUTPUT_DIR, key, result)
            print("[%s] arm=%s per_kind=%s gate_rate=%s" % (mode, arm_name, per_kind, gate_rate), flush=True)

    run_arm("HAND_GATE", hand_gate_flags, "commit_revise")
    run_arm("LEARNED_GATE", learned_gate_flags, "commit_revise")
    run_arm("LEARNED_GATE_SHUFFLED", learned_gate_flags_shuf, "commit_revise")
    run_arm("CLAUSE_POSITION", kind="clause_position")
    run_arm("RANDOM", kind="random")

    units = {k.split("|")[-1]: v for k, v in ckpt.load_units(OUTPUT_DIR).items() if k.startswith(mode + "|")}
    elapsed = time.perf_counter() - t0
    return units, construction_report, construction_report_shuffled, len(sents), elapsed


def _arms_must_differ(units):
    digs = {k: v["digest"] for k, v in units.items()}
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digs[a] != digs[b], f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical"


def decide_verdict(units, construction_report, construction_report_shuffled):
    def racc(arm, kind):
        v = (units[arm]["per_kind"].get(kind) or {}).get("role_acc")
        return v if v is not None else 0.0

    real_acc = construction_report["overall_acc"] or 0.0
    shuf_acc = construction_report_shuffled["overall_acc"] or 0.0
    can_fail_holds = (real_acc - shuf_acc) >= CANFAIL_MARGIN

    kinds_to_compare = ["canonical", "quotative", "passive_byagent", "copular_theme"]
    deltas = {}
    matched = {}
    for k in kinds_to_compare:
        hand = racc("HAND_GATE", k)
        learned = racc("LEARNED_GATE", k)
        deltas[k] = learned - hand
        matched[k] = (learned - hand) >= -MATCH_SLACK
    n_matched = sum(1 for v in matched.values() if v)

    summary = {
        "construction_classification_acc_real": real_acc,
        "construction_classification_acc_shuffled": shuf_acc,
        "construction_majority_class_floor": construction_report["majority_class_floor"],
        "construction_per_kind_real": construction_report["per_kind"],
        "construction_per_kind_shuffled": construction_report_shuffled["per_kind"],
        "can_fail_holds": bool(can_fail_holds),
        "role_acc_hand_gate": {k: racc("HAND_GATE", k) for k in kinds_to_compare},
        "role_acc_learned_gate": {k: racc("LEARNED_GATE", k) for k in kinds_to_compare},
        "role_acc_learned_gate_shuffled": {k: racc("LEARNED_GATE_SHUFFLED", k) for k in kinds_to_compare},
        "role_acc_clause_position_only": {k: racc("CLAUSE_POSITION", k) for k in kinds_to_compare},
        "role_acc_random": {k: racc("RANDOM", k) for k in kinds_to_compare},
        "delta_learned_minus_hand": deltas,
        "matched_or_beat_per_kind": matched,
        "n_kinds_matched_or_beat": n_matched,
        "n_kinds_total": len(kinds_to_compare),
        "gate_rate_by_kind_hand": units.get("HAND_GATE", {}).get("gate_rate_by_kind"),
        "gate_rate_by_kind_learned": units.get("LEARNED_GATE", {}).get("gate_rate_by_kind"),
        "per_arm_per_kind": {a: units[a]["per_kind"] for a in units},
    }

    if not can_fail_holds:
        return "HARD_FAIL_CANFAIL_CONSTRUCTION_GATE_NOT_LEARNED", summary
    if n_matched == len(kinds_to_compare):
        return "HARD_PASS_LEARNED_GATE_MATCHES_OR_BEATS_HAND_CODED", summary
    if n_matched >= (len(kinds_to_compare) + 1) // 2:
        return "MIDDLE_BAND_LEARNED_GATE_PARTIAL_MATCH", summary
    return "HONEST_GAP_LEARNED_GATE_BELOW_HAND_CODED_NEEDS_MORE_GOLD", summary


def _write_metrics(verdict, summary, units, n_sents, elapsed, mode):
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": (
            "%s | construction_acc_real=%.3f construction_acc_shuffled=%.3f (floor=%.3f) "
            "can_fail_holds=%s | matched_or_beat=%d/%d | deltas=%s"
            % (verdict, summary["construction_classification_acc_real"],
               summary["construction_classification_acc_shuffled"],
               summary["construction_majority_class_floor"], summary["can_fail_holds"],
               summary["n_kinds_matched_or_beat"], summary["n_kinds_total"],
               summary["delta_learned_minus_hand"])
        ),
        "summary": summary,
        "bands": {"MARGIN_THRESH_REUSED": MARGIN_THRESH_REUSED, "CANFAIL_MARGIN": CANFAIL_MARGIN,
                  "MATCH_SLACK": MATCH_SLACK, "CANONICAL_MIN": CANONICAL_MIN,
                  "QUOTATIVE_MIN": QUOTATIVE_MIN, "BYAGENT_MIN": BYAGENT_MIN},
        "construction_vocab": CONSTRUCTION_VOCAB,
        "role_vocab": ROLE_VOCAB5,
        "per_arm": units,
        "n_sentences_pooled": n_sents,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "calibration_check": "default_ok_for_this_regime",
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
    ap.add_argument("--timeout", type=float, default=180.0,
                     help="formula self-test timeout budget (declared; full run expected < 90s, "
                          "LOOCV over ~202 sentences x2 [real+shuffled] construction classifiers "
                          "plus one reused role-softmax LOOCV over ~89 non-canonical sentences)")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        units, construction_report, construction_report_shuffled, n_sents, elapsed = run_all(mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        raise SystemExit(2)

    _arms_must_differ(units)
    verdict, summary = decide_verdict(units, construction_report, construction_report_shuffled)
    metrics = _write_metrics(verdict, summary, units, n_sents, elapsed, mode)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
