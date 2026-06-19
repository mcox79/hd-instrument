"""Promote #4 EXP_t3_phaseA2_2level_recovery_cpu_v1 -> CERT_CHAIN_GRADE (Skunkworks 5-MM disposition #4 CONFIRM, 2026-06-19).
CERT 583 -> 584. The BROAD-envelope re-run on the CURRENT substrate REPRODUCED #4's recall_2level EXACTLY
(HYP 0.993/0.931/0.853 + PART_OF 0.627/0.500) -> the measurement is real + reproducible -> clean promote.
ALSO fixes the isolated mis-pointer: metrics_path was data/exp_b_alpha_broad_v3_2level (a DIFFERENT experiment) ->
re-point to the fresh reproducing run data/exp_substrate_broad_envelope_rerun_4and5_20260619/metrics.json.

SAFE metadata-patch + fresh-Store LOAD gate; MATH single-writer window. DRY-RUN default; --apply. ASCII; no Date.now.
"""
from __future__ import annotations
import argparse
import dataclasses
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

DATE = '2026-06-19'
ATOM = 'T3/EXP_t3_phaseA2_2level_recovery_cpu_v1'
FRESH_METRICS = 'data/exp_substrate_broad_envelope_rerun_4and5_20260619/metrics.json'
# reproduced recall (BROAD envelope re-run on current substrate; deterministic graph-BFS)
REPRODUCED = {'HYPERNYM_2hop': 0.993, 'HYPERNYM_3hop': 0.931, 'HYPERNYM_4hop': 0.853, 'PART_OF_2hop': 0.627, 'PART_OF_3hop': 0.500}


def cert_count(ps):
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def axiom_term_count(ps):
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def run(apply: bool) -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert_count(ps); pre_axiom = axiom_term_count(ps)
    a = next((x for x in ps.all_atoms() if str(x.id) == ATOM), None)
    if a is None:
        print('atom not found'); return 2
    md = dict(a.metadata or {})
    if md.get('provenance_quality') == 'CERT_CHAIN_GRADE':
        print('already CERT -> skip'); return 0
    # verify the in-atom claimed recall reproduces (reproduce-or-flag; Skunkworks condition)
    claimed = (md.get('key_metrics') or {}).get('recall_2level') or {}
    diverge = {k: (claimed.get(k), REPRODUCED[k]) for k in REPRODUCED if abs((claimed.get(k) or -1) - REPRODUCED[k]) > 0.01}
    print(f'PRE: CERT={pre_cert} axiom={pre_axiom}')
    print(f'  reproduce-check: claimed recall_2level vs BROAD-rerun -> diverge={diverge or "NONE (exact match)"}')
    if diverge:
        print('FLAG: divergence -> do NOT silently promote (Skunkworks reproduce-or-flag). Halt.'); return 3
    md['provenance_quality'] = 'CERT_CHAIN_GRADE'
    md['cert_vet_status'] = 'cert_promoted'
    md['cert_promoted_date'] = DATE
    md['cert_promoted_by_vet'] = 'skunkworks_5MM_disposition_#4_2026-06-19'
    md['cert_promoted_from'] = 'MEASURED_MECHANISM'
    md['metrics_path'] = FRESH_METRICS                      # FIX the isolated mis-pointer
    md['metrics_path_fixed_from'] = 'data/exp_b_alpha_broad_v3_2level/metrics.json (isolated mis-pointer -> different experiment)'
    md['rerun_reproduced'] = True
    md['rerun_reproduce_note'] = ('BROAD-envelope re-run on the current substrate reproduced recall_2level EXACTLY '
                                  '(HYP 0.993/0.931/0.853 + PART_OF 0.627/0.500); measured_graph_bfs_held_out; HYPERNYM '
                                  'secondhop edges survived the corruption-restore. measurement-class promote.')
    md['relevance_tier'] = md.get('relevance_tier') or 'ACTIVE'
    atom = dataclasses.replace(a, metadata=md)
    print(f'  {ATOM}: MEASURED_MECHANISM -> CERT_CHAIN_GRADE (verdict={md.get("verdict")}; metrics_path FIXED -> {FRESH_METRICS})')
    if not apply:
        print(f'\nDRY-RUN OK -> CERT {pre_cert}->{pre_cert+1}. Re-run --apply.'); return 0
    ps.add_atom(atom, source='promote_4_t3phaseA2_CERT584', note='Skunkworks #4 disposition; reproduces-exactly; mis-pointer fixed; measurement-class promote')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert = cert_count(ps2); post_axiom = axiom_term_count(ps2)
    b = next((x for x in ps2.all_atoms() if str(x.id) == ATOM), None)
    pq = (b.metadata or {}).get('provenance_quality') if b else None
    gate_ok = (pq == 'CERT_CHAIN_GRADE' and post_cert == pre_cert + 1 and post_axiom == pre_axiom)
    print(f'\nPOST: CERT={post_cert} (pre {pre_cert} +1) axiom={post_axiom} | pq={pq} | metrics_path={(b.metadata or {}).get("metrics_path")} | LOAD-gate {"OK" if gate_ok else "FAIL"}')
    if not gate_ok:
        print('HARD_FAIL: LOAD-gate/CERT.'); return 6
    print(f'\nPROMOTE OK: {ATOM} CERT_CHAIN_GRADE. CERT {pre_cert} -> {post_cert}. Route for Skunkworks verdict-VET.')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    return run(ap.parse_args().apply)


if __name__ == '__main__':
    raise SystemExit(main())
