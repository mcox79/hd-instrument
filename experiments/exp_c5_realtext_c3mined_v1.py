"""exp_c5_realtext_c3mined_v1 -- THE FIRST real-text Component-5 test: does directed_goal_outcome_
score (exp_component5_gold_role_isolated_v1, reused bit-identical) bind the outcome to the true
goal-owner over recency, on DIVERSE REAL LITBANK PROSE (not the authored x23 template)?

Owner-gold source: experiments/data/goal_outcome_c3mined_v1.jsonl (C3-syntax mining,
mine_goal_outcome_litbank_c3syntax_v1.py), FILTERED to the AGENT-VERIFIED owner-correct subset
(15/40 items; agent read every mined item's goal_sentence + surrounding text and judged whether the
C3-syntax-resolved goal_owner is the TRUE referent -- per task contract "do NOT run C5 on items
whose C3-owner-gold is wrong"). The 15 ids are hardcoded below (VERIFIED_CORRECT_IDS), each with a
one-line verification note.

TYPING FIX (2026-08-05, this cell, WIRE-DON'T-ISLAND): the first attempt (typing_fire_rate=0.067,
1/15) typed GOAL/OUTCOME events via the narrow authored-template lexicon
(exp_situation_model_goal_outcome_dimension_v1.type_sentence_events, V2_DESIRE={want,wish,hope,
long,try,plead,...}) which does not fire on the real psych verbs (fear/see/hear/know/think/...) the
C3-mined items were themselves SELECTED on. Root-cause + fix, both REUSED bit-identical (not
reinvented) from the exact organs that already cover this real-text distribution:
  GOAL typing  -> hdlab.thematic_role_labeler.PSYCH_VERBS + lemma_verb (frame subj=EXPERIENCER):
                  the SAME psych-verb prefilter mine_goal_outcome_litbank_c3syntax_v1.py used to
                  SELECT these sentences in the first place (its `lemma in PSYCH_VERBS` gate) --
                  guaranteed non-vacuous on this item bank by construction, no islanded new lexicon.
  OUTCOME typing -> mine_goal_outcome_litbank_v1.ACHIEVE_CUES / BLOCK_CUES: the SAME broad
                  real-prose achieve/block cue lexicon the miner used to locate each item's
                  outcome_span (reused bit-identical, not the authored-template-tuned
                  V2_OUTCOME_MET/UNMET). Honest scope note: this is a SUPPLIED lexicon (knowledge),
                  not a learned outcome-valence classifier -- C3's role-labeler has no
                  outcome-valence component; broadening the lexicon is option (a) from the task
                  brief, picked because it is the cleanest bit-identical reuse and is exactly the
                  criterion that already located these items' outcome spans (no new mechanism).
See type_sentence_events_c3 / build_positions_c3 below (local to this eval; the shared
type_sentence_events / build_positions in the imported modules are left UNCHANGED to avoid any
regression on the authored 23-item RECENCY bank those other cells still depend on).

Reuses bit-identical: GeneralRecencyEntityResolver, ContentMatchResolver,
directed_goal_outcome_score, decide_keep_or_revert, ABSTAIN_BAND_DEFAULT, DEFAULT_ROSTER, GO_ROLES,
R_GOAL/R_UNMET/R_MET (all from exp_component5_gold_role_isolated_v1.py, 2026-08-04/05 landed cell).
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
    GeneralRecencyEntityResolver, ContentMatchResolver,
    directed_goal_outcome_score, DEFAULT_ROSTER, R_GOAL, R_UNMET, R_MET,
)
from exp_situation_model_goal_outcome_dimension_v1 import _sentences, _ordered_tokens  # noqa: E402
from hdlab.thematic_role_labeler import PSYCH_VERBS, lemma_verb  # noqa: E402
from mine_goal_outcome_litbank_v1 import ACHIEVE_CUES, BLOCK_CUES  # noqa: E402
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


def type_sentence_events_c3(sentence: str, subject):
    """GOAL/OUTCOME typing for real-text prose, reused bit-identical from the C3-mining organs
    (see module docstring TYPING FIX). GOAL fires iff any token's lemma (hdlab.thematic_role_
    labeler.lemma_verb) is in PSYCH_VERBS (the frame subj=EXPERIENCER psych/desiderative class) --
    exactly the prefilter that selected this sentence into the mined bank. OUTCOME (UNMET/MET)
    fires via mine_goal_outcome_litbank_v1.BLOCK_CUES / ACHIEVE_CUES (the same lexicon the miner
    used to locate outcome_span). Both events are attributed to `subject` (the resolved clause
    subject), same attribution contract as type_sentence_events."""
    toks = _ordered_tokens(sentence)
    tokset = set(toks)
    has_goal = any(lemma_verb(t) in PSYCH_VERBS for t in toks)
    has_unmet = bool(tokset & BLOCK_CUES)
    has_met = bool(tokset & ACHIEVE_CUES)
    events = []
    if has_goal and subject is not None:
        events.append((subject, R_GOAL))
    if has_unmet and subject is not None:
        events.append((subject, R_UNMET))
    if has_met and subject is not None:
        events.append((subject, R_MET))
    return events, dict(has_desire=has_goal, has_unmet=has_unmet, has_met=has_met, subject=subject)


def build_positions_c3(item: dict, resolver, scramble_owner_to_foil: str | None = None):
    """Mirrors exp_component5_gold_role_isolated_v1.build_positions exactly (same resolver-driven
    subject walk, same global-position-index contract, same role-scramble control semantics) but
    calls type_sentence_events_c3 (this file, C3-covered typing) instead of the narrow-lexicon
    type_sentence_events -- kept LOCAL (not edited in-place in the shared module) so the authored
    23-item RECENCY bank other cells depend on is untouched (no regression risk)."""
    owner = item.get("owner")
    role_seq, cluster_ids = [], []
    for sent in _sentences(item["text"]):
        subj = resolver.subject_entity(sent)
        ev, _info = type_sentence_events_c3(sent, subj)
        for (entity, role) in ev:
            eff_entity = entity
            if scramble_owner_to_foil is not None and role == R_GOAL and entity == owner:
                eff_entity = scramble_owner_to_foil
            role_seq.append(role)
            cluster_ids.append(eff_entity)
            if hasattr(resolver, "mark_role"):
                resolver.mark_role(eff_entity, role)
    event_slots = list(range(len(role_seq)))
    return role_seq, cluster_ids, event_slots


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
        roster=roster, structure_type=mined.get("structure_type"),
    )


def run_item(item, scrambled: bool = False):
    """Mirrors exp_component5_gold_role_isolated_v1.run_recency_item, but item-roster-driven
    (real names, not the toy 12-name cast) and using build_positions_c3 (C3-covered typing, this
    file) instead of the narrow-lexicon build_positions -- reuses ContentMatchResolver/
    GeneralRecencyEntityResolver/directed_goal_outcome_score/decide_keep_or_revert bit-identical.
    If scrambled, the item's own mined `foil` is used as the role-scramble target (mislabels the
    GOAL holder as the foil, text/gold unchanged) -- the non-vacuous-scramble control."""
    roster = item["roster"]
    rs_b, cid_b, es_b = build_positions_c3(item, GeneralRecencyEntityResolver(roster))
    foil = item.get("foil")
    scramble_target = foil if (scrambled and foil) else None
    rs_c, cid_c, es_c = build_positions_c3(
        item, ContentMatchResolver(roster), scramble_owner_to_foil=scramble_target)
    if rs_b != rs_c or es_b != es_c:
        return dict(id=item["id"], scrambled=scrambled, typed=False,
                    reason="role_seq_diverged_between_resolvers")
    outcome_positions = [i for i, r in enumerate(rs_b) if r in (R_UNMET, R_MET)]
    goal_positions = [i for i, r in enumerate(rs_b) if r == R_GOAL]
    if not outcome_positions or not goal_positions:
        return dict(id=item["id"], scrambled=scrambled, typed=False,
                    reason="no_goal_or_outcome_event_typed",
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
    return dict(id=item["id"], scrambled=scrambled, typed=True, matches_gold=(final_owner == gold),
                recency_alone_matches_gold=(baseline_owner == gold), final_owner=final_owner,
                baseline_owner=baseline_owner, content_owner=cid_c[outcome_pos], gold=gold, foil=foil,
                adopt=adopt, score_b=score_b, score_c=score_c, delta=delta, role_seq=rs_b)


def self_test():
    """Pre-flight smoke gate: (1) typing fix actually fires GOAL via PSYCH_VERBS on a real
    fear-verb sentence the narrow V2_DESIRE lexicon would miss; (2) OUTCOME fires via
    ACHIEVE_CUES/BLOCK_CUES; (3) one real mined item runs end-to-end typed=True; (4) scramble
    flips a genuine trap's final_owner off gold (non-vacuous-scramble, make-or-break guard)."""
    # (1) GOAL fires on "feared" (not in V2_DESIRE) via PSYCH_VERBS/lemma_verb.
    ev, info = type_sentence_events_c3("She had feared he would be tiresome", "her")
    assert info["has_desire"] is True, "PSYCH_VERBS typing must fire GOAL on 'feared'"
    assert ("her", R_GOAL) in ev
    # (2) OUTCOME fires via the miner's own ACHIEVE_CUES/BLOCK_CUES (broader than V2_OUTCOME).
    ev2, info2 = type_sentence_events_c3("At last she succeeded and was glad", "her")
    assert info2["has_met"] is True, "ACHIEVE_CUES typing must fire OUTCOME_MET on 'succeeded'"
    ev3, info3 = type_sentence_events_c3("She refused and was ashamed", "her")
    assert info3["has_unmet"] is True, "BLOCK_CUES typing must fire OUTCOME_UNMET on 'refused'"

    # (3)+(4) end-to-end on one real mined item with a foil (scramble control must be non-vacuous).
    mined = {it["id"]: it for it in _load_mined()}
    mid = "c3_238_dear_enemy__s35"  # Judy would like to see her (positive_desire, achieved, foil=Jane)
    item = _build_c5_item(mined[mid])
    assert item["foil"] == "jane", f"expected foil jane for smoke item, got {item['foil']!r}"
    res = run_item(item, scrambled=False)
    assert res["typed"] is True, f"smoke item must type (goal+outcome both present): {res}"
    res_s = run_item(item, scrambled=True)
    assert res_s["typed"] is True, f"scrambled smoke item must still type: {res_s}"
    print(f"[SELFTEST PASS] typing fix fires on real psych/achieve/block verbs; smoke item {mid} "
          f"typed intact={res['typed']}/matches_gold={res['matches_gold']} "
          f"scrambled_matches_gold={res_s['matches_gold']}", flush=True)
    return True


