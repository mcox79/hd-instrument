"""Scaffold-free witness for hdlab.gather_reason (the promoted GATHER + REASON module,
2026-08-11 WIRE-don't-island promotion out of
experiments/exp_state_of_mind_relevance_gather_reasoning_union_v1.py -- see
hdlab/gather_reason.py module docstring).

Re-runs hdlab.gather_reason.self_test() (the module's own real-code-path self-test, which
reproduces the source cell's run_self_test() fixture through the generalized API plus a
direct restrict_hop1_to load-bearing check) as the primary pass/fail signal, then asserts each
of its reported sub-properties directly so a future regression in the module's own self_test
return shape cannot silently mask a real failure.

Passes with tracing=False (no trace bus configured anywhere in this file; hdlab.tracing.emit
is a no-op by default -- nothing here opts in).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import torch  # noqa: E402

import hdlab.gather_reason as gather_reason  # noqa: E402
from hdlab.kg_traversal import KGStore  # noqa: E402
from hdlab.situation_model_accumulate import RelationRegister, unit_phase_vec  # noqa: E402


def test_module_self_test_passes() -> None:
    """The module's own self-test (real KGStore + real cleanup_family.iterative_attractor +
    real RelationRegister objects, mirrors the source cell's run_self_test()) must pass and
    report every expected property."""
    result = gather_reason.self_test()
    assert result["n_ent"] == 7, result
    assert result["ca3_gathered"] == ["material0"], result
    assert result["blind_top1_idx"] == result["gold_idx"], result
    assert result["cued_top1_idx"] == result["gold_idx"], result
    assert result["restrict_hop1_to_load_bearing"] is True, result


def test_ca3_relevance_gather_is_query_conditioned() -> None:
    """(a) ca3_relevance_gather must recover DIFFERENT items for DIFFERENT query vectors drawn
    from the SAME codebook -- proving the peel-loop is genuinely conditioned on the query, not
    returning a fixed/first item regardless of input (a trivial-implementation failure mode)."""
    d = 512
    gen = torch.Generator().manual_seed(4242)
    names_to_vecs = {n: unit_phase_vec(d, gen) for n in ["alpha", "beta", "gamma", "delta"]}
    names, codebook = gather_reason.build_codebook(names_to_vecs)

    q_alpha = gather_reason.real_to_concat(names_to_vecs["alpha"])
    q_gamma = gather_reason.real_to_concat(names_to_vecs["gamma"])
    picked_alpha = gather_reason.ca3_relevance_gather(q_alpha, names, codebook, k_peel=3)
    picked_gamma = gather_reason.ca3_relevance_gather(q_gamma, names, codebook, k_peel=3)
    assert picked_alpha == ["alpha"], picked_alpha
    assert picked_gamma == ["gamma"], picked_gamma
    assert picked_alpha != picked_gamma, "gather is query-conditioned; must differ across queries"


def test_fanout_two_hop_restriction_changes_ranking() -> None:
    """(b) fanout_two_hop's restrict_hop1_to parameter must actually change which entities are
    reachable -- a sentinel-style direct check (not routed through self_test()) using a fresh,
    independently-constructed fixture so this test does not merely re-exercise the module's own
    internal self-test fixture under a different name."""
    n_ent = 5   # s, m_good, m_bad, o_good, o_bad
    S, M_GOOD, M_BAD, O_GOOD, O_BAD = range(n_ent)
    gen1 = torch.Generator().manual_seed(11)
    hop1 = KGStore(n_ent=n_ent, n_rel=2, n_dim=1024, generator=gen1)
    hop1.ingest_triples(torch.tensor([[S, 0, M_GOOD], [S, 0, M_BAD]], dtype=torch.long))
    gen2 = torch.Generator().manual_seed(11)
    hop2 = KGStore(n_ent=n_ent, n_rel=2, n_dim=1024, generator=gen2)
    hop2.ingest_triples(torch.tensor([[M_GOOD, 1, O_GOOD], [M_BAD, 1, O_BAD]], dtype=torch.long))

    ranked_unrestricted = gather_reason.fanout_two_hop(hop1, hop2, S, 0, 1, k1=5, k2=5,
                                                        n_ent=n_ent, restrict_hop1_to=None)
    ranked_restricted = gather_reason.fanout_two_hop(hop1, hop2, S, 0, 1, k1=5, k2=5,
                                                      n_ent=n_ent, restrict_hop1_to={M_GOOD})

    unrestricted_top1 = gather_reason.top1(ranked_unrestricted)
    restricted_top1 = gather_reason.top1(ranked_restricted)
    assert unrestricted_top1 in (O_GOOD, O_BAD), ranked_unrestricted
    assert restricted_top1 == O_GOOD, (
        f"restrict_hop1_to={{M_GOOD}} must steer the answer to O_GOOD, got {ranked_restricted}")
    restricted_scores = dict(ranked_restricted)
    assert O_BAD not in restricted_scores or restricted_scores[O_BAD] < restricted_scores[O_GOOD], (
        f"O_BAD must not outrank O_GOOD once M_BAD's route is excluded, got {ranked_restricted}")


def test_recovery_at_matches_reference() -> None:
    """recovery_at is a direct, deterministic membership check -- exercised here independently
    of any KGStore/attractor machinery."""
    ranked = [(5, 3.0), (2, 2.0), (9, 1.0)]
    assert gather_reason.recovery_at(ranked, gold_idx=5, k=1) == 1
    assert gather_reason.recovery_at(ranked, gold_idx=2, k=1) == 0
    assert gather_reason.recovery_at(ranked, gold_idx=2, k=2) == 1
    assert gather_reason.recovery_at(ranked, gold_idx=999, k=3) == 0


def _run_all() -> None:
    test_module_self_test_passes()
    test_ca3_relevance_gather_is_query_conditioned()
    test_fanout_two_hop_restriction_changes_ranking()
    test_recovery_at_matches_reference()


if __name__ == "__main__":
    _run_all()
    print("[test_gather_reason] PASS: module self-test + query-conditioning + "
          "restriction-changes-ranking + recovery_at all reproduced (tracing=False).")
