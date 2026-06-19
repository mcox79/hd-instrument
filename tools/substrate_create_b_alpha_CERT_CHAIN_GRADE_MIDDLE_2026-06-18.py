"""Scoped creation: B-alpha NARROW SCALE-UP as CERT_CHAIN_GRADE MIDDLE_BAND (Skunkworks SCHEMA-VET + validity-VET +
verdict-VET CONFIRM + tier ruling GO, 2026-06-18). The FIRST cert-grade DISCRIMINATING composed-reasoning experiment
(ARC-1 foundation-stone).

UNLIKE A1 (MEASURED_MECHANISM, 1.0/1.0 by-construction control), B-alpha DISCRIMINATES against an INDEPENDENT nltk
2-hop-hypernym gold (validity-VET PASS): recall 0.6067 MIDDLE (the walker attests 60.7% of the true closure; the rest
route through out-of-5k intermediates -> correctly REFUSED, no hallucination), 100% edge-verifiable (5th gate sound),
0 FP. CERT (rigor: full + measured + held-out + provenance-sound + gate0) is orthogonal to MIDDLE (verdict: honest
60.7% backbone coverage). CERT 569 -> 570.

Reads the CANONICAL dispatched _held_out metrics (data/exp_b_alpha_2hop_hypernym_qa_cpu_v1). One DIRECT atom write
(mirrors substrate_create_b_delta_v2/a1) -> exactly 1 atom, sidesteps the bulk-atomizer-glob-3-dirs dup risk (2 stale
dirs already removed). refuse-until-VET-PASS guard. STRENGTHENS edge -> A1 (its discriminating scale-up). axiom_term/
cap_pres gated; non-retroactive; CERT == pre + 1 enforced. ASCII-only. No LLM. Laptop-safe.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_b_alpha_2hop_hypernym_qa_cpu_v1'
A1_QID = 'math::T3/EXP_a1_multihop_provenance_cpu_v1'   # STRENGTHENS target (B-alpha = A1's discriminating scale-up)
CANON = Path('data/exp_b_alpha_2hop_hypernym_qa_cpu_v1/metrics.json')

CERT_VALUE = (
    "B-alpha is the FIRST cert-grade DISCRIMINATING composed-reasoning experiment: deterministic 2-hop-hypernym QA over "
    "the materialized WordNet HYPERNYM backbone, scored against an INDEPENDENT nltk gold (true 2-hop closure incl. "
    "out-of-5k intermediates). recall=0.6067 MIDDLE genuinely DISCRIMINATES (vs A1's 1.0/1.0 by-construction control): "
    "the walker attests 60.7% of the true closure via persisted paths and REFUSES the rest (no hallucination). 100% "
    "edge-verifiable (the 5th multi-hop-provenance gate firing: every returned hop a persisted Store tuple) + 0 FP "
    "(safety by construction: persisted edges subset true WordNet)."
)
SCOPE = (
    "DISCRIMINATING provenance-verified 2-hop-hypernym PATH-FINDING over the materialized within-5k HYPERNYM backbone vs "
    "an independent nltk gold; NOT general reasoning / NOT 'the substrate reasons'. ARC-1 foundation-stone (narrow, "
    "honest-scoped; 89%-mechanism-core framing). Denser edge-materialization (ingest out-of-5k intermediates) is the "
    "recall lever (next ARC) -- NOT a deficiency of the mechanism (which is provably sound). measured-bounds not "
    "fundamental (deeper hops / more rel-types / denser ingest untested)."
)
MIN_CERT = ("ontology-INGESTED WordNet-edge tier. The PATH is provenance-CERT (every edge a persisted Store tuple); the "
            "RESULT (recall + 100%-edge-verifiable + 0-FP) is the cert-grade EXPERIMENT; per-answer CLAIM-cert = the "
            "weakest edge tier = ontology-ingested (HYPERNYM from WordNet, not experiment-cert).")


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
    """refuse-until-VET-PASS: the canonical metrics MUST match the VET'd dispatched result, else HALT (no atomize)."""
    checks = {
        'verdict==MIDDLE_BAND': m.get('verdict') == 'MIDDLE_BAND',
        'held_out_source': 'held_out' in str(m.get('metrics_source') or '').lower(),
        'held_out_eval': m.get('held_out_eval') is True,
        'prereg_bands_present': bool(m.get('prereg_bands')),
        'run_mode==full': m.get('run_mode') == 'full',
        'FP==0': m.get('false_positives') == 0,
        'unverifiable==0': m.get('path_edges_unverifiable') == 0,
        'recall_in_MIDDLE': isinstance(m.get('recall_answer_found'), (int, float)) and 0.40 <= m['recall_answer_found'] < 0.70,
        'gate0_pass': (m.get('gate0_self_check') or {}).get('pass') is True,
    }
    ok = all(checks.values())
    print('VET-GUARD:', {k: v for k, v in checks.items()})
    return ok


