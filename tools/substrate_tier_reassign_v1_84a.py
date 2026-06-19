"""DECISION 84a: SUBSTRATE_HYGIENE_TIER_REASSIGN_v1 (PARTIAL: 2 of 4 safe).

Per Director DECISION 84a + 73rd-honest-signal style pre-check discipline.

Director's 4 targets:
  gradient_descent  T1 -> T3   [BLOCKED: 3 tier-monotone violations on incoming edges]
  newton_method     T1 -> T3   [SAFE]
  hessian           T1 -> T2   [SAFE]
  bayes_rule        T1 -> T2   [BLOCKED: 2 tier-monotone violations on outgoing edges]

Shipping the 2 SAFE; flagging the 2 BLOCKED with concrete violation evidence
for Director rescue (rescue likely = cycle-cleanup batch 2c on 5 backwards-
direction edges before re-attempting those re-tiers).

Per 89c's three-role collaborative recovery discipline (now operational).

Tier mutation pattern: add_atom() is upsert; build new Atom with updated tier
and re-add. Audit logs as `update_atom`. Relations untouched.

R3 + capability_preservation rollback per the v1 discipline.
"""
from __future__ import annotations
import sys
from dataclasses import replace
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Tier, Corpus


# Only the 2 monotonicity-clean targets
SAFE_RETIER = [
    ('newton_method', Tier.TIER_3_ALGORITHM),
    ('hessian',       Tier.TIER_2_PRIMITIVE),
]


def find_atom_by_short(ps, short):
    for a in ps.all_atoms():
        if str(a.id).split('/')[-1].lower() == short.lower():
            return a
    return None


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
    print(f'pre-retier: {pre_atoms} atoms, {pre_rels} relations, '
          f'axiom_term {pre_t}/{pre_total}\n')

    print('=== STEP 1: re-tier 2 SAFE atoms (upsert via add_atom) ===')
    snapshots = {}
    for short, new_tier in SAFE_RETIER:
        a = find_atom_by_short(ps, short)
        if a is None:
            print(f'  MISSING: {short}')
            continue
        if a.tier == new_tier:
            print(f'  SKIP (already at {new_tier.name}): {short}')
            continue
        old_tier = a.tier
        snapshots[short] = a  # save for rollback
        # Atom is a dataclass; use dataclasses.replace
        new_atom = replace(a, tier=new_tier)
        ps._store_for(a.corpus).add_atom(
            new_atom,
            source='tier_reassign_v1_84a',
            note=f'DECISION 84a re-tier {short}: {old_tier.name} -> {new_tier.name}',
        )
        print(f'  RETIERED: {short} {old_tier.name} -> {new_tier.name}')

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)
    print(f'\npost-retier: {post_atoms} atoms, {post_rels} relations, '
          f'axiom_term {post_t}/{post_total}')

    print(f'\n=== STEP 2: R3 verification ===')
    # Confirm re-tiered atoms hold their new tier
    for short, expected_tier in SAFE_RETIER:
        a = find_atom_by_short(ps, short)
        if a is None or a.tier != expected_tier:
            print(f'  TIER_VERIFY_FAIL: {short} tier={a.tier.name if a else "MISSING"}; expected {expected_tier.name}')

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
    if not hard_pass:
        print(f'\nHARD_FAIL detected; rolling back...')
        for short, snap in snapshots.items():
            ps._store_for(snap.corpus).add_atom(
                snap, source='tier_reassign_v1_84a_ROLLBACK',
                note='DECISION 84a ROLLBACK: R3 regression',
            )
            print(f'  ROLLED_BACK: {short} -> {snap.tier.name}')

    print(f'\nSUMMARY:')
    print(f'  re-tiered:       {len(snapshots)} / 2 SAFE targets (gradient_descent + bayes_rule held)')
    print(f'  axiom_term:      {post_t}/{post_total}  (pre: {pre_t}/{pre_total})')
    print(f'  modules:         {"OK" if mod_ok else "FAIL"}')
    print(f'  HARD_PASS:       {hard_pass}')
    print(f'\nTag: SUBSTRATE_HYGIENE_TIER_REASSIGN_v1_PARTIAL')


if __name__ == '__main__':
    main()
