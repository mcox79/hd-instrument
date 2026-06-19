"""Scoped creation: A2 v6 C-deferred (GROWN corpus) as CERT_CHAIN_GRADE ALREADY_SEPARATES (Skunkworks GRANTED; CERT 574->575).

Closes the A-now/C-deferred cert-chain at the scientifically-complete tier. Skunkworks verdict-VET GRANTED CERT_CHAIN_GRADE
(AUROC recomputed-from-72-raw-rows = 0.9628, matches headline; non-degenerate; run_mode full/measured_bge_gpu; A2-set-validity
PASS; corpus git-pinned cell_commit 84cd0840 clean grown checkout). The recheck-requirement was RECONCILED by CHAIN-ROBUSTNESS:
A-now (41330 pre-ingest, AUROC 0.965) + C-deferred (43905 grown, 0.9628) = the SAME finding on TWO independent corpus states
(different caches) -> a cache<->corpus mismatch would NOT reproduce across both -> stronger than a single hash-match; the
separate semantic-recheck is moot/folded for cert.

Finding (corpus-ROBUST): the untuned substrate ALREADY separates gap/in-cov by raw bge-confidence (AUROC ~0.96) on BOTH the
pre-ingest AND grown corpus -> B-beta: LoRA Stage-2 no rank-headroom (near-gap-precision UNTESTED per the A-now Layer-4
framing); a calibrated threshold suffices.

refuse-until-VET-PASS guard. CERT==pre+1. revert-on-fail. STRENGTHENS the A-now A2 v6 atom (chain). ASCII. No LLM.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType

ATOM_ID = 'T3/EXP_a2_decisive_test_untuned_auroc_grown_cpu_v1'
ANOW_QID = 'math::T3/EXP_a2_decisive_test_untuned_auroc_gpu_v1'   # the A-now (pre-ingest) A2 v6; this grown run closes the chain
DEFAULT_CANON = Path('data/exp_a2_decisive_test_untuned_auroc_grown_v1_metrics.json')

CERT_VALUE = (
    "A2 v6 C-deferred on the CLEAN GROWN 43905 corpus (cell_commit 84cd0840): untuned refuse-gate AUROC=0.9628 "
    "(near_gap 0.9338, far_gap 0.9951); ALREADY_SEPARATES. CLOSES the A-now/C-deferred cert-chain CORPUS-ROBUST: A-now "
    "(41330 pre-ingest, hash ffbbeb2c) AUROC 0.965 + C-deferred (43905 grown, commit 84cd0840) AUROC 0.9628 = the SAME "
    "finding on TWO independent corpus states / caches. The untuned substrate ALREADY separates gap vs in-coverage by raw "
    "bge-confidence on BOTH -> the scientifically-complete measurement."
)
SCOPE = (
    "untuned refuse-gate AUROC (raw bge-confidence rank-separation) on the GROWN 43905 corpus (the B-beta-decision corpus). "
    "CORPUS-ROBUST (pre-ingest 0.965 + grown 0.9628). B-beta: LoRA Stage-2 has NO rank-headroom; the near-gap-precision "
    "headroom is UNTESTED (not no-headroom NOR needs-LoRA -- the A-now Layer-4 framing); a calibrated threshold suffices. "
    "NOT general reasoning. Honest caveats carry from the A-now atom."
)
CHAIN_ROBUSTNESS = (
    "CHAIN-ROBUSTNESS is the load-bearing provenance (Skunkworks): the same ALREADY_SEPARATES finding reproduced on the "
    "pre-ingest (41330/ffbbeb2c) AND the grown (43905/84cd0840) corpus, built from DIFFERENT caches -> a cache<->corpus "
    "mismatch would not reproduce across both -> the separate semantic-recheck is moot/folded for cert (the +2562 FrameNet+"
    "WordNet ingests are linguistically orthogonal to the CS-algorithm gap-set; A2-set-validity independently VET'd 2026-06-18)."
)
HARDENING = ("Cell-hardening follow-on (NOT cert-blocking; Skunkworks): substrate_id_hash is None in the metrics top-level; "
             "the corpus-provenance is anchored by cell_commit 84cd0840 + the chain-robustness instead. Surface "
             "substrate_id_hash (cache<->corpus correspondence) in the NEXT A2-family cell for full self-attesting provenance.")


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
    g0 = m.get('gate0_self_check') or {}
    disc = m.get('discrimination_self_check') or {}
    checks = {
        'verdict==ALREADY_SEPARATES': m.get('verdict') == 'ALREADY_SEPARATES',
        'auroc>=0.70': (m.get('untuned_auroc') or 0) >= 0.70,
        'run_mode==full': m.get('run_mode') == 'full',
        'gate0_pass': g0.get('pass') is True,
        'discriminates': disc.get('discriminates') is True,
        'n_gap==38': m.get('n_gap') == 38,
        'n_in_cov==34': m.get('n_in_cov') == 34,
        'measured_bge': 'measured_bge' in str(m.get('metrics_source') or '').lower(),
    }
    ok = all(checks.values())
    print('VET-GUARD:', checks)
    return ok


def build_atom(m: dict, canon: Path) -> Atom:
    metadata = {
        'record_class': 'experiment_record', 'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'verdict': 'ALREADY_SEPARATES', 'provenance_quality': 'CERT_CHAIN_GRADE', 'relevance_tier': 'SUPPORTING',
        'run_mode': 'full', 'n_seeds': m.get('n_seeds', 1), 'metrics_source': m.get('metrics_source'),
        'held_out_eval': True, 'prereg_bands': m.get('bands'),
        'metrics_path': str(canon), 'experiment_path': 'experiments/exp_substrate_a2_decisive_test_untuned_auroc_gpu_v1.py',
        'cell_commit': m.get('cell_commit'), 'corpus_scope': 'grown_43905_commit_84cd0840',
        'key_metrics': {
            'untuned_auroc': m.get('untuned_auroc'), 'near_gap_auroc': m.get('near_gap_auroc'),
            'far_gap_auroc': m.get('far_gap_auroc'), 'n_gap': m.get('n_gap'), 'n_in_cov': m.get('n_in_cov'),
            'n_cells': m.get('n_cells'),
            'chain': {'a_now_41330_ffbbeb2c': 0.9652, 'c_deferred_43905_84cd0840': m.get('untuned_auroc')},
        },
        'cert_value': CERT_VALUE, 'claim_scope': SCOPE, 'honest_scope': SCOPE,
        'chain_robustness': CHAIN_ROBUSTNESS, 'hardening_follow_on': HARDENING,
        'b_beta_gate': 'CORPUS-ROBUST no LoRA rank-headroom (0.965 pre-ingest + 0.9628 grown); near-gap-precision headroom UNTESTED (Layer-4); calibrated threshold suffices. A-now/C-deferred chain scientifically complete.',
        'coincidental_mention_caveat': m.get('coincidental_mention_caveat'),
        'min_cert_along_path': 'bge embeddings (measured) + the validity-VET\'d 72-item gap/in-cov set; AUROC recomputed-from-raw-rows = 0.9628 (Skunkworks data-layer verify); grown-corpus git-pinned (84cd0840).',
        'bears_on': 'the A-now A2 v6 (pre-ingest; this grown run closes the chain corpus-robust); the B-beta LoRA gate; the refuse-gate; the A2 semantic-recheck (folded via chain-robustness)',
        'closes_chain': 'A-now/C-deferred A2-v6 cert-chain (pre-ingest + grown; corpus-robust ALREADY_SEPARATES)',
        'strengthens_cert': [ANOW_QID],
        'schema_vet_by': 'skunkworks', 'validity_vet_by': 'skunkworks', 'verdict_vet_by': 'skunkworks', 'vet_date': '2026-06-19',
        'vet_note': 'Skunkworks verdict-VET GRANTED CERT_CHAIN_GRADE (CERT 574->575): AUROC recomputed-from-raw-rows 0.9628 matches; non-degenerate; full/measured_bge_gpu; A2-set-validity PASS; git-pinned 84cd0840; chain-robust; recheck folded via chain-robustness; substrate_id_hash hardening (next A2-family cell).',
        'eleventh_rule_clean': True, 'deterministic_no_llm': True,
        'source': 'a2v6_c_deferred_grown_corpus_cert_chain_grade_skunkworks_granted',
    }
    return Atom(
        id=ATOM_ID,
        name='CERT (CERT_CHAIN_GRADE ALREADY_SEPARATES): A2 v6 on the GROWN 43905 corpus AUROC 0.9628 -- CLOSES the A-now/C-deferred chain (corpus-robust; no LoRA headroom)',
        description='CERT_CHAIN_GRADE ALREADY_SEPARATES (grown 43905; closes the chain corpus-robust). ' + CERT_VALUE + ' SCOPE: ' + SCOPE + ' PROVENANCE: ' + CHAIN_ROBUSTNESS,
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
    ps.add_atom(atom, source='a2v6_grown_c_deferred', note='Skunkworks GRANTED CERT_CHAIN_GRADE; CERT 574->575; closes A-now/C-deferred chain corpus-robust')
    edge_added = False
    if ps.get_atom(ANOW_QID) is not None:
        try:
            ps.add_relation(f'math::{ATOM_ID}', RelationType.STRENGTHENS, ANOW_QID,
                            source='a2v6_grown_c_deferred', note='grown-corpus confirmation closes the chain corpus-robust')
            edge_added = True
        except Exception as e:
            print(f'WARN: STRENGTHENS edge not added ({str(e)[:60]})')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_axiom = axiom_term_count(ps2); post_mod = module_liveness_ok(); post_cert = cert_count(ps2)
    rb = ps2.get_atom(f'math::{ATOM_ID}')
    rb_ok = (rb is not None and rb.kind == AtomKind.EXPERIMENT_RECORD and rb.algebra is None
             and rb.metadata.get('provenance_quality') == 'CERT_CHAIN_GRADE' and rb.metadata.get('verdict') == 'ALREADY_SEPARATES')
    gate_ok = post_axiom == 206 and post_mod and post_cert == pre_cert + 1 and rb_ok
    print(f'POST: axiom_term={post_axiom}  cap_pres={post_mod}  CERT={post_cert} (was {pre_cert})  read-back_ok={rb_ok}  strengthens_edge={edge_added}')
    if not gate_ok:
        print('HARD_FAIL: gate/read-back failed. Reverting.')
        ps2.remove_atom(f'math::{ATOM_ID}', source='revert', note='gate fail'); return 2
    print('=' * 72)
    print(f'A2 v6 GROWN landed: math::{ATOM_ID}  CERT {post_cert} (574->575)  axiom 206  cap_pres 6/6  -- A-now/C-deferred chain CLOSED corpus-robust')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
