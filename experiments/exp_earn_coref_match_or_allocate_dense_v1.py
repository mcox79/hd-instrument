"""EARN-COREFERENCE PROBE (DENSE re-run): SAME mechanism as
exp_earn_coref_match_or_allocate_v1.py (commit 68d25389b), ONE VARIABLE swapped -- the eval file
now points at data/eval_gold_mention_role_mcguffey_v1/gold_multientity_dense_v1.jsonl (18
passages, 3.67 entities/passage, 3-5 co-present SAME-GENDER entities -- multi-speaker dialogues
and group scenes) instead of gold_multiclause_LONG_v1.jsonl (24 passages, 1.46 entities/passage).

WHY THE RE-RUN: the LONG-gold probe found learnable coref beats random cleanly but could not beat
the naive recency-chain-everything floor (learn F1=0.8504 vs recency F1=0.8581) -- root cause was
NOT a mechanism failure but an EVAL-DENSITY failure: at 1.46 entities/passage, "chain everything
into one cluster" is nearly correct by construction (few passages have >1 entity to confuse).
The dense eval was hand-mined specifically so multi-entity co-presence forces the recency floor to
mis-merge distinct same-gender speakers -- a fair test the sparse eval could not run.

MECHANISM: reused VERBATIM from exp_earn_coref_match_or_allocate_v1.py (match-or-allocate,
Centering/discourse-salience constants from hdlab.state_of_mind, own lightweight token-overlap +
gender/number + determiner-bridging registry). No mechanism code changed; only GOLD_PATH and the
added entity-count stratification / error-diagnostic reporting are new in this file.

CAN-FAIL (same contract as the LONG-gold probe):
  (a) RANDOM assignment must score far worse than LEARNABLE.
  (b) RECENCY-ONLY floor must be beaten by LEARNABLE by >= 5% absolute B3-F1.
  KEY additional check for THIS probe: the recency floor's F1 should be markedly LOWER here than
  on the sparse LONG-gold (0.8581) -- that drop is the fair-test precondition. If the floor does
  NOT drop, the density manipulation didn't work as intended and the "fair test" claim is void.

METRIC: B-cubed precision/recall/F1 (identical bcubed() implementation), overall + name/pronoun
breakdown + NEW: entity-count-stratified (passages grouped by entity_count field) + a per-passage
error diagnostic (which gold entities the learnable arm split or merged) to aim the next lever.

Self-test: python exp_earn_coref_match_or_allocate_dense_v1.py --self-test
Full:      python exp_earn_coref_match_or_allocate_dense_v1.py
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.state_of_mind import (  # noqa: E402
    PRONOUN_SCOPE,
    infer_nominal_gender,
)

# Reuse the exact mechanism functions from the LONG-gold probe (verbatim, no reimplementation).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exp_earn_coref_match_or_allocate_v1 import (  # noqa: E402
    normalize_tokens,
    is_pronoun_mention,
    gender_number_for,
    gn_compatible,
    _Entity,
    run_learnable,
    run_recency_floor,
    run_random,
    bcubed,
    HARD_PASS_MARGIN,
    BASELINE_IN_BAND_LO,
    BASELINE_IN_BAND_HI,
    RANDOM_SEED,
)

ANCHOR_NAME = "earn_coref_match_or_allocate_dense_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multientity_dense_v1.jsonl"
)
SPARSE_GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multiclause_LONG_v1.jsonl"
)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
PRIOR_SPARSE_RECENCY_F1 = 0.8581  # from commit 68d25389b, for the fair-test-precondition check


def load_passages(path: str) -> List[dict]:
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return passages


def build_mention_stream(passage: dict) -> List[dict]:
    """Identical logic to the LONG-gold probe's build_mention_stream (duplicated here only
    because it is a short, self-contained function; all downstream identity-tracking functions
    are imported, not reimplemented)."""
    clauses = passage["clauses"]
    raw = []
    for ent_name, mentions in passage["entities"].items():
        for m in mentions:
            mtxt = m["mention"]
            if mtxt.strip().startswith("("):
                continue
            clause_idx = m["clause"]
            clause_text = clauses[clause_idx].lower()
            first_tok = mtxt.split()[0].lower().strip(".,'\"!?;:()/")
            pos = clause_text.find(first_tok)
            if pos < 0:
                pos = 0
            is_pron = is_pronoun_mention(mtxt)
            gender, number = gender_number_for(mtxt, is_pron)
            first_word = mtxt.strip().split()[0].lower().strip(".,'\"") if mtxt.strip() else ""
            has_determiner = first_word in {"the", "a", "an"}
            raw.append(
                {
                    "gold_entity": ent_name,
                    "clause": clause_idx,
                    "mention_text": mtxt,
                    "is_pronoun": is_pron,
                    "gender": gender,
                    "number": number,
                    "text_pos": pos,
                    "has_determiner": has_determiner,
                }
            )
    raw.sort(key=lambda r: (r["clause"], r["text_pos"]))
    return raw


# ---------------------------------------------------------------------------
# Error diagnostic: for the learnable arm, find which gold-entity pairs got MERGED (share a
# predicted cluster but are distinct gold entities) or SPLIT (same gold entity, different
# predicted clusters) -- classified by mention surface form to aim the next lever.
# ---------------------------------------------------------------------------
def diagnose_errors(passage_id: str, stream: List[dict], preds: List[int]) -> List[dict]:
    errs = []
    m = len(stream)
    for i in range(m):
        for j in range(i + 1, m):
            same_gold = stream[i]["gold_entity"] == stream[j]["gold_entity"]
            same_pred = preds[i] == preds[j]
            if same_gold and not same_pred:
                errs.append({
                    "passage_id": passage_id, "type": "SPLIT",
                    "gold_entity": stream[i]["gold_entity"],
                    "mention_a": stream[i]["mention_text"], "mention_b": stream[j]["mention_text"],
                })
            elif not same_gold and same_pred:
                errs.append({
                    "passage_id": passage_id, "type": "MERGE",
                    "gold_entity_a": stream[i]["gold_entity"], "gold_entity_b": stream[j]["gold_entity"],
                    "mention_a": stream[i]["mention_text"], "mention_b": stream[j]["mention_text"],
                })
    return errs


# ---------------------------------------------------------------------------
# Self-test: exercises the real code path (dense gold load, stream build, all 3 arms, bcubed,
# error diagnostic) plus the same synthetic Alice/Bob fixture the LONG-gold probe used, to
# confirm the imported mechanism functions still behave identically when reused from this file.
# ---------------------------------------------------------------------------
def self_test() -> None:
    fixture = [
        {
            "passage_id": "t1",
            "clauses": ["Alice went to the store.", "She bought bread.", "Bob saw her there."],
            "entities": {
                "Alice": [
                    {"clause": 0, "mention": "Alice", "role": "agent"},
                    {"clause": 1, "mention": "She", "role": "agent"},
                    {"clause": 2, "mention": "her", "role": "patient"},
                ],
                "Bob": [{"clause": 2, "mention": "Bob", "role": "agent"}],
            },
        }
    ]
    stream = build_mention_stream(fixture[0])
    assert len(stream) == 4
    learn_pred = run_learnable(stream)
    alice_idxs = [i for i, r in enumerate(stream) if r["gold_entity"] == "Alice"]
    bob_idxs = [i for i, r in enumerate(stream) if r["gold_entity"] == "Bob"]
    alice_ids = {learn_pred[i] for i in alice_idxs}
    bob_ids = {learn_pred[i] for i in bob_idxs}
    assert len(alice_ids) == 1, f"learnable failed to chain Alice/She/her: {alice_ids}"
    assert alice_ids.isdisjoint(bob_ids), "learnable incorrectly merged Alice and Bob"

    # 3-entity same-gender fixture: recency floor MUST mis-merge here (the fair-test property).
    fixture3 = {
        "passage_id": "t2",
        "clauses": ["Robert spoke.", "Willie spoke.", "Harry spoke."],
        "entities": {
            "Robert": [{"clause": 0, "mention": "Robert", "role": "agent"}],
            "Willie": [{"clause": 1, "mention": "Willie", "role": "agent"}],
            "Harry": [{"clause": 2, "mention": "Harry", "role": "agent"}],
        },
    }
    stream3 = build_mention_stream(fixture3)
    assert len(stream3) == 3
    learn3 = run_learnable(stream3)
    rec3 = run_recency_floor(stream3)
    b_learn3 = bcubed([(stream3, learn3)])
    b_rec3 = bcubed([(stream3, rec3)])
    assert b_learn3["f1"] == 1.0, f"learnable must perfectly separate 3 distinct bare-name entities: {b_learn3}"
    assert rec3 == [0, 0, 0], "recency floor must chain all 3 into one cluster (the trap this eval targets)"
    assert b_rec3["f1"] < b_learn3["f1"], "recency floor must score worse than learnable on the 3-entity trap"

    errs = diagnose_errors("t2", stream3, rec3)
    assert any(e["type"] == "MERGE" for e in errs), "diagnose_errors must catch the recency floor's merge"

    assert os.path.exists(GOLD_PATH), f"dense gold file missing: {GOLD_PATH}"
    real_passages = load_passages(GOLD_PATH)
    assert len(real_passages) == 18, f"expected 18 dense passages, got {len(real_passages)}"
    real_stream = build_mention_stream(real_passages[0])
    assert len(real_stream) > 0
    _ = run_learnable(real_stream)

    print("[SELF-TEST] PASS: dense gold real code path exercised, 3-entity trap + bcubed + diagnostic verified")


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

    streams = [build_mention_stream(p) for p in passages]
    n_mentions_total = sum(len(s) for s in streams)
    n_pronoun = sum(1 for s in streams for r in s if r["is_pronoun"])
    n_name = n_mentions_total - n_pronoun

    import random
    rng = random.Random(RANDOM_SEED)

    learn_preds = [run_learnable(s) for s in streams]
    rec_preds = [run_recency_floor(s) for s in streams]
    rand_preds = [run_random(s, rng) for s in streams]

    arms = {
        "learnable": list(zip(streams, learn_preds)),
        "recency_floor": list(zip(streams, rec_preds)),
        "random": list(zip(streams, rand_preds)),
    }
    results = {}
    for arm_name, pairs in arms.items():
        results[arm_name] = {
            "overall": bcubed(pairs),
            "name_only": bcubed(pairs, subset="name"),
            "pronoun_only": bcubed(pairs, subset="pronoun"),
        }

    # Entity-count stratification (2 vs 3 vs 4-5).
    strata: Dict[str, List[int]] = {}
    for idx, p in enumerate(passages):
        ec = p.get("entity_count", len(p["entities"]))
        bucket = "2" if ec <= 2 else ("3" if ec == 3 else "4_5")
        strata.setdefault(bucket, []).append(idx)
    strat_results = {}
    for bucket, idxs in sorted(strata.items()):
        for arm_name in arms:
            pairs_b = [(streams[i], (learn_preds if arm_name == "learnable"
                                      else rec_preds if arm_name == "recency_floor"
                                      else rand_preds)[i]) for i in idxs]
            strat_results.setdefault(bucket, {})[arm_name] = bcubed(pairs_b)
        strat_results[bucket]["n_passages"] = len(idxs)

    # Error diagnostic on the learnable arm (which gold entities split/merged, by construction).
    all_errs = []
    for p, s, pred in zip(passages, streams, learn_preds):
        all_errs.extend(diagnose_errors(p["passage_id"], s, pred))
    n_merge = sum(1 for e in all_errs if e["type"] == "MERGE")
    n_split = sum(1 for e in all_errs if e["type"] == "SPLIT")
    # tag by construction class (multi_speaker_dialogue / cross_species / appositive-like) for
    # each errored passage, to see which hard_feature the errors cluster on.
    err_passage_ids = {e["passage_id"] for e in all_errs}
    construction_of_errs = {}
    for p in passages:
        if p["passage_id"] in err_passage_ids:
            constr = p.get("construction", "unknown")
            construction_of_errs[constr] = construction_of_errs.get(constr, 0) + 1

    learn_f1 = results["learnable"]["overall"]["f1"]
    rec_f1 = results["recency_floor"]["overall"]["f1"]
    rand_f1 = results["random"]["overall"]["f1"]

    beats_recency = (learn_f1 - rec_f1) >= HARD_PASS_MARGIN
    beats_random = (learn_f1 - rand_f1) >= HARD_PASS_MARGIN
    floors_in_band = (BASELINE_IN_BAND_LO < rec_f1 < BASELINE_IN_BAND_HI) and \
                      (BASELINE_IN_BAND_LO < rand_f1 < BASELINE_IN_BAND_HI)
    floor_collapsed_vs_sparse = rec_f1 < (PRIOR_SPARSE_RECENCY_F1 - HARD_PASS_MARGIN)

    if beats_recency and beats_random and floors_in_band:
        verdict = "HARD_PASS_LEARNABLE_BEATS_BOTH_FLOORS_ON_DENSE_EVAL"
    elif beats_recency and beats_random:
        verdict = "MIDDLE_BAND_FLOORS_DEGENERATE"
    elif not floor_collapsed_vs_sparse:
        verdict = "MIDDLE_BAND_DENSITY_MANIPULATION_DID_NOT_COLLAPSE_FLOOR"
    else:
        verdict = "HARD_FAIL_LEARNABLE_DOES_NOT_BEAT_FLOOR_EVEN_ON_DENSE_EVAL"

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": (
            f"learnable_f1={learn_f1:.4f} recency_floor_f1={rec_f1:.4f} random_f1={rand_f1:.4f} "
            f"beats_recency={beats_recency} beats_random={beats_random} "
            f"floor_collapsed_vs_sparse(prior={PRIOR_SPARSE_RECENCY_F1:.4f})={floor_collapsed_vs_sparse} "
            f"n_passages={len(passages)} n_mentions={n_mentions_total} "
            f"n_name={n_name} n_pronoun={n_pronoun} n_merge_errs={n_merge} n_split_errs={n_split}"
        ),
        "summary": verdict,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "n_passages": len(passages),
        "n_mentions_total": n_mentions_total,
        "n_name_mentions": n_name,
        "n_pronoun_mentions": n_pronoun,
        "arms": results,
        "entity_count_stratified": strat_results,
        "error_diagnostic": {
            "n_merge_errs": n_merge,
            "n_split_errs": n_split,
            "construction_class_of_errored_passages": construction_of_errs,
            "sample_errs": all_errs[:20],
        },
        "cardinality_ok": len(streams) == len(passages),
        "bands": {
            "hard_pass_margin": HARD_PASS_MARGIN,
            "baseline_in_band": [BASELINE_IN_BAND_LO, BASELINE_IN_BAND_HI],
        },
        "gold_path": GOLD_PATH,
        "prior_sparse_gold_path": SPARSE_GOLD_PATH,
        "prior_sparse_recency_f1": PRIOR_SPARSE_RECENCY_F1,
        "prior_commit": "68d25389b",
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
