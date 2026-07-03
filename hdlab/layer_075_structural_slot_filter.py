"""Layer 0.75 v3-clean structural KG-slot filter (Exp 3E FULL arc-closure primitive).

Substrate-native, LLM-free structural filter that narrows a Layer 0.5 PPR-union
candidate set (~30 facts) down to the ~2-5 facts a two-hop composition query
actually needs. Consumed by Layer 1 (FHRR unbind-and-cleanup composition).

Query semantics (two-hop composition over (subject, relation, object) facts):
  "What is the r1 of the r2 of e0?"
  hop-1 fact:  (e0,  r2, mid)  -- retrieves the bridge mid
  hop-2 fact:  (mid, r1, ans)  -- retrieves the final answer

Filter definition (source-signature verbatim per MM_STANDARD; DO NOT abstract):
  hop_1_cands  = { f in ppr_union | subject(f) == e0  AND relation(f) == r2 }
  hop_2_cands  = { f in ppr_union | subject(f) in bridges AND relation(f) == r1 }
  filtered     = (hop_1_cands || hop_2_cands)[:k_final]
  fallback     = if union empty: ppr_union[:k_final]

Source cell:
  experiments/exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03.py
  (commit 01f41fc20; HARD_PASS_FULL_ARC_CLOSURE_V3_CLEAN at 2026-07-03T17:11Z;
  N=8192, 100q x 3 seeds; MAIN_V3_CLEAN=0.767 >= 0.90 * ORACLE=0.822).

CRITICAL DISCIPLINE (do not silently violate; enforced by verification test):
  Layer 0.5 Stage 1 (node-specificity IDF seed reweight) and Layer 0.5 Stage 2
  (hub-dampen adjacency scaling) MUST NOT be composed with this primitive. They
  SUBTRACT from structural filtering because Stage 2 hub-dampen demotes hop-2
  hub-subject facts (the bridge IS a hub by construction of the two-hop query).
  Evidence: Exp 3E FULL MAIN_V3_CLEAN=0.767 vs V3_STACKED_WITH_S1S2=0.511 = gap 0.256.
  Composition rule: uniform PPR union -> layer_075_v3_clean_filter -> FHRR compose.

Composes with:
  - hdlab.kg_traversal.KGStore.predict_one_hop_topk (structural KG lookup;
    bridges may be derived from top-k of (e0, r2, *) queries)
  - hdlab.char_trigram_encoder.CharTrigramEncoder (Exp 2C fuzzy bridge match;
    for real-corpus regimes where bridge extraction is not by-construction)
  - FHRR bind/unbind composition primitives (Layer 1; downstream of this filter)
"""

from __future__ import annotations

from typing import NamedTuple


class Query(NamedTuple):
    """Two-hop composition query decomposition; shape: (e0, r1, r2) as str names."""
    e0: str
    r1: str
    r2: str


def layer_075_v3_clean_filter(
    ppr_union: list[int],
    facts: list[tuple[str, str, str, str]],
    entities: list[str],
    e0: str,
    r1: str,
    r2: str,
    bridges: list[int],
    k_final: int = 5,
) -> tuple[list[int], dict]:
    """Structural KG-slot filter over a PPR-union candidate pool; shape: fact_indices, diag.

    Args:
      ppr_union: fact indices from Layer 0.5 PPR-union (uniform seed; NO Stage 1/2).
      facts: canonical fact list; each fact is (subject_name, relation_name, object_name, text).
      entities: entity vocabulary; entities[i] is the name for entity index i.
      e0: hop-anchor entity name from the query.
      r1: hop-1 relation name (the final answer's relation).
      r2: hop-2 relation name (the bridge relation).
      bridges: bridge entity INDICES (from co-occurrence extraction OR KGStore top-k).
      k_final: cap on returned candidates for Layer 1 FHRR composition.

    Returns:
      (filtered, diag) where filtered is up to k_final fact indices and diag is a
      dict with keys n_hop_1_cands, n_hop_2_cands, n_distractors, n_union_pre_cap,
      fallback_to_p1.
    """
    if not ppr_union:
        return [], {
            "n_hop_1_cands": 0, "n_hop_2_cands": 0, "n_distractors": 0,
            "n_union_pre_cap": 0, "fallback_to_p1": False,
        }
    bridge_set = set(bridges)
    e0_i = entities.index(e0)

    hop_1_cands: list[int] = []
    hop_2_cands: list[int] = []
    distractors: list[int] = []
    for fi in ppr_union:
        e, r, v, _t = facts[fi]
        si = entities.index(e)
        vi = entities.index(v)
        if si == e0_i and r == r2:
            hop_1_cands.append(fi)
        if si in bridge_set and r == r1:
            hop_2_cands.append(fi)
        if vi in bridge_set and si != e0_i:
            distractors.append(fi)

    seen: set[int] = set()
    union_ordered: list[int] = []
    for fi in hop_1_cands + hop_2_cands:
        if fi not in seen:
            union_ordered.append(fi)
            seen.add(fi)

    diag = {
        "n_hop_1_cands": len(hop_1_cands),
        "n_hop_2_cands": len(hop_2_cands),
        "n_distractors": len(distractors),
        "n_union_pre_cap": len(union_ordered),
        "fallback_to_p1": False,
    }
    if not union_ordered:
        diag["fallback_to_p1"] = True
        return list(ppr_union[:k_final]), diag
    return union_ordered[:k_final], diag


def layer_075_v3_clean(
    ppr_union: list[int],
    facts: list[tuple[str, str, str, str]],
    entities: list[str],
    query: Query,
    bridges: list[int],
    k_final: int = 5,
) -> tuple[list[int], dict]:
    """Query-shaped adapter over layer_075_v3_clean_filter; shape: fact_indices, diag."""
    return layer_075_v3_clean_filter(
        ppr_union, facts, entities,
        query.e0, query.r1, query.r2, bridges, k_final,
    )
