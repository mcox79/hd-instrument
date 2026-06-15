"""DECISION 116a: Phase 3 Sub-batch 3 -- collins word-order MERGE.

Per Director DECISION 116a + Skunkworks 105b/113c spec + Exp-Dev PRECHECK PASS GREEN.

Canonical: math::T3/structured_perceptron_collins (more-connected; minimizes churn)
DELETE:    math::T3/collins_structured_perceptron (word-order duplicate)

Standard merge pattern (re-point all incident edges + remove_atom + 105c cleanup).
No spurious drops. Low cross-store complexity per canonical choice.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import RelationType
from tools.substrate_cross_store_cleanup_v1 import cross_store_cleanup


CANONICAL = 'math::T3/structured_perceptron_collins'
DELETE_QID = 'math::T3/collins_structured_perceptron'


def matches_endpoint(ep, qid):
    if ep == qid:
        return True
    q = QualifiedAtomId.parse(qid)
    return ep == q.local_id


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
    print(f'pre-merge: {pre_atoms} atoms, {pre_rels} relations, axiom_term {pre_t}/{pre_total}\n')

    if not any(f'{a.corpus.value}::{a.id}' == CANONICAL for a in ps.all_atoms()):
        print(f'ABORT: canonical {CANONICAL} not present')
        return
    if not any(f'{a.corpus.value}::{a.id}' == DELETE_QID for a in ps.all_atoms()):
        print(f'ABORT: delete-target {DELETE_QID} not present')
        return
    print(f'canonical present: {CANONICAL}')
    print(f'delete present:    {DELETE_QID}\n')

    print('=== STEP 1: re-point all incident edges to canonical ===')
    incident = []
    for src, rel, tgt in list(ps.iter_all_relations()):
        if matches_endpoint(src, DELETE_QID) or matches_endpoint(tgt, DELETE_QID):
            incident.append((src, rel.name, tgt))
    print(f'  {len(incident)} incident edges found')

    added = 0
    skip_self = 0
    skip_dup = 0
    skip_has_users = 0
    for src, rel_name, tgt in incident:
        if rel_name == 'HAS_USERS':
            skip_has_users += 1
            continue
        new_src = CANONICAL if matches_endpoint(src, DELETE_QID) else src
        new_tgt = CANONICAL if matches_endpoint(tgt, DELETE_QID) else tgt
        if matches_endpoint(new_src, CANONICAL) and matches_endpoint(new_tgt, CANONICAL):
            skip_self += 1
            continue
        try:
            ps.add_relation(new_src, RelationType[rel_name], new_tgt,
                            source='phase3_subbatch3_collins_116a',
                            note=f'DECISION 116a collins MERGE: was {src} -{rel_name}-> {tgt}')
            added += 1
        except Exception as e:
            msg = str(e)[:100]
            if 'already' in msg.lower() or 'exists' in msg.lower():
                skip_dup += 1
            else:
                print(f'  ADD_FAIL: {new_src} -{rel_name}-> {new_tgt}: {msg}')
    print(f'  re-points: {added} added, {skip_self} self-loop, {skip_dup} dup, {skip_has_users} HAS_USERS')

    print(f'\n=== STEP 2: DELETE {DELETE_QID} (cascade within-math) ===')
    ok = ps.remove_atom(DELETE_QID, source='phase3_subbatch3_collins_116a',
                        note='DECISION 116a collins MERGE; canonical structured_perceptron_collins preserves capabilities')
    print(f'  atom deleted: {ok}')

    print(f'\n=== STEP 3: cross-store cleanup via 105c primitive ===')
    cleaned = cross_store_cleanup(ps, DELETE_QID, execute=True)
    print(f'  cross-store cleaned: {len(cleaned)}')
    for c in cleaned[:5]:
        print(f'    {c}')

    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_atoms = len(ps2.all_atoms())
    post_rels = sum(1 for _ in ps2.iter_all_relations())
    post_t, post_total = axiom_term(ps2)
    print(f'\npost-merge: {post_atoms} atoms (delta {post_atoms - pre_atoms}), '
          f'{post_rels} relations (delta {post_rels - pre_rels}), '
          f'axiom_term {post_t}/{post_total}')

    delete_set = {DELETE_QID, QualifiedAtomId.parse(DELETE_QID).local_id}
    dangling = []
    for src, rel, tgt in ps2.iter_all_relations():
        if src in delete_set or tgt in delete_set:
            dangling.append((src, rel.name, tgt))
    print(f'\ndangling refs: {len(dangling)} (must be 0)')

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

    hard_pass = ok and not dangling and post_t == post_total and mod_ok
    print(f'\nSUMMARY: deleted={ok}, re-points={added}, cross-store={len(cleaned)}, dangling={len(dangling)}, axiom_term={post_t}/{post_total}, modules={"OK" if mod_ok else "FAIL"}, delta_rels={post_rels - pre_rels}, HARD_PASS={hard_pass}')
    print(f'\nTag: PHASE_3_SUBBATCH_3_collins_WORD_ORDER_MERGE')


if __name__ == '__main__':
    main()
