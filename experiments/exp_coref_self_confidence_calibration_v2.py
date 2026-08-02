"""METACOGNITIVE CALIBRATION PROBE v2 -- POWERED pronoun eval + strict_cb mechanism.

WHAT (extends v1, commit c6eb94467): v1 established that the coref mechanism's OWN decision-margin
predicts its OWN errors on the NAME path (clean-label AUC 0.753, HARD_PASS, banked atom 29616), but
the PRONOUN path was content-underpowered (n=16 decisions on the dense gold). This v2 re-runs the
SAME clean local link-level (MUC-style) calibration on the POWERED eval and adds the current-best
coref mechanism (strict_cb) as a second instrumented mechanism.

WHY a v2 file (not an in-place re-run of v1): v1 is banked (atom 29616) and its dense-gold result
must stay reproducible/auditable. v2 REUSES v1's validated calibration machinery VERBATIM (imported,
never reimplemented): auc_from_scores, calibration_curve, best_youden_threshold, mention_link_wrong
(the clean local link-level label), run_learnable_instrumented, NO_COMPETITION_MARGIN.

TWO MECHANISMS, each with a byte-faithful instrumented copy VET'd to reproduce its cluster
assignments EXACTLY on every passage before its margins are trusted:
  (1) baseline = run_learnable (exp_earn_coref_match_or_allocate_v1) -- the calibrated-name-path
      mechanism from v1. Instrumented copy = v1's run_learnable_instrumented.
      * NAME margin  = best_overlap - 2nd_best_overlap (token-Jaccard gap over compatible cands).
      * PRONOUN margin = salience(top) - salience(2nd) (Centering salience gap over gn-compatible).
  (2) strict_cb = run_learnable_strict_cb (exp_earn_coref_pronoun_strict_cb_v1, commit 5b266248f)
      -- our BEST coref now; changes the PRONOUN decision to literal-Centering strict-Cb (hard
      tiered antecedent selection), name branch byte-identical to baseline. Instrumented copy =
      run_learnable_strict_cb_instrumented below, which drives the assignment through the SAME
      imported _pick_strict_cb / _resolve_name_branch as the mechanism and only ADDS margin logging.
      * NAME margin  = same token-Jaccard overlap gap as baseline.
      * PRONOUN margin = the gap in strict-Cb's OWN selection criterion between the chosen
        antecedent and the runner-up: rank compatible candidates by (most-recent subject-like
        clause before the pronoun's clause, else -1; then last_pos), descending -- this ranking's
        top IS the mechanism's pick (asserted). Then:
          - exactly one compatible candidate  -> NO_COMPETITION_MARGIN (unambiguous, nothing to
            confuse with).
          - top and runner-up differ in most-recent-subject-clause -> margin = that clause gap
            (>0; the subject-clause rule gave a clear winner -> confident).
          - top and runner-up TIE on most-recent-subject-clause (incl. both having none) ->
            margin = 0.0 -- the decision fell to a pure recency tiebreak among criterion-equal
            candidates = the KNOWN-HARD same-clause turn-taking ambiguity (Harry/Sam class), which
            is exactly the low-confidence event we want the flag to catch.

GROUND TRUTH (clean local link-level label, mention_link_wrong, validated in v1): allocate-new is
correct iff no gold-coreferent antecedent existed at decision time; a match is correct iff the
most-recent prior mention in the chosen predicted cluster is gold-coreferent. Judges only the
decision at decision time -- NOT tainted by later mentions (v1 proved the old global-purity label
dragged name-path AUC 0.48 -> 0.75 when fixed).

EVALS:
  - PRIMARY: gold_combined_pronoun_powered_v1.jsonl (36 passages; the same powered eval the
    strict_cb cell used) -- far more pronoun decisions than v1's dense-gold n=16.
  - SECONDARY: gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl (18 passages, director-reviewed
    pronoun-dense subset).
Streams built with build_mention_stream_with_role so strict_cb can see roles; run_learnable is
role-blind so both mechanisms consume the identical stream.

METRIC: per-PATH (name / pronoun kept SEPARATE -- never pool the incompatible margin scales) AUC of
margin -> P(error) for BOTH mechanisms on BOTH evals, calibration curve, and best-Youden-threshold
flag recall/precision on the PRONOUN path specifically (the bottleneck we want to flag).

CAN-FAIL (pre-registered BEFORE running), judged on the PRIMARY powered eval PRONOUN path:
  - HARD_PASS_PRONOUN_CALIBRATED: pronoun-path AUC >= 0.65 with a usable best-Youden threshold
    (flag recall >= 0.30 AND flag precision > the pronoun base error rate) -- for AT LEAST ONE
    mechanism; the flag can target the coref-quality bottleneck. Report which mechanism(s).
  - HARD_FAIL_PRONOUN_UNCALIBRATED: pronoun-path AUC <= 0.55 for BOTH mechanisms even when powered
    -- the margin does NOT predict pronoun errors; a real negative -> the flag needs a different/
    richer signal for pronouns (e.g. #compatible-candidates, or a coherence signal). Report
    honestly, do not spin.
  - MIDDLE_BAND_PRONOUN otherwise.

Self-test: python exp_coref_self_confidence_calibration_v2.py --self-test
Full:      python exp_coref_self_confidence_calibration_v2.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Reused VERBATIM from v1's validated calibration machinery (never reimplemented).
from exp_coref_self_confidence_calibration_v1 import (  # noqa: E402
    auc_from_scores,
    calibration_curve,
    best_youden_threshold,
    mention_link_wrong,
    run_learnable_instrumented,
    NO_COMPETITION_MARGIN,
    N_CALIBRATION_BINS,
)
from exp_earn_coref_match_or_allocate_v1 import (  # noqa: E402
    gn_compatible,
    normalize_tokens,
    run_learnable,
)
# strict_cb mechanism internals -- imported so the instrumented copy drives assignment through the
# SAME code the mechanism uses (byte-faithful), adding only margin logging.
from exp_earn_coref_pronoun_strict_cb_v1 import (  # noqa: E402
    run_learnable_strict_cb,
    _EntityCb,
    _pick_strict_cb,
    _resolve_name_branch,
    SUBJECT_LIKE_ROLES,
)
from exp_wire_coref_accumulate_situation_model_v1 import (  # noqa: E402
    build_mention_stream_with_role,
)

ANCHOR_NAME = "coref_self_confidence_calibration_v2"
GOLD_PATH_COMBINED = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_combined_pronoun_powered_v1.jsonl"
)
GOLD_PATH_G5G6 = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1",
    "gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl",
)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# Pre-registered bands (see module docstring CAN-FAIL).
AUC_HARD_FAIL_CEILING = 0.55
AUC_HARD_PASS_FLOOR = 0.65
FLAG_RECALL_HARD_PASS_FLOOR = 0.30


def load_passages(path: str) -> List[dict]:
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return sorted(passages, key=lambda p: p["passage_id"])


# ---------------------------------------------------------------------------
# strict_cb instrumented copy: byte-faithful to run_learnable_strict_cb (drives assignment through
# the imported _pick_strict_cb / _resolve_name_branch), adds per-decision margin logging.
# ---------------------------------------------------------------------------
def _name_overlap_margin(entities: List[_EntityCb], gender, number, toks: set,
                          has_determiner: bool) -> Tuple[float, float, bool, bool, int]:
    """Read-only recompute of the name/nominal branch's overlap ranking (does NOT mutate entities).
    Returns (margin, best_score, chose_new, bridging, n_compatible). Mirrors run_learnable's name
    branch exactly so the logged margin matches what _resolve_name_branch will act on."""
    compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
    overlaps: List[float] = []
    best_overlap = 0.0
    best = None
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
    if best is None and len(compat) == 1 and has_determiner:
        return 0.0, 0.0, False, True, len(compat)  # bridging default (weak evidence)
    if best is None:
        # allocate-new: no competition -> confident sentinel; competitors-but-no-overlap -> 0.0
        margin = NO_COMPETITION_MARGIN if len(compat) == 0 else 0.0
        return margin, 0.0, True, False, len(compat)
    ov_sorted = sorted(overlaps, reverse=True)
    second = ov_sorted[1] if len(ov_sorted) >= 2 else 0.0
    return ov_sorted[0] - second, ov_sorted[0], False, False, len(compat)


def _pronoun_strict_cb_margin(compat: List[_EntityCb], cur_clause: int) -> Tuple[float, float]:
    """Margin in strict-Cb's OWN selection criterion between chosen and runner-up. Returns
    (margin, best_subject_clause_as_score). Ranking key = (most-recent subject-like clause before
    cur_clause, else -1; then last_pos) descending -- its top equals _pick_strict_cb's pick."""
    def _sc(e: _EntityCb) -> int:
        c = e.most_recent_subject_clause(cur_clause)
        return c if c is not None else -1
    ranked = sorted(compat, key=lambda e: (_sc(e), e.last_pos), reverse=True)
    if len(ranked) == 1:
        return NO_COMPETITION_MARGIN, float(_sc(ranked[0]))
    sc_top, sc_run = _sc(ranked[0]), _sc(ranked[1])
    if sc_top != sc_run:
        return float(sc_top - sc_run), float(sc_top)
    return 0.0, float(sc_top)  # tie on primary criterion -> pure-recency tiebreak = ambiguous


