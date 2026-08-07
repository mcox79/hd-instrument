# WHOLE-PASSAGE OUTCOME RESOLUTION (increment 2b) MEASUREMENT WITNESS (2026-08-06). Scaffold-free,
# tracing=False (the organ under test does not take a tracing flag). NOT collected by pytest
# (named verify_*.py, not test_*.py -- pyproject.toml's python_files=["test_*.py"] does not discover
# it, matching the documented convention in verification/test_goal_owner_select.py's own docstring:
# a witness that pytest never runs is not a gate, so this file is meant to be run standalone and does
# NOT change `python verification/run_certification.py`'s 220 passed / 3 skipped count).
"""verification/verify_whole_passage_outcome_resolution_2b.py -- reproduces the MEASURED before/after
OUTCOME_NEVER_TYPED count for hdlab.goal_owner_select.build_candidate_role_seq's 2026-08-06 backward-
scan widening (increment 2b, notes/formalize_situation_model_DMN_integration_spec_2026-08-06.md op D:
"Whole-model outcome resolution"), on experiments/data/goal_bearing_modern_eval_v1.jsonl (44 items,
seed=0), AND the regression this widening measurably introduces on one of the 13 pre-2b principled-
correct owner picks (per-item honest disclosure, not a pass/fail cosmetic).

MECHANISM UNDER TEST (unchanged since 2b landed): build_candidate_role_seq's outcome-typing step tries
sents[-1] first (via the factored-out _type_outcome_at: lexical/similarity type_goal_events, then the
two Tier-3 bridges); if THAT still yields no MET/UNMET, it now walks BACKWARD over sents[:-1]
(latest-first) and takes the first sentence whose SAME _type_outcome_at hypothesis-test (entity=
outcome_entity) types one. STRICT-ADD: only runs when sents[-1] already produced nothing, so any item
resolving on its final sentence is byte-identical to pre-2b.

PRE-2b RECONSTRUCTION (not a duplicate mechanism): `_pre_2b_build_candidate_role_seq` below composes
the SAME certified pieces (`_type_outcome_at`, `_sentences`, `GeneralRecencyEntityResolver`,
`type_goal_events`) the production organ itself calls, just omitting the backward-scan loop -- the
identical reconstruction pattern verification/test_goal_owner_select.py already uses for its
`_positional_pick` (reconstruct a prior code path from certified production pieces, never re-author
the mechanism).

TWO CHECKS:
  (1) never-typed count: PRE-2b=18/44, POST-2b=14/44 (recovered 4 items). Gate (per the spec's
      increment-2b HARD-PASS band) needs POST-2b <= 12/44 (>=6 recovered) -- 14 is short of that.
  (2) zero-regression check on the 13 pre-2b principled-correct owner picks (non-alphabetical-
      fallback correct answers, i.e. NOT luck artifacts -- see scratch harness this witness's
      PRE_2B_PRINCIPLED_CORRECT set reproduces): exactly ONE regresses post-2b --
      lw_beth_slippers_piano_gift (gold=beth) flips to laurence. Root cause (see build_candidate_
      role_seq's own docstring + the exp_dev completion report that shipped this file): the backward
      scan applies type_goal_events' LEXICAL/verb-class typing to EARLIER sentences using outcome_
      entity as a blind hypothesis substitution, with no check against that sentence's own already-
      resolved structural subject (GeneralRecencyEntityResolver, computed one line above in the very
      same function) -- "Beth worked away early and late" types an OUTCOME_UNMET when hypothesis-
      tested with entity='laurence', even though Beth (not Laurence) is that sentence's real subject.
      The two Tier-3 bridges do NOT have this defect (they gate on addressee/holder == entity), so the
      failure is specific to the lexical branch once applied outside its originally-safe sents[-1]-only
      scope.

VERDICT: MEASURED HARD-FAIL per the increment-2b gate (recovered 4 < 6 needed, AND a real regression
where the gate requires zero). This witness reproduces that finding exactly, not a false HARD-PASS.
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_owner_select import (  # noqa: E402
    _sentences, GeneralRecencyEntityResolver, _type_outcome_at, _outcome_pos,
    directed_goal_outcome_score, enumerate_and_score, entity_goal_themes, clause_theme, R_GOAL,
)
from hdlab.goal_typing import type_goal_events  # noqa: E402

EVAL_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_bearing_modern_eval_v1.jsonl")

# The 13 PRE-2b principled-correct item ids (non-alphabetical-fallback correct owner picks), MEASURED
# on disk before increment 2b landed (Director's Step-0 + this witness's own PRE_2B reconstruction
# below independently agree -- see check_zero_regression_on_principled_correct's self-check).
PRE_2B_PRINCIPLED_CORRECT = {
    "lw_jo_laurie_snowball", "lw_jo_wanted_forgive_amy", "lw_beth_slippers_piano_gift",
    "lw_meg_currant_jelly", "lw_jo_story_prize", "ts_potter_failed_escape", "woz_scarecrow_brains",
    "woz_lion_courage_denied", "alice_beautiful_garden", "race_tim_rescue", "race_german_dog",
    "onestop_skydiver", "onestop_malala",
}


def _load_rows():
    with open(EVAL_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def _pre_2b_build_candidate_role_seq(passage_text, roster, outcome_entity):
    """Reconstructs the PRE-2b organ (sents[-1] only, no backward scan) from the exact same
    production pieces build_candidate_role_seq composes -- see module docstring."""
    sents = _sentences(passage_text)
    resolver = GeneralRecencyEntityResolver(roster)
    role_seq, cluster_ids = [], []
    for s in sents[:-1]:
        subj = resolver.subject_entity(s)
        for (entity, role) in type_goal_events(s, subj):
            role_seq.append(role)
            cluster_ids.append(entity)
    has_open_goal = any(r == R_GOAL and cid == outcome_entity for r, cid in zip(role_seq, cluster_ids))
    outcome_events = _type_outcome_at(sents[-1], roster, outcome_entity, has_open_goal)
    for (entity, role) in outcome_events:
        role_seq.append(role)
        cluster_ids.append(entity)
    return role_seq, cluster_ids


def _pre_2b_enumerate_and_score(passage_text, roster, seed):
    candidates = sorted(roster.keys())
    scored, any_typed = {}, False
    for c in candidates:
        rs, cid = _pre_2b_build_candidate_role_seq(passage_text, roster, c)
        pos = _outcome_pos(rs)
        if pos is None:
            scored[c] = 0.0
            continue
        any_typed = True
        scored[c] = directed_goal_outcome_score(rs, cid, seed, pos)
    if not any_typed:
        return None, None
    max_score = max(scored.values())
    winners = [c for c in candidates if scored[c] == max_score]
    return scored, winners


def _pick(scored, winners, passage_text, roster):
    """Mirrors select_outcome_owner's tie-break (content-coherence, else sorted-order) exactly."""
    if winners is None:
        return None
    if len(winners) == 1:
        return winners[0]
    goal_themes = entity_goal_themes(passage_text, roster)
    out_theme = clause_theme(_sentences(passage_text)[-1], roster)
    overlappers = [c for c in winners if goal_themes.get(c, set()) & out_theme]
    if len(overlappers) == 1:
        return overlappers[0]
    return winners[0]


