# WIRE-DON'T-ISLAND PROMOTION WITNESS (2026-08-07). Scaffold-free, tracing=False (no HDC tracing
# anywhere in this module -- the organs under test do not take a tracing flag).
"""verification/verify_path_unification_2a_part1.py -- reproduces the 2a-part-1 PATH-UNIFICATION
FALLBACK contract off the PROMOTED production organ (hdlab.goal_owner_select.enumerate_and_score's
new `_unify_owner_via_polarity_path` branch), against the REAL goal_bearing_modern_eval_v1.jsonl
44-item eval bank (the same bank Director's read-only scratch_vet_owner_attribution_step0.py probes),
never a re-authored toy bank.

WHAT THIS CHECKS (matching the promotion contract):
  (1) BEFORE count: reproduces the PRE-FIX owner-path never-typed count (18/44) by replaying the
      EXACT pre-fix per-candidate loop (build_candidate_role_seq + _outcome_pos over every roster
      candidate, `not any_typed` -> never-typed) -- this is the OLD enumerate_and_score's own inner
      loop, unmodified by this promotion, so re-deriving BEFORE this way needs no git revert.
  (2) AFTER count: the ACTUAL (post-fix) hdlab.goal_owner_select.enumerate_and_score never-typed count
      over the same 44 items, asserted <= 16 (recover >= 2, the pre-VET gate).
  (3) The recovered items (never-typed BEFORE, typed AFTER) each resolve to the CORRECT
      gold_outcome_owner via select_outcome_owner -- no recovered item is wrong.
  (4) The two decisive ids Director's prediction named (onestop_hunt_crowdfunding -> hunt,
      woz_dorothy_kansas_wish -> dorothy) are BOTH in the recovered set with the correct owner
      (whether or not additional items also recover is reported honestly, not required to be exactly
      2 -- the gate is >=2 correct, not ==2).
  (5) NO REGRESSION: every item NOT in the recovered set produces the IDENTICAL select_outcome_owner
      pick before vs after (byte-identical on the whole 44-item bank outside the recovered set) --
      proves the fallback is reached ONLY on the `not any_typed` branch, never perturbing an
      already-typed item.
  (6) The certified fair instruments stay byte-identical: reuses (imports, does not reimplement)
      verification/test_goal_owner_select.py's run() -- 48/48 fair instrument + 12/12 multigoal +
      flip-control, unchanged by this strict-ADD.

HONEST SCOPE: this witness measures the OWNER-SELECTION contract (per this task's brief), not the
full-precision owner-accuracy story on the 44-item bank (many of the 44 items' "correct" picks are
tie-break ALPHABETICAL_FALLBACK luck, a separate, already-documented artifact this promotion does not
touch or claim to fix -- see scratch_vet_owner_attribution_step0.py's own luck-artifact accounting,
unaffected by this change per check (5) above).
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_owner_select import (  # noqa: E402
    select_outcome_owner, enumerate_and_score, build_candidate_role_seq, _outcome_pos,
)

EVAL_BANK = os.path.join(REPO_ROOT, "experiments", "data", "goal_bearing_modern_eval_v1.jsonl")
SEED = 0
EXPECTED_BEFORE_NEVER_TYPED = 18
MIN_RECOVERED = 2
DIRECTOR_PREDICTED = {"onestop_hunt_crowdfunding": "hunt", "woz_dorothy_kansas_wish": "dorothy"}


def _load_bank():
    rows = []
    with open(EVAL_BANK, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _pre_fix_never_typed(passage_text: str, roster: dict) -> bool:
    """Replays the EXACT pre-fix enumerate_and_score inner loop (unmodified building blocks:
    build_candidate_role_seq + _outcome_pos), never invoking the new
    _unify_owner_via_polarity_path fallback -- True iff NO roster candidate's outcome slot is typed
    (the condition that used to raise ValueError before this promotion)."""
    for c in sorted(roster.keys()):
        rs, _cid = build_candidate_role_seq(passage_text, roster, c)
        if _outcome_pos(rs) is not None:
            return False
    return True


def check_before_after_recovery():
    rows = _load_bank()
    assert len(rows) == 44, f"expected the 44-item goal_bearing_modern_eval_v1 bank, got {len(rows)}"

    before_never_typed_ids = set()
    for r in rows:
        if _pre_fix_never_typed(r["text"], r["roster"]):
            before_never_typed_ids.add(r["id"])
    n_before = len(before_never_typed_ids)
    assert n_before == EXPECTED_BEFORE_NEVER_TYPED, (
        f"BEFORE (pre-fix replay) never-typed count must be {EXPECTED_BEFORE_NEVER_TYPED}, "
        f"got {n_before}: {sorted(before_never_typed_ids)}")

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
    # no item that was ALREADY typed before can become never-typed after (strict-ADD: the fallback
    # only ever runs on the `not any_typed` branch, so it can only ever REDUCE never-typed, never add).
    assert after_never_typed_ids.issubset(before_never_typed_ids), (
        f"strict-ADD violation: a previously-typed item became never-typed: "
        f"{sorted(after_never_typed_ids - before_never_typed_ids)}")

    gold_by_id = {r["id"]: r["gold_outcome_owner"] for r in rows}
    recovered_owners = {rid: after_pick[rid] for rid in recovered_ids}
    wrong_recoveries = {rid: (pick, gold_by_id[rid]) for rid, pick in recovered_owners.items()
                        if pick != gold_by_id[rid]}
    assert not wrong_recoveries, f"recovered owner(s) WRONG vs gold: {wrong_recoveries}"

    for rid, expected_owner in DIRECTOR_PREDICTED.items():
        assert rid in recovered_ids, f"Director-predicted recovery {rid!r} did not recover"
        assert recovered_owners[rid] == expected_owner == gold_by_id[rid], (
            f"{rid}: expected owner {expected_owner!r}, got {recovered_owners[rid]!r}")

    print(f"[CHECK before_after_recovery] before_never_typed={n_before}/44 "
          f"after_never_typed={n_after}/44 recovered={sorted(recovered_ids)} "
          f"recovered_owners={recovered_owners} (all correct) "
          f"director_predicted_both_recovered=True")
    return {"before_never_typed": n_before, "after_never_typed": n_after,
            "recovered_ids": sorted(recovered_ids), "recovered_owners": recovered_owners}


def check_no_regression_outside_recovered_set():
    """Every item NOT in the recovered set (i.e. was typed before AND after, or never-typed both
    before and after) produces the IDENTICAL select_outcome_owner pick pre- vs post-fix. Pre-fix pick
    is reproduced via the SAME unmodified build_candidate_role_seq/_outcome_pos primitives plus the
    module's own (untouched) tie-break, mirroring select_outcome_owner's body exactly but skipping the
    new fallback branch -- i.e. calling enumerate_and_score's pre-fix equivalent inline."""
    from hdlab.goal_owner_select import entity_goal_themes, clause_theme, _sentences

    def pre_fix_select(passage_text, roster, seed):
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
            from hdlab.goal_owner_select import directed_goal_outcome_score
            scored[c] = directed_goal_outcome_score(rs, cid, seed, pos)
        if not any_typed:
            return None  # would have raised
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
        pre = pre_fix_select(r["text"], r["roster"], SEED)
        if pre is None:
            continue  # was never-typed before -> not in the "outside recovered set, both-sides-typed" scope
        try:
            post = select_outcome_owner(r["text"], r["roster"], SEED)
        except ValueError:
            mismatches.append((r["id"], pre, "RAISED"))
            continue
        n_checked += 1
        if pre != post:
            mismatches.append((r["id"], pre, post))
    assert not mismatches, f"no-regression violated for items typed both before+after: {mismatches}"
    print(f"[CHECK no_regression_outside_recovered_set] {n_checked}/44 already-typed items "
          f"byte-identical pre- vs post-fix pick")
    return {"n_checked": n_checked}


def check_fair_instruments_unchanged():
    """Reuses (imports, does not reimplement) verification/test_goal_owner_select.py's run(): 48/48
    fair instrument + 12/12 multigoal + flip-control, must stay byte-identical under this strict ADD."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import test_goal_owner_select as FAIR  # noqa: E402
    result = FAIR.run()
    assert result["full_instrument"]["content_total"] == 48
    assert result["multigoal"]["content"] == 12
    print("[CHECK fair_instruments_unchanged] 48/48 fair + 12/12 multigoal reproduced via imported "
          "test_goal_owner_select.run() (byte-identical, unmodified by this promotion)")
    return result


def run():
    r1 = check_before_after_recovery()
    r2 = check_no_regression_outside_recovered_set()
    r3 = check_fair_instruments_unchanged()
    print("[ALL CHECKS PASS] 2a-part-1 path-unification fallback: never-typed 18->%d/44 "
          "(recovered %d, all correct, both Director-predicted ids included), zero regression on "
          "already-typed items, fair instruments unchanged." % (
              r1["after_never_typed"], len(r1["recovered_ids"])))
    return {"recovery": r1, "no_regression": r2, "fair_instruments": r3}


if __name__ == "__main__":
    run()
