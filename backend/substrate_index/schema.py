"""Data model for substrate self-index pilot.

Atoms are knowledge units (one math operation, one substrate primitive, one PP row,
one capability assertion). Relations are typed edges between atoms. Two corpora
(math and concept) are linked by USES (concept -> math) and HAS_USERS (math ->
concept; auto-derived reverse).

Per Research SUBSTRATE_SELF_INDEX_PILOT 2026-06-11 spec.
"""
from __future__ import annotations

import enum
import os
import json
import time
import itertools
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

    # Per Research SCIENCE_BATCH_01 2026-06-11 + USER massive math+science ingestion directive:
    # SCIENCE partition with 13-category algebra taxonomy (mirror of math) per FINDINGS #18 Gap 6.
    SCIENCE = "science"

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
    TIER_LEXICON = "T_lexicon"  # per Research NER_GAZETTEER_8: lexicon atoms in concept partition
    TIER_METHODOLOGY = "T_methodology"  # per FINDINGS_13: meta-rule atoms
    TIER_SCHOOL = "T_school"  # per Research SCHOOLS_BATCH_01: school-of-thought atoms


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
    LEXICON = "lexicon"          # per NER_GAZETTEER_8: entity-type gazetteer atoms
    METHODOLOGY_RULE = "methodology_rule"  # per FINDINGS_13 Tier 4: meta partition
                                            # atoms; human-authored OR substrate-extracted
                                            # from solution-history cliff patterns
    CROSS_DISC_ANALOGUE = "cross_disc_analogue"  # per CROSS_DISCIPLINE_ANALOGUES_BATCH_01
                                                  # 2026-06-12: brain/physics/chem -> math
                                                  # primitive grounding atoms (GROUNDS edges)
    MWP_SCHEMA = "mwp_schema"  # per Research MWP_WK_SCHEMAS_BATCH_01 2026-06-12:
                                # math word problem schema templates
    MWP_ROLE = "mwp_role"      # per Research MWP_WK_SCHEMAS_BATCH_01 2026-06-12:
                                # math word problem role definitions

    # Per Research full-research-ledger auto-ingest 2026-06-11:
    DRILL = "drill"               # research drill outputs
    DECISION = "decision"         # routing notes + user directives
    RESULT = "result"             # Exp-Dev result reports
    FINDING = "finding"           # Testbed findings notes
    VERDICT = "verdict"           # cap_map cycle verdicts (PP-NNN HARD_PASS/MIDDLE/HARD_FAIL)
    MEMORY = "memory"             # memory entries from .claude/projects/.../memory/*.md

    # Per Research DECISION 220b + Skunkworks TIER-2 atomization spec 2026-06-16
    # (ratified DECISION 222a + Testbed pre-receive VET 05fd0af8):
    AUDIT_LESSON = "audit_lesson"               # Tier-A audit-discipline lessons
                                                 # (88 confirmed + candidates); composes_with
                                                 # related lessons; confirmed_or_candidate +
                                                 # witnesses_count fields enforce CANDIDATE !=
                                                 # CONFIRMED discipline (Skunkworks condition 1)
    EXPERIMENT_RECORD = "experiment_record"     # Tier-B experiment records (for Tier-3
                                                 # atomizer); relevance_tier-filtered
                                                 # HIGH/MEDIUM/LOW/ARCHIVE
    DECISION_RECORD = "decision_record"         # Tier-B decision records;
                                                 # decision_class STRATEGIC/OPERATIONAL/ROUTINE
    HONEST_SIGNAL_RECORD = "honest_signal_record"  # Tier-C archive (per Skunkworks
                                                    # condition 4 RECO: git-only, not bulk-
                                                    # atomized; schema defined for on-demand use)
    COMMUNICATION_RECORD = "communication_record"  # Tier-C archive (same Skunkworks
                                                    # condition 4 RECO)
    RESEARCH_FINDING = "research_finding"        # Tier-B research findings (STEP-B research-onboarding
                                                 # atomizer); confidence_tier T0_PROVEN/T1_TESTED_PARTIAL/
                                                 # T2_RESEARCH_SUPPORTED/T3_HYPOTHESIS; NO algebra field
                                                 # (structural guard: excluded from axiom_term; never
                                                 # current_best_solution unless cert-promoted). research-
                                                 # being-wrong is STRUCTURALLY SAFE (queryable, never trusted)
    PROOF_RECORD = "proof_record"                # Tier-B formal-proof records (Lean formal-oracle; PHASE-2).
                                                 # metadata.confidence_tier = T0_PROVEN_FORMAL (the top trust
                                                 # tier, formal-proven). NO algebra field (SAME structural
                                                 # guard as RESEARCH_FINDING: excluded from axiom_term; the
                                                 # formal-proven identity is queryable PROVEN-FORMAL knowledge,
                                                 # NOT auto-promoted to the proven-core; axiom_term promotion is
                                                 # a SEPARATE explicit USER/PHASE-III authority). Skunkworks
                                                 # SEMANTICS-MATCH VET gates creation (P_lean == P_substrate;
                                                 # exact-not-approximate; real-not-complex). Per Skunkworks
                                                 # corrected-model 2026-06-18 (kind separate from trust-tier;
                                                 # USER+Research CONCUR; NOT a kind literally named T0_PROVEN_FORMAL)
    SCIENCE_CONCEPT = "science_concept"          # Tier-B science-ontology concept records (Bucket B2 GO ingest,
                                                 # PHASE-2 2026-06-18; Skunkworks plan-VET R2: biology ontology
                                                 # DISTINCT from LEXICON [lexical] -- a separate kind). NO algebra
                                                 # field (SAME structural guard as LEXICON/RESEARCH_FINDING/
                                                 # PROOF_RECORD: corpus=SCIENCE + algebra=None -> excluded from
                                                 # axiom_term; ontology concepts are queryable SCIENCE knowledge,
                                                 # NOT proven-core/current_best_solution). Internal ontology
                                                 # relations (is_a/part_of) carried as METADATA fields (mirrors
                                                 # the WordNet hypernym/hyponym-as-metadata rule). Skunkworks
                                                 # SCHEMA-VET confirms the enum-add at the B2 dry-run.
    CAPABILITY_MAP = "capability_map"            # Meta aggregation/INDEX atom over existing CERT atoms (Director-
                                                 # authored substrate-breadth-map; 2026-06-18; Skunkworks 432-map
                                                 # VET APPROVE per genuinely-distinct-role; pending pre-Store-write
                                                 # FINAL VET). TWO MANDATORY STRUCTURAL GUARDS: (a) NO algebra field
                                                 # (SAME guard as RESEARCH_FINDING/PROOF_RECORD/SCIENCE_CONCEPT:
                                                 # excluded from axiom_term -> axiom_term unchanged); (b)
                                                 # provenance_quality MUST NOT be CERT_CHAIN_GRADE (an INVENTORY
                                                 # pointing AT cert atoms, NEVER itself cert-counted -> CERT count
                                                 # unchanged by this kind). Distinct from CAPABILITY (single-concept
                                                 # with 8-field schema + serves_capability linkage); a capability-
                                                 # map is an AGGREGATION over many cert atoms with regeneratable
                                                 # scour-query metadata. Domain heuristics carry "approximate"
                                                 # qualifier (11th-rule clean: substring-match not LLM categorization).
    SEMANTIC_FRAME = "semantic_frame"            # FrameNet ARC-3 ingest (Item 2; USER-GO 2026-06-18; Skunkworks
                                                 # discretion). One atom per FrameNet frame (id=FN_<framename>,
                                                 # corpus=CONCEPT). STRUCTURAL GUARDS (same as SCIENCE_CONCEPT):
                                                 # (a) NO algebra field -> excluded from axiom_term; (b)
                                                 # provenance_quality=RESEARCH_FINDING (T2 non-load-bearing until
                                                 # cert-promoted by experiment). LU lemmas carried as METADATA;
                                                 # frame-to-frame relations as first-class FRAME_* rel_types.
    PHASE_PORTRAIT = "phase_portrait"            # Director-authored substrate operating-regime INVENTORY atom
                                                 # (Item 3, 20h sprint; USER 2026-06-18; Skunkworks SCHEMA-VET
                                                 # PASS sub-counts-verified). Sibling to CAPABILITY_MAP: a meta
                                                 # AGGREGATION over measured cert atoms (CERT_CHAIN_GRADE +
                                                 # MEASURED_MECHANISM) inventorying the substrate's measured
                                                 # operating regimes (N / alpha / kappa / encoder / readout /
                                                 # task-complexity / backbone-density / corpus-class). SAME TWO
                                                 # MANDATORY STRUCTURAL GUARDS as CAPABILITY_MAP: (a) NO algebra
                                                 # field -> excluded from axiom_term; (b) provenance_quality MUST
                                                 # NOT be CERT_CHAIN_GRADE (INVENTORY_NON_CERT; points AT cert
                                                 # atoms, never itself cert-counted -> CERT unchanged). Measured-
                                                 # only-no-extrapolation cert-condition (LOAD-BEARING per Skunkworks).
    CONCEPT_NODE = "concept_node"                # ConceptNet ARC-3 second-direction ingest (Item 4, 20h sprint;
                                                 # 2026-06-18; apply DEFERRED until push-fix). One atom per ConceptNet
                                                 # english concept (id=CN_<concept>, namespaced -> 0 cross-corpus id
                                                 # collision; lemma-overlap with WordNet WN_/LEXICON EXPECTED, not a
                                                 # collision). STRUCTURAL GUARDS (same as SEMANTIC_FRAME/SCIENCE_CONCEPT):
                                                 # (a) NO algebra field -> excluded from axiom_term; (b)
                                                 # provenance_quality=RESEARCH_FINDING (ingest tier; non-load-bearing
                                                 # until cert-promoted). ConceptNet relations carried as FIRST-CLASS
                                                 # rel_types (IsA->IS_A, PartOf->PART_OF, rest CN_*), NEVER metadata-
                                                 # on-RELATES (the edge-metadata-drop lesson).


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

    # Solution-history (per user 2026-06-11 late evening: each capability has
    # a current-best solution; replacements preserve history not delete):
    SUPERSEDES = "SUPERSEDES"           # new solution -> old solution (replacement)
    SUPERSEDED_BY = "SUPERSEDED_BY"     # old -> new (auto-derived reverse)
    CURRENT_BEST_FOR = "CURRENT_BEST_FOR"  # solution -> capability (it currently solves)

    # Generic fallback for fine-grained semantic relations (math batch 03 Phase A4
    # uses 40 distinct relation types; specific type stored in metadata['relation_subtype']):
    RELATES = "RELATES"                  # generic semantic relation
    GENERALIZES = "GENERALIZES"          # A generalizes B (B is a specific case of A)
    INSTANCE_OF = "INSTANCE_OF"          # A is an instance of B
    DEFINED_BY = "DEFINED_BY"            # A is defined by B
    DEFINED_OVER = "DEFINED_OVER"        # A is defined over B
    # Per Research SHARES_MATH auto-discovery R2.2 + Exp-Dev commit ab2c2efe (9 math
    # groups seed). Coalgebraic bisimulation equivalence; symbolic-structural
    # categorical (NOT geometric); orthogonal to P4 codebook geometry; preserves
    # P3 KP knowledge-promotion independence.
    SHARES_MATH = "SHARES_MATH"          # A and B share the same underlying math (bisimulation)

    # E2 first-class role rel_types (Bucket-2 TRACK-3 2026-06-18; USER-ratified). Per the
    # reference_store_drops_relation_edge_metadata finding: relation_role on a RELATES edge is
    # SILENTLY DROPPED on flush (3-tuple persistence). Making the role the REL_TYPE persists it
    # in the 3-tuple -> edge-queryable. Replaces RELATES+metadata.relation_role for these roles.
    STRENGTHENS = "STRENGTHENS"          # experiment/result STRENGTHENS a cert (e.g. A3 -> C1-cert)
    MECHANISM_FOR = "MECHANISM_FOR"      # mechanism atom explains a verdict (e.g. A1/A1-v2 -> measured-8a)
    REPLICATES = "REPLICATES"            # a run REPLICATES a prior result/cert

    # Edge-materialization rel_types (Bucket-2 TRACK-3 2026-06-18): materialize the B1 WordNet +
    # B2 GO hierarchy METADATA into TYPED EDGES (the graph is sparse: ~0.19 edges/atom; metadata
    # hierarchies not edge-queryable until materialized). 0-phantom: only when BOTH endpoints exist.
    HYPERNYM = "HYPERNYM"                # WordNet: synset -> its more-general (is-a-kind-of) synset
    IS_A = "IS_A"                        # GO: term -> its superclass term (ontological subsumption)
    PART_OF = "PART_OF"                  # WordNet meronym + GO part_of: part -> whole
    # FrameNet frame-to-frame relations (Item 2 ingest; first-class rel_types per metadata-drop lesson; 2026-06-18):
    FRAME_INHERITS = "FRAME_INHERITS"            # child frame inherits from parent frame (Inheritance)
    FRAME_USES = "FRAME_USES"                    # frame uses another frame (Using)
    FRAME_SUBFRAME = "FRAME_SUBFRAME"            # complex frame decomposes into subframe (Subframe)
    FRAME_PERSPECTIVE_ON = "FRAME_PERSPECTIVE_ON"  # frame is a perspective on a neutral frame (Perspective_on)
    FRAME_PRECEDES = "FRAME_PRECEDES"            # temporal ordering of subframes (Precedes)
    FRAME_INCHOATIVE_OF = "FRAME_INCHOATIVE_OF"  # inchoative (onset) of a state frame (Inchoative_of)
    FRAME_CAUSATIVE_OF = "FRAME_CAUSATIVE_OF"    # causative of a state/event frame (Causative_of)
    FRAME_SEE_ALSO = "FRAME_SEE_ALSO"            # cross-reference between related frames (See_also)
    FRAME_REFRAMING_MAPPING = "FRAME_REFRAMING_MAPPING"  # ReFraming_Mapping (in nltk; scaffold's 8 omitted it)
    FRAME_METAPHOR = "FRAME_METAPHOR"            # Metaphor (in nltk; scaffold's 8 omitted it)
    # ConceptNet ARC-3 second-direction ingest (Item 4, 20h sprint; 2026-06-18; apply DEFERRED until push-fix).
    # ALL ConceptNet relations FIRST-CLASS (rel_types-as-first-class principle; NEVER metadata-on-RELATES -- the
    # edge-metadata-drop lesson). IsA -> IS_A and PartOf -> PART_OF reuse the existing rel_types; the rest are CN_*.
    CN_RELATED_TO = "CN_RELATED_TO"
    CN_HAS_A = "CN_HAS_A"
    CN_USED_FOR = "CN_USED_FOR"
    CN_CAPABLE_OF = "CN_CAPABLE_OF"
    CN_AT_LOCATION = "CN_AT_LOCATION"
    CN_CAUSES = "CN_CAUSES"
    CN_HAS_SUBEVENT = "CN_HAS_SUBEVENT"
    CN_HAS_PREREQUISITE = "CN_HAS_PREREQUISITE"
    CN_HAS_PROPERTY = "CN_HAS_PROPERTY"
    CN_MOTIVATED_BY_GOAL = "CN_MOTIVATED_BY_GOAL"
    CN_OBSTRUCTED_BY = "CN_OBSTRUCTED_BY"
    CN_DESIRES = "CN_DESIRES"
    CN_CREATED_BY = "CN_CREATED_BY"
    CN_SYNONYM = "CN_SYNONYM"
    CN_ANTONYM = "CN_ANTONYM"
    CN_DISTINCT_FROM = "CN_DISTINCT_FROM"
    CN_DERIVED_FROM = "CN_DERIVED_FROM"
    CN_SYMBOL_OF = "CN_SYMBOL_OF"
    CN_DEFINED_AS = "CN_DEFINED_AS"
    CN_MANNER_OF = "CN_MANNER_OF"
    CN_LOCATED_NEAR = "CN_LOCATED_NEAR"
    CN_HAS_CONTEXT = "CN_HAS_CONTEXT"
    CN_SIMILAR_TO = "CN_SIMILAR_TO"
    CN_ETYMOLOGICALLY_RELATED_TO = "CN_ETYMOLOGICALLY_RELATED_TO"
    CN_ETYMOLOGICALLY_DERIVED_FROM = "CN_ETYMOLOGICALLY_DERIVED_FROM"
    CN_CAUSES_DESIRE = "CN_CAUSES_DESIRE"
    CN_MADE_OF = "CN_MADE_OF"
    CN_RECEIVES_ACTION = "CN_RECEIVES_ACTION"
    CN_FORM_OF = "CN_FORM_OF"


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

    # Per user direction 2026-06-11 late evening: each capability has a
    # current-best mathematical solution; replacements DO NOT delete the old
    # entry, they mark it obsolete. Encodes substrate progression history.
    current_best_solution: Optional[str] = None
                                            # Qualified atom_id of the math/algorithm
                                            # primitive that currently solves this
                                            # capability best (e.g.,
                                            # "math::T3/discriminative_perceptron").
    solution_history: tuple[dict, ...] = field(default_factory=tuple)
                                            # Ordered list of all current-bests for
                                            # this capability, most recent first:
                                            # [{solution_atom_id, adopted_date,
                                            #   replaced_date (null = current),
                                            #   replacement_reason, empirical_metric,
                                            #   source, status (current/superseded/
                                            #   reverted)}]
                                            # Captures the substrate's progression
                                            # without losing prior learnings.

    # Per FINDINGS #18 usability-gap analysis 2026-06-11: substrate must know
    # WHICH capabilities each math/concept atom serves so retrieval can be
    # capability-anchored, not just semantic. Reverse index from atom -> caps.
    # Multi-valued: one atom can serve many capabilities (universal levers like
    # discriminative_perceptron serve 11/12 caps per cross_capability_best_overlap).
    serves_capability: tuple[str, ...] = field(default_factory=tuple)
                                            # Qualified capability atom_ids
                                            # (e.g., "concept::cap_mwp_role_assign").
                                            # Populated at ingest (Research-seed)
                                            # OR via substrate-eval inference
                                            # (solution_history reverse-mapping).

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
        if self.current_best_solution is not None:
            d["current_best_solution"] = self.current_best_solution
        if self.solution_history:
            d["solution_history"] = [dict(s) for s in self.solution_history]
        if self.serves_capability:
            d["serves_capability"] = list(self.serves_capability)
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
            current_best_solution=d.get("current_best_solution"),
            solution_history=tuple(d.get("solution_history", [])),
            serves_capability=tuple(d.get("serves_capability", [])),
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


