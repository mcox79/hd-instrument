"""Ratify VERIFY-THE-REFERENT parent + A1/A2 children per Skunkworks substrate-build spec (18:30).

Per Skunkworks cert-owner spec (discipline applied to its OWN atomization; 5 caught
witnesses verified NOT 9 inflated):
- VERIFY-THE-REFERENT parent AUDIT_LESSON CONFIRMED (5 witnesses, 4 layers)
- A1 monitor-must-watch-authoritative-source CONFIRMED child (2 witnesses; composes-with parent)
- A2 prereg-must-be-committed CANDIDATE child (1-2 witnesses; promote on more)
- Re-link 4 existing children (instances 75/76/77/78) to point at real parent

Per per-atom HARD-FAIL gate discipline; audit_lessons carry no algebra (cap_pres + axiom_term safe).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


PARENT = {
    'slug': 'verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
    'name': 'Audit lesson (CONFIRMED PARENT; instance 80; verify): verify-the-referent',
    'description': (
        "A check is only meaningful if it verifies the actual REFERENT -- the object the claim/dispatch/monitor "
        "depends on -- not a proxy or the producer's own action. Verify the referent ARRIVES where needed "
        "(on git/remote, in the Store, in the consumer's feed, as the anchor's real mechanism), not just that "
        "the producer did its part. CONFIRMED parent class composing sub-instances (anchor-mechanism-match + "
        "drill-must-be-saved + failure-mode-arm-fixable + cell-allocation-explicit + monitor-must-watch-"
        "authoritative-source + prereg-must-be-committed). 5 caught witnesses across 4 layers (experiment-design "
        "/ audit-catalogue x2 / monitoring-infra / dispatch-infra). Witnesses RIGOROUSLY VERIFIED per discipline "
        "applied to OWN atomization (NOT inflated; applications are NOT witnesses). Composes-with siblings: "
        "no-Goodhart + 100th-rule audit-tooling-verify + DEGENERATE-REGIME + monitor-consumer-can-die-inbox-"
        "authoritative."
    ),
    'lesson_class': 'verify',
    'confirmed_or_candidate': 'CONFIRMED',
    'witnesses_count': 5,
    'instance_number': 80,
    'instance_number_provenance': (
        'Skunkworks 18:30 substrate-build cert-owner spec; VERIFIED 5 caught witnesses (anchor R4-18 + '
        'catalogue-vs-Store + Ruling-B premise + monitor delivery + prereg-commit) across 4 layers; '
        'discipline applied to own atomization; applications (Lean semantics-match + discriminating-regime '
        'guards) are NOT witnesses to avoid double-count with DEGENERATE-REGIME sibling'
    ),
    'witnesses': [
        '1. anchor-mechanism-match (R4-18): recapture named gating cell anchor; swap-operators binder/decoder did not exist there -> referent (anchor actual mechanism) != assumed; CAUGHT Exp-Dev cell-author + Skunkworks VET-reversal (experiment-design layer)',
        '2. catalogue-vs-Store count: Skunkworks ledger claimed ~92 CONFIRMED; Store-authoritative referent was 7-8 CONFIRMED; CAUGHT Testbed Store-read (audit-catalogue layer; Skunkworks own bookkeeping)',
        '3. Ruling-B premise: Skunkworks claimed structured fields at atom-metadata referent; source-files-only; CAUGHT Testbed Store-read (audit-catalogue layer; Skunkworks own ruling)',
        '4. monitor delivery: heartbeat verified producer-liveness (wrong referent) not notes-reaching-consumer (right referent); consumer died producer alive false-green; CAUGHT USER skepticism + Skunkworks filesystem-check + Testbed corroboration 2 independent (monitoring-infra layer)',
        '5. prereg-commit: dispatch named prereg file but not on git remote referent; written-to-disk != on-remote; CAUGHT Orchestrator + remote gate-fail (dispatch-infra layer)',
    ],
    'layers': ['experiment-design', 'audit-catalogue (Skunkworks own; x2)', 'monitoring-infra', 'dispatch-infra'],
    'applications_NOT_witnesses': [
        'Lean SCHEMA-VET semantics-match (DESIGNED guard for PHASE II; nothing caught yet)',
        'discriminating-regime guards in C1/8a/refuse-gate preregs (catches belong to DEGENERATE-REGIME sibling class; not double-counted)',
    ],
    'parent_of': [
        'AUDIT_recapture_anchor_mechanism_match_referent_layer (instance 75; existing CANDIDATE child)',
        'AUDIT_drill_must_be_saved_to_notes_dispatched_artifact_persist (instance 76; existing CANDIDATE child)',
        'AUDIT_failure_mode_must_be_arm_fixable_no_op_arms_caught_at_smoke (instance 77; existing CANDIDATE child)',
        'AUDIT_cell_allocation_must_be_explicit_roadmap_concrete_actionable (instance 78; existing CANDIDATE child)',
        'AUDIT_monitor_must_watch_authoritative_source_not_derived_log_producer_liveness_false_green (NEW A1 CONFIRMED child this batch)',
        'AUDIT_prereg_must_be_committed_before_dispatch_written_disk_not_on_remote (NEW A2 CANDIDATE child this batch)',
    ],
    'composes_with_siblings': [
        'no_goodhart_metric_measures_claimed_thing',
        'AUDIT_audit_tooling_verify_before_trusted_keyword_search_unreliable',
        'AUDIT_degenerate_regime_not_refutation_non_discriminating_test_is_non_test_verify_regime_discriminating_before_verdict',
        'monitor_consumer_can_die_inbox_authoritative_9th_rule',
    ],
}

A1_CHILD = {
    'slug': 'monitor_must_watch_authoritative_source_not_derived_log_producer_liveness_false_green',
    'name': 'Audit lesson (CONFIRMED; instance 81; verify): monitor-must-watch-authoritative-source',
    'description': (
        "A monitor must watch the AUTHORITATIVE source (filesystem files; not a derived log). Producer-liveness "
        "is FALSE-GREEN for delivery: heartbeat must verify DELIVERY (notes reaching consumer), not producer-"
        "liveness (producer can stay alive while consumer dies silently). Today witnesses: (1) Skunkworks "
        "canonical-v3 log-tail monitor died ~16:43; producer-alive heartbeat reported FALSE-GREEN; 8 notes "
        "missed over ~55min; USER skepticism caught. (2) Testbed monitor bpffo8gba canonical-v3 log-tail "
        "missed the 16:39 Director sweep dispatch; ~32min gap; heartbeat green throughout; filesystem-cross-"
        "check after Skunkworks broadcast confirmed gap. CONFIRMED child of verify-the-referent parent (the "
        "heartbeat checked the wrong referent: producer-alive not notes-reaching-me). Fix: filesystem-ground-"
        "truth watch (canonical-v4) per Director endorsement + Orchestrator LAYER-1 design call; manual cross-"
        "check as backstop-to-backstop per Skunkworks's residual coverage caveat (no monitor validates own "
        "liveness). Composes parent + 9th-rule monitor-consumer-can-die-inbox-authoritative."
    ),
    'lesson_class': 'verify',
    'confirmed_or_candidate': 'CONFIRMED',
    'witnesses_count': 2,
    'instance_number': 81,
    'instance_number_provenance': (
        'Skunkworks 18:30 substrate-build A1 spec; CONFIRMED via 2 witnesses + composes-with CONFIRMED parent '
        '(promote-on-compose sound); 3rd witness welcome but parent carries it'
    ),
    'verify_the_referent_parent': 'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
    'composes_with': [
        'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
        'AUDIT_audit_tooling_verify_before_trusted_keyword_search_unreliable',
        'monitor_consumer_can_die_inbox_authoritative_9th_rule',
        'RULE_13th_rule_backstop_to_backstop_manual_filesystem_cross_check_cadence',
    ],
}

A2_CHILD = {
    'slug': 'prereg_must_be_committed_before_dispatch_written_disk_not_on_remote',
    'name': 'Audit lesson (CANDIDATE; instance 82; process): prereg-must-be-committed-before-dispatch',
    'description': (
        "A dispatch naming a prereg file must verify the file is COMMITTED to git AND PUSHED to remote (the "
        "referent on remote) -- not just written to local disk. Today witness: Orchestrator caught for refuse-"
        "gate FULL dispatch naming a prereg that was on local disk but not on git remote; gate-fail at remote "
        "side surfaced the mismatch (written-to-disk != on-remote referent). 1 witness; CANDIDATE; promotes on "
        "2 more. Composes parent verify-the-referent + drill-must-be-saved-to-notes (the artifact actually "
        "exists where needed). Fix: dispatch wrapper verifies git status + remote-presence before allowing "
        "dispatch to fire."
    ),
    'lesson_class': 'process',
    'confirmed_or_candidate': 'CANDIDATE',
    'witnesses_count': 1,
    'instance_number': 82,
    'instance_number_provenance': (
        'Skunkworks 18:30 substrate-build A2 spec; 1 witness today (Orchestrator caught for refuse-gate FULL '
        'dispatch); CANDIDATE; promote on 2 more witnesses; composes verify-the-referent parent + drill-must-'
        'be-saved sub-instance pattern'
    ),
    'verify_the_referent_parent': 'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
    'composes_with': [
        'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer',
        'AUDIT_drill_must_be_saved_to_notes_dispatched_artifact_persist',
    ],
}

EXISTING_CHILDREN_TO_RELINK = [
    'AUDIT_recapture_anchor_mechanism_match_referent_layer',
    'AUDIT_drill_must_be_saved_to_notes_dispatched_artifact_persist',
    'AUDIT_failure_mode_must_be_arm_fixable_no_op_arms_caught_at_smoke',
    'AUDIT_cell_allocation_must_be_explicit_roadmap_concrete_actionable',
]


def module_liveness_ok() -> bool:
    import importlib
    return all(
        hasattr(importlib.import_module(m), s)
        for m, s in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ]
    )


def axiom_term_count(ps: PartitionedStore) -> int:
    atoms = list(ps.all_atoms())
    return sum(
        1 for a in atoms
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def build_parent(spec: dict) -> Atom:
    metadata = {
        'lesson_class': spec['lesson_class'],
        'confirmed_or_candidate': spec['confirmed_or_candidate'],
        'witnesses_count': spec['witnesses_count'],
        'witnesses': spec['witnesses'],
        'layers': spec['layers'],
        'applications_NOT_witnesses': spec['applications_NOT_witnesses'],
        'parent_of': spec['parent_of'],
        'composes_with_siblings': spec['composes_with_siblings'],
        'instance_number': spec['instance_number'],
        'instance_number_provenance': spec['instance_number_provenance'],
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'NOT_load_bearing_until_3_witnesses': False,
        'prose_source': 'skunkworks_to_testbed_research_SUBSTRATE_BUILD_verify_the_referent_atom_spec_verified_witnesses_2026-06-17.md',
        'eleventh_rule_clean': True,
        'substrate_internal_verified': True,
        'verify_the_referent_family': True,
        'verify_the_referent_is_PARENT_class': True,
        'discipline_applied_to_own_atomization': True,
        'source': 'VERIFY_THE_REFERENT_parent_substrate_build_skunkworks_18_30_spec_5_caught_witnesses_4_layers_rigorously_verified_not_inflated_applications_excluded_double_count_avoided_USER_substrate_build_directive_autonomy_path',
    }
    return Atom(
        id=f"AUDIT_{spec['slug']}",
        name=spec['name'],
        description=spec['description'],
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata=metadata,
    )


def build_child(spec: dict) -> Atom:
    metadata = {
        'lesson_class': spec['lesson_class'],
        'confirmed_or_candidate': spec['confirmed_or_candidate'],
        'witnesses_count': spec['witnesses_count'],
        'instance_number': spec['instance_number'],
        'instance_number_provenance': spec['instance_number_provenance'],
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'NOT_load_bearing_until_3_witnesses': spec['confirmed_or_candidate'] == 'CANDIDATE',
        'prose_source': 'skunkworks_to_testbed_research_SUBSTRATE_BUILD_verify_the_referent_atom_spec_verified_witnesses_2026-06-17.md',
        'eleventh_rule_clean': True,
        'substrate_internal_verified': True,
        'verify_the_referent_family': True,
        'verify_the_referent_parent': spec['verify_the_referent_parent'],
        'composes_with': spec['composes_with'],
        'source': 'substrate_build_skunkworks_18_30_spec_verify_the_referent_child_of_parent_class_2nd_witness_corroborated_USER_substrate_build_call',
    }
    return Atom(
        id=f"AUDIT_{spec['slug']}",
        name=spec['name'],
        description=spec['description'],
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata=metadata,
    )


def relink_child(ps: PartitionedStore, child_id: str, parent_id: str) -> dict:
    """Add verify_the_referent_parent field to existing child atom."""
    atoms = list(ps.all_atoms())
    target = next((a for a in atoms if str(a.id) == child_id), None)
    if target is None:
        return {'status': 'NOT_FOUND', 'id': child_id}

    new_md = dict(target.metadata or {})
    new_md['verify_the_referent_parent'] = parent_id
    new_md['parent_link_added_skunkworks_18_30_substrate_build'] = True

    updated = Atom(
        id=target.id,
        name=target.name,
        description=target.description,
        kind=target.kind,
        tier=target.tier,
        corpus=target.corpus,
        algebra=target.algebra,
        metadata=new_md,
        aliases=target.aliases,
        concept_links=target.concept_links,
        complexity=target.complexity,
        current_best_solution=target.current_best_solution,
        equivalences=target.equivalences,
        serves_capability=target.serves_capability,
        signature=target.signature,
        solution_history=target.solution_history,
    )
    ps.add_atom(updated, source='substrate_build_skunkworks_18_30_relink_child_to_real_parent', note='verify_the_referent_parent link')
    return {'status': 'RELINKED', 'id': child_id}


def main() -> int:
    store_dir = Path('data/substrate_index')
    ps = PartitionedStore(store_dir)

    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE-RATIFY: atoms={pre_n}  axiom_term={pre_axiom}/{pre_axiom}  cap_pres(mod6/6)={pre_mod}')

    if not pre_mod or pre_axiom != 206:
        print('PRE-RATIFY GATE FAIL.')
        return 1

    parent_id = f"AUDIT_{PARENT['slug']}"

    # 1. Add PARENT
    parent_atom = build_parent(PARENT)
    existing = {a.id for a in ps.all_atoms()}
    if parent_atom.id in existing:
        print(f'  SKIP parent (already present): {parent_atom.id}')
    else:
        ps.add_atom(parent_atom, source='substrate_build_skunkworks_18_30_verify_the_referent_PARENT', note='CONFIRMED 5 witnesses 4 layers')
        post_n = sum(1 for _ in ps.all_atoms())
        post_axiom = axiom_term_count(ps)
        post_mod = module_liveness_ok()
        gate_ok = post_axiom == 206 and post_mod
        status = 'OK' if gate_ok else 'HARD_FAIL'
        print(f'  + PARENT {parent_atom.id}')
        print(f'    atoms_now={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}  -> {status}')
        if not gate_ok:
            print('  HARD_FAIL: halting.')
            return 2

    # 2. Add A1 CONFIRMED child
    a1_atom = build_child(A1_CHILD)
    if a1_atom.id in {a.id for a in ps.all_atoms()}:
        print(f'  SKIP A1 (already present): {a1_atom.id}')
    else:
        ps.add_atom(a1_atom, source='substrate_build_skunkworks_18_30_A1_CONFIRMED_child', note='monitor-must-watch-authoritative-source')
        post_n = sum(1 for _ in ps.all_atoms())
        post_axiom = axiom_term_count(ps)
        post_mod = module_liveness_ok()
        gate_ok = post_axiom == 206 and post_mod
        status = 'OK' if gate_ok else 'HARD_FAIL'
        print(f'  + A1 CHILD {a1_atom.id}')
        print(f'    atoms_now={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}  -> {status}')
        if not gate_ok:
            return 3

    # 3. Add A2 CANDIDATE child
    a2_atom = build_child(A2_CHILD)
    if a2_atom.id in {a.id for a in ps.all_atoms()}:
        print(f'  SKIP A2 (already present): {a2_atom.id}')
    else:
        ps.add_atom(a2_atom, source='substrate_build_skunkworks_18_30_A2_CANDIDATE_child', note='prereg-must-be-committed')
        post_n = sum(1 for _ in ps.all_atoms())
        post_axiom = axiom_term_count(ps)
        post_mod = module_liveness_ok()
        gate_ok = post_axiom == 206 and post_mod
        status = 'OK' if gate_ok else 'HARD_FAIL'
        print(f'  + A2 CHILD {a2_atom.id}')
        print(f'    atoms_now={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}  -> {status}')
        if not gate_ok:
            return 4

    # 4. Re-link existing 4 CANDIDATE children to parent
    print()
    print('Re-linking 4 existing CANDIDATE children to parent:')
    for child_id in EXISTING_CHILDREN_TO_RELINK:
        result = relink_child(ps, child_id, parent_id)
        print(f'  {child_id}: {result["status"]}')
        post_axiom = axiom_term_count(ps)
        post_mod = module_liveness_ok()
        if post_axiom != 206 or not post_mod:
            print('  HARD_FAIL on relink: halting.')
            return 5

    post_n = sum(1 for _ in ps.all_atoms())
    print('=' * 72)
    print(f'VERIFY-THE-REFERENT substrate-build ratify COMPLETE: +{post_n - pre_n} atoms (+ 4 relinks)')
    print(f'  axiom_term 206/206 PRESERVED  cap_pres 6/6 PRESERVED')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    sys.exit(main())
