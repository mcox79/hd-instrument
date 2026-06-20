"""Skunkworks 2026-06-19 -- C1 ship-protocol: PRE-SHIP regression-set SNAPSHOT (read-only).

The post-ship landed-VET of a Phase-1 lever-ship must verify the dependent-cert-atom REGRESSION-SET
reproduces its verdicts + key metrics (the C1 state-change cert-protocol step 4). To do that rigorously
you need the PRE-SHIP baseline LOCKED before the ship mutates anything -- the A5 "snapshot per-record
state before any mass mutation" discipline applied to a ship.

This tool reads a named regression-set's CURRENT (pre-ship) verdict + provenance_quality + key_metrics
from the Store and emits a JSON snapshot. After the ship lands, the cell re-runs the regression-set;
the landed-VET compares the cell's post-ship re-runs against THIS snapshot (any verdict flip OR a
key-metric shift beyond the protocol tolerance -> ROLLBACK).

Read-ONLY (never mutates the Store). Composes tools/skunkworks_state_change_cert_protocol_v1.py
(the SCHEMA-VET side) -- this is the landed-VET-side baseline capture. ASCII; no Date.now.

Usage: python tools/skunkworks_ship_regression_snapshot_v1.py [--set csp] [--ids <substr> ...]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

# Named regression-sets (per the ship SPEC; the cert-owner curates these per-ship via the C1 protocol).
REGRESSION_SETS = {
    # CSP-first ship v2 (Phase 1 LEVER #1): 6 CSP-mechanism + 3 retrieval-accuracy (accuracy-neutrality
    # UNVERIFIED on the cert atom -> retrieval-accuracy class added per the C1 dependent-set completeness gate).
    'csp': [
        'csp_memory_warm_start_full_v3',
        'csp_hebbian_coexist_v1',
        'planted_csp_viability_full_v3',
        'hp12_v2_crypto_2048_gmpy2_latency_v1',
        'pp52_hebbian_lora_speedup_n4096_v1',
        'pp52_hebbian_lora_speedup_n8192_v1',
        'substrate_capacity_alpha_sweep_v1_512_16384_gpu',
        'substrate_capacity_composition_full_b2xb4xhier_v1_n2048',
        'substrate_continual_learning_30day_realistic_stream',
    ],
}


def md(a):
    return getattr(a, 'metadata', {}) or {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', default='csp', help='named regression-set (default: csp)')
    ap.add_argument('--ids', nargs='*', help='explicit atom-id substrings (overrides --set)')
    args = ap.parse_args()

    needles = args.ids if args.ids else REGRESSION_SETS.get(args.set)
    if not needles:
        print(f'unknown regression-set "{args.set}" and no --ids given; known: {list(REGRESSION_SETS)}')
        return 2

    ps = PartitionedStore(Path('data/substrate_index'))
    atoms = list(ps.all_atoms())

    snap = {}
    all_found = True
    for needle in needles:
        matches = [a for a in atoms if needle in str(a.id)]
        if not matches:
            snap[needle] = {'FOUND': False}
            all_found = False
            continue
        if len(matches) > 1:
            # prefer an exact-ish / shortest-id match; flag the ambiguity
            matches = sorted(matches, key=lambda a: len(str(a.id)))
        a = matches[0]
        m = md(a)
        snap[needle] = {
            'FOUND': True,
            'id': str(a.id),
            'pq': m.get('provenance_quality'),
            'verdict': m.get('verdict') or m.get('capint_verdict'),
            'is_cert': m.get('provenance_quality') == 'CERT_CHAIN_GRADE',
            'key_metrics': m.get('key_metrics') or {},
            'ambiguous_matches': [str(x.id) for x in matches[1:6]] if len(matches) > 1 else [],
        }

    out = {
        'tool': 'skunkworks_ship_regression_snapshot_v1',
        'regression_set': args.set,
        'n_atoms': len(needles),
        'all_found': all_found,
        'note': 'PRE-SHIP baseline. Post-ship landed-VET: each atom verdict must REPRODUCE (no flip) + key '
                'metrics within the ship-SPEC tolerance (CSP: M_critical/recall within 5%). Any deviation -> ROLLBACK.',
        'pre_ship_snapshot': snap,
    }
    print(json.dumps(out, indent=2))
    return 0 if all_found else 1


if __name__ == '__main__':
    raise SystemExit(main())
