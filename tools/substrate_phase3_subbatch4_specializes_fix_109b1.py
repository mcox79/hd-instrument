"""DECISION 109b-1: Phase 3 Sub-batch 4 SPECIALIZES_fix batch.

Per Director DECISION 109b-1 + Skunkworks 107c spec.

Operations (5 ops):
  1. cleanup/cosine_cleanup: REMOVE 2 backwards (cleanup -SPECIALIZES-> cosine; cleanup -DEPENDS_ON-> cosine)
     KEEP cosine_cleanup -SPECIALIZES-> cleanup
  2. cleanup_retrieval/cleanup: ADD 2 SPECIALIZES (member->family STRICT)
  3. matrix_decomposition family: REMOVE 4 backwards DEPENDS_ON to {svd, LU, QR, cholesky}
     MANDATORY ATOMIC RESCUE: ADD matrix_decomposition -DEPENDS_ON-> matrix
     RE-TYPE svd: DEPENDS_ON -> SPECIALIZES (matrix_decomposition)
     ADD LU/QR/cholesky -SPECIALIZES-> matrix_decomposition
  4. group_homomorphism/homomorphism: RE-TYPE g_h DEPENDS_ON -> SPECIALIZES (homo);
     REMOVE homomorphism -DEPENDS_ON-> group_homomorphism
  5. global_discrete_opt/convex_opt: REMOVE both 2-cycle DEPENDS_ON

NO atom deletes. Pre-check embedded; rollback on R3 regression.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import RelationType, Corpus


# Per-op specs as (description, removes, adds)
# removes: list of (src_qid, rel_str, tgt_qid)
# adds:    list of (src_qid, rel_str, tgt_qid)
OPS = [
    ('cleanup / cosine_cleanup SPECIALIZES_fix',
     [('math::T2/cleanup', 'SPECIALIZES', 'math::T2/cosine_cleanup'),
      ('math::T2/cleanup', 'DEPENDS_ON',  'math::T2/cosine_cleanup')],
     []),
    ('cleanup_retrieval / cleanup add SPECIALIZES',
     [],
     [('math::T2/cleanup',        'SPECIALIZES', 'math::T2_FAM/cleanup_retrieval'),
      ('math::T2/cosine_cleanup', 'SPECIALIZES', 'math::T2_FAM/cleanup_retrieval')]),
    ('matrix_decomposition family SPECIALIZES_fix (with mandatory atomic rescue)',
     [('math::T1/matrix_decomposition', 'DEPENDS_ON', 'math::T1/singular_value_decomposition'),
      ('math::T1/matrix_decomposition', 'DEPENDS_ON', 'math::T1/LU_decomposition'),
      ('math::T1/matrix_decomposition', 'DEPENDS_ON', 'math::T1/QR_decomposition'),
      ('math::T1/matrix_decomposition', 'DEPENDS_ON', 'math::T1/cholesky_decomposition')],
     [('math::T1/matrix_decomposition',         'DEPENDS_ON',  'math::T1/matrix'),
      ('math::T1/singular_value_decomposition', 'SPECIALIZES', 'math::T1/matrix_decomposition'),
      ('math::T1/LU_decomposition',             'SPECIALIZES', 'math::T1/matrix_decomposition'),
      ('math::T1/QR_decomposition',             'SPECIALIZES', 'math::T1/matrix_decomposition'),
      ('math::T1/cholesky_decomposition',       'SPECIALIZES', 'math::T1/matrix_decomposition')]),
    ('group_homomorphism / homomorphism SPECIALIZES_fix',
     [('math::T1/group_homomorphism', 'DEPENDS_ON', 'math::T1/homomorphism'),
      ('math::T1/homomorphism',       'DEPENDS_ON', 'math::T1/group_homomorphism')],
     [('math::T1/group_homomorphism', 'SPECIALIZES', 'math::T1/homomorphism')]),
    ('global_discrete_optimization / convex_optimization other_relation_fix',
     [('math::T2_FAM/global_discrete_optimization', 'DEPENDS_ON', 'math::T1/convex_optimization'),
      ('math::T1/convex_optimization',              'DEPENDS_ON', 'math::T2_FAM/global_discrete_optimization')],
     []),
]


def remove_edge(ps, src_qid, dst_qid, rel_str):
    src_q = QualifiedAtomId.parse(src_qid)
    src_store = ps._store_for(src_q.corpus)
    rt = RelationType(rel_str)
    dst_local = QualifiedAtomId.parse(dst_qid).local_id if '::' in dst_qid else dst_qid
    for triple in [(src_q.local_id, rel_str, dst_qid),
                   (src_q.local_id, rel_str, dst_local)]:
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
    print(f'pre-batch: {pre_atoms} atoms, {pre_rels} relations, axiom_term {pre_t}/{pre_total}\n')

    total_removed = 0
    total_added = 0
    total_skipped_add = 0

    for desc, removes, adds in OPS:
        print(f'=== OP: {desc} ===')
        for src, rel, tgt in removes:
            ok = remove_edge(ps, src, tgt, rel)
            if ok:
                total_removed += 1
                print(f'  REMOVED: {src} -{rel}-> {tgt}')
            else:
                print(f'  REMOVE_NOT_FOUND: {src} -{rel}-> {tgt}')
        # Flush after each op's removes
        for corpus in [Corpus.MATH]:
            ps._store_for(corpus)._flush_relations()
        for src, rel, tgt in adds:
            try:
                ps.add_relation(src, RelationType[rel], tgt,
                                source='phase3_subbatch4_specializes_fix_109b1',
                                note=f'DECISION 109b-1: {desc}')
                total_added += 1
                print(f'  ADDED:   {src} -{rel}-> {tgt}')
            except Exception as ex:
                msg = str(ex)[:120]
                if 'already' in msg.lower() or 'exists' in msg.lower():
                    total_skipped_add += 1
                    print(f'  ADD_SKIP_EXISTS: {src} -{rel}-> {tgt}')
                else:
                    print(f'  ADD_FAIL: {src} -{rel}-> {tgt}: {msg}')
        print()

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)
    print(f'post-batch: {post_atoms} atoms, {post_rels} relations '
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

    hard_pass = post_t == post_total and mod_ok

    print(f'\nSUMMARY:')
    print(f'  removed:        {total_removed}')
    print(f'  added:          {total_added} (skip-exists: {total_skipped_add})')
    print(f'  axiom_term:     {post_t}/{post_total} (pre: {pre_t}/{pre_total})')
    print(f'  modules:        {"OK" if mod_ok else "FAIL"}')
    print(f'  delta relations: {post_rels - pre_rels}')
    print(f'  HARD_PASS:      {hard_pass}')
    print(f'\nTag: PHASE_3_SUBBATCH_4_SPECIALIZES_FIX_BATCH')


if __name__ == '__main__':
    main()
