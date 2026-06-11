"""Data model for substrate self-index pilot.

Atoms are knowledge units (one math operation, one substrate primitive, one PP row,
one capability assertion). Relations are typed edges between atoms. Two corpora
(math and concept) are linked by USES (concept -> math) and HAS_USERS (math ->
concept; auto-derived reverse).

Per Research SUBSTRATE_SELF_INDEX_PILOT 2026-06-11 spec.
"""
from __future__ import annotations

import enum
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional


# ============================================================
# Enums
# ============================================================


class Corpus(enum.Enum):
    """Top-level corpus partition.

    Per Research SELF_INDEX_RESCOPE_ENDORSED 2026-06-11 Refinement 3:
    partitioned-substrate-with-role-binding architecture -- math + concept + meta
    are SEPARATE stores with explicit cross-store linking, NOT a single global
    substrate (prevents meta-rule self-collapse + unbounded self-reference).
    """
    MATH = "math"
    CONCEPT = "concept"
    META = "meta"      # methodology rules, architectural decisions, failure modes


class Tier(enum.Enum):
    """Tier for math atoms; CONCEPT/META atoms use TIER_NA."""
    TIER_1_FOUNDATIONAL = "T1"  # vector spaces, fields, distributions
    TIER_2_PRIMITIVE = "T2"     # FHRR bind/unbind/cleanup/bundle + family-tags
    TIER_3_ALGORITHM = "T3"     # Viterbi, Hungarian, PCA whitening + 300-500 sub-ops
    TIER_4_COMPOSED = "T4"      # substrate POS tagger, slot filler (macro-atoms)
    TIER_NA = "NA"              # concept/meta atoms don't have a tier


class AtomKind(enum.Enum):
    """Per Research Refinement 1 granularity: 300-500 sub-ops + 20-30 family-tags
    + 80-100 macro-atoms. AtomKind distinguishes the role within a tier.

    - PRIMITIVE: regular atomic operation or concept (default)
    - FAMILY_TAG: Tier-2 cluster tag grouping related sub-ops (e.g. "global discrete
                  optimization" tags Viterbi + Chu-Liu-Edmonds + Hungarian)
    - SUB_OP: Tier-3 fine-grained sub-operation (e.g. specific step in Viterbi DP)
    - MACRO: Tier-4 composite named entry point (substrate POS tagger references
             many sub-ops via USES_SUBPROC edges)
    """
    PRIMITIVE = "primitive"
    FAMILY_TAG = "family_tag"
    SUB_OP = "sub_op"
    MACRO = "macro"


class RelationType(enum.Enum):
    """Typed-edge relations.

    Per Research spec (~10 types). Within-corpus + cross-corpus relations.
    """
    # Within math corpus
    COMPOSES = "COMPOSES"               # A then B = C
    SPECIALIZES = "SPECIALIZES"         # A is a specific case of B
    DUAL = "DUAL"                       # binding/unbinding pair
    USES_SUBPROC = "USES_SUBPROC"       # A invokes B as subprocedure
    PRESERVES = "PRESERVES"             # A maintains property P
    OPTIMIZES = "OPTIMIZES"             # A solves optimization problem P
    APPROXIMATES = "APPROXIMATES"       # A approximates B with error bound

    # Within concept corpus
    ENABLES = "ENABLES"                 # A makes B possible
    VALIDATES = "VALIDATES"             # A confirms B (e.g. multi-seed validates n=1)
    REFUTES = "REFUTES"                 # A contradicts B
    DEPENDS_ON = "DEPENDS_ON"           # A requires B

    # Cross-corpus
    USES = "USES"                       # concept -> math operation
    HAS_USERS = "HAS_USERS"             # math operation -> concepts (auto-derived reverse of USES)


# ============================================================
# Dataclasses
# ============================================================


@dataclass(frozen=True)
class Atom:
    """One knowledge unit in the substrate self-index.

    `id` is the stable identifier (e.g., "math/T2/fhrr_bind" or "concept/PP-364").
    `name` is the human-readable short name.
    `description` is the multi-sentence English description that gets bge-encoded.
    `aliases` are alternate names that should match in retrieval.
    `metadata` is free-form (e.g., complexity class, paper reference).
    """
    id: str
    name: str
    corpus: Corpus
    tier: Tier
    description: str
    aliases: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "corpus": self.corpus.value,
            "tier": self.tier.value,
            "description": self.description,
            "aliases": list(self.aliases),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Atom":
        return cls(
            id=d["id"],
            name=d["name"],
            corpus=Corpus(d["corpus"]),
            tier=Tier(d.get("tier", "NA")),
            description=d["description"],
            aliases=tuple(d.get("aliases", [])),
            metadata=dict(d.get("metadata", {})),
        )


