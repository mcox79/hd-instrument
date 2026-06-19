"""Scoped creation: 40h M1 HYPERNYM held-out replication as CERT_CHAIN_GRADE HONEST_NEGATIVE (CERT 572->573).

Skunkworks SCHEMA-VET + verdict-VET = PASS (independently REPRODUCED exact). Tier-call = CERT_CHAIN_GRADE HONEST_NEGATIVE.
The multi-relation-robustness replication of Item 1: the coverage-completion lever does NOT transfer for HYPERNYM TOO
(held-out +0.010 vs train control +0.953 -- a DRAMATICALLY-validated control), replicating the PART_OF Item-1 HONEST_NEGATIVE.
=> The bound is now MULTI-RELATION-ROBUST: the substrate's n-hop WordNet QA is COVERAGE-COMPLETION, NOT REASONING, for BOTH
HYPERNYM and PART_OF. STRENGTHENS the PART_OF held-out atom (2nd relation-type witness of the SAME bound).

refuse-until-VET-PASS guard. CERT==pre+1; revert-on-fail. ASCII. No LLM. RUN only on Skunkworks tier-call (no-self-certify).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_hypernym_heldout_falsifiable_cpu_v1'
PARTOF_HELDOUT_QID = 'math::T3/EXP_partof_heldout_falsifiable_cpu_v1'   # the Item-1 PART_OF HONEST_NEGATIVE this REPLICATES/STRENGTHENS
DEFAULT_CANON = Path('data/exp_hypernym_heldout_falsifiable_v1/metrics.json')

BOUND = (
    "completing TRAIN intermediates' second-hop edges did NOT transfer to answer HELD-OUT intermediates' 2-hop QA "
    "(HYPERNYM held-out +0.010 vs train control +0.953); REPLICATES the PART_OF Item-1 HONEST_NEGATIVE. The coverage-"
    "completion lever is PER-UNIT-COVERAGE-BOUNDED, NOT transferable, for HYPERNYM + PART_OF both -> n-hop WordNet QA = "
    "COVERAGE, not REASONING (MULTI-RELATION-ROBUST). The deterministic BFS does NOT INFER a held-out unit's absent edges "
    "from OTHER units' completions, for either relation."
)
SCOPE = (
    "HYPERNYM (+ PART_OF) / WordNet / deterministic-BFS / in5k / second-hop-completion. NOT general reasoning. NOT other "
    "relation types untested (ENTAILMENT/CAUSES too sparse; ConceptNet untested). The empirical anti-over-claim, hardened "
    "from single-relation (PART_OF) to MULTI-RELATION-ROBUST."
)
TEST_VALIDITY = (
    "The TRAIN control moves +0.953 (0.004->0.957) -- the completion mechanism works DRAMATICALLY on completed intermediates "
    "-> the held-out null is a REAL transfer-failure, NOT a broken test (even STARKER than PART_OF's +0.121 control). "
    "baseline_flat = persisted HYPERNYM minus the second-hop edges (the 1-level FLAT state); held-out UNIT = the INTERMEDIATE "
    "(the symmetric-metadata adaptation: HYPERNYM hypernym/hyponym gap=0 -> the PART_OF asymmetry-completion would no-op, so "
    "the validated second-hop-on-completeness_target-intermediates lever was used instead). fp=0; DISCRIMINATING-regime."
)


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


def axiom_term_count(ps) -> int:
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def cert_count(ps) -> int:
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def vet_guard(m: dict) -> bool:
    checks = {
        'verdict==HONEST_NEGATIVE': m.get('verdict') == 'HONEST_NEGATIVE',
        'non_coextensive': m.get('non_coextensive') is True,
        'held_in_tc==0': m.get('heldout_intermediates_in_train_completion') == 0,
        'n_heldout>=30': (m.get('n_heldout_positives') or 0) >= 30,
        'fp==0': m.get('false_positives') == 0,
        'control_moves_more': (m.get('train_delta') or 0) > (m.get('heldout_delta') or 0),
        'run_mode==full': m.get('run_mode') == 'full',
    }
    ok = all(checks.values())
    print('VET-GUARD:', checks)
    return ok


def build_atom(m: dict, canon: Path) -> Atom:
    cert_value = ("40h M1: a non-coextensive HYPERNYM held-out falsifiable replication of Item 1 (held-out unit = the "
                  "completeness_target INTERMEDIATE; baseline_flat = persisted minus second-hop; complete TRAIN intermediates' "
                  "second-hop; test held-out 2-hop chains routing through HELD-OUT intermediates). RESULT (cert-grade "
                  "HONEST_NEGATIVE): " + BOUND)
    metadata = {
        'record_class': 'experiment_record', 'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'verdict': 'HONEST_NEGATIVE', 'provenance_quality': 'CERT_CHAIN_GRADE', 'relevance_tier': 'SUPPORTING',
        'run_mode': 'full', 'n_seeds': 1, 'metrics_source': m.get('metrics_source'),
        'held_out_eval': True, 'prereg_bands': m.get('prereg_bands'),
        'metrics_path': str(canon), 'experiment_path': 'experiments/exp_substrate_hypernym_heldout_falsifiable_cpu_v1.py',
        'design': m.get('design'), 'seed_salt': m.get('seed_salt'), 'device': m.get('device'),
        'held_out_unit': m.get('held_out_unit'),
        'key_metrics': {
            'heldout_recall_before': m.get('heldout_recall_before'), 'heldout_recall_after': m.get('heldout_recall_after'),
            'heldout_delta': m.get('heldout_delta'), 'heldout_band_after': m.get('heldout_band_after'),
            'train_recall_before': m.get('train_recall_before'), 'train_recall_after': m.get('train_recall_after'),
            'train_delta': m.get('train_delta'),
            'n_baseline_flat': m.get('n_baseline_flat'), 'n_train_completion_edges': m.get('n_train_completion_edges'),
            'heldout_intermediates_in_train_completion': m.get('heldout_intermediates_in_train_completion'),
            'n_completeness_target': m.get('n_completeness_target'), 'n_train_ct': m.get('n_train_ct'), 'n_heldout_ct': m.get('n_heldout_ct'),
            'n_heldout_positives': m.get('n_heldout_positives'), 'n_train_positives': m.get('n_train_positives'),
            'non_coextensive': m.get('non_coextensive'), 'false_positives': m.get('false_positives'),
        },
        'cert_value': cert_value, 'the_bound': BOUND, 'claim_scope': SCOPE, 'honest_scope': SCOPE, 'test_validity_note': TEST_VALIDITY,
        'min_cert_along_path': 'WordNet HYPERNYM edges ontology-INGESTED; the held-out recall is the cert-grade EXPERIMENT (non-coextensive, reproduced); the bound is a proven multi-relation-robust negative.',
        'multi_relation_robust': 'HYPERNYM + PART_OF both: the coverage-completion lever is per-unit-coverage-bounded, NOT transferable. n-hop WordNet QA = coverage, not reasoning. The hardened WRITEUP central claim (single-relation -> multi-relation-robust).',
        'bears_on': 'Item 1 PART_OF HONEST_NEGATIVE (this is the 2nd relation-type witness); the universal-lever bound; the Item-3 WRITEUP central claim',
        'replicates': PARTOF_HELDOUT_QID, 'strengthens_cert': [PARTOF_HELDOUT_QID],
        'reproduced_by': 'skunkworks (independent re-run; exact match held-out +0.010 / train +0.953)',
        'schema_vet_by': 'skunkworks', 'verdict_vet_by': 'skunkworks', 'tier_call_by': 'skunkworks', 'vet_date': '2026-06-19',
        'vet_note': 'Skunkworks SCHEMA-VET + verdict-VET PASS (reproduced exact) -> CERT_CHAIN_GRADE HONEST_NEGATIVE (CERT 572->573); 7 cert-conditions; non-coextensive; control +0.953 dramatic; multi-relation-robust bound; honest-scope verbatim.',
        'eleventh_rule_clean': True, 'deterministic_no_llm': True,
        'source': 'hypernym_heldout_falsifiable_cert_chain_grade_honest_negative_M1_40h',
    }
    return Atom(
        id=ATOM_ID,
        name='CERT (CERT_CHAIN_GRADE HONEST_NEGATIVE): HYPERNYM held-out replication BOUNDS the coverage-lever -- per-unit-coverage-bounded NOT transferable; MULTI-RELATION-ROBUST (HYPERNYM+PART_OF coverage-not-reasoning)',
        description='CERT_CHAIN_GRADE HONEST_NEGATIVE (non-coextensive held-out; reproduced; multi-relation-robust). ' + cert_value + ' SCOPE: ' + SCOPE,
        kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None, metadata=metadata,
    )


def main() -> int:
    canon = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CANON
    if not canon.exists():
        print(f'HALT: metrics not found at {canon}'); return 1
    m = json.loads(canon.read_text(encoding='utf-8'))
    if not vet_guard(m):
        print('HALT: VET-GUARD FAILED.'); return 1
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    print(f'PRE: axiom_term={pre_axiom}  cap_pres={pre_mod}  CERT={pre_cert}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL.'); return 1
    if ps.get_atom(f'math::{ATOM_ID}') is not None:
        print(f'SKIP (idempotent): {ATOM_ID}'); return 0
    atom = build_atom(m, canon)
    ps.add_atom(atom, source='hypernym_heldout_falsifiable', note='Skunkworks tier-call CERT_CHAIN_GRADE HONEST_NEGATIVE; CERT 572->573; multi-relation-robust')
    edge_added = False
    if ps.get_atom(PARTOF_HELDOUT_QID) is not None:
        try:
            ps.add_relation(f'math::{ATOM_ID}', RelationType.STRENGTHENS, PARTOF_HELDOUT_QID,
                            source='hypernym_heldout_falsifiable', note='2nd relation-type witness of the SAME coverage-not-reasoning bound -> multi-relation-robust')
            edge_added = True
        except Exception as e:
            print(f'WARN: STRENGTHENS edge not added ({str(e)[:60]})')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps2); post_mod = module_liveness_ok(); post_cert = cert_count(ps2)
    rb = ps2.get_atom(f'math::{ATOM_ID}')
    rb_ok = (rb is not None and rb.kind == AtomKind.EXPERIMENT_RECORD and rb.algebra is None
             and rb.metadata.get('provenance_quality') == 'CERT_CHAIN_GRADE' and rb.metadata.get('verdict') == 'HONEST_NEGATIVE')
    gate_ok = post_axiom == 206 and post_mod and post_cert == pre_cert + 1 and rb_ok
    print(f'POST: axiom_term={post_axiom}  cap_pres={post_mod}  CERT={post_cert} (was {pre_cert})  read-back_ok={rb_ok}  strengthens_edge={edge_added}')
    if not gate_ok:
        print('HARD_FAIL: gate/read-back failed. Reverting.')
        ps2.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail'); return 2
    print('=' * 72)
    print(f'M1 HYPERNYM held-out HONEST_NEGATIVE landed: math::{ATOM_ID}  CERT {post_cert} (572->573)  axiom 206  cap_pres 6/6')
    print('  MULTI-RELATION-ROBUST bound: coverage-completion-not-reasoning (HYPERNYM + PART_OF). STRENGTHENS the Item-1 PART_OF atom.')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
