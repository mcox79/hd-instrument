"""ORCHESTRATOR independent post-apply LOAD-gate for the I1 de-integration (dual-apply seam check).
Read-only. Reuses the de-integration tool's exact counting logic. Verifies the CURRENT working-tree
Store state is coherent after the Exp-Dev(committed) + Skunkworks(uncommitted) applies to the math/T3
partition. ASCII; no Date.now.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

ATOMS = [
    'T3/EXP_exp_hp12_v1_demo_scale_10k_facts_v1',
    'T3/EXP_substrate_codebook_collapse_monitoring_recovery_v1',
]
EXPECT_INTEGRATED = 457
EXPECT_CERT = 587
EXPECT_AXIOM = 206


def cert_count(atoms):
    return sum(1 for a in atoms if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def integrated_count(atoms):
    return sum(1 for a in atoms if (a.metadata or {}).get('capint_integrated') is True)


def axiom_term_count(atoms):
    return sum(1 for a in atoms
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def main() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    # Materialize once -- the load itself is the NULL-seam / unloadable check (throws if corrupt).
    atoms = list(ps.all_atoms())
    total = len(atoms)
    cert = cert_count(atoms)
    integ = integrated_count(atoms)
    axiom = axiom_term_count(atoms)
    print(f'LOAD OK: all_atoms={total} (no NULL-seam / unloadable)')
    print(f'CERT={cert} (expect {EXPECT_CERT})')
    print(f'capint_integrated={integ} (expect {EXPECT_INTEGRATED})')
    print(f'axiom={axiom} (expect {EXPECT_AXIOM})')

    by_id = {str(a.id): a for a in atoms}
    atoms_ok = True
    for aid in ATOMS:
        a = by_id.get(aid)
        if a is None:
            print(f'  {aid}: NOT FOUND -> FAIL'); atoms_ok = False; continue
        md = a.metadata or {}
        ci = md.get('capint_integrated')
        pq = md.get('provenance_quality')
        ok = (ci is False and pq == 'SMOKE_ONLY')
        atoms_ok = atoms_ok and ok
        print(f'  {aid}: capint_integrated={ci} (expect False) pq={pq} (expect SMOKE_ONLY untouched) -> {"OK" if ok else "FAIL"}')

    gate = (cert == EXPECT_CERT and integ == EXPECT_INTEGRATED and axiom == EXPECT_AXIOM and atoms_ok)
    print(f'\nGATE: {"PASS" if gate else "FAIL"} '
          f'(load-clean + integrated=={EXPECT_INTEGRATED} + CERT=={EXPECT_CERT} + axiom=={EXPECT_AXIOM} + both atoms False/SMOKE_ONLY)')
    return 0 if gate else 7


if __name__ == '__main__':
    raise SystemExit(main())
