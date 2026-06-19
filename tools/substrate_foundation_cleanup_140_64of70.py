"""DECISION 140 foundation-cleanup: ratify 64 CLEARED edges (Exp-Dev 140b verdict).

Per Skunkworks 140a spec + Exp-Dev 140b pre-check + Director DEC 140 dispatch.

Operations (64 edges across 47 atoms; -2 blocked atoms; Tier B 11 of 12):
  Tier A: REMOVE backwards-DEPENDS_ON/USES for 33 atoms (35 - 2 blocked)
    BLOCKED: bayes_rule (1 edge), gradient_descent (5 edges) -- path/field mismatch
  Tier B: REMOVE backwards + ADD textbook-rescue forward edge for 11 atoms
    HELD: dynamic_programming_bellman (Exp-Dev/Skunkworks domain call pending)

R3 + rollback per established discipline; atomic per atom.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import RelationType, Corpus


TIER_A_JSONL = Path('data/substrate_index/skunkworks_T1_foundation_backwards_edge_fix_spec_2026-06-15.jsonl')

# Atoms with blocked edges (per Exp-Dev 140b path/field tier mismatch)
BLOCKED_ATOMS = {'math::T1/bayes_rule', 'math::T1/gradient_descent'}

# Tier B 11 (excluding flagged dynamic_programming_bellman):
# (atom_qid, [removes], [adds])
# removes: [(rel_str, tgt_qid)]
# adds: [(rel_str, tgt_qid)]
TIER_B_CLEARED = [
    ('math::T1/brownian_motion',
     [('DEPENDS_ON', 'math::T3/gaussian_process')],
     [('DEPENDS_ON', 'math::T1/random_variable')]),
    ('math::T1/discrete_optimization',
     [('DEPENDS_ON', 'math::T3/dijkstra')],
     [('DEPENDS_ON', 'math::T1/set')]),
    ('math::T1/ergodicity',
     [('DEPENDS_ON', 'math::T3/mcmc_sampling')],
     [('DEPENDS_ON', 'math::T1/markov_chain')]),
    ('math::T1/graph_general',
     [('DEPENDS_ON', 'math::T3/chu_liu_edmonds')],
     [('DEPENDS_ON', 'math::T1/set')]),
    ('math::T1/group_axioms',
     [('DEPENDS_ON', 'math::T2_FAM/algebraic_binding')],
     [('INSTANCE_OF', 'math::T1/proposition')]),
    ('math::T1/importance_sampling',
     [('DEPENDS_ON', 'math::T3/importance_reweighting_lemma')],
     [('DEPENDS_ON', 'math::T1/probability_distribution')]),
    ('math::T1/lyapunov_stability',
     [('DEPENDS_ON', 'math::T2/modern_hopfield_ramsauer'),
      ('DEPENDS_ON', 'math::T2/cleanup')],
     [('DEPENDS_ON', 'math::T1/ode')]),
    ('math::T1/monte_carlo',
     [('DEPENDS_ON', 'math::T3/law_of_large_numbers_lemma')],
     [('DEPENDS_ON', 'math::T1/random_variable')]),
    ('math::T1/shortest_path',
     [('DEPENDS_ON', 'math::T3/dijkstra')],
     [('DEPENDS_ON', 'math::T1/graph_topology')]),
    ('math::T1/tensor',
     [('DEPENDS_ON', 'math::T2/tensor_product_representation')],
     [('DEPENDS_ON', 'math::T1/vector_space')]),
    ('math::T1/total_probability',
     [('DEPENDS_ON', 'math::T3/product_rule_probability_lemma')],
     [('DEPENDS_ON', 'math::T1/conditional_probability')]),
]


def remove_edge(ps, src_qid, dst_qid, rel_str):
    src_q = QualifiedAtomId.parse(src_qid)
    src_store = ps._store_for(src_q.corpus)
    rt = RelationType(rel_str)
    dst_local = QualifiedAtomId.parse(dst_qid).local_id if '::' in dst_qid else dst_qid
    for triple in [(src_q.local_id, rel_str, dst_qid), (src_q.local_id, rel_str, dst_local)]:
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
    print(f'pre: {pre_atoms} atoms / {pre_rels} relations / axiom_term {pre_t}/{pre_total}\n')

    # === Tier A: Process JSONL; skip BLOCKED atoms ===
    print('=== Tier A: backwards-edge REMOVE (skipping BLOCKED atoms) ===')
    tier_a_removed = 0
    tier_a_skipped_blocked = 0
    tier_a_not_found = 0
    with open(TIER_A_JSONL) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            e = json.loads(line)
            if '_meta' in e:
                continue
            atom_qid = e.get('atom')
            if not atom_qid:
                continue
            if atom_qid in BLOCKED_ATOMS:
                tier_a_skipped_blocked += len(e.get('remove_backwards', []))
                continue
            for rb in e.get('remove_backwards', []):
                rel = rb['rel']
                tgt = rb['tgt']
                ok = remove_edge(ps, atom_qid, tgt, rel)
                if ok:
                    tier_a_removed += 1
                else:
                    tier_a_not_found += 1
    ps._store_for(Corpus.MATH)._flush_relations()
    print(f'  Tier A removed: {tier_a_removed}; skipped (BLOCKED): {tier_a_skipped_blocked}; not_found: {tier_a_not_found}')

    # === Tier B: REMOVE + ADD rescue per atom ===
    print(f'\n=== Tier B: 11 atoms REMOVE+RESCUE ===')
    tier_b_removed = 0
    tier_b_added = 0
    for atom_qid, removes, adds in TIER_B_CLEARED:
        for rel, tgt in removes:
            ok = remove_edge(ps, atom_qid, tgt, rel)
            if ok:
                tier_b_removed += 1
                print(f'  REMOVED: {atom_qid} -{rel}-> {tgt}')
            else:
                print(f'  NOT_FOUND: {atom_qid} -{rel}-> {tgt}')
        ps._store_for(Corpus.MATH)._flush_relations()
        for rel, tgt in adds:
            try:
                ps.add_relation(atom_qid, RelationType[rel], tgt,
                                source='foundation_cleanup_140_64of70',
                                note='DECISION 140 Tier B rescue per Skunkworks 140a spec + Exp-Dev 140b clear')
                tier_b_added += 1
                print(f'  ADDED:   {atom_qid} -{rel}-> {tgt}')
            except Exception as ex:
                msg = str(ex)[:100]
                if 'already' in msg.lower() or 'exists' in msg.lower():
                    print(f'  ADD_SKIP_EXISTS: {atom_qid} -{rel}-> {tgt}')
                else:
                    print(f'  ADD_FAIL: {atom_qid} -{rel}-> {tgt}: {msg}')
    print(f'  Tier B removed: {tier_b_removed}; added: {tier_b_added}')

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)
    print(f'\npost: {post_atoms} atoms / {post_rels} relations / axiom_term {post_t}/{post_total}')
    print(f'delta_relations: {post_rels - pre_rels}')

    import importlib
    mod_ok = all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])
    hard_pass = post_t == post_total and mod_ok
    print(f'modules: {"OK" if mod_ok else "FAIL"}; HARD_PASS: {hard_pass}')


if __name__ == '__main__':
    main()
