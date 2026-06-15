"""DECISION 86a: svd MERGE PILOT - substrate's FIRST atom-deletion workstream.

Per Director DECISION 86a:
- Delete duplicate atom math::T1/SVD (canonical singular_value_decomposition kept)
- Drop 11 SVD-incident edges (cascade via Store.remove_atom):
  * 5 self-loops-after-merge (svd <-> singular_value_decomposition)
  * 5 dup-of-canonical (canonical already carries these edges)
  * 1 backwards (svd -DEPENDS_ON-> pseudoinverse; would re-create cycle)
- Capability_preservation = 1.0 trivially (canonical carries all unique relations)
- R3 invariants must HOLD or IMPROVE
- ROLLBACK on dangling reference OR capability regression

This is the substrate's FIRST atom-deletion workstream. Atomic discipline.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore


def inventory_svd_refs(ps):
    """Return list of (src, rel_name, tgt) for every edge mentioning T1/SVD."""
    refs = []
    for src, rel, tgt in ps.iter_all_relations():
        # match T1/SVD as exact suffix or qualified form
        if (src.endswith('T1/SVD') or tgt.endswith('T1/SVD')
                or src == 'T1/SVD' or tgt == 'T1/SVD'):
            refs.append((src, rel.name, tgt))
    return refs


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'pre-pilot: {pre_atoms} atoms, {pre_rels} relations\n')

    print('=== STEP 1: atom existence verification ===')
    canonical_qid = 'math::T1/singular_value_decomposition'
    delete_qid = 'math::T1/SVD'

    has_canonical = any(f'{a.corpus.value}::{a.id}' == canonical_qid for a in ps.all_atoms())
    has_delete = any(f'{a.corpus.value}::{a.id}' == delete_qid for a in ps.all_atoms())
    print(f'  canonical {canonical_qid}: {"PRESENT" if has_canonical else "MISSING"}')
    print(f'  delete    {delete_qid}: {"PRESENT" if has_delete else "MISSING"}')
    if not (has_canonical and has_delete):
        print('  ABORT: required atoms missing')
        return

    print('\n=== STEP 2: pre-delete inventory of T1/SVD-incident edges ===')
    pre_refs = inventory_svd_refs(ps)
    for src, rel, tgt in pre_refs:
        print(f'  {src} -{rel}-> {tgt}')
    print(f'  total: {len(pre_refs)} edges incident to T1/SVD')

    print('\n=== STEP 3: atomic atom deletion (Store.remove_atom cascades incident edges) ===')
    ok = ps.remove_atom(delete_qid, source='atom_merge_pilot_svd_86a',
                        note='DECISION 86a svd MERGE PILOT; canonical singular_value_decomposition kept')
    if not ok:
        print('  FAIL: remove_atom returned False (atom not found?)')
        return
    print(f'  REMOVED: {delete_qid} (atom + all incident relations cascaded)')

    print('\n=== STEP 4: dangling-reference check ===')
    post_refs = inventory_svd_refs(ps)
    if post_refs:
        print(f'  FAIL: {len(post_refs)} dangling refs remain:')
        for src, rel, tgt in post_refs:
            print(f'    {src} -{rel}-> {tgt}')
        print('  HARD_FAIL: dangling references; rollback required')
        return
    print('  OK: 0 dangling references to T1/SVD')

    print('\n=== STEP 5: canonical atom unchanged ===')
    canon_present = any(f'{a.corpus.value}::{a.id}' == canonical_qid for a in ps.all_atoms())
    print(f'  canonical {canonical_qid}: {"PRESENT" if canon_present else "MISSING"}')

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'\npost-pilot: {post_atoms} atoms (delta {post_atoms - pre_atoms}), '
          f'{post_rels} relations (delta {post_rels - pre_rels})')

    print('\n=== STEP 6: R3 verification ===')
    forward = {}
    for src, rel, tgt in ps.iter_all_relations():
        if rel.name in ('DEPENDS_ON', 'SPECIALIZES'):
            forward.setdefault(src, []).append(tgt)
    axioms = set()
    for a in ps.all_atoms():
        if str(a.tier.name) != 'TIER_1_FOUNDATIONAL': continue
        if str(a.corpus.name) != 'MATH': continue
        role = (a.algebra or {}).get('role', '')
        if (a.metadata or {}).get('is_axiom', False) or role in ('axiom_schema', 'axiom', 'type'):
            axioms.add(f'math::{a.id}')
    def terminates(s, d=15):
        seen = {s}; f = [s]
        for _ in range(d):
            n = []
            for x in f:
                if x in axioms: return True
                for t in forward.get(x, []):
                    if t not in seen: seen.add(t); n.append(t)
            f = n
            if not f: break
        return any(x in axioms for x in seen)
    ops = [a for a in ps.all_atoms()
           if str(a.corpus.name) == 'MATH'
           and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
           and a.algebra and len(a.algebra) >= 3
           and 'oeis' not in str(a.id).lower()
           and not str(a.id).startswith('T3/wikidata_')]
    t = sum(1 for op in ops if terminates(f'math::{op.id}'))
    print(f'axiom termination: {t}/{len(ops)} = {100 * t / len(ops):.1f}%')

    import importlib
    mod_ok = True
    for mod_name, sym in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ]:
        try:
            m = importlib.import_module(mod_name)
            assert hasattr(m, sym)
        except Exception:
            mod_ok = False
            print(f'  MOD_FAIL: {mod_name}.{sym}')
    print(f'Tier 1+2 modules: {"ALL OK" if mod_ok else "FAIL -- ROLLBACK CANDIDATE"}')

    hard_pass = (
        len(post_refs) == 0
        and canon_present
        and t == len(ops)
        and mod_ok
    )

    print(f'\nSUMMARY:')
    print(f'  atom deleted:       {delete_qid}')
    print(f'  edges cascaded:     {pre_rels - post_rels}  (expected ~11)')
    print(f'  dangling refs:      {len(post_refs)}        (must be 0)')
    print(f'  canonical intact:   {canon_present}')
    print(f'  R3 axiom term:      {t}/{len(ops)}')
    print(f'  R3 modules:         {"OK" if mod_ok else "FAIL"}')
    print(f'\n  HARD_PASS: {hard_pass}')
    print(f'\nTag: SUBSTRATE_HYGIENE_ATOM_MERGE_PILOT_v1')


if __name__ == '__main__':
    main()
