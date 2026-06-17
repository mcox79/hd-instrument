"""Audit-lesson catalog batch 1 ratify -- 6 CANDIDATE atoms (today's-new from ledger v1).

Per Skunkworks ledger v1 VET RATIFY + Ruling 3 (atomize 6 today's-new now).

  meta::AUDIT_director_ratify_prose_method_contingent (entry 5; 1 witness; 235d)
  meta::AUDIT_director_drill_synthesis_substrate_internal_search (entry 6; 1 witness; 234)
  meta::AUDIT_numbering_scheme_overload_time_drift_at_atomization (entry 7; 2 witnesses; 236c HOLD per Ruling 1)
  meta::AUDIT_auditor_cited_ledger_prose_without_verification (entry 8; 1 witness; 236f)
  meta::AUDIT_substrate_canonical_field_pollution (entry 9; 1 witness; 237c)
  meta::AUDIT_atomizer_drop_criterion_loses_older_schema_records (entry 10; 1 witness; 237d)

6 COMPOSES edges (entry 10's natural-parent edge to 92nd OMITTED per Skunkworks conservative literal spec;
Skunkworks will wire 237d<->92nd dual edge as follow-up batch).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType


def main():
    label = 'AUDIT-LESSON-BATCH-1'
    src_tag = 'audit_lesson_batch_1_6_CANDIDATE_atoms_ledger_v1_RATIFY_skunkworks_ruling_3_atomize_today_new'
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    meta_store = ps._store_for(Corpus.META)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels}', flush=True)

    atoms_spec = [
        dict(
            id='AUDIT_director_ratify_prose_method_contingent',
            name='Audit lesson (CANDIDATE; entry 5; 1 witness; 235d): Director-ratify-prose must carry method-contingent qualifier',
            instance_number=235,  # 235d
            description=(
                'When the Director ratifies via prose, a measured bound must carry the METHOD/CONFIG-contingent '
                'qualifier (not stated as fundamental); USER caught the over-generalization. Verify-not-assume at '
                'the Director-ratify-prose layer.'
            ),
            lesson_class='framing',
            witnesses_count=1,
            first_witness='2026-06-16 DECISION 235b (USER method-contingent correction; folded throughout P2 prose)',
            instance_number_provenance='cited as 235d in skunkworks audit_catalog finding; ledger entry 5',
            composes=['AUDIT_verify_not_assume_prior_lesson_applied'],
        ),
        dict(
            id='AUDIT_director_drill_synthesis_substrate_internal_search',
            name='Audit lesson (CANDIDATE; entry 6; 1 witness; 234): drill synthesis via substrate-internal search first',
            instance_number=234,
            description=(
                'Drill/synthesis should search the substrate internally first (substrate-internal-search) rather '
                'than re-derive externally. Verify-not-assume at the drill-synthesis layer.'
            ),
            lesson_class='procedural',
            witnesses_count=1,
            first_witness='2026-06-16 DECISION 234 (drill synthesis via substrate-internal search)',
            instance_number_provenance='ledger entry 6; today 5-new',
            composes=['RULE_verify_before_asserting'],
        ),
        dict(
            id='AUDIT_numbering_scheme_overload_time_drift_at_atomization',
            name='Audit lesson (CANDIDATE; entry 7; 2 witnesses; 236c; HOLD per Ruling 1): numbering scheme overload + time drift at atomization',
            instance_number=236,  # 236c
            description=(
                'Bare canonical numbers drift across sources/time at atomization; resolve via by-NAME slug + '
                'instance_number_provenance STRING (DECISION 236). Witnessed at methodology-rule layer + '
                'audit-catalog layer.'
            ),
            lesson_class='structural',
            witnesses_count=2,
            first_witness='2026-06-16 DECISION 236 (methodology-rule numbering collisions)',
            extra_metadata={
                'second_witness': '2026-06-16 DECISION 238 (audit-catalog status/count drift; Skunkworks finding)',
                'HOLD_at_2_per_Skunkworks_Ruling_1': 'Amendment-3 strict no-inflation; 3rd witness must be from genuinely distinct layer (not audit-catalog-numbering manifestation)',
            },
            instance_number_provenance='cited as 236c; 2 witnesses; HOLD per Skunkworks Ruling 1 (do not promote on borderline 3rd)',
            composes=['AUDIT_verify_not_assume_prior_lesson_applied'],
        ),
        dict(
            id='AUDIT_auditor_cited_ledger_prose_without_verification',
            name='Audit lesson (CANDIDATE; entry 8; 1 witness; 236f; self-logged by Skunkworks): auditor cited ledger prose without metric verification',
            instance_number=236,  # 236f
            description=(
                'The AUDITOR cited a ledger-PROSE line as a measured result without metric verification (the 236e '
                'ACF-rescue figure); caught by the Prover. Provenance binds to METRICS not prose -- applies to the '
                "auditor's OWN surfaces. (Self-logged after my own error.)"
            ),
            lesson_class='epistemic',
            witnesses_count=1,
            first_witness='2026-06-16 DECISION 236f (Skunkworks cited a cap-map PROSE figure as a metric result; Prover caught it)',
            extra_metadata={
                'self_logged_by_auditor': True,
                '19th_rule_witness': 'adversarial_self_correction_of_own_output_at_auditor_layer',
            },
            instance_number_provenance='cited as 236f; ledger entry 8',
            composes=['AUDIT_verify_not_assume_prior_lesson_applied', 'RULE_verify_before_asserting'],
        ),
        dict(
            id='AUDIT_substrate_canonical_field_pollution',
            name='Audit lesson (CANDIDATE; entry 9; 1 witness; 237c): substrate canonical field pollution; serves_capability 94% non-disambiguating',
            instance_number=237,  # 237c
            description=(
                'A substrate canonical metadata field can be over-set until it no longer disambiguates '
                '(serves_capability 94%); detect at atomization + exclude as a signal. Surfaced by the Tier-3 '
                'atomizer.'
            ),
            lesson_class='structural',
            witnesses_count=1,
            first_witness='2026-06-16 DECISION 237c (serves_capability set on 24653/26303 = 94% -> non-disambiguating)',
            instance_number_provenance='cited as 237c; ledger entry 9',
            composes=['AUDIT_dont_fabricate_grounding'],
        ),
        dict(
            id='AUDIT_atomizer_drop_criterion_loses_older_schema_records',
            name='Audit lesson (CANDIDATE; entry 10; 1 witness; 237d; DUAL of 92nd): atomizer drop criterion silently loses older-schema records',
            instance_number=237,  # 237d
            description=(
                'An atomizer drop criterion can silently DISCARD substantive records (older-schema; no verdict '
                'field) = false-negative loss; the DUAL of phantom-dep (false-positive). Catch via reading a '
                'dropped cell. (caught-by-cert-owner-VET.)'
            ),
            lesson_class='structural',
            witnesses_count=1,
            first_witness='2026-06-16 DECISION 237d (drop criterion silently lost older-schema pre-build experiments)',
            extra_metadata={
                'DUAL_of_92nd': 'AUDIT_phantom_dep_pre_ratify',
                'natural_parent_edge_OMITTED_pending_92nd_in_store': True,
                'NOTE': '92nd already landed at 52789caf; Skunkworks will wire 237d<->92nd dual edge as follow-up batch per their conservative literal spec',
            },
            instance_number_provenance='cited as 237d; ledger entry 10; DUAL of the 92nd phantom-dep (false-negative vs false-positive)',
            composes=[],  # Skunkworks conservatively omits per recursive phantom-dep discipline; will wire after 92nd lands (or as follow-up since 92nd IS now in-store)
        ),
    ]

    # Collision check
    for s in atoms_spec:
        if meta_store.get_atom(s['id']) is not None:
            print(f'[{label}] HARD_FAIL: meta::{s["id"]} already exists')
            return 1

    # Verify COMPOSES targets
    all_compose_targets = set()
    for s in atoms_spec:
        for t in s['composes']:
            all_compose_targets.add(t)
    for t in all_compose_targets:
        if meta_store.get_atom(t) is None:
            print(f'[{label}] HARD_FAIL: COMPOSES target missing meta::{t}')
            return 1
    print(f'[{label}] 6 collisions clean; {len(all_compose_targets)} unique COMPOSES targets verified (no phantom)', flush=True)

    # Author atoms
    n_edges = 0
    for s in atoms_spec:
        metadata = dict(
            lesson_class=s['lesson_class'],
            confirmed_or_candidate='CANDIDATE',
            witnesses_count=s['witnesses_count'],
            instance_number=s['instance_number'],
            instance_number_provenance=s['instance_number_provenance'],
            first_witness=s['first_witness'],
            term_class='PROCESS_KNOWLEDGE_NON_MATH',
            NOT_load_bearing_until_3_witnesses=(s['witnesses_count'] < 3),
            prose_source='skunkworks_ledger_v1 audit_lesson batch 1 today_new',
            eleventh_rule_clean=True,
            substrate_internal_verified=True,
            source=src_tag,
        )
        if 'extra_metadata' in s:
            metadata.update(s['extra_metadata'])
        atom = Atom(
            id=s['id'],
            name=s['name'],
            corpus=Corpus.META,
            tier=Tier.TIER_METHODOLOGY,
            kind=AtomKind.AUDIT_LESSON,
            description=s['description'],
            metadata=metadata,
            solution_history=tuple(),
        )
        meta_store.add_atom(atom, source=src_tag, note=f'audit_lesson batch 1 entry')
        print(f'[{label}]   +meta::{s["id"]} [CANDIDATE; {s["witnesses_count"]} witness]', flush=True)

        # Add COMPOSES edges for this atom
        for tgt in s['composes']:
            ps.add_relation(
                f'meta::{s["id"]}',
                RelationType.COMPOSES,
                f'meta::{tgt}',
                source=src_tag,
                note=f'audit_lesson batch 1 {s["id"]} COMPOSES {tgt}',
            )
            n_edges += 1
    meta_store._flush_relations()
    print(f'[{label}]   +{n_edges} COMPOSES edges (entry 10 dual-to-92nd OMITTED per Skunkworks literal spec; Skunkworks will wire as follow-up)', flush=True)

    # R3 invariants
    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())

    invariants_ok = (
        post_atoms == pre_atoms + 6
        and post_rels == pre_rels + n_edges
        and all(meta_store.get_atom(s['id']) is not None for s in atoms_spec)
    )

    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} (+{post_rels-pre_rels})', flush=True)

    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1

    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 6 audit_lesson CANDIDATE atoms + {n_edges} COMPOSES edges')
    print(f'  All 1-witness; 1 atom (237d) DUAL of 92nd with edge conservatively omitted')
    print(f'  HOLD at 2 (236c numbering-overload) per Skunkworks Ruling 1')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
