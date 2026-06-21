"""Skunkworks 2026-06-21 -- closure-audit FIX: the learned-key collapse MM atom
(T3/EXP_dense_KV_learned_key_calibration_v1) had a DANGLING composes_with ref to the flagship PROBE cell
(...PROBE_whiten_before_topk_v1) which was NEVER atomized -- only the LBUILD was (c13268e2). My own 5-atom closure-audit
caught it. Fix = repoint PROBE -> the existing T3/EXP_flagship_sparse_projected_KV_LBUILD_v1 (the flagship whiten-before-topk
work lives there). remove_atom + re-add the CORRECTED atom (imported from the now-fixed atomize tool).
A5: PRE CERT=583/atoms=177264 -> POST 583/177264 UNCHANGED (net 0: -1 remove +1 add); axiom 206; cap_pres 6/6; no dangling; reloads.
"""
from __future__ import annotations
import sys, importlib.util
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

# import the corrected ATOM from the (now-fixed) atomize tool
spec = importlib.util.spec_from_file_location("atz", "tools/skunkworks_atomize_dense_KV_learned_key_collapse_MM_whitening_revival_2026-06-21.py")
atz = importlib.util.module_from_spec(spec); spec.loader.exec_module(atz)
ATOM = atz.ATOM


def cert(p):
    return sum(1 for a in p.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
def axiom(p):
    return sum(1 for a in p.all_atoms()
               if str(a.corpus.name)=='MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE','TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra)>=3 and 'oeis' not in str(a.id).lower() and not str(a.id).startswith('T3/wikidata_'))


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    allids = set()
    for a in ps.all_atoms():
        allids.add(str(a.id)); allids.add(str(a.id).split('::')[-1])
    pre_cert, pre_ax = cert(ps), axiom(ps); pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax}")
    if pre_cert != 583 or pre_ax != 206:
        print("PRE-GATE FAIL. HALT."); return 1
    # confirm the corrected composes_with now resolves
    cw = (ATOM.metadata or {}).get('composes_with', [])
    dangling = [r for r in cw if r not in allids]
    print(f"corrected composes_with: {cw}")
    print(f"dangling after fix: {dangling}")
    if dangling:
        print("STILL DANGLING -- HALT (fix the ref first)."); return 1
    # remove the stale atom + re-add the corrected one
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed:
        ps.remove_atom(ATOM.qualified_id); print(f"  REMOVED stale: {ATOM.id}")
    ps.add_atom(ATOM, source='skunkworks_fix_learned_key_dangling_composes_with_2026_06_21', note='closure-audit fix: PROBE->LBUILD dangling composes_with')
    print(f"  RE-ADDED corrected: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax = cert(ps2), axiom(ps2); post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id)
    allids2 = set()
    for a in ps2.all_atoms():
        allids2.add(str(a.id)); allids2.add(str(a.id).split('::')[-1])
    cw2 = (a2.metadata or {}).get('composes_with', []) if a2 else []
    dangling2 = [r for r in cw2 if r not in allids2]
    bad = (a2 is None) or (a2.algebra is not None) or ((a2.metadata or {}).get('provenance_quality')!='MEASURED_MECHANISM') or dangling2
    print(f"POST: atoms={post_atoms} (expect {pre_atoms}) CERT={post_cert} (expect 583) axiom={post_ax} (expect 206) dangling={dangling2}")
    gate = (post_cert==583 and post_ax==206 and post_atoms==pre_atoms and not bad)
    print("GATE:", "OK -- dangling composes_with FIXED (PROBE->LBUILD), CERT 583 + atoms UNCHANGED, no dangling" if gate else "FAIL")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
