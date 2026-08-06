# WIRE-DON'T-ISLAND PROMOTION WITNESS (2026-08-05). Scaffold-free, tracing=False (no HDC tracing
# anywhere in this module -- the organ under test does not take a tracing flag).
"""verification/test_goal_owner_select.py -- reproduces the full goal-owner OUTCOME-SLOT SELECTOR
contract off the PROMOTED production function (hdlab.goal_owner_select.select_outcome_owner), not
off the experiment cells' own enumerate_and_select / enumerate_and_select_coherence. Bank data and
baseline/loader helpers are IMPORTED from the certified experiment cells (never re-authored) so this
witness cannot silently drift from the landed record:
  - experiments/exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1.py (commit b1b1ce460,
    the candidate-gen + argmax organ: primacy-bank loader, recency-trap regression-check harness)
  - experiments/exp_c5_multigoal_content_coherence_tiebreak_v1.py (commit 6961f5b49, the
    content-coherence tie-break: multi-goal cue-conflict bank loader)

Named test_*.py rather than verify_*.py (the sibling promotion-witness naming convention used
elsewhere in this directory, e.g. verify_goal_typing.py) so pytest (python_files = ["test_*.py"],
pyproject.toml) actually COLLECTS this witness into `python verification/run_certification.py` --
a witness pytest never runs is not a gate. Docstring/structure otherwise follows
verify_goal_typing.py's promotion-witness convention verbatim (check_* functions doing the real
work, thin test_* wrappers for pytest collection, a `run()`-equivalent `__main__` block).

Three checks, matching the promotion contract (exp_dev task brief, 2026-08-05):
  (1) full 48-item fair instrument (primacy ep 12 + ai 8, recency-trap divergent ep 18 + ai 10):
      select_outcome_owner (the PROMOTED selector, WITH the content-coherence tie-break) must score
      48/48; the same enumeration WITHOUT the tie-break (sorted-order fallback on ties) must score
      47/48 and be a strict subset of the 48 -- proves the tie-break is exactly what closes the gap.
  (2) multi-goal cue-conflict bank (12 items, 6 families x base/flip): content-coherence must score
      12/12; the tie-break-off path must score 6/12 (chance-level on a genuine tie).
  (3) flip-control: within every family, the base-variant pick and the flip-variant pick DIFFER
      (proves the tie-break is driven by THEME CONTENT, not entity identity/position).
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
for _p in (REPO_ROOT, EXPERIMENTS_DIR, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab.goal_owner_select import select_outcome_owner, enumerate_and_score  # noqa: E402

# ---- REUSED (imported, not re-authored): certified bank loaders + baseline harness pieces --------
import exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1 as PARENT  # noqa: E402
import exp_c5_multigoal_content_coherence_tiebreak_v1 as TIEBREAK  # noqa: E402

SEED = 0  # the organ's has_goal/theme signals are seed-invariant (asserted by TIEBREAK's own
          # seed_invariant check, commit 6961f5b49); SEED=0 is sufficient for this witness.


def _positional_pick(passage_text: str, roster: dict, seed: int) -> str:
    """The selector WITHOUT the content-coherence tie-break: enumerate + argmax + sorted-order
    fallback on ties -- the exact 47/48 / 6/12 baseline the tie-break promotion improved on."""
    _scored, winners = enumerate_and_score(passage_text, roster, seed)
    return winners[0]


def load_full_instrument():
    """The 48-item fair instrument, exactly as PARENT/TIEBREAK gate it: primacy ep(12)+ai(8) all
    items; recency-trap ep+ai DIVERGENT subset only (i.e. the recency positional baseline is wrong).
    Reused loaders/baseline, not re-authored."""
    items = []
    for vt in ("explicit_psych", "action_implied"):
        items.extend(PARENT.load_primacy(vt))
    for vt in ("explicit_psych", "action_implied"):
        core, _twins = PARENT.PREVMOD.load_bank(vt)
        for it in core:
            rec = PARENT.PREVMOD.resolve_outcome_recency_positional(it)
            if rec != it["gold_outcome_owner"]:
                items.append(it)
    return items


# ---------------------------------------------------------------------------
# (1) full instrument: content=48/48, positional(tiebreak-off)=47/48, no regression
# ---------------------------------------------------------------------------
def check_full_instrument_48_of_48():
    items = load_full_instrument()
    assert len(items) == 48, f"expected 48-item fair instrument, got {len(items)}"
    content_correct, positional_correct = set(), set()
    for it in items:
        gold = it["gold_outcome_owner"]
        c = select_outcome_owner(it["text"], it["roster"], SEED)
        p = _positional_pick(it["text"], it["roster"], SEED)
        if c == gold:
            content_correct.add(it["id"])
        if p == gold:
            positional_correct.add(it["id"])
    assert len(content_correct) == 48, (
        f"select_outcome_owner (promoted, with tie-break) must be 48/48, got {len(content_correct)}; "
        f"misses={sorted({it['id'] for it in items} - content_correct)}")
    assert len(positional_correct) == 47, (
        f"tie-break-off path must reproduce the pre-tiebreak 47/48, got {len(positional_correct)}")
    assert positional_correct.issubset(content_correct), (
        "content-coherence tie-break must not regress any item the positional path already got right")
    assert (content_correct - positional_correct) == {"t24_tom_boat_foil_sid"}, (
        f"the tie-break must fix exactly t24, got {sorted(content_correct - positional_correct)}")
    print("[CHECK full_instrument] content=48/48 positional=47/48 newly_fixed=[t24] no_regression=True "
          "(promoted hdlab.goal_owner_select.select_outcome_owner)")
    return {"content_total": len(content_correct), "positional_total": len(positional_correct)}


# ---------------------------------------------------------------------------
# (2) multi-goal cue-conflict bank: content=12/12, positional(tiebreak-off)=6/12 (chance)
# ---------------------------------------------------------------------------
def check_multigoal_12_of_12():
    mg = TIEBREAK.load_multigoal()
    assert len(mg) == 12, f"expected 12-item multi-goal bank, got {len(mg)}"
    n_content = n_positional = 0
    for it in mg:
        gold = it["gold_outcome_owner"]
        c = select_outcome_owner(it["text"], it["roster"], SEED)
        p = _positional_pick(it["text"], it["roster"], SEED)
        n_content += int(c == gold)
        n_positional += int(p == gold)
    assert n_content == 12, f"multigoal content-coherence must be 12/12, got {n_content}"
    assert n_positional == 6, (
        f"tie-break-off path must reproduce the chance-level 6/12, got {n_positional}")
    print(f"[CHECK multigoal] content=12/12 positional=6/12 (promoted selector, {len(mg)} items)")
    return {"content": n_content, "positional": n_positional}


# ---------------------------------------------------------------------------
# (3) flip-control: base/flip picks correct AND differ, within every family
# ---------------------------------------------------------------------------
def check_flip_control():
    mg = TIEBREAK.load_multigoal()
    fams: dict = {}
    for it in mg:
        fams.setdefault(it["family"], {})[it["variant"]] = it
    assert len(fams) == 6, f"expected 6 families, got {len(fams)}"
    for fam, vv in sorted(fams.items()):
        assert "base" in vv and "flip" in vv, f"family {fam} missing base/flip variant"
        b, f = vv["base"], vv["flip"]
        b_pick = select_outcome_owner(b["text"], b["roster"], SEED)
        f_pick = select_outcome_owner(f["text"], f["roster"], SEED)
        assert b_pick == b["gold_outcome_owner"], (
            f"family {fam} base: expected {b['gold_outcome_owner']!r}, got {b_pick!r}")
        assert f_pick == f["gold_outcome_owner"], (
            f"family {fam} flip: expected {f['gold_outcome_owner']!r}, got {f_pick!r}")
        assert b_pick != f_pick, (
            f"family {fam}: base and flip picks must DIFFER (theme-driven, not identity/position): "
            f"base={b_pick!r} flip={f_pick!r}")
    print(f"[CHECK flip_control] all {len(fams)} families flip under the promoted selector "
          "(theme-content driven, not position/identity)")
    return {"n_families": len(fams)}


# ---------------------------------------------------------------------------
# pytest collection wrappers
# ---------------------------------------------------------------------------
def test_full_fair_instrument_48_of_48():
    check_full_instrument_48_of_48()


def test_multigoal_content_coherence_12_of_12():
    check_multigoal_12_of_12()


def test_flip_control_all_families_flip():
    check_flip_control()


def test_module_self_test_green():
    from hdlab.goal_owner_select import self_test
    res = self_test()
    assert res["adopt"] == "content"
    assert res["t24_owner"] == "tom"
    assert res["p01_owner"] == "amy"


def run():
    r1 = check_full_instrument_48_of_48()
    r2 = check_multigoal_12_of_12()
    r3 = check_flip_control()
    print("[ALL CHECKS PASS] hdlab/goal_owner_select.select_outcome_owner reproduces 48/48 fair + "
          "12/12 multigoal + flip-control (byte-identical promoted mechanism).")
    return {"full_instrument": r1, "multigoal": r2, "flip_control": r3}


if __name__ == "__main__":
    run()
