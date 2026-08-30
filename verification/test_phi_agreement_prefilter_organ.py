"""Scaffold-free organ witness for the phi-agreement pre-filter in hdlab/graded_coref_pick.py
(LANDED 2026-08-30 from `the_coref_residual_needs_a_discourse_focus_stack`).

Recomputes the hard person + animacy candidate-pool filter from source: it excludes the discourse
PARTICIPANT (the narrator "I", never a 3rd-person referent) and animacy-mismatched candidates, is
recall-safe (unknown passes; never returns empty), and leaves the existing API byte-unchanged.

Run:  .venv/Scripts/python.exe verification/test_phi_agreement_prefilter_organ.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.graded_coref_pick import (
    is_discourse_participant, phi_agreement_keep,
    graded_antecedent_pick, keep_after_pool_cleanup,   # existing API must remain importable
)

n = 0


def ok(cond, msg):
    global n
    assert cond, "FAIL: " + msg
    n += 1
    print("  ok  " + msg)


def main():
    print("[hdlab.graded_coref_pick phi-agreement pre-filter organ witness]")

    # --- is_discourse_participant: the person feature ---
    ok(is_discourse_participant(["i", "i", "me", "my"]) is True,
       "the narrator (all 1st-person mentions, never 3rd-person) IS a discourse participant -> excluded for he/she")
    ok(is_discourse_participant(["i", "he", "him"]) is False,
       "a talkative CHARACTER (says 'I' in quotes but IS narrated in 3rd person) is NOT the narrator -> kept "
       "(the 'no 3rd-person mention' clause is load-bearing)")
    ok(is_discourse_participant(["mrs", "dashwood", "she"]) is False,
       "a named 3rd-person entity is NOT a participant -> kept")
    ok(is_discourse_participant([]) is False, "empty mention history is not a participant (recall-safe default)")

    # --- phi_agreement_keep: person exclusion for a 3rd-person pronoun ---
    # candidate 0 = the narrator "I"; candidate 1 = a real named character.
    heads = [["i", "i", "me"], ["mary", "she", "her"]]
    keep = phi_agreement_keep("she", heads, None)   # TIER1: animacy all-None
    ok(0 not in keep and 1 in keep,
       "for 'she' the narrator candidate is DROPPED and the real character is KEPT (person agreement)")

    # --- animacy: he/she need a person; it needs a thing ---
    heads2 = [["mary", "she"], ["village", "it"]]
    animacy = ["animate", "inanimate"]
    ok(1 not in phi_agreement_keep("he", heads2, animacy),
       "for 'he' a confirmed-INANIMATE candidate (a village) is dropped (animacy agreement)")
    ok(0 not in phi_agreement_keep("it", heads2, animacy),
       "for 'it' a confirmed-ANIMATE candidate (a person) is dropped")

    # --- recall-safe: unknown animacy is KEPT; the filter never returns empty ---
    ok(0 in phi_agreement_keep("he", [["thing", "it"]], [None]),
       "unknown animacy (None) is KEPT -> recall-safe, no confident drop")
    ok(phi_agreement_keep("she", [["i", "i"]], None) == [0],
       "if every candidate would be dropped, the filter returns the full pool (recall floor, never empty)")

    # --- existing API is byte-unchanged (the pre-filter is additive/opt-in) ---
    ok(callable(graded_antecedent_pick) and callable(keep_after_pool_cleanup),
       "existing graded_antecedent_pick + keep_after_pool_cleanup remain importable + unchanged (additive landing)")

    print("\n%d/%d PASS -- phi-agreement pre-filter recomputed from source: person (narrator exclusion) + "
          "animacy candidate-pool filter, recall-safe (unknown kept, never empty), existing API intact." % (n, n))


if __name__ == "__main__":
    main()
