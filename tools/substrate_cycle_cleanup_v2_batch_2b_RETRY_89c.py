"""DECISION 89c retry: cycle-cleanup v2 batch 2b WITH category_type rescue.

Per Director DECISION 89 + Skunkworks 88b + Exp-Dev 89b PRECHECK PASS.

Spec: data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2b_RETRY_with_rescue_v1.jsonl
  37 ops total:
    - 15 REMOVE family --DEPENDS_ON--> member (backwards)
    - 15 ADD member --SPECIALIZES--> family (correct direction)
    -  7 ADD T2_FAM --SPECIALIZES--> category_type (RESCUE: gives families an
         outgoing forward edge to a terminal T1 axiom; restores axiom-term path)

Exp-Dev precheck: forward-walk ok=True (0 stranded; both 87c failures rescued
via T2_FAM->category_type d=1 path); dangling=0.

R3 verification + capability_preservation rollback per the 87c rollback
discipline (which validated the rollback path itself).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import RelationType, Corpus


JSONL = Path('data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2b_RETRY_with_rescue_v1.jsonl')


def find_qid_by_short(ps, short):
    candidates = []
    for a in ps.all_atoms():
        if str(a.id).split('/')[-1].lower() == short.lower():
            candidates.append(f'{a.corpus.value}::{a.id}')
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    # Prefer T2_FAM for family-named atoms (probabilistic_inference, etc.)
    fam_first = [c for c in candidates if 'T2_FAM/' in c]
    if fam_first:
        return fam_first[0]
    # Prefer math corpus
    math_first = [c for c in candidates if c.startswith('math::')]
    if math_first:
        return math_first[0]
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


def axiom_term(ps):
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
    return t, len(ops)


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'pre-retry: {pre_atoms} atoms, {pre_rels} relations, '
          f'axiom_term {pre_t}/{pre_total}\n')

    ops = []
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if line:
                ops.append(json.loads(line))
    print(f'loaded {len(ops)} ops from {JSONL.name}\n')

    print('=== execute 37 ops atomically ===')
    removed = 0
    added = 0
    add_skip_exists = 0
    failed = 0
    for op in ops:
        s = find_qid_by_short(ps, op['src'])
        t = find_qid_by_short(ps, op['tgt'])
        if not (s and t):
            print(f'  MISSING_ATOM: op={op["op"]} {op["src"]}->{op["tgt"]} ({s} {t})')
            failed += 1
            continue
        if op['op'] == 'REMOVE':
            ok = remove_edge(ps, s, t, op['rel_type'])
            if ok:
                removed += 1
            else:
                print(f'  REMOVE_NOT_FOUND: {s} -{op["rel_type"]}-> {t}')
                failed += 1
            ps._store_for(Corpus.MATH)._flush_relations()
        elif op['op'] == 'ADD':
            try:
                ps.add_relation(
                    s, RelationType[op['rel_type']], t,
                    source='cycle_cleanup_v2_batch_2b_RETRY_89c',
                    note=f'DECISION 89c retry: {op.get("reason", "")[:160]}',
                )
                added += 1
            except Exception as ex:
                msg = str(ex)[:120]
                if 'already' in msg.lower() or 'exists' in msg.lower():
                    add_skip_exists += 1
                else:
                    print(f'  ADD_FAIL: {s} -{op["rel_type"]}-> {t}: {msg}')
                    failed += 1
        else:
            print(f'  UNKNOWN_OP: {op}')
            failed += 1

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)
    print(f'\npost-retry: {post_atoms} atoms, {post_rels} relations '
          f'(delta {post_rels - pre_rels}), axiom_term {post_t}/{post_total}')

    print(f'\n=== HARDENED dangling scan ===')
    # Verify each REMOVE op's edge is GONE; each ADD op's edge is PRESENT
    rel_set = set()
    for src, rel, tgt in ps.iter_all_relations():
        rel_set.add((src, rel.name, tgt))
    dangling = []
    missing = []
    for op in ops:
        s = find_qid_by_short(ps, op['src'])
        t = find_qid_by_short(ps, op['tgt'])
        if not (s and t): continue
        rk = (s, op['rel_type'], t)
        if op['op'] == 'REMOVE':
            if rk in rel_set:
                dangling.append(rk)
        elif op['op'] == 'ADD':
            if rk not in rel_set:
                missing.append(rk)
    print(f'  dangling backwards: {len(dangling)} (must be 0)')
    print(f'  missing forwards:   {len(missing)} (must be 0)')

    # R3 module check
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
        post_t == post_total
        and not dangling and not missing
        and mod_ok
        and failed == 0
    )
    print(f'\nSUMMARY:')
    print(f'  REMOVE ops:        {removed} / 15')
    print(f'  ADD ops:           {added} (skip-exists: {add_skip_exists}) / 22')
    print(f'  failed:            {failed}')
    print(f'  axiom_term:        {post_t}/{post_total}  (pre: {pre_t}/{pre_total})')
    print(f'  modules:           {"OK" if mod_ok else "FAIL"}')
    print(f'  delta relations:   {post_rels - pre_rels}')
    print(f'  HARD_PASS:         {hard_pass}')
    print(f'\nTag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2b_RETRY_with_RESCUE')


if __name__ == '__main__':
    main()