# ---------------------------------------------------------------------------
# (1) never-typed count: PRE-2b=18/44, POST-2b=14/44, recovered={4 named ids}
# ---------------------------------------------------------------------------
def check_never_typed_before_after():
    rows = _load_rows()
    assert len(rows) == 44, f"expected 44-item eval set, got {len(rows)}"
    before_never, after_never = set(), set()
    for r in rows:
        text, roster = r["text"], r["roster"]
        pre_scored, _pre_winners = _pre_2b_enumerate_and_score(text, roster, seed=0)
        if pre_scored is None:
            before_never.add(r["id"])
        try:
            enumerate_and_score(text, roster, seed=0)
        except ValueError:
            after_never.add(r["id"])
    assert len(before_never) == 18, f"PRE-2b OUTCOME_NEVER_TYPED must reproduce 18/44, got {len(before_never)}"
    assert len(after_never) == 14, f"POST-2b OUTCOME_NEVER_TYPED must reproduce 14/44, got {len(after_never)}"
    recovered = before_never - after_never
    newly_broken = after_never - before_never
    expected_recovered = {"agg_anne_picnic_wish_ch14", "ts_becky_anatomy_book_confession",
                           "ts_tom_sugar_theft", "race_davey_wiffle"}
    assert recovered == expected_recovered, f"recovered set changed: {sorted(recovered)}"
    assert not newly_broken, f"a previously-typed item stopped typing entirely: {sorted(newly_broken)}"
    print(f"[CHECK never_typed] before=18/44 after=14/44 recovered={sorted(recovered)} "
          f"(n_recovered={len(recovered)}; gate needs >=6 recovered / <=12 remaining for HARD-PASS)")
    return {"n_before": len(before_never), "n_after": len(after_never), "recovered": sorted(recovered)}


# ---------------------------------------------------------------------------
# (2) zero-regression check on the 13 PRE-2b principled-correct items
# ---------------------------------------------------------------------------
def check_zero_regression_on_principled_correct():
    rows = {r["id"]: r for r in _load_rows()}
    assert len(PRE_2B_PRINCIPLED_CORRECT) == 13
    regressions = []
    for pid in sorted(PRE_2B_PRINCIPLED_CORRECT):
        r = rows[pid]
        text, roster, gold = r["text"], r["roster"], r["gold_outcome_owner"]
        pre_scored, pre_winners = _pre_2b_enumerate_and_score(text, roster, seed=0)
        pre_pick = _pick(pre_scored, pre_winners, text, roster)
        assert pre_pick == gold, (
            f"PRE-2b regression-baseline reproduction failed for {pid}: expected gold={gold!r} "
            f"(principled-correct baseline), got {pre_pick!r} -- baseline set is stale, re-derive it")
        post_scored, post_winners = enumerate_and_score(text, roster, seed=0)
        post_pick = _pick(post_scored, post_winners, text, roster)
        if post_pick != gold:
            regressions.append((pid, gold, post_pick))
    assert regressions == [("lw_beth_slippers_piano_gift", "beth", "laurence")], (
        f"regression set changed from the measured finding: {regressions}")
    print(f"[CHECK zero_regression] 13 pre-2b principled-correct items re-checked post-2b: "
          f"{len(regressions)} regression(s) = {regressions} "
          f"(gate requires 0 for HARD-PASS -- this is the MEASURED HARD-FAIL trigger)")
    return {"n_checked": len(PRE_2B_PRINCIPLED_CORRECT), "regressions": regressions}


def test_never_typed_before_after():
    check_never_typed_before_after()


def test_zero_regression_on_principled_correct():
    check_zero_regression_on_principled_correct()


def run():
    r1 = check_never_typed_before_after()
    r2 = check_zero_regression_on_principled_correct()
    gate_pass = (r1["n_after"] <= 12 and len(r2["regressions"]) == 0)
    verdict = "HARD-PASS" if gate_pass else "HARD-FAIL"
    print(f"[VERDICT] increment 2b whole-passage outcome resolution: {verdict} "
          f"(never_typed 18->{r1['n_after']}, recovered={len(r1['recovered'])} of 6 needed, "
          f"regressions={len(r2['regressions'])} of 0 allowed)")
    return {"never_typed": r1, "regression": r2, "verdict": verdict}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, default=str))
