"""Fix the 2 I4/I5 fields on the q_b1 A/B atom (Skunkworks landed-VET 2026-06-19). A5-safe capint-only;
CERT 588 unchanged. I4: shared_benchmark -> 'q_b1_chain_depth' (match cluster). I5: proven_bound (was None).
DRY-RUN default; --apply."""
from __future__ import annotations
import argparse, dataclasses, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
ATOM = 'T3/EXP_q_b1_ab_iterate_3arm_v1_n16384'
BENCH = 'q_b1_chain_depth'
PROVEN = ('cleanup-between-hops (snap-to-nearest-stored-node) extends q_b1 chain-depth to PASS through d293 '
          'at N=16384, 5/5 seeds; cliff eliminated in the tested range (<=d293); extent beyond d293 UNTESTED '
          '(d300-d500 follow-up locates the new cliff). Honest-scope: the cleanup-between-hops mechanism, not '
          'a generic deep-chain claim.')

def run(apply):
    ps = PartitionedStore(Path('data/substrate_index'))
    a = next((x for x in ps.all_atoms() if str(x.id) == ATOM), None)
    if a is None:
        print('atom not found'); return 2
    md = dict(a.metadata or {})
    print('PRE: shared_benchmark=', md.get('capint_shared_benchmark'), '| proven_bound set=', md.get('capint_proven_bound') is not None)
    md['capint_shared_benchmark'] = BENCH
    md['capint_proven_bound'] = PROVEN
    if md.get('provenance_quality') != 'CERT_CHAIN_GRADE':
        print('WARN pq not CERT'); return 3
    if not apply:
        print('DRY-RUN OK -> set shared_benchmark=%s + proven_bound (A5-safe; pq/CERT unchanged). --apply.' % BENCH); return 0
    ps.add_atom(dataclasses.replace(a, metadata=md), source='fix_qb1_AB_I4_I5', note='Skunkworks landed-VET I4/I5 field fixes; A5-safe capint-only')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    b = next((x for x in ps2.all_atoms() if str(x.id) == ATOM), None); bmd = b.metadata or {}
    ok = (bmd.get('capint_shared_benchmark') == BENCH and bmd.get('capint_proven_bound') == PROVEN and bmd.get('provenance_quality') == 'CERT_CHAIN_GRADE')
    print('POST: shared_benchmark=%s | proven_bound set=%s | pq=%s | gate %s' % (bmd.get('capint_shared_benchmark'), bmd.get('capint_proven_bound') is not None, bmd.get('provenance_quality'), 'OK' if ok else 'FAIL'))
    return 0 if ok else 6

ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
raise SystemExit(run(ap.parse_args().apply))
