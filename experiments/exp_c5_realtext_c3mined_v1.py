"""exp_c5_realtext_c3mined_v1 -- THE FIRST real-text Component-5 test: does directed_goal_outcome_
score (exp_component5_gold_role_isolated_v1, reused bit-identical) bind the outcome to the true
goal-owner over recency, on DIVERSE REAL LITBANK PROSE (not the authored x23 template)?

Owner-gold source: experiments/data/goal_outcome_c3mined_v1.jsonl (C3-syntax mining,
mine_goal_outcome_litbank_c3syntax_v1.py), FILTERED to the AGENT-VERIFIED owner-correct subset
(15/40 items; agent read every mined item's goal_sentence + surrounding text and judged whether the
C3-syntax-resolved goal_owner is the TRUE referent -- per task contract "do NOT run C5 on items
whose C3-owner-gold is wrong"). The 15 ids are hardcoded below (VERIFIED_CORRECT_IDS), each with a
one-line verification note.

Reuses bit-identical: GeneralRecencyEntityResolver, ContentMatchResolver, build_positions,
directed_goal_outcome_score, decide_keep_or_revert, ABSTAIN_BAND_DEFAULT, DEFAULT_ROSTER, GO_ROLES,
R_GOAL/R_UNMET/R_MET (all from exp_component5_gold_role_isolated_v1.py, 2026-08-04/05 landed cell).
No new mechanism code -- this cell is pure harness wiring real-mined items into the existing C5
pipeline, per task brief ("RUN C5 selection end-to-end on them").
"""
from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from exp_component5_gold_role_isolated_v1 import (  # noqa: E402
    GeneralRecencyEntityResolver, ContentMatchResolver, build_positions,
    directed_goal_outcome_score, DEFAULT_ROSTER, R_GOAL, R_UNMET, R_MET,
)
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402

MINED_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_outcome_c3mined_v1.jsonl")
OUTPUT_PATH = os.path.join(REPO_ROOT, "data", "exp_c5_realtext_c3mined_v1", "metrics.json")

# AGENT-VERIFIED owner-correct subset (agent read all 40 mined items' goal_sentence in context;
# owner-acc = 15/40 = 0.375, see completion report). Each id -> True (owner correct) with the
# syntactic construction verified: control/xcomp subject-sharing, relative-clause gapped subject,
# or coordinated-clause same-clause subject -- all cases the arc-parser's core_dep/coord rule
# correctly licensed AND the resolved token is the real referent (not a roster-corrupted
# pseudo-name like "Her"/"His"/"Mistress"/"King" -- see report for that failure-mode diagnosis).
VERIFIED_CORRECT_IDS = {
    "c3_238_dear_enemy__s35": "Judy would like to see her (subject-control, PROPN Judy)",
    "c3_113_the_secret_garden__s32": "Mary heard her say (core_dep subject, PROPN Mary)",
    "c3_95_the_prisoner_of_zenda__s7": "brother Robert...not to mind (control chain, PROPN Robert)",
    "c3_9830_the_beautiful_and_damned__s99": "Anthony went to see (control, PROPN Anthony)",
    "c3_541_the_age_of_innocence__s23": "Newland Archer saw (core_dep, PROPN Archer)",
    "c3_351_of_human_bondage__s80": "William is waiting...to see (control, PROPN William)",
    "c3_74_the_adventures_of_tom_sawyer__s44": "Tom knew (core_dep, PROPN Tom)",
    "c3_502_desert_gold__s83": "Cameron had not cared to know (control, PROPN Cameron)",
    "c3_514_little_women__s14": "Mother didn't say...she won't wish (same-sent coref, she=Mother)",
    "c3_4217_a_portrait_of_the_artist_as_a_young_man__s89": "Father Arnall knew (core_dep, title+name)",
    "c3_208_daisy_miller_a_study__s53": "Winterbourne wondered (core_dep, PROPN Winterbourne)",
    "c3_472_the_house_behind_the_cedars__s22": "Warwick saw (core_dep, PROPN Warwick)",
    "c3_1342_pride_and_prejudice__s30": "Bingley will be glad to see (control, PROPN Bingley)",
    "c3_502_desert_gold__s24": "Cameron saw (core_dep, PROPN Cameron)",
    "c3_45_anne_of_green_gables__s18": "Rachel knew (core_dep, PROPN Rachel)",
}

# Minimal, mechanical gender patch for names that appear in these 15 items but that
# hdlab.state_of_mind.infer_nominal_gender cannot classify (uncommon proper names with no
# title/kinship cue) -- WITHOUT this, GeneralRecencyEntityResolver/ContentMatchResolver silently
# fail to match a pronoun to its antecedent (gender=None never satisfies a gendered want), which
# would measure a ROSTER-COVERAGE gap, not the C5 selection mechanism. Declared honestly (not
# hidden): every name here is gender-obvious from the item's own text (a title, an explicit
# pronoun co-reference in the same item, or common-name convention), not invented.
GENDER_PATCH = {
    "judy": "f", "jane": "f", "mary": "f", "robert": "m", "anthony": "m", "archer": "m",
    "newland": "m", "william": "m", "watkin": "f", "tom": "m", "polly": "f", "cameron": "m",
    "mother": "f", "jo": "f", "father": "m", "dante": "f", "winterbourne": "m", "warwick": "m",
    "bingley": "m", "bennet": "m", "rachel": "f", "cuthbert": "m", "peter": "m",
}


