"""Discovery engine for substrate self-index -- the 'find better solutions' module.

Per user direction (2026-06-11): substrate self-index should help us find better
solutions, surface non-obvious patterns, suggest where to invest next.

This module operates over a populated PartitionedStore + Retriever. Each function
returns a structured Finding for inclusion in report.py output.

Discovery surfaces (with cheapest-first ordering):

1. structural_gap()             atoms missing edges of expected types
                                (e.g., math op with no concept user; concept
                                with no math foundation; sealed PP row with
                                no VALIDATES)
2. cluster_unification()        atoms in the same family-tag whose pairwise
                                semantic similarity is high enough to suggest
                                a unifying primitive
3. centrality_anomaly()         atoms whose graph centrality changed sharply
                                between two snapshots (drift signal)
4. cross_corpus_orphans()       math primitives with no concept users; concepts
                                with no math foundation -- gap = next-build
                                candidate
5. semantic_vs_structural_disagreement()
                                atoms where semantic and structural neighbors
                                diverge -- either a missing relation or a wrong
                                semantic embedding
6. transitive_chain_unification()
                                long A->B->C chains where A->C is semantically
                                strong but no direct relation exists -- candidate
                                shortcut primitive
7. underutilized_relation_types()
                                relation types with too few edges; may be
                                under-used or unnecessary in the schema
8. tier_imbalance()             tiers with relatively few or many atoms vs design
                                (e.g., 300-500 expected at T3 but only 50 present)

Each Finding carries:
  - kind: short identifier
  - severity: 'info' / 'suggest' / 'warning'
  - subject: atom_id(s) the finding is about
  - evidence: machine-readable details
  - hypothesis: human-readable interpretation
  - suggested_action: concrete next-step (e.g., 'add relation X', 'split atom Y')
"""
from __future__ import annotations

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.retrieve import Retriever
from backend.substrate_index.schema import AtomKind, Corpus, RelationType, Tier

logger = logging.getLogger(__name__)


# ============================================================
# Finding
# ============================================================


@dataclass(frozen=True)
class Finding:
    """One discovery result. Structured for report.py serialization."""
    kind: str
    severity: str               # 'info' / 'suggest' / 'warning'
    subject: tuple[str, ...]    # qualified atom ids (or single)
    evidence: dict
    hypothesis: str
    suggested_action: str
    confidence: float = 0.5     # 0..1; how strongly the discovery believes this

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "severity": self.severity,
            "subject": list(self.subject),
            "evidence": dict(self.evidence),
            "hypothesis": self.hypothesis,
            "suggested_action": self.suggested_action,
            "confidence": self.confidence,
        }


# ============================================================
# 1. Structural gap detection
# ============================================================


def structural_gap(
    pstore: PartitionedStore,
    rel_type: RelationType,
    direction: str = "out",
    corpus_filter: Optional[Corpus] = None,
    tier_filter: Optional[Tier] = None,
    kind_filter: Optional[AtomKind] = None,
    max_findings: int = 20,
) -> list[Finding]:
    """Atoms missing edges of a given type/direction. Most common discovery."""
    findings: list[Finding] = []
    for atom in pstore.all_atoms():
        if corpus_filter is not None and atom.corpus != corpus_filter:
            continue
        if tier_filter is not None and atom.tier != tier_filter:
            continue
        if kind_filter is not None and atom.kind != kind_filter:
            continue
        qid = atom.qualified_id
        if direction == "out":
            neigh = pstore.out_neighbors(qid, rel_type)
        else:
            neigh = pstore.in_neighbors(qid, rel_type)
        if neigh:
            continue
        # Severity higher when this is a load-bearing kind/tier
        severity = "warning" if atom.kind in (AtomKind.MACRO, AtomKind.PRIMITIVE) else "suggest"
        findings.append(Finding(
            kind="structural_gap",
            severity=severity,
            subject=(qid,),
            evidence={
                "rel_type": rel_type.value,
                "direction": direction,
                "atom_name": atom.name,
                "tier": atom.tier.value,
                "atom_kind": atom.kind.value,
            },
            hypothesis=(
                f"{atom.name} has no {direction}-going {rel_type.value} relation. "
                f"This may indicate a missing edge (the relation exists but wasn't "
                f"authored) or a genuine capability gap."
            ),
            suggested_action=(
                f"Audit whether {atom.name} should have outgoing {rel_type.value} edges "
                f"to existing atoms. If not, this is a 'next-build candidate' "
                f"(atom needs more downstream/upstream support)."
            ),
            confidence=0.75,
        ))
        if len(findings) >= max_findings:
            break
    return findings


