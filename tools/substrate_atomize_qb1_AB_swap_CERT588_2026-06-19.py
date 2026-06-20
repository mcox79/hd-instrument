#!/usr/bin/env python3
"""Atomize the q_b1 A/B HARD_PASS as the new current_best of the q_b1_chain_depth_cliff cluster
(Skunkworks verdict-VET PASS + swap-design CONFIRMED 2026-06-19). CERT 587 -> 588 (ONE cert event).

Cluster-canonical swap (Skunkworks Q1/Q2/Q3 answers):
  1. CREATE new A/B cert atom T3/EXP_q_b1_ab_iterate_3arm_v1_n16384 = canonical of q_b1_chain_depth_cliff,
     CERT_CHAIN_GRADE / HARD_PASS / is_bound=False; I7 superseded_chain=[d276]; I9 swap_win_condition+cell_commit.
  2. DEMOTE d276: capint_cluster_member_role canonical -> scale_point (Q1); current_best_citation -> new atom.
  3. RE-POINT ALL members citing d276 (Q2): capint_current_best_citation -> new atom.
  4. LINK resonator n4096 smoke atom via strengthened_by -> new atom; STAYS SMOKE_ONLY (Q3: NO in-place
     pq-promote -- n4096 iterated-retrieval is a DIFFERENT config/task than N=16384 chain-depth; promoting
     would certify an un-re-run claim = version-marker/honest-scope violation).
Honest-scope LOCKED: cleanup-between-hops extends q_b1 chain-depth PASS through d293; cliff eliminated in
tested range (<=d293); extent beyond UNTESTED. A5-safe (no pq recompute elsewhere). DRY-RUN default; --apply.
Post-state gate: exactly 1 canonical (new), d276=scale_point, all citers re-pointed, CERT 588, integrated 491,
resonator pq still SMOKE_ONLY, Store loads. ASCII; no Date.now.
"""
from __future__ import annotations
import argparse
import dataclasses
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

DATE = '2026-06-19'
NEW_ID = 'T3/EXP_q_b1_ab_iterate_3arm_v1_n16384'
D276 = 'T3/EXP_q_b1_bisect_d276_v1_n16384'
CLUSTER = 'q_b1_chain_depth_cliff'
OLD_CITATION = 'math::' + D276
NEW_CITATION = 'math::' + NEW_ID
RESONATOR = 'T3/EXP_substrate_resonator_augmented_iterated_retrieval_v1_n4096'
METRICS = 'data/exp_q_b1_ab_iterate_3arm_v1_n16384/metrics.json'
CELL_COMMIT = 'cf33942257170431eda61a2851b60b75d6f85577'
HONEST_SCOPE = ('resonator cleanup-between-hops (snap-to-nearest-stored-node each hop) extends q_b1 chain-depth '
                'to PASS through d293 (control collapses at d287); cliff ELIMINATED in the tested range (<=d293), '
                'extent beyond d293 UNTESTED (not "no cliff"). Mechanism: per-hop exact-snap resets crosstalk '
                'accumulation. Specific op; not a generic reasoning-depth claim.')
WIN_CONDITION = 'pre-reg v4 HARD_PASS: PASS d>=287 AND no-regression d100+d276; N=1 alpha=0.05 (commit 2b9bf477)'


def cert_count(ps):
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def integ_count(ps):
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('capint_integrated') is True)


def build_new_atom(key_metrics):
    md = {
        'provenance_quality': 'CERT_CHAIN_GRADE', 'verdict': 'HARD_PASS',
        'cert_vet_status': 'cert_atomized', 'cert_promoted_date': DATE,
        'cert_promoted_by_vet': 'skunkworks_qb1_AB_verdict_VET_2026-06-19',
        'metrics_path': METRICS, 'metrics_source': 'measured_gpu_heteroassoc_chain_depth_3arm_ab',
        'cell_commit': CELL_COMMIT, 'key_metrics': key_metrics, 'honest_scope': HONEST_SCOPE,
        'relevance_tier': 'ACTIVE',
        # cap-int swap (new canonical)
        'capint_integrated': True, 'capint_primary_domain': 'reasoning_multihop',
        'capint_cluster_id': CLUSTER, 'capint_cluster_member_role': 'canonical',
        'capint_capability_name': 'Q_B1 chain-depth reasoning (cleanup-extended)',
        'capint_verdict': 'HARD_PASS', 'capint_is_bound': False,
        'capint_current_best_citation': NEW_CITATION,
        'capint_canonical_substring_all': ['q_b1_ab_iterate_3arm_v1_n16384'],
        'capint_superseded_chain': [D276],
        'capint_swap_win_condition': WIN_CONDITION,
        'capint_shared_benchmark': 'q_b1 heteroassoc chain-depth cliff at N=16384',
        'strengthened_by': [RESONATOR],
    }
    return Atom(
        id=NEW_ID, name='Q_B1 chain-depth A/B: cleanup-between-hops extends cliff to d293',
        corpus=Corpus.MATH, tier=Tier.TIER_3_ALGORITHM, kind=AtomKind.EXPERIMENT_RECORD,
        description=HONEST_SCOPE, metadata=md,
    )


