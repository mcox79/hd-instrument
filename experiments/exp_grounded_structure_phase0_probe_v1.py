# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor: n/a (fixed 4/12-item discriminator, no capacity sweep)
# - calibration_check: default_ok_for_this_regime (feature-match weights fixed +1/-1/0,
#   declared before running, not tuned post-hoc)
# - cell_chunked: false (single-shot, n=12, seconds); heartbeat_present: false (exempt,
#   elapsed_s << 1800s threshold)
# - all numbers MEASURED@ tagged in the completion report, not this file
#
# PHASE-0 GROUNDING-PREMISE PROBE. See
# preregs/2026-08-03_grounded_structure_phase0_probe_v1.md for the full pre-reg including the
# two post-review fairness/brain-foundational gates. ONE QUESTION: does a grounded, appraisal-
# theory-structured representation (TARGET=ToM self/other, VALENCE=harm/help tendency,
# PRIOR_BLOCK=causal-attribution) disambiguate REVENGE_PUNISH/SELF_DISCIPLINE/CARE_FOR_OTHERS/
# PROTECT_OTHERS better than the strongest prior text-only method, on real McGuffey-adjacent
# public-domain narrative text (Little Women / Wizard of Oz / Alice in Wonderland)?
#
# FAIRNESS: VALENCE and TARGET are BLIND, FIXED, UNIFORM functions applied identically to all
# 12 items (reused verbatim from experiments/exp_situated_goal_structure_valence_v1.py, built
# prior to and disjoint from these category labels -- no per-item tuning). PRIOR_BLOCK has two
# variants: AUTO_BLIND (derived from corpus structure only, no entity-linking, expected
# coarse/noisy) and ORACLE_NARRATIVE (explicitly declared an ORACLE CEILING, sourced from one
# independently-checkable textual fact, not from the category label). A SCRAMBLED-VALENCE
# negative control (verb table classes swapped) must collapse the lift for the result to be
# non-contaminated.
#
# BRAIN-FOUNDATIONAL: the composition is framed as a Lazarus/Scherer-CPM appraisal computation
# (TARGET=ToM, VALENCE=goal-congruence, PRIOR_BLOCK=causal-attribution), not an ad-hoc
# decision tree. Every failure is classified BRAIN_LIKE_MISS (irony-fooled /
# patient-vs-beneficiary confusion -- expected, honest) vs ARCHITECTURE_ARTIFACT (the feature
# set structurally cannot distinguish two candidates -- a real shape-gap).
"""Phase-0 grounding-premise probe: blind appraisal-structured classifier vs strongest prior
text-only method, with a scrambled-valence contamination control and a per-item brain-fidelity
audit of failures. DIAGNOSTIC CEILING -- hand-built fixed rule + fixed valence table, NOT the
earned mechanism."""
import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "grounded_structure_phase0_probe_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
if EXPERIMENTS_DIR not in sys.path:
    sys.path.insert(0, EXPERIMENTS_DIR)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import exp_construction_integration_relation_inference_v1 as ci  # noqa: E402 (parent cell, reused verbatim)
import exp_situated_goal_structure_valence_v1 as sgv  # noqa: E402 (target resolver + valence lexicon, reused verbatim)

CONFUSED_ITEM_IDS = [
    "relinf_unstated_007",
    "relinf_unstated_010",
    "relinf_unstated_011",
    "relinf_unstated_012",
]

# Reference (cited, not recomputed): prior SITUATED_STRUCTURE arm (auto-lexicon valence, NO
# prior-block/causal-attribution feature) confused_4 accuracy.
PRIOR_SITUATED_STRUCTURE_CONFUSED4_REF = 0.5  # MEASURED@d:/AI/hd-instrument/data/exp_situated_goal_structure_valence_v1/metrics.json:metrics_by_scope.confused_4.SITUATED_STRUCTURE_accuracy

