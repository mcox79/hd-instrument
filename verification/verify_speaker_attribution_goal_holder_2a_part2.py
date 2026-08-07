# WIRE-DON'T-ISLAND VERIFICATION WITNESS (2026-08-07). Scaffold-free, tracing=False (no HDC tracing
# anywhere in this module -- the organs under test do not take a tracing flag).
"""verification/verify_speaker_attribution_goal_holder_2a_part2.py -- reproduces the 2a-part-2
SPEAKER-ATTRIBUTION goal-holder fallback contract off the PROMOTED production organ
(hdlab.goal_owner_select._unify_owner_via_polarity_path's new _speaker_attributed_goal_holder branch),
against the REAL goal_bearing_modern_eval_v1.jsonl 44-item eval bank (the SAME bank 2a-part-1's own
verify_path_unification_2a_part1.py witness uses).

WHAT THIS CHECKS:
  (1) BEFORE count (post-2a-part-1, pre-2a-part-2): replays _unify_owner_via_polarity_path AS IT STOOD
      after 2a-part-1 (subject-based resolution ONLY, no speaker-attribution) via a local re-derivation
      using the SAME unmodified primitives the production function itself imports
      (congruence_with_lexicon_fallback, _sentences, GeneralRecencyEntityResolver, find_desired_state,
      build_candidate_role_seq, _outcome_pos) -- asserted == 15, matching the pre-VET's stated "OWNER
      OUTCOME_NEVER_TYPED 15" baseline (18 raw pre-fix - 3 2a-part-1 recoveries).
  (2) AFTER count: the ACTUAL (2a-part-2-applied) hdlab.goal_owner_select.enumerate_and_score
      never-typed count over the same 44 items, asserted <= 14 (recover >= 1: woodman).
  (3) woz_tin_woodman_heart is in the recovered set and resolves to gold_outcome_owner == 'woodman' via
      select_outcome_owner.
  (4) NO REGRESSION on the three 2a-part-1 recoveries (onestop_hunt_crowdfunding -> hunt,
      woz_dorothy_kansas_wish -> dorothy, onestop_limal_dating -> limal): all three still resolve to
      their correct gold owner post-2a-part-2 (this fallback is STRICT-ADD -- it only ever runs when
      subject-based resolution, 2a-part-1's own path, ALREADY returned None; it must never perturb an
      item 2a-part-1 already fixed).
  (5) NO REGRESSION on every OTHER item (not newly recovered by 2a-part-2): byte-identical
      select_outcome_owner pick vs the post-2a-part-1 (pre-2a-part-2) replay.
  (6) The certified fair instruments stay byte-identical: reuses (imports, does not reimplement)
      verification/test_goal_owner_select.py's run() -- 48/48 fair instrument + 12/12 multigoal,
      unchanged by this strict-ADD.

HONEST SCOPE: this witness measures the OWNER-SELECTION contract for the ONE decisive speaker-
attribution case (woz_tin_woodman_heart), per this task's pre-VET; it does not claim to fix any other
never-typed item in the bank (the other 14 items remain never-typed, unaffected by this change).
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_owner_select import (  # noqa: E402
    select_outcome_owner, enumerate_and_score, build_candidate_role_seq, _outcome_pos,
    _sentences, GeneralRecencyEntityResolver, entity_goal_themes, clause_theme,
    directed_goal_outcome_score,
)
from hdlab.goal_typing import congruence_with_lexicon_fallback, find_desired_state  # noqa: E402

EVAL_BANK = os.path.join(REPO_ROOT, "experiments", "data", "goal_bearing_modern_eval_v1.jsonl")
SEED = 0
EXPECTED_BEFORE_NEVER_TYPED = 15  # post-2a-part-1, pre-2a-part-2 (18 raw pre-fix - 3 part-1 recoveries)
MIN_RECOVERED = 1
TARGET_ID = "woz_tin_woodman_heart"
TARGET_OWNER = "woodman"
PART1_RECOVERIES = {"onestop_hunt_crowdfunding": "hunt", "woz_dorothy_kansas_wish": "dorothy",
                     "onestop_limal_dating": "limal"}


def _load_bank():
    rows = []
    with open(EVAL_BANK, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _owner_path_never_typed(passage_text, roster):
    """True iff the OWNER path's own typer (unmodified) types NOTHING for ANY roster candidate -- the
    `not any_typed` precondition BOTH the 2a-part-1 and 2a-part-2 fallbacks require to even be
    reached."""
    for c in sorted(roster.keys()):
        rs, _cid = build_candidate_role_seq(passage_text, roster, c)
        if _outcome_pos(rs) is not None:
            return False
    return True


def _pre_part2_unify(passage_text, roster):
    """Replays _unify_owner_via_polarity_path AS IT STOOD AFTER 2a-part-1 (subject-based resolution
    ONLY -- no speaker-attribution fallback), using the SAME unmodified primitives the production
    function itself imports. This is the "BEFORE" state for 2a-part-2's own before/after measurement,
    mirroring how 2a-part-1's own witness replayed ITS pre-fix baseline."""
    verdict, _detail = congruence_with_lexicon_fallback(passage_text)
    if verdict not in ("MET", "UNMET"):
        return None
    sents = _sentences(passage_text)
    resolver = GeneralRecencyEntityResolver(roster)
    goal_holder = None
    for s in sents[:-1]:
        subj = resolver.subject_entity(s)
        if find_desired_state(s) is not None:
            goal_holder = subj
            break
    if goal_holder is None or goal_holder not in roster:
        return None
    return goal_holder


