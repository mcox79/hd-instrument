"""experiments/exp_verbclass_backoff_coverage_v2.py -- RETEST (test-first) of the Levin/VerbNet
verb-class backoff, with the diagnosed ONE-CHANGE FIX: LAST-RESORT TIER PLACEMENT.

BACKGROUND (commit 883e1b7ba, exp_verbclass_backoff_coverage_v1.py): the v1 cell monkeypatched
hdlab.goal_typing._verb_classes GLOBALLY for the entire 44-item pass. Because _verb_classes is a
shared helper called from INSIDE find_desired_state / find_actual_state_candidates, which are in turn
called by the FIRST tier of the production cascade (congruence_outcome_valence_windowed, reached via
congruence_with_lexicon_fallback), the backoff table gave that FIRST tier a confident (non-NA) class
verdict for items it previously abstained on. That confident-but-WRONG first-tier verdict then
PRE-EMPTED later, more-reliable tiers (congruence_referent_recurrence_windowed /
congruence_grounded_result_class / ...) that were correctly answering those exact items via referent
matching rather than verb class. MEASURED result: net -2 (17->15 correct): +1 genuine gain
(ts_tom_wish_free_potter, get->possession, NA->CORRECT) but -3 regression (lw_aunt_march_opposition
CORRECT->NA, woz_dorothy_kansas_wish CORRECT->WRONG, onestop_limal_dating CORRECT->WRONG -- all three
via reason="referent_mismatch"/"abstain_fallback_to_lexicon" after the patched first tier no longer
abstained and never let the later tiers run). Full record: data/exp_verbclass_backoff_coverage_v1/
metrics.json (verdict=HARD_FAIL).

PRIOR-WORK CHECK (substrate_query.sh "verb class backoff last resort tier ordering pre-emption
congruence cascade", run before authoring this v2): top-5 hits all cosine<=0.2588 (last_resort/
congruence/pre-emption WordNet entries + one generic 'last resort' atom) -- NO prior cell or design
doc at cosine>0.30. This is a genuinely novel narrow architectural fix, not a rediscovery.

THE FIX (this cell, isolated, does NOT edit hdlab/goal_typing.py on disk): reuses the EXACT SAME Levin
class table + monkeypatch machinery from v1 (imported, not duplicated -- see `import
exp_verbclass_backoff_coverage_v1 as v1` below) but changes WHEN the patch is consulted. Instead of
patching _verb_classes for the whole 44-item pass (so tier 1 of the cascade sees it), this cell:
  1. Runs the FULL production cascade (gt.congruence_with_lexicon_fallback, UNPATCHED -- literally the
     unmodified module function, byte-identical to what ships today) end-to-end, including its own
     internal tiers 1-4 (verb-class / referent-recurrence / grounded-result / request-response) AND its
     own bare-lexicon fallback.
  2. ONLY IF that entire unpatched cascade abstains (verdict in {NA, NONE, AMBIGUOUS} -- the exact same
     abstain-token set exp_verbclass_backoff_coverage_v1._score already uses) does it install the Levin
     backoff patch and re-run the SAME cascade function a second time.
  3. If the second (patched) pass produces a non-abstain verdict, THAT is returned as the LAST-RESORT
     answer. If it too abstains, the original abstain verdict is kept.

STRICT-ADD SAFETY PROPERTY (load-bearing, this IS the fix): step 1's unpatched verdict is the ONLY
thing ever inspected to decide whether to even ATTEMPT the backoff. An item where the unpatched
cascade already returns MET/UNMET (correct OR wrong) is returned from step 1 verbatim -- the patched
second pass is never even invoked for it, so it is IMPOSSIBLE for the backoff to touch (let alone
flip) an already-decided item. This is the architectural fix for the v1 pre-emption bug: v1 let the
patch influence the FIRST decision; v2 only ever lets it influence the LAST decision when nothing else
fired.

PREDICTED (per Director spawn prompt, stated BEFORE running -- tagged HYPOTHESIZED, not measured
until the run below): ts_tom_wish_free_potter recovers (+1, its unpatched cascade -- including bare
lexicon -- was NA per v1 metrics, so nothing else can fire there to be pre-empted); lw_aunt_march_
opposition / woz_dorothy_kansas_wish / onestop_limal_dating all KEEP their unpatched-cascade CORRECT
verdicts (their v1 regressions were caused SOLELY by first-tier pre-emption, which this design
structurally cannot do) -> zero regression.

Run: .venv/Scripts/python.exe experiments/exp_verbclass_backoff_coverage_v2.py
Writes: data/exp_verbclass_backoff_coverage_v2/metrics.json
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, EXPERIMENTS_DIR)

ANCHOR_NAME = "exp_verbclass_backoff_coverage_v2"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
EVAL_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_bearing_modern_eval_v1.jsonl")

_ABSTAIN_TOKENS = ("NA", "NONE", "AMBIGUOUS")


# ================================================================================================
# Reuse v1's Levin class table + monkeypatch machinery verbatim (no duplication; SAME data).
# ================================================================================================
import exp_verbclass_backoff_coverage_v1 as v1  # noqa: E402


# ================================================================================================
# THE FIX: last-resort wrapper (v2-only logic; everything else below is eval-harness plumbing)
# ================================================================================================

def congruence_with_levin_last_resort(gt, backoff_table, passage_text: str):
    """Run the production cascade UNPATCHED first; only on total abstain, retry the SAME cascade
    with the Levin backoff installed. Returns (verdict, detail, tier_used) where tier_used in
    {"primary_cascade_no_backoff_needed", "levin_last_resort_backoff", "both_abstain"}."""
    verdict, detail = gt.congruence_with_lexicon_fallback(passage_text)
    if verdict.upper() not in _ABSTAIN_TOKENS:
        return verdict, detail, "primary_cascade_no_backoff_needed"
    orig_verb_classes, orig_class_relation = v1._install_patch(gt, backoff_table)
    try:
        verdict2, detail2 = gt.congruence_with_lexicon_fallback(passage_text)
    finally:
        v1._restore_patch(gt, orig_verb_classes, orig_class_relation)
    if verdict2.upper() not in _ABSTAIN_TOKENS:
        return verdict2, detail2, "levin_last_resort_backoff"
    return verdict, detail, "both_abstain"


# ================================================================================================
# Eval harness (mirrors v1's _score / _diff exactly, so before/after comparisons are apples-to-apples)
# ================================================================================================

def _load_items():
    with open(EVAL_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _status(verdict_upper: str, gold: str) -> str:
    if verdict_upper in _ABSTAIN_TOKENS:
        return "NA"
    return "CORRECT" if verdict_upper == gold else "WRONG"


def _score_baseline(items, gt):
    """UNPATCHED full cascade -- byte-identical to v1's baseline (and to production today)."""
    out = {}
    for it in items:
        verdict, detail = gt.congruence_with_lexicon_fallback(it["text"])
        gold = it["gold_outcome_polarity"].upper()
        v = verdict.upper()
        out[it["id"]] = {"status": _status(v, gold), "verdict": v, "gold": gold,
                          "reason": detail.get("reason") if isinstance(detail, dict) else None}
    return out


