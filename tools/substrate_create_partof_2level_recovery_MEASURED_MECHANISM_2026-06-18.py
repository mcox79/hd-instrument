"""Scoped creation: PART_OF 2-level completion RECOVERY as MEASURED_MECHANISM (verdict=ATTRIBUTION; Item 1, 20h sprint).

The discriminating-experiment Skunkworks pre-stated (Item 1 SCHEMA-VET PASS). PART_OF 2-level completion materialized
each in-corpus synset's direct in-corpus HOLONYM edges the meronym-based original ingest missed (+125 gold-independent
edges, 0 new atoms; a 29% holonym-direction gap). Re-running BROAD --full (single-variable; same frozen gold; same BFS):
  PART_OF_2hop 0.627 -> 0.820  (+0.193)   PART_OF_3hop 0.500 -> 0.700  (+0.200)   BOTH MIDDLE -> HARD_PASS
  HYPERNYM unchanged (0.993/0.931/0.853; separate axis, already densified). Envelope MIDDLE_BAND(3P/2M) -> HARD_PASS(5P/0F).

=> JUMPS (Skunkworks tier-by-outcome) -> MEASURED_MECHANISM ATTRIBUTION. The FINDING: PART_OF was ALSO COVERAGE-limited
(the 29% holonym gap MATTERED). The prior "PART_OF depth-robust" framing is REFUTED -- PART_OF was not algorithmically
robust, only less-densified (meronym-only ingest). After holonym completion it jumps like HYPERNYM did. This gives the
depth-cliff coverage-story a SECOND relation-type data-point: coverage-limited-not-algorithmic is GENERAL across relation
types (HYPERNYM + PART_OF), not hypernym-specific. The canonical-direct-link completion is the UNIVERSAL lever.

CERT-TIER: verdict=ATTRIBUTION -> MEASURED_MECHANISM, NOT CERT_CHAIN_GRADE (the Phase A2 forward cert-condition). The
+125 are the 1-level PART_OF edges 2-hop QA traverses -> the AFTER recall is COEXTENSIVE/near-tautological. The SCIENTIFIC
value is the baseline-vs-after CONTRAST (MIDDLE -> HARD_PASS) discriminating coverage-vs-algorithmic. CERT stays 570.
ASCII. No LLM. Deterministic.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_partof_2level_completion_cpu_v1'
RECOVERY_QID = 'math::T3/EXP_t3_phaseA2_2level_recovery_cpu_v1'   # the HYPERNYM recovery; this is the 2nd relation-type witness
BROAD_QID = 'math::T3/EXP_b_alpha_broad_envelope_cpu_v1'           # the envelope this updates (PART_OF now HARD_PASS)

CERT_VALUE = (
    "PART_OF 2-level completion (+125 gold-independent holonym-direction edges X->in-corpus-holonym Z; 0 new atoms; the "
    "29% holonym-gap the meronym-based original ingest missed) -> BROAD PART_OF RECOVERS: PART_OF_2hop 0.627->0.820, "
    "PART_OF_3hop 0.500->0.700 (BOTH MIDDLE->HARD_PASS; 100% provenance-sound, 0 FP; HYPERNYM unchanged). Envelope "
    "MIDDLE_BAND(3P/2M)->HARD_PASS(5P/0F). The baseline-vs-after CONTRAST => PART_OF was ALSO COVERAGE-limited (the 29% "
    "holonym gap MATTERED for the 2-hop gold). The prior 'PART_OF depth-robust' framing is REFUTED: not algorithmically "
    "robust, only less-densified (meronym-only ingest). SECOND relation-type data-point => coverage-limited-not-algorithmic "
    "is GENERAL across relation types (HYPERNYM + PART_OF), not hypernym-specific; canonical-direct-link completion = the "
    "UNIVERSAL lever."
)
COEXTENSIVE_CAVEAT = (
    "MEASURED_MECHANISM (verdict=ATTRIBUTION), NOT CERT: gold-INDEPENDENT selection (each synset's own nltk holonyms; not "
    "by-construction-fraud) BUT the +125 are the 1-level PART_OF edges 2-hop QA traverses -> the AFTER recall (0.820/0.700) "
    "is COEXTENSIVE/near-tautological (the Phase A2 + A1 parallel). It measures path-completeness + BFS-correctness, NOT a "
    "generalizable lever-magnitude. The cert-grade SCIENTIFIC value is the CONTRAST (MIDDLE baseline vs HARD_PASS after) "
    "that discriminates coverage-vs-algorithmic for a SECOND relation type. CERT stays 570."
)
SCOPE = (
    "PART_OF/meronymic/WordNet/deterministic-BFS/in5k closure. The 0.820/0.700 are not 1.0 because some 2/3-hop gold "
    "chains still route through out-of-5k holonym intermediates the substrate never ingested -> correct REFUSE (no "
    "hallucination; coverage scales with depth, same as HYPERNYM). Gold-independent (each synset's canonical direct "
    "holonyms; consistent with the coextensive-MEASURED_MECHANISM framing). min-cert-along-path: WordNet PART_OF edges "
    "ontology-INGESTED (LEXICON tier), not experiment-cert. NOT a non-meronymic claim; NOT 'the substrate reasons'."
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


def build_atom() -> Atom:
    metadata = {
        'record_class': 'measured_mechanism',
        'verdict': 'ATTRIBUTION',
        'provenance_quality': 'MEASURED_MECHANISM',
        'relevance_tier': 'ARCHIVE',
        'run_mode': 'full', 'n_seeds': 1, 'metrics_source': 'measured_graph_bfs_held_out',
        'metrics_path_before': 'data/exp_partof_broad_before/metrics.json',
        'metrics_path_after': 'data/exp_partof_broad_after/metrics.json',
        'experiment_path': 'experiments/exp_substrate_b_alpha_broad_envelope_cpu_v1.py (re-run before/after on the PART_OF-completed substrate)',
        'completion_tool': 'tools/substrate_partof_2level_completion_2026-06-18.py (+125 holonym-direction edges, 0 new atoms)',
        'key_metrics': {
            'recall_after_completion': {'PART_OF_2hop': 0.820, 'PART_OF_3hop': 0.700,
                                        'HYPERNYM_2hop': 0.993, 'HYPERNYM_3hop': 0.931, 'HYPERNYM_4hop': 0.853},
            'recall_baseline_pre_completion': {'PART_OF_2hop': 0.627, 'PART_OF_3hop': 0.500,
                                               'HYPERNYM_2hop': 0.993, 'HYPERNYM_3hop': 0.931, 'HYPERNYM_4hop': 0.853},
            'recovery_delta': {'PART_OF_2hop': 0.193, 'PART_OF_3hop': 0.200,
                               'HYPERNYM_2hop': 0.0, 'HYPERNYM_3hop': 0.0, 'HYPERNYM_4hop': 0.0},
            'completion_edges_added': 125, 'holonym_gap_pct_over_baseline': 28.8, 'new_atoms_added': 0,
            'envelope_before': '3 HARD_PASS / 2 MIDDLE / 0 HARD_FAIL', 'envelope_after': '5 HARD_PASS / 0 MIDDLE / 0 HARD_FAIL',
            'provenance_sound': True, 'false_positives': 0,
        },
        'cert_value': CERT_VALUE, 'coextensiveness_caveat': COEXTENSIVE_CAVEAT, 'claim_scope': SCOPE, 'honest_scope': SCOPE,
        'min_cert_along_path': 'WordNet PART_OF edges ontology-INGESTED (LEXICON tier), not experiment-cert; the RECOVERY is MEASURED_MECHANISM (coextensive), not a cert-counted lever.',
        'depth_cliff_verdict_generalization': 'COVERAGE-limited-not-algorithmic now confirmed for a SECOND relation type (PART_OF, like HYPERNYM). The depth-cliff coverage-story GENERALIZES across relation types: apparent depth-robustness differences reflect baseline ingest-completeness, NOT algorithmic differences. Canonical-direct-link completion is the universal lever. REFUTES the prior PART_OF-depth-robust framing.',
        'bears_on': 'T3 Phase A2 2-level recovery (HYPERNYM; this is the 2nd relation-type witness of the SAME coverage-limited mechanism); B-alpha BROAD envelope (PART_OF now HARD_PASS); the depth-cliff coverage-vs-algorithmic question',
        'strengthens_cert': [RECOVERY_QID],
        'schema_vet_by': 'skunkworks', 'verdict_vet_by': 'skunkworks_pending', 'vet_date': '2026-06-18',
        'vet_note': 'Skunkworks Item 1 SCHEMA-VET PASS + pre-stated tier-by-outcome (JUMPS -> MEASURED_MECHANISM ATTRIBUTION coextensive); tier-call/landed-verify routed. CERT stays 570; coextensiveness + scope notes carried.',
        'eleventh_rule_clean': True, 'deterministic_no_llm': True,
        'source': 'partof_2level_completion_recovery_measured_mechanism_item1_20h_sprint',
    }
    return Atom(
        id=ATOM_ID,
        name='Measured mechanism (MEASURED_MECHANISM): PART_OF 2-level completion RECOVERS PART_OF recall (0.627->0.820, 0.500->0.700) -> PART_OF ALSO coverage-limited; depth-cliff coverage-story generalizes across relation types',
        description='MEASURED_MECHANISM (verdict ATTRIBUTION; NOT cert-counted; coextensive). ' + CERT_VALUE + ' CAVEAT: ' + COEXTENSIVE_CAVEAT,
        kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None, metadata=metadata,
    )


def main() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    print(f'PRE: axiom_term={pre_axiom}  cap_pres={pre_mod}  CERT={pre_cert}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1
    if ps.get_atom(f'math::{ATOM_ID}') is not None:
        print(f'SKIP (idempotent): {ATOM_ID}'); return 0
    atom = build_atom()
    ps.add_atom(atom, source='partof_2level_recovery_measured_mechanism', note='Item 1; MEASURED_MECHANISM (verdict=ATTRIBUTION); CERT 570 unchanged')
    edge_added = False
    if ps.get_atom(RECOVERY_QID) is not None:
        try:
            ps.add_relation(f'math::{ATOM_ID}', RelationType.STRENGTHENS, RECOVERY_QID,
                            source='partof_2level_recovery_measured_mechanism', note='2nd relation-type witness of coverage-limited-not-algorithmic; generalizes the HYPERNYM recovery')
            edge_added = True
        except Exception as e:
            print(f'WARN: STRENGTHENS edge not added ({str(e)[:60]})')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps2); post_mod = module_liveness_ok(); post_cert = cert_count(ps2)
    rb = ps2.get_atom(f'math::{ATOM_ID}')
    rb_ok = (rb is not None and rb.kind == AtomKind.EXPERIMENT_RECORD and rb.algebra is None
             and rb.metadata.get('provenance_quality') == 'MEASURED_MECHANISM' and rb.metadata.get('verdict') == 'ATTRIBUTION')
    gate_ok = post_axiom == 206 and post_mod and post_cert == pre_cert and rb_ok
    print(f'POST: axiom_term={post_axiom}  cap_pres={post_mod}  CERT={post_cert} (unchanged from {pre_cert})  read-back_ok={rb_ok}  strengthens_edge={edge_added}')
    if not gate_ok:
        print('HARD_FAIL: gate/read-back failed (CERT must stay unchanged). Reverting.')
        ps2.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail'); return 2
    print('=' * 72)
    print(f'PART_OF 2-level RECOVERY landed: math::{ATOM_ID}  MEASURED_MECHANISM  CERT {post_cert} (unchanged)  axiom_term 206  cap_pres 6/6')
    print('  Depth-cliff coverage-story GENERALIZES: PART_OF also coverage-limited (2nd relation-type witness). Route landed-verify + tier-call to Skunkworks + Testbed 2nd-witness.')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
