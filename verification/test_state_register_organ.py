"""Scaffold-free organ witness for hdlab/state_register.py (CORE PROMOTED 2026-08-30).

Exercises the spaCy-free tracking + semantic-matching CORE through the promoted hdlab organ (the
parser-dependent extraction stays experiment-side, matching hdlab/location_register.py). Recomputes
from source: per-entity state timeline (had-been / co-states / supersede-on-incompatible) + the
ATL-style graded semantic matcher (synonymy / scalar entailment / typed contrary-vs-contradictory
antonymy guards). NO spaCy import.

Run:  .venv/Scripts/python.exe verification/test_state_register_organ.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.state_register import (
    StateRegister, state_match, incompatible, _contradictory_pair,
    PRIOR, CURRENT, RESULT,
)

n = 0


def ok(cond, msg):
    global n
    assert cond, "FAIL: " + msg
    n += 1
    print("  ok  " + msg)


def main():
    print("[hdlab.state_register organ witness]")

    # --- tracking core (hand-supplied events; the extraction adapter is experiment-side) ---
    reg = StateRegister().fold(["she"], [("state", "she", "ill", CURRENT, 1, 1)], n_clauses=4)
    ok(reg.is_in_state("she", "ill", 2) in (True, "MATCH", 1) or "ill" in reg.state_at("she", 2),
       "a current state (ill) is tracked and holds at a later clause")

    # supersede on an INCOMPATIBLE state; the prior state is remembered via had_been
    reg2 = StateRegister().fold(
        ["door"],
        [("state", "door", "locked", RESULT, 1, 1), ("state", "door", "unlocked", RESULT, 1, 3)],
        n_clauses=5,
    )
    ok("unlocked" in reg2.state_at("door", 4), "an incompatible later state (unlocked) supersedes locked")
    ok("locked" not in reg2.state_at("door", 4), "the superseded state (locked) no longer holds")
    ok("locked" in reg2.had_been("door", 4), "had_been() remembers the earlier state (locked)")

    # co-states that are NOT incompatible persist together (ill + soldier)
    reg3 = StateRegister().fold(
        ["he"],
        [("state", "he", "soldier", PRIOR, 1, 1), ("state", "he", "ill", CURRENT, 1, 2)],
        n_clauses=5,
    )
    st = reg3.state_at("he", 3)
    ok("soldier" in st and "ill" in st, "non-opposing co-states (soldier + ill) both hold")

    # --- the ATL-style graded semantic matcher ---
    ok(state_match("unwell", "ill") == "MATCH", "synonymy: query 'unwell' matches stored 'ill' (WordNet)")
    ok(state_match("broken", "shattered") == "MATCH", "scalar entailment: stored 'shattered' entails query 'broken'")
    ok(state_match("open", "closed") == "NO", "opposites: stored 'closed' holds -> query 'open' does NOT")

    # typed antonymy guard: 'not alive' |= dead (closed-scale) but 'not tall' =/= short (open-scale)
    ok(state_match("dead", "alive", stored_polarity=-1) == "MATCH",
       "typed CONTRADICTORY: stored 'not alive' -> query 'dead' MATCHes (closed scale)")
    ok(state_match("well", "ill", stored_polarity=-1) == "NONE",
       "typed CONTRARY: stored 'not ill' -> query 'well' is NONE, not a flip (open scale, guard on)")
    ok(state_match("well", "ill", stored_polarity=-1, guards=False) == "MATCH",
       "ablation: with the antonymy guard OFF, 'not ill' WRONGLY flips to 'well' (the guard is load-bearing)")

    # --- incompatibility lexicon (opposing groups, not flat exclusion) ---
    ok(incompatible("locked", "unlocked") and incompatible("alive", "dead"),
       "explicit + morphological opposites are incompatible")
    ok(not incompatible("ill", "soldier"), "non-opposing states are NOT incompatible (co-exist)")
    ok(_contradictory_pair("alive", "dead") and not _contradictory_pair("tall", "short"),
       "contradictory (closed) vs contrary (open) antonyms are typed correctly")

    print("\n%d/%d PASS -- hdlab.state_register core recomputed from source (per-entity state timeline: "
          "had-been / co-states / supersede-on-incompatible; ATL graded matcher: synonymy / entailment / "
          "typed antonymy guards; no spaCy)." % (n, n))


if __name__ == "__main__":
    main()