def _score_last_resort(items, gt, backoff_table):
    out = {}
    tier_counts = {"primary_cascade_no_backoff_needed": 0, "levin_last_resort_backoff": 0,
                   "both_abstain": 0}
    for it in items:
        verdict, detail, tier = congruence_with_levin_last_resort(gt, backoff_table, it["text"])
        gold = it["gold_outcome_polarity"].upper()
        v = verdict.upper()
        tier_counts[tier] += 1
        out[it["id"]] = {"status": _status(v, gold), "verdict": v, "gold": gold,
                          "reason": detail.get("reason") if isinstance(detail, dict) else None,
                          "tier": tier}
    return out, tier_counts


def _diff(baseline, patched):
    coverage_gain, na_to_wrong, regressions, unchanged = [], [], [], []
    for iid in baseline:
        b, p = baseline[iid], patched[iid]
        if b["status"] == "CORRECT" and p["status"] != "CORRECT":
            regressions.append({"id": iid, "before": b, "after": p})
        elif b["status"] == "NA" and p["status"] == "CORRECT":
            coverage_gain.append({"id": iid, "before": b, "after": p})
        elif b["status"] == "NA" and p["status"] == "WRONG":
            na_to_wrong.append({"id": iid, "before": b, "after": p})
        else:
            unchanged.append(iid)
    return coverage_gain, na_to_wrong, regressions, unchanged


