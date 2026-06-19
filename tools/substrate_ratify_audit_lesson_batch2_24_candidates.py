"""Audit-lesson batches 2a + 2b combined ratify: 24 CANDIDATE atoms (instances 45-70 minus 53/66 already in-store).

All CANDIDATE; 1 witness (except 64th flagged 3 witnesses but NOT promoted per Amendment 3 strict).
COMPOSES family parent by lesson_class: epistemic->91, structural->53, procedural->66, framing->91.
All targets in-store (PHASE-1 9da528ca).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType


# class -> COMPOSES parent
CLASS_PARENT = {
    'epistemic': 'AUDIT_verify_not_assume_prior_lesson_applied',
    'structural': 'AUDIT_dont_fabricate_grounding',
    'procedural': 'AUDIT_integrator_pre_ratify_catch',
    'framing': 'AUDIT_verify_not_assume_prior_lesson_applied',
}


def make_atom_spec(id_short, instance_num, lesson_class, desc, witnesses_count=1, extra=None):
    return dict(
        id=f'AUDIT_{id_short}',
        instance_number=instance_num,
        lesson_class=lesson_class,
        description=desc,
        witnesses_count=witnesses_count,
        extra_metadata=extra or {},
    )


def main():
    label = 'AUDIT-LESSON-BATCH-2'
    src_tag = 'audit_lesson_batch_2_24_CANDIDATE_atoms_ledger_v1_entries_11_34_instances_45_70_memory_enumeration_director_RATIFIED_recipe_Ruling_2_refinement'
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    meta_store = ps._store_for(Corpus.META)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels}', flush=True)

    # batch 2a: instances 45-57
    atoms = [
        make_atom_spec('hygiene_pattern_over_extension_director_dispatch', 45, 'procedural',
                       'Hygiene-pattern over-extension on a Director dispatch (Wave-4 retracted) -- a cleanup pattern applied beyond its validated scope; caught + retracted.'),
        make_atom_spec('type_aware_authoring_provenance', 46, 'structural',
                       'Type-aware authoring provenance (FORM-A): new-atom authoring stamps type/form provenance so downstream can audit the authoring class.'),
        make_atom_spec('sibling_probe_failure_as_integrity_dimension', 47, 'structural',
                       'A sibling-probe failure is itself an integrity dimension (a failing sibling check signals a real structural gap, not noise to discard).'),
        make_atom_spec('atom_prose_overclaim_from_smoke_inflation', 48, 'epistemic',
                       'Atom-prose can over-claim by inflating a SMOKE result to full-grade language; catch the smoke-vs-full inflation at the prose layer.'),
        make_atom_spec('smoke_vs_full_corroboration_scale_verification', 49, 'procedural',
                       'Corroboration must verify at the SAME scale as the claim (smoke corroboration does not corroborate a full-scale claim).'),
        make_atom_spec('11th_rule_learned_layer_catch_on_corroboration_cell', 50, 'structural',
                       '11th-rule (substrate-internal/no-LLM) catch on a corroboration cell -- a learned-vector layer (lap3_rotate) EXCLUDED to keep the demonstration substrate-internal.'),
        make_atom_spec('run_mode_discipline_empirically_validated_by_rerun', 51, 'procedural',
                       'run_mode discipline (smoke vs full) empirically validated by the rerun distribution matching expectation.'),
        make_atom_spec('atom_prose_overclaim_catch_and_arbitrate', 52, 'epistemic',
                       'Atom-prose over-claim catch-and-arbitrate discipline (REVISED from PATTERN): when prose over-claims vs the cell verdict, catch + arbitrate to the honest verdict.'),
        make_atom_spec('bilateral_kappa_external_anchor', 54, 'epistemic',
                       'Bilateral kappa as an external anchor -- inter-rater agreement against an external rater anchors a claim beyond self-assessment.'),
        make_atom_spec('control_leak_caught_at_sanity', 55, 'structural',
                       'A control leak caught at the sanity-check stage (Exp-Dev C0 pre-dedup catch) -- a leak in the control condition found before it contaminated the result.'),
        make_atom_spec('forward_work_on_every_wake_cross_session_adoption', 56, 'procedural',
                       'Forward-work-on-every-wake adopted cross-session (the no-idle-stand discipline operationalized across all sessions, not just one).'),
        make_atom_spec('counting_logic_reconciliation_discipline', 57, 'epistemic',
                       'Counting-logic reconciliation discipline (MOTIF-B 28 vs 31) -- when two counts disagree, reconcile the counting logic rather than pick one.'),
        # batch 2b: instances 58-65 + 67-70
        make_atom_spec('document_citation_motif_as_soft_gerrymander', 58, 'structural',
                       'Document-citation motif as a soft gerrymander (11/31 doc-citations; canonical 20 math-scoped) -- citation count can soft-inflate scope; canonicalize to the math-scoped set.'),
        make_atom_spec('cross_session_counting_diff_resolves_to_deeper_scope_finding', 59, 'epistemic',
                       "A cross-session counting difference resolves to a deeper SCOPE finding (the diff isn't an error to pick from -- it reveals a scope distinction)."),
        make_atom_spec('USER_interpretation_relay_vs_direct', 60, 'framing',
                       'USER-interpretation relay vs direct (DECISION 165 superseded; USER-direct is authoritative over a relayed interpretation).'),
        make_atom_spec('cross_drill_convergent_finding_qualified', 61, 'epistemic',
                       'A cross-drill convergent finding must be QUALIFIED per the shared-source caveat (convergence across drills sharing a source is not independent corroboration).'),
        make_atom_spec('empirical_witness_overrides_shared_source_lit_prior', 62, 'epistemic',
                       'An empirical witness OVERRIDES a shared-source literature prior (Exp-Dev STAGE-1.2) -- measurement beats a lit-prior even when several lit sources agree (shared source).'),
        make_atom_spec('smoke_validation_vs_full_claim_scoping', 63, 'procedural',
                       'Smoke-validation vs full-claim scoping (Director over-claim caught) -- a smoke validation scopes only a smoke claim; a full claim needs full validation.'),
        make_atom_spec('auto_verdict_overclaim_catch_via_verify_before_asserting', 64, 'epistemic',
                       "Auto-verdict over-claim catch via verify-before-asserting -- a cell's autonomous PASS verdict checked against the honest filed disposition (ARM-3 dual-label).",
                       witnesses_count=3,
                       extra={'NOTE_3_same_day_witnesses_NOT_promoted_per_Amendment_3': 'ternary leak / FPE grid / C3 class-vs-unique; cross-cell-distinctness verification pending'}),
        make_atom_spec('compute_allocation_underestimate_caught_by_USER_thermal', 65, 'procedural',
                       'Compute-allocation underestimate caught by USER thermal observation (laptop overheating on a C0 graded run mis-classified as thermal-safe).'),
        make_atom_spec('remote_dispatch_error_caught_via_prover_self_check', 67, 'procedural',
                       "A remote-dispatch error caught via the Prover's self-check (verify-before-asserting on own dispatch)."),
        make_atom_spec('pre_precheck_grounding_resolution_proactive', 68, 'procedural',
                       'Pre-precheck grounding-resolution done PROACTIVELY per a prior-arm lesson (resolve grounding deps before the precheck, having learned from the prior arm).'),
        make_atom_spec('cross_arm_contamination_check_pre_ratify', 69, 'structural',
                       'Cross-arm contamination check pre-ratify (ARM-2 deps verified to contain NO ARM-1 cleanup contamination before ratify).'),
        make_atom_spec('qualified_finding_filed_without_overclaim_cross_session_consensus', 70, 'framing',
                       'A QUALIFIED finding filed without over-claim via cross-session consensus (ARM-3 C3: cell auto-PASS but filed QUALIFIED on uniqueness ground, agreed across sessions).'),
    ]

    # Pre-receive: collision check
    for a in atoms:
        if meta_store.get_atom(a['id']) is not None:
            print(f'[{label}] HARD_FAIL: meta::{a["id"]} already exists')
            return 1

    # Pre-receive: COMPOSES targets
    targets = set(CLASS_PARENT.values())
    for t in targets:
        if meta_store.get_atom(t) is None:
            print(f'[{label}] HARD_FAIL: COMPOSES target missing meta::{t}')
            return 1
    print(f'[{label}] {len(atoms)} collisions clean; {len(targets)} COMPOSES parents verified (PHASE-1 family)', flush=True)

    n_edges = 0
    for spec in atoms:
        compose_parent = CLASS_PARENT[spec['lesson_class']]
        metadata = dict(
            lesson_class=spec['lesson_class'],
            confirmed_or_candidate='CANDIDATE',
            witnesses_count=spec['witnesses_count'],
            instance_number=spec['instance_number'],
            instance_number_provenance=f'cited as {spec["instance_number"]}th in substrate_director_session_2026_06_16 memory enumeration; ledger v1 entry',
            term_class='PROCESS_KNOWLEDGE_NON_MATH',
            NOT_load_bearing_until_3_witnesses=(spec['witnesses_count'] < 3),
            prose_source='skunkworks_ledger_v1 audit_lesson batches 2a+2b memory_enumeration_45_70_director_RATIFIED_recipe',
            eleventh_rule_clean=True,
            substrate_internal_verified=True,
            source=src_tag,
            **spec['extra_metadata'],
        )
        atom = Atom(
            id=spec['id'],
            name=f'Audit lesson (CANDIDATE; instance {spec["instance_number"]}; {spec["lesson_class"]}): {spec["id"][6:60]}',
            corpus=Corpus.META,
            tier=Tier.TIER_METHODOLOGY,
            kind=AtomKind.AUDIT_LESSON,
            description=spec['description'],
            metadata=metadata,
            solution_history=tuple(),
        )
        meta_store.add_atom(atom, source=src_tag, note=f'audit_lesson batch 2 {spec["id"]}')

        ps.add_relation(
            f'meta::{spec["id"]}',
            RelationType.COMPOSES,
            f'meta::{compose_parent}',
            source=src_tag,
            note=f'audit_lesson batch 2 {spec["id"]} COMPOSES {compose_parent}',
        )
        n_edges += 1
    meta_store._flush_relations()
    print(f'[{label}]   +{len(atoms)} atoms; +{n_edges} COMPOSES edges (class-parent family)', flush=True)

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    invariants_ok = (
        post_atoms == pre_atoms + len(atoms)
        and post_rels == pre_rels + n_edges
        and all(meta_store.get_atom(a['id']) is not None for a in atoms)
    )
    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} (+{post_rels-pre_rels})', flush=True)
    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1
    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 24 audit_lesson CANDIDATE atoms (instances 45-70 minus 53+66 in-store) + {n_edges} COMPOSES')
    print(f'  All CANDIDATE; 64th has 3 witnesses but NOT promoted per Amendment 3 strict')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