# Appraisal-structure table (Lazarus/Scherer-CPM framing, see pre-reg "APPRAISAL-THEORY
# FRAMING"): category -> (TARGET [ToM], VALENCE [goal-congruence], PRIOR_BLOCK [causal-
# attribution]). Extends sgv.CATEGORY_TARGET_VALENCE with the causal-attribution dimension.
# FIXED, declared BEFORE scoring -- not reverse-engineered to fit the 4 confused items.
CATEGORY_STRUCTURE = {}
for _cat, (_t, _v) in sgv.CATEGORY_TARGET_VALENCE.items():
    if _cat == "REVENGE_PUNISH":
        CATEGORY_STRUCTURE[_cat] = (_t, _v, True)
    elif _cat in ("CARE_FOR_OTHERS", "PROTECT_OTHERS"):
        CATEGORY_STRUCTURE[_cat] = (_t, _v, False)
    elif _cat == "SELF_DISCIPLINE":
        CATEGORY_STRUCTURE[_cat] = (_t, _v, None)  # prior-block N/A for self-targeted acts
    else:
        CATEGORY_STRUCTURE[_cat] = (_t, _v, None)

# ORACLE_NARRATIVE prior-block source: relinf_unstated_008 (SAME gold file, little_women ch8,
# line_range [3149,3150], strictly earlier than relinf_unstated_007's [3278,3278]) narrates
# Amy's defiant confession of burning Jo's manuscript -- an independently-checkable textual
# fact, NOT derived from any "this-is-revenge" category flag. All other items: no oracle claim
# (default False). Declared an ORACLE CEILING per the fairness gate, not today's automatic
# capability.
ORACLE_PRIOR_BLOCK = {
    "relinf_unstated_007": True,
}


# ---------------------------------------------------------------------------
# Start marker / crash diagnostic (META Sec 13B/13C)
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# ---------------------------------------------------------------------------
# BLIND feature resolvers
# ---------------------------------------------------------------------------
def resolve_valence_blind(action_text: str, scrambled: bool = False) -> str:
    """FIXED, UNIFORM verb/word valence table, reused verbatim from sgv (built prior to and
    disjoint from these category labels). scrambled=True swaps the two word classes wholesale
    (negative control -- must collapse the grounded arm's lift if the lift is real)."""
    toks = ci.tokenize(action_text)
    harm_set = sgv.HELP_WORDS if scrambled else sgv.HARM_WORDS
    help_set = sgv.HARM_WORDS if scrambled else sgv.HELP_WORDS
    harm = sum(1 for t in toks if t in harm_set)
    help_ = sum(1 for t in toks if t in help_set)
    if harm > help_:
        return "HARM"
    if help_ > harm:
        return "HELP"
    return "NA"


def resolve_prior_block_auto_blind(item, all_items) -> bool:
    """Corpus-structure-only derivation, NO entity-linking, NO category label used: True iff
    an earlier item in the same novel+chapter (strictly earlier line_range) has blind
    valence=HARM and blind target=OTHER. Coarse proxy -- expected to misfire when two distinct
    antagonist dynamics share a chapter (reported honestly, not hidden)."""
    novel, chapter = item["novel"], item["chapter"]
    line_start = item["line_range"][0]
    for other in all_items:
        if other["id"] == item["id"]:
            continue
        if other.get("novel") != novel or other.get("chapter") != chapter:
            continue
        if other["line_range"][0] >= line_start:
            continue
        if (resolve_valence_blind(other["action_text"]) == "HARM"
                and sgv.resolve_target(other["action_text"]) == "OTHER"):
            return True
    return False


def resolve_prior_block_oracle(item_id: str) -> bool:
    return ORACLE_PRIOR_BLOCK.get(item_id, False)


def _feat_score(pred, gold):
    if pred in (None, "NA") or gold in (None, "NA"):
        return 0.0
    return 1.0 if pred == gold else -1.0


