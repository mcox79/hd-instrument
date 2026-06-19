"""Scoped creation: A1 multi-hop-provenance as MEASURED_MECHANISM (Skunkworks SCHEMA-VET PASS + tier ruling 2026-06-18).

A1 = deterministic provenance-sound multi-hop traversal over the materialized typed-edge backbone. The 1.0/1.0 result
is BY-CONSTRUCTION (a deterministic COMPLETE walker over the same graph it samples) -> NOT a discriminating performance
cert; it IS a valid MEASURED mechanism-existence + provenance-soundness DEMONSTRATION + the 5th-gate's CONTROL.
verdict=ATTRIBUTION -> pq=MEASURED_MECHANISM. Keeps CERT at 569 (no by-construction inflation). Mirrors the A1-v2
MEASURED_MECHANISM create. ASCII-only. No LLM. Laptop-safe.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_a1_multihop_provenance_cpu_v1'
EDGEMAT = 'math::T3/EXP_b_delta_readout_lever_transfer_v2'   # placeholder bears_on (no edge-materialization atom); use the typed-edge context

# Skunkworks honest cert-VALUE framing (verbatim intent).
CERT_VALUE = (
    "A1 DEMONSTRATES (by-construction) that a deterministic provenance-sound multi-hop traversal mechanism EXISTS over "
    "the materialized typed-edge backbone, and ESTABLISHES the multi-hop-provenance gate (5th self-cert gate). A1 is the "
    "CONTROL: the gate + metric earn their DISCRIMINATING value on a FUTURE non-trivial walker (cross-corpus where "
    "reachability is not guaranteed, or a learned/embedding walker that COULD hallucinate a hop) -- that is where "
    "MEASURED_MECHANISM becomes a discriminating CERT; that scale-up awaits USER ARC-1 ratify."
)
SCOPE = (
    "provenance-verified multi-hop PATH-FINDING over the materialized within-5k typed-edge backbone (IS_A/HYPERNYM/"
    "PART_OF); NOT general reasoning / NOT 'the substrate reasons'. ARC-1 T1 proof-of-mechanism (narrow, honest-scoped); "
    "scale-up awaits USER ratify. min-cert-along-path: PATH is provenance-CERT (every edge a persisted Store tuple); "
    "per-answer CLAIM-cert = weakest edge tier = ontology-INGESTED (IS_A/HYPERNYM/PART_OF from WordNet/GO, not experiment-cert)."
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
    return sum(1 for a in ps.all_atoms() if a.metadata.get('provenance_quality') == 'CERT_CHAIN_GRADE')


def build_atom() -> Atom:
    metadata = {
        'record_class': 'measured_mechanism',
        'verdict': 'ATTRIBUTION',
        'provenance_quality': 'MEASURED_MECHANISM',   # by-construction 1.0/1.0 -> not cert-counted (Skunkworks tier ruling)
        'relevance_tier': 'ARCHIVE',
        'run_mode': 'full',
        'metrics_source': 'measured_graph_bfs',
        'metrics_path': 'data/substrate_a1_multihop_provenance_cpu_v1/metrics.json',
        'experiment_path': 'experiments/exp_substrate_a1_multihop_provenance_cpu_v1.py',
        'cell_commit': '35ec2a55',
        'key_metrics': {
            'answer_found': 1.0, 'refuse_rate': 1.0, 'path_edges_total': 600, 'path_edges_unverifiable': 0,
            'is_provenance_sound': True, 'n_answerable': 300, 'n_distractor': 300, 'n_2hop_chains_available': 11944,
            'by_construction': 'deterministic complete walker over the sampled graph -> 1.0/1.0 saturated (control, not performance-cert)',
        },
        'cert_value': CERT_VALUE,
        'claim_scope': SCOPE,
        'min_cert_along_path': 'ontology-INGESTED edge tier (IS_A/HYPERNYM/PART_OF; WordNet/GO; NOT experiment-cert)',
        'fifth_self_cert_gate': 'path_provenance_self_check (producer 35ec2a55) + path_provenance_gate (consumer a7497620); engine 4->5',
        'composed_reasoning_arc': 'ARC-1 T1 proof-of-mechanism; scale-up (cross-corpus / learned walker) awaits USER ratify',
        'bears_on': 'TRACK-3 edge-materialization (IS_A/HYPERNYM/PART_OF typed edges); the 5-gate self-cert engine; composed-reasoning hand-off A1',
        'schema_vet_by': 'skunkworks', 'verdict_vet_by': 'skunkworks', 'vet_date': '2026-06-18',
        'vet_note': 'SCHEMA-VET PASS (5 cert-conditions) + tier=MEASURED_MECHANISM (1.0/1.0 by-construction = soundness-demo CONTROL, not discriminating perf-cert; NOT NON_TEST [by-design demo, not degenerate-hiding-signal])',
        'eleventh_rule_clean': True, 'deterministic_no_llm': True,
        'source': 'a1_multihop_provenance_measured_mechanism_skunkworks_tier_ruling',
    }
    return Atom(
        id=ATOM_ID,
        name='Measured mechanism (MEASURED_MECHANISM): deterministic provenance-sound multi-hop traversal over the typed-edge KG (A1; 5th-gate control)',
        description='MEASURED_MECHANISM (verdict ATTRIBUTION; NOT cert-counted). ' + CERT_VALUE + ' SCOPE: ' + SCOPE,
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata=metadata,
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
    ps.add_atom(atom, source='a1_multihop_provenance_measured_mechanism', note='Skunkworks SCHEMA-VET PASS + MEASURED_MECHANISM tier; CERT 569 unchanged')

    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps2); post_mod = module_liveness_ok(); post_cert = cert_count(ps2)
    rb = ps2.get_atom(f'math::{ATOM_ID}')
    rb_ok = (rb is not None and rb.kind == AtomKind.EXPERIMENT_RECORD and rb.algebra is None
             and rb.metadata.get('provenance_quality') == 'MEASURED_MECHANISM')
    gate_ok = post_axiom == 206 and post_mod and post_cert == pre_cert and rb_ok   # CERT UNCHANGED (key: no inflation)
    print(f'POST: axiom_term={post_axiom}  cap_pres={post_mod}  CERT={post_cert} (unchanged from {pre_cert})  read-back_ok={rb_ok}')
    if not gate_ok:
        print('HARD_FAIL: gate/read-back failed (CERT must stay unchanged). Reverting.')
        ps2.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail'); return 2
    print('=' * 72)
    print(f'A1 MEASURED_MECHANISM landed: math::{ATOM_ID}  CERT {post_cert} (unchanged)  axiom_term 206  cap_pres 6/6')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