# ============================================================
# 2. Cluster unification: family-tag members that look TOO similar
# ============================================================


def cluster_unification(
    pstore: PartitionedStore,
    retriever: Retriever,
    similarity_threshold: float = 0.85,
    max_findings: int = 20,
) -> list[Finding]:
    """For each FAMILY_TAG atom, compute pairwise semantic similarity among its
    members. If two members are extremely close (>= threshold), they might be
    redundant -- candidate for unification into a single primitive.

    Requires that family-tag atoms have a `members` metadata field listing
    qualified ids of their members.
    """
    findings: list[Finding] = []
    for atom in pstore.all_atoms():
        if atom.kind != AtomKind.FAMILY_TAG:
            continue
        members = atom.metadata.get("members") or []
        if len(members) < 2:
            continue
        vecs = []
        ids = []
        for m in members:
            # members may be local ids; try qualified first
            if "::" not in m:
                m = f"{atom.corpus.value}::{m}"
            v = retriever.get_vectors(m)
            if v is None:
                continue
            vecs.append(v.semantic)
            ids.append(m)
        if len(vecs) < 2:
            continue
        vecs = np.array(vecs)
        sims = vecs @ vecs.T
        np.fill_diagonal(sims, 0.0)
        # Find the most similar pair
        max_idx = np.unravel_index(np.argmax(sims), sims.shape)
        max_sim = float(sims[max_idx])
        if max_sim < similarity_threshold:
            continue
        a_id, b_id = ids[max_idx[0]], ids[max_idx[1]]
        findings.append(Finding(
            kind="cluster_unification_candidate",
            severity="suggest",
            subject=(a_id, b_id),
            evidence={
                "family_tag": atom.qualified_id,
                "pair_similarity": round(max_sim, 3),
                "threshold": similarity_threshold,
            },
            hypothesis=(
                f"In family '{atom.name}', members {a_id} and {b_id} have semantic "
                f"similarity {max_sim:.3f} -- nearly identical. They may describe "
                f"the same underlying primitive."
            ),
            suggested_action=(
                "Inspect the two atoms' descriptions; consider merging into one "
                "primitive OR distinguishing them more sharply if they're genuinely "
                "different operations."
            ),
            confidence=0.6,
        ))
        if len(findings) >= max_findings:
            break
    return findings


# ============================================================
# 3. Centrality anomaly (requires two snapshots; surfaced via report.py drift)
# ============================================================


@dataclass(frozen=True)
class CentralitySnapshot:
    """Per-atom degree snapshot for drift comparison."""
    qid: str
    in_degree: int
    out_degree: int

    def to_dict(self) -> dict:
        return {"qid": self.qid, "in": self.in_degree, "out": self.out_degree}


def centrality_snapshot(pstore: PartitionedStore) -> list[CentralitySnapshot]:
    in_deg: dict[str, int] = defaultdict(int)
    out_deg: dict[str, int] = defaultdict(int)
    for src, _rt, tgt in pstore.iter_all_relations():
        in_deg[tgt] += 1
        out_deg[src] += 1
    return [
        CentralitySnapshot(qid=qid, in_degree=in_deg.get(qid, 0), out_degree=out_deg.get(qid, 0))
        for qid in sorted(pstore.all_qualified_ids())
    ]