def classify_grounded(item, pred_target, pred_valence, pred_prior_block):
    """FIXED appraisal-composition rule (Lazarus/Scherer-CPM framing): argmax feature-match
    score over the item's candidates; ties broken by cosine (declared, not hidden)."""
    correct = item["correct_category"]
    cands = [correct] + list(item["distractor_categories"])
    scores = {}
    for c in cands:
        ct, cv, cp = CATEGORY_STRUCTURE[c]
        scores[c] = (_feat_score(pred_target, ct) + _feat_score(pred_valence, cv)
                     + _feat_score(pred_prior_block, cp))
    best = max(scores.values())
    tied = [c for c in cands if scores[c] == best]
    tie_broken = len(tied) > 1
    if tie_broken:
        action_vec = ci.text_bundle(item["action_text"])
        cos = {c: ci.cos_sim(action_vec, ci.bundle(ci.CATEGORY_PROTOTYPES[c])) for c in tied}
        pick = max(tied, key=lambda c: cos[c])
    else:
        pick = tied[0]
    return pick, scores, tie_broken


# ---------------------------------------------------------------------------
# Brain-fidelity classification of failures
# ---------------------------------------------------------------------------
IRONY_FOOLED_IDS = {"relinf_unstated_007"}          # "take care of herself" -- spiteful non-help read as help
BENEFICIARY_PATIENT_IDS = {"relinf_unstated_011"}   # slap-the-Lion -- patient (Lion) harmed, beneficiary (Toto) protected
CARE_PROTECT_COLLISION_CATS = {"CARE_FOR_OTHERS", "PROTECT_OTHERS"}


def brain_fidelity_class(item_id, correct, pick, tied_cats):
    """Classify a miss as BRAIN_LIKE_MISS (plausible human appraisal error) vs
    ARCHITECTURE_ARTIFACT (feature set cannot represent the needed distinction)."""
    if pick == correct:
        return "CORRECT"
    if {correct, pick} <= CARE_PROTECT_COLLISION_CATS or (
            tied_cats and CARE_PROTECT_COLLISION_CATS.issuperset(set(tied_cats) & CARE_PROTECT_COLLISION_CATS)
            and correct in CARE_PROTECT_COLLISION_CATS and pick in CARE_PROTECT_COLLISION_CATS):
        return "ARCHITECTURE_ARTIFACT_CARE_PROTECT_COLLISION"
    if item_id in IRONY_FOOLED_IDS:
        return "BRAIN_LIKE_MISS_IRONY_FOOLED"
    if item_id in BENEFICIARY_PATIENT_IDS:
        return "BRAIN_LIKE_MISS_PATIENT_VS_BENEFICIARY"
    return "OTHER_MISS_UNCLASSIFIED"


