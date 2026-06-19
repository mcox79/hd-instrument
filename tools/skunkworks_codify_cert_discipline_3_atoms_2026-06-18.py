"""Skunkworks 2026-06-18 bandwidth codification: 3 cert-discipline atoms (Research-assigned + my-domain).
  1 AUDIT_LESSON  -- the 5-layer verify-the-referent-on-an-atom-field chain (PP-371 discovery).
  2 METHODOLOGY_RULE -- (a) cert-architecture engine/checklist separation; (b) optimal-per-evidence cert-VET discipline.
META corpus, TIER_METHODOLOGY, algebra=None (process-knowledge -> NOT cert-counted -> CERT 570 unchanged; NOT axiom_term).
A5-safe: snapshot CERT/axiom/cap_pres before -> add (single guarded invocation) -> verify after + read-back. ASCII.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


def cert(p):
    return sum(1 for a in p.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def axiom(p):
    return sum(1 for a in p.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def modlive():
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


VTR_PARENT = 'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer'

ATOMS = [
    Atom(
        id='AUDIT_verify_referent_atom_field_multi_layer_value_resolves_id_form',
        name=('Audit lesson (CANDIDATE; instance 238; verify): verify-the-referent on an atom-field has MULTIPLE '
              'layers -- field-EXISTS / field-LOCATION / value-RESOLVES / id-FORM'),
        description=(
            "Verify-the-referent on an atom-field has MULTIPLE layers; a referent-check is COMPLETE only when the "
            "VALUE RESOLVES to a real atom via the correct match-key. Layers: (1) field-EXISTS (the field is in the "
            "Store); (2) field-LOCATION (a top-level Atom attr like a.current_best_solution vs metadata.get -- a "
            "metadata.get on a top-level field returns a FALSE None); (3) value-RESOLVES-to-an-atom (the field HAS a "
            "value but the value may point to NO atom = phantom); (4) id-FORM (the resolution check must use "
            "a.qualified_id, the atomizer match-key, NOT a.id -- a bare-vs-qualified mismatch falsely flags all-"
            "resolving as all-phantom); (5) disagreement-after-both-verified IS the catch. Discovered in the PP-371 "
            "capability-update VET (2026-06-18): the source current_best 'T2/prototype_bundle_cleanup' field EXISTED "
            "but RESOLVED to no atom (phantom); a back-fill would have propagated it. CANDIDATE (w=1; the 5-layer "
            "chain in one event); NOT load-bearing until 3 witnesses."),
        kind=AtomKind.AUDIT_LESSON, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
        metadata={
            'lesson_class': 'verify', 'confirmed_or_candidate': 'CANDIDATE', 'witnesses_count': 1,
            'witnesses': ["PP-371 capability-update VET 2026-06-18: Director mined source current_best EXISTS "
                          "(field-EXISTS); Exp-Dev metadata.get false-None (field-LOCATION); Skunkworks caught value "
                          "'T2/prototype_bundle_cleanup' resolves to NO atom (value-RESOLVES); Skunkworks self-caught "
                          "first scan used a.id not a.qualified_id (id-FORM); disagreement-after-both-verified was the catch"],
            'instance_number': 238,
            'instance_number_provenance': ('Skunkworks 2026-06-18 PP-371 capability-update VET-on-landing: NEW '
                                           'CANDIDATE (w=1; 5-layer chain in one event); promote on 3 distinct witness-events'),
            'term_class': 'PROCESS_KNOWLEDGE_NON_MATH', 'NOT_load_bearing_until_3_witnesses': True,
            'prose_source': ('skunkworks_VET_recovery_PASS_capupdate_REFINE_PP371_source_currentbest_PHANTOM_HOLD + '
                             'skunkworks_to_exp_dev_research_B2_PP371_backfill_HOLD_source_value_PHANTOM_crossed_ACK + '
                             'research_to_skunkworks_exp_dev_RETRACT_ACK_B2_HOLD_5_layer_audit_lesson_B1_refine (2026-06-18)'),
            'eleventh_rule_clean': True, 'substrate_internal_verified': True,
            'composes_with': [VTR_PARENT, 'AUDIT_audit_input_corpus_completeness'],
            'verify_the_referent_family': True, 'verify_the_referent_parent': VTR_PARENT,
            'source': 'PP371_capability_update_5_layer_verify_referent_chain_skunkworks_2026_06_18',
        }),
    Atom(
        id='RULE_cert_architecture_engine_atomize_vs_checklist_dispatch_separation',
        name=('Methodology rule (cert-architecture): self-cert ENGINE (atomize-time cert-correctness) vs pre-dispatch '
              'CHECKLIST (dispatch-time cell-readiness) -- keep separate; do NOT migrate dispatch-properties into the engine'),
        description=(
            "Cert-architecture separation. The self-cert ENGINE (atomize-time) tiers atoms by RESULT properties "
            "bearing on cert-CORRECTNESS: discrimination / baseline-cliff / corpus-completeness / multi-hop-provenance "
            "/ verdict-mappability / phantom-deps. The pre-dispatch CHECKLIST (dispatch-time) enforces cell-READINESS: "
            "prereg-committed / run-mode=full / import-torch / checkpoint-resume / atom-add-mechanism. "
            "Performance/robustness properties are NOT cert-correctness -- a per-atom-built atom is EXACTLY as cert-"
            "valid as a batched one -- so they go to the CHECKLIST, never the engine. Migrating dispatch-properties "
            "into the atomize-engine is wrong: it proliferates the engine AND forces tier-changes that do not bear on "
            "the atom truth. Decided when the atom-add-mechanism check (8th-gate candidate) was DECLINED as an engine-"
            "gate and kept as a dispatch-checklist/SCHEMA-VET condition; the engine stays 7 LIVE."),
        kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
        metadata={
            'rule_class': 'cert_architecture', 'status': 'ADOPTED', 'confidence': 'high',
            'extracted_by': 'skunkworks', 'extracted_date': '2026-06-18',
            'witnesses': ['8th-gate atom-add-mechanism DECLINED-as-engine -> dispatch-checklist',
                          'prereg-committed + drill-persist routed to dispatch pipeline not engine',
                          'checkpoint-resume = 6th pre-dispatch checklist item not an atomize gate'],
            'composes_with': ['RULE_discrimination_regime_self_cert_gate_audit79_deterministic',
                              'reference_remote_dispatch_cell_readiness_checklist_2026-06-17'],
            'eleventh_rule_clean': True, 'substrate_internal_verified': True,
            'source': '8th_gate_decline_engine_checklist_separation_skunkworks_2026_06_18',
        }),
    Atom(
        id='RULE_optimal_per_evidence_cert_vet_discipline',
        name=('Methodology rule (cert-VET): any "optimal / better-approach" claim (capability-APPROACH or '
              'operating-POINT) gets the SAME cert-VET -- cert-grade-better / honest-scope / not-coextensive-or-'
              'by-construction / not-over-strong-label / discriminating'),
        description=(
            "Optimal-per-evidence cert-VET discipline. Capability-mining (optimal APPROACH per capability) and the "
            "phase-portrait (optimal OPERATING-POINT per regime) are TWO FACES of the same question: are we doing the "
            "best-known thing per existing measurements? Any 'optimal / better-approach' claim gets the SAME cert-VET: "
            "(a) cert-grade-better (a real cert-grade comparison, not SMOKE-read-as-lever); (b) honest-scope "
            "(method/config-contingent); (c) NOT coextensive/by-construction (the intervention not structurally-"
            "matched to the measurement); (d) NOT over-strong-label; (e) discriminating (not a degenerate regime); "
            "and the current_best VALUE must RESOLVE to a real atom (per the multi-layer verify-the-referent lesson). "
            "NEGATIVITY-BIAS-symmetric: cuts both ways -- do not under- OR over-claim 'better'. Discovered via the "
            "RETRIEVAL_multi_hop current-best VET + the capability-mining/phase-portrait unification (2026-06-18)."),
        kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
        metadata={
            'rule_class': 'cert_vet', 'status': 'ADOPTED', 'confidence': 'high',
            'extracted_by': 'skunkworks', 'extracted_date': '2026-06-18',
            'witnesses': ['RETRIEVAL_multi_hop current-best VET-on-landing (current_best must resolve + cert-grade-better)',
                          '2-level recovery coextensive -> MEASURED_MECHANISM not blind-cert',
                          'capability-mining + phase-portrait = two-faces-of-optimal-per-evidence unification'],
            'composes_with': ['AUDIT_verify_referent_atom_field_multi_layer_value_resolves_id_form',
                              'feedback_negativity_bias_symmetric', 'AUDIT_audit_input_corpus_completeness'],
            'eleventh_rule_clean': True, 'substrate_internal_verified': True,
            'source': 'capability_mining_phase_portrait_unification_optimal_per_evidence_skunkworks_2026_06_18',
        }),
]


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206:
        print("PRE-GATE FAIL (axiom!=206 or cap_pres down). HALT."); return 1
    added = 0
    for a in ATOMS:
        if ps.get_atom(a.qualified_id) is not None:
            print(f"  SKIP exists: {a.id}"); continue
        ps.add_atom(a, source='skunkworks_bandwidth_codify_2026_06_18',
                    note='cert-discipline codification (5-layer audit-lesson + 2 methodology-rules)')
        added += 1
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed = sorted(a.id for a in ps2.all_atoms() if a.id in {x.id for x in ATOMS})
    bad_alg = [a.id for a in ps2.all_atoms() if a.id in {x.id for x in ATOMS} and a.algebra is not None]
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect {pre_cert}) "
          f"axiom={post_ax} (expect 206) cap_pres={post_mod}")
    print(f"  added={added} landed={landed} algebra!=None={bad_alg}")
    gate = (post_cert == pre_cert and post_ax == 206 and post_mod and len(landed) == 3 and not bad_alg)
    print("GATE:", "OK" if gate else "FAIL")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
