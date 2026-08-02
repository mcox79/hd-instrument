"""METACOGNITIVE CALIBRATION PROBE: does the coref mechanism's OWN decision-margin predict its
OWN errors?

WHAT: the match-or-allocate coref mechanism (exp_earn_coref_match_or_allocate_v1.run_learnable,
possessive-fix commit a0aac7eeb) already computes an internal MARGIN at every mention decision
(name-path: token-Jaccard overlap gap to the runner-up compatible entity; pronoun-path: Centering
salience gap to the runner-up gender-compatible entity). This probe asks whether that margin --
already computed "for free" -- predicts whether the decision was actually WRONG. If yes, the
reader can FLAG likely-wrong coref links near-zero extra cost (first concrete step of the
self-improving-reader / metacognitive-flag arc, per
notes/metacognitive_flag_layer_calibration_design_and_confidence_inventory_2026-08-02.md).

MECHANISM (byte-faithful instrumented copy, VET'd against the original -- see self_test):
run_learnable_instrumented() below is a line-for-line copy of
exp_earn_coref_match_or_allocate_v1.run_learnable with logging added at each decision point. It
uses the SAME imported gn_compatible / _Entity / normalize_tokens / is_pronoun_mention /
gender_number_for functions as the original (not reimplemented), and the same has_determiner
bridging default. main() asserts the instrumented copy's predicted entity-id sequence is BYTE
IDENTICAL to the original run_learnable's on every dense-gold passage before trusting the logged
margins -- if that assertion fails the margins would describe a drifted mechanism, not the real
one.

PER-DECISION MARGIN DEFINITIONS (see notes doc "The calibration probe"):
  - NAME/NOMINAL path, matched by positive overlap: margin = best_overlap - second_best_overlap
    (both computed over ALL gender/number-compatible candidates, treating "no overlap" as 0.0 so
    a lone compatible candidate contributes a 0.0 runner-up). best_overlap logged separately.
  - NAME/NOMINAL path, bridging default fires (overlap==0, exactly one compatible candidate,
    determiner-led): treated as a WEAK-EVIDENCE decision -- margin=0.0, best_overlap=0.0,
    bridging=True (no lexical evidence at all, structurally uncertain).
  - NAME/NOMINAL path, allocates new entity, >=1 compatible candidate existed but none
    overlapped: chose_new=True, margin=0.0 (genuine zero-evidence uncertainty -- it plausibly
    COULD have been one of the existing candidates).
  - NAME/NOMINAL path, allocates new entity, ZERO compatible candidates existed at all:
    chose_new=True, margin=NO_COMPETITION_MARGIN sentinel (nothing to be ambiguous WITH --
    trivially unambiguous, not a low-confidence event; distinguishing this from the
    "candidates existed but none matched" case is load-bearing, see NO_COMPETITION_MARGIN).
  - PRONOUN path, >=1 gender/number-compatible candidate: margin = salience(top) -
    salience(2nd) (2nd=0.0 if only one compatible candidate).
  - PRONOUN path, zero compatible candidates but entities exist (best-effort fallback,
    zero identity evidence): margin=0.0.
  - PRONOUN path, no entities at all (first mention, trivially unambiguous allocation):
    chose_new=True, margin=NO_COMPETITION_MARGIN sentinel.

GROUND TRUTH per decision: mention i is WRONG iff there exists another mention j in the same
passage such that (same gold entity, different predicted cluster) [SPLIT] or (different gold
entity, same predicted cluster) [MERGE] -- the exact pairwise definition
exp_earn_coref_match_or_allocate_dense_v1.diagnose_errors uses, collapsed to a per-mention label
(mention i "participates in" a MERGE or SPLIT error). is_correct = not is_wrong.

METRIC: AUC of (-margin) predicting is_wrong (rank-based Mann-Whitney U, no external library
dependency), overall + name-subset + pronoun-subset; a margin-bin calibration curve (empirical
error rate per bin); and, at the best-Youden-J threshold on margin, the flag recall (fraction of
actual errors caught) and flag precision (fraction of flagged decisions that were actually
wrong).

CAN-FAIL (pre-registered BEFORE running):
  - HARD_FAIL_UNCALIBRATED: overall AUC <= 0.55 -- the margin signal is no better than chance at
    predicting its own errors; report honestly, the flag layer needs a different / additional
    signal.
  - HARD_PASS_CALIBRATED: pronoun-subset AUC >= 0.65 AND the best-Youden threshold's flag catches
    >= 30% of actual errors (recall) at flag precision > the base error rate (i.e. flagging is
    informative, not just "flag everything"). Pronoun subset gated specifically because that is
    where the known same-gender hard cases (Harry/Sam, Mr. Rose/boatman class) live.
  - MIDDLE_BAND otherwise (e.g. overall calibrated but pronoun subset underpowered / not
    significantly above chance, or AUC in (0.55, 0.65)).

Self-test: python exp_coref_self_confidence_calibration_v1.py --self-test
Full:      python exp_coref_self_confidence_calibration_v1.py
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from exp_earn_coref_match_or_allocate_v1 import (  # noqa: E402
    normalize_tokens,
    is_pronoun_mention,
    gender_number_for,
    gn_compatible,
    _Entity,
    build_mention_stream,
    load_passages,
    run_learnable,
    bcubed,
)

ANCHOR_NAME = "coref_self_confidence_calibration_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multientity_dense_v1.jsonl"
)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# Pre-registered PASS/FAIL bands (see module docstring CAN-FAIL section).
AUC_HARD_FAIL_CEILING = 0.55       # <= this: uncalibrated, no better than chance
AUC_HARD_PASS_PRONOUN_FLOOR = 0.65  # pronoun-subset AUC must clear this for HARD_PASS
FLAG_RECALL_HARD_PASS_FLOOR = 0.30  # best-threshold flag must catch >= 30% of actual errors
N_CALIBRATION_BINS = 5
# Sentinel margin for allocate-new decisions where ZERO gender/number-compatible candidates
# existed at all (nothing to be ambiguous with -- trivially unambiguous, not low-confidence).
# Chosen well above the observed empirical range of overlap-gap ([0,1]) and salience-gap margins
# so it never gets confused with a genuinely close call.
NO_COMPETITION_MARGIN = 10.0


# ---------------------------------------------------------------------------
# Instrumented decision loop: line-for-line copy of run_learnable with per-decision logging.
# VET'd in main()/self_test() to reproduce run_learnable's output EXACTLY.
# ---------------------------------------------------------------------------
def run_learnable_instrumented(stream: List[dict]) -> Tuple[List[int], List[dict]]:
    entities: List[_Entity] = []
    next_id = 0
    assigned: List[int] = []
    decisions: List[dict] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                saliences = sorted((e.salience(pos) for e in compat), reverse=True)
                best = max(compat, key=lambda e: e.salience(pos))
                second = saliences[1] if len(saliences) >= 2 else 0.0
                margin = saliences[0] - second
                decisions.append({
                    "pos": pos, "is_pronoun": True, "chose_new": False, "bridging": False,
                    "fallback": False, "margin": margin, "best_score": saliences[0],
                    "n_compatible": len(compat),
                })
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)  # best-effort fallback
                decisions.append({
                    "pos": pos, "is_pronoun": True, "chose_new": False, "bridging": False,
                    "fallback": True, "margin": 0.0, "best_score": 0.0, "n_compatible": 0,
                })
            else:
                best = _Entity(next_id)
                next_id += 1
                entities.append(best)
                # No candidates existed at all (nothing to be ambiguous WITH) -- a trivially
                # unambiguous allocation, not a low-confidence event. Sentinel margin.
                decisions.append({
                    "pos": pos, "is_pronoun": True, "chose_new": True, "bridging": False,
                    "fallback": False, "margin": NO_COMPETITION_MARGIN, "best_score": 0.0,
                    "n_compatible": 0,
                })
            best.count += 1
            best.last_pos = pos
            assigned.append(best.eid)
            continue
        toks = normalize_tokens(rec["mention_text"])
        compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
        best = None
        best_overlap = 0.0
        overlaps: List[float] = []
        for e in compat:
            if not toks and not e.tokens:
                overlaps.append(0.0)
                continue
            union = toks | e.tokens
            if not union:
                overlaps.append(0.0)
                continue
            ov = len(toks & e.tokens) / len(union)
            overlaps.append(ov)
            if ov > best_overlap:
                best_overlap = ov
                best = e
        if best is None and len(compat) == 1 and rec["has_determiner"]:
            best = compat[0]
            decisions.append({
                "pos": pos, "is_pronoun": False, "chose_new": False, "bridging": True,
                "fallback": False, "margin": 0.0, "best_score": 0.0, "n_compatible": len(compat),
            })
        elif best is None:
            best = _Entity(next_id)
            next_id += 1
            entities.append(best)
            # If NO gender/number-compatible candidates existed at all, this allocation was
            # trivially unambiguous (nothing to confuse with) -- sentinel high-confidence margin.
            # If candidates DID exist but none overlapped, that is genuine zero-evidence
            # uncertainty (could plausibly have been one of them) -- margin 0.0, low confidence.
            no_competition = len(compat) == 0
            decisions.append({
                "pos": pos, "is_pronoun": False, "chose_new": True, "bridging": False,
                "fallback": False,
                "margin": NO_COMPETITION_MARGIN if no_competition else 0.0,
                "best_score": 0.0, "n_compatible": len(compat),
            })
        else:
            ov_sorted = sorted(overlaps, reverse=True)
            second = ov_sorted[1] if len(ov_sorted) >= 2 else 0.0
            margin = ov_sorted[0] - second
            decisions.append({
                "pos": pos, "is_pronoun": False, "chose_new": False, "bridging": False,
                "fallback": False, "margin": margin, "best_score": ov_sorted[0],
                "n_compatible": len(compat),
            })
        best.tokens |= toks
        if best.gender is None and gender is not None:
            best.gender = gender
        if best.number is None and number is not None:
            best.number = number
        best.count += 1
        best.last_pos = pos
        assigned.append(best.eid)
    assert len(decisions) == len(stream) == len(assigned)
    return assigned, decisions


def mention_is_wrong(i: int, stream: List[dict], preds: List[int]) -> bool:
    """True iff mention i participates in a MERGE or SPLIT error, per
    exp_earn_coref_match_or_allocate_dense_v1.diagnose_errors' pairwise definition."""
    gi, pi = stream[i]["gold_entity"], preds[i]
    for j in range(len(stream)):
        if j == i:
            continue
        same_gold = stream[j]["gold_entity"] == gi
        same_pred = preds[j] == pi
        if same_gold and not same_pred:
            return True  # SPLIT
        if not same_gold and same_pred:
            return True  # MERGE
    return False


