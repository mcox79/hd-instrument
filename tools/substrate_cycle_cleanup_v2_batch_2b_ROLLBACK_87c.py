"""DECISION 87c ROLLBACK: reverse the 15 family REMOVE-AND-REPLACE operations.

Per Director DECISION 87c "ROLLBACK on ANY regression":
- axiom termination dropped 213/213 -> 211/213 (T2_FAM/discriminative_classification +
  T2_FAM/graph_traversal became leaf-stranded after their outgoing DEPENDS_ON to
  members were inverted to incoming SPECIALIZES)
- Rollback: REMOVE the added member->SPECIALIZES->family; ADD back family->DEPENDS_ON->member

This returns substrate to post-86b state (213/213 axiom term; 5273 relations).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import RelationType, Corpus


JSONL = Path('data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2b_15_family_edges.jsonl')


def find_qid_by_short(ps, short):
    candidates = []
    for a in ps.all_atoms():
        if str(a.id).split('/')[-1].lower() == short.lower():
            candidates.append(f'{a.corpus.value}::{a.id}')
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    fam_first = [c for c in candidates if 'T2_FAM/' in c]
    if fam_first:
        return fam_first[0]
    return candidates[0]


def remove_edge(ps, src_qid, dst_qid, rel_str):
    src_q = QualifiedAtomId.parse(src_qid)
    src_store = ps._store_for(src_q.corpus)
    rt = RelationType(rel_str)
    for triple in [(src_q.local_id, rel_str, dst_qid),
                   (src_q.local_id, rel_str, QualifiedAtomId.parse(dst_qid).local_id)]:
        if triple in src_store._all_relations:
            src_store._all_relations.discard(triple)
            tgt = triple[2]
            if (src_q.local_id, rt) in src_store._out:
                src_store._out[(src_q.local_id, rt)].discard(tgt)
            if (tgt, rt) in src_store._in:
                src_store._in[(tgt, rt)].discard(src_q.local_id)
            return True
    return False


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'pre-rollback: {pre_atoms} atoms, {pre_rels} relations\n')

    edges = []
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if line:
                edges.append(json.loads(line))

    print(f'=== reverse each of {len(edges)} operations ===')
    revs_removed = 0
    revs_added = 0
    for e in edges:
        fam_qid = find_qid_by_short(ps, e['family'])
        mem_qid = find_qid_by_short(ps, e['member'])
        # REMOVE the added member -SPECIALIZES-> family
        ok = remove_edge(ps, mem_qid, fam_qid, 'SPECIALIZES')
        if ok:
            revs_removed += 1
            print(f'  REMOVED-SPECIALIZES: {mem_qid} -SPECIALIZES-> {fam_qid}')
        else:
            print(f'  SPECIALIZES_NOT_FOUND: {mem_qid} -SPECIALIZES-> {fam_qid}')
        ps._store_for(Corpus.MATH)._flush_relations()
        # ADD back family -DEPENDS_ON-> member
        try:
            ps.add_relation(
                fam_qid, RelationType.DEPENDS_ON, mem_qid,
                source='cycle_cleanup_v2_batch_2b_ROLLBACK_87c',
                note=f'DECISION 87c ROLLBACK: restore {e["family"]} -DEPENDS_ON-> {e["member"]} '
                     f'(axiom-term regression at 211/213)',
            )
            revs_added += 1
            print(f'  RE-ADDED-DEPENDS_ON: {fam_qid} -DEPENDS_ON-> {mem_qid}')
        except Exception as ex:
            print(f'  RE-ADD_FAIL: {fam_qid} -DEPENDS_ON-> {mem_qid}: {str(ex)[:120]}')

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'\npost-rollback: {post_atoms} atoms, {post_rels} relations')

    print(f'\n=== R3 verification (should be 213/213 = 100%) ===')
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

    print(f'\nSUMMARY:')
    print(f'  SPECIALIZES removed: {revs_removed}/15')
    print(f'  DEPENDS_ON re-added: {revs_added}/15')
    print(f'  R3 axiom term:       {t}/{len(ops)}')
    print(f'  rollback complete:   {t == len(ops)}')


if __name__ == '__main__':
    main()
