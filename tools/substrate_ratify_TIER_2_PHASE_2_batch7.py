"""TIER-2 PHASE-2 batch 7 ratify -- 1 atom RULE_orthogonal_architecture_axes_tools_vs_materials CONFIRMED."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType


def main():
    label = 'TIER-2-PHASE-2(b7)'
    src_tag = 'PHASE_2_batch_7_RULE_orthogonal_architecture_axes_tools_vs_materials_13th_EPISTEMIC_PROMOTED_CONFIRMED_AAA3_DEFINITIVE_4_witnesses_user_origin_craftsman'
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    meta_store = ps._store_for(Corpus.META)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels}', flush=True)

    new_id = 'RULE_orthogonal_architecture_axes_tools_vs_materials'
    if meta_store.get_atom(new_id) is not None:
        print(f'[{label}] HARD_FAIL: meta::{new_id} already exists')
        return 1

    compose_tgt = 'RULE_universal_operators_field_specific'  # batch 5
    if meta_store.get_atom(compose_tgt) is None:
        print(f'[{label}] HARD_FAIL: COMPOSES target missing meta::{compose_tgt}')
        return 1
    print(f'[{label}] 0 collision; COMPOSES target verified (no phantom)', flush=True)

    atom = Atom(
        id=new_id,
        name='Methodology rule (CONFIRMED PROMOTED AAA3; 13th EPISTEMIC; collides with 13th USER-LOCKED): orthogonal architecture axes TOOLS vs MATERIALS',
        corpus=Corpus.META,
        tier=Tier.TIER_METHODOLOGY,
        kind=AtomKind.METHODOLOGY_RULE,
        description=(
            'Substrate architecture distinguishes TOOLS (substrate-load-bearing capability primitives the operators '
            'USE to do work -- e.g. addition, inner_product, convolution, fhrr_bind, axioms; a small ~35-50 STABLE '
            'set) from MATERIALS (epistemically-foundational content the substrate WORKS ON -- theorems, wikidata '
            'facts, article extracts; grows with ingest). These are ORTHOGONAL axes, NOT a single tier ladder; '
            'conflating them produces incorrect promotion semantics (citation-foundational != operationally-load-'
            "bearing). USER craftsman distinction verbatim: 'a book cited by 1M books isn't necessarily USEFUL... "
            "ADDITION is extraordinarily foundational... different worlds'. Locked as a 3-AXIS architecture: Axis 1 "
            'epistemic tier (T0-T3; CHTV-1 + L6-PROOF + KP), Axis 2 substrate-load-bearing (TOOLS vs MATERIALS; the '
            'NOVEL axis), Axis 3 content-type (FORMAL/INFORMAL/RECORDS/EPISODIC). KP P6 = operator-code-audit '
            'detection of load-bearing atoms (not statistical promotion).'
        ),
        metadata=dict(
            rule_scheme='METHODOLOGY_EPISTEMIC',
            rule_number_provenance=(
                'cited as 13th methodology (EPISTEMIC family) -- COLLIDES with the 13th USER-LOCKED '
                '(active-state-check); disambiguated via name + rule_scheme + rule_class per DECISION 236. '
                'PROMOTED candidate->CONFIRMED via AAA3 DEFINITIVE in substrate_AAA3_DEFINITIVE 2026-06-13.'
            ),
            rule_class='SUBSTRATE_DERIVED',
            user_origin=True,
            user_origin_quote='USER craftsman tools-vs-materials distinction: book cited 1M times not necessarily USEFUL vs ADDITION extraordinarily foundational',
            confirmed_or_candidate='CONFIRMED',
            confirmed=True,
            witnesses_count=4,
            promoted_via='4_witnesses_PROVISIONAL_1p33x_INTRINSIC_3of3_DEFINITIVE_2p34x_p_0p0005_USER_craftsman_corroboration_plus_Cell3_foundational_not_frequency_plus_KP_P6_orthogonal_tagging_3_axis_ARCHITECTURALLY_LOCKED',
            frozen=True,
            term_class='PROCESS_KNOWLEDGE_NON_MATH',
            prose_source='substrate_architecture_two_orthogonal_axes + substrate_3_axis_EMPIRICALLY_ORTHOGONAL + substrate_AAA3_DEFINITIVE_13th_rule_PROMOTED 2026-06-13',
            numbering_collision_note='13th EPISTEMIC vs 13th USER-LOCKED RULE_active_state_check (PHASE-1); both keep number 13 in their family; disambiguated by name + rule_scheme + rule_class per DECISION 236 (same pattern as 11th-collision note on RULE_substrate_internal_no_llm)',
            axis_1_epistemic_tier='T0-T3 CHTV-1 + L6-PROOF + KP',
            axis_2_substrate_load_bearing='TOOLS_vs_MATERIALS_novel_axis',
            axis_3_content_type='FORMAL_INFORMAL_RECORDS_EPISODIC',
            tools_examples='addition_inner_product_convolution_fhrr_bind_axioms_35_50_stable_set',
            materials_examples='theorems_wikidata_facts_article_extracts_grows_with_ingest',
            eleventh_rule_clean=True,
            substrate_internal_verified=True,
            source=src_tag,
        ),
        solution_history=tuple(),
    )
    meta_store.add_atom(atom, source=src_tag, note='13th EPISTEMIC PROMOTED CONFIRMED AAA3')
    print(f'[{label}]   +meta::{new_id} [CONFIRMED PROMOTED AAA3]', flush=True)

    ps.add_relation(
        f'meta::{new_id}',
        RelationType.COMPOSES,
        f'meta::{compose_tgt}',
        source=src_tag,
        note=f'13th orthogonal-axes COMPOSES 12th universal-operators (operators USE these load-bearing primitives)',
    )
    meta_store._flush_relations()
    print(f'[{label}]   +1 COMPOSES edge (-> 12th universal-operators)', flush=True)

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    invariants_ok = (
        post_atoms == pre_atoms + 1
        and post_rels == pre_rels + 1
        and meta_store.get_atom(new_id) is not None
    )
    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} (+{post_rels-pre_rels})', flush=True)
    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1
    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 13th EPISTEMIC CONFIRMED PROMOTED (collision-handled per DECISION 236)')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