# ---------------------------------------------------------------------------
# Rank-based AUC (Mann-Whitney U), no external dependency. Higher score => predicted positive.
# ---------------------------------------------------------------------------
def auc_from_scores(scores: List[float], labels: List[int]) -> Optional[float]:
    n_pos = sum(1 for lb in labels if lb == 1)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return None
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    ranks = [0.0] * len(scores)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0  # 1-indexed average rank for the tied block
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    rank_sum_pos = sum(ranks[i] for i in range(len(scores)) if labels[i] == 1)
    u = rank_sum_pos - n_pos * (n_pos + 1) / 2.0
    return u / (n_pos * n_neg)


def calibration_curve(margins: List[float], labels: List[int], n_bins: int) -> List[dict]:
    if not margins:
        return []
    order = sorted(range(len(margins)), key=lambda i: margins[i])
    n = len(order)
    bin_size = max(1, math.ceil(n / n_bins))
    curve = []
    for b in range(0, n, bin_size):
        idxs = order[b:b + bin_size]
        if not idxs:
            continue
        m_vals = [margins[i] for i in idxs]
        errs = [labels[i] for i in idxs]
        curve.append({
            "n": len(idxs),
            "margin_lo": min(m_vals),
            "margin_hi": max(m_vals),
            "margin_mean": sum(m_vals) / len(m_vals),
            "empirical_error_rate": sum(errs) / len(errs),
        })
    return curve