def _pre_part2_never_typed(passage_text, roster):
    """True iff the item is never-typed under the POST-2a-part-1 / PRE-2a-part-2 system (owner path
    typed nothing AND the pre-part-2 fallback also abstains)."""
    if not _owner_path_never_typed(passage_text, roster):
        return False
    return _pre_part2_unify(passage_text, roster) is None


def check_before_after_recovery():
    rows = _load_bank()
    assert len(rows) == 44, f"expected the 44-item goal_bearing_modern_eval_v1 bank, got {len(rows)}"

    before_never_typed_ids = {r["id"] for r in rows if _pre_part2_never_typed(r["text"], r["roster"])}
    n_before = len(before_never_typed_ids)
    assert n_before == EXPECTED_BEFORE_NEVER_TYPED, (
        f"BEFORE (post-2a-part-1/pre-2a-part-2 replay) never-typed count must be "
        f"{EXPECTED_BEFORE_NEVER_TYPED}, got {n_before}: {sorted(before_never_typed_ids)}")

    after_never_typed_ids = set()
    after_pick = {}
    for r in rows:
        try:
            _scored, winners = enumerate_and_score(r["text"], r["roster"], SEED)
            after_pick[r["id"]] = winners[0] if len(winners) == 1 else select_outcome_owner(
                r["text"], r["roster"], SEED)
        except ValueError:
            after_never_typed_ids.add(r["id"])
    n_after = len(after_never_typed_ids)
    assert n_after <= EXPECTED_BEFORE_NEVER_TYPED - MIN_RECOVERED, (
        f"AFTER never-typed count must be <= {EXPECTED_BEFORE_NEVER_TYPED - MIN_RECOVERED} "
        f"(recover >= {MIN_RECOVERED}), got {n_after}")

    recovered_ids = before_never_typed_ids - after_never_typed_ids
    assert len(recovered_ids) >= MIN_RECOVERED, (
        f"must recover >= {MIN_RECOVERED} items, got {len(recovered_ids)}: {sorted(recovered_ids)}")
    # strict-ADD: the fallback can only ever REDUCE never-typed, never add.
    assert after_never_typed_ids.issubset(before_never_typed_ids), (
        f"strict-ADD violation: a previously-typed item became never-typed: "
        f"{sorted(after_never_typed_ids - before_never_typed_ids)}")

    assert TARGET_ID in recovered_ids, f"{TARGET_ID} did not recover"
    gold_by_id = {r["id"]: r["gold_outcome_owner"] for r in rows}
    assert gold_by_id[TARGET_ID] == TARGET_OWNER, (
        f"gold sanity: {TARGET_ID} gold_outcome_owner must be {TARGET_OWNER!r}, "
        f"got {gold_by_id[TARGET_ID]!r}")
    assert after_pick[TARGET_ID] == TARGET_OWNER, (
        f"{TARGET_ID}: expected owner {TARGET_OWNER!r}, got {after_pick[TARGET_ID]!r}")

    print(f"[CHECK before_after_recovery] before_never_typed={n_before}/44 "
          f"after_never_typed={n_after}/44 recovered={sorted(recovered_ids)} "
          f"{TARGET_ID}_owner={after_pick[TARGET_ID]!r} (correct)")
    return {"before_never_typed": n_before, "after_never_typed": n_after,
            "recovered_ids": sorted(recovered_ids), "target_owner": after_pick[TARGET_ID]}


