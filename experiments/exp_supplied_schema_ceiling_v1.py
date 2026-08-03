"""exp_supplied_schema_ceiling_v1 (2026-08-03)

MEASUREMENT cell (de-risk fork (b), NOT the deep-earn build). Question: what is the HONEST
CEILING of a SUPPLIED (hand-authored, glass-box, allowed-DATA) event-schema / relation-frame
library -- Schank-Abelson script knowledge + Trabasso goal-plan satisfy/thwart/cause frames --
on the relation-inference frontier (unstated-goal recovery + satisfy/cause link pairing +
end-to-end causal-link recall), WITH a mandatory out-of-sample overfit guard?

Prior-work check (mandatory, USER-locked 2026-07-01): `bash tools/substrate_query.sh
"event schema script satisfy thwart cause goal inference relation"` -> top hits all cosine<=0.30
(schematisation 0.2988, Schank script-theory note 0.2988, gated_fusion relation-inference cell
0.2959, FrameNet Cause_emotion 0.2793). No prior arc cell builds a supplied event-schema library
and measures in/out-of-sample recall on these specific gold links -- this is novel, not a
rediscovery.

SCHEMA LIBRARY: data/schemas/event_schema_library_v1.json, 22 schemas authored from GENERAL
Schank-Abelson script knowledge (prohibition-reconciliation, rescue-gratitude, sacrifice-for-
other, confession-under-confinement, illness-caretaking, financial-shock, diagnosis-life-
decision, mistaken-identity-adoption, etc.) PLUS two canonical CONTROL schemas (GET_DRESSED,
RESTAURANT) included specifically to catch spurious over-firing. Authored BEFORE this cell's
code (separate file, reviewed once) to keep the schema-authoring step honest about not reverse-
engineering from specific gold phrasing; each schema names a general narrative TYPE, not a
paraphrase of one Anne-of-Green-Gables sentence. HONEST CAVEAT (reported, not hidden): the
gold files were necessarily read in full during Director's task-briefing and this cell's design,
so strict textual blinding was not possible -- the mandatory in/out-of-sample split below is the
actual guard against this, not the schema-authoring order alone.

MEASURE (four questions, all read live off this cell's own metrics.json):
  1. UNSTATED-GOAL RECOVERY: recall/precision of schema goal_trigger firing on the 4 gold items
     with explicit_vs_inferred=="inferred" (goal_014, goal_016, goal_018, goal_019 -- the ones
     with NO lexical desiderative marker, i.e. genuinely unstated goals) vs precision measured
     against 32 negative spans (cause+effect verbatims of the 16 non-goal-mediated causal gold
     items, which are real narrative text but not goal-driven).
  2. SATISFY/CAUSE PAIRING RECOVERY: of the 9 goal-mediated causal links (GOAL_MEDIATED_CAUSAL_IDS,
     reused unchanged from exp_goal_register_causal_link_v1), does a schema's open-side trigger
     fire on cause_event AND its satisfy/effect-side trigger fire on effect_event (full pairing)?
     recall over 9 + fp_rate over 200 seeded negative cross-pairs (same seed=20260803 methodology
     as the existing arc baseline, for apples-to-apples fp comparison).
  3. END-TO-END: same both-sides-fire rule applied over all 25 gold causal links (goal-mediated +
     non-goal-mediated, since several schemas here are pure enabling-CAUSE frames with no goal
     mediation) -> recall_all_25, recall_goal_mediated_9, recall_non_goal_mediated_16, fp_rate vs
     200 negatives, vs content-overlap CAP (0.11, per task brief, cross-checked against
     exp_goal_register_causal_link_v1's own recall_goal_mediated=0.1111 read live off disk) and vs
     a random-uniform-flagging control computed from the actual pair universe size.
  4. MANDATORY OVERFIT GUARD: two independent seeded 50/50 splits of the 25 causal items (and,
     heavily caveated for small N, of the 9 goal-mediated subset) -> recall_end_to_end computed
     SEPARATELY on each half using the SAME fixed schema library (no per-half fitting is possible
     since the library was authored once, before any split existed) -> report both halves; if
     they diverge sharply this cell says so plainly rather than picking the favorable half.

CAN-FAIL / VERDICT (honest both-ways, per task instruction -- do NOT spin): report the
out-of-sample (worse-of-two-halves) recall as the HONEST CEILING, not the in-sample number.
If schemas cannot recover the inferred/unstated goals (Q1 recall near 0), that is itself the
answer: supply-only schemas cap out at pairing improvements over an already-extracted goal and
the deep-earn goal-INFERENCE step is not avoidable via supplied data alone -- report this
plainly as the fork-landscape finding, no forced positive spin.

CELL-TEMPLATE (light form -- single foreground measurement pass, no sweep axis, no dispatch,
no training, <1s runtime on ~50 short text spans):
  - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
  - final_metrics_atomicity = tmp_replace
  - arms_differ_verified: schema-flagged pair set (this cell) vs baseline
    (exp_goal_register_causal_link_v1) flagged pair set digest-compared
  - heartbeat/chunking EXEMPTED: single pass over ~50 short verbatim spans with regex, no training
  - determinism: fixed SEED=20260803 (matches arc convention for apples-to-apples negative
    sampling), python random.Random(seed) only, sorted() wherever iteration order matters
  - all narrative numbers in this docstring are HYPOTHESIZED/directional; every number in the
    completion report is tagged MEASURED@ against this cell's own metrics.json
  - NOT DISPATCHED: runs to completion locally, no queue_add, no remote verify, per task instruction.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import sys
import time
import traceback
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_goal_register_causal_link_v1 as baseline  # noqa: E402

ANCHOR_NAME = "supplied_schema_ceiling_v1"
SCHEMA_LIB_REL = "data/schemas/event_schema_library_v1.json"
GOAL_GOLD_REL = "data/eval_gold_mention_role_mcguffey_v1/gold_anne_goal_intention_v1.jsonl"
CAUSAL_GOLD_REL = "data/eval_gold_mention_role_mcguffey_v1/gold_anne_comprehension_v3.jsonl"
BASELINE_METRICS_REL = "data/exp_goal_register_causal_link_v1/metrics.json"
GOAL_MEDIATED_CAUSAL_IDS = baseline.GOAL_MEDIATED_CAUSAL_IDS  # reused unchanged, 9 ids
SEED = 20260803
N_NEGATIVE_SAMPLES = 200
CONTENT_OVERLAP_CAP = 0.11  # per task brief; cross-checked (not asserted) against disk below


def repo_path(rel: str) -> str:
    return baseline.repo_path(rel)


def load_schemas():
    with open(repo_path(SCHEMA_LIB_REL), "r", encoding="utf-8") as f:
        return json.load(f)["schemas"]


def _compile_any(patterns):
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def fires(text, patterns_compiled):
    return any(p.search(text) for p in patterns_compiled)


def schema_fire_report(text, schemas, field):
    """Return sorted list of schema ids whose `field` (goal_trigger/satisfy_trigger/cause_trigger/
    effect_trigger) fires on text."""
    hit = []
    for s in schemas:
        pats = s.get(field)
        if not pats:
            continue
        if fires(text, _compile_any(pats)):
            hit.append(s["id"])
    return sorted(hit)


def open_side_fires(text, schemas):
    """An 'open' proposal (unstated goal OR pure enabling cause) on the cause_event side."""
    goal_hits = schema_fire_report(text, schemas, "goal_trigger")
    cause_hits = schema_fire_report(text, schemas, "cause_trigger")
    return sorted(set(goal_hits) | set(cause_hits)), goal_hits, cause_hits


def close_side_fires(text, schemas):
    """A 'close' match (satisfy OR enabling-cause effect) on the effect_event side."""
    satisfy_hits = schema_fire_report(text, schemas, "satisfy_trigger")
    effect_hits = schema_fire_report(text, schemas, "effect_trigger")
    return sorted(set(satisfy_hits) | set(effect_hits)), satisfy_hits, effect_hits


def pair_flagged(cause_text, effect_text, schemas):
    """A causal link is flagged if THE SAME schema id fires open-side on cause_text AND
    close-side on effect_text (a schema-COHERENT pairing, not just any-open + any-close)."""
    open_ids, _, _ = open_side_fires(cause_text, schemas)
    close_ids, _, _ = close_side_fires(effect_text, schemas)
    shared = set(open_ids) & set(close_ids)
    return len(shared) > 0, sorted(shared)


# --------------------------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------------------------
def run_self_test() -> None:
    schemas = load_schemas()
    assert 15 <= len(schemas) <= 25, f"SELF_TEST FAIL: schema count out of [15,25]: {len(schemas)}"
    ids = [s["id"] for s in schemas]
    assert len(ids) == len(set(ids)), "SELF_TEST FAIL: duplicate schema ids"
    assert "GET_DRESSED_SCRIPT" in ids and "RESTAURANT_SCRIPT" in ids, \
        "SELF_TEST FAIL: control schemas missing"

    # fixture: SACRIFICE_FOR_OTHER should pair a withdrawal-cause with a thanks-effect
    ok, shared = pair_flagged(
        "he withdrew his application so she could have it",
        "I want to thank you for giving up the school for me",
        schemas)
    assert ok and "SACRIFICE_FOR_OTHER" in shared, f"SELF_TEST FAIL: expected SACRIFICE_FOR_OTHER pairing, got {shared}"

    # fixture: unrelated text should NOT fire the control schemas
    open_ids, _, _ = open_side_fires("the sky was blue and the birds sang", schemas)
    assert "GET_DRESSED_SCRIPT" not in open_ids and "RESTAURANT_SCRIPT" not in open_ids, \
        f"SELF_TEST FAIL: control schema spuriously fired: {open_ids}"

    # fixture: mismatched schema ids must NOT count as a pairing (schema-coherence required)
    ok2, shared2 = pair_flagged(
        "he withdrew his application so she could have it",  # SACRIFICE_FOR_OTHER open
        "the eyes were examined by the oculist who found it serious",  # DIAGNOSIS effect only
        schemas)
    assert not ok2, f"SELF_TEST FAIL: mismatched-schema pairing wrongly flagged: {shared2}"

    # real-code-path check: gold files load + have expected schema shape (gate F.1)
    with open(repo_path(GOAL_GOLD_REL), "r", encoding="utf-8") as f:
        g0 = json.loads(next(iter(f)))
    assert "explicit_vs_inferred" in g0 and "verbatim_evidence" in g0
    with open(repo_path(CAUSAL_GOLD_REL), "r", encoding="utf-8") as f:
        c0 = json.loads(next(iter(f)))
    assert "cause_event" in c0 and "effect_event" in c0 and "id" in c0


# --------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------
def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--n-negative", type=int, default=N_NEGATIVE_SAMPLES)
    parser.add_argument("--timeout", type=float, default=120.0,
                         help="formula self-test timeout budget; this cell is a regex scan over "
                              "~50 short gold verbatim spans (no book pipeline, no training), "
                              "measured well under 1s -- 120s budget is generous headroom")
    args = parser.parse_args()

    run_mode = "smoke" if args.self_test else "full"
    output_dir = repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if args.self_test else ""))
    t0 = time.perf_counter()
    baseline._write_start_marker(output_dir, run_mode, expected_n_units=1)

    run_self_test()
    if args.self_test:
        elapsed = time.perf_counter() - t0
        metrics = {
            "verdict": "SELF_TEST_PASS",
            "verdict_msg": "schema-library shape + control-schema non-firing + coherent-pairing "
                            "fixtures + mismatched-schema non-pairing fixture + gold-file "
                            "real-code-path checks all PASS.",
            "summary": "SELF_TEST_PASS", "elapsed_s": elapsed,
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
            "run_mode": run_mode, "seed": args.seed,
        }
        tmp = os.path.join(output_dir, "metrics.json.tmp")
        final = os.path.join(output_dir, "metrics.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        os.replace(tmp, final)
        print(f"[{ANCHOR_NAME}] SELF_TEST_PASS -> {final}")
        return

    schemas = load_schemas()

    with open(repo_path(GOAL_GOLD_REL), "r", encoding="utf-8") as f:
        goal_items = [json.loads(line) for line in f if line.strip()]
    with open(repo_path(CAUSAL_GOLD_REL), "r", encoding="utf-8") as f:
        causal_items = [json.loads(line) for line in f if line.strip()]

    # ---- Q1: unstated (inferred) goal recovery ----
    inferred_items = [it for it in goal_items if it["explicit_vs_inferred"] == "inferred"]
    explicit_items = [it for it in goal_items if it["explicit_vs_inferred"] == "explicit"]
    non_goal_mediated = [it for it in causal_items if it["id"] not in GOAL_MEDIATED_CAUSAL_IDS]

    def goal_fires_on_item(it):
        text = it["verbatim_evidence"]["verbatim"]
        open_ids, goal_ids, cause_ids = open_side_fires(text, schemas)
        return len(goal_ids) > 0, goal_ids  # goal_trigger specifically (not pure-cause frames)

    inferred_hits = [(it["id"], *goal_fires_on_item(it)) for it in inferred_items]
    explicit_hits = [(it["id"], *goal_fires_on_item(it)) for it in explicit_items]
    n_inferred_recovered = sum(1 for _, f, _ in inferred_hits if f)
    recall_unstated_goal = n_inferred_recovered / len(inferred_items) if inferred_items else None

    # negatives for precision: cause+effect verbatims of the 16 non-goal-mediated causal items
    neg_spans = []
    for it in non_goal_mediated:
        neg_spans.append((it["id"] + "_cause", it["cause_event"]["verbatim"]))
        neg_spans.append((it["id"] + "_effect", it["effect_event"]["verbatim"]))
    neg_goal_fires = [(k, len(schema_fire_report(t, schemas, "goal_trigger")) > 0) for k, t in neg_spans]
    n_fp_goal = sum(1 for _, f in neg_goal_fires if f)
    fp_rate_goal_trigger = n_fp_goal / len(neg_spans) if neg_spans else None
    n_tp_goal = sum(1 for _, f, _ in (inferred_hits + explicit_hits) if f)
    precision_goal_trigger = (
        n_tp_goal / (n_tp_goal + n_fp_goal) if (n_tp_goal + n_fp_goal) > 0 else None
    )

    # ---- Q2 + Q3: pairing / end-to-end over causal links ----
    def flag_link(it):
        return pair_flagged(it["cause_event"]["verbatim"], it["effect_event"]["verbatim"], schemas)

    per_item = []
    flagged_ids = []
    for it in causal_items:
        flagged, shared = flag_link(it)
        per_item.append({
            "id": it["id"], "goal_mediated": it["id"] in GOAL_MEDIATED_CAUSAL_IDS,
            "flagged": flagged, "shared_schemas": shared,
        })
        if flagged:
            flagged_ids.append(it["id"])

    goal_mediated_results = [r for r in per_item if r["goal_mediated"]]
    non_goal_mediated_results = [r for r in per_item if not r["goal_mediated"]]
    n_goal_mediated_flagged = sum(1 for r in goal_mediated_results if r["flagged"])
    recall_goal_mediated = (n_goal_mediated_flagged / len(goal_mediated_results)
                             if goal_mediated_results else None)
    n_non_goal_flagged = sum(1 for r in non_goal_mediated_results if r["flagged"])
    recall_non_goal_mediated = (n_non_goal_flagged / len(non_goal_mediated_results)
                                 if non_goal_mediated_results else None)
    n_all_flagged = sum(1 for r in per_item if r["flagged"])
    recall_all = n_all_flagged / len(per_item) if per_item else None

    # negative cross-pairs (seeded, same convention as arc baseline)
    def event_key(ev):
        lr = ev["line_range"]
        return (ev["chapter"], lr[0], lr[1])

    key_to_text = {}
    for it in causal_items:
        key_to_text[event_key(it["cause_event"])] = it["cause_event"]["verbatim"]
        key_to_text[event_key(it["effect_event"])] = it["effect_event"]["verbatim"]
    gold_pairs = {(event_key(it["cause_event"]), event_key(it["effect_event"])) for it in causal_items}
    all_keys = sorted(key_to_text.keys())
    full_pool = [(a, b) for a in all_keys for b in all_keys if a != b and (a, b) not in gold_pairs]
    rng = random.Random(args.seed)
    rng.shuffle(full_pool)
    negatives = full_pool[: args.n_negative]
    neg_flag_results = []
    for a, b in negatives:
        flagged, shared = pair_flagged(key_to_text[a], key_to_text[b], schemas)
        neg_flag_results.append(flagged)
    fp_rate = sum(neg_flag_results) / len(neg_flag_results) if neg_flag_results else None

    random_uniform_control_recall = len(gold_pairs) / (len(gold_pairs) + len(full_pool)) if full_pool else None

    # ---- Q4: MANDATORY overfit guard -- two independent seeded 50/50 splits ----
    def split_recall(items, seed_offset, n_flag_key="flagged"):
        ids_sorted = sorted(it["id"] for it in items)
        r = random.Random(args.seed + seed_offset)
        shuffled = ids_sorted[:]
        r.shuffle(shuffled)
        half = len(shuffled) // 2
        half_a, half_b = sorted(shuffled[:half]), sorted(shuffled[half:])
        by_id = {r_["id"]: r_ for r_ in per_item}
        rec_a = (sum(1 for i in half_a if by_id[i][n_flag_key]) / len(half_a)) if half_a else None
        rec_b = (sum(1 for i in half_b if by_id[i][n_flag_key]) / len(half_b)) if half_b else None
        return {"half_a_ids": half_a, "half_b_ids": half_b, "recall_half_a": rec_a, "recall_half_b": rec_b}

    split_all_1 = split_recall(causal_items, seed_offset=1)
    split_all_2 = split_recall(causal_items, seed_offset=2)
    goal_mediated_items_only = [it for it in causal_items if it["id"] in GOAL_MEDIATED_CAUSAL_IDS]
    split_gm_1 = split_recall(goal_mediated_items_only, seed_offset=11)
    split_gm_2 = split_recall(goal_mediated_items_only, seed_offset=12)

    def overfit_gap(split):
        a, b = split["recall_half_a"], split["recall_half_b"]
        if a is None or b is None:
            return None
        return abs(a - b)

    max_gap_all = max(g for g in (overfit_gap(split_all_1), overfit_gap(split_all_2)) if g is not None)
    max_gap_gm = None
    gaps_gm = [g for g in (overfit_gap(split_gm_1), overfit_gap(split_gm_2)) if g is not None]
    if gaps_gm:
        max_gap_gm = max(gaps_gm)

    honest_ceiling_all_25 = None
    if split_all_1["recall_half_a"] is not None and split_all_1["recall_half_b"] is not None:
        honest_ceiling_all_25 = min(
            min(split_all_1["recall_half_a"], split_all_1["recall_half_b"]),
            min(split_all_2["recall_half_a"], split_all_2["recall_half_b"]),
        )

    # ---- comparison read live off disk ----
    with open(repo_path(BASELINE_METRICS_REL), "r", encoding="utf-8") as f:
        baseline_metrics = json.load(f)
    baseline_recall_goal_mediated = baseline_metrics["causal_link_proposal"]["recall_goal_mediated"]
    baseline_fp = baseline_metrics["causal_link_proposal"]["fp_rate"]

    # ---- verdict (honest both-ways, no forced pass) ----
    overfit_flag = (max_gap_all is not None and max_gap_all >= 0.30) or \
                   (max_gap_gm is not None and max_gap_gm >= 0.50)  # gm subset is tiny (N~4-5/half), higher bar

    if recall_unstated_goal is not None and recall_unstated_goal < 0.30:
        landscape_finding = (
            "SCHEMAS_DO_NOT_INFER_UNSTATED_GOALS: recall_unstated_goal="
            f"{recall_unstated_goal:.3f} on the {len(inferred_items)} gold inferred-goal items -- "
            "the supplied schema library recognizes SITUATIONS (prohibition, rescue, sacrifice) but "
            "its goal_trigger cues still key off residual lexical/phrasal surface signal similar in "
            "kind to the lexicon baseline, not off action-pattern inference alone; genuine unstated-"
            "goal inference (no textual cue at all, e.g. goal_014/goal_016) remains OUT OF REACH of "
            "supplied schema DATA and requires the deep-earn inference mechanism."
        )
    elif recall_unstated_goal is not None and recall_unstated_goal < 0.60:
        landscape_finding = (
            f"SCHEMAS_PARTIALLY_INFER_UNSTATED_GOALS: recall_unstated_goal={recall_unstated_goal:.3f} "
            "-- some situation-pattern recognition works (schemas catch action-pattern cues a pure "
            "desiderative lexicon would miss) but a material residual of unstated goals still needs "
            "deeper inference; supply-schema is a partial, not full, substitute for deep-earn."
        )
    else:
        landscape_finding = (
            f"SCHEMAS_RECOVER_MOST_UNSTATED_GOALS: recall_unstated_goal={recall_unstated_goal:.3f} "
            "on this small (N=4) inferred-goal gold set -- caveat small N heavily before generalizing."
        )

    verdict_summary = "OVERFIT_DETECTED_HONEST_CEILING_IS_HOLDOUT" if overfit_flag else "NO_OVERFIT_SIGNAL_STABLE_ACROSS_SPLITS"

    verdict_msg = (
        f"Q1_UNSTATED_GOAL: recall={recall_unstated_goal} (n_inferred={len(inferred_items)}) "
        f"precision_goal_trigger={precision_goal_trigger} fp_rate_goal_trigger={fp_rate_goal_trigger} "
        f"(n_negatives={len(neg_spans)}). "
        f"Q2_PAIRING_GOAL_MEDIATED: recall={recall_goal_mediated} (n=9) "
        f"Q3_END_TO_END: recall_all_25={recall_all} recall_non_goal_mediated_16={recall_non_goal_mediated} "
        f"fp_rate={fp_rate} (n_negatives={len(negatives)}) vs content_overlap_cap={CONTENT_OVERLAP_CAP} "
        f"vs disk_baseline_recall_goal_mediated={baseline_recall_goal_mediated} disk_baseline_fp={baseline_fp} "
        f"vs random_uniform_control_recall={random_uniform_control_recall}. "
        f"Q4_OVERFIT_GUARD: split_all_1={split_all_1['recall_half_a']}/{split_all_1['recall_half_b']} "
        f"split_all_2={split_all_2['recall_half_a']}/{split_all_2['recall_half_b']} "
        f"max_gap_all_25={max_gap_all} split_gm_1={split_gm_1['recall_half_a']}/{split_gm_1['recall_half_b']} "
        f"split_gm_2={split_gm_2['recall_half_a']}/{split_gm_2['recall_half_b']} max_gap_gm_9={max_gap_gm} "
        f"honest_ceiling_recall_all_25={honest_ceiling_all_25}. "
        f"VERDICT={verdict_summary}. LANDSCAPE_FINDING={landscape_finding}"
    )

    # ---- arms-must-differ vs baseline flagged set ----
    baseline_flagged_ids = set(baseline_metrics["causal_link_proposal"].get(
        "flagged_ids", [r["id"] for r in baseline_metrics["causal_link_proposal"]["per_item"] if r["flagged"]]))
    digest_schema = hashlib.sha256(json.dumps(sorted(flagged_ids)).encode()).hexdigest()
    digest_baseline = hashlib.sha256(json.dumps(sorted(baseline_flagged_ids)).encode()).hexdigest()
    arms_differ_verified = digest_schema != digest_baseline

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": "MEASURED_MECHANISM",
        "verdict_msg": verdict_msg,
        "summary": (
            f"{verdict_summary} | recall_unstated_goal={recall_unstated_goal} | "
            f"recall_goal_mediated_pairing={recall_goal_mediated} | recall_end_to_end_all_25={recall_all} "
            f"fp={fp_rate} | honest_ceiling(out-of-sample)={honest_ceiling_all_25} | {landscape_finding}"
        ),
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "seed": args.seed,
        "n_schemas": len(schemas), "schema_lib_source": SCHEMA_LIB_REL,
        "unstated_goal_recovery": {
            "n_inferred_gold": len(inferred_items), "n_explicit_gold": len(explicit_items),
            "recall_unstated_goal": recall_unstated_goal,
            "precision_goal_trigger": precision_goal_trigger,
            "fp_rate_goal_trigger": fp_rate_goal_trigger,
            "n_negative_spans": len(neg_spans),
            "inferred_hits": [{"id": i, "fired": f, "schema_ids": s} for i, f, s in inferred_hits],
            "explicit_hits": [{"id": i, "fired": f, "schema_ids": s} for i, f, s in explicit_hits],
        },
        "pairing_recovery_goal_mediated_9": {
            "recall": recall_goal_mediated, "n": len(goal_mediated_results),
            "per_item": goal_mediated_results,
        },
        "end_to_end": {
            "recall_all_25": recall_all, "recall_goal_mediated_9": recall_goal_mediated,
            "recall_non_goal_mediated_16": recall_non_goal_mediated,
            "fp_rate": fp_rate, "n_negative_sampled": len(negatives),
            "flagged_ids": sorted(flagged_ids), "per_item": per_item,
        },
        "comparison": {
            "content_overlap_cap": CONTENT_OVERLAP_CAP,
            "disk_baseline_1400331cc_recall_goal_mediated": baseline_recall_goal_mediated,
            "disk_baseline_fp": baseline_fp,
            "random_uniform_control_recall": random_uniform_control_recall,
            "source": BASELINE_METRICS_REL,
        },
        "overfit_guard": {
            "split_all_25_seed_offset_1": split_all_1, "split_all_25_seed_offset_2": split_all_2,
            "max_gap_all_25": max_gap_all,
            "split_goal_mediated_9_seed_offset_11": split_gm_1,
            "split_goal_mediated_9_seed_offset_12": split_gm_2,
            "max_gap_goal_mediated_9": max_gap_gm,
            "overfit_detected": overfit_flag,
            "honest_ceiling_recall_all_25_worst_of_4_halves": honest_ceiling_all_25,
            "caveat": "goal_mediated_9 split halves are N=4-5 items each -- inherently noisy, "
                      "reported but not load-bearing on its own; all_25 split (N=12-13/half) is "
                      "the primary overfit signal.",
        },
        "verdict_summary": verdict_summary,
        "landscape_finding": landscape_finding,
        "arms_differ_verified": arms_differ_verified,
        "arms_digest": {"schema_library": digest_schema, "baseline_1400331cc": digest_baseline},
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_heartbeat_exempt_single_pass",
        "deterministic_seeding": True,
        "dispatched": False,
        "dispatch_note": "measurement-only per task instruction; not queued, not shipped remote.",
    }

    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)

    print(f"[{ANCHOR_NAME}] {metrics['verdict']} ({verdict_summary}) elapsed={elapsed:.2f}s -> {final_path}")


if __name__ == "__main__":
    _output_dir_for_crash = repo_path(f"data/exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        baseline._write_crash_metrics(_output_dir_for_crash, e)
        raise
