#!/usr/bin/env python3
"""Skunkworks 2026-06-19 -- C1 SUBSTRATE-STATE-CHANGE CERT-PROTOCOL (Phase-1 ship gate).

The PART_OF-revert lesson (inst-243), GENERALIZED into standing infrastructure: ANY
substrate-state change (a lever-ship, a re-encode, an operational-baseline change) can
SILENTLY INVALIDATE existing cert atoms certified against the OLD state. This tool gates
such a change -- it mechanizes the dependent-cert-atom regression-set identification (the
hard part) + prints the C1 protocol checklist + the ship-decision criteria. READ-ONLY.

C1 is one of the cert-architecture layer's protocols (C0-C6); it is the Phase-1 ship gate
in the comprehensive program. Composes the reconciliation protocol (C5) + integration-check
v1.2 swap-gating (C3) + the substrate-state-completeness lesson (inst-243).

THE C1 PROTOCOL (every state-changing ship):
  1. PRE-SHIP baseline: record the dependent cert atoms' CURRENT results (this tool lists them).
  2. SHIP behind a CONFIG-FLAG (reversible; default OFF).
  3. SECOND CERT-EVENT: the lever delivers its PROVEN lift at the PRODUCTION operating-point
     (not just its test-point) -- a cert-grade run at the deployed config.
  4. DEPENDENT-CERT-ATOM REGRESSION-CHECK: re-run the dependent cert atoms under the NEW
     state; compare to their cert-claims. Any that BREAK -> re-VET (downgrade/re-scope)
     BEFORE flipping the default. (This is the load-bearing step -- the PART_OF lesson.)
  5. v1.2 I7/I8/I9 swap-gating IF the lever becomes a capability's new current_best.
  6. RECORD the deployed-config cert-event + the regression-check result.

SHIP-DEFAULT decision: flip the flag to default ONLY IF (3) passes AND (4) passes (no
dependent cert atom breaks, OR every break is re-VET'd + accepted with honest re-scope).
Else: keep the flag OFF (opt-in only) or re-scope the lever's claim.

Usage: python tools/skunkworks_state_change_cert_protocol_v1.py --lever <name>
  levers: csp_warm_start | capacity_battery | pca_prewhitening | sparse_coding | multiplicative_composition
Read-only; prints the candidate dependent-set + the protocol checklist. ASCII.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

# Each lever changes a specific axis of the operating point; the dependent cert atoms are
# those whose eval OPERATES ON that axis (keyword proxy -- a STARTING set the cert-owner refines).
LEVER_AXES = {
    'csp_warm_start': {
        'axis': 'initialization-path (NOT the representation)',
        'risk': 'LOW (speedup/init; representation unchanged)',
        'keywords': ['csp', 'warm_start', 'initialization', 'speedup', 'convergence'],
        'expect_size': '~6 (init/speedup-dependent only)',
    },
    'capacity_battery': {
        'axis': 'capacity sweet-spot config (N / load)',
        'risk': 'LOW-MEDIUM (config tune)',
        'keywords': ['capacity', 'n_', 'load', 'scale', 'alpha_c', 'saturat'],
        'expect_size': '~15',
    },
    'pca_prewhitening': {
        'axis': 'ENCODING (encoded-vector geometry)',
        'risk': 'MEDIUM (encoder-dependent atoms)',
        'keywords': ['encoder', 'minilm', 'pythia', 'llama', 'whiten', 'embedding',
                     'retrieval', 'refuse', 'bge', 'recall', 'pca'],
        'expect_size': '~48',
    },
    'sparse_coding': {
        'axis': 'REPRESENTATION (sparsity / vector density)',
        'risk': 'HIGH (most representation-dependent atoms)',
        'keywords': ['sparse', 'dense', 'capacity', 'readout', 'cleanup', 'hopfield',
                     'recall', 'entmax', 'codebook', 'retrieval', 'refuse', 'compose'],
        'expect_size': '~298 (broad; sub-batch per domain)',
    },
    'multiplicative_composition': {
        'axis': 'COMPOSITION operator (bind/superpose)',
        'risk': 'HIGHEST (composition-dependent atoms)',
        'keywords': ['compose', 'bind', 'superpose', 'multihop', 'khop', 'chain', 'depth',
                     'cross_layer', 'composition', 'binding', 'multiplicative'],
        'expect_size': '~347 (broadest; sub-batch per domain)',
    },
}


def md(a):
    return getattr(a, 'metadata', {}) or {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lever', required=True, choices=sorted(LEVER_AXES))
    ap.add_argument('--show', type=int, default=15)
    args = ap.parse_args()
    spec = LEVER_AXES[args.lever]

    ps = PartitionedStore(Path('data/substrate_index'))
    atoms = list(ps.all_atoms())
    cert = [a for a in atoms if md(a).get('provenance_quality') == 'CERT_CHAIN_GRADE']
    dep = []
    for a in cert:
        blob = (a.id + ' ' + str(getattr(a, 'name', '') or '') + ' ' + str(getattr(a, 'description', '') or '')).lower()
        if any(k in blob for k in spec['keywords']):
            dep.append(a)

    print('=' * 80)
    print(f'C1 STATE-CHANGE CERT-PROTOCOL -- lever: {args.lever}')
    print(f'  affected axis: {spec["axis"]}')
    print(f'  regression-risk: {spec["risk"]}  | expected dependent-set: {spec["expect_size"]}')
    print('-' * 80)
    print(f'CANDIDATE DEPENDENT CERT-ATOM SET (the regression-set): {len(dep)} atoms')
    print('  (cert atoms whose eval OPERATES ON the affected axis -- a STARTING set; cert-owner refines)')
    for a in dep[:args.show]:
        print(f'    {a.id.split("/")[-1][:54]:<54} | {md(a).get("verdict")}')
    if len(dep) > args.show:
        print(f'    ... +{len(dep)-args.show} more (full list via --show {len(dep)})')
    print('-' * 80)
    print('C1 PROTOCOL (gate this ship):')
    print('  1. PRE-SHIP baseline: record these atoms\' CURRENT results (under the OLD state).')
    print('  2. SHIP behind a CONFIG-FLAG (reversible; default OFF).')
    print('  3. SECOND CERT-EVENT: lever delivers its proven lift at the PRODUCTION operating-point.')
    print('  4. DEPENDENT-CERT-ATOM REGRESSION-CHECK: re-run the set above under the NEW state;')
    print('     any that BREAK -> re-VET (downgrade/re-scope) BEFORE flipping the default. [load-bearing]')
    print('  5. v1.2 I7/I8/I9 swap-gating IF the lever becomes a capability\'s new current_best.')
    print('  6. RECORD the deployed-config cert-event + the regression-check result.')
    print('-' * 80)
    print('SHIP-DEFAULT decision: flip-to-default ONLY IF (3) passes AND (4) passes')
    print('  (no dependent cert atom breaks, OR every break is re-VET\'d + honestly re-scoped).')
    print('  Else: keep the flag OFF (opt-in) or re-scope the lever\'s claim. NEVER silent-default.')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
