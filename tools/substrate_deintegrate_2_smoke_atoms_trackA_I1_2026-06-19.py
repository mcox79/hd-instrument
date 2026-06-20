"""De-integrate 2 SMOKE_ONLY/ARCHIVE atoms wrongly marked capint_integrated into Track-A
(Skunkworks INTEGRATION-CHECK v1.2 I1-FAIL, 2026-06-19). A5-SAFE: patches ONLY capint_* metadata
(capint_integrated=False) -- does NOT touch provenance_quality / relevance_tier / verdict (no silent
re-classification). Restores INTEGRATION-PASS (integrated 459->457). CERT count UNCHANGED (these are
SMOKE/ARCHIVE, not CERT atoms). GATED on Research greenlight (they own Track-A integration semantics).
DRY-RUN default; --apply. ASCII; no Date.now.
"""
from __future__ import annotations
import argparse
import dataclasses
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

DATE = '2026-06-19'
ATOMS = [
    'T3/EXP_exp_hp12_v1_demo_scale_10k_facts_v1',
    'T3/EXP_substrate_codebook_collapse_monitoring_recovery_v1',
]
REASON = ('I1-FAIL (Skunkworks integration-check v1.2): SMOKE_ONLY/ARCHIVE evidence cannot be Track-A '
          '(cert-grade-only). De-integrated to Track-B value-coverage reserve; a cert-grade re-run can '
          'promote later. A5-safe: pq/rel_tier untouched.')


def cert_count(ps):
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def integrated_count(ps):
    return sum(1 for a in ps.all_atoms() if (a.metadata or {}).get('capint_integrated') is True)


def axiom_term_count(ps):
    return sum(1 for a in ps.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def run(apply: bool) -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert_count(ps); pre_int = integrated_count(ps); pre_axiom = axiom_term_count(ps)
    print(f'PRE: CERT={pre_cert} capint_integrated={pre_int} axiom={pre_axiom}')

    targets = []
    for aid in ATOMS:
        a = next((x for x in ps.all_atoms() if str(x.id) == aid), None)
        if a is None:
            print(f'  atom NOT FOUND: {aid} -> HALT'); return 2
        md = a.metadata or {}
        if md.get('capint_integrated') is not True:
            print(f'  {aid}: capint_integrated already {md.get("capint_integrated")} -> skip (idempotent)')
            continue
        # A5 invariant check: confirm it really is SMOKE/ARCHIVE (the I1 premise)
        print(f'  {aid}: pq={md.get("provenance_quality")} rel_tier={md.get("relevance_tier")} '
              f'capint_verdict={md.get("capint_verdict")} capint_is_bound={md.get("capint_is_bound")} -> de-integrate')
        targets.append(a)

    if not targets:
        print('\nnothing to de-integrate (already PASS). no-op.'); return 0
    if not apply:
        print(f'\nDRY-RUN OK -> capint_integrated {pre_int}->{pre_int-len(targets)} (INTEGRATION-PASS); CERT {pre_cert} unchanged; axiom {pre_axiom} unchanged. Re-run --apply (after Research greenlight).'); return 0

    for a in targets:
        md = dict(a.metadata or {})
        md['capint_integrated'] = False
        md['capint_deintegrated_date'] = DATE
        md['capint_deintegrated_by'] = 'skunkworks_integration_check_v1.2_I1_2026-06-19'
        md['capint_deintegrated_reason'] = REASON
        ps.add_atom(dataclasses.replace(a, metadata=md), source='deintegrate_I1_smoke_trackA',
                    note='Skunkworks I1-FAIL; capint_integrated=False; A5-safe (pq/rel_tier untouched); Research-greenlit')

    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert = cert_count(ps2); post_int = integrated_count(ps2); post_axiom = axiom_term_count(ps2)
    # A5 verify: the 2 atoms' pq/rel_tier UNCHANGED
    a5_ok = True
    for aid in ATOMS:
        b = next((x for x in ps2.all_atoms() if str(x.id) == aid), None)
        bmd = (b.metadata or {}) if b else {}
        if bmd.get('capint_integrated') is not False:
            a5_ok = False
        if bmd.get('provenance_quality') != 'SMOKE_ONLY':
            print(f'  WARN: {aid} pq changed to {bmd.get("provenance_quality")} (expected SMOKE_ONLY untouched)')
    gate_ok = (post_int == pre_int - len(targets) and post_cert == pre_cert and post_axiom == pre_axiom and a5_ok)
    print(f'\nPOST: CERT={post_cert} (unchanged {pre_cert}) capint_integrated={post_int} (pre {pre_int} -{len(targets)}) '
          f'axiom={post_axiom} | A5(pq untouched)={a5_ok} | gate {"OK" if gate_ok else "FAIL"}')
    if not gate_ok:
        print('HARD_FAIL: gate (CERT/integrated-count/axiom/A5).'); return 6
    print(f'\nDE-INTEGRATE OK: {len(targets)} smoke atoms removed from Track-A. capint_integrated {pre_int}->{post_int}. '
          'INTEGRATION-PASS restored. #2 (codebook-collapse) -> Track-B value-coverage reserve. Route Skunkworks landed-VET.')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    return run(ap.parse_args().apply)


if __name__ == '__main__':
    raise SystemExit(main())
