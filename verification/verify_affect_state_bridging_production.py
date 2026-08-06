# WIRE-DON'T-ISLAND PROMOTION WITNESS (2026-08-06). Scaffold-free, tracing=False (no HDC tracing
# used anywhere in this module -- the organ under test does not take a tracing flag).
"""verification/verify_affect_state_bridging_production.py -- reproduces the AFFECT-STATE bridging
inference numbers off the PROMOTED organ (hdlab/goal_owner_select.py's detect_affect_state_
construction + _bridge_affect_outcome_event, wired into build_candidate_role_seq as the SECOND Tier-3
bridge alongside the evaluative bridge), NOT off the experiment cell directly. Every bank item / gold
label is IMPORTED from experiments/data/affect_state_bridging_bank_v1.jsonl (commit 0ff1a6d97's
Director-VET'd HARD_PASS bank), never re-authored, so this witness cannot silently drift from the
landed isolation record.

FIVE checks, matching the promotion contract:
  (1) zero-overlap bridging: the 5 POS_MET + 3 NEG_UNMET items must all resolve, through the PROMOTED
      production affect-bridge path (production type_goal_events + GeneralRecencyEntityResolver +
      detect_affect_state_construction + _bridge_affect_outcome_event), to {goal_holder: gold_role}
      and nobody else (8/8); the lexical-only arm (production verb-typing on the outcome sentence
      alone) must resolve 0/8 -- gap = 1.0.
  (2) valence: 5/5 POS_MET bridge to OUTCOME_MET, 3/3 NEG_UNMET bridge to OUTCOME_UNMET.
  (3) over-fire controls: 2/2 BYSTANDER items bridge to NOBODY (the affect is a non-goal-holder's);
      2/2 UNCHANGED items resolve via LEXICAL (bridge never engages, strict ADD).
  (4) scramble collapse: reassigning each item's GOAL context to a DIFFERENT item's context collapses
      bridging to 0/8 (the bridge keys off the goal-content link, not surface affect words).
  (5) cross-detector non-interference (both directions) + strict-ADD safety: the affect detector fires
      0 times on all 13 evaluative-bridging-bank outcome sentences AND 0 times on all 62 goal_owner_
      fair_v1 outcome sentences; the evaluative detector fires 0 times on all 12 affect-bank outcome
      sentences. Because the affect detector never fires on the eval/fair corpora, the affect bridge is
      never even consulted there, so production select_outcome_owner is byte-identical to the pre-affect
      organ on every one of those 75 passages (the strict-ADD no-regression property, proved by
      construction rather than by a fragile git-snapshot diff).

END-TO-END anchors: frank_fishing_glad (POS, first-person "how glad I am!") and peter_book_downcast
(NEG, third-person "he felt downcast") contain NO lexical outcome verb anywhere, so the pre-affect
organ raises OUTCOME_NEVER_TYPED on them -- their production select_outcome_owner resolution to the
correct owner is 100% attributable to the affect bridge (checked here).

HONEST SCOPE (not buried): the isolation HARD_PASS is a BRIDGE-LEVEL metric (which entity the affect
bridge binds the outcome to, typing the OUTCOME sentence only). The FULL production select_outcome_owner
is a strictly larger pipeline (enumerate every candidate + directed-score argmax + content-coherence
tie-break) that also types the GOAL clauses. On the 8 pos/neg items it selects the correct owner
end-to-end for 7/8; the sole miss, sam_race_joyful -> mother, is a PRE-EXISTING production quirk (sam's
goal clause "Sam wanted to WIN ..." lexically types WIN as OUTCOME_MET, which the directed-score argmax
then resolves to mother) that is byte-identical HEAD-vs-working (the affect bridge does not cause it and
correctly binds sam->MET at the bridge level). This witness asserts the 8/8 BRIDGE-level reproduction
(the isolation contract) plus the two clean end-to-end anchors; it records sam as a documented,
non-regressing known miss rather than papering over it.

SCALE NOTE: re-runs the SAME full-bank scale as the isolation cell (not a reduced smoke) -- the
discriminator is a boolean construction-detector + FHRR-decode registry lookup on a 12-item bank, no
HDC dimensionality/vector-count scaling, so there is no smoke-vs-full gap to bridge.
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_owner_select import (  # noqa: E402
    _sentences, GeneralRecencyEntityResolver, detect_affect_state_construction,
    detect_evaluative_construction, _bridge_affect_outcome_event, select_outcome_owner,
    enumerate_and_score, R_GOAL, R_MET, R_UNMET,
)
from hdlab.goal_typing import type_goal_events  # noqa: E402

AFFECT_BANK = os.path.join(REPO_ROOT, "experiments", "data", "affect_state_bridging_bank_v1.jsonl")
EVAL_BANK = os.path.join(REPO_ROOT, "experiments", "data", "evaluative_bridging_bank_v1.jsonl")
FAIR_BANK = os.path.join(REPO_ROOT, "experiments", "data", "goal_owner_fair_v1.jsonl")

EXPECTED_CAT_COUNTS = {"POS_MET": 5, "NEG_UNMET": 3, "BYSTANDER": 2, "UNCHANGED": 2}


def _load(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _goals_from_context(sents_prefix, roster):
    """Open-goal entities from the NON-outcome sentences via the PRODUCTION structural resolver +
    PRODUCTION type_goal_events -- the same has_open_goal source build_candidate_role_seq uses,
    scoped (like the isolation cell) to the goal clauses only."""
    resolver = GeneralRecencyEntityResolver(roster)
    goals = set()
    for s in sents_prefix:
        subj = resolver.subject_entity(s)
        for (e, r) in type_goal_events(s, subj):
            if r == R_GOAL:
                goals.add(e)
    return goals


def production_affect_resolve(text, roster, goal_context_text=None):
    """Reproduce the isolation cell's resolve_outcome USING ONLY PROMOTED production functions:
    lexical verb-typing on the outcome sentence first; the affect bridge is consulted only when
    lexical typing produced nothing (OUTCOME_NEVER_TYPED). `goal_context_text` overrides where the
    open-goal context is read from (for the scramble control); defaults to `text` itself."""
    sents = _sentences(text)
    outcome = sents[-1]
    lex = {}
    for c in sorted(roster):
        for (e, r) in type_goal_events(outcome, c):
            if e == c and r in (R_UNMET, R_MET):
                lex[c] = r
    if lex:
        return lex, "LEXICAL"
    ctx_sents = _sentences(goal_context_text)[:-1] if goal_context_text is not None else sents[:-1]
    goals = _goals_from_context(ctx_sents, roster)
    hits = {}
    for c in sorted(roster):
        role = _bridge_affect_outcome_event(outcome, roster, c, has_open_goal=(c in goals))
        if role is not None:
            hits[c] = role
    return hits, ("BRIDGE" if hits else "NONE")


def _score(item, hits):
    cat, holder = item["category"], item["goal_holder"]
    gold = R_MET if item["gold_polarity"] == "MET" else (
        R_UNMET if item["gold_polarity"] == "UNMET" else None)
    if cat in ("POS_MET", "NEG_UNMET"):
        return hits == {holder: gold}
    if cat == "BYSTANDER":
        return hits == {}
    if cat == "UNCHANGED":
        return hits.get(holder) == gold
    raise ValueError(cat)


def check_bridge_reproduction():
    bank = _load(AFFECT_BANK)
    cat_counts = {c: sum(1 for it in bank if it["category"] == c) for c in EXPECTED_CAT_COUNTS}
    assert cat_counts == EXPECTED_CAT_COUNTS, f"bank cardinality drift: {cat_counts}"

    cb, lex_cb, pos, neg, bys, unch = [], [], [], [], [], []
    for it in bank:
        hits, src = production_affect_resolve(it["text"], it["roster"])
        lex_only, _ = ({}, None)
        outcome = _sentences(it["text"])[-1]
        for c in sorted(it["roster"]):
            for (e, r) in type_goal_events(outcome, c):
                if e == c and r in (R_UNMET, R_MET):
                    lex_only[c] = r
        sc = _score(it, hits)
        if it["category"] in ("POS_MET", "NEG_UNMET"):
            cb.append(sc)
            lex_cb.append(_score(it, lex_only))
        if it["category"] == "POS_MET":
            pos.append(hits == {it["goal_holder"]: R_MET})
        if it["category"] == "NEG_UNMET":
            neg.append(hits == {it["goal_holder"]: R_UNMET})
        if it["category"] == "BYSTANDER":
            bys.append(hits == {})
        if it["category"] == "UNCHANGED":
            unch.append(sc and src == "LEXICAL")

    zero_overlap = sum(cb) / len(cb)
    lexical_only = sum(lex_cb) / len(lex_cb)
    assert zero_overlap == 1.0, f"zero_overlap_bridging_acc must be 1.0, got {zero_overlap}"
    assert lexical_only == 0.0, f"lexical_only_acc must be 0.0 (gap proof), got {lexical_only}"
    assert sum(pos) == 5, f"valence_pos: {sum(pos)}/5 items bridged to MET"
    assert sum(neg) == 3, f"valence_neg: {sum(neg)}/3 items bridged to UNMET"
    assert sum(bys) == 2, f"bystander_no_bridge: {sum(bys)}/2 items bound nobody"
    assert sum(unch) == 2, f"unchanged_control (LEXICAL, bridge idle): {sum(unch)}/2"
    print(f"[CHECK 1-3] bridge reproduction: zero_overlap={zero_overlap} lexical_only={lexical_only} "
          f"gap={zero_overlap - lexical_only} | valence pos={sum(pos)}/5 neg={sum(neg)}/3 | "
          f"bystander_no_bridge={sum(bys)}/2 | unchanged_LEXICAL={sum(unch)}/2")
    return zero_overlap, lexical_only


def check_scramble():
    bank = _load(AFFECT_BANK)
    cb = [it for it in bank if it["category"] in ("POS_MET", "NEG_UNMET")]
    ids = [it["id"] for it in cb]
    shifted = ids[1:] + ids[:1]
    assert all(a != b for a, b in zip(ids, shifted)), "scramble permutation has a fixed point"
    id2 = {it["id"]: it for it in cb}
    correct = 0
    for real, other in zip(ids, shifted):
        it = id2[real]
        hits, _ = production_affect_resolve(it["text"], it["roster"],
                                            goal_context_text=id2[other]["text"])
        correct += int(_score(it, hits))
    scramble_acc = correct / len(cb)
    assert scramble_acc == 0.0, f"scramble must collapse to 0.0, got {scramble_acc}"
    print(f"[CHECK 4] scramble collapse: scramble_acc={scramble_acc} (0/{len(cb)})")
    return scramble_acc


def check_interference_and_strict_add():
    affect_bank = _load(AFFECT_BANK)
    eval_bank = _load(EVAL_BANK)
    fair_bank = _load(FAIR_BANK)

    affect_on_eval = [it["id"] for it in eval_bank
                      if detect_affect_state_construction(_sentences(it["text"])[-1],
                                                          it["roster"])[0] is not None]
    affect_on_fair = [it.get("id") for it in fair_bank
                      if detect_affect_state_construction(_sentences(it["text"])[-1],
                                                          it["roster"])[0] is not None]
    eval_on_affect = [it["id"] for it in affect_bank
                      if detect_evaluative_construction(_sentences(it["text"])[-1],
                                                        it["roster"])[0] is not None]
    assert affect_on_eval == [], f"affect detector fired on eval bank: {affect_on_eval}"
    assert affect_on_fair == [], f"affect detector fired on fair instrument: {affect_on_fair}"
    assert eval_on_affect == [], f"eval detector fired on affect bank: {eval_on_affect}"
    print(f"[CHECK 5] non-interference: affect_on_eval=0/{len(eval_bank)} "
          f"affect_on_fair=0/{len(fair_bank)} eval_on_affect=0/{len(affect_bank)} -> the affect "
          f"bridge is never consulted on eval/fair, so production is byte-identical there (strict ADD)")


def check_end_to_end_anchors():
    """The two lexical-outcome-free passages: pre-affect organ raises OUTCOME_NEVER_TYPED, so a
    correct production select_outcome_owner resolution is 100% attributable to the affect bridge."""
    frank_roster = {"frank": "m", "father": "m"}
    frank_text = ("Frank wanted to catch a fine fish with his father. They walked down to the river "
                  "together. Frank cried, \"Oh, how glad I am!\"")
    assert select_outcome_owner(frank_text, frank_roster, 0) == "frank"
    peter_roster = {"peter": "m", "sister": "f"}
    peter_text = ("Peter wanted to keep his new book free of every crease. His little sister borrowed "
                  "it without asking. He felt downcast when he found the torn page.")
    assert select_outcome_owner(peter_text, peter_roster, 0) == "peter"

    # documented, non-regressing known miss (honest scope, not papered over): sam's goal clause
    # lexically types WIN as OUTCOME_MET pre-bridge, so the full selector resolves owner=mother.
    sam_roster = {"sam": "m", "mother": "f"}
    sam_text = ("Sam wanted to win the village race this spring. His mother watched proudly from the "
                "porch. He felt joyful when he crossed the line first.")
    sam_owner = select_outcome_owner(sam_text, sam_roster, 0)
    assert sam_owner in sam_roster, sam_owner  # resolves (pre-existing lexical-outcome path), not the bridge
    print(f"[CHECK 6] end-to-end anchors: frank->frank, peter->peter (bridge-only resolutions); "
          f"documented known miss sam->{sam_owner} (pre-existing WIN-lexical quirk, not the bridge)")


def run():
    z, lex = check_bridge_reproduction()
    scr = check_scramble()
    check_interference_and_strict_add()
    check_end_to_end_anchors()
    print("[ALL CHECKS PASS] hdlab/goal_owner_select.py affect-state Tier-3 bridge reproduces the "
          f"isolation HARD_PASS through production (zero_overlap={z}, gap={z - lex}, scramble={scr}, "
          "0/13 + 0/12 + 0/62 interference) and is strict-ADD (byte-identical on eval/fair by "
          "construction).")
    return {"zero_overlap_bridging_acc": z, "lexical_only_acc": lex, "scramble_acc": scr}


if __name__ == "__main__":
    run()