def _load_mined():
    items = []
    with open(MINED_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def _build_c5_item(mined):
    roster = dict(DEFAULT_ROSTER)
    roster.update({k: v for k, v in mined.get("roster", {}).items() if v})
    for name in [mined["goal_owner"]] + ([mined["foil"]] if mined.get("foil") else []):
        low = name.lower()
        if low in GENDER_PATCH:
            roster[low] = GENDER_PATCH[low]
    return dict(
        id=mined["id"], text=mined["text"], owner=mined["goal_owner"].lower(),
        gold_outcome_owner=mined["goal_owner"].lower(), foil=(mined["foil"].lower() if mined.get("foil") else None),
        roster=roster,
    )


def run_item(item):
    """Mirrors exp_component5_gold_role_isolated_v1.run_recency_item, but item-roster-driven
    (real names, not the toy 12-name cast) -- reuses build_positions/ContentMatchResolver/
    GeneralRecencyEntityResolver/directed_goal_outcome_score/decide_keep_or_revert bit-identical."""
    roster = item["roster"]
    rs_b, cid_b, es_b = build_positions(item, GeneralRecencyEntityResolver(roster))
    rs_c, cid_c, es_c = build_positions(item, ContentMatchResolver(roster))
    if rs_b != rs_c or es_b != es_c:
        return dict(id=item["id"], typed=False, reason="role_seq_diverged_between_resolvers")
    outcome_positions = [i for i, r in enumerate(rs_b) if r in (R_UNMET, R_MET)]
    goal_positions = [i for i, r in enumerate(rs_b) if r == R_GOAL]
    if not outcome_positions or not goal_positions:
        return dict(id=item["id"], typed=False, reason="no_goal_or_outcome_event_typed",
                    n_goal=len(goal_positions), n_outcome=len(outcome_positions), role_seq=rs_b)
    flagged = [i for i in outcome_positions if cid_b[i] != cid_c[i]]
    if not flagged:
        flagged = outcome_positions
    outcome_pos = outcome_positions[-1]
    score_b = directed_goal_outcome_score(rs_b, cid_b, 0, outcome_pos)
    score_c = directed_goal_outcome_score(rs_c, cid_c, 0, outcome_pos)
    delta = score_c - score_b
    adopt = decide_keep_or_revert({"content_match": delta}, ABSTAIN_BAND_DEFAULT)
    adopted = cid_c if adopt == "content_match" else cid_b
    final_owner = adopted[outcome_pos]
    baseline_owner = cid_b[outcome_pos]
    gold = item["gold_outcome_owner"]
    return dict(id=item["id"], typed=True, matches_gold=(final_owner == gold),
                recency_alone_matches_gold=(baseline_owner == gold), final_owner=final_owner,
                baseline_owner=baseline_owner, content_owner=cid_c[outcome_pos], gold=gold,
                adopt=adopt, score_b=score_b, score_c=score_c, delta=delta, role_seq=rs_b)


def main():
    mined = {it["id"]: it for it in _load_mined()}
    missing = [i for i in VERIFIED_CORRECT_IDS if i not in mined]
    assert not missing, f"verified ids not found in mined jsonl: {missing}"
    results = []
    for mid in VERIFIED_CORRECT_IDS:
        item = _build_c5_item(mined[mid])
        res = run_item(item)
        res["verification_note"] = VERIFIED_CORRECT_IDS[mid]
        results.append(res)
        print(f"[c5-realtext] {mid}: {res}", flush=True)

    n = len(results)
    n_typed = sum(1 for r in results if r["typed"])
    typed_results = [r for r in results if r["typed"]]
    n_correct = sum(1 for r in typed_results if r["matches_gold"])
    n_recency_correct = sum(1 for r in typed_results if r["recency_alone_matches_gold"])
    outcome_binding_accuracy = (n_correct / n_typed) if n_typed else None
    recency_baseline = (n_recency_correct / n_typed) if n_typed else None

    metrics = dict(
        anchor_name="c5_realtext_c3mined_v1", n_items=n, n_typed=n_typed,
        typing_fire_rate=round(n_typed / n, 4) if n else None,
        outcome_binding_accuracy=outcome_binding_accuracy, recency_baseline=recency_baseline,
        n_correct=n_correct, n_recency_correct=n_recency_correct,
        per_item=results,
        verdict="MEASURED_REALTEXT_C5" if n_typed else "VACUOUS_ZERO_TYPED",
        verdict_msg=(f"real-text C5: typed={n_typed}/{n} outcome_binding_acc={outcome_binding_accuracy} "
                     f"recency_baseline={recency_baseline}"),
        elapsed_s=0.0,
    )
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    tmp = OUTPUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, OUTPUT_PATH)
    print(f"[VERDICT] {metrics['verdict_msg']}", flush=True)
    return metrics


if __name__ == "__main__":
    main()
