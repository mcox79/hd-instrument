"""
_qa_route_primitives.py -- Exp-Dev validated substrate-native route mechanisms, packaged for Gap-4 v1 router absorption.

ROUTING: Research Cycle 45 (research_to_exp_dev_testbed_BENCHMARK_DIVISION_LABOR_OPTION_1_NOW_OPTION_3_TARGET) -- Exp-Dev wraps its
  validated route mechanisms into Gap-4-compatible primitives; Testbed integrates them into the canonical Gap-4 v1 intent-router so
  both score the canonical 60-Q via ONE shared router. These are the substrate-NATIVE retrieval primitives validated on the 53-Q
  mechanism benchmark (B-vocab +0.42, relation-G 0.014->0.667/Q28 1.0, D bidirectional 0.25->0.50). No cell/benchmark coupling --
  pure functions over (atoms, relations, pstore). substrate-only, no LLM.

Absorption map (per Research Cycle 45 table):
  predecessors_via                  <- B-vocab reconciliation (DEPENDS_ON+USES + src_ns precision filter)
  analogues_via_relation_traversal  <- relation-G analogue traversal over INFLUENCED_BY/GROUNDS/INSTANTIATES/RELATES/DUAL/...
  composition_reachable             <- D bidirectional reachability
  serves                            <- C what_serves (passthrough)
"""
from __future__ import annotations


def norm(qid: str) -> str:
    """Canonical id-part: strip a leading 'corpus::' prefix; lowercase. Robust to math::T2/x vs T2/x vs school::SCHOOL/x."""
    s = qid.split("::", 1)[1] if "::" in qid else qid
    return s.strip().lower()


# substrate's actual analogue/cross-disc edge vocabulary (Testbed evolve maps GROUNDS/INSTANTIATES -> INFLUENCED_BY/INSTANCE_OF)
ANALOGUE_REL_TYPES = frozenset({
    "RELATES", "GROUNDS", "INSTANTIATES", "ANALOGOUS_TO", "ANALOG_OF", "DUAL",
    "BIOLOGICAL_INSPIRATION_FOR", "INFLUENCED_BY", "GENERALIZES", "SPECIALIZES",
})

# benchmark-intent -> substrate's actual relation vocabulary (substrate has no DECOMPOSES_TO/USED_FOR_LIFT)
B_VOCAB_MAP = {
    "DECOMPOSES_TO": ("DEPENDS_ON", "USES"),
    "USES": ("USES", "INSTANCE_OF", "DEFINED_OVER", "RELATES"),
    "INSTANCE_OF": ("INSTANCE_OF",),
    "DEPENDS_ON": ("DEPENDS_ON",),
    "SUPERSEDES": ("SUPERSEDES",),
    "USED_FOR_LIFT": ("USES", "DEPENDS_ON"),
}


def predecessors_via(relations, target, rel_types=None, src_ns=None, id2corpus=None):
    """B-axis: atoms X with (X rel target) for rel in rel_types, optionally filtered by source namespace (precision).
    target='*' = wildcard (all sources of rel_types). rel_types None -> derive from B_VOCAB_MAP not applied here (pass explicit).
    Returns set of normalized src ids. (substrate-as-ground-truth: uses substrate's actual edge vocabulary.)"""
    accept = {r.upper() for r in (rel_types or ["USES"])}
    tgt = norm(target); wild = (tgt == "*")
    out = set()
    for r in relations:
        if str(r.get("rel_type", "")).upper() not in accept:
            continue
        s = norm(r.get("src_id", "")); t = norm(r.get("tgt_id", ""))
        if wild or t == tgt:
            if src_ns and id2corpus is not None and id2corpus.get(s) not in src_ns:
                continue
            out.add(s)
    return out


def analogues_via_relation_traversal(relations, anchor, analogue_rel_types=ANALOGUE_REL_TYPES):
    """G-axis: 1-hop neighbors of `anchor` over analogue-type edges (either direction). Analogues are EDGES not keywords.
    Returns set of normalized neighbor ids. (Validated: Q28 theta_gamma -> {sdm,resonator,permutation,circular_conv} F1 1.0.)"""
    a = norm(anchor); accept = {x.upper() for x in analogue_rel_types}
    out = set()
    for r in relations:
        if str(r.get("rel_type", "")).upper() not in accept:
            continue
        s = norm(r.get("src_id", "")); t = norm(r.get("tgt_id", ""))
        if s == a: out.add(t)
        if t == a: out.add(s)
    return out


def composition_reachable(pstore, sk, src_qid, tgt_qid, max_depth=5, bidirectional=True):
    """D-axis: is there a composition path src<->tgt? Substrate dependency edges point capability->primitive, so a
    primitive->capability question must also try the reverse. Returns bool. (Validated: Q15 0->1.0 via bidirectional.)"""
    try:
        if sk.composition_paths(pstore, src_qid, tgt_qid, max_depth=max_depth):
            return True
        if bidirectional and sk.composition_paths(pstore, tgt_qid, src_qid, max_depth=max_depth):
            return True
    except Exception:
        pass
    return False


def serves(pstore, sk, capability_qid):
    """C-axis: atoms whose serves_capability includes capability_qid. Returns set of normalized ids. (Strongest axis 0.64.)"""
    try:
        return {norm(a.id) for a in sk.what_serves(pstore, capability_qid)}
    except Exception:
        return set()


def _selftest():
    assert norm("math::T2/fhrr_bind") == "t2/fhrr_bind"
    assert norm("school::SCHOOL/vsa_family") == "school/vsa_family"
    rels = [{"src_id": "concept::CAP_x", "tgt_id": "math::T2/fhrr_bind", "rel_type": "DEPENDS_ON"},
            {"src_id": "BIO/theta_gamma_binding", "tgt_id": "math::T3/resonator", "rel_type": "INFLUENCED_BY"}]
    assert predecessors_via(rels, "T2/fhrr_bind", ["DEPENDS_ON", "USES"]) == {"cap_x"}
    assert analogues_via_relation_traversal(rels, "BIO/theta_gamma_binding") == {"t3/resonator"}
    assert predecessors_via(rels, "*", ["INFLUENCED_BY"]) == {"bio/theta_gamma_binding"}
    print("[selftest] PASS: qa-route-primitives")


if __name__ == "__main__":
    _selftest()
