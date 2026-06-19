"""Self-reflection over the substrate self-index.

Operations that let the system describe itself + surface its own state, gaps,
and load-bearing atoms. Operates over a populated PartitionedStore (+ optional
Retriever for semantic introspection).

Public surface:
  - summarize_state()                 high-level corpus summary
  - identify_strongest_claims()       atoms with most VALIDATES + cross-corpus USES
                                      = best-supported concepts
  - identify_exposed_atoms()          high-centrality atoms with weak support
                                      = single-points-of-failure
  - knowledge_pertaining_to()         inverse query: what does the system know
                                      about an atom? (all incoming + outgoing
                                      edges + semantic neighbors)
  - describe_self()                   natural-language self-summary

Per Refinement 3 design AGAINST rule 1 (meta-rule self-collapse):
operations operate over the math + concept partitions; meta partition is
write-protected against self-relations.
"""
from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.retrieve import Retriever
from backend.substrate_index.schema import AtomKind, Corpus, RelationType, Tier

logger = logging.getLogger(__name__)


# ============================================================
# State summary
# ============================================================


@dataclass(frozen=True)
class StateSummary:
    """High-level snapshot of what the index knows."""
    total_atoms: int
    atoms_by_corpus: dict
    atoms_by_tier: dict
    atoms_by_kind: dict
    total_relations: int
    relations_by_type: dict
    cross_corpus_relations: int
    coverage: dict     # fraction of atoms touched by ANY edge

    def to_dict(self) -> dict:
        return {
            "total_atoms": self.total_atoms,
            "atoms_by_corpus": dict(self.atoms_by_corpus),
            "atoms_by_tier": dict(self.atoms_by_tier),
            "atoms_by_kind": dict(self.atoms_by_kind),
            "total_relations": self.total_relations,
            "relations_by_type": dict(self.relations_by_type),
            "cross_corpus_relations": self.cross_corpus_relations,
            "coverage": dict(self.coverage),
        }


def summarize_state(pstore: PartitionedStore) -> StateSummary:
    raw = pstore.stats()
    by_corpus = {}
    by_tier = {}
    by_kind = {}
    for corpus, sub in raw["partitions"].items():
        by_corpus[corpus] = sub["n_atoms"]
        for tier_v, count in sub["n_atoms_by_tier"].items():
            by_tier[tier_v] = by_tier.get(tier_v, 0) + count
    for atom in pstore.all_atoms():
        by_kind[atom.kind.value] = by_kind.get(atom.kind.value, 0) + 1

    # Coverage: fraction of atoms participating in ANY edge
    touched: set[str] = set()
    for src, _rt, tgt in pstore.iter_all_relations():
        touched.add(src)
        touched.add(tgt)
    total_atoms = raw["total_atoms"]
    coverage = {
        "atoms_with_any_edge": len(touched),
        "atoms_isolated": total_atoms - len(touched),
        "coverage_fraction": round(len(touched) / max(1, total_atoms), 3),
    }

    rel_counts = {}
    for _, rt, _ in pstore.iter_all_relations():
        rel_counts[rt.value] = rel_counts.get(rt.value, 0) + 1

    return StateSummary(
        total_atoms=total_atoms,
        atoms_by_corpus=by_corpus,
        atoms_by_tier=by_tier,
        atoms_by_kind=by_kind,
        total_relations=raw["total_relations"],
        relations_by_type=rel_counts,
        cross_corpus_relations=raw["cross_store_relations"],
        coverage=coverage,
    )


# ============================================================
# Strongest claims (high VALIDATES + cross-corpus USES + low REFUTES)
# ============================================================


@dataclass(frozen=True)
class ClaimStrength:
    """A concept atom's level of empirical / structural support."""
    atom_id: str
    name: str
    validates_in: int      # incoming VALIDATES edges (n drills/PPs that support)
    validates_out: int     # outgoing VALIDATES edges (this atom validates others)
    uses_out: int          # outgoing USES (count of math foundations cited)
    refutes_in: int        # incoming REFUTES (warns of fragility)
    cross_corpus_uses: int # outgoing USES to other partition (a strong claim
                           # bridges concept->math)
    score: float           # composite strength: uses + validates - refutes

    def to_dict(self) -> dict:
        return {
            "atom_id": self.atom_id, "name": self.name,
            "validates_in": self.validates_in, "validates_out": self.validates_out,
            "uses_out": self.uses_out, "refutes_in": self.refutes_in,
            "cross_corpus_uses": self.cross_corpus_uses, "score": self.score,
        }