# ---------------------------------------------------------------------------
# Per-item scoring across all arms
# ---------------------------------------------------------------------------
def score_item(item, all_items, rng):
    correct = item["correct_category"]
    action_text = item["action_text"]

    pred_target = sgv.resolve_target(action_text)
    pred_valence = resolve_valence_blind(action_text, scrambled=False)
    pred_valence_scrambled = resolve_valence_blind(action_text, scrambled=True)
    pred_prior_auto = resolve_prior_block_auto_blind(item, all_items)
    pred_prior_oracle = resolve_prior_block_oracle(item["id"])

    pick_auto_blind, scores_auto, tie_auto = classify_grounded(item, pred_target, pred_valence, pred_prior_auto)
    pick_oracle, scores_oracle, tie_oracle = classify_grounded(item, pred_target, pred_valence, pred_prior_oracle)
    pick_oracle_scrambled, scores_scr, tie_scr = classify_grounded(
        item, pred_target, pred_valence_scrambled, pred_prior_oracle)

    # TEXT_ONLY_LEXICAL + RANDOM reused verbatim from the parent cell (no structure at all)
    bc = ci.score_goal_item(item, rng)
    lex_pick = bc["lex_pick"]
    rand_pick = bc["rand_pick"]

    gold_target, gold_valence = sgv.CATEGORY_TARGET_VALENCE[correct]
    gold_prior_block = CATEGORY_STRUCTURE[correct][2]

    return {
        "id": item["id"], "correct_category": correct, "action_text": action_text,
        "gold_target": gold_target, "gold_valence": gold_valence, "gold_prior_block": gold_prior_block,
        "pred_target": pred_target, "pred_valence": pred_valence,
        "pred_prior_block_auto_blind": pred_prior_auto, "pred_prior_block_oracle": pred_prior_oracle,
        "target_matches_gold": pred_target == gold_target,
        "valence_matches_gold": (gold_valence == "NA") or (pred_valence == gold_valence),
        "GROUNDED_AUTO_BLIND_pick": pick_auto_blind, "GROUNDED_AUTO_BLIND_correct": pick_auto_blind == correct,
        "GROUNDED_ORACLE_NARRATIVE_pick": pick_oracle, "GROUNDED_ORACLE_NARRATIVE_correct": pick_oracle == correct,
        "GROUNDED_ORACLE_SCRAMBLED_VALENCE_pick": pick_oracle_scrambled,
        "GROUNDED_ORACLE_SCRAMBLED_VALENCE_correct": pick_oracle_scrambled == correct,
        "TEXT_ONLY_LEXICAL_pick": lex_pick, "TEXT_ONLY_LEXICAL_correct": lex_pick == correct,
        "RANDOM_pick": rand_pick, "RANDOM_correct": rand_pick == correct,
        "brain_fidelity_auto_blind": brain_fidelity_class(item["id"], correct, pick_auto_blind, None),
        "brain_fidelity_oracle": brain_fidelity_class(item["id"], correct, pick_oracle, None),
        "solved_by": ("BLIND" if pick_auto_blind == correct else
                      ("ORACLE_ONLY" if pick_oracle == correct else "UNSOLVED")),
        "prediction_vector": [pick_auto_blind, pick_oracle, pick_oracle_scrambled, lex_pick, rand_pick],
    }


ARM_NAMES = ["GROUNDED_AUTO_BLIND", "GROUNDED_ORACLE_NARRATIVE", "GROUNDED_ORACLE_SCRAMBLED_VALENCE",
             "TEXT_ONLY_LEXICAL", "RANDOM"]


def arms_must_differ(results):
    """META_RULE_AF: assert the 5 arms are not bit-identical across the full 12-item run."""
    vecs = {name: [] for name in ARM_NAMES}
    for r in results:
        for i, name in enumerate(ARM_NAMES):
            vecs[name].append(r["prediction_vector"][i])
    digests = {name: hashlib.sha256("|".join(seq).encode()).hexdigest() for name, seq in vecs.items()}
    for i, a in enumerate(ARM_NAMES):
        for b in ARM_NAMES[i + 1:]:
            if digests[a] == digests[b]:
                raise AssertionError(
                    f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical (hash={digests[a]})"
                )
    return digests


def _agg(results, key, ids=None):
    subset = [r for r in results if ids is None or r["id"] in ids]
    n = len(subset)
    return (sum(1 for r in subset if r[key]) / n) if n else 0.0, n


