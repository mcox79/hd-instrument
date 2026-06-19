"""Scoped creation: T3 Phase A 1-level-completion FLAT result as CERT_CHAIN_GRADE HONEST_NEGATIVE (Skunkworks tier-call
2026-06-18). The cleanest cert-grade piece of the depth-cliff centerpiece: a rigorous, gold-INDEPENDENT, DISCRIMINATING
pre-reg NULL with empirical root-cause = cert-grade NEGATIVE-KNOWLEDGE.

FINDING: T3 Phase A completed every in-5k synset's direct-parent link (gold-independent; +1339 LEXICON atoms + 2219
in5k->new-parent HYPERNYM edges; backbone 2884->5103, +77% density). Re-running BROAD on this denser substrate -> recall
UNCHANGED vs baseline (HYP-2 0.607, HYP-3 0.368, HYP-4 0.200, PART_OF-2 0.627, PART_OF-3 0.500; delta ~0). EMPIRICAL
ROOT-CAUSE (verify-the-referent, not inferred): the no-recursion 1-level added the intermediates' INCOMING edges
(in5k->Y, 2219) but 0 OUTGOING (Y->z); a 2-hop chain x->Y->z needs BOTH -> dangling-upward intermediates -> 0 chains
completed -> FLAT. So 1-level direct-parent completion is INSUFFICIENT for multi-hop recovery: a path needs ALL its edges.
The pre-reg "2-hop recovers from direct-parent completion" was EMPIRICALLY FALSE (pre-reg-sacrosanct: recorded).

verdict=HONEST_NEGATIVE -> CERT_CHAIN_GRADE (a rigorous discriminating verdict-null, NOT a verdict-less attribution).
CERT 569 -> 570 (ADDITIVE; A5-clean). Contrast w/ the 2-level recovery (MEASURED_MECHANISM, separate atom) DISCRIMINATES
coverage-vs-algorithmic -> the centerpiece answer: depth-cliff is COVERAGE-limited, NOT algorithmic. ASCII. No LLM.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_t3_phaseA_completeness_1level_FLAT_cpu_v1'
BROAD_QID = 'math::T3/EXP_b_alpha_broad_envelope_cpu_v1'   # STRENGTHENS target (the baseline this nulls against)

CERT_VALUE = (
    "T3 Phase A 1-level direct-parent COMPLETENESS (gold-independent; +1339 LEXICON atoms + 2219 in5k->parent HYPERNYM "
    "edges; backbone 2884->5103, +77% density) -> BROAD recall UNCHANGED vs baseline (FLAT: HYP-2 0.607, HYP-3 0.368, "
    "HYP-4 0.200, PART_OF-2 0.627, PART_OF-3 0.500; delta ~0). EMPIRICAL ROOT-CAUSE: the new intermediates have 2219 "
    "INCOMING edges (in5k->Y) but 0 OUTGOING (Y->z); a 2-hop chain x->Y->z needs BOTH hops -> dangling-upward -> 0 chains "
    "completed -> FLAT. => 1-level direct-parent completion is INSUFFICIENT for multi-hop recovery (a path needs ALL its "
    "edges). DISCRIMINATING gold-independent pre-reg NULL (recall could have moved with +77% edges; it did not)."
)
SCOPE = (
    "HYPERNYM/PART_OF taxonomic; WordNet; deterministic-BFS. The pre-reg DIRECTION ('coverage matters') held but the "
    "SPECIFIC '2-hop recovers from 1-level completion' was EMPIRICALLY FALSE -> the honest correction: coverage recovery "
    "needs FULL-PATH (all-edges-along-chain) completion, scaling with depth (n-hop needs n-level). This 1-level-FLAT is "
    "the clean discriminating NULL; the 2-level-recovers contrast (separate MEASURED_MECHANISM atom) confirms "
    "COVERAGE-limited-not-algorithmic. min-cert-along-path: WordNet edges are ontology-INGESTED (LEXICON tier), not "
    "experiment-cert; the RESULT (FLAT recall + empirical root-cause) is the cert-grade discriminating verdict."
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
        'record_class': 'experiment_record', 'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'verdict': 'HONEST_NEGATIVE', 'provenance_quality': 'CERT_CHAIN_GRADE', 'relevance_tier': 'SUPPORTING',
        'run_mode': 'full', 'n_seeds': 1, 'metrics_source': 'measured_graph_bfs_held_out', 'held_out_eval': True,
        'prereg_bands': {'hard_pass': 0.70, 'hard_fail': 0.40},
        'metrics_path': 'data/exp_b_alpha_broad_v2_denser_preview/metrics.json',
        'experiment_path': 'experiments/exp_substrate_b_alpha_broad_envelope_cpu_v1.py (re-run on the +77%-denser substrate)',
        'phase_a_ingest': 'tools/substrate_wordnet_completeness_t3_phaseA.py (+1339 LEXICON atoms, +2219 HYPERNYM edges)',
        'key_metrics': {
            'recall_v2_denser': {'HYPERNYM_2hop': 0.607, 'HYPERNYM_3hop': 0.368, 'HYPERNYM_4hop': 0.200,
                                 'PART_OF_2hop': 0.627, 'PART_OF_3hop': 0.500},
            'recall_baseline': {'HYPERNYM_2hop': 0.607, 'HYPERNYM_3hop': 0.368, 'HYPERNYM_4hop': 0.200,
                                'PART_OF_2hop': 0.627, 'PART_OF_3hop': 0.500},
            'recall_delta': {'HYPERNYM_2hop': 0.0, 'HYPERNYM_3hop': 0.0, 'HYPERNYM_4hop': 0.0,
                             'PART_OF_2hop': 0.0, 'PART_OF_3hop': 0.0},
            'densification': {'atoms_added': 1339, 'hypernym_edges_added': 2219, 'backbone_2884_to_5103': '+77pct'},
            'root_cause': 'new intermediates: 2219 INCOMING edges (in5k->Y), 0 OUTGOING (Y->z) -> dangling-upward -> 0 two-hop chains completed',
        },
        'cert_value': CERT_VALUE, 'claim_scope': SCOPE,
        'min_cert_along_path': 'WordNet HYPERNYM edges ontology-INGESTED (LEXICON tier, not experiment-cert); the RESULT (FLAT recall + empirical root-cause) is the cert-grade discriminating verdict.',
        'honest_scope': SCOPE,
        'depth_cliff_finding': '1-level direct-parent completion INSUFFICIENT for multi-hop recovery (path needs all edges); '
                               'the 2-level-recovers contrast (separate MEASURED_MECHANISM) -> depth-cliff COVERAGE-limited not algorithmic',
        'pre_reg_correction': 'pre-reg "2-hop recovers from 1-level direct-parent completion" was EMPIRICALLY FALSE (recorded; pre-reg-sacrosanct); direction (coverage matters) held',
        'bears_on': 'B-alpha BROAD baseline (the null vs it); T3 Phase A completeness ingest; the depth-cliff coverage-vs-algorithmic question',
        'strengthens_cert': [BROAD_QID],
        'schema_vet_by': 'skunkworks', 'verdict_vet_by': 'skunkworks', 'vet_date': '2026-06-18',
        'vet_note': 'Skunkworks cert-tier call: rigorous gold-independent DISCRIMINATING pre-reg NULL + empirical root-cause -> CERT_CHAIN_GRADE HONEST_NEGATIVE (tier-up from MEASURED_MECHANISM lean; negative-knowledge kept cert-grade)',
        'eleventh_rule_clean': True, 'deterministic_no_llm': True,
        'source': 't3_phaseA_1level_FLAT_honest_negative_skunkworks_tier_call',
    }
    return Atom(
        id=ATOM_ID,
        name='CERT (CERT_CHAIN_GRADE HONEST_NEGATIVE): 1-level direct-parent completion does NOT recover the multi-hop depth-cliff (FLAT; path needs all edges)',
        description='CERT_CHAIN_GRADE HONEST_NEGATIVE (discriminating pre-reg null). ' + CERT_VALUE + ' SCOPE: ' + SCOPE,
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
    ps.add_atom(atom, source='t3_phaseA_1level_FLAT_honest_negative', note='Skunkworks tier-call CERT_CHAIN_GRADE HONEST_NEGATIVE; CERT 569->570')
    edge_added = False
    if ps.get_atom(BROAD_QID) is not None:
        try:
            ps.add_relation(f'math::{ATOM_ID}', RelationType.STRENGTHENS, BROAD_QID,
                            source='t3_phaseA_1level_FLAT_honest_negative', note='1-level FLAT null strengthens the BROAD baseline finding')
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
    print(f'T3 Phase A FLAT landed: math::{ATOM_ID}  CERT {post_cert} (569->570)  axiom_term 206  cap_pres 6/6')
    print('  Depth-cliff centerpiece: 1-level completion = FLAT (cert-grade discriminating null); coverage-limited-not-algorithmic.')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
