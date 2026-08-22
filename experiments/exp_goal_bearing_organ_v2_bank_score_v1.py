"""exp_goal_bearing_organ_v2_bank_score_v1 -- MEASUREMENT ONLY (no gates, no HARD_PASS/FAIL bands).

Board Q113. Scores the already-built goal-outcome (outcome-valence) organ --
hdlab.goal_typing.congruence_with_lexicon_fallback, the PRODUCTION entry point -- against the new
124-scorable-item v2 eval bank (experiments/data/goal_bearing_modern_eval_v2.jsonl). The organ's
level on v2 was UNMEASURED before this cell; this cell measures it, WITH FLOORS RECOMPUTED ON v2's
OWN POPULATION, and reports per-class recall separately because the organ is known UNMET-biased on
v1 (majority-class coincidence risk on v2, whose majority flipped to UNMET 60.5%).

Two scoring arms, both READ-ONLY with respect to the bank (never trains on it, per the
eval_bank_too_small contamination rule -- gold was fixed before any organ output was consulted):

  organ_base     -- congruence_with_lexicon_fallback with NO acquired-OOV overlay registered. This
                    is the actual deployed state: hdlab.verb_lexical_similarity.
                    ACQUIRED_OUTCOME_VERB_FEATURES is a module-level dict that is empty unless a
                    caller populates it, and nothing persists a population across process runs. So
                    "the organ" out of the box, today, IS this arm.
  organ_v1_overlay -- the SAME production entry point, but with the 18-lemma OOV overlay that
                    exp_consequence_learning_loop_oov_outcome_verb_valence_v1 (HARD_FAIL) learned
                    from the 4 source novels re-registered before scoring, exactly as that cell's
                    own _score_with_overlay does. Reported for completeness ONLY, with an explicit
                    CONTAMINATION_RISK flag: that overlay was trained excluding only v1's citation
                    line-ranges (+/-50), and v2 draws NEW items from the SAME 4 novels (Little
                    Women, Anne of Green Gables, Tom Sawyer, Wizard of Oz) at DIFFERENT line ranges
                    that were never excluded from that training pass. Any v2 item whose passage (or
                    a paraphrase of it) fell inside the training corpus is not a clean held-out
                    measurement for this arm. This cell does NOT attempt to rebuild the exclusion
                    mask for v2 (that would require re-running the multi-minute corpus-learning
                    pass, disproportionate to a measurement task) -- it reports the arm and the risk
                    honestly instead, per compute-proportionality (cheapest decisive method for a
                    diagnostic question).

Floors: tools.floor_battery.run_battery (the full 12-baseline battery), run on v2's OWN 124
scorable items -- never importing the v1 floor numbers (dead there: length permutation p=0.984).
Positional baselines: verification.goal_bearing_eval_v2_gates.positional_baselines, RECOMPUTED on
the 124-item scorable subset (the shipped baselines file's recency/first_mention/nearest_subject/
majority numbers are on the FULL 166; this cell does not quote those for the scorable population).

AMBIGUOUS handling: congruence_with_lexicon_fallback can return "AMBIGUOUS" or "NA"; neither equals
gold "MET"/"UNMET" so _score counts them as wrong by omission (score_counts_abstention_as_error,
filed separately -- NOT fixed here). This cell reports the AMBIGUOUS/NA count per arm so the
abstention rate is visible rather than silently folded into "wrong".

No read()/ReadResult path: this cell scores each item's given passage text directly via the
production congruence function -- it does not call a corpus reader with a requested-sentence-count,
so there is no n_sentences_requested vs n_sentences shortfall to report for THIS cell.

No pre-reg filed: this is a measurement/diagnostic instrument (same class as tools/floor_battery.py
and verification/goal_bearing_eval_v2_gates.py, neither of which carries a pre-reg) reporting
numbers with floors, not a capability claim being gated to HARD_PASS/HARD_FAIL. If a future capacity
claim is built on these numbers, THAT cell gets the pre-reg with bands.

# CELL-TEMPLATE MANDATORY (subset applicable to a single-shot foreground diagnostic):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - deterministic: floor_battery seed=3 (its default), positional_baselines has no RNG
# - start_marker + crash_diagnostic present
# - progress_logging: print(..., flush=True)
# - arms_differ_verified: organ_base vs organ_v1_overlay differ (different registered lexicon state)
# - all numbers MEASURED@ this cell's own metrics.json
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_typing import congruence_with_lexicon_fallback  # noqa: E402
from hdlab import verb_lexical_similarity as _vls  # noqa: E402
from tools.floor_battery import run_battery  # noqa: E402
from verification.goal_bearing_eval_v2_gates import _scorable, positional_baselines  # noqa: E402

ANCHOR_NAME = "goal_bearing_organ_v2_bank_score_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
BANK_REL = os.path.join("experiments", "data", "goal_bearing_modern_eval_v2.jsonl")
V1_ORGAN_METRICS_REL = os.path.join(
    "data", "exp_consequence_learning_loop_oov_outcome_verb_valence_v1", "metrics.json")


# ------------------------------------------------------------------ start-marker / crash diagnostics
def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
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


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ------------------------------------------------------------------ bank load
def _load_bank():
    rows = []
    with open(os.path.join(REPO_ROOT, BANK_REL), "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _load_v1_overlay():
    """The 18-lemma registered overlay from the landed (HARD_FAIL) v1 organ run, if present."""
    path = os.path.join(REPO_ROOT, V1_ORGAN_METRICS_REL)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    return d.get("registered")


# ------------------------------------------------------------------ scoring
def _score_arm(scorable_rows):
    """Score with WHATEVER overlay state is currently registered in verb_lexical_similarity (caller's
    responsibility to register/clear before calling). Returns per-item + aggregate dict."""
    details = []
    correct = met_c = unmet_c = abstain_c = 0
    n_met = sum(1 for r in scorable_rows if r["gold_outcome_polarity"] == "met")
    n_unmet = len(scorable_rows) - n_met
    for r in scorable_rows:
        gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
        pred, detail = congruence_with_lexicon_fallback(r["text"])
        ok = (pred == gold)
        is_abstain = pred not in ("MET", "UNMET")
        correct += int(ok)
        abstain_c += int(is_abstain)
        if gold == "MET":
            met_c += int(ok)
        else:
            unmet_c += int(ok)
        details.append({"id": r.get("id"), "outcome_lemma": r.get("outcome_verb_lemma"),
                        "gold": gold, "pred": pred, "reason": detail.get("reason"),
                        "correct": bool(ok), "trap_type": r.get("trap_type"),
                        "difficulty": r.get("difficulty")})
    n = len(scorable_rows)
    return {
        "n": n, "accuracy": round(correct / n, 4) if n else None, "correct": correct,
        "met_recall": f"{met_c}/{n_met}",
        "met_recall_frac": round(met_c / n_met, 4) if n_met else None,
        "unmet_recall": f"{unmet_c}/{n_unmet}",
        "unmet_recall_frac": round(unmet_c / n_unmet, 4) if n_unmet else None,
        "n_met": n_met, "n_unmet": n_unmet,
        "abstain_count": abstain_c,
        "pred_distribution": {
            "MET": sum(1 for d in details if d["pred"] == "MET"),
            "UNMET": sum(1 for d in details if d["pred"] == "UNMET"),
            "OTHER_ABSTAIN": sum(1 for d in details if d["pred"] not in ("MET", "UNMET")),
        },
        "per_item_predictions": details,
    }


# ------------------------------------------------------------------ arms-must-differ check
def _arms_differ(arm_a_details, arm_b_details):
    a_sig = tuple(d["pred"] for d in arm_a_details)
    b_sig = tuple(d["pred"] for d in arm_b_details)
    return a_sig != b_sig


# ------------------------------------------------------------------ core run
def _run_all():
    t0 = time.perf_counter()
    all_rows = _load_bank()
    scorable = _scorable(all_rows)
    n_total = len(all_rows)
    n_scorable = len(scorable)
    n_met = sum(1 for r in scorable if r["gold_outcome_polarity"] == "met")
    n_unmet = n_scorable - n_met
    majority_class = "unmet" if n_unmet >= n_met else "met"
    majority_floor = round(max(n_met, n_unmet) / n_scorable, 4)

    print(f"[progress] loaded bank: n_total={n_total} n_scorable={n_scorable} "
          f"n_met={n_met} n_unmet={n_unmet} majority_class={majority_class} "
          f"majority_floor={majority_floor}", flush=True)

    # ---- arm 1: organ_base (no overlay -- the actual out-of-the-box deployed state) ------------
    _vls.clear_acquired_outcome()
    print("[progress] scoring organ_base (no acquired-OOV overlay)", flush=True)
    base_arm = _score_arm(scorable)
    print(f"[progress] organ_base: acc={base_arm['accuracy']} met_recall={base_arm['met_recall']} "
          f"unmet_recall={base_arm['unmet_recall']} abstain={base_arm['abstain_count']}", flush=True)

    # ---- arm 2: organ_v1_overlay (contamination-risk arm, reported honestly) --------------------
    v1_overlay = _load_v1_overlay()
    overlay_arm = None
    if v1_overlay:
        _vls.clear_acquired_outcome()
        for lemma, pol in v1_overlay.items():
            _vls.register_acquired_outcome(lemma, pol)
        print(f"[progress] scoring organ_v1_overlay ({len(v1_overlay)} registered lemmas, "
              f"CONTAMINATION_RISK vs v2)", flush=True)
        overlay_arm = _score_arm(scorable)
        _vls.clear_acquired_outcome()
        print(f"[progress] organ_v1_overlay: acc={overlay_arm['accuracy']} "
              f"met_recall={overlay_arm['met_recall']} unmet_recall={overlay_arm['unmet_recall']} "
              f"abstain={overlay_arm['abstain_count']}", flush=True)
    else:
        print("[progress] no v1 overlay metrics.json found -- skipping organ_v1_overlay arm", flush=True)

    arms_differ = None
    if overlay_arm is not None:
        arms_differ = _arms_differ(base_arm["per_item_predictions"], overlay_arm["per_item_predictions"])

    # ---- floors: full 12-baseline battery on v2's OWN scorable population ----------------------
    print("[progress] running floor_battery (12-baseline) on v2 scorable population", flush=True)
    texts = [r["text"] for r in scorable]
    labels = [1 if r["gold_outcome_polarity"] == "met" else 0 for r in scorable]
    floor_report = run_battery(texts, labels)
    print(f"[progress] floors: majority={floor_report['majority_floor']} "
          f"strongest={floor_report['strongest']} "
          f"strongest_clears_own_null={floor_report['strongest_that_clears_its_own_null']}", flush=True)

    # ---- positional baselines, recomputed on the 124-item SCORABLE subset (not the full 166) ---
    print("[progress] recomputing positional baselines on the scorable subset", flush=True)
    pos_scorable = positional_baselines(scorable)
    pos_full = positional_baselines(all_rows)
    print(f"[progress] positional (scorable n={pos_scorable['n']}): {pos_scorable['overall_acc']} "
          f"defeat_all_four={pos_scorable['n_defeat_all_four']}", flush=True)

    elapsed = round(time.perf_counter() - t0, 2)

    agg = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "MEASURED",
        "verdict_msg": (
            "MEASUREMENT ONLY, no HARD_PASS/FAIL bands. "
            f"organ_base acc={base_arm['accuracy']} (n={n_scorable}, majority_floor={majority_floor} "
            f"class={majority_class}) met_recall={base_arm['met_recall']} "
            f"unmet_recall={base_arm['unmet_recall']} abstain={base_arm['abstain_count']} | "
            f"strongest_floor_that_clears_own_null="
            f"{floor_report['strongest_that_clears_its_own_null']} | "
            f"positional_scorable_defeat_all_four={pos_scorable['n_defeat_all_four']}/{n_scorable}"),
        "bank_path": BANK_REL,
        "n_total": n_total, "n_scorable": n_scorable,
        "n_met": n_met, "n_unmet": n_unmet,
        "majority_class": majority_class, "majority_floor": majority_floor,
        "arms": {
            "organ_base": base_arm,
            "organ_v1_overlay": overlay_arm,
        },
        "organ_v1_overlay_contamination_risk": (
            "organ_v1_overlay was trained on Little Women / Anne of Green Gables / Tom Sawyer / "
            "Wizard of Oz excluding only v1's citation line-ranges (+/-50). v2 draws NEW items from "
            "those same 4 novels at different line ranges never excluded from that training pass, "
            "plus 19 Sherlock Holmes items (not in the training corpus at all) and 28 surviving v1 "
            "items (independently gold-fixed, non-contaminating). The organ_base arm above is the "
            "clean, actually-deployed measurement; organ_v1_overlay is reported for completeness "
            "only and should not be treated as a held-out number."
            if v1_overlay else "no overlay arm run (v1 organ metrics.json not found)"),
        "arms_differ_verified": arms_differ,
        "ambiguous_note": (
            "congruence_with_lexicon_fallback's non-MET/UNMET returns (AMBIGUOUS/NA) are counted as "
            "wrong by omission in accuracy/recall above (score_counts_abstention_as_error, filed "
            "separately -- not fixed here). abstain_count / pred_distribution.OTHER_ABSTAIN report "
            "the raw abstention count per arm so it is visible, not silently folded in."),
        "floor_battery": floor_report,
        "positional_baselines_scorable_124": pos_scorable,
        "positional_baselines_full_166_reference_only": pos_full,
        "read_result_note": (
            "This cell scores each item's given passage text directly via the production congruence "
            "function; it does not call a corpus reader with a requested-sentence-count, so there is "
            "no ReadResult / n_sentences_requested vs n_sentences shortfall applicable here."),
        "scored_population_ids": [r.get("id") for r in scorable],
        "elapsed_s": elapsed,
    }
    return agg


# ------------------------------------------------------------------ driver
def run():
    _write_start_marker(OUTPUT_DIR, "full")
    agg = _run_all()
    _atomic_write_metrics(OUTPUT_DIR, agg)
    print(json.dumps({"verdict": agg["verdict"], "verdict_msg": agg["verdict_msg"],
                      "elapsed_s": agg["elapsed_s"]}, indent=2), flush=True)
    return agg


def self_test():
    """Real-code-path self-test: loads the REAL v2 bank, calls the REAL production congruence
    function on a real item's text, exercises floor_battery.run_battery and positional_baselines on
    a tiny real slice. No synthetic-only branch."""
    all_rows = _load_bank()
    assert len(all_rows) == 166, f"expected 166 total items, got {len(all_rows)}"
    scorable = _scorable(all_rows)
    assert len(scorable) == 124, f"expected 124 scorable items, got {len(scorable)}"
    n_met = sum(1 for r in scorable if r["gold_outcome_polarity"] == "met")
    assert n_met == 49, f"expected 49 met, got {n_met}"
    # real congruence call on a real item
    _vls.clear_acquired_outcome()
    pred, detail = congruence_with_lexicon_fallback(scorable[0]["text"])
    assert pred in ("MET", "UNMET", "AMBIGUOUS", "NA", "NONE"), f"unexpected pred {pred!r}"
    # arms-must-differ helper sanity: identical detail lists must NOT differ
    same = [{"pred": "MET"}, {"pred": "UNMET"}]
    assert not _arms_differ(same, same)
    diff = [{"pred": "MET"}, {"pred": "MET"}]
    assert _arms_differ(same, diff)
    # floor_battery on a real (tiny) slice of the real texts/labels
    tiny_texts = [r["text"] for r in scorable[:24]]
    tiny_labels = [1 if r["gold_outcome_polarity"] == "met" else 0 for r in scorable[:24]]
    if len(set(tiny_labels)) < 2:
        tiny_labels = [i % 2 for i in range(len(tiny_texts))]
    rep = run_battery(tiny_texts, tiny_labels, n_perm=20)
    assert "strongest" in rep and "majority_floor" in rep
    # positional_baselines on a tiny real slice
    pos = positional_baselines(scorable[:10])
    assert pos["n"] == 10
    return {"n_total": len(all_rows), "n_scorable": len(scorable), "n_met": n_met,
            "sample_pred": pred, "floor_battery_smoke_n": rep["n"],
            "positional_smoke_n": pos["n"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        res = self_test()
        print(json.dumps(res, indent=2))
        print("SELF_TEST_PASS")
        return
    run()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
