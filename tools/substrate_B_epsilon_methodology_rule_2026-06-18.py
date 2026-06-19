"""B-epsilon methodology_rule (Skunkworks solo; completes TRACK 4's discrimination-regime gate deliverable).

1 METHODOLOGY_RULE documenting the discrimination-regime self-cert gate (the 2nd self-cert gate, code in 0aa86078):
  degenerate-regime-not-refutation (audit lesson 79, CONFIRMED 7-witness) is now encoded as a DETERMINISTIC
  self-applied gate -- producer discrimination_self_check + consumer discrimination_gate (non-discriminating ->
  NON_TEST). The substrate-autonomy path: a CONFIRMED audit JUDGMENT -> a deterministic self-applied check.

Gated: axiom_term 206/206 + cap_pres 6/6 + CERT 568 unchanged (pre+post). Serial; fresh-load.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

RULE = {
    'id': 'RULE_discrimination_regime_self_cert_gate_audit79_deterministic',
    'name': 'Methodology rule (PHASE-2; cert-autonomy): discrimination-regime self-cert gate (audit-79 -> deterministic)',
    'description': (
        "The DISCRIMINATION-REGIME check is a deterministic self-cert gate (the 2nd of the self-cert engine; "
        "code 0aa86078). It encodes degenerate-regime-not-refutation (audit lesson 79, CONFIRMED 7-witness) as "
        "producer-attest + consumer-enforce: the PRODUCER cell self-attests whether its regime DISCRIMINATES "
        "(reference point measurably > floor AND < ceiling; not saturated/collapsed/one-hot/under-stressed) via "
        "_cell_provenance.discrimination_self_check; the CONSUMER atomizer's discrimination_gate forces the "
        "effective verdict to NON_TEST when discriminates==False (a PASS/HARD_FAIL on a non-discriminating regime "
        "is meaningless). ADDITIVE + NON-RETROACTIVE (cells without the field unchanged). Generalizes the per-cell "
        "discrimination guard hand-written in A3/8a/refuse-gate into ONE shared gate. Auto-catches the "
        "self-dominance-wall / saturation / one-hot 'PASS'. Substrate-autonomy increment: a CONFIRMED audit "
        "JUDGMENT (79) -> a deterministic self-applied check (the auditor bootstrapping toward self-certification)."
    ),
    'rule_class': 'cert_autonomy',
    'witnesses': ['A3 nonzero<=2 self-dominance-wall', '8a degenerate-regime guard', 'refuse-gate NON_TEST',
                  'C1 self-dominance one-hot (audit 79 witnesses)'],
    'composes_with': ['AUDIT_degenerate_regime_not_refutation_non_discriminating_test_is_non_test_verify_regime_discriminating_before_verdict',
                      'RULE_gate0_both_ends_producer_self_attest_consumer_enforce_walltime_is_tell_not_gate',
                      'feedback_substrate_autonomy_path_encode_audit_discipline_as_self_certification'],
}


def module_liveness_ok() -> bool:
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


def axiom_term_count(ps: PartitionedStore) -> int:
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH'
               and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3
               and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def cert_count(ps: PartitionedStore) -> int:
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def main() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_n = sum(1 for _ in ps.all_atoms()); pre_ax = axiom_term_count(ps); pre_cert = cert_count(ps); pre_mod = module_liveness_ok()
    print(f'PRE: atoms={pre_n} axiom_term={pre_ax} CERT={pre_cert} cap_pres={pre_mod}')
    if not pre_mod or pre_ax != 206:
        print('PRE-GATE FAIL.'); return 1
    if RULE['id'] in {a.id for a in ps.all_atoms()}:
        print(f'SKIP (present): {RULE["id"]}'); return 0
    meta = {'rule_class': RULE['rule_class'], 'status': 'PHASE_2', 'confidence': 'high',
            'extracted_by': 'skunkworks', 'extracted_date': '2026-06-18',
            'witnesses': RULE['witnesses'], 'composes_with': RULE['composes_with'],
            'implements_audit_lesson': 79, 'self_cert_gate_number': 2,
            'eleventh_rule_clean': True, 'substrate_internal_verified': True,
            'source': 'B_epsilon_discrimination_regime_self_cert_gate_2026_06_18_0aa86078'}
    atom = Atom(id=RULE['id'], name=RULE['name'], description=RULE['description'], kind=AtomKind.METHODOLOGY_RULE,
                tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None, metadata=meta)
    ps.add_atom(atom, source='B_epsilon_methodology_rule_2026_06_18', note='PHASE-2 cert-autonomy; audit-79 -> deterministic gate')
    post_n = sum(1 for _ in ps.all_atoms()); post_ax = axiom_term_count(ps); post_cert = cert_count(ps); post_mod = module_liveness_ok()
    ok = post_ax == 206 and post_mod and post_cert == pre_cert
    print(f'  + {RULE["id"]}')
    print(f'POST: atoms={post_n} (+{post_n-pre_n}) axiom_term={post_ax} CERT={post_cert} (unchanged={post_cert==pre_cert}) cap_pres={post_mod} -> {"OK" if ok else "HARD_FAIL"}')
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
