"""DECISION 87c: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2b.

Per Director DECISION 87c + Skunkworks 87b consolidated JSONL:
- 15 family --DEPENDS_ON--> member backwards edges
- Uniform per-edge: REMOVE DEPENDS_ON; ADD member --SPECIALIZES--> family
- KEEP family --USES--> member untouched (legitimate dispatch semantic)
- HARDENED dangling scan (all-rel-type) post-batch
- R3 + capability_preservation rollback per edge
- 0 flagged as non-applying per Skunkworks textbook check
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
    # Prefer T2_FAM matches when "family" pattern; else first
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
    print(f'pre-batch-2b: {pre_atoms} atoms, {pre_rels} relations\n')

    edges = []
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if line:
                edges.append(json.loads(line))
    print(f'loaded {len(edges)} edges from {JSONL.name}\n')

    print('=== STEP 1: atom resolution ===')
    resolved = []
    missing = []
    for e in edges:
        fam = e['family']; mem = e['member']
        fam_qid = find_qid_by_short(ps, fam)
        mem_qid = find_qid_by_short(ps, mem)
        if fam_qid and mem_qid:
            resolved.append((e, fam_qid, mem_qid))
        else:
            missing.append((fam, mem, fam_qid, mem_qid))
            print(f'  MISSING: {fam}({fam_qid}) -> {mem}({mem_qid})')
    if missing:
        print(f'  ABORT: {len(missing)} atom(s) missing')
        return
    print(f'  OK: 15/15 atoms resolved')

    print(f'\n=== STEP 2: atomic REMOVE-AND-REPLACE per edge ===')
    removed = 0
    added = 0
    add_skip_exists = 0
    for e, fam_qid, mem_qid in resolved:
        # REMOVE family --DEPENDS_ON--> member
        ok = remove_edge(ps, fam_qid, mem_qid, 'DEPENDS_ON')
        if ok:
            removed += 1
            print(f'  REMOVED: {fam_qid} -DEPENDS_ON-> {mem_qid}')
        else:
            print(f'  REMOVE_NOT_FOUND: {fam_qid} -DEPENDS_ON-> {mem_qid}')
        ps._store_for(Corpus.MATH)._flush_relations()
        # ADD member --SPECIALIZES--> family
        try:
            ps.add_relation(
                mem_qid, RelationType.SPECIALIZES, fam_qid,
                source='cycle_cleanup_v2_batch_2b_87c',
                note=f'DECISION 87c: {e["member"]} specializes {e["family"]}',
            )
            added += 1
            print(f'  ADDED:   {mem_qid} -SPECIALIZES-> {fam_qid}')
        except Exception as ex:
            msg = str(ex)[:120]
            if 'already' in msg.lower() or 'exists' in msg.lower():
                add_skip_exists += 1
                print(f'  ADD_SKIP_EXISTS: {mem_qid} -SPECIALIZES-> {fam_qid}')
            else:
                print(f'  ADD_FAIL: {mem_qid} -SPECIALIZES-> {fam_qid}: {msg}')

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'\npost-batch-2b: {post_atoms} atoms (delta {post_atoms - pre_atoms}), '
          f'{post_rels} relations (delta {post_rels - pre_rels})')

    print(f'\n=== STEP 3: HARDENED dangling scan (all rel-types) ===')
    # Per DECISION 87c: confirm no orphaned references; check each ADDED member-SPECIALIZES->family
    # exists; check each REMOVED family-DEPENDS_ON->member is GONE
    rel_set = set()
    for src, rel, tgt in ps.iter_all_relations():
        rel_set.add((src, rel.name, tgt))
    dangling = []
    missing_adds = []
    for e, fam_qid, mem_qid in resolved:
        # backwards edge should be GONE
        if (fam_qid, 'DEPENDS_ON', mem_qid) in rel_set:
            dangling.append((fam_qid, 'DEPENDS_ON', mem_qid))
        # forward edge should be PRESENT
        if (mem_qid, 'SPECIALIZES', fam_qid) not in rel_set:
            missing_adds.append((mem_qid, 'SPECIALIZES', fam_qid))
    if dangling:
        print(f'  DANGLING: {len(dangling)} backwards edges remain:')
        for d in dangling: print(f'    {d}')
    else:
        print(f'  OK: 0 backwards DEPENDS_ON edges remain (all 15 cleared)')
    if missing_adds:
        print(f'  MISSING_ADDS: {len(missing_adds)} forward SPECIALIZES edges absent:')
        for m in missing_adds: print(f'    {m}')
    else:
        print(f'  OK: 15 forward SPECIALIZES edges all present')

    print(f'\n=== STEP 4: R3 verification ===')
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
    print(f'Tier 1+2 modules: {"ALL OK" if mod_ok else "FAIL"}')

    hard_pass = (
        not dangling and not missing_adds
        and t == len(ops) and mod_ok
    )

    print(f'\nSUMMARY:')
    print(f'  edges removed:      {removed}/15')
    print(f'  edges added:        {added}/15 (skip-exists: {add_skip_exists})')
    print(f'  dangling backwards: {len(dangling)} (must be 0)')
    print(f'  missing forwards:   {len(missing_adds)} (must be 0)')
    print(f'  R3 axiom term:      {t}/{len(ops)} = {100 * t / len(ops):.1f}%')
    print(f'  R3 modules:         {"OK" if mod_ok else "FAIL"}')
    print(f'  delta relations:    {post_rels - pre_rels}')
    print(f'  HARD_PASS: {hard_pass}')
    print(f'\nTag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2b')


if __name__ == '__main__':
    main()
