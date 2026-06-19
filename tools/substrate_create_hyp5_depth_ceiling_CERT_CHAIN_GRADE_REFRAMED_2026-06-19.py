"""Scoped creation: HYP-5 depth-ceiling as CERT_CHAIN_GRADE (REFRAMED per Skunkworks tier-call 2026-06-19; CERT 573->574).

Skunkworks SCHEMA-VET + verdict-VET = PASS (reproduced exact). RATIFIED the Exp-Dev honest self-catch: the
"coverage-vs-algorithmic" gate is DEGENERATE (algorithmic-misses=0 BY CONSTRUCTION; the BFS walker cannot miss a persisted
path -> that category cannot be populated). So that framing is NOT atomized. TIER = CERT_CHAIN_GRADE on the GENUINE
discriminating content (walker-INDEPENDENT, could-have-come-out-otherwise): (1) the recall curve-SHAPE (extends/plateau
~0.84, NOT a crash) + (2) the coverage_ceiling(fundamental, growing 64->230)-vs-edge_gap(fixable, tiny+constant ~21) split.
The verdict is REFRAMED accordingly + the degenerate-gate is FLAGGED verbatim in the atom.

refuse-until-VET-PASS guard. CERT==pre+1. revert-on-fail. ASCII. No LLM. RUN only on Skunkworks tier-call (no-self-certify).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_hyp5_depth_ceiling_cpu_v1'
PHASEA2_QID = 'math::T3/EXP_t3_phaseA2_2level_recovery_cpu_v1'           # the depth-cliff lever this EXTENDS to depth-5
M1_QID = 'math::T3/EXP_hypernym_heldout_falsifiable_cpu_v1'             # the coverage-not-reasoning bound, now depth-extended
DEFAULT_CANON = Path('data/exp_hyp5_depth_ceiling_v1/metrics.json')

REFRAME = (
    "The coverage-completion lever EXTENDS to depth-5 (recall plateaus ~0.84, K2..K5 = 0.944/0.891/0.863/0.845, NO crash). "
    "The depth-ceiling is the INTRINSIC 5k-CORPUS-BOUNDARY (coverage_ceiling fundamental-dominated, GROWING 64->230 with "
    "depth = more hops exit the 5k), NOT a fixable in-5k completion-gap (edge_gap tiny+CONSTANT ~21 = the in-5k backbone is "
    "near-complete). EXTENDS the coverage-completion-not-reasoning bound (Item-1/M1) to DEEP hops: the bound holds at depth-5, "
    "and the limit is corpus-coverage (the 5k boundary), NOT an algorithmic depth-limit."
)
DEGENERATE_GATE_CAVEAT = (
    "The coverage-VS-algorithmic gate is DEGENERATE (algorithmic-misses=0 BY CONSTRUCTION: the BFS walker cannot miss a "
    "persisted path -> the algorithmic category cannot be populated by this design). So 'not algorithmic' is NOT an empirical "
    "discriminator here -- it is structurally guaranteed. The cert-bearing discriminating content is (1) the recall curve-shape "
    "(extends/plateau, not crash) + (2) the fundamental(coverage_ceiling, growing)-vs-fixable(edge_gap, constant-tiny) split -- "
    "both walker-INDEPENDENT (nltk-in5k-measured) + could-have-come-out-otherwise. A 2nd independent walker would be needed to "
    "make 'algorithmic' empirically testable; this cell does NOT test it."
)
SCOPE = (
    "HYPERNYM / WordNet / deterministic-BFS / in5k / depth-2..5. NOT general reasoning. The cert-bearing claims are the "
    "depth-EXTENT (lever extends to depth-5) + the 5k-CORPUS-BOUNDARY ceiling (fundamental, not fixable-completion-gap) -- "
    "NOT 'coverage-vs-algorithmic discriminated' (that sub-gate is degenerate; see the degenerate_gate_caveat)."
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
    attr = m.get('attribution') or {}
    checks = {
        'recall_curve_present': bool(m.get('recall_curve')),
        'no_crash_extends': m.get('no_crash_extends') is True,
        'declining_or_plateau': m.get('declining_or_plateau') is True,
        'fp_total==0': m.get('fp_total') == 0,
        'attribution_sums': m.get('total_miss') == (m.get('total_coverage_miss', 0) + m.get('total_algorithmic_miss', 0)),
        'fundamental_grows': (attr.get('K5', {}).get('coverage_ceiling', 0) > attr.get('K2', {}).get('coverage_ceiling', 0)),
        'run_mode==full': m.get('run_mode') == 'full',
    }
    ok = all(checks.values())
    print('VET-GUARD:', checks)
    return ok


def build_atom(m: dict, canon: Path) -> Atom:
    cert_value = ("HYP-5 depth-ceiling: a NON-coextensive measurement + break-point attribution probe (no completion added). "
                  + REFRAME)
    metadata = {
        'record_class': 'experiment_record', 'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'verdict': 'DISCRIMINATING_DEPTH_EXTENT',   # REFRAMED (NOT the cell's degenerate 'coverage-vs-algorithmic' label)
        'provenance_quality': 'CERT_CHAIN_GRADE', 'relevance_tier': 'SUPPORTING',
        'run_mode': 'full', 'n_seeds': 1, 'metrics_source': m.get('metrics_source'),
        'held_out_eval': True, 'prereg_bands': m.get('prereg_bands'),
        'metrics_path': str(canon), 'experiment_path': 'experiments/exp_substrate_hyp5_depth_ceiling_cpu_v1.py',
        'design': m.get('design'), 'seed': m.get('seed'), 'sample_n_synsets': m.get('sample_n_synsets'), 'device': m.get('device'),
        'key_metrics': {
            'recall_curve': m.get('recall_curve'), 'attribution': m.get('attribution'),
            'total_miss': m.get('total_miss'), 'total_coverage_miss': m.get('total_coverage_miss'),
            'total_algorithmic_miss': m.get('total_algorithmic_miss'), 'fp_total': m.get('fp_total'),
            'fundamental_coverage_ceiling_K2_to_K5': [m['attribution'][f'K{k}']['coverage_ceiling'] for k in (2, 3, 4, 5)],
            'fixable_edge_gap_K2_to_K5': [m['attribution'][f'K{k}']['edge_gap'] for k in (2, 3, 4, 5)],
        },
        'cert_value': cert_value, 'reframed_verdict': REFRAME, 'degenerate_gate_caveat': DEGENERATE_GATE_CAVEAT,
        'claim_scope': SCOPE, 'honest_scope': SCOPE,
        'depth_extends_bound': 'EXTENDS the coverage-completion-not-reasoning bound (Item-1 PART_OF + M1 HYPERNYM) to depth-5: the bound holds at deep hops; the depth-ceiling is the intrinsic 5k-corpus-boundary (fundamental, growing), NOT algorithmic + NOT a fixable in-5k completion-gap (in-5k near-complete).',
        'min_cert_along_path': 'WordNet HYPERNYM edges ontology-INGESTED; the recall-curve + the nltk-in5k-measured fundamental/fixable split are the cert-bearing measurements (walker-independent; non-coextensive).',
        'bears_on': 'Phase-A2 2-level recovery (the depth-cliff lever, EXTENDED to depth-5); Item-1/M1 coverage-not-reasoning bound (depth-extended); the universal-lever DEPTH extent + the 5k-corpus-boundary ceiling',
        'extends_cert': [PHASEA2_QID, M1_QID], 'strengthens_cert': [PHASEA2_QID],
        'reproduced_by': 'skunkworks (independent re-run; exact recall curve + attribution)',
        'schema_vet_by': 'skunkworks', 'verdict_vet_by': 'skunkworks', 'tier_call_by': 'skunkworks', 'vet_date': '2026-06-19',
        'vet_note': 'Skunkworks tier-call CERT_CHAIN_GRADE REFRAMED: degenerate coverage-vs-algorithmic gate FLAGGED (algorithmic=0 by construction); cert-bearing content = curve-shape (extends/plateau) + fundamental/fixable split (walker-independent); NO 2nd-walker required; verdict reframed to depth-extent + 5k-boundary-fundamental.',
        'eleventh_rule_clean': True, 'deterministic_no_llm': True,
        'source': 'hyp5_depth_ceiling_cert_chain_grade_reframed_skunkworks_tier_call',
    }
    return Atom(
        id=ATOM_ID,
        name='CERT (CERT_CHAIN_GRADE, REFRAMED): the coverage-lever EXTENDS to depth-5 (recall plateau ~0.84); the ceiling is the intrinsic 5k-corpus-boundary (fundamental, not fixable); coverage-vs-algorithmic sub-gate degenerate-FLAGGED',
        description='CERT_CHAIN_GRADE (reframed; non-coextensive depth-ceiling probe). ' + cert_value + ' DEGENERATE-GATE CAVEAT: ' + DEGENERATE_GATE_CAVEAT,
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
    ps.add_atom(atom, source='hyp5_depth_ceiling', note='Skunkworks tier-call CERT_CHAIN_GRADE REFRAMED; CERT 573->574; depth-extent + 5k-boundary; degenerate-gate flagged')
    edges = 0
    for tgt in (PHASEA2_QID, M1_QID):
        if ps.get_atom(tgt) is not None:
            try:
                ps.add_relation(f'math::{ATOM_ID}', RelationType.STRENGTHENS, tgt,
                                source='hyp5_depth_ceiling', note='extends the depth-cliff lever / coverage-not-reasoning bound to depth-5')
                edges += 1
            except Exception as e:
                print(f'WARN: STRENGTHENS->{tgt} not added ({str(e)[:60]})')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps2); post_mod = module_liveness_ok(); post_cert = cert_count(ps2)
    rb = ps2.get_atom(f'math::{ATOM_ID}')
    rb_ok = (rb is not None and rb.kind == AtomKind.EXPERIMENT_RECORD and rb.algebra is None
             and rb.metadata.get('provenance_quality') == 'CERT_CHAIN_GRADE'
             and 'degenerate_gate_caveat' in rb.metadata)
    gate_ok = post_axiom == 206 and post_mod and post_cert == pre_cert + 1 and rb_ok
    print(f'POST: axiom_term={post_axiom}  cap_pres={post_mod}  CERT={post_cert} (was {pre_cert})  read-back_ok={rb_ok}  strengthens_edges={edges}')
    if not gate_ok:
        print('HARD_FAIL: gate/read-back failed. Reverting.')
        ps2.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail'); return 2
    print('=' * 72)
    print(f'HYP-5 depth-ceiling landed: math::{ATOM_ID}  CERT {post_cert} (573->574)  axiom 206  cap_pres 6/6  (REFRAMED; degenerate-gate flagged)')
    print('  Lever EXTENDS to depth-5; ceiling = intrinsic 5k-corpus-boundary (fundamental, not fixable). Bound depth-extended.')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