def run_learnable_strict_cb_instrumented(stream: List[dict]) -> Tuple[List[int], List[dict]]:
    entities: List[_EntityCb] = []
    next_id = 0
    assigned: List[int] = []
    decisions: List[dict] = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause = rec["clause"]
        cur_role = rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            if compat:
                best = _pick_strict_cb(compat, cur_clause)  # actual mechanism pick
                margin, best_score = _pronoun_strict_cb_margin(compat, cur_clause)
                # safety: our margin ranking's top must equal the mechanism's pick
                def _sc(e: _EntityCb) -> int:
                    c = e.most_recent_subject_clause(cur_clause)
                    return c if c is not None else -1
                ranked_top = sorted(compat, key=lambda e: (_sc(e), e.last_pos), reverse=True)[0]
                assert ranked_top.eid == best.eid, "strict_cb margin ranking disagrees with pick"
                decisions.append({
                    "pos": pos, "is_pronoun": True, "chose_new": False, "bridging": False,
                    "fallback": False, "margin": margin, "best_score": best_score,
                    "n_compatible": len(compat),
                })
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)  # tier-4 best-effort
                decisions.append({
                    "pos": pos, "is_pronoun": True, "chose_new": False, "bridging": False,
                    "fallback": True, "margin": 0.0, "best_score": 0.0, "n_compatible": 0,
                })
            else:
                best = _EntityCb(next_id)
                next_id += 1
                entities.append(best)
                decisions.append({
                    "pos": pos, "is_pronoun": True, "chose_new": True, "bridging": False,
                    "fallback": False, "margin": NO_COMPETITION_MARGIN, "best_score": 0.0,
                    "n_compatible": 0,
                })
            best.count += 1
            best.last_pos = pos
            if cur_role is not None:
                best.clause_role[cur_clause] = cur_role
            assigned.append(best.eid)
            continue
        toks = normalize_tokens(rec["mention_text"])
        first_word = rec["mention_text"].strip().split()[0].lower().strip(".,'\"") \
            if rec["mention_text"].strip() else ""
        has_determiner = rec.get("has_determiner", first_word in {"the", "a", "an"})
        margin, best_score, chose_new, bridging, n_comp = _name_overlap_margin(
            entities, gender, number, toks, has_determiner)
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        decisions.append({
            "pos": pos, "is_pronoun": False, "chose_new": chose_new, "bridging": bridging,
            "fallback": False, "margin": margin, "best_score": best_score, "n_compatible": n_comp,
        })
        best.tokens |= toks
        if best.gender is None and gender is not None:
            best.gender = gender
        if best.number is None and number is not None:
            best.number = number
        best.count += 1
        best.last_pos = pos
        if cur_role is not None:
            best.clause_role[cur_clause] = cur_role
        assigned.append(best.eid)
    assert len(decisions) == len(stream) == len(assigned)
    return assigned, decisions


