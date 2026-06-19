"""Promote T3/EXP_a8_continual_writes_no_catastrophic_forgetting_v1 SMOKE_ONLY -> CERT_CHAIN_GRADE
(Skunkworks formal verdict-VET PASS 2026-06-19; CERT 585 -> 586). FIRST 104-queue value-coverage
pull-up cert-graded. Reads the CONSUMED local_cpu_queue full-run metrics.json, reproduce-checks the
key invariants (HARD_PASS / full / n=5 / X=0.30 / capacity_stress_ok / region_max_std<=0.05), and
carries Skunkworks's LOCKED honest-scope. SAFE metadata patch + fresh-Store LOAD gate; MATH
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
ATOM = 'T3/EXP_a8_continual_writes_no_catastrophic_forgetting_v1'
METRICS = 'data/exp_a8_continual_writes_no_catastrophic_forgetting_v1/metrics.json'
HONEST_SCOPE = ('no catastrophic forgetting up to alpha=0.30 (the MEASURED cliff); seed-reproducibility '
                'verified IN the no-forgetting region (region_std=0.000); cliff-edge variance at '
                'alpha>=0.50 is the expected phase-transition, OUTSIDE the no-forgetting claim')


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
    # reproduce-check the cert-load-bearing invariants from the consumed full run
    checks = {
        'verdict==HARD_PASS': m.get('verdict') == 'HARD_PASS',
        'run_mode==full': m.get('run_mode') == 'full',
        'n_seeds==5': m.get('n_seeds') == 5,
        'X==0.30': abs((det.get('no_forget_boundary_X') or 0) - 0.30) < 1e-6,
        'capacity_stress_ok': det.get('capacity_stress_ok') is True,
        'region_std<=0.05': (det.get('region_max_std') if det.get('region_max_std') is not None else 1) <= 0.05,
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
    md['provenance_quality'] = 'CERT_CHAIN_GRADE'
    md['verdict'] = 'HARD_PASS'
    md['cert_vet_status'] = 'cert_promoted'
    md['cert_promoted_date'] = DATE
    md['cert_promoted_by_vet'] = 'skunkworks_continual_writes_formal_VET_2026-06-19'
    md['cert_promoted_from'] = 'SMOKE_ONLY'
    md['metrics_path'] = METRICS
    md['honest_scope'] = HONEST_SCOPE
    md['key_metrics'] = {
        'no_forget_boundary_X': det.get('no_forget_boundary_X'),
        'capacity_stress_ok': det.get('capacity_stress_ok'),
        'acc_max_alpha': det.get('acc_max_alpha'),
        'region_max_std': det.get('region_max_std'),
        'global_max_std': det.get('global_max_std'),
        'mean_acc': det.get('mean_acc'),
    }
    md['rerun_reproduced'] = True
    md['rerun_reproduce_note'] = ('local_cpu_queue full run (n=5) reproduces the dry-run EXACTLY: HARD_PASS, '
                                  'X=0.30 (2.2x the naive Hopfield alpha_c=0.138), cliff found (acc 0.50->0.16'
                                  '->0.10), capacity-stress verified (acc@1.5=0.10, not degenerate); region-'
                                  'scoped seed-reproduce (region_std=0.000) per Skunkworks adjudication. '
                                  'measurement-class -> CERT (discriminating-regime validated end-to-end).')
    md['relevance_tier'] = md.get('relevance_tier') or 'ACTIVE'
    atom = dataclasses.replace(a, metadata=md)
    print(f'PRE: CERT={pre_cert} axiom={pre_axiom}')
    print(f'  {ATOM}: SMOKE_ONLY -> CERT_CHAIN_GRADE (verdict HARD_PASS; honest-scope locked)')
    if not apply:
        print(f'\nDRY-RUN OK -> CERT {pre_cert}->{pre_cert+1}. Re-run --apply.'); return 0
    ps.add_atom(atom, source='promote_continual_writes_CERT586', note='Skunkworks formal-VET PASS; SMOKE->CERT; first 104-queue pull-up; region-scoped HARD_PASS')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert = cert_count(ps2); post_axiom = axiom_term_count(ps2)
    b = next((x for x in ps2.all_atoms() if str(x.id) == ATOM), None)
    pq = (b.metadata or {}).get('provenance_quality') if b else None
    gate_ok = (pq == 'CERT_CHAIN_GRADE' and post_cert == pre_cert + 1 and post_axiom == pre_axiom)
    print(f'\nPOST: CERT={post_cert} (pre {pre_cert} +1) axiom={post_axiom} | pq={pq} | LOAD-gate {"OK" if gate_ok else "FAIL"}')
    if not gate_ok:
        print('HARD_FAIL: LOAD-gate/CERT (possible concurrent MATH write -> re-snapshot + retry).'); return 6
    print(f'\nPROMOTE OK: {ATOM} CERT_CHAIN_GRADE. CERT {pre_cert} -> {post_cert}. FIRST 104-queue value-coverage pull-up. Route for Skunkworks landed-VET.')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    return run(ap.parse_args().apply)


if __name__ == '__main__':
    raise SystemExit(main())