def centrality_drift(
    current: list[CentralitySnapshot],
    baseline: list[CentralitySnapshot],
    min_delta: int = 3,
) -> list[Finding]:
    """Atoms whose in_degree+out_degree changed by >= min_delta between snapshots.

    Useful in report.py to flag what shifted since the last benchmark run.
    """
    base_by_id = {s.qid: s for s in baseline}
    findings: list[Finding] = []
    for s in current:
        b = base_by_id.get(s.qid)
        b_total = (b.in_degree + b.out_degree) if b else 0
        c_total = s.in_degree + s.out_degree
        delta = c_total - b_total
        if abs(delta) >= min_delta:
            findings.append(Finding(
                kind="centrality_drift",
                severity="info" if delta > 0 else "warning",
                subject=(s.qid,),
                evidence={
                    "baseline_total_degree": b_total,
                    "current_total_degree": c_total,
                    "delta": delta,
                },
                hypothesis=(
                    f"{s.qid} centrality changed by {delta:+d} edges since last snapshot. "
                    f"{'Gained' if delta > 0 else 'Lost'} connectedness."
                ),
                suggested_action=(
                    "Inspect what relations were added/removed. If positive, atom became "
                    "more central -- worth promoting in benchmark coverage. If negative, "
                    "atom may be losing relevance -- worth auditing why."
                ),
                confidence=0.7,
            ))
    return findings


# ============================================================
# 4. Cross-corpus orphans
# ============================================================


def cross_corpus_orphans(pstore: PartitionedStore) -> list[Finding]:
    """Math atoms with no HAS_USERS (no concepts use them) -- candidate next-build.

    Also surfaces concepts with no USES (claims with no math foundation).
    """
    findings: list[Finding] = []
    # Math atoms with no concepts using them
    for atom in pstore.all_atoms():
        qid = atom.qualified_id
        if atom.corpus == Corpus.MATH:
            users = pstore.in_neighbors(qid, RelationType.USES)
            if not users:
                # Filter: only flag non-family-tag, non-T1 (T1 is foundational, may
                # be implicit; T2+ should have concept users to justify their inclusion)
                if atom.kind in (AtomKind.FAMILY_TAG,):
                    continue
                if atom.tier == Tier.TIER_1_FOUNDATIONAL:
                    continue
                findings.append(Finding(
                    kind="cross_corpus_orphan_math",
                    severity="suggest",
                    subject=(qid,),
                    evidence={"tier": atom.tier.value, "kind": atom.kind.value},
                    hypothesis=(
                        f"Math atom {atom.name} (tier {atom.tier.value}, "
                        f"kind {atom.kind.value}) has no concepts using it. "
                        f"Either no concept-level capability exercises this primitive yet, "
                        f"or the USES relation was missed during corpus authoring."
                    ),
                    suggested_action=(
                        "Search concept corpus for capabilities that mention this primitive's "
                        "operation -- if any are found, add explicit USES edges. If none, "
                        "this primitive is a candidate 'next concept to build' (it provides "
                        "untapped capability)."
                    ),
                    confidence=0.65,
                ))
        elif atom.corpus == Corpus.CONCEPT:
            uses = pstore.out_neighbors(qid, RelationType.USES)
            if not uses:
                findings.append(Finding(
                    kind="cross_corpus_orphan_concept",
                    severity="warning",
                    subject=(qid,),
                    evidence={},
                    hypothesis=(
                        f"Concept atom {atom.name} has no documented math foundation "
                        f"(no outgoing USES edges). This is a warning: a capability "
                        f"claim without math grounding is harder to defend."
                    ),
                    suggested_action=(
                        "Either author USES edges to the math primitives this concept "
                        "depends on, OR flag the concept as 'descriptive-only' (no "
                        "mathematical content)."
                    ),
                    confidence=0.7,
                ))
    return findings


# ============================================================
# 5. Semantic vs structural disagreement
# ============================================================