def run(run_mode: str):
    t0 = time.perf_counter()
    gold = ci.load_gold()
    all_goal_items = gold["unstated_goal"]
    expected_n_units = len(all_goal_items) * len(ARM_NAMES)
    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, run_mode, expected_n_units)

    rng = __import__("random").Random(ci.FIXED_RANDOM_SEED)
    results = [score_item(it, all_goal_items, rng) for it in all_goal_items]

    if len(results) * len(ARM_NAMES) != expected_n_units:
        raise AssertionError(f"META_RULE_H CARDINALITY BREACH: got {len(results)*len(ARM_NAMES)}, expected {expected_n_units}")

    arm_digests = arms_must_differ(results)

    confused_ids = set(CONFUSED_ITEM_IDS)
    metrics_by_scope = {}
    for scope_name, ids in [("confused_4", confused_ids), ("full_12", None)]:
        scope = {"n": _agg(results, "GROUNDED_AUTO_BLIND_correct", ids)[1]}
        for arm in ARM_NAMES:
            acc, _ = _agg(results, f"{arm}_correct", ids)
            scope[f"{arm}_accuracy"] = acc
        metrics_by_scope[scope_name] = scope

    lex_c4 = metrics_by_scope["confused_4"]["TEXT_ONLY_LEXICAL_accuracy"]
    strongest_text_only_c4 = max(lex_c4, PRIOR_SITUATED_STRUCTURE_CONFUSED4_REF)
    oracle_c4 = metrics_by_scope["confused_4"]["GROUNDED_ORACLE_NARRATIVE_accuracy"]
    auto_c4 = metrics_by_scope["confused_4"]["GROUNDED_AUTO_BLIND_accuracy"]
    scrambled_c4 = metrics_by_scope["confused_4"]["GROUNDED_ORACLE_SCRAMBLED_VALENCE_accuracy"]

    scramble_collapsed = scrambled_c4 <= strongest_text_only_c4 + 0.25  # <=1-item tolerance
    oracle_pays = (oracle_c4 >= 0.75) and ((oracle_c4 - strongest_text_only_c4) >= 0.25)
    auto_pays_today = (auto_c4 >= 0.75) and ((auto_c4 - strongest_text_only_c4) >= 0.25)

    both_gates_hold = scramble_collapsed  # fairness gate; brain-foundational gate is structural
    # (appraisal framing) and verified by construction + the brain_fidelity per-item audit below,
    # not a numeric threshold -- reported, not gated on a number.

    if not scramble_collapsed:
        verdict = "CONTAMINATED_INCONCLUSIVE"
    elif oracle_pays and auto_pays_today:
        verdict = "PREMISE_PAYS_TODAY"
    elif oracle_pays:
        verdict = "PREMISE_PAYS_ORACLE_ONLY"
    else:
        verdict = "PREMISE_WEAK"

    confused_results = [r for r in results if r["id"] in confused_ids]
    per_item_ablation = [
        {k: r[k] for k in (
            "id", "correct_category", "gold_target", "gold_valence", "gold_prior_block",
            "pred_target", "pred_valence", "pred_prior_block_auto_blind", "pred_prior_block_oracle",
            "GROUNDED_AUTO_BLIND_pick", "GROUNDED_AUTO_BLIND_correct",
            "GROUNDED_ORACLE_NARRATIVE_pick", "GROUNDED_ORACLE_NARRATIVE_correct",
            "GROUNDED_ORACLE_SCRAMBLED_VALENCE_pick", "GROUNDED_ORACLE_SCRAMBLED_VALENCE_correct",
            "TEXT_ONLY_LEXICAL_pick", "TEXT_ONLY_LEXICAL_correct", "RANDOM_pick", "RANDOM_correct",
            "brain_fidelity_auto_blind", "brain_fidelity_oracle", "solved_by",
        )}
        for r in confused_results
    ]

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict}: confused_4 AUTO_BLIND={auto_c4:.3f} ORACLE_NARRATIVE={oracle_c4:.3f} "
            f"SCRAMBLED_control={scrambled_c4:.3f} strongest_text_only={strongest_text_only_c4:.3f} "
            f"(lexical={lex_c4:.3f}, prior_situated_structure={PRIOR_SITUATED_STRUCTURE_CONFUSED4_REF:.3f}) "
            f"scramble_collapsed={scramble_collapsed}"
        ),
        "summary": f"{verdict} on n=4 confused subset; fairness+brain-foundational gates reported",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "measured_n_units": len(results) * len(ARM_NAMES),
        "cardinality_ok": True, "arms_differ_verified": True, "arm_digests": arm_digests,
        "metrics_by_scope": metrics_by_scope,
        "gates": {
            "fairness_scramble_collapsed": scramble_collapsed,
            "oracle_pays": oracle_pays, "auto_pays_today": auto_pays_today,
            "strongest_text_only_confused4": strongest_text_only_c4,
        },
        "valence_table_harm_words": sorted(sgv.HARM_WORDS),
        "valence_table_help_words": sorted(sgv.HELP_WORDS),
        "oracle_prior_block_declared": ORACLE_PRIOR_BLOCK,
        "category_structure_appraisal_table": {k: list(v) for k, v in CATEGORY_STRUCTURE.items()},
        "per_item_ablation_confused_4": per_item_ablation,
        "note_appraisal_framing": (
            "Composition = Lazarus/Scherer-CPM appraisal (TARGET=ToM, VALENCE=goal-congruence, "
            "PRIOR_BLOCK=causal-attribution); goal-relevance held constant (all items goal-directed "
            "by construction), coping-potential out of scope for this cheap pass."
        ),
        "note_supply_vs_earn": (
            "VALENCE table and classification RULE are SUPPLIED (fixed, hand-built) -- a diagnostic "
            "ceiling, NOT brain-faithful earning. What is tested is the STRUCTURE/HYPOTHESIS (appraisal "
            "composition over target+valence+causal-attribution is the right shape), not the earning."
        ),
        "note_oracle_declaration": (
            "GROUNDED_ORACLE_NARRATIVE's prior_block for relinf_unstated_007 is an explicitly declared "
            "ORACLE CEILING (sourced from relinf_unstated_008's action_text, same gold file, earlier "
            "line_range -- an independent textual fact, not the category label). NOT claimed as today's "
            "automatic capability; GROUNDED_AUTO_BLIND is the fully-automatic variant."
        ),
        "note_scramble_control": (
            "GROUNDED_ORACLE_SCRAMBLED_VALENCE swaps the HARM_WORDS/HELP_WORDS classes wholesale "
            "(fixed permutation, still category-blind) as a contamination check; its lift over "
            "strongest-text-only MUST collapse for the result to be non-contaminated."
        ),
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)
    return metrics


