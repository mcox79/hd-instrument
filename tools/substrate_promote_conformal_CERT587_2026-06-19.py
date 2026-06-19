"""Promote T3/EXP_conformal_splitcp_cpu_v1 -> CERT_CHAIN_GRADE as a MIDDLE_BAND BOUNDED capability
(Skunkworks conformal verdict-VET PASS 2026-06-19; CERT 586 -> 587). 2nd value-coverage pull-up (an
honest BOUND: tight on multi-class, loose on binary). Reads the landed full-run metrics.json,
reproduce-checks (MIDDLE_BAND / full / n=5 / tight includes ag_news+atis / guarantee_break False),
carries Skunkworks's LOCKED honest-scope + is_bound=True. SAFE metadata patch + fresh-Store LOAD gate;
single-writer window. DRY-RUN default; --apply. ASCII; no Date.now.
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
ATOM = 'T3/EXP_conformal_splitcp_cpu_v1'
METRICS = 'data/exp_conformal_splitcp_cpu_v1/metrics.json'
HONEST_SCOPE = ('substrate-classical + APS split-conformal: distribution-free coverage guarantee holds '
                'by-construction (cov>=0.93) on all tested tasks; set-size MEANINGFULLY TIGHT (<=0.5*L) on '
                'MULTI-class tasks (ag_news 0.44L, atis_intent 0.26L); binary sst2 structurally LOOSE '
                '(0.5L=1.0 requires confident single-class). A BOUND, not a clean win (is_bound=True).')


def cert_count(ps):
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def axiom_term_count(ps):
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def run(apply: bool) -> int:
    m = json.load(open(METRICS, encoding='utf-8'))
    det = m.get('detail', {})
    tight = det.get('tight_tasks') or []
    checks = {
        'verdict==MIDDLE_BAND': m.get('verdict') == 'MIDDLE_BAND',
        'run_mode==full': m.get('run_mode') == 'full',
        'n_seeds==5': m.get('n_seeds') == 5,
        'tight_has_agnews+atis': ('ag_news' in tight and 'atis_intent' in tight),
        'guarantee_break==False': det.get('guarantee_break') is False,
    }
    print('reproduce-check:', checks)
    if not all(checks.values()):
        print('FLAG: metrics do not match the VET-PASS invariants -> HALT (reproduce-or-flag).'); return 3

    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert_count(ps); pre_axiom = axiom_term_count(ps)
    a = next((x for x in ps.all_atoms() if str(x.id) == ATOM), None)
    if a is None:
        print('atom not found'); return 2
    md = dict(a.metadata or {})
    if md.get('provenance_quality') == 'CERT_CHAIN_GRADE':
        print('already CERT -> skip'); return 0
    md['cert_promoted_from'] = md.get('provenance_quality')   # LEGACY_EXCERPT
    md['provenance_quality'] = 'CERT_CHAIN_GRADE'
    md['verdict'] = 'MIDDLE_BAND'
    md['is_bound'] = True
    md['cert_vet_status'] = 'cert_promoted'
    md['cert_promoted_date'] = DATE
    md['cert_promoted_by_vet'] = 'skunkworks_conformal_verdict_VET_2026-06-19'
    md['metrics_path'] = METRICS
    md['honest_scope'] = HONEST_SCOPE
    md['key_metrics'] = {'per_task': det.get('per_task'), 'tight_tasks': tight,
                         'band_correction': det.get('band_correction')}
    md['rerun_reproduced'] = True
    md['rerun_reproduce_note'] = ('local_cpu_queue full run (n=5, 4 tasks) reproduces the dry-run: MIDDLE_BAND, '
                                  'coverage guarantee by-construction on all tasks (cov>=0.93, lower-bound band '
                                  'co-signed -- the >0.98 false-FAIL on atis was dropped), set-size discriminator: '
                                  'ag_news 0.44L + atis 0.26L tight, mbpp 0.53L middle, sst2 0.88L binary-loose. '
                                  'discriminating-regime (set-size-vs-random + multi-task) caught the coverage-by-'
                                  'construction tautology trap -> honest BOUND, not over-claim.')
    md['relevance_tier'] = md.get('relevance_tier') or 'ACTIVE'
    atom = dataclasses.replace(a, metadata=md)
    print(f'PRE: CERT={pre_cert} axiom={pre_axiom}')
    print(f'  {ATOM}: {md["cert_promoted_from"]} -> CERT_CHAIN_GRADE (verdict MIDDLE_BAND, is_bound=True)')
    if not apply:
        print(f'\nDRY-RUN OK -> CERT {pre_cert}->{pre_cert+1}. Re-run --apply.'); return 0
    ps.add_atom(atom, source='promote_conformal_CERT587', note='Skunkworks conformal VET PASS; MIDDLE_BAND bounded; 2nd value-coverage pull-up')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert = cert_count(ps2); post_axiom = axiom_term_count(ps2)
    b = next((x for x in ps2.all_atoms() if str(x.id) == ATOM), None)
    pq = (b.metadata or {}).get('provenance_quality') if b else None
    gate_ok = (pq == 'CERT_CHAIN_GRADE' and post_cert == pre_cert + 1 and post_axiom == pre_axiom)
    print(f'\nPOST: CERT={post_cert} (pre {pre_cert} +1) axiom={post_axiom} | pq={pq} | is_bound={(b.metadata or {}).get("is_bound")} | LOAD-gate {"OK" if gate_ok else "FAIL"}')
    if not gate_ok:
        print('HARD_FAIL: LOAD-gate/CERT (possible concurrent MATH write -> re-snapshot + retry).'); return 6
    print(f'\nPROMOTE OK: {ATOM} CERT_CHAIN_GRADE MIDDLE_BAND. CERT {pre_cert} -> {post_cert}. 2nd value-coverage pull-up. Route for Skunkworks landed-VET.')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    return run(ap.parse_args().apply)


if __name__ == '__main__':
    raise SystemExit(main())