def run(apply: bool) -> int:
    m = json.load(open(METRICS, encoding='utf-8'))
    det = m.get('detail', {})
    if not (m.get('verdict') == 'HARD_PASS' and m.get('metrics_source') == 'measured_gpu_heteroassoc_chain_depth_3arm_ab' and m.get('n_seeds') == 5):
        print('FLAG: q_b1 metrics not the marker-verified HARD_PASS v-run -> HALT.'); return 3
    key_metrics = {'arm_verdict': det.get('arm_verdict'), 'per_depth': det.get('per_depth'),
                   'best_candidate': det.get('best_candidate'),
                   'cand2_endpoint_d293': det.get('mean_profile', {}).get('cand2_cleanup', {}).get('293', {}).get('293'),
                   'control_endpoint_d287': det.get('mean_profile', {}).get('control', {}).get('287', {}).get('287')}

    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert_count(ps); pre_int = integ_count(ps)
    atoms = list(ps.all_atoms())
    if any(str(a.id) == NEW_ID for a in atoms):
        print('new atom already exists -> skip (idempotent)'); return 0
    d276 = next((a for a in atoms if str(a.id) == D276), None)
    reson = next((a for a in atoms if str(a.id) == RESONATOR), None)
    if d276 is None or reson is None:
        print('d276 or resonator atom not found -> HALT'); return 2
    # citers EXCLUDING d276 (d276 is handled by the demote below; including it here would re-add d276
    # from its ORIGINAL canonical metadata + overwrite the demote -> 2 canonicals -> I4 FAIL).
    citers = [a for a in atoms if (a.metadata or {}).get('capint_current_best_citation') == OLD_CITATION
              and str(a.id) != D276]
    print(f'PRE: CERT={pre_cert} integrated={pre_int}')
    print(f'  d276 -> demote (canonical->scale_point) + current_best->A/B (handled separately)')
    print(f'  other citers to re-point: {[str(a.id) for a in citers]}')

    # build mutations
    new_atom = build_new_atom(key_metrics)
    d276_md = dict(d276.metadata or {}); d276_md['capint_cluster_member_role'] = 'scale_point'; d276_md['capint_current_best_citation'] = NEW_CITATION
    d276_md['capint_superseded_by'] = NEW_ID
    reson_md = dict(reson.metadata or {})
    sb = list(reson_md.get('strengthens') or []);
    if NEW_ID not in sb: sb.append(NEW_ID)
    reson_md['strengthens'] = sb
    reson_md['strengthens_note'] = ('precursor smoke-evidence (n4096 iterated-retrieval, 6x lower-bound); the '
                                    'cleanup-between-hops MECHANISM is now cert-validated in q_b1 N=16384 chain-depth '
                                    'via CERT 588. This n4096 retrieval claim itself stays SMOKE_ONLY (different config) '
                                    'until re-run at its own config.')
    print(f'  CREATE {NEW_ID} (canonical, CERT/HARD_PASS); DEMOTE d276 canonical->scale_point; '
          f'RE-POINT {len(citers)} citers; LINK resonator (strengthens; stays SMOKE_ONLY).')
    if not apply:
        print(f'\nDRY-RUN OK -> CERT {pre_cert}->{pre_cert+1}, integrated {pre_int}->{pre_int+1}. Re-run --apply (PRE-ANNOUNCE first).'); return 0

    ps.add_atom(new_atom, source='atomize_qb1_AB_swap_CERT588', note='q_b1 A/B HARD_PASS; new cluster canonical; swap from d276')
    ps.add_atom(dataclasses.replace(d276, metadata=d276_md), source='atomize_qb1_AB_swap_CERT588', note='demote d276 canonical->scale_point; current_best->A/B')
    for c in citers:
        cmd = dict(c.metadata or {}); cmd['capint_current_best_citation'] = NEW_CITATION
        ps.add_atom(dataclasses.replace(c, metadata=cmd), source='atomize_qb1_AB_swap_CERT588', note='re-point current_best to A/B canonical')
    ps.add_atom(dataclasses.replace(reson, metadata=reson_md), source='atomize_qb1_AB_swap_CERT588', note='strengthens link to A/B; stays SMOKE_ONLY (Q3)')

    ps2 = PartitionedStore(Path('data/substrate_index')); atoms2 = list(ps2.all_atoms())
    post_cert = cert_count(ps2); post_int = integ_count(ps2)
    canon = [str(a.id) for a in atoms2 if (a.metadata or {}).get('capint_cluster_id') == CLUSTER and (a.metadata or {}).get('capint_cluster_member_role') == 'canonical']
    d276b = next((a for a in atoms2 if str(a.id) == D276), None)
    resonb = next((a for a in atoms2 if str(a.id) == RESONATOR), None)
    remaining_citers = [str(a.id) for a in atoms2 if (a.metadata or {}).get('capint_current_best_citation') == OLD_CITATION]
    gate = (post_cert == pre_cert + 1 and post_int == pre_int + 1 and canon == [NEW_ID]
            and (d276b.metadata or {}).get('capint_cluster_member_role') == 'scale_point'
            and not remaining_citers
            and (resonb.metadata or {}).get('provenance_quality') == 'SMOKE_ONLY')
    print(f'\nPOST: CERT={post_cert} (pre {pre_cert}+1) | integrated={post_int} (pre {pre_int}+1) | cluster canonical={canon} '
          f'| d276 role={(d276b.metadata or {}).get("capint_cluster_member_role")} | remaining d276-citers={remaining_citers} '
          f'| resonator pq={(resonb.metadata or {}).get("provenance_quality")} | gate {"OK" if gate else "FAIL"}')
    if not gate:
        print('HARD_FAIL: gate.'); return 6
    print(f'\nATOMIZE OK: q_b1 A/B -> CERT {pre_cert}->{post_cert}; cluster canonical swapped to A/B; d276=scale_point; '
          f'{len(citers)} citers re-pointed; resonator strengthens-linked (SMOKE_ONLY). Route Orchestrator LOAD-gate + Skunkworks I4/I7/I8/I9.')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    return run(ap.parse_args().apply)


if __name__ == '__main__':
    raise SystemExit(main())
