"""exp_c5_realtext_c3mined_v2_38item_v1 -- HONEST MEASUREMENT (not a pass/fail cell): re-run the
real-text Component-5 pipeline (exp_c5_realtext_c3mined_v1.py's type_sentence_events_c3 /
build_positions_c3 / directed_goal_outcome_score / generalized resolvers, ALL REUSED BIT-IDENTICAL
via import, nothing reimplemented) on the IMPROVED 38-item goal_outcome_c3mined_v1.jsonl bank
(owner-ID accuracy 31/38=0.816 after commit c90173b48, up from the 15/40=0.375-era set the v1 cell
measured on).

WHY A NEW FILE (not editing v1 in place): v1's VERIFIED_CORRECT_IDS hardcodes 15 ids + verification
notes from the OLD 40-item mined bank; the regenerated 38-item bank has DIFFERENT sentence ids (s87
vs s89 etc, see mismatch check below) so the old ids don't cleanly map onto the new file. This cell
re-derives owner-correctness for the NEW 38-item bank directly (agent read every item's text below,
see OWNER_WRONG_IDS with a one-line reason per item) and runs the SAME pipeline end-to-end, without
touching v1 (no regression risk to the landed v1 cell/metrics).

Prior-work check (SUBSTRATE-KB, mandatory before authoring): `tools/substrate_query.sh` was run for
"goal owner selection coherence binding recency outcome real text C3 mined" -- top hits were the
v1 cell itself (this arc) and notes/research_component5_goal_owner_selection_binding_2026-08-04.md
(same arc, already cited by v1/exp_component5_gold_role_isolated_v1.py). This is a re-measurement on
improved data within the SAME arc, not a rediscovery -- no new mechanism, no new prior-art claim.

OWNER-CORRECTNESS RE-VERIFICATION (agent read all 38 items' text+goal_verb+outcome_span on disk,
2026-08-05, this cell): cross-checked against commit c90173b48's stated residual-failure taxonomy
(7 wrong: 2 place-metonym-as-subject, 1 predicate-adjective mistag, 1 verb-sense-ambiguity "saw",
1 vocative-mistaken-for-subject, 2 more place-metonym/locative-adjunct, 1 garbled-subordinate-parse
-- exact count 7 matches 31/38=0.816). See OWNER_WRONG_IDS below for the exact 7 ids + per-item
reason (independently re-derived from the item text, not copied from the commit message).

Reuses bit-identical (import, not reimplemented): type_sentence_events_c3, build_positions_c3,
run_item, _build_c5_item, GENDER_PATCH (extended below with the additional names this larger item
bank introduces -- same mechanical, text-obvious gender-patch discipline v1 used, declared not
hidden), all from exp_c5_realtext_c3mined_v1.py. GeneralRecencyEntityResolver / ContentMatchResolver
/ directed_goal_outcome_score / decide_keep_or_revert / ABSTAIN_BAND_DEFAULT reused bit-identical
via that module's own imports (transitively, not re-imported here to avoid duplicate-symbol drift).

CONTRACT (per task brief): this is a MEASUREMENT cell (verdict describes what was measured, not a
forced PASS/FAIL). Small-N (38 items, ~31 owner-correct) -> directional, N reported prominently.
Reports BOTH: (a) C5 binding restricted to the owner-correct subset (does NOT let owner-ID errors
contaminate the outcome-binding number), and (b) the FULL end-to-end number over all 38 items where
an item only counts correct if BOTH owner-ID AND outcome-binding are correct (the honest "does the
whole pipeline get the right answer" number). Per-item and per-structure_type breakdown included so
failures are decomposed (owner-ID error vs typing-miss vs coref/binding error), not aggregated away.

GUARDS: glass-box; deterministic; ASCII-only; atomic metrics write (os.replace); LOCAL-ONLY, no
push, in-process foreground per task brief; no silent except (outer try/except re-raises after
writing CELL_CRASHED diagnostic per META_RULE_AH/§8 ordering).
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ANCHOR_NAME = "c5_realtext_c3mined_v2_38item_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "metrics.json")

from exp_c5_realtext_c3mined_v1 import (  # noqa: E402
    MINED_PATH, _load_mined, type_sentence_events_c3, build_positions_c3,
    run_item, _build_c5_item, GENDER_PATCH as _V1_GENDER_PATCH,
)
import exp_c5_realtext_c3mined_v1 as _v1  # noqa: E402  (to extend its module-level GENDER_PATCH)

# ---- OWNER-CORRECTNESS ON THE 38-ITEM BANK (agent-verified 2026-08-05, this cell) ----------------
# 7 items whose C3-syntax-resolved goal_owner is WRONG (the true goal-holder is a different entity
# than the mined `goal_owner` field) -- read directly off each item's `text`/`goal_sentence` field.
# The other 31/38 = 0.816 are owner-correct (matches commit c90173b48's disk-verified 31/38 count).
OWNER_WRONG_IDS = {
    "c3_541_the_age_of_innocence__s3":
        "owner='York' is a place-metonym fragment of 'New York' (subject of 'dread'), not a person",
    "c3_145_middlemarch__s34":
        "owner='Celia', goal_verb='knowing' is a PREDICATE ADJECTIVE ('Celia was knowing and "
        "worldly-wise' = Celia IS shrewd), not the desiderative verb 'to know X' -- POS/WSD mistag",
    "c3_805_this_side_of_paradise__s9":
        "owner='England' is a locative adjunct ('learned in England to prefer...'), true subject "
        "of 'prefer' is 'her' (Beatrice), not the place name",
    "c3_171_charlotte_temple__s18":
        "owner='Portsmouth' is a locative object of 'return to', true subject of 'think' is 'I' "
        "(Montraville), not the place name",
    "c3_238_dear_enemy__s8":
        "owner='Judy', goal_verb='see' in 'I see through you!' -- Judy is the VOCATIVE addressee "
        "('My dear Judy...I see through you'), true subject of 'see' is 'I' (the letter-writer)",
    "c3_6053_evelina_or_the_history_of_a_young_ladys_entrance_into_the_world__s43":
        "owner='Evelyn', goal_verb='trust' -- garbled/truncated subordinate-clause excerpt, the "
        "coord-rule subject pick does not track the sentence's real (elided/embedded) subject",
    "c3_74_the_adventures_of_tom_sawyer__s37":
        "owner='Jim', goal_verb='saw' in 'help Jim...saw next-day's wood' -- verb-sense ambiguity, "
        "'saw' here is the tool-use sense (cut wood), not the perception verb 'see'; lemma_verb "
        "collapses both senses to the same PSYCH_VERBS-firing lemma",
}

# ---- Extended gender patch for names this larger 38-item bank introduces beyond v1's 15-item ------
# subset (mechanical, text-obvious per item; same discipline as v1's GENDER_PATCH, not invented).
# Place/object/collective "owners" (york, england, portsmouth, brahmins, moonstone, time, states,
# french, lausanne, helstone, sunnyside, baldy, rabbit) are OWNER-WRONG or non-person and
# intentionally left unpatched -- gender=None for those is honest (they are not gendered people;
# 3 of them are in OWNER_WRONG_IDS already, the rest never become pronoun antecedents in-bank).
GENDER_PATCH_EXT = {
    "alice": "f", "annie": "f", "beatrice": "f", "celia": "f", "curtis": "m", "dale": "m",
    "dorothea": "f", "edith": "f", "evelyn": "m", "gabriel": "m", "good": "m", "hallock": "m",
    "halsey": "m", "jim": "m", "johnson": "m", "liddy": "f", "lucas": "m", "margaret": "f",
    "morel": "m", "oak": "m", "sahib": "f", "spencer": "f", "strether": "m", "temple": "f",
    "todd": "f", "warwick": "m", "waymarsh": "m", "charles": "m", "bennet": "m",
}
GENDER_PATCH = dict(_V1_GENDER_PATCH)
GENDER_PATCH.update(GENDER_PATCH_EXT)
_v1.GENDER_PATCH = GENDER_PATCH  # _build_c5_item (imported, reused bit-identical) reads this at call time


def self_test():
    """Pre-flight smoke: (1) mined file loads with the expected 38 items and OWNER_WRONG_IDS is a
    subset of it; (2) owner-correct count == 31 (cross-check vs commit c90173b48's disk-verified
    number); (3) one owner-correct item and one owner-wrong item both run end-to-end without crash
    via the reused run_item pipeline (real code path, not a synthetic-only branch)."""
    mined = {it["id"]: it for it in _load_mined()}
    assert len(mined) == 38, f"expected 38 mined items, got {len(mined)}"
    missing = [i for i in OWNER_WRONG_IDS if i not in mined]
    assert not missing, f"OWNER_WRONG_IDS references ids not in mined file: {missing}"
    n_correct = len(mined) - len(OWNER_WRONG_IDS)
    assert n_correct == 31, f"expected 31 owner-correct items, got {n_correct}"

    ok_id = "c3_1342_pride_and_prejudice__s30"  # Bingley control chain, owner-correct
    wrong_id = "c3_541_the_age_of_innocence__s3"  # York place-metonym, owner-wrong
    item_ok = _build_c5_item(mined[ok_id])
    res_ok = run_item(item_ok, scrambled=False)
    assert "typed" in res_ok, f"run_item did not return a typed field: {res_ok}"
    item_wr = _build_c5_item(mined[wrong_id])
    res_wr = run_item(item_wr, scrambled=False)
    assert "typed" in res_wr, f"run_item did not return a typed field: {res_wr}"
    print(f"[SELFTEST PASS] 38 items loaded, 31 owner-correct / 7 owner-wrong cross-checked; "
          f"pipeline runs end-to-end on ok={ok_id}(typed={res_ok['typed']}) and "
          f"wrong={wrong_id}(typed={res_wr['typed']}) via the reused run_item real code path.",
          flush=True)
    return True


def main():
    mined_list = _load_mined()
    mined = {it["id"]: it for it in mined_list}
    assert len(mined) == 38, f"expected 38 mined items on disk, got {len(mined)}"

    all_ids = list(mined.keys())
    owner_correct_ids = [i for i in all_ids if i not in OWNER_WRONG_IDS]
    assert len(owner_correct_ids) == 31, f"expected 31 owner-correct, got {len(owner_correct_ids)}"

    results = {}
    for mid in all_ids:
        mined_item = mined[mid]
        item = _build_c5_item(mined_item)
        res = run_item(item, scrambled=False)
        res["structure_type"] = mined_item.get("structure_type")
        res["owner_correct"] = (mid not in OWNER_WRONG_IDS)
        res["owner_wrong_reason"] = OWNER_WRONG_IDS.get(mid)
        results[mid] = res
        print(f"[c5-v2-38item] {mid}: owner_correct={res['owner_correct']} typed={res['typed']} "
              f"matches_gold={res.get('matches_gold')} recency_correct={res.get('recency_alone_matches_gold')}",
              flush=True)

    all_results = [results[i] for i in all_ids]
    owner_correct_results = [results[i] for i in owner_correct_ids]

    def _bucket(rows):
        n = len(rows)
        typed_rows = [r for r in rows if r["typed"]]
        n_typed = len(typed_rows)
        n_correct = sum(1 for r in typed_rows if r["matches_gold"])
        n_recency_correct = sum(1 for r in typed_rows if r["recency_alone_matches_gold"])
        n_divergent = sum(1 for r in typed_rows if r.get("baseline_owner") != r.get("content_owner"))
        return dict(
            n=n, n_typed=n_typed,
            typing_fire_rate=round(n_typed / n, 4) if n else None,
            outcome_binding_accuracy=round(n_correct / n_typed, 4) if n_typed else None,
            recency_baseline=round(n_recency_correct / n_typed, 4) if n_typed else None,
            n_correct=n_correct, n_recency_correct=n_recency_correct,
            n_candidate_divergent=n_divergent,
            candidate_divergence_rate=round(n_divergent / n_typed, 4) if n_typed else None,
            selection_mechanism_exercised=(n_divergent > 0),
        )

    owner_subset_bucket = _bucket(owner_correct_results)  # (a) C5 binding, owner-ID errors excluded

    # (b) FULL end-to-end (per task brief): an item only counts correct if BOTH owner-ID is correct
    # AND the pipeline binds the outcome to the true owner. Owner-wrong items are typed/scored by
    # the pipeline same as any item (against the mined -- possibly wrong -- `gold_outcome_owner`),
    # but are FORCED to not-count-as-correct in the full-pipeline number regardless of what the
    # pipeline output was, because the "gold" itself misidentifies the true real-world referent.
    n_full = len(all_results)
    typed_full = [r for r in all_results if r["typed"]]
    n_typed_full = len(typed_full)
    n_full_correct = sum(1 for r in typed_full if r["owner_correct"] and r["matches_gold"])
    n_full_recency_correct = sum(1 for r in typed_full if r["owner_correct"] and r["recency_alone_matches_gold"])
    n_divergent_full = sum(1 for r in typed_full if r.get("baseline_owner") != r.get("content_owner"))
    full_bucket = dict(
        n=n_full, n_typed=n_typed_full,
        typing_fire_rate=round(n_typed_full / n_full, 4) if n_full else None,
        # denominator = n_typed_full (all typed items, incl owner-wrong) -- the true end-to-end rate
        outcome_binding_accuracy_full_pipeline=round(n_full_correct / n_typed_full, 4) if n_typed_full else None,
        recency_baseline_full_pipeline=round(n_full_recency_correct / n_typed_full, 4) if n_typed_full else None,
        n_correct=n_full_correct, n_recency_correct=n_full_recency_correct,
        n_candidate_divergent=n_divergent_full,
        candidate_divergence_rate=round(n_divergent_full / n_typed_full, 4) if n_typed_full else None,
        selection_mechanism_exercised=(n_divergent_full > 0),
    )

    # per structure_type breakdown (owner-correct subset AND full, honest small-N transparency)
    def _by_struct(rows):
        by = {}
        for r in rows:
            st = r.get("structure_type") or "unknown"
            d = by.setdefault(st, dict(n=0, n_typed=0, n_correct=0, n_owner_correct=0))
            d["n"] += 1
            if r["owner_correct"]:
                d["n_owner_correct"] += 1
            if r["typed"]:
                d["n_typed"] += 1
                if r["owner_correct"] and r["matches_gold"]:
                    d["n_correct"] += 1
        return by

    by_structure_type = _by_struct(all_results)

    # FAILURE DECOMPOSITION (per task brief "decompose the number honestly"): for every item, class
    # the failure mode -- OWNER_ID_ERROR (upstream C3 owner mining wrong, this cell's OWNER_WRONG_IDS)
    # / TYPING_MISS (owner-correct but GOAL/OUTCOME never typed) / BINDING_ERROR (owner-correct,
    # typed, but final_owner != gold) / CORRECT.
    failure_decomp = dict(OWNER_ID_ERROR=0, TYPING_MISS=0, BINDING_ERROR=0, CORRECT=0)
    for mid in all_ids:
        r = results[mid]
        if not r["owner_correct"]:
            failure_decomp["OWNER_ID_ERROR"] += 1
        elif not r["typed"]:
            failure_decomp["TYPING_MISS"] += 1
        elif not r["matches_gold"]:
            failure_decomp["BINDING_ERROR"] += 1
        else:
            failure_decomp["CORRECT"] += 1
    assert sum(failure_decomp.values()) == 38, f"decomposition does not sum to 38: {failure_decomp}"

    verdict = "MEASURED_HONEST_NUMBER"  # per task brief: this is a measurement, not a pass/fail cell
    reframe_holds = (owner_subset_bucket["candidate_divergence_rate"] in (0.0, None))

    metrics = dict(
        anchor_name=ANCHOR_NAME,
        n_items=38, n_owner_correct=31, n_owner_wrong=7,
        owner_correct_subset=owner_subset_bucket,
        full_pipeline=full_bucket,
        failure_decomposition=failure_decomp,
        by_structure_type=by_structure_type,
        reframe_holds_c5_edge_case=reframe_holds,
        owner_wrong_ids=OWNER_WRONG_IDS,
        per_item={mid: results[mid] for mid in all_ids},
        verdict=verdict,
        verdict_msg=(
            f"MEASURED (38 items, 31 owner-correct, 7 owner-wrong; directional small-N): "
            f"owner_correct_subset(n_typed={owner_subset_bucket['n_typed']}/31): "
            f"outcome_binding_acc={owner_subset_bucket['outcome_binding_accuracy']} "
            f"recency_baseline={owner_subset_bucket['recency_baseline']} "
            f"candidate_divergence_rate={owner_subset_bucket['candidate_divergence_rate']} | "
            f"full_pipeline_incl_owner_errors(n_typed={full_bucket['n_typed']}/38): "
            f"outcome_binding_acc={full_bucket['outcome_binding_accuracy_full_pipeline']} "
            f"recency_baseline={full_bucket['recency_baseline_full_pipeline']} | "
            f"failure_decomposition={failure_decomp} | "
            f"reframe_holds_c5_edge_case={reframe_holds}"
        ),
        n=38, small_n=True, elapsed_s=0.0,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        prereg_note="MEASUREMENT cell per task brief; no formal pre-reg bands (verdict is the "
                     "measured number, not a forced pass/fail); reuses exp_c5_realtext_c3mined_v1.py "
                     "pipeline bit-identical on the improved 38-item goal_outcome_c3mined_v1.jsonl.",
        source_mined_path=MINED_PATH,
    )
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = OUTPUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, OUTPUT_PATH)
    print(f"[VERDICT] {metrics['verdict_msg']}", flush=True)
    return metrics


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    try:
        if args.self_test:
            raise SystemExit(0 if self_test() else 1)
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        tmp = OUTPUT_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            json.dump(dict(
                verdict="CELL_CRASHED", verdict_msg=f"{type(e).__name__}: {str(e)[:500]}",
                summary=f"CELL_CRASHED: {type(e).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(),
                anchor_name=ANCHOR_NAME,
            ), f, indent=2)
        os.replace(tmp, OUTPUT_PATH)
        raise
