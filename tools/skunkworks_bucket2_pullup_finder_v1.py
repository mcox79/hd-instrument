"""Skunkworks 2026-06-20 -- BUCKET-2 PULL-UP FINDER (read-only): for the certify-the-backlog COVERAGE half.

Finds enabling-capability operating-points whose BEST existing evidence is SUB-cert (no cert-grade sibling) =
the iso-protocol cert-PULL-UP candidates (bucket-2 source 2; distinct from the OOM-INCOMPLETE rebuild source).
Groups an enabling theme's experiment_records by a normalized capability-STEM (strips _vN/_nN/_seedN/_dN/_lN/
suffixes), finds each group's best grade, and flags groups whose best is sub-cert AND that have a PASS member
(real evidence worth pulling up, not legacy junk).

HONEST CAVEATS: (1) stem-grouping is a HEURISTIC (id-based; a capability may split across stems or merge
distinct ones) -- the cert-owner + Director PRIORITIZE which are canonical, this just surfaces candidates;
(2) most candidates are n=1 smoke -> the pull-up COST is a multi-seed iso-protocol re-run each (11th rule);
(3) grade = Store pq (verify-the-referent by construction). Read-ONLY. ASCII. --json optional.
"""
from __future__ import annotations
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

GRADE = {'CERT_CHAIN_GRADE': 7, 'MEASURED_MECHANISM': 6, 'COST_MODEL': 5, 'RESEARCH_FINDING': 4,
         'SMOKE_ONLY': 3, 'LEGACY_EXCERPT': 2, 'UNVERIFIED': 1, 'ARCHIVE': 0, 'INVENTORY_NON_CERT': 0,
         'None': 0, None: 0}
THEMES = {
    'composition': ('composition', 'b2xb4', 'multi_hop', 'compose', 'q_b1', 'chain_depth', 'cleanup_mediated'),
    'capacity': ('capacity', 'm_critical', 'readout', 'n_scaling', 'sweet_spot', 'modern_hopfield', 'm_crit'),
    'sparse': ('sparse', 'alpha', 'crosstalk'),
    'knowledge_graph': ('fb15k237', 'kg_', '_kg', 'knowledge_graph', 'khop', 'k_hop', 'triple', 'traversal'),
    'continual': ('continual', '30day', '90day', 'lifelong', 'forgetting'),
    'drift': ('drift', 'kappa3', 'distribution_shift', 'covariate', 'kappa_3'),
}


def kn(a):
    return a.kind.value if hasattr(a.kind, 'value') else str(a.kind)


def pq(a):
    return (a.metadata or {}).get('provenance_quality')


def opstem(aid):
    s = str(aid).split('/')[-1]
    for pat in (r'_n\d+', r'_v\d+', r'_seed\d+', r'_d\d+', r'_[lL]\d+', r'_\d+$'):
        s = re.sub(pat, '', s)
    return re.sub(r'_(smoke|gpu|cpu|full|rerun|rescue)$', '', s)


def find(atoms, theme, kws):
    recs = [a for a in atoms if kn(a) == 'experiment_record' and any(k in str(a.id).lower() for k in kws)]
    groups = defaultdict(list)
    for a in recs:
        groups[opstem(a.id)].append(a)
    out = []
    for stem, mem in groups.items():
        best = max(mem, key=lambda a: GRADE.get(pq(a), 0))
        if GRADE.get(pq(best), 0) >= 7:
            continue  # has a cert member -> already covered
        has_pass = any('PASS' in ((m.metadata or {}).get('verdict') or '').upper() for m in mem)
        out.append({'stem': stem, 'best_grade': str(pq(best)), 'best_verdict': str((best.metadata or {}).get('verdict')),
                    'best_id': str(best.id).split('/')[-1], 'n_members': len(mem), 'has_pass': has_pass})
    out.sort(key=lambda d: (-GRADE.get(d['best_grade'], 0), -d['n_members']))
    return recs, groups, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--theme', default=None, help='one theme (default: all enabling themes)')
    ap.add_argument('--show', type=int, default=15)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    ps = PartitionedStore(Path('data/substrate_index'))
    atoms = list(ps.all_atoms())
    themes = {args.theme: THEMES[args.theme]} if args.theme else THEMES
    result = {}
    for theme, kws in themes.items():
        recs, groups, cands = find(atoms, theme, kws)
        passcands = [c for c in cands if c['has_pass']]
        result[theme] = {'records': len(recs), 'stem_groups': len(groups), 'subcert_best': len(cands),
                         'with_pass': len(passcands), 'candidates': passcands}
    if args.json:
        import json as _json
        print(_json.dumps(result, indent=2))
        return 0
    for theme, r in result.items():
        print('=== %s: %d records / %d groups / %d sub-cert-best / %d with-PASS (pull-up candidates) ===' %
              (theme, r['records'], r['stem_groups'], r['subcert_best'], r['with_pass']))
        for c in r['candidates'][:args.show]:
            print('   [%-14s %-10s] n=%d  %s' % (c['best_grade'], c['best_verdict'][:10], c['n_members'], c['best_id'][:58]))
        if len(r['candidates']) > args.show:
            print('   ... +%d more with-PASS' % (len(r['candidates']) - args.show))
    print('NOTE: heuristic stem-grouping; cert-owner+Director PRIORITIZE canonical vs exploratory; pull-up = multi-seed re-run.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
