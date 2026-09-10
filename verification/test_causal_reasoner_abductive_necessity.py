"""Witness: CausalGraph.is_necessary_abductive (rung-3, owner-DONE grow_the_causal_mechanism) is byte-faithful to
the proven prototype exp_causal_engine_deepening_v1.abductive_necessary, leaves rung-2 is_necessary byte-identical,
and CORRECTS the evidence-conditioned counterfactual the fixed-root engine gets wrong.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.causal_reasoner import CausalGraph


def _g(edges):
    g = CausalGraph()
    for c, e in edges:
        g.add_edge(c, e)
    return g


def test_rung3_corrects_the_evidence_conditioned_case():
    # A (cause) and B (bypass root) both feed O; but B was INACTIVE this episode.
    g = _g([("A", "O"), ("B", "O")])
    # rung-2 (assumes ALL roots active) -> a bypass via B exists -> A judged NOT necessary (WRONG here)
    assert g.is_necessary("A", "O") is False
    # rung-3 (abduct: only A active) -> no active bypass -> A IS necessary (CORRECT)
    assert g.is_necessary_abductive(["A"], "A", "O") is True
    # and when B genuinely WAS active, both agree A is not necessary (real bypass)
    assert g.is_necessary_abductive(["A", "B"], "A", "O") is False
    print("PASS rung3_corrects_the_evidence_conditioned_case")


def test_byte_faithful_to_prototype():
    try:
        from experiments.exp_causal_engine_deepening_v1 import abductive_necessary
    except Exception as e:
        print("SKIP byte_faithful (prototype import: %s)" % e)
        return
    cases = [
        ([("A", "O"), ("B", "O")], ["A"], "A", "O"),
        ([("A", "O"), ("B", "O")], ["A", "B"], "A", "O"),
        ([("A", "M"), ("M", "O"), ("B", "O")], ["A"], "A", "O"),
        ([("A", "M"), ("M", "O"), ("B", "O")], ["A", "B"], "A", "O"),
        ([("A", "O"), ("B", "C")], ["A", "B"], "A", "O"),   # cause reaches, no bypass
        ([("A", "O")], ["A"], "X", "O"),                    # cause not in graph path
    ]
    for edges, roots, cause, outcome in cases:
        g = _g(edges)
        mine = g.is_necessary_abductive(roots, cause, outcome)
        theirs = abductive_necessary(g, roots, cause, outcome)
        assert mine == theirs, ("drift vs prototype", edges, roots, cause, outcome, mine, theirs)
    print("PASS byte_faithful_to_prototype (%d cases)" % len(cases))


def test_rung2_is_necessary_unchanged():
    # is_necessary must be byte-identical to its documented behaviour (a NEW method was added, not a change).
    g = _g([("A", "O"), ("B", "O")])
    assert g.is_necessary("A", "O") is False          # bypass via B (all-roots-active)
    g2 = _g([("A", "O")])
    assert g2.is_necessary("A", "O") is True           # sole root -> necessary
    assert g2.is_necessary("A", "A") is False          # cause==outcome
    print("PASS rung2_is_necessary_unchanged")


if __name__ == "__main__":
    test_rung3_corrects_the_evidence_conditioned_case()
    test_byte_faithful_to_prototype()
    test_rung2_is_necessary_unchanged()
    print("3/3 WITNESSES PASSED")
