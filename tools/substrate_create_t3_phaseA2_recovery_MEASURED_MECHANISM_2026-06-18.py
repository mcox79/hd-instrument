"""Scoped creation: T3 Phase A2 2-level RECOVERY as MEASURED_MECHANISM (verdict=ATTRIBUTION; Skunkworks forward
cert-condition 2026-06-18). The discriminating-contrast arm that completes the depth-cliff verdict.

Phase A2 materialized the new intermediates' OWN canonical direct-parent edges (+1110 gold-independent edges, 0 new
atoms). Re-running BROAD on this 2-level substrate -> HYPERNYM RECOVERS across ALL depths:
  HYP-2 0.607->0.993 | HYP-3 0.368->0.931 | HYP-4 0.200->0.853 (all HARD_PASS) | PART_OF unchanged (separate axis, not densified).

CERT-TIER (Skunkworks ruling, FORWARD cert-condition): verdict=ATTRIBUTION -> MEASURED_MECHANISM, NOT CERT_CHAIN_GRADE.
The selection is gold-INDEPENDENT (not fraud) BUT the intervention materializes the canonical hypernym CLOSURE =
COEXTENSIVE with what the n-hop QA traverses -> near-tautological (the A1 1.0/1.0 parallel). The 0.993/0.931/0.853
measures PATH-COMPLETENESS + BFS-CORRECTNESS, NOT a generalizable lever-magnitude. CERT stays 570 (NOT cert-counted).

THE DISCRIMINATOR (the scientific value): Phase A FLAT (1-level, CERT HONEST_NEGATIVE) + this 2-level RECOVERY +
BFS-correct (5th gate) => the HYPERNYM depth-cliff is COVERAGE-limited (ingest-completeness artifact), NOT algorithmic.
The substrate CAN reason deeply over hypernyms given complete canonical paths; coverage requirement SCALES with depth.
SCOPE precision (Skunkworks note-2): "2-level + partial-deeper via inter-intermediate (among-new) chains" -- explains
HYP-4 0.853. ASCII. No LLM.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_t3_phaseA2_2level_recovery_cpu_v1'
FLAT_QID = 'math::T3/EXP_t3_phaseA_completeness_1level_FLAT_cpu_v1'   # STRENGTHENS target (the 1-level null this contrasts)

CERT_VALUE = (
    "T3 Phase A2 2-level completion (+1110 gold-independent second-hop edges Y->canonical-parent; 0 new atoms) -> BROAD "
    "HYPERNYM RECOVERS across ALL depths: HYP-2 0.607->0.993, HYP-3 0.368->0.931, HYP-4 0.200->0.853 (all HARD_PASS; "
    "100% provenance-sound, 0 FP). PART_OF unchanged (separate axis, not densified). The 1-level-FLAT (CERT null) vs "
    "2-level-RECOVERS CONTRAST + BFS-correctness (5th gate) => the HYPERNYM depth-cliff is COVERAGE-limited (ingest-"
    "completeness artifact), NOT algorithmic. The substrate CAN reason deeply over hypernyms given complete canonical "
    "paths; the coverage requirement SCALES with depth (n-hop needs n-level)."
)
COEXTENSIVE_CAVEAT = (
    "MEASURED_MECHANISM (verdict=ATTRIBUTION), NOT CERT: gold-INDEPENDENT selection (not by-construction-fraud) BUT the "
    "intervention materializes the canonical hypernym CLOSURE = COEXTENSIVE with what n-hop QA traverses -> near-"
    "tautological (the A1 1.0/1.0 parallel). The 0.993/0.931/0.853 measures path-completeness + BFS-correctness, NOT a "
    "generalizable capability-lever magnitude. The SCIENTIFIC value is the CONTRAST (1-level FLAT vs 2-level RECOVERS) "
    "that discriminates coverage-vs-algorithmic -- THAT is the cert-grade finding (in the Phase A FLAT atom + this contrast)."
)
SCOPE = (
    "HYPERNYM/taxonomic/WordNet/deterministic-BFS/in5k closure. 2-LEVEL + PARTIAL-DEEPER: the 333 among-new edges "
    "(Y->another-new-Y) extend the canonical closure via inter-intermediate chains -> partial-3-level -> explains HYP-4 "
    "recovering to 0.853 (its 3rd/4th edges are new-Y parents now present). Gold-independent (each synset's canonical "
    "direct-parent), consistent with the coextensive-MEASURED_MECHANISM framing. min-cert-along-path: WordNet edges are "
    "ontology-INGESTED (LEXICON tier), not experiment-cert. NOT a one-shot fix; NOT a non-taxonomic claim."
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
        'verdict': 'ATTRIBUTION',                      # -> MEASURED_MECHANISM (NOT cert-counted; the forward cert-condition)
        'provenance_quality': 'MEASURED_MECHANISM',
        'relevance_tier': 'ARCHIVE',
        'run_mode': 'full', 'n_seeds': 1, 'metrics_source': 'measured_graph_bfs_held_out',
        'metrics_path': 'data/exp_b_alpha_broad_v3_2level/metrics.json',
        'experiment_path': 'experiments/exp_substrate_b_alpha_broad_envelope_cpu_v1.py (re-run on the 2-level substrate)',
        'phase_a2_edgemat': 'tools/substrate_wordnet_completeness_t3_phaseA2_secondhop.py (+1110 second-hop edges, 0 new atoms)',
        'key_metrics': {
            'recall_2level': {'HYPERNYM_2hop': 0.993, 'HYPERNYM_3hop': 0.931, 'HYPERNYM_4hop': 0.853,
                              'PART_OF_2hop': 0.627, 'PART_OF_3hop': 0.500},
            'recall_baseline_1level_flat': {'HYPERNYM_2hop': 0.607, 'HYPERNYM_3hop': 0.368, 'HYPERNYM_4hop': 0.200,
                                            'PART_OF_2hop': 0.627, 'PART_OF_3hop': 0.500},
            'recovery_delta': {'HYPERNYM_2hop': 0.386, 'HYPERNYM_3hop': 0.563, 'HYPERNYM_4hop': 0.653,
                               'PART_OF_2hop': 0.0, 'PART_OF_3hop': 0.0},
            'second_hop_edges_added': 1110, 'new_atoms_added': 0, 'envelope': '3 HARD_PASS / 2 MIDDLE / 0 HARD_FAIL',
            'provenance_sound': True, 'false_positives': 0,
        },
        'cert_value': CERT_VALUE, 'coextensiveness_caveat': COEXTENSIVE_CAVEAT, 'claim_scope': SCOPE, 'honest_scope': SCOPE,
        'min_cert_along_path': 'WordNet HYPERNYM edges ontology-INGESTED (LEXICON tier), not experiment-cert; the RECOVERY is MEASURED_MECHANISM (coextensive), not a cert-counted lever.',
        'depth_cliff_verdict': 'COVERAGE-limited (ingest-completeness artifact), NOT algorithmic. Phase A FLAT (1-level, CERT HONEST_NEGATIVE) + 2-level RECOVERY (this, MEASURED_MECHANISM) + 5th-gate BFS-correct = the combined verdict. Substrate CAN reason deeply over hypernyms given complete canonical paths; coverage scales with depth. PART_OF separate axis (depth-robust at baseline).',
        'bears_on': 'T3 Phase A FLAT (the 1-level null this contrasts); T3 Phase A2 edge-mat; B-alpha BROAD; the depth-cliff coverage-vs-algorithmic question',
        'strengthens_cert': [FLAT_QID],
        'schema_vet_by': 'skunkworks', 'verdict_vet_by': 'skunkworks', 'vet_date': '2026-06-18',
        'vet_note': 'Skunkworks forward cert-condition: recovery = verdict=ATTRIBUTION -> MEASURED_MECHANISM (NOT PASS/CERT -- coextensive false-cert avoided); CERT stays 570; coextensiveness + 2-level+partial-deeper scope notes carried',
        'eleventh_rule_clean': True, 'deterministic_no_llm': True,
        'source': 't3_phaseA2_2level_recovery_measured_mechanism_skunkworks_forward_cert_condition',
    }
    return Atom(
        id=ATOM_ID,
        name='Measured mechanism (MEASURED_MECHANISM): 2-level canonical-path completion RECOVERS the HYPERNYM depth-cliff (0.607->0.993 etc.) -> coverage-limited not algorithmic',
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
    ps.add_atom(atom, source='t3_phaseA2_2level_recovery_measured_mechanism', note='Skunkworks MEASURED_MECHANISM (verdict=ATTRIBUTION); CERT 570 unchanged')
    edge_added = False
    if ps.get_atom(FLAT_QID) is not None:
        try:
            ps.add_relation(f'math::{ATOM_ID}', RelationType.STRENGTHENS, FLAT_QID,
                            source='t3_phaseA2_2level_recovery_measured_mechanism', note='2-level recovery contrasts/strengthens the 1-level FLAT null -> coverage-limited')
            edge_added = True
        except Exception as e:
            print(f'WARN: STRENGTHENS edge not added ({str(e)[:60]})')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps2); post_mod = module_liveness_ok(); post_cert = cert_count(ps2)
    rb = ps2.get_atom(f'math::{ATOM_ID}')
    rb_ok = (rb is not None and rb.kind == AtomKind.EXPERIMENT_RECORD and rb.algebra is None
             and rb.metadata.get('provenance_quality') == 'MEASURED_MECHANISM' and rb.metadata.get('verdict') == 'ATTRIBUTION')
    gate_ok = post_axiom == 206 and post_mod and post_cert == pre_cert and rb_ok   # CERT UNCHANGED (MEASURED_MECHANISM)
    print(f'POST: axiom_term={post_axiom}  cap_pres={post_mod}  CERT={post_cert} (unchanged from {pre_cert})  read-back_ok={rb_ok}  strengthens_edge={edge_added}')
    if not gate_ok:
        print('HARD_FAIL: gate/read-back failed (CERT must stay unchanged). Reverting.')
        ps2.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail'); return 2
    print('=' * 72)
    print(f'T3 Phase A2 RECOVERY landed: math::{ATOM_ID}  MEASURED_MECHANISM  CERT {post_cert} (unchanged)  axiom_term 206  cap_pres 6/6')
    print('  Depth-cliff verdict COMPLETE: coverage-limited not algorithmic (1-level FLAT [CERT] + 2-level RECOVERS [MM] + BFS-correct).')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