def build_atom(m: dict) -> Atom:
    metadata = {
        'record_class': 'experiment_record',
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'verdict': 'MIDDLE_BAND',
        'provenance_quality': 'CERT_CHAIN_GRADE',     # Skunkworks tier ruling: first cert-grade DISCRIMINATING composed-reasoning
        'relevance_tier': 'SUPPORTING',
        'run_mode': 'full',
        'n_seeds': 1,                                  # held-out deterministic eval -> n_seeds-independent (Skunkworks)
        'metrics_source': m.get('metrics_source'),     # measured_graph_bfs_held_out (the cert-marker)
        'held_out_eval': True,
        'prereg_bands': m.get('prereg_bands'),
        'metrics_path': str(CANON),
        'experiment_path': 'experiments/exp_substrate_b_alpha_2hop_hypernym_qa_cpu_v1.py',
        'cell_commit': m.get('cell_commit') or '0a43a8d5',
        'key_metrics': {
            'recall_answer_found': m.get('recall_answer_found'), 'refuse_rate': m.get('refuse_rate'),
            'false_positives': m.get('false_positives'), 'path_edges_total': m.get('path_edges_total'),
            'path_edges_unverifiable': m.get('path_edges_unverifiable'), 'edge_verifiable_100pct': True,
            'n_positives': m.get('n_positives'), 'n_negatives': m.get('n_negatives'), 'n_found': m.get('n_found'),
            'rel_type': m.get('rel_type'), 'max_depth': m.get('max_depth'),
            'discriminating': 'recall 0.6067 MIDDLE vs INDEPENDENT nltk gold (not A1 by-construction 1.0/1.0)',
        },
        'cert_value': CERT_VALUE,
        'claim_scope': SCOPE,
        'min_cert_along_path': MIN_CERT,
        'honest_scope': m.get('honest_scope'),
        'fifth_self_cert_gate': 'path_provenance_self_check (producer) + path_provenance_gate (consumer a7497620); '
                                'B-alpha is the DISCRIMINATING realization (A1 was the by-construction control)',
        'composed_reasoning_arc': 'ARC-1 foundation-stone REALIZED (USER-ratified 2026-06-18); first cert-grade discriminating composed-reasoning',
        'bears_on': 'A1 multi-hop-provenance (its discriminating scale-up); 5th self-cert gate (a7497620); '
                    'TRACK-3 HYPERNYM edge-materialization (2884 edges); gold sha 9c9b71bf (validity-VET PASS)',
        'strengthens_cert': [A1_QID],                  # STRENGTHENS edge target (first-class rel_type)
        'gold_validity_vet': 'Skunkworks independent nltk recompute over all 600 (300/300 pos true 2-hop, 300/300 neg not-2hop+unreachable); sha 9c9b71bf',
        'schema_vet_by': 'skunkworks', 'validity_vet_by': 'skunkworks', 'verdict_vet_by': 'skunkworks', 'vet_date': '2026-06-18',
        'vet_note': 'SCHEMA-VET PASS (11th-clean deterministic-BFS + 5th-gate wired + discrimination bites) + validity-VET PASS '
                    '(gold correct, sha 9c9b71bf) + verdict-VET CONFIRM (remote==local, no Store drift) + tier=CERT_CHAIN_GRADE MIDDLE_BAND',
        'eleventh_rule_clean': True, 'deterministic_no_llm': True,
        'source': 'b_alpha_2hop_hypernym_qa_cert_chain_grade_skunkworks_tier_ruling',
    }
    return Atom(
        id=ATOM_ID,
        name='CERT (CERT_CHAIN_GRADE MIDDLE_BAND): discriminating 2-hop-hypernym QA over the WordNet backbone vs independent nltk gold (B-alpha; ARC-1 foundation-stone)',
        description='CERT_CHAIN_GRADE MIDDLE_BAND (first cert-grade DISCRIMINATING composed-reasoning). ' + CERT_VALUE + ' SCOPE: ' + SCOPE,
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata=metadata,
    )


