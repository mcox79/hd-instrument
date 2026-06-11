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

    Per Research ALGEBRA_VEC_SUPPORT_PLUS_SCHOOLS_CORPUS 2026-06-11
    (user direction: represent schools of thought): fourth partition SCHOOL
    holds intellectual lineage atoms (VSA / FHRR, HMM, cognitive architecture,
    etc.) linked to math primitives via CONTRIBUTES_TO / TRACES_TO and to
    other schools via INFLUENCED_BY. Enables provenance + unexplored-field
    discovery.
    """
    MATH = "math"
    CONCEPT = "concept"
    META = "meta"      # methodology rules, architectural decisions, failure modes
    SCHOOL = "school"  # intellectual lineage; key_contributors + core_methods

    # Per Research FINDINGS_08_VALIDATE_METHODOLOGY_PARTITION 2026-06-11:
    # SUBSTRATE-PROPOSED partition (Type D self-improvement signal). 4 NOVEL
    # atoms cluster as multi-operation methodological content (verification +
    # exploration + orchestration). Distinct from math/concept/meta/school/
    # results-history/decision-history/findings-history.
    METHODOLOGY = "methodology"

    # Per Research SUBSTRATE_AS_FULL_RESEARCH_LEDGER + AUTO_INGEST_VIA_EVOLVE_PY
    # 2026-06-11. Four ledger partitions auto-ingested from project artifacts:
    RESEARCH_HISTORY = "research_history"   # notes/research_drill_*_2x_*.md
    DECISION_HISTORY = "decision_history"   # notes/research_to_*.md + user directives
    RESULTS_HISTORY = "results_history"     # notes/exp_dev_to_research_*.md
    FINDINGS_HISTORY = "findings_history"   # notes/testbed_to_research_*.md
    VERDICT_HISTORY = "verdict_history"     # strategy_decisions_*.md cap_map cycles
    MEMORY_HISTORY = "memory_history"       # C:/Users/marsh/.claude/projects/.../memory/*.md


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
    SCHOOL = "school"      # per Research SCHOOLS_CORPUS proposal; school atoms only
    CAPABILITY = "capability"  # per Research concept-corpus 8-field schema; concept atoms
    METHODOLOGY = "methodology"  # per FINDINGS_08_VALIDATE_METHODOLOGY_PARTITION
                                  # substrate-proposed: multi-operation methodological content

    # Per Research full-research-ledger auto-ingest 2026-06-11:
    DRILL = "drill"               # research drill outputs
    DECISION = "decision"         # routing notes + user directives
    RESULT = "result"             # Exp-Dev result reports
    FINDING = "finding"           # Testbed findings notes
    VERDICT = "verdict"           # cap_map cycle verdicts (PP-NNN HARD_PASS/MIDDLE/HARD_FAIL)
    MEMORY = "memory"             # memory entries from .claude/projects/.../memory/*.md


# Per Research ALGEBRA_VEC_REFINED_13_CATEGORY 2026-06-11 (drill output):
# 13 categories on 3 axes; category 13 'substrate_native' is the novel
# substrate-distinguishing category (phasor / bipolar / role-filler binding)
# that classical formal systems don't model.
ALGEBRA_CATEGORIES = (
    # Axis A: Classical algebra
    "group", "ring", "field", "vector_space", "module",
    # Axis B: Generalized
    "monoid", "semigroup", "semiring", "lattice",
    # Axis C: Structural/applied
    "category", "topology", "metric_space",
    # Substrate-native (novel)
    "substrate_native",
)


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
    EQUIVALENT_UNDER = "EQUIVALENT_UNDER"  # A = B under transformation T (FFT-dual,
                                            # semiring-shift, etc.); fidelity in note

    # Within concept corpus
    ENABLES = "ENABLES"                 # A makes B possible
    VALIDATES = "VALIDATES"             # A confirms B (e.g. multi-seed validates n=1)
    REFUTES = "REFUTES"                 # A contradicts B
    DEPENDS_ON = "DEPENDS_ON"           # A requires B

    # Cross-corpus (concept <-> math)
    USES = "USES"                       # concept -> math operation
    HAS_USERS = "HAS_USERS"             # math operation -> concepts (auto-derived reverse of USES)

    # Cross-corpus (school <-> math; school <-> school)
    CONTRIBUTES_TO = "CONTRIBUTES_TO"   # school -> math operation it produced
    TRACES_TO = "TRACES_TO"             # math -> school (auto-derived reverse of CONTRIBUTES_TO)
    INFLUENCED_BY = "INFLUENCED_BY"     # school -> earlier school it inherits from


# ============================================================
# Dataclasses
# ============================================================


@dataclass(frozen=True)
class Atom:
    """One knowledge unit in the substrate self-index.

    `id` is the stable identifier (e.g., "T2/fhrr_bind", "PP-364"). Within a single
    Corpus partition (math / concept / meta), ids are unique.
    `name` is the human-readable short name.
    `corpus` is the partition the atom lives in (controls which Store holds it).
    `tier` is the Tier classification (math) or TIER_NA (concept / meta).
    `kind` is the role classification (PRIMITIVE / FAMILY_TAG / SUB_OP / MACRO);
        defaults to PRIMITIVE.
    `description` is the multi-sentence English description that gets bge-encoded.
    `aliases` are alternate names that should match in retrieval.
    `metadata` is free-form (e.g., complexity class, paper reference).

    Fully qualified atom id is `{corpus.value}::{id}` -- e.g., `math::T2/fhrr_bind`.
    The partitioned-store coordinator handles cross-store relations using these
    qualified ids.
    """
    id: str
    name: str
    corpus: Corpus
    tier: Tier
    description: str
    kind: AtomKind = AtomKind.PRIMITIVE
    aliases: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict = field(default_factory=dict)

    # Per Research ALGEBRA_VEC_SUPPORT 2026-06-11: structured algebraic-properties
    # for math atoms (None for non-math atoms). Sub-vectors composed from these
    # fields contribute to the composite atom vector when populated.
    algebra: Optional[dict] = None         # {structure, commutative, associative,
                                            #  identity, inverse, distributes_over,
                                            #  domain}
    signature: Optional[dict] = None       # {input_arity, input_types,
                                            #  output_type, preserves: {...}}
    complexity: Optional[dict] = None      # {time_class, space_class,
                                            #  parallelism, online}
    equivalences: tuple[dict, ...] = field(default_factory=tuple)
                                            # [{equivalent_to, under_transformation,
                                            #   fidelity}, ...]
    concept_links: tuple[str, ...] = field(default_factory=tuple)
                                            # Per Research ALGEBRA_VEC_REFINED 2026-06-11:
                                            # cross-corpus atom_ids (math -> concept,
                                            # math -> school). Substrate-product
                                            # differentiator: classical formal systems
                                            # (Lean/Coq/Mathematica) have no equivalent.

    @property
    def qualified_id(self) -> str:
        return f"{self.corpus.value}::{self.id}"

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "name": self.name,
            "corpus": self.corpus.value,
            "tier": self.tier.value,
            "kind": self.kind.value,
            "description": self.description,
            "aliases": list(self.aliases),
            "metadata": dict(self.metadata),
        }
        if self.algebra is not None:
            d["algebra"] = dict(self.algebra)
        if self.signature is not None:
            d["signature"] = dict(self.signature)
        if self.complexity is not None:
            d["complexity"] = dict(self.complexity)
        if self.equivalences:
            d["equivalences"] = [dict(e) for e in self.equivalences]
        if self.concept_links:
            d["concept_links"] = list(self.concept_links)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Atom":
        """Construct Atom from dict, normalizing Research's flat-metadata format.

        Two formats accepted natively (no external normalizer needed):

        1. Dedicated top-level fields (preferred going forward):
           {algebra: {structure, ...}, signature: {...}, complexity: {...},
            concept_links: [...]}

        2. Flat metadata format (Research batch 02 refined atoms):
           {metadata: {algebra_category: 1-13, domain: "R^N",
                       concept_links: [...], commutative: bool, ...}}

        Format-2 fields are lifted into dedicated fields at construct time.
        Idempotent: format-1 atoms pass through unchanged.
        """
        meta = dict(d.get("metadata", {}))
        algebra = d.get("algebra")
        signature = d.get("signature")
        complexity = d.get("complexity")
        concept_links = d.get("concept_links")

        # Format 2 -> Format 1 lifting
        if algebra is None and ("algebra_category" in meta or "domain" in meta):
            algebra = {}
            if "algebra_category" in meta:
                cat = meta.pop("algebra_category")
                algebra["category_int"] = cat
                if isinstance(cat, int) and 1 <= cat <= 13:
                    algebra["structure"] = ALGEBRA_CATEGORIES[cat - 1]
            for key in ("domain", "commutative", "associative",
                        "preserves_unit_modulus", "identity", "inverse"):
                if key in meta:
                    algebra[key] = meta.pop(key)

        if signature is None and any(k in meta for k in ("input_arity", "input_types", "output_type")):
            signature = {}
            for key in ("input_arity", "input_types", "output_type", "preserves"):
                if key in meta:
                    signature[key] = meta.pop(key)

        if complexity is None and any(k in meta for k in ("time_class", "space_class", "parallelism")):
            complexity = {}
            for key in ("time_class", "space_class", "parallelism", "online"):
                if key in meta:
                    complexity[key] = meta.pop(key)

        if concept_links is None and "concept_links" in meta:
            concept_links = list(meta.pop("concept_links"))

        # Concept-corpus 8-field schema (per Research INDEX_FINDINGS_03_RESPONSE):
        # decomposes_to / family_tag_members / validated_axis / tier_concept /
        # empirical_validation_status / drill_origin / related_concepts /
        # substrate_lever. Pull into metadata for now; ingest tool converts
        # decomposes_to + related_concepts into typed-edge relations.
        for ck in ("decomposes_to", "family_tag_members", "validated_axis",
                   "tier_concept", "empirical_validation_status",
                   "drill_origin", "related_concepts", "substrate_lever"):
            if ck in d and ck not in meta:
                meta[ck] = d[ck]

        return cls(
            id=d["id"],
            name=d["name"],
            corpus=Corpus(d["corpus"]),
            tier=Tier(d.get("tier", "NA")),
            kind=AtomKind(d.get("kind", "primitive")),
            description=d["description"],
            aliases=tuple(d.get("aliases", [])),
            metadata=meta,
            algebra=algebra,
            signature=signature,
            complexity=complexity,
            equivalences=tuple(d.get("equivalences", [])),
            concept_links=tuple(concept_links) if concept_links else tuple(),
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
