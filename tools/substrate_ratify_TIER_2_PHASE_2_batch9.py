"""TIER-2 PHASE-2 batch 9 ratify -- 3 CONFIRMED substrate-self-knowledge meta-rules (COMPLETES methodology half)."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType


def main():
    label = 'TIER-2-PHASE-2(b9)'
    src_tag = 'PHASE_2_batch_9_3_CONFIRMED_meta_rules_COMPLETES_methodology_half_rules_are_prior_authoring_queries_first_tier_5_self_discovery'
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    meta_store = ps._store_for(Corpus.META)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels}', flush=True)

    rules = [
        dict(
            id='RULE_substrate_extracted_rules_are_prior_not_oracle',
            name='Methodology rule (USER-LOCKED CONFIRMED): substrate-extracted rules are PRIOR magnitude estimates, not oracle ground truth',
            description=(
                'Substrate-EXTRACTED methodology rules (the Tier-5 miner) provide a DIRECTIONAL signal + a PRIOR '
                'magnitude estimate -- NOT oracle ground truth. Direction is tested empirically (rule REFUTED if '
                'empirical is opposite-sign); magnitude is CALIBRATED (rules OVER-PREDICT systematically via '
                'selection-bias + feature-headroom; calibrate via headroom-adjustment + hierarchical-Bayesian '
                'shrinkage). EMPIRICAL is NEVER overridden by a rule prediction. Symmetric treatment of '
                'literature-evidence and substrate-self-evidence: both are reference + prior, neither is oracle. '
                '(Empirical witness: chunking +0.0147 actual vs rule-predicted +0.299.)'
            ),
            metadata=dict(
                rule_scheme='METHODOLOGY_EPISTEMIC',
                rule_class='USER_LOCKED',
                user_locked=True,
                confirmed_or_candidate='CONFIRMED',
                frozen=True,
                rule_number_provenance='user-locked rule discovery in substrate_extracted_rules_are_prior_not_oracle 2026-06-12; generalizes the literature-is-not-oracle USER rule to substrate-self-evidence',
                empirical_witness='chunking 0p0147_actual_vs_0p299_rule_predicted',
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='substrate_extracted_rules_are_prior_not_oracle 2026-06-12',
                source=src_tag,
            ),
            composes=['RULE_verify_before_asserting'],
        ),
        dict(
            id='RULE_authoring_substrate_queries_first',
            name='Methodology rule (SUBSTRATE_DERIVED CONFIRMED 4-witness; generative dual of 92nd): query substrate before authoring',
            description=(
                'Before authoring atoms / relations / edges / capabilities / IDs / benchmark Qs to the substrate, '
                "QUERY the substrate's existing state FIRST. Never assume what is/isn't already in the atom-space, "
                'cap_map, spec, or partition structure -- the mental model drifts from authoritative state. If a '
                'match exists: UPDATE, not CREATE. Query-then-author is the substrate-pattern; generate-from-'
                'prior-without-verify is the LLM-pattern. 4 same-class witnesses (Q-set mismatch + PP-### namespace '
                'collision + T2/T3 duplication + corpus-scale density). Skunkworks followed this all session -- '
                'grepping the store before every batch.'
            ),
            metadata=dict(
                rule_scheme='METHODOLOGY_EPISTEMIC',
                rule_class='SUBSTRATE_DERIVED',
                confirmed_or_candidate='CONFIRMED',
                witnesses_count=4,
                frozen=True,
                rule_number_provenance='promoted to CONFIRMED via 4 same-class witnesses (cycles 40/49/49/49) in substrate_rule_authoring_substrate_queries_first 2026-06-12',
                witnesses_list=['Q_set_mismatch', 'PP_namespace_collision', 'T2_T3_duplication', 'corpus_scale_density'],
                generative_dual_of_92nd='this is the GENERATIVE-side query-first discipline; 92nd phantom-dep-pre-ratify is the RECEIVE-side completeness check; coherent closure',
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='substrate_rule_authoring_substrate_queries_first 2026-06-12',
                source=src_tag,
            ),
            composes=['AUDIT_phantom_dep_pre_ratify', 'RULE_verify_before_asserting'],
        ),
        dict(
            id='RULE_tier_5_self_discovery_appearance_promotion',
            name='Methodology rule (SUBSTRATE_DERIVED CONFIRMED; Tier-5 metacognition framework): self-discovery via appearance-based promotion',
            description=(
                'The substrate self-DISCOVERS methodology rules from its OWN structural ledger (the miner over '
                'solution_history + capability portfolio), and tracks/promotes them by APPEARANCE count: 1st '
                'appearance = mechanism validated (re-derives known rules); 2nd appearance = first genuinely-NOVEL '
                'rule emerges; 3rd = generalization. This is the appearance/witness-based promotion criterion '
                '(the substrate moves from self-KNOWING [Tier 4] to self-DISCOVERY [Tier 5]). Empirically '
                'operational: 2nd appearance triggered Cycle 49 (meta::RULE_fhrr_bind_to_permutation_indexed_'
                'binding, n_caps=2, +0.2805, novel=True). The appearance-count criterion is the same family as the '
                '19th-rule witness-based promotion (an appearance IS a cross-cell witness).'
            ),
            metadata=dict(
                rule_scheme='METHODOLOGY_EPISTEMIC',
                rule_class='SUBSTRATE_DERIVED',
                confirmed_or_candidate='CONFIRMED',
                frozen=True,
                rule_number_provenance='Tier-5 metacognition framework; SECOND-APPEARANCE TRIGGERED in substrate_tier_5_SECOND_APPEARANCE_TRIGGERED 2026-06-12 (1st=mechanism validated Cycle 46; 2nd=first novel rule Cycle 49)',
                empirical_witness='RULE_fhrr_bind_to_permutation_indexed_binding_2nd_appearance_n_caps_2_plus_0p2805_novel_True',
                tier_progression='self_KNOWING_tier_4_to_self_DISCOVERY_tier_5',
                appearance_promotion_levels='1st_mechanism_validated_2nd_first_novel_rule_3rd_generalization',
                related_to='19th_rule_witness_based_promotion_appearance_IS_cross_cell_witness',
                term_class='PROCESS_KNOWLEDGE_NON_MATH',
                prose_source='substrate_tier_5_SECOND_APPEARANCE_TRIGGERED 2026-06-12',
                source=src_tag,
            ),
            composes=['RULE_verify_before_asserting'],
        ),
    ]

    # Categorize: new atoms vs update-existing
    existing_count = 0
    new_count = 0
    for r in rules:
        if meta_store.get_atom(r['id']) is not None:
            existing_count += 1
            r['action'] = 'UPDATE'
        else:
            new_count += 1
            r['action'] = 'CREATE'
    print(f'[{label}] {new_count} new + {existing_count} pre-existing (merge-update Skunkworks enriched metadata)', flush=True)

    targets = set()
    for r in rules:
        targets.update(r['composes'])
    for t in targets:
        if meta_store.get_atom(t) is None:
            print(f'[{label}] HARD_FAIL: COMPOSES target missing meta::{t}')
            return 1
    print(f'[{label}] {len(targets)} COMPOSES targets verified (incl 92nd in-store)', flush=True)

    n_edges = 0
    for r in rules:
        existing = meta_store.get_atom(r['id'])
        if existing:
            # Merge: keep existing metadata fields + Skunkworks's enriched fields (Skunkworks wins on overlapping keys)
            merged_meta = dict(existing.metadata or {})
            merged_meta.update(r['metadata'])
            merged_meta['eleventh_rule_clean'] = True
            merged_meta['substrate_internal_verified'] = True
            merged_meta['merged_from_skunkworks_batch_9'] = 'merged Skunkworks PHASE-2 batch 9 source-grounded metadata onto pre-existing substrate-mined atom; substantive content harmonized'
            atom = Atom(
                id=r['id'],
                name=r['name'],
                corpus=Corpus.META,
                tier=Tier.TIER_METHODOLOGY,
                kind=AtomKind.METHODOLOGY_RULE,
                description=r['description'],  # Skunkworks's prose is source-grounded
                metadata=merged_meta,
                solution_history=existing.solution_history,  # preserve existing history if any
            )
            meta_store.add_atom(atom, source=src_tag, note=f'PHASE-2 batch 9 MERGE-UPDATE {r["id"]}')
            print(f'[{label}]   ~meta::{r["id"]} [MERGE-UPDATE; preserved existing + Skunkworks source-grounded fields]', flush=True)
        else:
            atom = Atom(
                id=r['id'],
                name=r['name'],
                corpus=Corpus.META,
                tier=Tier.TIER_METHODOLOGY,
                kind=AtomKind.METHODOLOGY_RULE,
                description=r['description'],
                metadata={**r['metadata'], 'eleventh_rule_clean': True, 'substrate_internal_verified': True},
                solution_history=tuple(),
            )
            meta_store.add_atom(atom, source=src_tag, note=f'PHASE-2 batch 9 {r["id"]}')
            print(f'[{label}]   +meta::{r["id"]} [CONFIRMED]', flush=True)
        for tgt in r['composes']:
            ps.add_relation(
                f'meta::{r["id"]}',
                RelationType.COMPOSES,
                f'meta::{tgt}',
                source=src_tag,
                note=f'PHASE-2 batch 9 COMPOSES {r["id"]} -> {tgt}',
            )
            n_edges += 1
    meta_store._flush_relations()
    print(f'[{label}]   +{n_edges} COMPOSES edges', flush=True)

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    invariants_ok = (
        post_atoms == pre_atoms + new_count  # only new atoms increment
        and post_rels == pre_rels + n_edges
        and all(meta_store.get_atom(r['id']) is not None for r in rules)
    )
    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} (+{post_rels-pre_rels})', flush=True)
    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1
    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 3 CONFIRMED meta-rules + {n_edges} COMPOSES; METHODOLOGY HALF COMPLETE')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