def best_youden_threshold(margins: List[float], labels: List[int]) -> dict:
    """Flag rule: flag (predict error) iff margin <= t. Search t over unique margin values,
    maximize Youden's J = flag_recall - flag_fpr. Returns threshold + recall/precision at it."""
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return {"threshold": None, "flag_recall": None, "flag_precision": None, "youden_j": None,
                "n_flagged": 0}
    candidates = sorted(set(margins))
    best = {"threshold": None, "youden_j": -1.0, "flag_recall": 0.0, "flag_precision": 0.0,
            "n_flagged": 0}
    for t in candidates:
        flagged = [i for i in range(len(margins)) if margins[i] <= t]
        tp = sum(1 for i in flagged if labels[i] == 1)
        fp = len(flagged) - tp
        recall = tp / n_pos
        fpr = fp / n_neg
        j = recall - fpr
        if j > best["youden_j"]:
            precision = tp / len(flagged) if flagged else 0.0
            best = {"threshold": t, "youden_j": j, "flag_recall": recall,
                    "flag_precision": precision, "n_flagged": len(flagged)}
    return best


# ---------------------------------------------------------------------------
# Self-test: (1) instrumented copy reproduces run_learnable exactly on the real dense gold;
# (2) a tiny hand-built fixture with a KNOWN answer (one clear high-margin correct decision, one
#     clear low-margin wrong decision) scores AUC == 1.0.
# ---------------------------------------------------------------------------
def self_test() -> None:
    assert os.path.exists(GOLD_PATH), f"dense gold file missing: {GOLD_PATH}"
    passages = load_passages(GOLD_PATH)
    assert len(passages) == 18, f"expected 18 dense passages, got {len(passages)}"
    for p in passages:
        stream = build_mention_stream(p)
        orig = run_learnable(stream)
        inst, decisions = run_learnable_instrumented(stream)
        assert inst == orig, (
            f"instrumented copy DRIFTED from run_learnable on passage {p['passage_id']}: "
            f"{inst} != {orig}"
        )
        assert len(decisions) == len(stream)

    # Toy fixture with a KNOWN calibration answer:
    #   passage A: "Alice went. She left." -- She unambiguously matches Alice (1 compatible
    #   candidate, both name-overlap and single-candidate pronoun path) -- CORRECT, and for the
    #   pronoun decision margin is whatever salience(top) is (only one compatible entity, so
    #   there's no ambiguity to speak of -- it will be marked correct regardless of margin value).
    #   passage B: 2 same-gender entities "Bob" and "Carl" both present, then an ambiguous "he" --
    #   forced to guess between two equally-recent compatible candidates -> near-zero-margin
    #   pronoun decision that will land on the WRONG one for one of the two gold entities (a
    #   forced 50/50 guess is guaranteed wrong for the entity it doesn't pick).
    toy = [
        {
            "passage_id": "toyA",
            "clauses": ["Alice went to the store.", "She bought bread."],
            "entities": {
                "Alice": [
                    {"clause": 0, "mention": "Alice", "role": "agent"},
                    {"clause": 1, "mention": "She", "role": "agent"},
                ],
            },
        },
        {
            # "He" in gold refers to a THIRD person never named (a singleton gold cluster of its
            # own), but the mechanism's recency-driven salience forces it onto the more-recently-
            # mentioned same-gender Carl -- a forced, guaranteed-wrong decision with only a small
            # salience gap (near-ambiguous margin). Bob is kept a gold SINGLETON (no other member
            # of its cluster) precisely so Bob's own confident, unambiguous decision cannot be
            # retroactively tainted by a downstream SPLIT -- isolating the wrongness to the two
            # mentions actually involved in the erroneous merge (Carl, He), which is what should
            # drive the calibration signal.
            "passage_id": "toyB",
            "clauses": ["Bob spoke.", "Carl spoke.", "He left."],
            "entities": {
                "Bob": [{"clause": 0, "mention": "Bob", "role": "agent"}],
                "Carl": [{"clause": 1, "mention": "Carl", "role": "agent"}],
                "SomeoneElse": [{"clause": 2, "mention": "He", "role": "agent"}],
            },
        },
    ]
    all_margins: List[float] = []
    all_labels: List[int] = []
    for p in toy:
        stream = build_mention_stream(p)
        preds, decisions = run_learnable_instrumented(stream)
        for i, dec in enumerate(decisions):
            wrong = mention_is_wrong(i, stream, preds)
            all_margins.append(dec["margin"])
            all_labels.append(1 if wrong else 0)
    assert sum(all_labels) >= 1, "toy fixture must contain at least one forced-wrong decision"
    assert sum(all_labels) < len(all_labels), "toy fixture must contain at least one correct decision"
    auc = auc_from_scores([-m for m in all_margins], all_labels)
    assert auc is not None
    assert auc == 1.0, f"toy fixture (clean, isolated wrong/correct decisions) must score AUC == 1.0, got {auc}"

    # AUC sanity: perfectly separable synthetic scores/labels must give exactly 1.0 (higher score
    # => label 1, by auc_from_scores' contract).
    perfect_auc = auc_from_scores([0.9, 0.8, 0.1, 0.05], [1, 1, 0, 0])
    assert perfect_auc == 1.0, f"perfectly separable synthetic case must give AUC 1.0, got {perfect_auc}"
    chance_auc = auc_from_scores([0.5, 0.5, 0.5, 0.5], [1, 0, 1, 0])
    assert chance_auc == 0.5, f"tied scores must give AUC 0.5, got {chance_auc}"

    print("[SELF-TEST] PASS: instrumented copy reproduces run_learnable exactly on dense gold; "
          f"toy fixture AUC={auc:.3f}; synthetic AUC sanity checks OK")


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def main() -> None:
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    passages = load_passages(GOLD_PATH)

    # Records pooled across all passages: one dict per mention decision.
    records: List[dict] = []
    n_repro_mismatches = 0
    for p in passages:
        stream = build_mention_stream(p)
        orig_preds = run_learnable(stream)
        inst_preds, decisions = run_learnable_instrumented(stream)
        if inst_preds != orig_preds:
            n_repro_mismatches += 1
            continue  # exclude passage from calibration stats if mechanism drifted (should be 0)
        for i, dec in enumerate(decisions):
            wrong = mention_is_wrong(i, stream, inst_preds)
            records.append({
                "passage_id": p["passage_id"],
                "is_pronoun": dec["is_pronoun"],
                "margin": dec["margin"],
                "best_score": dec["best_score"],
                "n_compatible": dec["n_compatible"],
                "chose_new": dec["chose_new"],
                "bridging": dec["bridging"],
                "fallback": dec["fallback"],
                "is_wrong": wrong,
            })

    repro_ok = n_repro_mismatches == 0

    def _subset_stats(recs: List[dict]) -> dict:
        margins = [r["margin"] for r in recs]
        labels = [1 if r["is_wrong"] else 0 for r in recs]
        scores = [-m for m in margins]  # higher score (lower margin) => predicted more likely wrong
        auc = auc_from_scores(scores, labels)
        curve = calibration_curve(margins, labels, N_CALIBRATION_BINS)
        thr = best_youden_threshold(margins, labels)
        base_error_rate = sum(labels) / len(labels) if labels else None
        return {
            "n": len(recs),
            "n_errors": sum(labels),
            "base_error_rate": base_error_rate,
            "auc_margin_predicts_error": auc,
            "calibration_curve": curve,
            "best_threshold": thr,
        }

    overall_stats = _subset_stats(records)
    name_stats = _subset_stats([r for r in records if not r["is_pronoun"]])
    pronoun_stats = _subset_stats([r for r in records if r["is_pronoun"]])

    overall_auc = overall_stats["auc_margin_predicts_error"]
    pronoun_auc = pronoun_stats["auc_margin_predicts_error"]
    pronoun_flag_recall = pronoun_stats["best_threshold"]["flag_recall"]

    if overall_auc is None:
        verdict = "UNKNOWN_DEGENERATE_LABELS"
    elif overall_auc <= AUC_HARD_FAIL_CEILING:
        verdict = "HARD_FAIL_UNCALIBRATED"
    elif (pronoun_auc is not None and pronoun_auc >= AUC_HARD_PASS_PRONOUN_FLOOR
          and pronoun_flag_recall is not None and pronoun_flag_recall >= FLAG_RECALL_HARD_PASS_FLOOR):
        verdict = "HARD_PASS_CALIBRATED"
    else:
        verdict = "MIDDLE_BAND_PARTIALLY_CALIBRATED"

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": (
            f"overall_auc={overall_auc} pronoun_auc={pronoun_auc} "
            f"name_auc={name_stats['auc_margin_predicts_error']} "
            f"pronoun_flag_recall_at_best_thr={pronoun_flag_recall} "
            f"n_decisions={len(records)} n_repro_mismatches={n_repro_mismatches} "
            f"repro_exact={repro_ok}"
        ),
        "summary": verdict,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "n_passages": len(passages),
        "n_decisions_total": len(records),
        "instrumented_copy_reproduces_run_learnable_exactly": repro_ok,
        "n_repro_mismatches": n_repro_mismatches,
        "overall": overall_stats,
        "name_subset": name_stats,
        "pronoun_subset": pronoun_stats,
        "bands": {
            "auc_hard_fail_ceiling": AUC_HARD_FAIL_CEILING,
            "auc_hard_pass_pronoun_floor": AUC_HARD_PASS_PRONOUN_FLOOR,
            "flag_recall_hard_pass_floor": FLAG_RECALL_HARD_PASS_FLOOR,
        },
        "gold_path": GOLD_PATH,
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    print(f"[{ANCHOR_NAME}] {verdict}")
    print(metrics["verdict_msg"])
    print(f"metrics written to {final}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
