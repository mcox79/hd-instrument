"""Skunkworks 2026-06-20 -- BACKLOG-CERTIFICATION LANDSCAPE (read-only).

USER directive: "going through all the experiments and certifying them / prioritizing the truly
enabling is key, then we can focus on new things." Orchestrator's run-status inventory established
1256/1542 backlog runs are GENUINE (completed-with-verdict). This tool answers the cert-owner's
next question: of the existing experiment_record atoms, what is the provenance_quality (cert-tier)
DISTRIBUTION, and which ENABLING-themed records are genuine-but-not-yet-cert-graded (= the pull-up
candidates Research prioritizes)?

Read-ONLY. ASCII. Prints a report + optional --json.

Cert tiers (provenance_quality): CERT_CHAIN_GRADE / MEASURED_MECHANISM / COST_MODEL /
RESEARCH_FINDING / SMOKE_ONLY / LEGACY_EXCERPT / ARCHIVE / INVENTORY_NON_CERT / (None).

Enabling themes (per the re-weighted value-coverage ENABLING_CORE): composition / capacity /
sparse / knowledge_graph / continual / drift. A genuine enabling record at a sub-cert tier is a
pull-up candidate.
"""
from __future__ import annotations
import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore


def kname(a):
    return a.kind.value if hasattr(a.kind, 'value') else str(a.kind)


# enabling-theme -> id/metadata substrings (lowercased match)
ENABLING_THEMES = {
    'composition': ('composition', 'b2xb4', 'multi_hop', 'multihop', 'compose', 'q_b1', 'chain_depth', 'cleanup_mediated'),
    'capacity': ('capacity', 'm_critical', 'readout', 'n_scaling', 'sweet_spot', 'modern_hopfield'),
    'sparse': ('sparse', 'alpha', 'crosstalk'),
    'knowledge_graph': ('fb15k237', 'kg_', '_kg', 'knowledge_graph', 'khop', 'k_hop', 'triple', 'traversal'),
    'continual': ('continual', '30day', '90day', 'lifelong', 'forgetting'),
    'drift': ('drift', 'kappa3', 'distribution_shift', 'covariate'),
}

# tiers that are NOT yet load-bearing cert (pull-up candidates if enabling + genuine)
SUBCERT_TIERS = {'MEASURED_MECHANISM', 'RESEARCH_FINDING', 'SMOKE_ONLY', 'LEGACY_EXCERPT', None, 'None'}


def themes_of(a):
    blob = (str(a.id) + ' ' + ' '.join(str(v) for v in (a.metadata or {}).values() if isinstance(v, (str, int, float)))).lower()
    return [t for t, subs in ENABLING_THEMES.items() if any(s in blob for s in subs)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--kind', default='experiment_record', help='atom kind to inventory (default experiment_record)')
    args = ap.parse_args()

    ps = PartitionedStore(Path('data/substrate_index'))
    atoms = list(ps.all_atoms())

    def pq(a):
        return (a.metadata or {}).get('provenance_quality')

    # overall cert-tier distribution (all kinds)
    overall = Counter(str(pq(a)) for a in atoms)

    # target-kind distribution
    target = [a for a in atoms if kname(a) == args.kind]
    target_pq = Counter(str(pq(a)) for a in target)

    # enabling-themed records: tier x theme
    enab = [a for a in target if themes_of(a)]
    enab_by_theme_tier = defaultdict(Counter)
    pullup = defaultdict(list)  # theme -> list of (id, tier) for genuine sub-cert enabling records
    for a in enab:
        ts = themes_of(a)
        tier = pq(a)
        for t in ts:
            enab_by_theme_tier[t][str(tier)] += 1
            if tier in SUBCERT_TIERS:
                pullup[t].append((str(a.id), str(tier)))

    if args.json:
        import json as _json
        out = {
            'kind': args.kind,
            'overall_pq_distribution': dict(overall),
            'target_kind_count': len(target),
            'target_pq_distribution': dict(target_pq),
            'enabling_themed_count': len(enab),
            'enabling_by_theme_tier': {t: dict(c) for t, c in enab_by_theme_tier.items()},
            'pullup_candidate_counts': {t: len(v) for t, v in pullup.items()},
        }
        print(_json.dumps(out, indent=2))
        return 0

    print('=' * 78)
    print('BACKLOG-CERTIFICATION LANDSCAPE v1 (read-only) -- kind=%s' % args.kind)
    print('-' * 78)
    print('OVERALL provenance_quality distribution (all %d atoms):' % len(atoms))
    for tier, n in overall.most_common():
        print('  %-22s %6d' % (tier, n))
    print('-' * 78)
    print('%s provenance_quality distribution (%d atoms):' % (args.kind, len(target)))
    for tier, n in target_pq.most_common():
        print('  %-22s %6d' % (tier, n))
    print('-' * 78)
    print('ENABLING-themed %s (%d atoms) -- tier x theme:' % (args.kind, len(enab)))
    for t in ENABLING_THEMES:
        c = enab_by_theme_tier.get(t)
        if c:
            print('  %-16s %s' % (t, dict(c)))
    print('-' * 78)
    print('PULL-UP CANDIDATES (genuine enabling records at sub-cert tier):')
    for t in ENABLING_THEMES:
        lst = pullup.get(t, [])
        print('  %-16s %d candidates' % (t, len(lst)))
        for aid, tier in lst[:6]:
            print('      [%s] %s' % (tier, aid))
        if len(lst) > 6:
            print('      ... +%d more' % (len(lst) - 6))
    print('=' * 78)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
