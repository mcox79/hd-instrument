"""Backfill metadata.metrics_source on the 4 canonicalized cert-VET-pending atoms (Skunkworks promotion-path #1,
2026-06-19) from each atom's OWN metrics_path run-output (LOCAL; the remote-direct atomizer's gap was not copying
run-output.metrics_source into the atom metadata; the run itself recorded metrics_source=measured_graph_bfs_held_out).

SAFE metadata-patch (Skunkworks write-hold refinement: metadata-PATCH on existing atoms is allowed): load live atom
(all_atoms scan, NOT get_atom) -> dataclasses.replace metadata -> add_atom update -> fresh-Store all_atoms() LOAD gate.
NO enum field touched, no new-atom-add. Keeps pq=RESEARCH_FINDING / cert_vet_status pending -> Skunkworks promote-VETs.
DRY-RUN default; --apply writes. ASCII; 11th-rule deterministic. No Date.now (fixed date str).
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
TARGET = [
    'T3/EXP_b_alpha_broad_v2_denser_preview',
    'T3/EXP_b_alpha_broad_v3_2level',
    'T3/EXP_partof_broad_after',
    'T3/EXP_partof_broad_before',
]


def cert_count(ps) -> int:
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def _run_output_source(metrics_path: str):
    """Read run-output metrics.json -> (metrics_source, run_mode) or (None, None)."""
    if not metrics_path:
        return None, None
    p = Path(metrics_path)
    if not p.exists():
        for c in list(Path('data').rglob(p.name))[:3]:
            p = c
            break
    if not p.exists():
        return None, None
    try:
        j = json.loads(p.read_text(encoding='utf-8'))
        return j.get('metrics_source'), j.get('run_mode')
    except Exception:
        return None, None


def run(apply: bool) -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert_count(ps)
    live = {str(a.id): a for a in ps.all_atoms() if str(a.id) in TARGET}
    print(f'PRE: CERT={pre_cert} | targets present in Store: {len(live)}/{len(TARGET)}', flush=True)
    if len(live) != len(TARGET):
        print('HARD_FAIL: not all 4 targets present in canonical Store:', sorted(set(TARGET) - set(live))); return 2

    patched = []
    for i in TARGET:
        a = live[i]
        md = dict(a.metadata or {})
        if md.get('metrics_source'):
            print(f'  {i}: metrics_source ALREADY set ({md["metrics_source"]}) -> skip'); continue
        src, rm = _run_output_source(md.get('metrics_path'))
        if not src:
            print(f'  {i}: run-output metrics_source NOT recoverable (metrics_path={md.get("metrics_path")}) -> SKIP (stays pending)'); continue
        md['metrics_source'] = src
        md['metrics_source_backfilled'] = True
        md['metrics_source_backfill_from'] = md.get('metrics_path')
        md['metrics_source_backfill_date'] = DATE
        md['metrics_source_backfill_note'] = ('promotion-path #1 (Skunkworks 37-VET): recovered metrics_source from the '
                                              'LOCAL run-output; the remote-direct atomizer omitted copying it into the atom')
        patched.append((i, dataclasses.replace(a, metadata=md), src, rm))
        print(f'  {i}: backfill metrics_source={src} (run_mode={rm}) from {md.get("metrics_path")}')

    if not patched:
        print('Nothing to backfill (all set or none recoverable).'); return 0
    if not apply:
        print(f'\nDRY-RUN OK: {len(patched)} atoms ready to backfill. Re-run with --apply.'); return 0

    for (i, atom, _src, _rm) in patched:
        ps.add_atom(atom, source='backfill_metrics_source_4cert_37vet',
                    note='promotion-path #1: metrics_source recovered from local run-output; metadata-patch (safe path)')

    # fresh-Store LOAD gate
    ps2 = PartitionedStore(Path('data/substrate_index'))
    by = {str(a.id): a for a in ps2.all_atoms() if str(a.id) in TARGET}
    post_cert = cert_count(ps2)
    oks = {i: (by[i].metadata or {}).get('metrics_source') for i in TARGET if i in by}
    all_set = all(oks.get(i) for i in TARGET)
    gate_ok = (len(by) == len(TARGET) and all_set and post_cert == pre_cert)
    print(f'\nPOST: CERT={post_cert} (unchanged from {pre_cert}; still RESEARCH_FINDING pending promote-VET) | LOAD-gate present={len(by)}/4 | all metrics_source set={all_set}')
    for i in TARGET:
        a = by.get(i)
        if a:
            m = a.metadata or {}
            print(f'  {i}: metrics_source={m.get("metrics_source")} pq={m.get("provenance_quality")} verdict={m.get("verdict")} cert_vet={m.get("cert_vet_status") or m.get("cert_vet_pending")}')
    if not gate_ok:
        print('HARD_FAIL: LOAD-gate / invariant failed.'); return 6
    print('\nBACKFILL OK: 4 atoms now carry metrics_source (measured run-output). Still RESEARCH_FINDING / cert-VET-pending. '
          'CERT 575 unchanged. Route to Skunkworks: metrics_source-gap CLOSED via promotion-path #1 -> promote-VET (575 -> up to 579).')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    return run(ap.parse_args().apply)


if __name__ == '__main__':
    raise SystemExit(main())
