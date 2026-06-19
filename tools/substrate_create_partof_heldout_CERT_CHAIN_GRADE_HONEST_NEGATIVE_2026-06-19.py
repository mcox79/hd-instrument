"""Scoped creation: Item 1 Design-B held-out PART_OF falsifiable test as CERT_CHAIN_GRADE HONEST_NEGATIVE (CERT 571->572).

Skunkworks SCHEMA-VET + verdict-VET = PASS (independently REPRODUCED; exact match). Tier-call = CERT_CHAIN_GRADE
HONEST_NEGATIVE. The sprint-3 discriminating cert-experiment: a GENUINELY NON-COEXTENSIVE held-out falsifiable test that
BOUNDS the universal-lever -> COVERAGE-COMPLETION-not-REASONING. The FIRST cert-grade result of sprint-3 + a NEGATIVE that
bounds the claim (the highest-integrity outcome; discipline cutting toward honest limits, not just wins).

Result (held-out PART_OF, in-memory/0-persist): held-out 2-hop recall 0.576->0.598 (+0.022, MIDDLE) vs TRAIN control
0.603->0.724 (+0.121). Completing TRAIN synsets' edges did NOT transfer to HELD-OUT synsets' own-edge-dependent 2-hop QA.
non_coextensive (heldout_edges_in_train_completion=0); n_heldout=92; fp=0; discriminating-regime (control moves).

refuse-until-VET-PASS guard. CERT==pre+1; revert-on-fail. ASCII. No LLM. RUN only on Skunkworks tier-call (no-self-certify).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_partof_heldout_falsifiable_cpu_v1'
PARTOF_LEVER_QID = 'math::T3/EXP_partof_2level_completion_cpu_v1'   # the PART_OF MEASURED_MECHANISM this held-out test BOUNDS
DEFAULT_CANON = Path('data/exp_partof_heldout_falsifiable_v1/metrics.json')

BOUND = (
    "completing TRAIN synsets' 2-level edges did NOT transfer to answer HELD-OUT synsets' own-edge-dependent 2-hop QA "
    "(held-out 0.576->0.598 = +0.022 vs TRAIN control 0.603->0.724 = +0.121). The lever is PER-SYNSET-COVERAGE-BOUNDED, "
    "NOT transferable: the deterministic BFS does NOT INFER a held-out synset's absent edges from OTHER synsets' "
    "completions. The substrate's n-hop QA is COVERAGE-COMPLETION, not REASONING."
)
SCOPE = (
    "PART_OF / meronymic / WordNet / deterministic-BFS / in5k. NOT a general-reasoning claim. The empirical anti-over-claim "
    "the USER's recapture->substrate-wide extrapolation-catch demands: n-hop WordNet QA = coverage, NOT reasoning/inference-"
    "transfer. GENUINELY NON-COEXTENSIVE (unlike the HYP/PART_OF MEASURED_MECHANISM coextensive recoveries) -> a positive "
    "WOULD have been cert-grade-discriminating; the negative is equally cert-grade (a proven bound)."
)
MARGINAL_TRANSFER = (
    "NEGATIVITY-BIAS-symmetric: the +0.022 held-out lift is NOT zero (~18% of the control's +0.121) -- a few held-out "
    "chains route hop-2 through a shared TRAIN intermediate whose edge got completed. Report the small transfer, do NOT "
    "round to 0; the conclusion (coverage-bounded, no meaningful generalization) holds because it is far below the control."
)
TEST_VALIDITY = (
    "The TRAIN control MOVES +0.121 -> the completion mechanism WORKS on completed synsets -> the held-out null is a REAL "
    "transfer-failure, NOT a broken test. fp=0 on verified-unreachable held-out negatives. Baseline built from the Store's "
    "STORED metadata['meronyms'] (the ASYMMETRIC pre-Item-1 ~530-edge state), NOT nltk's symmetric closure (which would "
    "no-op the completion -- the baseline-closure bug caught+fixed via the control-moves validity gate). "
    "DISCRIMINATING-REGIME (not degenerate) -> passes DEGENERATE-REGIME-NOT-REFUTATION: a real refutation, not a non-test."
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
        'heldout_edges_in_tc==0': m.get('heldout_edges_in_train_completion') == 0,
        'n_heldout>=30': (m.get('n_heldout_positives') or 0) >= 30,
        'fp==0': m.get('false_positives') == 0,
        'discriminating_regime': m.get('discriminating_regime') is True,
        'control_moves_more_than_heldout': (m.get('train_delta') or 0) > (m.get('heldout_delta') or 0),
        'run_mode==full': m.get('run_mode') == 'full',
    }
    ok = all(checks.values())
    print('VET-GUARD:', checks)
    return ok


def build_atom(m: dict, canon: Path) -> Atom:
    cert_value = (
        "Item 1 Design-B: a GENUINELY NON-COEXTENSIVE held-out PART_OF falsifiable test (build 2-level completion on a TRAIN "
        "synset subset; test 2-hop QA on HELD-OUT synsets whose answer-paths need edges the train-completion did NOT add). "
        "RESULT (cert-grade HONEST_NEGATIVE): " + BOUND
    )
    metadata = {
        'record_class': 'experiment_record',
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'verdict': 'HONEST_NEGATIVE',
        'provenance_quality': 'CERT_CHAIN_GRADE',
        'relevance_tier': 'SUPPORTING',
        'run_mode': 'full', 'n_seeds': 1, 'metrics_source': m.get('metrics_source'),
        'held_out_eval': True, 'prereg_bands': m.get('prereg_bands'),
        'metrics_path': str(canon),
        'experiment_path': 'experiments/exp_substrate_partof_heldout_falsifiable_cpu_v1.py',
        'design': m.get('design'), 'seed_salt': m.get('seed_salt'), 'device': m.get('device'),
        'key_metrics': {
            'heldout_recall_before': m.get('heldout_recall_before'), 'heldout_recall_after': m.get('heldout_recall_after'),
            'heldout_delta': m.get('heldout_delta'), 'heldout_band_after': m.get('heldout_band_after'),
            'train_recall_before': m.get('train_recall_before'), 'train_recall_after': m.get('train_recall_after'),
            'train_delta': m.get('train_delta'),
            'n_baseline_edges': m.get('n_baseline_edges'), 'n_train_completion_edges': m.get('n_train_completion_edges'),
            'heldout_edges_in_train_completion': m.get('heldout_edges_in_train_completion'),
            'n_heldout_positives': m.get('n_heldout_positives'), 'n_train_positives': m.get('n_train_positives'),
            'non_coextensive': m.get('non_coextensive'), 'false_positives': m.get('false_positives'),
            'train_synsets': m.get('n_train_synsets'), 'heldout_synsets': m.get('n_heldout_synsets'),
        },
        'cert_value': cert_value, 'the_bound': BOUND, 'claim_scope': SCOPE, 'honest_scope': SCOPE,
        'marginal_transfer_note': MARGINAL_TRANSFER, 'test_validity_note': TEST_VALIDITY,
        'min_cert_along_path': 'WordNet PART_OF edges ontology-INGESTED (LEXICON tier); the HELD-OUT AUROC/recall is the cert-grade EXPERIMENT (non-coextensive, reproduced); the bound is a proven negative.',
        'bounds_lever': 'BOUNDS the PART_OF/HYPERNYM coverage-completion lever (the MEASURED_MECHANISM recoveries): the lever is per-synset-coverage-bounded, NOT a transferable reasoning capability. Load-bearing for the substrate-as-reasoning-engine WRITEUP honest-scope (n-hop WordNet QA = coverage, NOT reasoning).',
        'bears_on': 'the universal-lever claim (HYP+PART_OF coverage-limited MEASURED_MECHANISM); the Item-3 WRITEUP honest-scope; the coextensive-vs-genuine-generalization cert-question; A1/A2 by-construction controls',
        'strengthens_cert': [PARTOF_LEVER_QID],
        'reproduced_by': 'skunkworks (independent re-run; exact match held-out 0.5761->0.5978 +0.0217 / train +0.1206)',
        'schema_vet_by': 'skunkworks', 'verdict_vet_by': 'skunkworks', 'tier_call_by': 'skunkworks', 'vet_date': '2026-06-19',
        'vet_note': 'Skunkworks SCHEMA-VET + verdict-VET PASS (independently reproduced) -> CERT_CHAIN_GRADE HONEST_NEGATIVE (CERT 571->572); 7 cert-conditions met; non-coextensive (binding); control-moves test-validity; honest-scope verbatim.',
        'eleventh_rule_clean': True, 'deterministic_no_llm': True,
        'source': 'partof_heldout_falsifiable_cert_chain_grade_honest_negative_item1_sprint3',
    }
    return Atom(
        id=ATOM_ID,
        name='CERT (CERT_CHAIN_GRADE HONEST_NEGATIVE): held-out PART_OF falsifiable test BOUNDS the coverage-lever -- per-synset-coverage-bounded, NOT transferable (coverage-completion-not-reasoning)',
        description='CERT_CHAIN_GRADE HONEST_NEGATIVE (non-coextensive held-out; reproduced). ' + cert_value + ' SCOPE: ' + SCOPE,
        kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None, metadata=metadata,
    )


def main() -> int:
    canon = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CANON
    if not canon.exists():
        print(f'HALT: canonical metrics not found at {canon}'); return 1
    m = json.loads(canon.read_text(encoding='utf-8'))
    if not vet_guard(m):
        print('HALT: VET-GUARD FAILED. NO atomize.'); return 1
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    print(f'PRE: axiom_term={pre_axiom}  cap_pres={pre_mod}  CERT={pre_cert}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1
    if ps.get_atom(f'math::{ATOM_ID}') is not None:
        print(f'SKIP (idempotent): {ATOM_ID}'); return 0
    atom = build_atom(m, canon)
    ps.add_atom(atom, source='partof_heldout_falsifiable', note='Skunkworks tier-call CERT_CHAIN_GRADE HONEST_NEGATIVE; CERT 571->572; bounds the coverage-lever')
    edge_added = False
    if ps.get_atom(PARTOF_LEVER_QID) is not None:
        try:
            ps.add_relation(f'math::{ATOM_ID}', RelationType.STRENGTHENS, PARTOF_LEVER_QID,
                            source='partof_heldout_falsifiable', note='held-out test BOUNDS the coverage-lever (per-synset-bounded, not transferable)')
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
        print('HARD_FAIL: gate/read-back failed (CERT must be exactly pre+1). Reverting.')
        ps2.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail'); return 2
    print('=' * 72)
    print(f'PART_OF held-out HONEST_NEGATIVE landed: math::{ATOM_ID}  CERT {post_cert} (571->572)  axiom_term 206  cap_pres 6/6')
    print('  Universal-lever EMPIRICALLY BOUNDED: coverage-completion-not-reasoning (non-coextensive held-out; reproduced).')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
