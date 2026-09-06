"""Entity world-model resolver — the full brain-foundational chain (owner-DONE
seed_the_entity_world_model_resolver_with_a_world_knowledge_role_kinship_prior_phase1).

Q111 landing: imports the exact `exp_entitykb_resolver_v2.resolve` (byte-faithful — it CALLS the reverified
function; hdlab organs already import experiments cells, e.g. situation_reader imports _causal_network /
_space_reader / _belief_reader). The curated role/kinship/scenario KB is inline in the imported cell (glass-box,
NO LLM). The KB SEED ALONE is a LOCATED NEGATIVE (~2% coverage); the CHAIN crosses — curated KB + situation-model
instance binding + pronoun-into-entity + the reader's REAL per-text head-coreference (Step-3, the biggest lever):
aggregate common-noun CoNLL +0.0882 CI-sep on the harness (test_entitykb_resolver_v2.py 6/6). Do NOT wire the
reader AGENT head-match (it regresses named coref).

BOARD-VISIBILITY (disk-verified 2026-09-05): the board `coref` dim scores PRONOUN coref, while this improves
COMMON-NOUN clustering — the harness win may NOT reach the board coref dim; its payoff is INDIRECT (feeding the
affect/goal experiencers that bind through common-noun entities). The full Step-3 reader_coref lever wants the
reader's OWN per-text clustering (a two-pass); passing reader_coref=None runs the KB+sitmodel+pron_coref chain.
"""
from __future__ import annotations

_FULL = dict(salience="composite", kb=True, repair=True, sitmodel=True, sitmodel_margin=1.0,
             attrs=True, pron_coref=True)


def resolve_common_noun(mentions, gaz, reader_coref=None, window=8):
    """Full-chain entity-world-model resolution over the reader's OWN mentions -> {midx: label}. reader_coref =
    the reader's live per-text co-referent head-sets (Step-3); None runs the chain without that lever."""
    from experiments.exp_entitykb_resolver_v2 import resolve
    return resolve(mentions, gaz, window=window, reader_coref=reader_coref, **_FULL)


def reader_coref_from_entities(entities):
    """Build the live reader_coref (per-entity non-pronoun head-sets, >=2 heads) from the reader's OWN sm.entities
    -- the reader's REAL per-text clustering. Mirrors exp_reader_sitmodel_cache_v1.person_entity_heads."""
    out = []
    for e in (entities or []):
        heads = sorted({str(h).strip().lower() for h in getattr(e, "heads", []) if str(h).strip()})
        if len(heads) >= 2:
            out.append(heads)
    return out
