# WIRE-DON'T-ISLAND PROMOTION WITNESS (2026-08-09). Scaffold-free, tracing=False (the organ under
# test takes no HDC tracing flag).
"""verification/test_direction_b_union_wire.py -- witness for the UNION OOV-recovery channel
(hdlab.goal_achievement.utility_channel_union_grounded, M2 result-type + M1 idiom + fork-A relation,
precedence resulttype -> relation -> idiom_fallback, plus fork-A's own no-active-attribute
RELATION_LINK fallback) AND its strict-ADD wiring into goal_achievement_verdict.

See hdlab/goal_achievement.py's `goal_achievement_verdict` docstring for the wiring design, and
experiments/exp_direction_b_union_wire_v1.py for the full DesireDB measurement this promotion is
gated on (WIRE_DECISION=True, commit landed data/exp_direction_b_union_wire_v1/metrics.json):

  PRIMARY cohort (n=22, 8 gold-Unfulfilled): union recovery 5/8=0.625 vs best single sub-mechanism
    (M2 resulttype) 3/8=0.375 -- genuinely additive (exactly the SET UNION of what each of the 3
    sub-mechanisms individually recovers, no interference, no double-counting losses).
  BREADTH context (900-row draw, cohort n=152, 37 gold-Unfulfilled): union recovery 10/37=0.2703 vs
    M2-alone 9/37=0.2432, M1-alone 0/37, relation-alone 3/37.
  Full-bench composed macro-F1 (base-alone vs union-wired): n=160 0.6623 -> 0.6875 (+0.0252), n=80
    0.6992 -> 0.7248 (+0.0256) -- NO REGRESSION either scale.
  Pairscramble (wrong-goal cue): PRIMARY |scr-i|=0.0000 (collapses), |scr-mech|=0.1818 (not-leak);
    BREADTH-at-scale delta=0.0461 (collapses).
  harness_validity_check (n=80, pre-wire pipeline): measured_macro_f1=0.6992 vs documented 0.686
    (delta=0.0132, within 0.03 tolerance) -- the '0.686/0.699' pair this arc's cells cite.

This witness CANNOT reproduce those DesireDB numbers (DesireDB.csv is not committed -- same
constraint as verification/test_goal_achievement.py), so it asserts the per-mechanism precedence
behavior + the wiring's cohort-membership-stability guarantee + determinism instead, using the
EXACT hand-authored flagship cases hdlab.goal_achievement.self_test_union_grounded_channel()
verified this session (MEASURED@this session's design probe, see that function's docstring).

Four checks:
  (1) PRECEDENCE MECHANISM-FIRES: each of the 3 precedence branches (resulttype-first,
      relation-second, idiom-fallback-last) plus the no-active-attribute RELATION_LINK fallback
      (both its learned-classifier and dictionary-lookup sub-paths) fires correctly + the plain
      3-channel WordNet-only channel genuinely abstains on the same inputs (proving the union adds
      real coverage, not a redundant re-derivation).
  (2) WIRING ENGAGES + STAYS STRICT-ADD: goal_achievement_verdict recovers a case the pre-wire
      3-channel pipeline would default to MAJORITY_CLASS on, WHILE `channel` stays 'majority' (the
      cohort-membership-stability guarantee -- any code filtering on channel=='majority' keeps
      selecting the identical cohort population) and a non-majority case (relation/valence/contrast
      already decided) is provably UNTOUCHED by the union.
  (3) PAIRSCRAMBLE (wrong-goal cue) does not reproduce a correct recovery via the wired pipeline.
  (4) DETERMINISM: same (desire, outcome) -> byte-identical wired result dict, twice.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_achievement import (  # noqa: E402
    goal_achievement_verdict, utility_channel_trace_union_grounded, utility_channel_union_grounded,
    utility_channel_trace, activate_attributes, self_test_union_grounded_channel,
)
from hdlab import result_type_induction as _rti  # noqa: E402
from hdlab import goal_outcome_relation as _gor  # noqa: E402

# (desire, outcome, expected_union_verdict, expected_secondary_source_or_path)
_RT_NAME, _RT_HYP = _rti.get_induced_hypothesis()
_REL_NAME, _REL_HYP = _gor.get_induced_hypothesis()

CASES = [
    # resulttype precedence (1st in line; ALSO matches idiom's own 'uh_no' pattern -- proves
    # precedence, not merely standalone firing).
    ("My girl [wanted to] act it out in real life, even wanting to move to England! Uh. No.",
     "Uh. No. Uh. No.", "Unfulfilled", "resulttype"),
    # relation precedence (2nd in line; resulttype genuinely abstains on this outcome).
    ("I wanted to stay busy and finish the project.", "She went shopping instead all afternoon.",
     "Fulfilled", "relation"),
    # idiom fallback (3rd/last in line; resulttype AND relation both genuinely abstain).
    ("I wanted to win the lottery.", "It was a piece of cake and things came together nicely.",
     "Fulfilled", "idiom_fallback"),
]

# no-active-attribute RELATION_LINK fallback (fork-A's own flagships; a DIFFERENT code path from the
# 3-way precedence layer above -- the ONE place the union's coverage is a strict superset of M1/M2's
# reach, not just a precedence extension of the shared per-attribute layer).
FALLBACK_CASES = [
    ("I wanted to know why he left.", "We discussed it at length last night.", "Fulfilled"),
    ("She wanted to be out and about.", "In the end everyone backed off and stayed home instead.",
     "Unfulfilled"),
]


def check_precedence_mechanism_fires():
    for desire, outcome, exp_v, exp_source in CASES:
        plain = utility_channel_trace(desire, outcome)
        assert plain["verdict"] is None, (
            f"fixture assumption broken: plain WordNet-only channel did not abstain for {outcome!r}: {plain}")
        u = utility_channel_trace_union_grounded(desire, outcome, _RT_NAME, _RT_HYP, _REL_NAME, _REL_HYP)
        assert u["verdict"] == exp_v, f"union verdict {u['verdict']!r} != {exp_v!r} for {outcome!r} ({u})"
        sources = {a: info["grounding_trace"]["secondary_source"] for a, info in u["active"].items()}
        assert all(s == exp_source for s in sources.values()), (
            f"PRECEDENCE FAILURE: expected all-{exp_source!r} for {outcome!r}, got {sources}")
    for desire, outcome, exp_v in FALLBACK_CASES:
        assert activate_attributes(desire) == {}, f"fixture assumption broken: an ATTRIBUTE activated on {desire!r}"
        u = utility_channel_trace_union_grounded(desire, outcome, _RT_NAME, _RT_HYP, _REL_NAME, _REL_HYP)
        assert u["verdict"] == exp_v, f"RELATION_LINK fallback verdict {u['verdict']!r} != {exp_v!r} ({u})"
        assert u["active"]["RELATION_LINK"]["path"] == "relation_link_fallback", u
    print(f"[CHECK precedence_mechanism_fires] {len(CASES)} precedence cases (resulttype/relation/"
          f"idiom_fallback) + {len(FALLBACK_CASES)} RELATION_LINK fallback cases: correct verdict via "
          f"expected source, plain channel abstains on all precedence cases")
    return {"n_precedence": len(CASES), "n_fallback": len(FALLBACK_CASES)}


def check_wiring_engages_and_strict_add():
    # (a) a majority-abstain case the pre-wire pipeline would default to MAJORITY_CLASS ('Fulfilled')
    # on: the wired goal_achievement_verdict must recover the union's answer, WHILE `channel` stays
    # 'majority' (cohort-membership-stability guarantee).
    desire, outcome = CASES[0][0], CASES[0][1]
    r = goal_achievement_verdict(desire, outcome)
    assert r["channel"] == "majority", (
        f"COHORT-STABILITY FAILURE: channel {r['channel']!r} != 'majority' -- wiring must never "
        f"overwrite `channel` (any code filtering on channel=='majority' would silently see a "
        f"different cohort): {r}")
    assert r["verdict"] == "Unfulfilled", f"WIRING DID NOT ENGAGE: {r}"
    assert r["trace"]["union_oov_recovery_fired"] is True, r
    assert r["trace"]["union_verdict"] == "Unfulfilled", r
    assert r["trace"]["base"] == "Fulfilled", (  # the PRE-union base was still MAJORITY_CLASS
        f"fixture assumption broken: base trace should still record the pre-union majority default: {r}")

    # (b) a case where relation_channel already decided (channel != 'majority') must be COMPLETELY
    # UNTOUCHED by the union -- strict-ADD, zero risk to the existing 3-channel precedence.
    r2 = goal_achievement_verdict("I wanted to save him.", "But I couldn't.")
    assert r2["channel"].startswith("relation"), f"fixture assumption broken: {r2}"
    assert "union_oov_recovery_fired" not in r2["trace"], (
        f"STRICT-ADD VIOLATION: union fields present on a non-majority-channel result: {r2}")

    # (c) a case where valence_channel already decided must ALSO be untouched.
    r3 = goal_achievement_verdict("I wanted a good day.", "It was wonderful and I felt so happy.")
    assert r3["channel"] == "valence", f"fixture assumption broken: {r3}"
    assert "union_oov_recovery_fired" not in r3["trace"], (
        f"STRICT-ADD VIOLATION: union fields present on a non-majority-channel result: {r3}")

    print("[CHECK wiring_engages_and_strict_add] wiring recovers a majority-abstain case while "
          "channel stays 'majority' (cohort-stable); relation/valence-decided cases untouched")
    return {"wired_case_verdict": r["verdict"], "wired_case_channel": r["channel"]}


def check_pairscramble():
    desire, outcome = CASES[1][0], CASES[1][1]  # relation-precedence case
    real_active = activate_attributes(desire)
    scramble_desire = "I wanted to buy a new bike."
    scrambled = utility_channel_union_grounded(scramble_desire, outcome, _RT_NAME, _RT_HYP, _REL_NAME, _REL_HYP)
    assert scrambled != "Fulfilled" or activate_attributes(scramble_desire) != real_active, (
        f"SCRAMBLE-CONTROL AMBIGUOUS: scrambled-cue verdict={scrambled!r} reproduced the correct "
        f"union pick with an IDENTICAL activation set to the real goal")
    print(f"[CHECK pairscramble] wrong-goal cue verdict={scrambled!r} (real pick was 'Fulfilled') -- "
          f"does not silently reproduce the goal-conditioned recovery")
    return {"scrambled_verdict": scrambled}


def check_determinism():
    for desire, outcome, _v, _s in CASES:
        a = goal_achievement_verdict(desire, outcome)
        b = goal_achievement_verdict(desire, outcome)
        assert a == b, f"non-deterministic wired result on {outcome!r}: {a!r} != {b!r}"
    print(f"[CHECK determinism] {len(CASES)} wired cases stable across repeated calls")
    return {"n": len(CASES)}


def test_precedence_mechanism_fires():
    check_precedence_mechanism_fires()


def test_module_self_test_passes():
    # the module's own embedded self-test (broader coverage, same discipline) must pass.
    r = self_test_union_grounded_channel()
    assert r["case1_resulttype_precedence"]["verdict"] == "Unfulfilled"
    assert r["case2_relation_precedence"]["verdict"] == "Fulfilled"
    assert r["case3_idiom_fallback"]["verdict"] == "Fulfilled"


def test_wiring_engages_and_strict_add():
    check_wiring_engages_and_strict_add()


def test_pairscramble():
    check_pairscramble()


def test_determinism():
    check_determinism()


def run():
    r1 = check_precedence_mechanism_fires()
    r2 = check_wiring_engages_and_strict_add()
    r3 = check_pairscramble()
    r4 = check_determinism()
    print("ALL CHECKS PASSED (tracing=False)")
    return {"precedence_mechanism_fires": r1, "wiring_engages_and_strict_add": r2,
            "pairscramble": r3, "determinism": r4}


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, default=str))
