"""Scoped creation: B-alpha BROAD as ONE CERT_CHAIN_GRADE MIDDLE_BAND ENVELOPE atom (Skunkworks Q-b i + tier ruling).

The ARC-1 T2 milestone: the multi-benchmark composed-reasoning ENVELOPE characterizing WHERE deterministic multi-hop QA
over the materialized typed-edge backbone works vs CLIFFS. v2 (HYP-3 full-gold) envelope = 0P/3M/2F: HYPERNYM cliffs at
3+ hops (HARD_FAIL), PART_OF depth-robust (2-3 hop MIDDLE). The depth-cliff is the HONEST FINDING (named first-class in
headline + honest_scope so it's queryable as a cliff, not buried). ONE envelope atom (Q-b i: count-honesty; per-benchmark
in key_metrics). CERT 570 -> 571.

Reads the CANONICAL dispatched metrics (path arg; default the dispatched dir). refuse-until-VET-PASS guard. STRENGTHENS
edges -> B-alpha NARROW (its single-benchmark predecessor) + A1 (control). axiom_term/cap_pres gated; CERT==pre+1; revert-
on-fail. RUN ONLY AFTER Skunkworks's verdict-VET + tier ruling on the dispatched verdict (no-self-certify). ASCII-only. No LLM.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_b_alpha_broad_envelope_cpu_v1'
NARROW_QID = 'math::T3/EXP_b_alpha_2hop_hypernym_qa_cpu_v1'   # BROAD generalizes NARROW (STRENGTHENS)
A1_QID = 'math::T3/EXP_a1_multihop_provenance_cpu_v1'
DEFAULT_CANON = Path('data/exp_b_alpha_broad_envelope_v1/metrics.json')


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


def vet_guard(m: dict) -> bool:
    env = m.get('envelope') or {}
    checks = {
        'verdict==MIDDLE_BAND': m.get('verdict') == 'MIDDLE_BAND',
        'held_out_source': 'held_out' in str(m.get('metrics_source') or '').lower(),
        'held_out_eval': m.get('held_out_eval') is True,
        'prereg_bands_present': bool(m.get('prereg_bands')),
        'run_mode==full': m.get('run_mode') == 'full',
        'no_false_positive': m.get('any_false_positive') is False,
        'unverifiable==0': m.get('path_edges_unverifiable') == 0,
        'gate0_pass': (m.get('gate0_self_check') or {}).get('pass') is True,
        'envelope_5_benchmarks': len(env) == 5,
        'envelope_all_FP0': all(v.get('false_positives') == 0 for v in env.values()),
    }
    ok = all(checks.values())
    print('VET-GUARD:', {k: v for k, v in checks.items()})
    return ok


def build_atom(m: dict, canon: Path) -> Atom:
    env = m.get('envelope') or {}
    cliff = [k for k, v in env.items() if v.get('band') == 'HARD_FAIL']
    pass_mid = [k for k, v in env.items() if v.get('band') in ('HARD_PASS', 'MIDDLE_BAND')]
    cert_value = (
        "B-alpha BROAD (ARC-1 T2): the multi-benchmark composed-reasoning ENVELOPE over the materialized typed-edge "
        "backbone, each benchmark vs its own INDEPENDENT nltk gold (per-benchmark discrimination). Envelope = "
        f"0 HARD_PASS / {sum(1 for v in env.values() if v['band']=='MIDDLE_BAND')} MIDDLE / {len(cliff)} HARD_FAIL. "
        f"DEPTH-CLIFF: composed reasoning works at 2-hop (MIDDLE) but CLIFFS at 3+ hops -- HARD_FAIL benchmarks: "
        f"{', '.join(cliff)} (the walker correctly REFUSES out-of-5k-intermediate chains; no hallucination). "
        "RELATION-GENERALITY: HYPERNYM + PART_OF both MIDDLE at 2-hop; PART_OF more depth-robust. 100% edge-verifiable "
        "(5th gate) + 0 FP across all benchmarks."
    )
    scope = (
        "DISCRIMINATING multi-benchmark composed-reasoning ENVELOPE vs independent per-benchmark nltk gold. Characterizes "
        f"WHERE composed reasoning works (2-hop MIDDLE) vs CLIFFS (3-4 hop HARD_FAIL: {', '.join(cliff)}). Per-benchmark "
        "HARD_FAIL = HONEST cliff FINDING (not a failure to hide). NOT general reasoning. ARC-1 T2 (BROAD). Denser/deeper "
        "edge-materialization is the recall lever (future ARC). measured-bounds not fundamental."
    )
    metadata = {
        'record_class': 'experiment_record',
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'verdict': 'MIDDLE_BAND',
        'provenance_quality': 'CERT_CHAIN_GRADE',
        'relevance_tier': 'SUPPORTING',
        'run_mode': 'full', 'n_seeds': 1,
        'metrics_source': m.get('metrics_source'),
        'held_out_eval': True, 'prereg_bands': m.get('prereg_bands'),
        'metrics_path': str(canon),
        'experiment_path': 'experiments/exp_substrate_b_alpha_broad_envelope_cpu_v1.py',
        'cell_commit': m.get('cell_commit'),
        'envelope': env,
        'key_metrics': {
            'n_benchmarks': m.get('n_benchmarks'), 'n_hard_pass': m.get('n_hard_pass'),
            'n_middle': m.get('n_middle'), 'n_hard_fail': m.get('n_hard_fail'),
            'path_edges_total': m.get('path_edges_total'), 'path_edges_unverifiable': m.get('path_edges_unverifiable'),
            'any_false_positive': m.get('any_false_positive'),
            **{f'recall_{k}': v['recall'] for k, v in env.items()},
            **{f'band_{k}': v['band'] for k, v in env.items()},
        },
        'cliff_benchmarks_HARD_FAIL': cliff,             # NAMED first-class (queryable cliff-finding)
        'working_benchmarks': pass_mid,
        'cert_value': cert_value, 'claim_scope': scope, 'honest_scope': m.get('honest_scope'),
        'min_cert_along_path': m.get('min_cert_along_path'),
        'depth_cliff_finding': 'HYPERNYM composed reasoning cliffs at 3+ hops (HYP-3 0.368, HYP-4 0.200 HARD_FAIL); '
                               'PART_OF depth-robust (2-3 hop MIDDLE). Denser/deeper ingest = the lever.',
        'fifth_self_cert_gate': 'path_provenance_self_check (aggregate) + path_provenance_gate (a7497620)',
        'composed_reasoning_arc': 'ARC-1 T2 milestone (BROAD); multi-benchmark generalization of B-alpha NARROW',
        'bears_on': 'B-alpha NARROW (HYPERNYM 2-hop single-benchmark predecessor); A1 control; 5th gate; TRACK-3 edge-mat',
        'strengthens_cert': [NARROW_QID, A1_QID],
        'gold_validity_vet': 'Skunkworks independent nltk over all 1500 (v1) + HYP-3 full-gold re-VET (3326/3326 true 3-hop); v2 sha a29f649e',
        'schema_vet_by': 'skunkworks', 'validity_vet_by': 'skunkworks', 'verdict_vet_by': 'skunkworks', 'vet_date': '2026-06-18',
        'vet_note': 'SCHEMA-VET PASS + validity-VET PASS (1500 + HYP-3 full re-VET) + verdict-VET + tier=CERT_CHAIN_GRADE MIDDLE_BAND envelope (Q-b i one atom)',
        'eleventh_rule_clean': True, 'deterministic_no_llm': True,
        'source': 'b_alpha_broad_envelope_cert_chain_grade_skunkworks_tier_ruling',
    }
    return Atom(
        id=ATOM_ID,
        name='CERT (CERT_CHAIN_GRADE MIDDLE_BAND): composed-reasoning ENVELOPE over the typed-edge backbone -- 2-hop works, 3+ hop cliffs (B-alpha BROAD; ARC-1 T2)',
        description='CERT_CHAIN_GRADE MIDDLE_BAND envelope (ARC-1 T2 milestone). ' + cert_value + ' SCOPE: ' + scope,
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
    ps.add_atom(atom, source='b_alpha_broad_envelope', note='Skunkworks tier ruling CERT_CHAIN_GRADE MIDDLE_BAND envelope; CERT 570->571')
    edges_added = 0
    for tgt in (NARROW_QID, A1_QID):
        if ps.get_atom(tgt) is not None:
            try:
                ps.add_relation(f'math::{ATOM_ID}', RelationType.STRENGTHENS, tgt,
                                source='b_alpha_broad_envelope', note='BROAD generalizes/strengthens predecessor')
                edges_added += 1
            except Exception as e:
                print(f'WARN: STRENGTHENS->{tgt} not added ({str(e)[:60]})')

    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps2); post_mod = module_liveness_ok(); post_cert = cert_count(ps2)
    rb = ps2.get_atom(f'math::{ATOM_ID}')
    rb_ok = (rb is not None and rb.kind == AtomKind.EXPERIMENT_RECORD and rb.algebra is None
             and rb.metadata.get('provenance_quality') == 'CERT_CHAIN_GRADE' and rb.metadata.get('verdict') == 'MIDDLE_BAND')
    gate_ok = post_axiom == 206 and post_mod and post_cert == pre_cert + 1 and rb_ok
    print(f'POST: axiom_term={post_axiom}  cap_pres={post_mod}  CERT={post_cert} (was {pre_cert})  read-back_ok={rb_ok}  strengthens_edges={edges_added}')
    if not gate_ok:
        print('HARD_FAIL: gate/read-back failed (CERT must be exactly pre+1). Reverting.')
        ps2.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail'); return 2
    print('=' * 72)
    print(f'B-alpha BROAD envelope landed: math::{ATOM_ID}  CERT {post_cert} (570->571)  axiom_term 206  cap_pres 6/6')
    print(f'  ARC-1 T2 milestone: composed-reasoning ENVELOPE (depth-cliff at 3+ hops = honest finding).')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