# ---------------------------------------------------------------------------
# Per-subset calibration stats (clean label). Reuses v1's imported AUC/curve/threshold helpers.
# ---------------------------------------------------------------------------
def _subset_stats(recs: List[dict]) -> dict:
    margins = [r["margin"] for r in recs]
    labels = [1 if r["is_wrong_clean"] else 0 for r in recs]
    scores = [-m for m in margins]  # higher score (lower margin) => predicted more likely wrong
    auc = auc_from_scores(scores, labels)
    curve = calibration_curve(margins, labels, N_CALIBRATION_BINS)
    thr = best_youden_threshold(margins, labels)
    # ALTERNATIVE cheap signal the coordinator named: #compatible-candidates (more compatible
    # antecedents => more ambiguity => more likely wrong). Higher n_compatible => predicted wrong.
    n_comp = [r["n_compatible"] for r in recs]
    auc_ncomp = auc_from_scores([float(c) for c in n_comp], labels)
    return {
        "n": len(recs),
        "n_errors": sum(labels),
        "base_error_rate": (sum(labels) / len(labels)) if labels else None,
        "auc_margin_predicts_error": auc,
        "auc_ncompatible_predicts_error": auc_ncomp,
        "calibration_curve": curve,
        "best_threshold": thr,
    }


def _records_for(passages: List[dict], mechanism: str) -> Tuple[List[dict], int]:
    """Build per-decision calibration records for one mechanism on one passage set. Verifies the
    instrumented copy reproduces the mechanism's cluster assignments exactly."""
    records: List[dict] = []
    n_repro_mismatches = 0
    for p in passages:
        stream = build_mention_stream_with_role(p)
        if mechanism == "baseline":
            orig = run_learnable(stream)
            inst, decisions = run_learnable_instrumented(stream)
        elif mechanism == "strict_cb":
            orig = run_learnable_strict_cb(stream)
            inst, decisions = run_learnable_strict_cb_instrumented(stream)
        else:
            raise ValueError(mechanism)
        if inst != orig:
            n_repro_mismatches += 1
            continue
        for i, dec in enumerate(decisions):
            records.append({
                "passage_id": p["passage_id"],
                "is_pronoun": dec["is_pronoun"],
                "margin": dec["margin"],
                "best_score": dec["best_score"],
                "n_compatible": dec["n_compatible"],
                "chose_new": dec["chose_new"],
                "is_wrong_clean": mention_link_wrong(i, stream, inst),
            })
    return records, n_repro_mismatches