def identify_strongest_claims(pstore: PartitionedStore, top_n: int = 20) -> list[ClaimStrength]:
    """Concept atoms ranked by structural support.

    score = 0.5 * uses_out + 1.0 * validates_in + 1.0 * cross_corpus_uses
            - 1.0 * refutes_in
    """
    results = []
    for atom in pstore.concept.all_atoms():
        qid = atom.qualified_id
        vi = len(pstore.in_neighbors(qid, RelationType.VALIDATES))
        vo = len(pstore.out_neighbors(qid, RelationType.VALIDATES))
        uo = pstore.out_neighbors(qid, RelationType.USES)
        ri = len(pstore.in_neighbors(qid, RelationType.REFUTES))
        cross_uses = len([n for n in uo if n.startswith("math::") or n.startswith("meta::")])
        score = 0.5 * len(uo) + 1.0 * vi + 1.0 * cross_uses - 1.0 * ri
        results.append(ClaimStrength(
            atom_id=qid, name=atom.name,
            validates_in=vi, validates_out=vo,
            uses_out=len(uo), refutes_in=ri,
            cross_corpus_uses=cross_uses, score=round(score, 2),
        ))
    return sorted(results, key=lambda c: -c.score)[:top_n]


# ============================================================
# Exposed atoms (high centrality, weak support)
# ============================================================


@dataclass(frozen=True)
class ExposureReport:
    """Atoms that are load-bearing but weakly supported."""
    atom_id: str
    name: str
    fan_in: int             # incoming USES edges (downstream depends on this)
    fan_out: int            # outgoing USES edges
    own_support: int        # incoming VALIDATES + outgoing PROVES
    exposure_score: float   # high fan_in / (own_support + 1) means exposed

    def to_dict(self) -> dict:
        return {
            "atom_id": self.atom_id, "name": self.name,
            "fan_in": self.fan_in, "fan_out": self.fan_out,
            "own_support": self.own_support,
            "exposure_score": self.exposure_score,
        }


def identify_exposed_atoms(pstore: PartitionedStore, top_n: int = 10) -> list[ExposureReport]:
    """Math atoms that many concepts depend on but have weak own support.

    'Exposed' = if this atom is wrong or insufficient, many concepts break.
    Surfacing these tells you where to invest rescue effort.
    """
    results = []
    for atom in pstore.math.all_atoms():
        qid = atom.qualified_id
        fan_in = len(pstore.in_neighbors(qid, RelationType.USES))
        if fan_in == 0:
            continue
        fan_out = len(pstore.out_neighbors(qid, RelationType.USES_SUBPROC))
        own_support = (
            len(pstore.in_neighbors(qid, RelationType.VALIDATES))
            + fan_out  # composing on multiple sub-ops adds support
        )
        exposure = fan_in / (own_support + 1)
        results.append(ExposureReport(
            atom_id=qid, name=atom.name,
            fan_in=fan_in, fan_out=fan_out,
            own_support=own_support,
            exposure_score=round(exposure, 2),
        ))
    return sorted(results, key=lambda r: -r.exposure_score)[:top_n]


# ============================================================
# Knowledge pertaining to a given atom (inverse query)
# ============================================================


@dataclass(frozen=True)
class KnowledgeProfile:
    """Everything the system knows about a specific atom."""
    qualified_id: str
    name: str
    description: str
    corpus: str
    tier: str
    kind: str
    outgoing: dict      # {rel_type: [qualified ids]}
    incoming: dict      # {rel_type: [qualified ids]}
    semantic_top_5: list  # ids most similar by description
    isolation: bool       # True if no relations at all

    def to_dict(self) -> dict:
        return {
            "qualified_id": self.qualified_id,
            "name": self.name,
            "description": self.description,
            "corpus": self.corpus,
            "tier": self.tier,
            "kind": self.kind,
            "outgoing": dict(self.outgoing),
            "incoming": dict(self.incoming),
            "semantic_top_5": list(self.semantic_top_5),
            "isolation": self.isolation,
        }