_save_tmp_seq = itertools.count()


def _unique_tmp(path: Path) -> Path:
    """UNIQUE temp path per write (pid + monotonic counter) so CONCURRENT save_atoms/save_relations on the SAME
    partition write DISTINCT tmps -> os.replace = last-writer-wins, NEVER an interleaved/NULL-corrupted SHARED tmp.
    Root-cause fix for the 2026-06-19 concept-partition corruption (two save_atoms(concept) -- bulk ingest + cap-int --
    both wrote concept/atoms.jsonl.tmp -> interleave -> NULL seam -> Store unloadable). Deterministic naming; no
    randomness. pid disambiguates processes; the per-process counter disambiguates concurrent same-process calls."""
    return path.with_suffix(path.suffix + f".tmp.{os.getpid()}.{next(_save_tmp_seq)}")


def _atomic_replace(tmp: Path, path: Path) -> None:
    """os.replace with a bounded retry. On Windows os.replace raises PermissionError (WinError 5/32) if the target is
    momentarily open by a concurrent reader/writer; retry briefly. The unique-tmp ALREADY prevents corruption -- this
    only prevents a transient lock from RAISING under concurrency (last-writer-wins). Raises if still locked after the
    bound (a genuine persistent lock, not transient)."""
    for attempt in range(20):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.02 * (attempt + 1))


