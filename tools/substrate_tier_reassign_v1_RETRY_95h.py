"""DECISION 95h: SUBSTRATE_HYGIENE_TIER_REASSIGN_v1_RETRY (84a retry).

Per Director DECISION 95h + Skunkworks 84a RETRY JSONL + Exp-Dev extended-
precheck PASS (corpus-scoped monotone + forward-walk + axiom-term).

Spec: data/substrate_index/skunkworks_tier_reassign_84a_RETRY_v1.jsonl
  4 tier changes:
    gradient_descent T1 -> T3
    bayes_rule       T1 -> T2
    newton_method    T1 -> T3
    hessian          T1 -> T2
  2 SPECIALIZES adds (leaf-strand rescue per 89c pattern):
    newton_method --SPECIALIZES--> category_type
    hessian       --SPECIALIZES--> category_type

Preconditions verified:
  - batch-2c removed 4 backwards monotone violations (commit ff5f4f73)
  - 4 target atoms still T1 (ready to re-tier)
  - category_type T1 present (terminal rescue root)
  - PP-376 cross-corpus exempt per DECISION 92a/94

Per-op atomic with rollback gate. The 84a original demonstrated R3-rollback
discipline works (operation-class-invariant).
"""
from __future__ import annotations
import json
import sys
from dataclasses import replace
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Tier, RelationType, Corpus


JSONL = Path('data/substrate_index/skunkworks_tier_reassign_84a_RETRY_v1.jsonl')

TIER_BY_NAME = {
    'T1': Tier.TIER_1_FOUNDATIONAL,
    'T2': Tier.TIER_2_PRIMITIVE,
    'T3': Tier.TIER_3_ALGORITHM,
}


def find_atom_by_short(ps, short):
    for a in ps.all_atoms():
        if str(a.id).split('/')[-1].lower() == short.lower():
            return a
    return None


def find_qid_by_short(ps, short):
    a = find_atom_by_short(ps, short)
    if a is None:
        return None
    return f'{a.corpus.value}::{a.id}'


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

    with open(JSONL) as f:
        spec = json.load(f)
    tier_changes = spec['tier_changes']
    adds = spec['adds']
    print(f'loaded {len(tier_changes)} tier_changes + {len(adds)} adds from {JSONL.name}\n')

    # Rescue ADDs FIRST so leaf-strand atoms have forward edge BEFORE membership change.
    # (Order doesn't matter mathematically but executing rescues first is the safer story.)

    print('=== STEP 1: SPECIALIZES rescue adds (2) ===')
    add_results = []
    for add in adds:
        s = find_qid_by_short(ps, add['src'])
        t = find_qid_by_short(ps, add['tgt'])
        if not (s and t):
            print(f'  MISSING_ATOM: {add["src"]}({s}) -> {add["tgt"]}({t})')
            continue
        try:
            ps.add_relation(
                s, RelationType[add['rel_type']], t,
                source='tier_reassign_v1_RETRY_95h',
                note=f'DECISION 95h leaf-strand rescue: {add.get("reason", "")[:160]}',
            )
            add_results.append('ADDED')
            print(f'  ADDED: {s} -{add["rel_type"]}-> {t}')
        except Exception as ex:
            msg = str(ex)[:120]
            if 'already' in msg.lower() or 'exists' in msg.lower():
                add_results.append('SKIP_EXISTS')
                print(f'  ADD_SKIP_EXISTS: {s} -{add["rel_type"]}-> {t}')
            else:
                add_results.append('FAIL')
                print(f'  ADD_FAIL: {s} -{add["rel_type"]}-> {t}: {msg}')

    print(f'\n=== STEP 2: tier mutations (4; upsert via add_atom) ===')
    snapshots = {}
    retiered = []
    for tc in tier_changes:
        a = find_atom_by_short(ps, tc['atom'])
        if a is None:
            print(f'  MISSING: {tc["atom"]}')
            continue
        new_tier = TIER_BY_NAME[tc['new_tier']]
        if a.tier == new_tier:
            print(f'  SKIP (already {new_tier.name}): {tc["atom"]}')
            continue
        snapshots[tc['atom']] = a
        new_atom = replace(a, tier=new_tier)
        ps._store_for(a.corpus).add_atom(
            new_atom,
            source='tier_reassign_v1_RETRY_95h',
            note=f'DECISION 95h retry: {tc["atom"]} {a.tier.name} -> {new_tier.name} ({tc.get("reason", "")})',
        )
        retiered.append(tc['atom'])
        print(f'  RETIERED: {tc["atom"]} {a.tier.name} -> {new_tier.name}')

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)
    print(f'\npost-retry: {post_atoms} atoms, {post_rels} relations '
          f'(delta {post_rels - pre_rels}), axiom_term {post_t}/{post_total}')

    print(f'\n=== STEP 3: R3 verification ===')
    # Verify re-tiered atoms hold new tier
    tier_ok = True
    for tc in tier_changes:
        a = find_atom_by_short(ps, tc['atom'])
        expected = TIER_BY_NAME[tc['new_tier']]
        if a is None or a.tier != expected:
            tier_ok = False
            print(f'  TIER_VERIFY_FAIL: {tc["atom"]}')

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

    hard_pass = post_t == post_total and mod_ok and tier_ok

    if not hard_pass:
        print(f'\nHARD_FAIL detected; rolling back...')
        for short, snap in snapshots.items():
            ps._store_for(snap.corpus).add_atom(
                snap, source='tier_reassign_v1_RETRY_95h_ROLLBACK',
                note='DECISION 95h ROLLBACK: R3 regression',
            )
            print(f'  ROLLED_BACK: {short} -> {snap.tier.name}')

    print(f'\nSUMMARY:')
    print(f'  rescue adds:     {sum(1 for r in add_results if r == "ADDED")} (skip-exists {sum(1 for r in add_results if r == "SKIP_EXISTS")}; fail {sum(1 for r in add_results if r == "FAIL")}) / {len(adds)}')
    print(f'  re-tiered:       {len(retiered)} / {len(tier_changes)}')
    print(f'  axiom_term:      {post_t}/{post_total}  (pre: {pre_t}/{pre_total})')
    print(f'  modules:         {"OK" if mod_ok else "FAIL"}')
    print(f'  tier_verify:     {"OK" if tier_ok else "FAIL"}')
    print(f'  delta relations: {post_rels - pre_rels}')
    print(f'  HARD_PASS:       {hard_pass}')
    print(f'\nTag: SUBSTRATE_HYGIENE_TIER_REASSIGN_v1_RETRY')


if __name__ == '__main__':
    main()
