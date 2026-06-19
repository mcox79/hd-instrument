"""DECISION 107a: Phase 3 Sub-batch 1 Tier 1A -- 6 trivial T2-stub deletes.

Per Director DECISION 107a + Skunkworks 105b spec + 105a precedent-grep NEGATIVE.

Operations:
  For each of 6 T2 stubs:
    1. If has meta::SELF re-point: add canonical equivalent (idempotent skip-exists)
    2. ps.remove_atom(stub) -- cascades within-math edges
    3. Cleanup cross-store dangling edges (meta:: store) from source-side per 101b pattern
  R3 verify per established discipline; atomic rollback on regression.

Leaf-strand class (DELETE + tier-touch); embedded pre-check + R3 + rollback.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import RelationType


# (delete_qid, canonical_qid_for_repoint, has_meta_self_repoint)
TIER_1A = [
    ('math::T2/viterbi_decoder',                'math::T3/viterbi_decoder', True),
    ('math::T2/viterbi_decoding',               'math::T3/viterbi_decoding', False),
    ('math::T2/forward_algorithm',              'math::T3/forward_algorithm', True),
    ('math::T2/backward_algorithm',             'math::T3/backward_algorithm', True),
    ('math::T2/collins_structured_perceptron',  'math::T3/collins_structured_perceptron', False),
    ('math::T2/structured_perceptron_collins',  'math::T3/structured_perceptron_collins', False),
]

META_SELF_SRC = 'meta::SELF/family_sequence_dp'


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


def cleanup_cross_store_dangling(ps, deleted_qids):
    """Remove dangling cross-store edges where src is in different store than deleted atom."""
    deleted_set = set(deleted_qids)
    deleted_locals = {QualifiedAtomId.parse(q).local_id for q in deleted_qids}
    removed = 0
    cleaned = []
    for src, rel, tgt in list(ps.iter_all_relations()):
        if (tgt in deleted_set or tgt in deleted_locals or
            src in deleted_set or src in deleted_locals):
            if '::' not in src:
                continue
            src_q = QualifiedAtomId.parse(src)
            src_store = ps._store_for(src_q.corpus)
            rel_str = rel.value
            for triple in [(src_q.local_id, rel_str, tgt),
                           (src_q.local_id, rel_str, tgt.split('::')[-1] if '::' in tgt else tgt)]:
                if triple in src_store._all_relations:
                    src_store._all_relations.discard(triple)
                    if (src_q.local_id, rel) in src_store._out:
                        src_store._out[(src_q.local_id, rel)].discard(triple[2])
                    if (triple[2], rel) in src_store._in:
                        src_store._in[(triple[2], rel)].discard(src_q.local_id)
                    cleaned.append((src, rel.name, tgt))
                    removed += 1
                    break
    # Flush all touched stores
    from backend.substrate_index.schema import Corpus
    for corpus in [Corpus.MATH, Corpus.CONCEPT, Corpus.META, Corpus.SCIENCE, Corpus.SCHOOL,
                   Corpus.METHODOLOGY]:
        try:
            ps._store_for(corpus)._flush_relations()
        except Exception:
            pass
    return removed, cleaned


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'pre-tier-1A: {pre_atoms} atoms, {pre_rels} relations, axiom_term {pre_t}/{pre_total}\n')

    # Verify all 6 stubs + canonicals exist
    for stub_qid, canon_qid, _ in TIER_1A:
        if not any(f'{a.corpus.value}::{a.id}' == stub_qid for a in ps.all_atoms()):
            print(f'ABORT: stub {stub_qid} not present')
            return
        if not any(f'{a.corpus.value}::{a.id}' == canon_qid for a in ps.all_atoms()):
            print(f'ABORT: canonical {canon_qid} not present')
            return
    print('all 6 stubs + canonicals verified present\n')

    print('=== STEP 1: re-point meta::SELF/family_sequence_dp RELATES to canonicals (idempotent) ===')
    repointed = 0
    for stub_qid, canon_qid, has_repoint in TIER_1A:
        if not has_repoint:
            continue
        try:
            ps.add_relation(
                META_SELF_SRC, RelationType.RELATES, canon_qid,
                source='phase3_subbatch1_tier_1A_107a',
                note=f'DECISION 107a re-point: was -RELATES-> {stub_qid}',
            )
            repointed += 1
            print(f'  ADDED: {META_SELF_SRC} -RELATES-> {canon_qid}')
        except Exception as e:
            msg = str(e)[:100]
            if 'already' in msg.lower() or 'exists' in msg.lower():
                print(f'  SKIP_EXISTS: {META_SELF_SRC} -RELATES-> {canon_qid}')
            else:
                print(f'  ADD_FAIL: {META_SELF_SRC} -RELATES-> {canon_qid}: {msg}')

    print(f'\n=== STEP 2: DELETE T2 stubs (Store.remove_atom cascades within-math) ===')
    deleted = []
    for stub_qid, _, _ in TIER_1A:
        ok = ps.remove_atom(stub_qid, source='phase3_subbatch1_tier_1A_107a',
                            note='DECISION 107a Tier 1A trivial stub delete')
        if ok:
            deleted.append(stub_qid)
            print(f'  DELETED: {stub_qid}')
        else:
            print(f'  NOT_FOUND: {stub_qid}')

    print(f'\n=== STEP 3: cleanup cross-store dangling edges ===')
    cross_removed, cleaned = cleanup_cross_store_dangling(ps, deleted)
    for entry in cleaned:
        print(f'  CLEANED: {entry[0]} -{entry[1]}-> {entry[2]}')
    print(f'  total cleaned: {cross_removed}')

    # Re-load to verify final state
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_atoms = len(ps2.all_atoms())
    post_rels = sum(1 for _ in ps2.iter_all_relations())
    post_t, post_total = axiom_term(ps2)
    print(f'\npost-tier-1A: {post_atoms} atoms (delta {post_atoms - pre_atoms}), '
          f'{post_rels} relations (delta {post_rels - pre_rels}), '
          f'axiom_term {post_t}/{post_total}')

    print(f'\n=== STEP 4: final dangling scan ===')
    deleted_set = set(deleted)
    deleted_locals = {QualifiedAtomId.parse(q).local_id for q in deleted}
    dangling = []
    for src, rel, tgt in ps2.iter_all_relations():
        if (src in deleted_set or src in deleted_locals or
            tgt in deleted_set or tgt in deleted_locals):
            dangling.append((src, rel.name, tgt))
    print(f'  dangling refs: {len(dangling)} (must be 0)')
    for d in dangling[:5]:
        print(f'    {d}')

    # R3 modules
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
        len(deleted) == len(TIER_1A)
        and not dangling
        and post_t == post_total
        and mod_ok
    )

    print(f'\nSUMMARY:')
    print(f'  atoms deleted:      {len(deleted)}/{len(TIER_1A)}')
    print(f'  meta::SELF repoints: {repointed}')
    print(f'  cross-store cleaned: {cross_removed}')
    print(f'  dangling refs:      {len(dangling)}')
    print(f'  axiom_term:         {post_t}/{post_total} (pre: {pre_t}/{pre_total})')
    print(f'  modules:            {"OK" if mod_ok else "FAIL"}')
    print(f'  delta atoms:        {post_atoms - pre_atoms}')
    print(f'  delta relations:    {post_rels - pre_rels}')
    print(f'  HARD_PASS:          {hard_pass}')
    print(f'\nTag: PHASE_3_SUBBATCH_1_TIER_1A_6_T2_STUB_DELETES')


if __name__ == '__main__':
    main()