def knowledge_pertaining_to(
    pstore: PartitionedStore,
    qualified_id: str,
    retriever: Optional[Retriever] = None,
) -> Optional[KnowledgeProfile]:
    """Full inverse profile of a single atom: what does the system know about it?"""
    atom = pstore.get_atom(qualified_id)
    if atom is None:
        return None
    outgoing = {}
    incoming = {}
    for rt in RelationType:
        out_n = pstore.out_neighbors(qualified_id, rt)
        if out_n:
            outgoing[rt.value] = sorted(out_n)
        in_n = pstore.in_neighbors(qualified_id, rt)
        if in_n:
            incoming[rt.value] = sorted(in_n)
    isolation = (not outgoing) and (not incoming)

    semantic_top_5 = []
    if retriever is not None:
        cands = retriever.semantic(atom.description + " " + " ".join(atom.aliases), top_k=6)
        semantic_top_5 = [c.atom_id for c in cands if c.atom_id != qualified_id][:5]

    return KnowledgeProfile(
        qualified_id=qualified_id,
        name=atom.name,
        description=atom.description,
        corpus=atom.corpus.value,
        tier=atom.tier.value,
        kind=atom.kind.value,
        outgoing=outgoing,
        incoming=incoming,
        semantic_top_5=semantic_top_5,
        isolation=isolation,
    )


# ============================================================
# Self description: natural-language summary
# ============================================================


def describe_self(pstore: PartitionedStore) -> str:
    """Render a human-readable summary of the index's current state.

    Used by report.py / CLI to give a one-page 'where the index stands today'
    answer to operator queries.
    """
    s = summarize_state(pstore)
    strong = identify_strongest_claims(pstore, top_n=5)
    exposed = identify_exposed_atoms(pstore, top_n=5)

    lines = []
    lines.append("# Substrate self-index: state summary")
    lines.append("")
    lines.append(f"- total atoms: **{s.total_atoms}** across {len(s.atoms_by_corpus)} partitions")
    for corpus, n in s.atoms_by_corpus.items():
        lines.append(f"  - {corpus}: {n} atoms")
    lines.append("")
    lines.append(f"- atoms by tier:")
    for tier_v, n in sorted(s.atoms_by_tier.items()):
        lines.append(f"  - {tier_v}: {n}")
    lines.append("")
    lines.append(f"- atoms by kind:")
    for kind_v, n in sorted(s.atoms_by_kind.items()):
        lines.append(f"  - {kind_v}: {n}")
    lines.append("")
    lines.append(f"- total relations: **{s.total_relations}** ({s.cross_corpus_relations} cross-corpus)")
    if s.relations_by_type:
        lines.append(f"- relations by type:")
        for rt_v, n in sorted(s.relations_by_type.items(), key=lambda x: -x[1]):
            lines.append(f"  - {rt_v}: {n}")
    lines.append("")
    lines.append(f"- coverage:")
    lines.append(f"  - atoms with any edge: {s.coverage['atoms_with_any_edge']}/{s.total_atoms} "
                 f"({s.coverage['coverage_fraction'] * 100:.0f}%)")
    lines.append(f"  - isolated atoms: {s.coverage['atoms_isolated']}")
    lines.append("")
    if strong:
        lines.append("## Strongest claims (top 5 by structural support)")
        lines.append("")
        for c in strong:
            lines.append(f"- **{c.name}** ({c.atom_id})  score={c.score}; "
                         f"validates_in={c.validates_in}, uses_out={c.uses_out}, "
                         f"cross={c.cross_corpus_uses}, refutes_in={c.refutes_in}")
        lines.append("")
    if exposed:
        lines.append("## Most exposed atoms (top 5 by fan-in / own-support)")
        lines.append("")
        for e in exposed:
            lines.append(f"- **{e.name}** ({e.atom_id})  exposure={e.exposure_score}; "
                         f"fan_in={e.fan_in}, fan_out={e.fan_out}, own_support={e.own_support}")
        lines.append("")
    return "\n".join(lines)
