"""Rollback compositional_depth FORM-C entry per DECISION 148a HOLD.

REASON: Smoke-mode K10/15/20=1.0 was INFLATED (smaller N = less interference); full-mode shows
L5>=0.70 / L8>=0.30. The d5deb37b ratify bound the inflated smoke numbers; capability is REAL
but at lower full-mode numbers. Per Skunkworks's stronger finding + Director DECISION 148a HOLD,
revert this entry; re-spec FORM-C on full-mode metrics when Exp-Dev's rerun lands.

Surgical filter: remove the single solution_history entry whose source tag matches the
form_c_decision_147b_skunkworks_release_n1_single_seed_stamp_accepted ratify. Atomic; reversible
(other 2 pre-existing entries preserved).
"""
from __future__ import annotations
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId


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
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    target_source = 'form_c_decision_147b_skunkworks_release_n1_single_seed_stamp_accepted'
    cap_qid = QualifiedAtomId.parse('concept::PP-compositional_depth_retrieval')
    concept_store = ps._store_for(cap_qid.corpus)
    cap = concept_store.get_atom(cap_qid.local_id)
    if cap is None:
        print('HARD_FAIL: PP-compositional_depth_retrieval missing')
        return 1

    existing = tuple(cap.solution_history or ())
    pre_sh_n = len(existing)
    filtered = tuple(e for e in existing if e.get('source') != target_source)
    removed_n = pre_sh_n - len(filtered)

    if removed_n != 1:
        print(f'HARD_FAIL: expected 1 entry with source={target_source}; found {removed_n}')
        return 1

    cap_new = replace(cap, solution_history=filtered)
    concept_store.add_atom(cap_new)
    concept_store._flush_atoms()

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)

    import importlib
    mod_ok = all(hasattr(importlib.import_module(m_), s) for m_, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])

    cap_check = ps._store_for(cap_qid.corpus).get_atom(cap_qid.local_id)
    post_sh_n = len(cap_check.solution_history or ())

    invariants_ok = (
        post_atoms == pre_atoms       # additive metadata rollback: atom count unchanged
        and post_rels == pre_rels     # no relation change
        and post_t == pre_t           # axiom-term preserved
        and post_total == pre_total
        and mod_ok                    # cap_pres=1.0 still holds
        and post_sh_n == pre_sh_n - 1 # 1 entry removed
    )

    print(f'post: atoms={post_atoms} rels={post_rels} axiom_term={post_t}/{post_total} '
          f'mod_ok={mod_ok} sh_entries={pre_sh_n}->{post_sh_n} (removed={removed_n})', flush=True)

    if not invariants_ok:
        print('HARD_FAIL: R3 invariant violation on rollback')
        return 1

    print('R3 verify: PASS (rollback additive-undo; cap_pres=1.0; axiom_term unchanged)')
    print('HARD_PASS: compositional_depth FORM-C entry ROLLED BACK per DECISION 148a HOLD')
    return 0


if __name__ == '__main__':
    sys.exit(main())
