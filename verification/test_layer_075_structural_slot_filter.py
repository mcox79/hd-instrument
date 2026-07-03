"""Verification witnesses for hdlab.layer_075_structural_slot_filter (Exp 3E primitive)."""

from __future__ import annotations

import numpy as np

from hdlab.layer_075_structural_slot_filter import (
    Query,
    layer_075_v3_clean,
    layer_075_v3_clean_filter,
)

ENTITIES = [
    "Alton", "Bexley", "Coral", "Delft", "Erie", "Fjord", "Gulch",
    "Hara", "Iona", "Juno", "Kelm", "Pome", "Quill", "Xylo",
]


def _mini_facts() -> list[tuple[str, str, str, str]]:
    """Same synthetic six-fact corpus the source cell's --self-test uses (fi 0..5)."""
    return [
        ("Alton", "mayor",    "Fjord", "The mayor of Alton is Fjord."),
        ("Bexley", "river",   "Fjord", "The river of Bexley is Fjord."),
        ("Fjord", "capital",  "Gulch", "The capital of Fjord is Gulch."),
        ("Hara", "founder",   "Kelm",  "The founder of Hara is Kelm."),
        ("Iona", "neighbor",  "Kelm",  "The neighbor of Iona is Kelm."),
        ("Pome", "mayor",     "Quill", "The mayor of Pome is Quill."),
    ]


def test_positive_two_hop_answer_hop1_and_hop2_in_output() -> None:
    """Query 'capital of the mayor of Alton?': hop-1 fact 0 + hop-2 fact 2 both surface."""
    facts = _mini_facts()
    ppr_union = [0, 1, 2, 3, 4, 5]
    # Alton -mayor-> Fjord -capital-> Gulch; Fjord (idx 5) is the bridge.
    fjord_idx = ENTITIES.index("Fjord")
    selected, diag = layer_075_v3_clean_filter(
        ppr_union, facts, ENTITIES,
        e0="Alton", r1="capital", r2="mayor",
        bridges=[fjord_idx], k_final=5,
    )
    assert 0 in selected, f"hop-1 fact 0 (Alton mayor Fjord) missing: {selected}"
    assert 2 in selected, f"hop-2 fact 2 (Fjord capital Gulch) missing: {selected}"
    assert diag["n_hop_1_cands"] == 1
    assert diag["n_hop_2_cands"] == 1
    assert diag["fallback_to_p1"] is False
    assert 2 <= len(selected) <= 5


def test_negative_bridge_as_object_of_distractor_is_filtered_out() -> None:
    """Fact (Iona neighbor Kelm) has Kelm as OBJECT; must NOT surface when Kelm is a bridge."""
    facts = _mini_facts()
    ppr_union = [3, 4]  # only the Kelm-object facts
    kelm_idx = ENTITIES.index("Kelm")
    # Query where Kelm is the bridge (hop-2 SUBJECT-of); fact 4 has Kelm as OBJECT so
    # is a distractor (subject Iona, not Kelm), fact 3 same (subject Hara).
    selected, diag = layer_075_v3_clean_filter(
        ppr_union, facts, ENTITIES,
        e0="Hara", r1="capital", r2="founder",
        bridges=[kelm_idx], k_final=5,
    )
    # Both facts have Kelm as OBJECT (distractor role), neither has Kelm as SUBJECT.
    # Fact 3 IS a valid hop-1 (Hara-founder-Kelm) so surfaces; fact 4 is pure distractor.
    assert 4 not in selected, f"distractor fact 4 (Iona-neighbor-Kelm) leaked: {selected}"
    assert diag["n_distractors"] >= 1, f"distractor unaccounted: {diag}"


def test_fallback_when_no_slot_matches() -> None:
    """Query with no matching slots falls back to first k_final of ppr_union."""
    facts = _mini_facts()
    ppr_union = [0, 1, 2, 3, 4, 5]
    fjord_idx = ENTITIES.index("Fjord")
    selected, diag = layer_075_v3_clean_filter(
        ppr_union, facts, ENTITIES,
        e0="Xylo", r1="river", r2="founder",
        bridges=[fjord_idx], k_final=3,
    )
    assert diag["fallback_to_p1"] is True
    assert selected == [0, 1, 2]


def test_query_shaped_adapter_matches_positional() -> None:
    """layer_075_v3_clean(query=Query(...)) matches layer_075_v3_clean_filter(e0,r1,r2)."""
    facts = _mini_facts()
    ppr_union = [0, 1, 2, 3, 4, 5]
    fjord_idx = ENTITIES.index("Fjord")
    q = Query(e0="Alton", r1="capital", r2="mayor")
    sel_a, _ = layer_075_v3_clean(ppr_union, facts, ENTITIES, q, [fjord_idx], k_final=5)
    sel_b, _ = layer_075_v3_clean_filter(
        ppr_union, facts, ENTITIES,
        e0="Alton", r1="capital", r2="mayor",
        bridges=[fjord_idx], k_final=5,
    )
    assert sel_a == sel_b


def test_composes_with_fhrr_composition_primitive() -> None:
    """Sanity: filter output feeds directly into FHRR bind/unbind cleanup (Layer 1 shape)."""
    facts = _mini_facts()
    ppr_union = [0, 1, 2, 3, 4, 5]
    fjord_idx = ENTITIES.index("Fjord")
    selected, _ = layer_075_v3_clean_filter(
        ppr_union, facts, ENTITIES,
        e0="Alton", r1="capital", r2="mayor",
        bridges=[fjord_idx], k_final=5,
    )
    # Build minimal FHRR codebooks over these entities + relations. This mirrors the
    # source cell's composition_primitive shape without importing it (it's cell-local).
    rng = np.random.default_rng(0)
    n_dim = 512
    ents = ENTITIES
    rels = ["mayor", "river", "capital", "founder", "neighbor"]
    E = (rng.random((len(ents), n_dim)) * 2.0 - 1.0) * np.pi
    R = (rng.random((len(rels), n_dim)) * 2.0 - 1.0) * np.pi

    def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return (a + b + np.pi) % (2.0 * np.pi) - np.pi

    def unbind(a: np.ndarray, c: np.ndarray) -> np.ndarray:
        return (c - a + np.pi) % (2.0 * np.pi) - np.pi

    def phase_cos_row(a: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.mean(np.cos(B - a[None, :]), axis=1)

    fact_hds = np.zeros((len(facts), n_dim), dtype=np.float64)
    for i, (e, r, v, _t) in enumerate(facts):
        ei = ents.index(e); ri = rels.index(r); vi = ents.index(v)
        fact_hds[i] = bind(E[ei], bind(R[ri], E[vi]))

    # Hop-1: unbind (Alton, mayor) from each filtered fact; expect Fjord to win cleanup.
    q1 = bind(E[ents.index("Alton")], R[rels.index("mayor")])
    best_sim = -np.inf
    mid_idx = 0
    for k in selected:
        cand = unbind(q1, fact_hds[k])
        sims = phase_cos_row(cand, E)
        s = float(sims.max())
        if s > best_sim:
            best_sim = s
            mid_idx = int(sims.argmax())
    assert ents[mid_idx] == "Fjord", (
        f"composition cleanup missed bridge: got {ents[mid_idx]!r}"
    )


def test_empty_union_returns_empty() -> None:
    """Empty ppr_union: filter returns empty, no crash, no fallback flag."""
    facts = _mini_facts()
    selected, diag = layer_075_v3_clean_filter(
        [], facts, ENTITIES,
        e0="Alton", r1="capital", r2="mayor",
        bridges=[5], k_final=5,
    )
    assert selected == []
    assert diag["n_union_pre_cap"] == 0
