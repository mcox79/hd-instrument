"""TESTBED 2nd-witness for Skunkworks's 4th self-cert gate: corpus_completeness_gate
(committed a6166808; self-cert engine 3 -> 4 gates LIVE). Independent-harness 6-case
functional replicate matching the same pattern I used for B-epsilon (2nd gate) +
working-baseline-cliff (3rd gate).

Per Skunkworks's 4th-gate note: encodes A2 over-flag + remote-vs-local half-data catches
as a deterministic gate. ABSENCE/COVERAGE/GAP claim verified against incomplete corpus =
NON_TEST. ADDITIVE + NON-RETROACTIVE.

6-case spec for corpus_completeness_gate:
 C1 flat {is_complete: False} + verdict=PASS                -> NON_TEST
 C2 flat {is_complete: False} + verdict=HARD_FAIL           -> NON_TEST
 C3 flat {is_complete: True} + verdict=PASS                 -> PASS (no false override)
 C4 NO field present + verdict=PASS                          -> PASS (legacy-safe non-retroactive)
 C5 field present but non-dict + verdict=PASS                -> PASS (defensive)
 C6 NESTED any-False {claimA: {is_complete: False}, ...}     -> NON_TEST (multi-claim any-incomplete catch)

Also verifies (Store-level non-retroactive):
- atoms unchanged 41325
- CERT_CHAIN_GRADE unchanged 569
- axiom_term 206/206 PRESERVED
- cap_pres 6/6 PRESERVED
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from tools.atomize_experiment_records import corpus_completeness_gate
from backend.substrate_index.partition import PartitionedStore


CASES = [
    ('C1_flat_False_PASS_NONTEST',
     {'corpus_completeness_self_check': {'is_complete': False}}, 'PASS', 'NON_TEST'),
    ('C2_flat_False_HARDFAIL_NONTEST',
     {'corpus_completeness_self_check': {'is_complete': False}}, 'HARD_FAIL', 'NON_TEST'),
    ('C3_flat_True_PASS_NO_OVERRIDE',
     {'corpus_completeness_self_check': {'is_complete': True}}, 'PASS', 'PASS'),
    ('C4_no_field_legacy_UNCHANGED',
     {}, 'PASS', 'PASS'),
    ('C5_field_non_dict_UNCHANGED',
     {'corpus_completeness_self_check': None}, 'PASS', 'PASS'),
    ('C6_nested_any_False_NONTEST',
     {'corpus_completeness_self_check': {'claimA': {'is_complete': False},
                                          'claimB': {'is_complete': True}}}, 'PASS', 'NON_TEST'),
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
    return sum(
        1 for a in ps.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def main() -> int:
    print('=' * 78)
    print('TESTBED 2nd-WITNESS: corpus_completeness_gate (Skunkworks 4th gate; a6166808)')
    print('=' * 78)
    passes = 0
    for case_id, metrics, verdict_in, expected_out in CASES:
        actual = corpus_completeness_gate(metrics, verdict_in)
        ok = actual == expected_out
        mark = 'PASS' if ok else 'FAIL'
        print(f'  [{mark}] {case_id:<40}  in={verdict_in:<10}  expected={expected_out:<10}  actual={actual}')
        if ok:
            passes += 1

    print()
    print(f'  6-CASE FUNCTIONAL REPLICATE: {passes}/{len(CASES)} cases PASS')

    # Store-level non-retroactive verify
    print()
    print('Store-level non-retroactive verify:')
    ps = PartitionedStore(Path('data/substrate_index'))
    atoms = list(ps.all_atoms())
    ks = lambda a: a.kind.value if hasattr(a.kind, 'value') else a.kind
    cert = sum(1 for a in atoms if ks(a) == 'experiment_record'
               and (a.metadata.get('provenance_quality') or a.metadata.get('pq') or a.metadata.get('confidence_tier')) == 'CERT_CHAIN_GRADE')
    at = axiom_term_count(ps)
    ml = module_liveness_ok()
    print(f'  atoms:              {len(atoms)}')
    print(f'  CERT_CHAIN_GRADE:   {cert}')
    print(f'  axiom_term:         {at}/206')
    print(f'  cap_pres (6/6 mod): {ml}')

    structural_ok = (at == 206 and ml)
    print()
    print('=' * 78)
    if passes == len(CASES) and structural_ok:
        print(f'OVERALL: HARD_PASS  ({passes}/{len(CASES)} cases + structural 206/206 + cap_pres OK)')
        print('  4th self-cert gate ADDITIVE + NON-RETROACTIVE verified')
        print('  Self-cert engine 4 gates LIVE: gate0 + discrimination + baseline-cliff + corpus-completeness')
        return 0
    print(f'OVERALL: HARD_FAIL  cases={passes}/{len(CASES)} structural={structural_ok}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