# ================================================================================================
# Gate 3: generalization probe -- SAME 8 held-out sentences as v1 (imported, not duplicated), but run
# through the v2 LAST-RESORT WRAPPER (not "always-patched") so this measures the architecture that
# would actually ship.
# ================================================================================================

def _run_heldout_probes_last_resort(gt, backoff_table):
    results = []
    n_correct = 0
    for goal_s, outcome_s, gold, note in v1._HELDOUT_PROBES:
        passage = goal_s + " " + outcome_s
        verdict, detail, tier = congruence_with_levin_last_resort(gt, backoff_table, passage)
        ok = verdict.upper() == gold
        n_correct += int(ok)
        results.append({"goal": goal_s, "outcome": outcome_s, "gold": gold,
                         "verdict": verdict.upper(), "correct": ok, "tier": tier,
                         "reason": detail.get("reason") if isinstance(detail, dict) else None,
                         "note": note})
    return results, n_correct


# ================================================================================================
# Gate 4: adversarial over-fire probes
#   (a)/(c): class-table-level checks -- reuse v1's checks verbatim (table membership; no patch
#            needed).
#   (b): "do" through the LIVE v2 LAST-RESORT WRAPPER on a synthetic goal+outcome passage that would
#        otherwise abstain -- must still abstain (never let "do" borrow a class from the backoff).
# ================================================================================================

def _run_adversarial_probes_v2(gt, backoff_table):
    results = {}
    results["do_excluded_from_table"] = v1.ADVERSARIAL_EXCLUDED_LIGHT_VERB not in backoff_table
    for w in v1.ADVERSARIAL_UNRELATED_PROBES:
        results[f"unrelated_{w}_in_table"] = w in backoff_table
    # live last-resort pipeline probe: a "do" goal whose outcome sentence has nothing else for any
    # tier to grab onto -- if the backoff over-fired on "do" this would spuriously resolve to MET.
    do_passage = "Chen decided to do something about it. Chen did something about it."
    verdict, detail, tier = congruence_with_levin_last_resort(gt, backoff_table, do_passage)
    results["do_live_last_resort_verdict"] = verdict.upper()
    results["do_live_last_resort_tier"] = tier
    results["do_stays_unclassed"] = verdict.upper() in _ABSTAIN_TOKENS
    return results


# ================================================================================================
# main
# ================================================================================================