def _mechanism_block(passages: List[dict], mechanism: str) -> dict:
    records, n_repro_mismatches = _records_for(passages, mechanism)
    name_recs = [r for r in records if not r["is_pronoun"]]
    pron_recs = [r for r in records if r["is_pronoun"]]
    return {
        "instrumented_copy_reproduces_mechanism_exactly": n_repro_mismatches == 0,
        "n_repro_mismatches": n_repro_mismatches,
        "n_decisions": len(records),
        "name_subset": _subset_stats(name_recs),
        "pronoun_subset": _subset_stats(pron_recs),
    }


# ---------------------------------------------------------------------------
# Self-test.
# ---------------------------------------------------------------------------
def self_test() -> None:
    assert os.path.exists(GOLD_PATH_COMBINED), f"combined gold missing: {GOLD_PATH_COMBINED}"
    assert os.path.exists(GOLD_PATH_G5G6), f"g5g6 gold missing: {GOLD_PATH_G5G6}"
    combined = load_passages(GOLD_PATH_COMBINED)
    g5g6 = load_passages(GOLD_PATH_G5G6)
    assert len(combined) == 36, f"expected 36 combined passages, got {len(combined)}"
    assert len(g5g6) == 18, f"expected 18 g5g6 passages, got {len(g5g6)}"

    # Both instrumented copies reproduce their mechanisms exactly on every combined passage.
    for p in combined:
        stream = build_mention_stream_with_role(p)
        base_orig = run_learnable(stream)
        base_inst, base_dec = run_learnable_instrumented(stream)
        assert base_inst == base_orig, f"baseline instrumented drift on {p['passage_id']}"
        assert len(base_dec) == len(stream)
        cb_orig = run_learnable_strict_cb(stream)
        cb_inst, cb_dec = run_learnable_strict_cb_instrumented(stream)
        assert cb_inst == cb_orig, f"strict_cb instrumented drift on {p['passage_id']}"
        assert len(cb_dec) == len(stream)

    # Turn-taking ambiguity fixture: two same-gender speakers each agent of adjacent clauses, then a
    # pronoun. strict_cb margin must be 0.0 on the ambiguous pronoun (tie on subject-clause? no --
    # here the two speakers' most-recent subject clauses DIFFER, so margin>0). Build a genuine TIE
    # case: both candidates last held agent role in the SAME clause via a conjoined subject is not
    # expressible here; instead test the clear cases:
    #   - "Robert ran. Willie appeared. He laughed." -> He: Robert agent@0, Willie agent@1;
    #     subject clauses differ (1 vs 0) -> margin = 1.0 (>0, confident pick of Willie).
    fixture = {
        "passage_id": "cb_margin_clear",
        "clauses": ["Robert ran.", "Willie appeared.", "He laughed."],
        "entities": {
            "Robert": [{"clause": 0, "mention": "Robert", "role": "agent"}],
            "Willie": [{"clause": 1, "mention": "Willie", "role": "agent"},
                       {"clause": 2, "mention": "He", "role": "agent"}],
        },
    }
    stream = build_mention_stream_with_role(fixture)
    cb_inst, cb_dec = run_learnable_strict_cb_instrumented(stream)
    he_idx = [i for i, r in enumerate(stream) if r["mention_text"] == "He"][0]
    assert cb_dec[he_idx]["is_pronoun"] and cb_dec[he_idx]["margin"] == 1.0, cb_dec[he_idx]
    # and the pick is correct (Willie) -> clean label says correct
    assert not mention_link_wrong(he_idx, stream, cb_inst), "He should correctly link to Willie"

    # A wrong low-margin pronoun case: gold 'He' refers to a third party but strict_cb must pick a
    # present same-gender candidate -> wrong; margin reflects the criterion gap. Just assert the
    # instrumented copy reproduces and the label machinery runs.
    fixture2 = {
        "passage_id": "cb_margin_wrong",
        "clauses": ["Robert ran.", "Willie appeared.", "He laughed."],
        "entities": {
            "Robert": [{"clause": 0, "mention": "Robert", "role": "agent"}],
            "Willie": [{"clause": 1, "mention": "Willie", "role": "agent"}],
            "SomeoneElse": [{"clause": 2, "mention": "He", "role": "agent"}],
        },
    }
    s2 = build_mention_stream_with_role(fixture2)
    cb2_orig = run_learnable_strict_cb(s2)
    cb2_inst, _ = run_learnable_strict_cb_instrumented(s2)
    assert cb2_inst == cb2_orig
    he2 = [i for i, r in enumerate(s2) if r["mention_text"] == "He"][0]
    assert mention_link_wrong(he2, s2, cb2_inst), "He->present-candidate should be a wrong link"

    print("[SELF-TEST] PASS: both instrumented copies reproduce their mechanisms exactly on 36 "
          "combined passages; strict_cb margin definition verified (clear pick margin=1.0, correct; "
          "wrong-link case labeled wrong); v1 machinery reused")


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
    combined = load_passages(GOLD_PATH_COMBINED)
    g5g6 = load_passages(GOLD_PATH_G5G6)

    results = {
        "combined_powered": {
            "n_passages": len(combined),
            "baseline": _mechanism_block(combined, "baseline"),
            "strict_cb": _mechanism_block(combined, "strict_cb"),
        },
        "g5g6_only": {
            "n_passages": len(g5g6),
            "baseline": _mechanism_block(g5g6, "baseline"),
            "strict_cb": _mechanism_block(g5g6, "strict_cb"),
        },
    }

    # Verdict is judged on the PRIMARY powered eval PRONOUN path.
    def _pron_pass(block: dict) -> Tuple[bool, Optional[float], Optional[float], Optional[float]]:
        ps = block["pronoun_subset"]
        auc = ps["auc_margin_predicts_error"]
        thr = ps["best_threshold"]
        recall = thr["flag_recall"]
        precision = thr["flag_precision"]
        base = ps["base_error_rate"]
        usable = (auc is not None and auc >= AUC_HARD_PASS_FLOOR
                  and recall is not None and recall >= FLAG_RECALL_HARD_PASS_FLOOR
                  and precision is not None and base is not None and precision > base)
        return usable, auc, recall, precision

    base_pass, base_auc, base_rec, base_prec = _pron_pass(results["combined_powered"]["baseline"])
    cb_pass, cb_auc, cb_rec, cb_prec = _pron_pass(results["combined_powered"]["strict_cb"])

    passing_mechs = [m for m, ok in [("baseline", base_pass), ("strict_cb", cb_pass)] if ok]
    both_uncalibrated = (
        base_auc is not None and cb_auc is not None
        and base_auc <= AUC_HARD_FAIL_CEILING and cb_auc <= AUC_HARD_FAIL_CEILING
    )

    if passing_mechs:
        verdict = "HARD_PASS_PRONOUN_CALIBRATED"
    elif both_uncalibrated:
        verdict = "HARD_FAIL_PRONOUN_UNCALIBRATED"
    else:
        verdict = "MIDDLE_BAND_PRONOUN"

    n_pron_combined = results["combined_powered"]["baseline"]["pronoun_subset"]["n"]
    verdict_msg = (
        f"[POWERED, clean label] pronoun-path AUC: baseline={base_auc} strict_cb={cb_auc} "
        f"(n_pronoun_decisions={n_pron_combined}); best-thr flag baseline(recall={base_rec},"
        f"prec={base_prec}) strict_cb(recall={cb_rec},prec={cb_prec}); "
        f"passing_mechanisms={passing_mechs}; "
        f"name-path AUC baseline={results['combined_powered']['baseline']['name_subset']['auc_margin_predicts_error']} "
        f"strict_cb={results['combined_powered']['strict_cb']['name_subset']['auc_margin_predicts_error']}; "
        f"repro_exact baseline={results['combined_powered']['baseline']['instrumented_copy_reproduces_mechanism_exactly']} "
        f"strict_cb={results['combined_powered']['strict_cb']['instrumented_copy_reproduces_mechanism_exactly']}"
    )

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict,
        "label_definition": (
            "clean local link-level (MUC-style, mention_link_wrong from v1): allocate-new correct "
            "iff no gold-coreferent antecedent existed; match correct iff the most-recent prior "
            "mention in the chosen predicted cluster is gold-coreferent. Judged at decision time."
        ),
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "verdict_driven_by": "combined_powered.pronoun_subset (both mechanisms)",
        "results": results,
        "bands": {
            "auc_hard_fail_ceiling": AUC_HARD_FAIL_CEILING,
            "auc_hard_pass_floor": AUC_HARD_PASS_FLOOR,
            "flag_recall_hard_pass_floor": FLAG_RECALL_HARD_PASS_FLOOR,
            "flag_precision_must_exceed": "pronoun base_error_rate",
        },
        "gold_path_combined": GOLD_PATH_COMBINED,
        "gold_path_g5g6": GOLD_PATH_G5G6,
        "prior_v1_commit": "c6eb94467",
        "strict_cb_mechanism_commit": "5b266248f",
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    print(f"[{ANCHOR_NAME}] {verdict}")
    print(verdict_msg)
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