def check_part1_recoveries_unregressed():
    """The three 2a-part-1 recoveries (hunt/dorothy/limal) must still resolve to their correct gold
    owner post-2a-part-2."""
    rows = {r["id"]: r for r in _load_bank()}
    for rid, expected_owner in PART1_RECOVERIES.items():
        r = rows[rid]
        owner = select_outcome_owner(r["text"], r["roster"], SEED)
        assert owner == expected_owner == r["gold_outcome_owner"], (
            f"{rid}: expected {expected_owner!r}, got {owner!r} (2a-part-1 recovery regressed)")
    print(f"[CHECK part1_recoveries_unregressed] {sorted(PART1_RECOVERIES)} all still correct "
          f"post-2a-part-2")
    return {"checked": sorted(PART1_RECOVERIES)}


def check_no_regression_outside_new_recovery():
    """Every item NOT newly recovered by 2a-part-2 (i.e. was resolvable, or still never-typed, under
    the post-2a-part-1/pre-2a-part-2 system) produces the IDENTICAL select_outcome_owner pick before
    vs after this change."""
    def pre_part2_select(passage_text, roster, seed):
        candidates = sorted(roster.keys())
        scored = {}
        any_typed = False
        for c in candidates:
            rs, cid = build_candidate_role_seq(passage_text, roster, c)
            pos = _outcome_pos(rs)
            if pos is None:
                scored[c] = 0.0
                continue
            any_typed = True
            scored[c] = directed_goal_outcome_score(rs, cid, seed, pos)
        if not any_typed:
            return _pre_part2_unify(passage_text, roster)
        max_score = max(scored.values())
        winners = [c for c in candidates if scored[c] == max_score]
        if len(winners) > 1:
            goal_themes = entity_goal_themes(passage_text, roster)
            out_theme = clause_theme(_sentences(passage_text)[-1], roster)
            overlappers = [c for c in winners if goal_themes.get(c, set()) & out_theme]
            if len(overlappers) == 1:
                return overlappers[0]
        return winners[0]

    rows = _load_bank()
    mismatches = []
    n_checked = 0
    for r in rows:
        pre = pre_part2_select(r["text"], r["roster"], SEED)
        if pre is None:
            continue  # never-typed pre-part-2 -> either the newly-recovered item or still never-typed;
                       # both are already covered by check_before_after_recovery's set assertions
        try:
            post = select_outcome_owner(r["text"], r["roster"], SEED)
        except ValueError:
            mismatches.append((r["id"], pre, "RAISED"))
            continue
        n_checked += 1
        if pre != post:
            mismatches.append((r["id"], pre, post))
    assert not mismatches, (
        f"no-regression violated for items resolvable both before+after: {mismatches}")
    print(f"[CHECK no_regression_outside_new_recovery] {n_checked}/44 already-resolvable items "
          f"byte-identical pre- vs post-part-2 pick")
    return {"n_checked": n_checked}


def check_fair_instruments_unchanged():
    """Reuses (imports, does not reimplement) verification/test_goal_owner_select.py's run(): 48/48
    fair instrument + 12/12 multigoal, must stay byte-identical under this strict ADD."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import test_goal_owner_select as FAIR  # noqa: E402
    result = FAIR.run()
    assert result["full_instrument"]["content_total"] == 48
    assert result["multigoal"]["content"] == 12
    print("[CHECK fair_instruments_unchanged] 48/48 fair + 12/12 multigoal reproduced via imported "
          "test_goal_owner_select.run() (byte-identical, unmodified by this strict-ADD)")
    return result


def run():
    r1 = check_before_after_recovery()
    r2 = check_part1_recoveries_unregressed()
    r3 = check_no_regression_outside_new_recovery()
    r4 = check_fair_instruments_unchanged()
    print("[ALL CHECKS PASS] 2a-part-2 speaker-attribution goal-holder fallback: owner "
          "never-typed %d->%d/44 (recovered %s, correct owner=%s), 2a-part-1 recoveries "
          "(hunt/dorothy/limal) unregressed, zero regression elsewhere, fair instruments "
          "unchanged." % (r1["before_never_typed"], r1["after_never_typed"], TARGET_ID,
                           r1["target_owner"]))
    return {"recovery": r1, "part1_unregressed": r2, "no_regression": r3, "fair_instruments": r4}


if __name__ == "__main__":
    run()