def semantic_vs_structural_disagreement(
    pstore: PartitionedStore,
    retriever: Retriever,
    rel_type: RelationType,
    top_k: int = 5,
    min_pairs: int = 1,
    max_findings: int = 20,
) -> list[Finding]:
    """For each atom: get its top-K semantic neighbors AND its structural neighbors
    via rel_type. Surface atoms where the two sets are completely disjoint --
    that means one signal is wrong (either the relation is missing or the embedding
    is misaligned).
    """
    findings: list[Finding] = []
    for atom in pstore.all_atoms():
        qid = atom.qualified_id
        sem = {
            c.atom_id for c in retriever.semantic(
                atom.description + " " + " ".join(atom.aliases),
                top_k=top_k,
            )
            if c.atom_id != qid
        }
        struct = pstore.out_neighbors(qid, rel_type)
        if not struct:
            continue  # no structural baseline; skip
        overlap = sem & struct
        if len(overlap) < min_pairs:
            findings.append(Finding(
                kind="semantic_structural_disagreement",
                severity="info",
                subject=(qid,),
                evidence={
                    "semantic_top_k": sorted(sem),
                    "structural_neighbors": sorted(struct),
                    "overlap_count": len(overlap),
                    "rel_type": rel_type.value,
                },
                hypothesis=(
                    f"For atom {atom.name}, its semantic top-{top_k} and its "
                    f"{rel_type.value} typed-edge neighbors share {len(overlap)} atoms. "
                    f"Low overlap suggests either (a) the typed edge captures a "
                    f"non-semantic relationship (e.g., DUAL pairs aren't semantically "
                    f"similar), or (b) one of the two signals is mis-aligned with reality."
                ),
                suggested_action=(
                    "Inspect manually. For relation types like DUAL or COMPOSES this "
                    "is expected (the typed edge encodes non-semantic structure). For "
                    "USES or SPECIALIZES, low overlap is a signal to audit either the "
                    "atom's description or the relation."
                ),
                confidence=0.55,
            ))
        if len(findings) >= max_findings:
            break
    return findings


# ============================================================
# 6. Underutilized relation types
# ============================================================


def underutilized_relation_types(
    pstore: PartitionedStore,
    min_edges_threshold: int = 3,
) -> list[Finding]:
    """Relation types with fewer than min_edges_threshold edges -- may be
    under-used or unnecessary in the schema.
    """
    counts: Counter[str] = Counter()
    for _, rt, _ in pstore.iter_all_relations():
        counts[rt.value] += 1
    findings: list[Finding] = []
    for rt in RelationType:
        n = counts.get(rt.value, 0)
        if n < min_edges_threshold:
            findings.append(Finding(
                kind="underutilized_relation_type",
                severity="info",
                subject=(rt.value,),
                evidence={"edge_count": n, "threshold": min_edges_threshold},
                hypothesis=(
                    f"Relation type {rt.value} has only {n} edges; may be unused or "
                    f"under-specified in the corpus."
                ),
                suggested_action=(
                    f"If you intend this relation type to be common, audit the corpus "
                    f"to find missing edges. If not, consider removing the relation "
                    f"type from the schema entirely."
                ),
                confidence=0.5,
            ))
    return findings


# ============================================================
# 7. Tier imbalance vs design intent
# ============================================================


# Expected counts per Research's drill granularity recommendation
EXPECTED_TIER_COUNTS = {
    Tier.TIER_1_FOUNDATIONAL.value: 15,    # ~15-20
    Tier.TIER_2_PRIMITIVE.value: 30,        # ~10-15 primitives + ~20-25 family-tags
    Tier.TIER_3_ALGORITHM.value: 400,       # 300-500 sub-ops
    Tier.TIER_4_COMPOSED.value: 18,         # 15-20 macros
}


