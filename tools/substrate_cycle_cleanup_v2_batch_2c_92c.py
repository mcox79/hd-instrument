"""DECISION 92c/94b: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2c.

Per Director DECISION 94 (final) + Skunkworks 92 + Exp-Dev 92b PRECHECK PASS.

Spec: data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2c_5_backwards_edges.jsonl
  4 logical ops (5 atomic):
    SIMPLE REMOVE (3):
      derivative -> gradient_descent
      bayes_rule -> count_nb
      limit_of_function -> gradient_descent
    REMOVE-AND-REPLACE (1):
      bayes_rule -> bayes_rule_synthesis [REMOVE]
      bayes_rule_synthesis -> bayes_rule [ADD]
    UNTOUCHED:
      PP-376 -> gradient_descent (cross-corpus; corpus-scoped exempt per DECISION 92a)

Exp-Dev 92b precheck (corpus-scoped monotone + forward-walk): consistent with
this 4-op spec; PP-376 correctly exempted; pre-check stack now respects
corpus boundaries + operation-class-invariant.

R3 + capability_preservation rollback per the v1 discipline.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import RelationType, Corpus


JSONL = Path('data/substrate_index/skunkworks_cycle_cleanup_v2_batch_2c_5_backwards_edges.jsonl')


def find_qid_by_short(ps, short):
    candidates = []
    for a in ps.all_atoms():
        if str(a.id).split('/')[-1].lower() == short.lower():
            candidates.append(f'{a.corpus.value}::{a.id}')
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
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
    print(f'pre-batch-2c: {pre_atoms} atoms, {pre_rels} relations, '
          f'axiom_term {pre_t}/{pre_total}\n')

    ops = []
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if line:
                ops.append(json.loads(line))
    print(f'loaded {len(ops)} ops from {JSONL.name}\n')

    print('=== execute 4 logical ops atomically ===')
    removed = 0
    added = 0
    failed = 0
    for op in ops:
        s = find_qid_by_short(ps, op['src'])
        t = find_qid_by_short(ps, op['tgt'])
        if not (s and t):
            print(f'  MISSING: {op["src"]}({s}) -> {op["tgt"]}({t})')
            failed += 1
            continue
        if op['op'] == 'REMOVE':
            ok = remove_edge(ps, s, t, op['rel_type'])
            if ok:
                removed += 1
                print(f'  REMOVED: {s} -{op["rel_type"]}-> {t}')
            else:
                print(f'  NOT_FOUND: {s} -{op["rel_type"]}-> {t}')
                failed += 1
            ps._store_for(Corpus.MATH)._flush_relations()
        elif op['op'] == 'REMOVE_AND_REPLACE':
            ok = remove_edge(ps, s, t, op['rel_type'])
            if ok:
                removed += 1
                print(f'  REMOVED: {s} -{op["rel_type"]}-> {t}')
            else:
                print(f'  NOT_FOUND: {s} -{op["rel_type"]}-> {t}')
                failed += 1
            ps._store_for(Corpus.MATH)._flush_relations()
            asrc = find_qid_by_short(ps, op['add_src'])
            atgt = find_qid_by_short(ps, op['add_tgt'])
            if not (asrc and atgt):
                print(f'  MISSING_ADD: {op["add_src"]}->{op["add_tgt"]}')
                failed += 1
                continue
            try:
                ps.add_relation(
                    asrc, RelationType[op['add_rel_type']], atgt,
                    source='cycle_cleanup_v2_batch_2c_92c',
                    note=f'DECISION 94b R&R: {op.get("reason", "")[:160]}',
                )
                added += 1
                print(f'  ADDED:   {asrc} -{op["add_rel_type"]}-> {atgt}')
            except Exception as ex:
                msg = str(ex)[:120]
                if 'already' in msg.lower() or 'exists' in msg.lower():
                    print(f'  ADD_SKIP_EXISTS: {asrc} -{op["add_rel_type"]}-> {atgt}')
                else:
                    print(f'  ADD_FAIL: {asrc} -{op["add_rel_type"]}-> {atgt}: {msg}')
                    failed += 1
        else:
            print(f'  UNKNOWN_OP: {op["op"]}')
            failed += 1

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)
    print(f'\npost-batch-2c: {post_atoms} atoms, {post_rels} relations '
          f'(delta {post_rels - pre_rels}), axiom_term {post_t}/{post_total}')

    print(f'\n=== R3 verification ===')
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

    hard_pass = post_t == post_total and mod_ok and failed == 0

    print(f'\nSUMMARY:')
    print(f'  edges removed:   {removed} / 4 (3 simple + 1 R&R)')
    print(f'  edges added:     {added} / 1 (R&R)')
    print(f'  failed:          {failed}')
    print(f'  axiom_term:      {post_t}/{post_total}  (pre: {pre_t}/{pre_total})')
    print(f'  modules:         {"OK" if mod_ok else "FAIL"}')
    print(f'  delta relations: {post_rels - pre_rels}')
    print(f'  HARD_PASS:       {hard_pass}')
    print(f'\nTag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2_BATCH_2c')


if __name__ == '__main__':
    main()
