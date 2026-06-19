"""BATCH 26 ingest: 12 MOTIVATION + TIME substrate primitives (INFORMAL_SYSTEMS content-type).

Per research_to_testbed_T1_T2_BATCH_26_MOTIVATION_TIME_substrate_primitives_*.md
(LANE C T1.15 priority). 12 philosophy-of-action + philosophy-of-time atoms per
USER architecture extension (philosophy as 4th content_type after FORMAL_SYSTEMS,
RECORDS, EPISODIC).

NEW fields on atoms (stored in metadata dict since Atom dataclass already supports
free-form metadata):
  - content_type: FORMAL_SYSTEMS / INFORMAL_SYSTEMS / RECORDS / EPISODIC
  - substrate_load_bearing: bool (True = substrate operators USE this; False = substrate KNOWS but doesn't USE)

Tolerant of missing source atoms (warn + skip rather than fail) per BATCH 17
established pattern. Local laptop substrate likely doesn't have causation_concept_general
or conditional_probability so some edges will skip-warn locally.

NO LLM. NO bge. Pure schema work; no heat.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


# Atom specs: (local_id, name, tier, aliases, description, content_type, substrate_load_bearing,
#              serves_capability, science_algebra_category, signature_hint, depends_on)
BATCH_26_ATOMS = [
    # ---- MOTIVATION primitives (philosophy of action) ----
    {
        "id": "T1/intentionality_aboutness_relation",
        "name": "Intentionality (aboutness)",
        "tier": Tier.TIER_1_FOUNDATIONAL,
        "aliases": ("aboutness", "brentano_aboutness", "intentional_content"),
        "description": (
            "Mental state has intentional content; is ABOUT some object or concept; reference "
            "relation explicit (Brentano 1874). Aboutness-directedness, propositional content, "
            "intensional not extensional."
        ),
        "content_type": "INFORMAL_SYSTEMS",
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_self_knowledge_aboutness", "motivation_ruleset_foundation"),
        "science_algebra_category": "informal_systems::philosophy_of_action::intentionality",
        "signature_hint": "aboutness_relation_axiom",
        "is_axiom": True,
        "depends_on": (),
    },
    {
        "id": "T1/goal_directedness_telos",
        "name": "Goal-directedness (telos)",
        "tier": Tier.TIER_1_FOUNDATIONAL,
        "aliases": ("telos", "aristotelian_telos", "final_cause"),
        "description": (
            "Directedness-toward-end; Aristotelian telos (final cause); Davidson 1963 'Actions, "
            "Reasons and Causes'."
        ),
        "content_type": "INFORMAL_SYSTEMS",
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_master_plan_telos", "motivation_ruleset_means_end"),
        "science_algebra_category": "informal_systems::philosophy_of_action::teleology",
        "signature_hint": "telos_directedness_toward_end",
        "is_axiom": False,
        "depends_on": ("math::T1/intentionality_aboutness_relation",),
    },
    {
        "id": "T2/practical_reason_anscombe",
        "name": "Practical reason (Anscombe)",
        "tier": Tier.TIER_2_PRIMITIVE,
        "aliases": ("practical_syllogism", "anscombe_intention"),
        "description": (
            "Reasoning about what to DO not what is the case (Anscombe 1957); practical "
            "syllogism + means-end reasoning."
        ),
        "content_type": "INFORMAL_SYSTEMS",
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_decision_making", "master_plan_reasoning"),
        "science_algebra_category": "informal_systems::philosophy_of_action::practical_reason",
        "signature_hint": "practical_reasoning_about_action",
        "is_axiom": False,
        "depends_on": ("math::T1/goal_directedness_telos", "math::T1/intentionality_aboutness_relation"),
    },
    {
        "id": "T2/agency_higher_order_desire_frankfurt",
        "name": "Higher-order desire agency (Frankfurt)",
        "tier": Tier.TIER_2_PRIMITIVE,
        "aliases": ("frankfurt_freedom_of_will", "second_order_endorsement"),
        "description": (
            "Frankfurt 1971 hierarchy of desires; first-order desire wants X; second-order desire "
            "wants to want X; agency = higher-order endorsement; wantonness as failure."
        ),
        "content_type": "INFORMAL_SYSTEMS",
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_recursive_self_improvement_higher_order",
                              "master_plan_endorsement"),
        "science_algebra_category": "informal_systems::philosophy_of_action::agency",
        "signature_hint": "higher_order_desire_endorsement",
        "is_axiom": False,
        "depends_on": ("math::T2/practical_reason_anscombe",
                       "math::T1/intentionality_aboutness_relation"),
    },
    {
        "id": "T2/bratman_planning_theory",
        "name": "Bratman planning theory",
        "tier": Tier.TIER_2_PRIMITIVE,
        "aliases": ("bratman_intentions_plans", "planning_agency"),
        "description": (
            "Bratman 1987 'Intentions Plans and Practical Reason'; planning agency = future-directed "
            "intentions + plans as structures of practical reasoning; partial plans + plan filtering "
            "+ reconsideration resistance."
        ),
        "content_type": "INFORMAL_SYSTEMS",
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_master_plan_structure", "future_directed_intention"),
        "science_algebra_category": "informal_systems::philosophy_of_action::planning",
        "signature_hint": "planning_as_practical_reasoning_structure",
        "is_axiom": False,
        "depends_on": ("math::T2/practical_reason_anscombe",
                       "math::T2/agency_higher_order_desire_frankfurt"),
    },
    # ---- TIME-BASED primitives (philosophy of time + temporal logic) ----
    {
        "id": "T1/a_series_indexical_temporal_NOW",
        "name": "A-series indexical temporal (NOW pointer)",
        "tier": Tier.TIER_1_FOUNDATIONAL,
        "aliases": ("mctaggart_a_series", "indexical_PAST_PRESENT_FUTURE"),
        "description": (
            "McTaggart 1908 A-series; indexical temporal predicates past/present/future relative to "
            "NOW pointer; presentism-compatible; NOW pointer required."
        ),
        "content_type": "INFORMAL_SYSTEMS",
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_NOW_pointer", "agent_temporal_reasoning"),
        "science_algebra_category": "informal_systems::philosophy_of_time::a_series",
        "signature_hint": "indexical_temporal_NOW_axiom",
        "is_axiom": True,
        "depends_on": (),
    },
    {
        "id": "T1/b_series_relational_temporal",
        "name": "B-series relational temporal (earlier/later)",
        "tier": Tier.TIER_1_FOUNDATIONAL,
        "aliases": ("mctaggart_b_series", "earlier_than_later_than"),
        "description": (
            "McTaggart B-series; relational earlier-than/later-than predicates; permanent + not "
            "indexical; eternalist-compatible; no NOW required."
        ),
        "content_type": "INFORMAL_SYSTEMS",
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_commit_history_temporal", "B_series_event_ordering"),
        "science_algebra_category": "informal_systems::philosophy_of_time::b_series",
        "signature_hint": "relational_temporal_earlier_later",
        "is_axiom": True,
        "depends_on": (),
    },
    {
        "id": "T2/diachronic_identity_persistence_parfit",
        "name": "Diachronic identity (Parfit)",
        "tier": Tier.TIER_2_PRIMITIVE,
        "aliases": ("parfit_personal_identity", "psychological_continuity"),
        "description": (
            "Parfit 1984 personal identity across time; persistence via psychological continuity + "
            "connectedness vs branching; what-matters not identity."
        ),
        "content_type": "INFORMAL_SYSTEMS",
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_cycle_to_cycle_identity", "cross_cycle_continuity"),
        "science_algebra_category": "informal_systems::philosophy_of_time::diachronic_identity",
        "signature_hint": "psychological_continuity_persistence",
        "is_axiom": False,
        "depends_on": ("math::T1/b_series_relational_temporal",
                       "math::T1/a_series_indexical_temporal_NOW"),
    },
    {
        "id": "T2/causal_intervention_pearl",
        "name": "Causal intervention (Pearl do-operator)",
        "tier": Tier.TIER_2_PRIMITIVE,
        "aliases": ("pearl_causality", "do_operator"),
        "description": (
            "Pearl 2009 causal hierarchy 1-2-3; level 2 intervention do(X=x) counterfactual; "
            "substrate's recursive loop Stage 4 verify-fix-spec IS intervention; structural causal "
            "model."
        ),
        "content_type": "INFORMAL_SYSTEMS",
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_recursive_loop_Stage_4_intervention", "causal_inference"),
        "science_algebra_category": "informal_systems::philosophy_of_time::causation",
        "signature_hint": "interventional_do_operator",
        "is_axiom": False,
        "depends_on": ("math::T1/conditional_probability",),
    },
    {
        "id": "T2/counterfactual_dependence_lewis",
        "name": "Counterfactual dependence (Lewis)",
        "tier": Tier.TIER_2_PRIMITIVE,
        "aliases": ("lewis_counterfactuals", "possible_worlds_semantics"),
        "description": (
            "Lewis 1973 'Counterfactuals'; counterfactual If A had not occurred, C would not occur; "
            "closeness of possible worlds semantics; sphere system over worlds."
        ),
        "content_type": "INFORMAL_SYSTEMS",
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_recursive_loop_Stage_6_regression_check",
                              "counterfactual_reasoning"),
        "science_algebra_category": "informal_systems::philosophy_of_time::counterfactuals",
        "signature_hint": "possible_world_similarity_counterfactual",
        "is_axiom": False,
        "depends_on": ("math::T2/causal_intervention_pearl",),
    },
    {
        "id": "T2/linear_temporal_logic_LTL",
        "name": "Linear Temporal Logic (LTL; Pnueli)",
        "tier": Tier.TIER_2_PRIMITIVE,
        "aliases": ("LTL", "pnueli_temporal_logic"),
        "description": (
            "Pnueli 1977 Linear Temporal Logic; modal operators X (next) F (eventually) G (always) "
            "U (until); LTL formula evaluated over infinite linear sequence of states; "
            "model-checking decidable."
        ),
        "content_type": "FORMAL_SYSTEMS",  # LTL is mathematically formalizable
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_state_sequence_specification", "model_checking_substrate"),
        "science_algebra_category": "informal_systems::philosophy_of_time::temporal_logic",
        "signature_hint": "linear_temporal_modal_operators",
        "is_axiom": False,
        "depends_on": ("math::T1/b_series_relational_temporal",),
    },
    {
        "id": "T2/computation_tree_logic_CTL",
        "name": "Computation Tree Logic (CTL; Clarke-Emerson)",
        "tier": Tier.TIER_2_PRIMITIVE,
        "aliases": ("CTL", "branching_time_logic"),
        "description": (
            "Clarke + Emerson 1981 CTL; branching-time modal logic; path quantifiers A (all) E (exists) "
            "over temporal operators; model-checking decidable polynomial."
        ),
        "content_type": "FORMAL_SYSTEMS",
        "substrate_load_bearing": False,
        "serves_capability": ("substrate_branching_state_specification", "model_checking_substrate"),
        "science_algebra_category": "informal_systems::philosophy_of_time::temporal_logic",
        "signature_hint": "branching_time_modal_logic",
        "is_axiom": False,
        "depends_on": ("math::T2/linear_temporal_logic_LTL",),
    },
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    # --- Step 1: author 12 new atoms ---
    created = 0
    skipped_exists = 0
    failed = 0
    for spec in BATCH_26_ATOMS:
        qid = f"math::{spec['id']}"
        if ps.has_atom(qid):
            print(f"  ATOM SKIP (exists): {qid}")
            skipped_exists += 1
            continue
        try:
            atom = Atom(
                id=spec["id"],
                name=spec["name"],
                corpus=Corpus.MATH,
                tier=spec["tier"],
                description=spec["description"],
                kind=AtomKind.PRIMITIVE,
                aliases=spec["aliases"],
                metadata={
                    "science_algebra_category": spec["science_algebra_category"],
                    "signature_hint": spec["signature_hint"],
                    "is_axiom": spec["is_axiom"],
                    "content_type": spec["content_type"],
                    "substrate_load_bearing": spec["substrate_load_bearing"],
                    "batch_origin": "batch_26_motivation_time_informal_systems",
                },
                serves_capability=spec["serves_capability"],
            )
            ps.add_atom(
                atom,
                source="t1_t2_batch_26_motivation_time_informal_systems",
                note="BATCH 26 philosophy primitives per Research LANE C T1.15 + USER architecture extension",
            )
            print(f"  ATOM CREATED: {qid} [{spec['content_type']}]")
            created += 1
        except Exception as e:
            print(f"  ATOM FAIL: {qid}: {str(e)[:120]}")
            failed += 1

    print(f"\n  atoms: created={created} skipped_exists={skipped_exists} failed={failed}")

    # --- Step 2: DEPENDS_ON edges ---
    existing_edges = set()
    for r in ps.iter_all_relations():
        try:
            existing_edges.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    added = 0
    skipped_miss_tgt = 0
    skipped_dup = 0
    edge_failed = 0
    for spec in BATCH_26_ATOMS:
        src_qid = f"math::{spec['id']}"
        if not ps.has_atom(src_qid):
            continue
        for tgt_qid in spec["depends_on"]:
            if not ps.has_atom(tgt_qid):
                print(f"  EDGE SKIP_MISS_TGT: {src_qid} -> {tgt_qid}")
                skipped_miss_tgt += 1
                continue
            key = (src_qid, "DEPENDS_ON", tgt_qid)
            if key in existing_edges:
                print(f"  EDGE SKIP_DUP: {src_qid} -> {tgt_qid}")
                skipped_dup += 1
                continue
            try:
                ps.add_relation(
                    src_qid, RelationType.DEPENDS_ON, tgt_qid,
                    source="t1_t2_batch_26_motivation_time_informal_systems",
                    note="BATCH 26 philosophy primitive DEPENDS_ON per Research LANE C T1.15",
                )
                print(f"  EDGE ADD: {src_qid} DEPENDS_ON {tgt_qid}")
                added += 1
            except Exception as e:
                msg = str(e)[:120]
                if any(k in msg.lower() for k in ("already", "exists", "duplicate")):
                    skipped_dup += 1
                else:
                    print(f"  EDGE FAIL: {src_qid} -> {tgt_qid}: {msg}")
                    edge_failed += 1

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== BATCH 26 SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  atom created: {created} / skipped_exists: {skipped_exists} / failed: {failed}")
    print(f"  edge added: {added}")
    print(f"  edge skipped_miss_tgt: {skipped_miss_tgt}")
    print(f"  edge skipped_dup: {skipped_dup}")
    print(f"  edge failed: {edge_failed}")
    print(f"\nPre-reg KPI:")
    print(f"  atoms target: +12 (10 INFORMAL + 2 FORMAL philosophy primitives)")
    print(f"  edges target: +12 (intra-batch + 1 external = T1/conditional_probability for Pearl)")
    print(f"  content_type axis NOW POPULATED with INFORMAL_SYSTEMS classification")
    print(f"  substrate_load_bearing axis: all 12 atoms = False (KNOWS not USES)")


if __name__ == "__main__":
    main()