def tier_imbalance(pstore: PartitionedStore, tolerance: float = 0.4) -> list[Finding]:
    """Flag tiers whose actual atom count is far from design intent."""
    actual = {t.value: 0 for t in Tier}
    for atom in pstore.math.all_atoms():
        actual[atom.tier.value] += 1
    findings: list[Finding] = []
    for tier_value, expected in EXPECTED_TIER_COUNTS.items():
        a = actual.get(tier_value, 0)
        if expected == 0:
            continue
        ratio = a / expected
        if ratio < (1 - tolerance):
            findings.append(Finding(
                kind="tier_underfilled",
                severity="info",
                subject=(tier_value,),
                evidence={"actual_count": a, "expected_count": expected, "ratio": round(ratio, 2)},
                hypothesis=(
                    f"Tier {tier_value} has {a} atoms; design intent expects ~{expected}. "
                    f"Under-filled by {(1-ratio)*100:.0f}%."
                ),
                suggested_action=(
                    f"Add more atoms at tier {tier_value}, or revise design-intent "
                    f"if the lower count is intentional."
                ),
                confidence=0.6,
            ))
        elif ratio > (1 + tolerance) and a > expected + 10:
            findings.append(Finding(
                kind="tier_overfilled",
                severity="info",
                subject=(tier_value,),
                evidence={"actual_count": a, "expected_count": expected, "ratio": round(ratio, 2)},
                hypothesis=(
                    f"Tier {tier_value} has {a} atoms; design intent expects ~{expected}. "
                    f"Over-filled by {(ratio-1)*100:.0f}%."
                ),
                suggested_action=(
                    f"Consider whether some atoms at this tier should be promoted to a "
                    f"higher tier (e.g., T3 sub-ops graduating to T4 macros)."
                ),
                confidence=0.5,
            ))
    return findings


# ============================================================
# Run-all entry point
# ============================================================


@dataclass(frozen=True)
class DiscoveryReport:
    """All findings from a discovery run, organized by category."""
    findings: tuple[Finding, ...]
    stats: dict

    def by_severity(self, severity: str) -> list[Finding]:
        return [f for f in self.findings if f.severity == severity]

    def by_kind(self, kind: str) -> list[Finding]:
        return [f for f in self.findings if f.kind == kind]

    def to_dict(self) -> dict:
        return {
            "stats": self.stats,
            "findings": [f.to_dict() for f in self.findings],
            "summary": {
                "total": len(self.findings),
                "warnings": len(self.by_severity("warning")),
                "suggestions": len(self.by_severity("suggest")),
                "info": len(self.by_severity("info")),
            },
        }


def discover_all(
    pstore: PartitionedStore,
    retriever: Optional[Retriever] = None,
    centrality_baseline: Optional[list[CentralitySnapshot]] = None,
) -> DiscoveryReport:
    """Run all discovery checks. Returns a structured report."""
    findings: list[Finding] = []

    # 1. Cross-corpus orphans -- highest signal-to-noise
    findings.extend(cross_corpus_orphans(pstore))

    # 2. Underutilized relation types
    findings.extend(underutilized_relation_types(pstore))

    # 3. Tier imbalance
    findings.extend(tier_imbalance(pstore))

    # 4. Structural gaps for the most important relation types
    for rt in (RelationType.USES, RelationType.DUAL, RelationType.COMPOSES):
        findings.extend(structural_gap(pstore, rt, direction="out", max_findings=10))

    # 5. Centrality drift if baseline provided
    if centrality_baseline is not None:
        current_snap = centrality_snapshot(pstore)
        findings.extend(centrality_drift(current_snap, centrality_baseline))

    # 6. Cluster unification (needs retriever)
    if retriever is not None:
        findings.extend(cluster_unification(pstore, retriever, max_findings=10))

    # 7. Semantic vs structural disagreement on USES
    if retriever is not None:
        findings.extend(
            semantic_vs_structural_disagreement(pstore, retriever, RelationType.USES, max_findings=10)
        )

    return DiscoveryReport(
        findings=tuple(findings),
        stats=pstore.stats(),
    )
