"""CERT 591 (kv_learned_projection_v1) key_metrics label-fidelity relabel (Skunkworks NOD 2026-06-20).
The 'worst' keys were the M=10000 per-M MEANS, not worst-across-units (Testbed 2nd-witness off per_unit;
Orchestrator verify-own-atom). Rename worst->mean + ADD true worst_per_unit + ADD max_std_per_unit.
pq/cert-class/relevance_tier/verdict UNTOUCHED (A5: label-fidelity, NOT re-classification). CERT 591/592 unchanged.
Consumer-check (grep tools/experiments/verification/hdlab) was EMPTY -> safe to rename. DRY-RUN default; --apply.
"""
from __future__ import annotations
import argparse, dataclasses, json, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

ATOM = 'T3/EXP_kv_learned_projection_v1'
# verify-the-referent: the LIVE pre-state values I snapshotted (assert before mutating)
PRE = {'heldout_recall_10k_worst': 0.8273, 'keysep_worst': 0.8784, 'max_std': 0.0189}
RELABEL_NOTE = (
    "2026-06-20 label-fidelity (Skunkworks nod): 'heldout_recall_10k_worst'(0.8273) + 'keysep_worst'(0.8784) "
    "were M=10000 per-M MEANS, NOT worst-across-units -> renamed to _mean + added true _worst_per_unit "
    "(recall 0.805 [M10k seed1], keysep 0.726 [M2k seed4]) + max_std_per_unit 0.021 [true max per-M std, M10k]. "
    "pq/cert-class/verdict UNTOUCHED. CERT 591 HOLDS (4 gates pass even at actual worst 0.805). "
    "Src: Testbed 2nd-witness off per_unit + Orchestrator verify-own-atom. FLAGGED-NOT-CHANGED (Skunkworks call): "
    "analytic_ceiling(0.0804=M2k mean) + learned_minus_analytic(0.7469=cross-M-mean margin; true worst 0.705) "
    "are same imprecision-class but deeper (cross-M conflation) -> separate cert-semantics decision."
)


def run(apply):
    ps = PartitionedStore(Path('data/substrate_index'))
    a = next((x for x in ps.all_atoms() if str(x.id) == ATOM), None)
    if a is None:
        print('ATOM NOT FOUND:', ATOM); return 2
    md = dict(a.metadata or {})
    km = dict(md.get('key_metrics') or {})
    # === verify-the-referent: assert the live pre-state matches my snapshot ===
    for k, v in PRE.items():
        if abs(float(km.get(k, -999)) - v) > 1e-6:
            print('PRE-STATE MISMATCH %s: live=%s expected=%s -- ABORT' % (k, km.get(k), v)); return 4
    if md.get('provenance_quality') != 'CERT_CHAIN_GRADE':
        print('WARN pq != CERT_CHAIN_GRADE:', md.get('provenance_quality')); return 3
    print('PRE key_metrics:', json.dumps(km))
    # === relabel (ADD-don't-break; rename worst->mean since consumer-check empty) ===
    km['heldout_recall_10k_mean'] = km.pop('heldout_recall_10k_worst')   # 0.8273 (correctly labeled)
    km['heldout_recall_10k_worst_per_unit'] = 0.805                       # true worst-across-units (M10k seed1)
    km['keysep_10k_mean'] = km.pop('keysep_worst')                       # 0.8784
    km['keysep_worst_per_unit'] = 0.726                                  # true worst (M2k seed4)
    km['max_std_per_unit'] = 0.021                                       # true max per-M std (M10k); max_std=0.0189 kept
    md['key_metrics'] = km
    md['_relabel_note_2026_06_20'] = RELABEL_NOTE
    print('POST key_metrics:', json.dumps(km))
    print('pq (unchanged):', md.get('provenance_quality'), '| verdict (unchanged):', md.get('verdict'))
    if not apply:
        print('DRY-RUN OK -> relabel ready (pq/verdict UNTOUCHED, +0 atoms). Re-run with --apply.'); return 0
    ps.add_atom(dataclasses.replace(a, metadata=md), source='orchestrator_cert591_relabel',
                note='Skunkworks nod: worst->mean + worst_per_unit + max_std_per_unit; A5 label-fidelity; pq untouched')
    # === reciprocal verify off a fresh load ===
    ps2 = PartitionedStore(Path('data/substrate_index'))
    b = next((x for x in ps2.all_atoms() if str(x.id) == ATOM), None)
    bmd = b.metadata or {}; bkm = bmd.get('key_metrics') or {}
    ok = (bkm.get('heldout_recall_10k_mean') == 0.8273
          and bkm.get('heldout_recall_10k_worst_per_unit') == 0.805
          and bkm.get('keysep_10k_mean') == 0.8784
          and bkm.get('keysep_worst_per_unit') == 0.726
          and bkm.get('max_std_per_unit') == 0.021
          and 'heldout_recall_10k_worst' not in bkm
          and 'keysep_worst' not in bkm
          and bmd.get('provenance_quality') == 'CERT_CHAIN_GRADE'
          and bmd.get('verdict') == a.metadata.get('verdict'))
    print('POST-RELOAD verify:', 'OK' if ok else 'FAIL')
    print('  reloaded key_metrics:', json.dumps(bkm))
    return 0 if ok else 6


ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
raise SystemExit(run(ap.parse_args().apply))