def main() -> int:
    if not CANON.exists():
        print(f'HALT: canonical metrics not found at {CANON}'); return 1
    m = json.loads(CANON.read_text(encoding='utf-8'))
    if not vet_guard(m):
        print('HALT: VET-GUARD FAILED (canonical metrics do not match the VET\'d dispatched result). NO atomize.'); return 1

    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps); pre_mod = module_liveness_ok(); pre_cert = cert_count(ps)
    print(f'PRE: axiom_term={pre_axiom}  cap_pres={pre_mod}  CERT={pre_cert}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.'); return 1
    if ps.get_atom(f'math::{ATOM_ID}') is not None:
        print(f'SKIP (idempotent): {ATOM_ID}'); return 0
    if ps.get_atom(A1_QID) is None:
        print(f'HALT: STRENGTHENS target {A1_QID} not in store (0-phantom guard).'); return 1

    atom = build_atom(m)
    ps.add_atom(atom, source='b_alpha_cert_chain_grade', note='Skunkworks tier ruling CERT_CHAIN_GRADE MIDDLE_BAND; CERT 569->570')
    # STRENGTHENS edge: B-alpha -> A1 (the discriminating scale-up strengthens the A1 mechanism-control)
    try:
        ps.add_relation(f'math::{ATOM_ID}', RelationType.STRENGTHENS, A1_QID,
                        source='b_alpha_cert_chain_grade', note='B-alpha discriminating scale-up STRENGTHENS A1 control')
        edge_added = True
    except Exception as e:
        edge_added = False
        print(f'WARN: STRENGTHENS edge not added ({str(e)[:80]}); strengthens_cert metadata still records the link.')

    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps2); post_mod = module_liveness_ok(); post_cert = cert_count(ps2)
    rb = ps2.get_atom(f'math::{ATOM_ID}')
    rb_ok = (rb is not None and rb.kind == AtomKind.EXPERIMENT_RECORD and rb.algebra is None
             and rb.metadata.get('provenance_quality') == 'CERT_CHAIN_GRADE' and rb.metadata.get('verdict') == 'MIDDLE_BAND')
    gate_ok = post_axiom == 206 and post_mod and post_cert == pre_cert + 1 and rb_ok   # CERT += 1 (no more, no less)
    print(f'POST: axiom_term={post_axiom}  cap_pres={post_mod}  CERT={post_cert} (was {pre_cert})  '
          f'read-back_ok={rb_ok}  strengthens_edge={edge_added}')
    if not gate_ok:
        print('HARD_FAIL: gate/read-back failed (CERT must be exactly pre+1). Reverting.')
        ps2.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail'); return 2
    print('=' * 72)
    print(f'B-alpha CERT_CHAIN_GRADE MIDDLE_BAND landed: math::{ATOM_ID}  CERT {post_cert} (569->570)  axiom_term 206  cap_pres 6/6')
    print('  FIRST cert-grade DISCRIMINATING composed-reasoning experiment (ARC-1 foundation-stone REALIZED).')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