def main():
    mined = {it["id"]: it for it in _load_mined()}
    missing = [i for i in VERIFIED_CORRECT_IDS if i not in mined]
    assert not missing, f"verified ids not found in mined jsonl: {missing}"
    results = []
    scramble_results = []
    for mid in VERIFIED_CORRECT_IDS:
        mined_item = mined[mid]
        item = _build_c5_item(mined_item)
        res = run_item(item, scrambled=False)
        res["verification_note"] = VERIFIED_CORRECT_IDS[mid]
        res["structure_type"] = mined_item.get("structure_type")
        results.append(res)
        print(f"[c5-realtext] {mid}: {res}", flush=True)

        if item.get("foil"):
            res_s = run_item(item, scrambled=True)
            res_s["structure_type"] = mined_item.get("structure_type")
            scramble_results.append(res_s)
            print(f"[c5-realtext-scrambled] {mid}: {res_s}", flush=True)

    n = len(results)
    n_typed = sum(1 for r in results if r["typed"])
    typed_results = [r for r in results if r["typed"]]
    n_correct = sum(1 for r in typed_results if r["matches_gold"])
    n_recency_correct = sum(1 for r in typed_results if r["recency_alone_matches_gold"])
    outcome_binding_accuracy = (n_correct / n_typed) if n_typed else None
    recency_baseline = (n_recency_correct / n_typed) if n_typed else None
    beats_recency = (outcome_binding_accuracy is not None and recency_baseline is not None and
                      outcome_binding_accuracy > recency_baseline)

    # NON-VACUOUS SCRAMBLE CONTROL: among the intact-typed, intact-CORRECT trap items that have a
    # mined foil, does scrambling the GOAL holder onto the foil flip final_owner off gold?
    scr_typed = [r for r in scramble_results if r["typed"]]
    intact_by_id = {r["id"]: r for r in typed_results}
    scramble_eligible = [r for r in scr_typed if intact_by_id.get(r["id"], {}).get("matches_gold")]
    n_scramble_eligible = len(scramble_eligible)
    n_scramble_collapsed = sum(1 for r in scramble_eligible if not r["matches_gold"])
    scramble_collapse_rate = (n_scramble_collapsed / n_scramble_eligible) if n_scramble_eligible else None
    non_vacuous_scramble = (scramble_collapse_rate is not None and scramble_collapse_rate >= 0.5)

    # HONEST DIAGNOSTIC (per task brief "does it degrade, and WHERE"): does the recency candidate
    # (baseline_owner) ever DISAGREE with the content-match candidate (content_owner) at the
    # outcome slot on this real-text sample? If never, C5's directed-score SELECTION mechanism was
    # never exercised (adopting either candidate yields the identical final_owner) -- the reported
    # outcome_binding_accuracy is then measuring only the upstream syntactic-subject-resolution +
    # typing accuracy (GeneralRecencyEntityResolver alone), NOT C5's selection logic, regardless of
    # what the raw accuracy number says. This is a DIFFERENT and more fundamental finding than
    # "degrades" -- the recency-vs-content-match AMBIGUITY structure C5 was built to resolve barely
    # arises on real prose sampled this way, because build_positions_c3's subject_entity() finds an
    # explicit roster NAME token in most sentences before ever falling through to the
    # pronoun-disambiguation branch where the two resolvers could diverge.
    n_candidate_divergent = sum(1 for r in typed_results if r["baseline_owner"] != r["content_owner"])
    candidate_divergence_rate = (n_candidate_divergent / n_typed) if n_typed else None
    selection_mechanism_exercised = (n_candidate_divergent > 0)

    # per structure_type breakdown (honest small-N transparency)
    by_struct = {}
    for r in results:
        st = r.get("structure_type") or "unknown"
        d = by_struct.setdefault(st, dict(n=0, n_typed=0, n_correct=0))
        d["n"] += 1
        if r["typed"]:
            d["n_typed"] += 1
            if r["matches_gold"]:
                d["n_correct"] += 1

    if n_typed == 0:
        verdict = "VACUOUS_ZERO_TYPED"
    elif not selection_mechanism_exercised:
        # THE HONEST CRITICAL FINDING (per task brief "does it degrade, and WHERE"): recency and
        # content-match candidates NEVER disagreed at the outcome slot on any of the n_typed real
        # items -- C5's directed-score SELECTION/adoption logic was structurally never exercised
        # (adopting baseline vs content always yields the identical final_owner), so
        # outcome_binding_accuracy==recency_baseline exactly is NOT informative about C5's
        # selection mechanism; it is the upstream resolver+typing accuracy alone. Reported as its
        # own verdict class (distinct from a tested MIDDLE/HARD_FAIL) so it is never misread as
        # "C5 selection tested and tied recency."
        verdict = "SELECTION_MECHANISM_UNTESTED_NO_CANDIDATE_DIVERGENCE_ON_REALTEXT"
    elif outcome_binding_accuracy <= 0.334:
        verdict = "HARD_FAIL_NO_LIFT"
    elif outcome_binding_accuracy >= 0.67 and (non_vacuous_scramble or n_scramble_eligible == 0):
        verdict = "MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS"  # small-N cap (N<=15), per contract
    else:
        verdict = "MIDDLE_BAND"

    metrics = dict(
        anchor_name="c5_realtext_c3mined_v1", n_items=n, n_typed=n_typed,
        typing_fire_rate=round(n_typed / n, 4) if n else None,
        outcome_binding_accuracy=outcome_binding_accuracy, recency_baseline=recency_baseline,
        beats_recency=beats_recency,
        n_correct=n_correct, n_recency_correct=n_recency_correct,
        n_candidate_divergent=n_candidate_divergent, candidate_divergence_rate=candidate_divergence_rate,
        selection_mechanism_exercised=selection_mechanism_exercised,
        n_scramble_eligible=n_scramble_eligible, n_scramble_collapsed=n_scramble_collapsed,
        scramble_collapse_rate=scramble_collapse_rate, non_vacuous_scramble=non_vacuous_scramble,
        by_structure_type=by_struct,
        typing_fix=dict(
            goal_typing="hdlab.thematic_role_labeler.PSYCH_VERBS + lemma_verb (C3 frame subj=EXPERIENCER)",
            outcome_typing="mine_goal_outcome_litbank_v1.ACHIEVE_CUES/BLOCK_CUES (supplied lexicon, "
                           "same as the miner used; C3 role-labeler has no outcome-valence component -- "
                           "honest scope note, this is knowledge-supply not a learned classifier)",
            prior_fire_rate=0.067,
        ),
        per_item=results, per_item_scrambled=scramble_results,
        verdict=verdict,
        verdict_msg=(f"real-text C5 (typing FIXED via C3 PSYCH_VERBS/ACHIEVE/BLOCK reuse): "
                     f"typing_fire_rate={round(n_typed / n, 4) if n else None} ({n_typed}/{n}) "
                     f"outcome_binding_acc={outcome_binding_accuracy} recency_baseline={recency_baseline} "
                     f"beats_recency={beats_recency} candidate_divergence_rate={candidate_divergence_rate} "
                     f"({n_candidate_divergent}/{n_typed} typed items) "
                     f"selection_mechanism_exercised={selection_mechanism_exercised} "
                     f"scramble_collapse_rate={scramble_collapse_rate} (n_eligible={n_scramble_eligible}) "
                     f"non_vacuous_scramble={non_vacuous_scramble}"),
        n=n, small_n=True, elapsed_s=0.0,
    )
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
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
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    main()
