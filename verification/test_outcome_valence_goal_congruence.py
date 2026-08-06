# WIRE-DON'T-ISLAND PROMOTION WITNESS (2026-08-06). Scaffold-free, tracing=False (no HDC tracing
# anywhere in this module -- the organ under test does not take a tracing flag).
"""verification/test_outcome_valence_goal_congruence.py -- reproduces the OUTCOME-VALENCE
GOAL-CONGRUENCE contract off the PROMOTED production functions (hdlab.goal_typing.congruence_decision
/ congruence_with_lexicon_fallback / lexicon_predict), not off the experiment cells' own copies. Bank
data and loader helpers are IMPORTED from the certified experiment cells (never re-authored) so this
witness cannot silently drift from the landed record:
  - experiments/exp_outcome_valence_goal_congruence_v1.py (commit 63c71935d, original 10-item bank +
    mechanism origin)
  - experiments/exp_outcome_valence_goal_congruence_v2.py (commit 3ed374148, 26-item expanded bank +
    discourse-entity referent resolution that closed the coverage wall)

Named test_*.py rather than verify_*.py (the sibling promotion-witness naming convention used
elsewhere in this directory, e.g. verify_goal_typing.py) so pytest (python_files = ["test_*.py"],
pyproject.toml) actually COLLECTS this witness into `python verification/run_certification.py` -- a
witness pytest never runs is not a gate. Docstring/structure otherwise follows
verification/test_goal_owner_select.py's promotion-witness convention verbatim (check_* functions
doing the real work, thin test_* wrappers for pytest collection, a `run()`-equivalent `__main__`
block).

Six checks, matching the promotion contract (exp_dev task brief, 2026-08-06):
  (1) core_flip (16 items, families A-J, no referent stress): mechanism_accuracy must be 16/16 (1.0).
  (2) coverage_stress (6 items, families K/L/M: pronoun/synonym/multi-object referent stress):
      accuracy_when_fired must be 6/6 (1.0) -- the discourse-entity referent linker (Tier-1 pronoun
      coref via hdlab.coreference_resolver, Tier-2 shared-feature-similarity organ lifted from
      exp_n11c, 2026-08-06 WIRE-DONT-ISLAND upgrade of the prior hand-authored synonym group)
      closing the coverage wall a plain-string-equality match could not close.
  (3) over-link guard: D-unmet (ECM "wanted his sister to win" vs "his rival won") and M-unmet (a
      same-class distractor clause) must both stay UNMET via referent_mismatch/no_link -- two
      distinct common nouns with no pronoun/synonym relationship (sim(sister,rival)=0.398 stays
      below SIMILARITY_LINK_THRESHOLD=0.50, a genuine measurement not an OOV-fallthrough) must
      never spuriously link.
  (4) precision guard (H/H2 abstain) and positive controls (G/G2 correct), the remaining v2 gates.
  (5) backward-compat: hdlab.goal_owner_select.select_outcome_owner (untouched by this promotion)
      stays 48/48 on the fair instrument -- proves polarity-only outcome-valence changes cannot move
      owner-selection (select_outcome_owner's scoring only inspects has_goal, never n_unmet/n_met).
  (6) v1 regression: v1's original 10-item bank re-verdicts bit-identically under the promoted
      module's expanded CLASS_REGISTRY (proves the v2 register expansion did not silently change v1
      behavior).
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
for _p in (REPO_ROOT, EXPERIMENTS_DIR, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab.goal_typing import (  # noqa: E402
    congruence_decision, congruence_with_lexicon_fallback, self_test as goal_typing_self_test,
)
from hdlab.goal_owner_select import select_outcome_owner  # noqa: E402

# ---- REUSED (imported, not re-authored): certified bank loaders + id sets -------------------------
import exp_outcome_valence_goal_congruence_v1 as V1CELL  # noqa: E402
import exp_outcome_valence_goal_congruence_v2 as V2CELL  # noqa: E402

CORE_FLIP_IDS = V2CELL.CORE_FLIP_IDS          # 16 items, families A-J
COVERAGE_STRESS_IDS = V2CELL.COVERAGE_STRESS_IDS  # 6 items, families K/L/M


def _run_item_promoted(item: dict) -> dict:
    """Byte-identical logic to V2CELL.run_bank_item, with the mechanism call swapped for the
    PROMOTED hdlab.goal_typing.congruence_decision (not V2CELL's own copy)."""
    sents = V2CELL._sentences(item["text"])
    goal_sentences, outcome_sentence = sents[:-1], sents[-1]
    verdict, detail = congruence_decision(goal_sentences, outcome_sentence)
    return dict(id=item["id"], gold=item["gold"], mechanism=verdict, detail=detail,
                matches=(verdict == item["gold"]), fired=(verdict != "NA"))


# ---------------------------------------------------------------------------
# (1) core_flip: 16/16, off the promoted organ
# ---------------------------------------------------------------------------
def check_core_flip_16_of_16():
    rows = V2CELL.load_bank_v2()
    assert len(rows) == 26, f"expected 26-item v2 bank, got {len(rows)}"
    core_rows = [_run_item_promoted(it) for it in rows if it["id"] in CORE_FLIP_IDS]
    assert len(core_rows) == 16, f"expected 16 core_flip items, got {len(core_rows)}"
    n_correct = sum(r["matches"] for r in core_rows)
    assert n_correct == 16, (
        f"promoted hdlab.goal_typing.congruence_decision must score core_flip 16/16, got {n_correct}; "
        f"misses={[r['id'] for r in core_rows if not r['matches']]}")
    print("[CHECK core_flip] 16/16 (promoted hdlab.goal_typing.congruence_decision)")
    return {"core_flip_correct": n_correct, "core_flip_total": 16}


# ---------------------------------------------------------------------------
# (2) coverage_stress: accuracy_when_fired 6/6, off the promoted organ
# ---------------------------------------------------------------------------
def check_coverage_stress_accuracy_when_fired():
    rows = V2CELL.load_bank_v2()
    cov_rows = [_run_item_promoted(it) for it in rows if it["id"] in COVERAGE_STRESS_IDS]
    assert len(cov_rows) == 6, f"expected 6 coverage_stress items, got {len(cov_rows)}"
    fired = [r for r in cov_rows if r["fired"]]
    assert len(fired) == 6, (
        f"expected all 6 coverage_stress items to FIRE (not abstain), got {len(fired)}; "
        f"abstained={[r['id'] for r in cov_rows if not r['fired']]}")
    n_correct = sum(r["matches"] for r in fired)
    assert n_correct == 6, (
        f"promoted organ must score coverage_stress accuracy_when_fired 6/6, got {n_correct}; "
        f"misses={[r['id'] for r in fired if not r['matches']]}")
    # the three decisive flips must each go through the discourse-entity linker, not a literal match
    # that happened to already agree (proves the referent-linking machinery actually fired).
    k_met = next(r for r in cov_rows if r["id"] == "K-met")
    l_met = next(r for r in cov_rows if r["id"] == "L-met")
    m_met = next(r for r in cov_rows if r["id"] == "M-met")
    assert k_met["detail"]["link_tier"] == "pronoun_coref", (
        f"K-met must resolve via pronoun_coref, got {k_met['detail']['link_tier']}")
    assert l_met["detail"]["link_tier"] == "shared_feature", (
        f"L-met must resolve via shared_feature (hdlab.lexical_similarity organ, 2026-08-06 "
        f"upgrade of the prior hand-authored synonym-group tier), got {l_met['detail']['link_tier']}")
    assert m_met["detail"]["link_tier"] == "literal", (
        f"M-met must resolve via literal (2nd candidate, first-match-hijack fix), "
        f"got {m_met['detail']['link_tier']}")
    print("[CHECK coverage_stress] accuracy_when_fired=6/6, fire_rate=6/6 "
          "(K-met=pronoun_coref L-met=shared_feature M-met=literal-2nd-candidate)")
    return {"coverage_stress_correct": n_correct, "coverage_stress_fired": len(fired)}


# ---------------------------------------------------------------------------
# (3) over-link guard: D-unmet and M-unmet stay UNMET (referent_mismatch / no_link)
# ---------------------------------------------------------------------------
def check_over_link_guard():
    rows = {r["id"]: r for r in V2CELL.load_bank_v2()}
    d_unmet = _run_item_promoted(rows["D-unmet"])
    m_unmet = _run_item_promoted(rows["M-unmet"])
    assert d_unmet["mechanism"] == "UNMET" and d_unmet["matches"], (
        f"D-unmet (sister vs rival) must stay UNMET (over-link guard), got {d_unmet['mechanism']} "
        f"({d_unmet['detail']})")
    assert d_unmet["detail"]["reason"] == "referent_mismatch"
    assert m_unmet["mechanism"] == "UNMET" and m_unmet["matches"], (
        f"M-unmet must stay UNMET (over-link guard), got {m_unmet['mechanism']} ({m_unmet['detail']})")
    print(f"[CHECK over_link_guard] D-unmet=UNMET({d_unmet['detail']['reason']}) "
          f"M-unmet=UNMET({m_unmet['detail']['reason']}) (promoted organ)")
    return {"d_unmet": d_unmet["mechanism"], "m_unmet": m_unmet["mechanism"]}


# ---------------------------------------------------------------------------
# (4) precision guard (H/H2 abstain) + positive controls (G/G2 correct)
# ---------------------------------------------------------------------------
def check_precision_guard_and_positive_controls():
    rows = {r["id"]: r for r in V2CELL.load_bank_v2()}
    h = _run_item_promoted(rows["H-abstain"])
    h2 = _run_item_promoted(rows["H2-abstain"])
    g = _run_item_promoted(rows["G-control"])
    g2 = _run_item_promoted(rows["G2-control"])
    assert h["mechanism"] == "NA", f"H-abstain must abstain (NA), got {h['mechanism']}"
    assert h2["mechanism"] == "NA", f"H2-abstain must abstain (NA), got {h2['mechanism']}"
    assert g["matches"], f"G-control must be correct, got {g['mechanism']} (gold={g['gold']})"
    assert g2["matches"], f"G2-control must be correct, got {g2['mechanism']} (gold={g2['gold']})"
    print("[CHECK precision_and_positive_controls] H/H2 abstain=True G/G2 correct=True (promoted organ)")
    return {"h_abstains": True, "h2_abstains": True, "g_correct": True, "g2_correct": True}


# ---------------------------------------------------------------------------
# (5) backward-compat: select_outcome_owner (untouched) stays 48/48
# ---------------------------------------------------------------------------
def check_backward_compat_48_of_48():
    rows = V2CELL.load_fair_bank()
    subset48 = V2CELL.load_48_item_subset(rows)
    assert len(subset48) == 48, f"expected 48-item fair subset, got {len(subset48)}"
    n_correct = 0
    misses = []
    for it in subset48:
        pick = select_outcome_owner(it["text"], it["roster"], seed=0)
        if pick == it["gold_outcome_owner"]:
            n_correct += 1
        else:
            misses.append(it["id"])
    assert n_correct == 48, (
        f"select_outcome_owner (untouched by this promotion) must stay 48/48, got {n_correct}; "
        f"misses={misses}")
    print("[CHECK backward_compat] owner_48_held=True (hdlab.goal_owner_select.select_outcome_owner, "
          "structurally unaffected by outcome-valence polarity)")
    return {"owner_correct": n_correct, "owner_total": 48}


# ---------------------------------------------------------------------------
# (6) v1 regression: v1's original 10-item bank re-verdicts bit-identically
# ---------------------------------------------------------------------------
def check_v1_regression_identical():
    v1_rows = V1CELL.load_bank()
    assert len(v1_rows) == 10, f"expected v1's original 10-item bank, got {len(v1_rows)}"
    mismatches = []
    for row in v1_rows:
        v1_verdict = V1CELL.run_bank_item(row)["mechanism"]
        sents = V1CELL._sentences(row["text"])
        promoted_verdict, _pd = congruence_decision(sents[:-1], sents[-1])
        if promoted_verdict != v1_verdict:
            mismatches.append((row["id"], promoted_verdict, v1_verdict))
    assert not mismatches, f"v1 regression under promoted expanded registry: {mismatches}"
    print(f"[CHECK v1_regression] {len(v1_rows)} items, 0 mismatches under the promoted "
          "(expanded-registry) organ")
    return {"n_checked": len(v1_rows), "mismatches": mismatches}


# ---------------------------------------------------------------------------
# pytest collection wrappers
# ---------------------------------------------------------------------------
def test_core_flip_16_of_16():
    check_core_flip_16_of_16()


def test_coverage_stress_accuracy_when_fired_1_0():
    check_coverage_stress_accuracy_when_fired()


def test_over_link_guard_holds():
    check_over_link_guard()


def test_precision_guard_and_positive_controls():
    check_precision_guard_and_positive_controls()


def test_backward_compat_owner_48_of_48():
    check_backward_compat_48_of_48()


def test_v1_regression_identical():
    check_v1_regression_identical()


def test_abstain_falls_back_to_lexicon():
    """Theme-mismatch ABSTAIN must fall back to the V2_OUTCOME_UNMET/_MET lexicon end-to-end (the
    strict-ADD contract), not merely abstain and stop."""
    verdict, detail = congruence_with_lexicon_fallback(
        "Owen wanted to open the greenhouse before winter came. The gardener reached the market.")
    assert verdict == "MET" and detail["reason"] == "abstain_fallback_to_lexicon", (
        f"expected fallback to lexicon MET (via 'reached'), got {verdict} ({detail})")


def test_module_self_test_green():
    res = goal_typing_self_test()
    ov = res["outcome_valence"]
    assert ov["flip_unmet"] == "UNMET" and ov["flip_met"] == "MET"
    assert ov["pronoun_referent_met"] == "MET"
    assert ov["over_link_guard_unmet"] == "UNMET"
    assert ov["theme_mismatch_abstain"] == "NA"
    assert ov["v1_regression_mismatches"] == []


def run():
    r1 = check_core_flip_16_of_16()
    r2 = check_coverage_stress_accuracy_when_fired()
    r3 = check_over_link_guard()
    r4 = check_precision_guard_and_positive_controls()
    r5 = check_backward_compat_48_of_48()
    r6 = check_v1_regression_identical()
    print("[ALL CHECKS PASS] hdlab/goal_typing.py outcome-valence goal-congruence reproduces "
          "core_flip 16/16 + coverage_stress accuracy_when_fired 6/6 + over-link guard + "
          "precision/positive controls + owner_48_held + v1 regression 0 mismatches "
          "(byte-identical promoted mechanism).")
    return {"core_flip": r1, "coverage_stress": r2, "over_link_guard": r3,
            "precision_and_controls": r4, "backward_compat": r5, "v1_regression": r6}


if __name__ == "__main__":
    run()