def main():
    t0 = datetime.now(timezone.utc)
    import hdlab.goal_typing as gt
    from hdlab.thematic_role_labeler import lemma_verb

    items = _load_items()
    assert len(items) == 44, f"expected 44 eval items, got {len(items)}"

    # ---- Step 0: baseline (fully unpatched) full-44 pass, identical definition to v1's baseline ----
    baseline = _score_baseline(items, gt)
    n_base_correct = sum(1 for v in baseline.values() if v["status"] == "CORRECT")
    n_base_wrong = sum(1 for v in baseline.values() if v["status"] == "WRONG")
    n_base_na = sum(1 for v in baseline.values() if v["status"] == "NA")

    # ---- Build backoff table (SAME data as v1, imported not duplicated) ----------------------
    full_table, core_table, heldout_table = v1._build_backoff_table(lemma_verb)

    # ---- LAST-RESORT pass: patch only ever consulted per-item, only on total-abstain -----------
    last_resort, tier_counts = _score_last_resort(items, gt, full_table)
    n_lr_correct = sum(1 for v in last_resort.values() if v["status"] == "CORRECT")
    n_lr_wrong = sum(1 for v in last_resort.values() if v["status"] == "WRONG")
    n_lr_na = sum(1 for v in last_resort.values() if v["status"] == "NA")

    coverage_gain, na_to_wrong, regressions, unchanged = _diff(baseline, last_resort)

    heldout_results, n_heldout_correct = _run_heldout_probes_last_resort(gt, full_table)
    adversarial = _run_adversarial_probes_v2(gt, full_table)

    # ---- Restoration self-test: module state must be byte-identical to pre-run after the whole
    # per-item install/restore cycle (proves no patch ever leaks across items or past the run) -------
    baseline_after = _score_baseline(items, gt)
    restoration_ok = baseline_after == baseline

    # ---- Verdict arithmetic (per Director spawn-prompt gate, NOT v1's >=3 bar -- v2's predicted
    # gain is exactly +1 (ts_tom); the gate here is the one specified in the retest task) -----------
    n_gain = len(coverage_gain)
    n_regress = len(regressions)
    n_na_to_wrong = len(na_to_wrong)
    heldout_pass = n_heldout_correct >= 6  # >=6/8 (75%) held-out generalization bar (same bar as v1)
    no_overfire = (adversarial["do_stays_unclassed"]
                   and not any(adversarial[f"unrelated_{w}_in_table"] for w in v1.ADVERSARIAL_UNRELATED_PROBES))

    if n_gain >= 1 and n_regress == 0 and no_overfire and heldout_pass:
        verdict = "HARD_PASS"
    elif n_regress > 0 or n_gain == 0 or not no_overfire:
        verdict = "HARD_FAIL"
    else:
        # n_gain >= 1, n_regress == 0, no_overfire True, but heldout below bar
        verdict = "PARTIAL"

    verdict_msg = (
        f"coverage_gain={n_gain} (NA->CORRECT) na_to_wrong={n_na_to_wrong} "
        f"regressions={n_regress} heldout={n_heldout_correct}/8 no_overfire={no_overfire} "
        f"restoration_ok={restoration_ok} tier_counts={tier_counts} verdict={verdict}"
    )
    print(verdict_msg, flush=True)
    for g in coverage_gain:
        print("  GAIN:", g["id"], g["before"], "->", g["after"], flush=True)
    for r in regressions:
        print("  REGRESSION:", r["id"], r["before"], "->", r["after"], flush=True)
    for n in na_to_wrong:
        print("  NA_TO_WRONG:", n["id"], n["before"], "->", n["after"], flush=True)

    elapsed_s = (datetime.now(timezone.utc) - t0).total_seconds()

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": elapsed_s,
        "ts_iso": t0.isoformat(),
        "run_mode": "full",
        "eval_path": EVAL_PATH,
        "n_items": len(items),
        "prior_cell": "experiments/exp_verbclass_backoff_coverage_v1.py (commit 883e1b7ba, HARD_FAIL, "
                       "early-tier pre-emption)",
        "fix_applied": "last_resort_tier_placement (patch consulted only after the FULL unpatched "
                        "cascade -- including bare-lexicon fallback -- abstains)",
        "baseline": {"correct": n_base_correct, "wrong": n_base_wrong, "na": n_base_na},
        "last_resort": {"correct": n_lr_correct, "wrong": n_lr_wrong, "na": n_lr_na},
        "tier_counts": tier_counts,
        "coverage_gain_count": n_gain,
        "coverage_gain_items": coverage_gain,
        "na_to_wrong_count": n_na_to_wrong,
        "na_to_wrong_items": na_to_wrong,
        "regression_count": n_regress,
        "regression_items": regressions,
        "unchanged_count": len(unchanged),
        "restoration_ok": restoration_ok,
        "heldout_generalization": {"n_correct": n_heldout_correct, "n_total": len(v1._HELDOUT_PROBES),
                                    "pass_bar": 6, "results": heldout_results},
        "adversarial_overfire_probe": adversarial,
        "backoff_table_size": {"full": len(full_table), "core": len(core_table),
                                "heldout": len(heldout_table)},
        "gates": {
            "coverage_gain_ge_1": n_gain >= 1,
            "no_regression": n_regress == 0,
            "heldout_generalization_ge_6_of_8": heldout_pass,
            "no_overfire": no_overfire,
            "restoration_ok": restoration_ok,
        },
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)
    print(f"[metrics written] {final_path}", flush=True)
    return metrics


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        diag = {
            "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}",
            "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "anchor_name": ANCHOR_NAME,
        }
        tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
        final_path = os.path.join(OUTPUT_DIR, "metrics.json")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(diag, f, indent=2)
        os.replace(tmp_path, final_path)
        raise
