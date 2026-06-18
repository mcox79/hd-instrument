"""Deliberate cert-re-validation (Skunkworks solo; USER-ratified cert-re-validation auto-route 2026-06-18).

Re-tiers the 2 CERT_CHAIN_GRADE atoms with verdict=None (legacy mis-tiers) -> UNVERIFIED. These were tagged
CERT under OLDER atomizer logic; under CURRENT rules a verdict=None (unmappable) + raw metrics_source=None
atom -> method_gate FAILS + verdict-unmappable -> UNVERIFIED (verified: cpu_v1 has n_seeds=5 so would_be_cert,
but null source fails method_gate_ok). The defensible CLEAR-DEFECT set (exactly 2; verdict=None is metadata-
detectable, NOT a schema artifact -- contrast metrics_source which IS a schema artifact, so NOT swept here per
the negativity-bias-symmetric guardrail).

A5: SNAPSHOT per-record state BEFORE mutation. Deliberate cert-owner re-classification (no auto-recompute of
the rest). CERT 571 -> 569 (the honest count; the 2 NEW B-alpha composed-reasoning atoms replace these 2 legacy
mis-tiers = a net cert-QUALITY upgrade). axiom_term 206/206 + cap_pres 6/6 unchanged (experiment_records, no
algebra; no module change). ASCII-only; no LLM.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom

TARGET_IDS = [
    "T3/EXP_cardinality_generalization_stage1_190c_2026_06_16",
    "T3/EXP_cardinality_generalization_stage1_190c_cpu_v1",
]
SNAPSHOT = Path("tools/_snapshot_revalidation_190c_2026-06-18.json")
RETIER_NOTE = ("CERT_CHAIN_GRADE->UNVERIFIED (deliberate cert-owner re-validation 2026-06-18; verdict=None "
               "unmappable + raw metrics_source=None -> fails current method_gate + verdict-mapping -> UNVERIFIED "
               "under current atomizer; legacy mis-tier from pre-method-gate logic; USER-ratified cert-re-validation "
               "auto-route; CERT 571->569)")


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


def axiom_term_count(ps: PartitionedStore) -> int:
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH'
               and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3
               and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def cert_count(ps: PartitionedStore) -> int:
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def main() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_cert = cert_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE: atoms={pre_n}  axiom_term={pre_axiom}  CERT={pre_cert}  cap_pres={pre_mod}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL (cap_pres or axiom_term).'); return 1

    by_id = {a.id: a for a in ps.all_atoms()}
    targets = []
    for tid in TARGET_IDS:
        a = by_id.get(tid)
        if a is None:
            print(f'  WARN: target not found: {tid}'); continue
        pq = (a.metadata or {}).get('provenance_quality')
        vd = (a.metadata or {}).get('verdict')
        if pq != 'CERT_CHAIN_GRADE' or vd is not None:
            print(f'  SKIP {tid}: pq={pq} verdict={vd} (not a CERT+verdict=None mis-tier); no retier'); continue
        targets.append(a)

    if not targets:
        print('No targets to re-tier (already corrected or not found). No-op.'); return 0

    # A5: SNAPSHOT per-record state BEFORE mutation
    snap = [{'id': a.id, 'name': a.name, 'kind': str(a.kind), 'tier': str(a.tier), 'corpus': str(a.corpus),
             'metadata': a.metadata} for a in targets]
    SNAPSHOT.write_text(json.dumps(snap, indent=2), encoding='utf-8')
    print(f'  SNAPSHOT {len(snap)} atom(s) -> {SNAPSHOT}')

    # Re-tier CERT_CHAIN_GRADE -> UNVERIFIED (deliberate cert-owner reclass)
    for a in targets:
        md = dict(a.metadata or {})
        md['provenance_quality'] = 'UNVERIFIED'
        md['pq_retier_2026_06_18'] = RETIER_NOTE
        new = Atom(id=a.id, name=a.name, description=a.description, kind=a.kind,
                   tier=a.tier, corpus=a.corpus, algebra=a.algebra, metadata=md)
        ps.add_atom(new, source='skunkworks_revalidation_190c_2026_06_18',
                    note='CERT_CHAIN_GRADE->UNVERIFIED legacy verdict=None mis-tier (deliberate)')
        print(f'  ~ retier: {a.id}  provenance_quality CERT_CHAIN_GRADE -> UNVERIFIED')

    # POST gates
    post_n = sum(1 for _ in ps.all_atoms())
    post_axiom = axiom_term_count(ps)
    post_cert = cert_count(ps)
    post_mod = module_liveness_ok()
    expect_cert = pre_cert - len(targets)
    cert_ok = post_cert == expect_cert
    gate_ok = post_axiom == 206 and post_mod and cert_ok and post_n == pre_n
    print('=' * 72)
    print(f'POST: atoms={post_n} (delta {post_n-pre_n})  axiom_term={post_axiom}  CERT={post_cert} '
          f'(was {pre_cert}; expect {expect_cert}; ok={cert_ok})  cap_pres={post_mod}  -> {"OK" if gate_ok else "HARD_FAIL"}')
    if not gate_ok:
        print('HARD_FAIL: atoms/axiom_term/cap_pres/CERT-count off. INVESTIGATE (snapshot saved for rollback).'); return 2
    print(f'RE-VALIDATION COMPLETE: {len(targets)} legacy verdict=None mis-tier(s) CERT->UNVERIFIED; '
          f'CERT {pre_cert}->{post_cert}; axiom_term 206 + cap_pres + atom-count unchanged.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