def save_atoms(atoms: list[Atom], path: Path) -> None:
    """Atomic write via UNIQUE-temp + fsync + os.replace per Research Pattern 1
    (write-tmp + fsync + os.replace; production-database standard).
    Solves recurring JSONDecodeError race in concurrent readers during ingest
    bursts. Original fix commit 56ff427e (lost across worktree split);
    re-applied a5acfc36; fsync added per atomic-write-shard-swap routing
    2026-06-13; UNIQUE per-write tmp added 2026-06-19 (concurrent-save tmp-collision root-cause fix)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = _unique_tmp(path)
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            for a in atoms:
                f.write(json.dumps(a.to_dict(), ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        _atomic_replace(tmp, path)
    finally:
        if os.path.exists(tmp):  # only lingers if the write threw before os.replace consumed it
            try:
                os.remove(tmp)
            except OSError:
                pass


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
    """Atomic write via UNIQUE-temp + fsync + os.replace per Research Pattern 1
    (UNIQUE per-write tmp added 2026-06-19 -- same concurrent-save tmp-collision fix as save_atoms)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = _unique_tmp(path)
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            for r in relations:
                f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        _atomic_replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


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
    """Atomic write via temp + fsync + os.replace per Research Pattern 1."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump([q.to_dict() for q in qs], f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def load_test_queries(path: Path) -> list[TestQuery]:
    path = Path(path)
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [TestQuery.from_dict(q) for q in data]