def self_test():
    gold = ci.load_gold()
    items = gold["unstated_goal"]
    assert len(items) >= 4
    by_id = {it["id"]: it for it in items}
    for cid in CONFUSED_ITEM_IDS:
        assert cid in by_id, f"confused item {cid} not found in gold"

    # blind valence sanity (fixed table, category-blind)
    assert resolve_valence_blind("he rescued the kitten and held it softly to comfort it") == "HELP"
    assert resolve_valence_blind("she punished him out of spite and cruel revenge") == "HARM"
    # scramble actually flips the classification for a clearly-signed sentence
    assert resolve_valence_blind("she punished him out of spite and cruel revenge", scrambled=True) != "HARM"

    # oracle prior-block source is a real earlier item in the same gold file
    src = by_id["relinf_unstated_008"]
    assert src["line_range"][0] < by_id["relinf_unstated_007"]["line_range"][0]
    assert src["novel"] == by_id["relinf_unstated_007"]["novel"] == "little_women"
    assert src["chapter"] == by_id["relinf_unstated_007"]["chapter"] == 8

    rng = __import__("random").Random(ci.FIXED_RANDOM_SEED)
    r = score_item(by_id["relinf_unstated_012"], items, rng)
    assert r["GROUNDED_AUTO_BLIND_pick"] in ([r["correct_category"]] + list(by_id["relinf_unstated_012"]["distractor_categories"]))
    assert r["GROUNDED_ORACLE_NARRATIVE_pick"] in ([r["correct_category"]] + list(by_id["relinf_unstated_012"]["distractor_categories"]))

    # CATEGORY_STRUCTURE cardinality: every category referenced by any item's candidates is present
    all_cats = set()
    for it in items:
        all_cats.add(it["correct_category"])
        all_cats.update(it["distractor_categories"])
    missing = all_cats - set(CATEGORY_STRUCTURE.keys())
    assert not missing, f"CATEGORY_STRUCTURE missing categories: {missing}"

    print("[self-test] PASS", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run-mode", default="full", choices=["full", "smoke", "self_test"])
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    metrics = run(args.run_mode)
    print(f"[done] verdict={metrics['verdict']} elapsed_s={metrics['elapsed_s']:.3f}", flush=True)
    print(json.dumps(metrics["metrics_by_scope"], indent=2), flush=True)
    print(json.dumps(metrics["gates"], indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
