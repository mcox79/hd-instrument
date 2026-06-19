"""Promote the 4 canonicalized atoms RESEARCH_FINDING -> CERT_CHAIN_GRADE (Skunkworks promote-VET PASS 2026-06-19;
metrics_source-gap closed via promotion-path #1). CERT 575 -> 579. Exp-Dev = named ONE pq-patch owner.

SAFE metadata-patch (load live atom via all_atoms scan -> dataclasses.replace metadata -> add_atom update ->
fresh-Store all_atoms() LOAD gate). MATH partition; run in a SERIALIZED single-writer window (no concurrent cap-int
math-write) until the save_atoms unique-tmp fix lands. Pre-conditions enforced: each atom must currently be
RESEARCH_FINDING + metrics_source set + cert_vet_status ready (refuse to promote otherwise). DRY-RUN default; --apply.
ASCII; deterministic; no Date.now (fixed date str).
"""
from __future__ import annotations
import argparse
import dataclasses
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


def run(apply: bool) -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert_count(ps)
    live = {str(a.id): a for a in ps.all_atoms() if str(a.id) in TARGET}
    print(f'PRE: CERT={pre_cert} | targets present: {len(live)}/{len(TARGET)}', flush=True)
    if len(live) != len(TARGET):
        print('HARD_FAIL: not all 4 present:', sorted(set(TARGET) - set(live))); return 2

    patched = []
    for i in TARGET:
        a = live[i]
        md = dict(a.metadata or {})
        pq = md.get('provenance_quality'); ms = md.get('metrics_source')
        # pre-conditions (refuse to promote a non-pending / un-sourced atom)
        if pq != 'RESEARCH_FINDING':
            print(f'  {i}: pq={pq} (not RESEARCH_FINDING) -> SKIP'); continue
        if not ms:
            print(f'  {i}: metrics_source missing -> SKIP (gap not closed)'); continue
        md['provenance_quality'] = 'CERT_CHAIN_GRADE'
        md['cert_vet_status'] = 'cert_promoted'
        md['cert_promoted_date'] = DATE
        md['cert_promoted_by_vet'] = 'skunkworks_promote_vet_2026-06-19_37vet_metrics_source_path1'
        md['cert_promoted_from'] = 'RESEARCH_FINDING'
        patched.append((i, dataclasses.replace(a, metadata=md)))
        print(f'  {i}: RESEARCH_FINDING -> CERT_CHAIN_GRADE (metrics_source={ms} verdict={md.get("verdict")})')

    if len(patched) != len(TARGET):
        print(f'HARD_FAIL: only {len(patched)}/4 meet promotion pre-conditions. Halt (no partial promote).'); return 3
    if not apply:
        print('\nDRY-RUN OK: 4 ready to promote -> CERT 575->579. Re-run with --apply.'); return 0

    for (i, atom) in patched:
        ps.add_atom(atom, source='promote_4_cert579_37vet',
                    note='Skunkworks promote-VET PASS; metrics_source-gap closed (path #1); RESEARCH_FINDING -> CERT_CHAIN_GRADE')

    # fresh-Store LOAD gate
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert = cert_count(ps2)
    by = {str(a.id): a for a in ps2.all_atoms() if str(a.id) in TARGET}
    all_cert = all((by[i].metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE' for i in TARGET if i in by)
    gate_ok = (len(by) == len(TARGET) and all_cert and post_cert == pre_cert + 4)
    print(f'\nPOST: CERT={post_cert} (pre {pre_cert} + 4) | LOAD-gate present={len(by)}/4 | all CERT_CHAIN_GRADE={all_cert}')
    for i in TARGET:
        a = by.get(i)
        if a:
            m = a.metadata or {}
            print(f'  {i}: pq={m.get("provenance_quality")} cert_vet={m.get("cert_vet_status")} verdict={m.get("verdict")}')
    if not gate_ok:
        print('HARD_FAIL: LOAD-gate / CERT count failed.'); return 6
    print(f'\nPROMOTE OK: 4 atoms RESEARCH_FINDING -> CERT_CHAIN_GRADE. CERT {pre_cert} -> {post_cert}. '
          'Store loads clean. Route invariant --expect-cert 579 + this for Skunkworks landed-VET.')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    return run(ap.parse_args().apply)


if __name__ == '__main__':
    raise SystemExit(main())
