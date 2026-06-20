"""Atomize phase4b-multistep v3 pull-up -> CERT_CHAIN_GRADE (Skunkworks verdict-VET HARD_PASS CONFIRMED;
CERT 588->589). FIRST value-coverage pull-up to complete the full SCHEMA-VET->dispatch->verdict-VET->cert
cycle. NEW singleton cert atom + cap-int integrate; strengthen-link the legacy phase4b atoms (promoted via
the v3 iso-protocol; they stay LEGACY_EXCERPT). Reads the marker-verified landed metrics for key_metrics.
A5-safe; single-writer; DRY-RUN default; --apply. ASCII; no Date.now."""
from __future__ import annotations
import argparse, dataclasses, json, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

NEW_ID = 'T3/EXP_phase4b_multistep_pull_up_v2_cpu_v1'
METRICS = 'data/exp_phase4b_multistep_pull_up_v2_cpu_v1/metrics.json'
LEGACY = ['T3/EXP_phase4b_multistep_cpu_v1', 'T3/EXP_phase4b_multistep_multiseed_cpu_v1']
HS = ('substrate-classical 2-op composition on MultiArith (acc 0.692, 40x over the 1-op baseline; no LLM) + '
      '1-op generalization on ASDiv/MAWPS; op-depth matched to each benchmark content; BOUNDED to 2-op (MultiArith '
      '3-op cliff=0.0, reported); ASDiv/MAWPS 2-op + SVAMP = representation/content boundaries (reported, not gated).')


def cert_count(ps): return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
def integ_count(ps): return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('capint_integrated') is True)


def run(apply):
    m = json.load(open(METRICS, encoding='utf-8'))
    if not (m.get('verdict') == 'HARD_PASS' and m.get('metrics_source') == 'measured_cpu_substrate_multistep_composition_4bench_opdepth' and m.get('n_seeds') == 5):
        print('FLAG: metrics not the marker-verified HARD_PASS v3 run -> HALT'); return 3
    d = m.get('detail', {})
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert_count(ps); pre_int = integ_count(ps)
    if any(str(a.id) == NEW_ID for a in ps.all_atoms()):
        print('atom exists -> skip (idempotent)'); return 0
    km = {'GATING': d.get('GATING_op_depth_matched'), 'MultiArith_ratio': d.get('MultiArith_ratio_2op_1op'),
          'reported': {'ASDiv_2op': d.get('REPORTED_ASDiv_2op'), 'MAWPS_2op': d.get('REPORTED_MAWPS_2op'),
                       'SVAMP_2op': d.get('REPORTED_SVAMP_2op'), 'cliff_3op_MultiArith': d.get('REPORTED_cliff_3op_MultiArith')}}
    md = {'provenance_quality': 'CERT_CHAIN_GRADE', 'verdict': 'HARD_PASS', 'cert_vet_status': 'cert_atomized',
          'cert_promoted_date': '2026-06-19', 'cert_promoted_by_vet': 'skunkworks_phase4b_v3_verdict_VET_2026-06-19',
          'metrics_path': METRICS, 'metrics_source': m.get('metrics_source'), 'key_metrics': km, 'honest_scope': HS,
          'relevance_tier': 'ACTIVE', 'capint_integrated': True, 'capint_primary_domain': 'reasoning_multihop',
          'capint_cluster_id': None, 'capint_cluster_member_role': 'singleton', 'capint_shared_benchmark': 'MultiArith 2-op composition + cross-benchmark 1-op generalization',
          'capint_capability_name': 'Substrate 2-op composition word-problem solver (op-depth-matched unified)',
          'capint_verdict': 'HARD_PASS', 'capint_is_bound': False,
          'capint_proven_bound': HS, 'capint_current_best_citation': 'reasoning_multihop::' + NEW_ID,
          'capint_canonical_substring_all': ['phase4b_multistep_pull_up_v2_cpu_v1'], 'strengthened_by': LEGACY}
    atom = Atom(id=NEW_ID, name='Substrate 2-op composition word-problem solver (phase4b v3 unified, op-depth-matched)',
                corpus=Corpus.MATH, tier=Tier.TIER_3_ALGORITHM, kind=AtomKind.EXPERIMENT_RECORD, description=HS, metadata=md)
    print('PRE: CERT=%d integrated=%d' % (pre_cert, pre_int))
    print('  CREATE %s (CERT/HARD_PASS singleton; cap-int integrated; strengthen-link %d legacy)' % (NEW_ID, len(LEGACY)))
    if not apply:
        print('\nDRY-RUN OK -> CERT %d->%d, integrated %d->%d. --apply (PRE-ANNOUNCE first).' % (pre_cert, pre_cert+1, pre_int, pre_int+1)); return 0
    ps.add_atom(atom, source='atomize_phase4b_CERT589', note='Skunkworks verdict-VET HARD_PASS; first full-cycle pull-up; unified-solver composition')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert = cert_count(ps2); post_int = integ_count(ps2)
    b = next((x for x in ps2.all_atoms() if str(x.id) == NEW_ID), None); bmd = (b.metadata or {}) if b else {}
    gate = (post_cert == pre_cert+1 and post_int == pre_int+1 and bmd.get('provenance_quality') == 'CERT_CHAIN_GRADE' and bmd.get('capint_is_bound') is False)
    print('\nPOST: CERT=%d (pre %d+1) integrated=%d (pre %d+1) | pq=%s | is_bound=%s | gate %s' %
          (post_cert, pre_cert, post_int, pre_int, bmd.get('provenance_quality'), bmd.get('capint_is_bound'), 'OK' if gate else 'FAIL'))
    if not gate: print('HARD_FAIL gate'); return 6
    print('\nATOMIZE OK: phase4b -> CERT %d->%d. First full-cycle value-coverage pull-up. Route Orchestrator LOAD-gate + Skunkworks landed-VET (I1/I3/I5).' % (pre_cert, post_cert))
    return 0

ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
raise SystemExit(run(ap.parse_args().apply))
