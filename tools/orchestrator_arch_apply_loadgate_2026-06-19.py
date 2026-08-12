"""ORCHESTRATOR independent post-apply LOAD-gate for the CORRECTED architecture Track-A apply.
Read-only. Compares the current (post-apply) Store to the pre-apply baseline snapshot.
Usage: python orchestrator_arch_apply_loadgate_2026-06-19.py <expected_added_N>
  where N = the count Exp-Dev pre-announces (the resolver dry-run clean-set, e.g. 30 or 32).
Checks: Store loads clean (no NULL-seam) + integrated == baseline+N + architecture-domain == N
+ NO other domain shrank (the already-integrated-clobber failure mode) + total atoms unchanged.
ASCII; no Date.now.
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

BASELINE_PATH = 'data/.metrics_sync/arch_apply_preapply_baseline.json'


def main() -> int:
    if len(sys.argv) < 2:
        print('usage: gate.py <expected_added_N>'); return 2
    n = int(sys.argv[1])
    base = json.loads(Path(BASELINE_PATH).read_text())
    base_dom = base['domains']
    base_int = base['integrated']
    base_total = base['total']

    ps = PartitionedStore(Path('data/substrate_index'))
    atoms = list(ps.all_atoms())  # load == NULL-seam / unloadable check
    total = len(atoms)
    integ = 0
    dom = Counter()
    for a in atoms:
        md = a.metadata or {}
        if md.get('capint_integrated') is True:
            integ += 1
            dom[str(md.get('capint_primary_domain'))] += 1

    print(f'LOAD OK: total={total} (baseline {base_total})')
    print(f'capint_integrated={integ} (expect baseline+N = {base_int}+{n} = {base_int + n})')
    print(f'architecture-domain={dom.get("architecture", 0)} (expect N={n})')

    # No other domain may shrink (clobber => a domain loses atoms to architecture).
    shrunk = []
    for d, c in base_dom.items():
        if d == 'architecture':
            continue
        post = dom.get(d, 0)
        if post < c:
            shrunk.append(f'{d}: {c}->{post}')
    if shrunk:
        print('  DOMAIN SHRINK (clobber!) ->', '; '.join(shrunk))
    else:
        print('  no non-architecture domain shrank (already-integrated guard held)')

    total_ok = (total == base_total)
    integ_ok = (integ == base_int + n)
    arch_ok = (dom.get('architecture', 0) == n)
    no_clobber = (len(shrunk) == 0)
    gate = total_ok and integ_ok and arch_ok and no_clobber
    print(f'\nGATE: {"PASS" if gate else "FAIL"} '
          f'(load-clean + total-unchanged={total_ok} + integrated==+{n}={integ_ok} + architecture=={n}={arch_ok} + no-clobber={no_clobber})')
    if not gate:
        print('  NOTE: if N differs from Exp-Dev pre-announce, re-run with the correct N before concluding.')
    return 0 if gate else 7


if __name__ == '__main__':
    raise SystemExit(main())
