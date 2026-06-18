"""Scoped creation: B-delta v2-final as a CERT-eligible EXPERIMENT_RECORD (Skunkworks verdict-VET CONFIRM + atomize GO).

Capacity-lever cross-VALUE-TYPE transfer CONFIRMED (full grid, both working-baseline cliffs verified independently by
Skunkworks + by me). CERT 568 -> 569. Honest VALUE-TYPE scope (NOT key-distribution). Uses first-class STRENGTHENS
rel_type edges (E2) -> ARCH-B + C1 (the one-lever thesis it strengthens). Mirrors the A3 CERT-grade EXPERIMENT_RECORD.
ASCII-only. No LLM. Laptop-safe.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_b_delta_readout_lever_transfer_v2'
ARCH_B = 'math::T3/EXP_arch_b_replicate_n2048_v1'
C1 = 'math::T3/EXP_substrate_C1_entmax_alpha_readout_v1'

# Skunkworks verbatim CONFIRM scope.
SCOPE = (
    "The nonlinear-readout CAPACITY lever (modern-Hopfield softmax EXTENDS associative-memory capacity past the linear "
    "~0.14N cliff) generalizes across VALUE-TYPE (bipolar + continuous-Gaussian values; both uniform i.i.d. keys). NOT "
    "tested across key-distribution (clustered = separate interference study; mild-correlation = follow-up). "
    "Measured-bounds at N=1024/noise=0.15, NOT fundamental."
)


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


def axiom_term_count(ps) -> int:
    return sum(
        1 for a in ps.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def cert_count(ps) -> int:
    return sum(1 for a in ps.all_atoms() if a.metadata.get('provenance_quality') == 'CERT_CHAIN_GRADE')


def build_atom() -> Atom:
    metadata = {
        'record_class': 'experiment_record',
        'term_class': 'capability_frontier',
        'metric_type': 'capacity_extension_recall',
        'experiment_path': 'experiments/exp_substrate_b_delta_readout_lever_transfer_v1.py',
        'metrics_path': 'data/exp_b_delta_readout_lever_transfer_v2/metrics.json',
        'cell_sha': '764ec487',
        'hypothesis': 'Does the nonlinear-readout capacity lever transfer across value-type (bipolar vs continuous)?',
        'metrics_headline': SCOPE,
        'key_metrics': {
            'bipolar_lin_cliff': 'M64=1.0 M128=1.0 M256=1.0 M512=0.002 M1024=0.0',
            'continuous_lin_cliff': 'M64=1.0 M128=1.0 M256=0.259 M512=0.0 M1024=0.0',
            'nonlinear_recall_all_M': '1.0 (both value-types, every M)',
            'capacity_extension_pp': {'bipolar': 100.0, 'continuous': 100.0},
            'both_working_baseline_cliffs': True,
            'generality_axis': 'VALUE_TYPE_not_key_distribution',
            'n_seeds': 3, 'n_cells': 30, 'N': 1024, 'noise': 0.15,
            'discrimination': 'both tasks working-baseline-cliff (first B-epsilon real adoption)',
        },
        'strengthens_cert': [ARCH_B, C1],   # the one-lever thesis it strengthens (value-type axis)
        'verdict': 'HARD_PASS',
        'verdict_raw': 'HARD_PASS',
        'relevance_tier': 'HIGH',
        'run_mode': 'full',
        'metrics_source': 'measured_torch_gpu',
        'era': 'PHASE-2',
        'provenance_quality': 'CERT_CHAIN_GRADE',   # full + measured + n_seeds>=3 + gate0 + method-gate (Skunkworks GO)
        'n_seeds': 3,
        'gate0_self_check_pass': True,
        'claim_scope': SCOPE,
        'value_type_scope_honest': 'tests value-type generality; NOT key-distribution (clustered=interference study; mild-correlation=follow-up)',
        'verdict_vet_by': 'skunkworks', 'verdict_vet_date': '2026-06-18',
        'verdict_vet_note': 'CONFIRM (read actual v2 metrics; both full-grid working-baseline cliffs verified; v1 was degenerate NON_TEST)',
        'eleventh_rule_clean': True, 'deterministic_no_llm': True,
        'source': 'b_delta_v2_cert_experiment_record_capacity_lever_value_type_transfer',
    }
    return Atom(
        id=ATOM_ID,
        name='Experiment record (CERT): nonlinear-readout capacity lever transfers across value-type (B-delta v2)',
        description='CERT_CHAIN_GRADE capacity-lever cross-value-type transfer. ' + SCOPE,
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
    # 0-phantom: strengthens targets must resolve
    if ps.get_atom(ARCH_B) is None or ps.get_atom(C1) is None:
        print(f'PHANTOM: strengthens target missing (ARCH_B={ps.get_atom(ARCH_B) is not None}, C1={ps.get_atom(C1) is not None}). Halt.'); return 4
    if ps.get_atom(f'math::{ATOM_ID}') is not None:
        print(f'SKIP (idempotent): {ATOM_ID}'); return 0

    atom = build_atom()
    ps.add_atom(atom, source='b_delta_v2_cert', note='capacity-lever value-type transfer CONFIRMED; Skunkworks verdict-VET GO; CERT 568->569')
    # first-class STRENGTHENS edges (E2) -> ARCH-B + C1 (role IS the rel_type, persists)
    ps.add_relation(f'math::{ATOM_ID}', RelationType.STRENGTHENS, ARCH_B, source='b_delta_v2_strengthens', note='value-type axis of the one-lever thesis')
    ps.add_relation(f'math::{ATOM_ID}', RelationType.STRENGTHENS, C1, source='b_delta_v2_strengthens', note='value-type axis of the one-lever thesis')

    ps2 = PartitionedStore(Path('data/substrate_index'))   # fresh reload verify
    post_axiom = axiom_term_count(ps2); post_mod = module_liveness_ok(); post_cert = cert_count(ps2)
    rb = ps2.get_atom(f'math::{ATOM_ID}')
    rb_ok = (rb is not None and rb.kind == AtomKind.EXPERIMENT_RECORD and rb.algebra is None
             and rb.metadata.get('provenance_quality') == 'CERT_CHAIN_GRADE' and SCOPE in (rb.metadata.get('claim_scope') or ''))
    gate_ok = post_axiom == 206 and post_mod and post_cert == pre_cert + 1 and rb_ok
    print(f'POST: axiom_term={post_axiom}  cap_pres={post_mod}  CERT={post_cert} (was {pre_cert})  read-back_ok={rb_ok}')
    if not gate_ok:
        print('HARD_FAIL: gate/read-back failed. Reverting.')
        ps2.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail'); return 2
    print('=' * 72)
    print(f'B-delta v2 CERT EXPERIMENT_RECORD landed: math::{ATOM_ID}  CERT {pre_cert}->{post_cert}  axiom_term 206  cap_pres 6/6')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