@dataclass(frozen=True)
class Relation:
    """A typed edge between two atoms.

    `src_id` -> `tgt_id` with type `rel_type`. Bidirectional retrieval is handled
    at the store layer (auto-derived HAS_USERS reverse for USES).
    """
    src_id: str
    tgt_id: str
    rel_type: RelationType
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "src_id": self.src_id,
            "tgt_id": self.tgt_id,
            "rel_type": self.rel_type.value,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Relation":
        return cls(
            src_id=d["src_id"],
            tgt_id=d["tgt_id"],
            rel_type=RelationType(d["rel_type"]),
            metadata=dict(d.get("metadata", {})),
        )


# ============================================================
# Query + result types
# ============================================================


class QueryType(enum.Enum):
    """Pre-registered query category. Used by metrics layer."""
    SEMANTIC = "semantic"          # "find math ops similar to X"
    STRUCTURAL = "structural"      # "what concepts USE X"
    HYBRID = "hybrid"              # semantic + structural combination
    GAP_DETECTION = "gap_detection"  # "what X has NO Y" (negative query)
    TRIVIAL_CHECK = "trivial_check"  # encoding-faithfulness sanity, e.g. "dual of bind = unbind"


@dataclass(frozen=True)
class TestQuery:
    """A pre-registered query with expected answer (for benchmark scoring)."""
    qid: str
    query_text: str
    query_type: QueryType
    expected_atom_ids: tuple[str, ...]   # ordered by ideal rank; empty if irrelevant
    expected_relations: tuple[tuple[str, str, str], ...] = field(default_factory=tuple)  # (src, rel_type, tgt)
    sealed: bool = False             # True for the 5 sealed queries
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "qid": self.qid,
            "query_text": self.query_text,
            "query_type": self.query_type.value,
            "expected_atom_ids": list(self.expected_atom_ids),
            "expected_relations": [list(r) for r in self.expected_relations],
            "sealed": self.sealed,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TestQuery":
        return cls(
            qid=d["qid"],
            query_text=d["query_text"],
            query_type=QueryType(d["query_type"]),
            expected_atom_ids=tuple(d["expected_atom_ids"]),
            expected_relations=tuple(tuple(r) for r in d.get("expected_relations", [])),
            sealed=bool(d.get("sealed", False)),
            notes=d.get("notes", ""),
        )


@dataclass(frozen=True)
class QueryResult:
    """A system's answer to one query."""
    qid: str
    returned_atom_ids: tuple[str, ...]                 # ranked list
    returned_relations: tuple[tuple[str, str, str], ...] = field(default_factory=tuple)
    latency_ms: float = 0.0
    raw_scores: tuple[float, ...] = field(default_factory=tuple)  # per-atom similarity / confidence

    def to_dict(self) -> dict:
        return {
            "qid": self.qid,
            "returned_atom_ids": list(self.returned_atom_ids),
            "returned_relations": [list(r) for r in self.returned_relations],
            "latency_ms": float(self.latency_ms),
            "raw_scores": list(self.raw_scores),
        }


# ============================================================
# Persistence helpers
# ============================================================


def save_atoms(atoms: list[Atom], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for a in atoms:
            f.write(json.dumps(a.to_dict(), ensure_ascii=False) + "\n")


def load_atoms(path: Path) -> list[Atom]:
    path = Path(path)
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(Atom.from_dict(json.loads(line)))
    return out


def save_relations(relations: list[Relation], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in relations:
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")


def load_relations(path: Path) -> list[Relation]:
    path = Path(path)
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(Relation.from_dict(json.loads(line)))
    return out


def save_test_queries(qs: list[TestQuery], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([q.to_dict() for q in qs], f, indent=2, ensure_ascii=False)


def load_test_queries(path: Path) -> list[TestQuery]:
    path = Path(path)
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [TestQuery.from_dict(q) for q in data]
