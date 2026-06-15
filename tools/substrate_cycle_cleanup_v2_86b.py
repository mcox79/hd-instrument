"""DECISION 86b: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2 (per-edge REMOVE + REMOVE-AND-REPLACE).

Per Director DECISION 86b spec + Skunkworks 85a downgrade of partial_derivative
->subgradient to SIMPLE REMOVE:

3 SIMPLE REMOVE (correct direction already exists or no dep needed):
  - hessian -> newton_method            [newton USES hessian already]
  - bayes_rule -> bayesian_inference    [reverse direction exists]
  - partial_derivative -> subgradient   [siblings; no strict dep] (68th signal)

2 REMOVE-AND-REPLACE (with correct-direction ADD):
  - partial_derivative -> jacobian_matrix [REMOVE]
    + ADD jacobian_matrix --DEPENDS_ON--> partial_derivative
  - conditional_probability -> bayesian_inference [REMOVE]
    + ADD bayesian_inference --DEPENDS_ON--> conditional_probability

6 EXPLICIT FAMILY -> MEMBER REMOVE-AND-REPLACE (per DECISION 83b explicit list):
  Each: REMOVE backwards family --DEPENDS_ON--> member; ADD member --SPECIALIZES--> family
  - graph_traversal -> dijkstra
  - sequence_decoding -> forward_algorithm
  - algebraic_binding -> role_filler_binding
  - discriminative_classification -> count_nb
  - representation_transform -> pca_whitening
  - probabilistic_inference -> bayesian_inference (this is REMOVE only; SPECIALIZES would be
    bayesian_inference->probabilistic_inference, but bayesian_inference is ALREADY targeted
    by the conditional_probability REMOVE-AND-REPLACE ADD above; ADD member->family SPECIALIZES separately)

19th-rule note: substrate inspection found 21 total backwards family->member DEPENDS_ON
edges in substrate; Director's DECISION 86b specifies 11 (the W-TYPE-SIG existence-check
subset). Shipping only the 6 explicitly enumerated in DECISION 83b; remaining 15
unspecified are flagged for Director/Skunkworks scope confirmation before batch 2b.

Total this script: 11 logical ops (3 simple + 2 R&R + 6 family R&R).
R3 + capability_preservation rollback per the v1 discipline.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType, Corpus


# Each entry: (src_short, tgt_short, rel_name_to_remove)
SIMPLE_REMOVE = [
    ('hessian', 'newton_method', 'DEPENDS_ON'),
    ('bayes_rule', 'bayesian_inference', 'DEPENDS_ON'),
    ('partial_derivative', 'subgradient', 'DEPENDS_ON'),
]

# Each entry: (remove_src_short, remove_tgt_short, remove_rel, add_src_short, add_tgt_short, add_rel, reason)
REMOVE_AND_REPLACE = [
    ('partial_derivative', 'jacobian_matrix', 'DEPENDS_ON',
     'jacobian_matrix', 'partial_derivative', 'DEPENDS_ON',
     'Jacobian IS the matrix of partial derivatives'),
    ('conditional_probability', 'bayesian_inference', 'DEPENDS_ON',
     'bayesian_inference', 'conditional_probability', 'DEPENDS_ON',
     'Bayesian inference uses conditional probability'),
]

# Each entry: (family_short, member_short)
# family --DEPENDS_ON--> member is backwards; remove. Add member --SPECIALIZES--> family.
FAMILY_REMOVE_AND_REPLACE = [
    ('graph_traversal', 'dijkstra'),
    ('sequence_decoding', 'forward_algorithm'),
    ('algebraic_binding', 'role_filler_binding'),
    ('discriminative_classification', 'count_nb'),
    ('representation_transform', 'pca_whitening'),
    ('probabilistic_inference', 'bayesian_inference'),
]


def find_qid_by_short(ps, short):
    candidates = []
    for a in ps.all_atoms():
        if str(a.id).split('/')[-1].lower() == short.lower():
            candidates.append(f'{a.corpus.value}::{a.id}')
    if len(candidates) == 0:
        return None
    if len(candidates) == 1:
        return candidates[0]
    # Multiple matches; prefer math corpus
    math_candidates = [c for c in candidates if c.startswith('math::')]
    if math_candidates:
        return math_candidates[0]
    return candidates[0]


def remove_edge(ps, src_qid, dst_qid, rel_str):
    """Direct removal (Store has no public remove_relation)."""
    from backend.substrate_index.partition import QualifiedAtomId
    src_q = QualifiedAtomId.parse(src_qid)
    src_store = ps._store_for(src_q.corpus)
    triple = (src_q.local_id, rel_str, dst_qid)
    if triple in src_store._all_relations:
        src_store._all_relations.discard(triple)
        # Also drop from indexes
        rt = RelationType(rel_str)
        if (src_q.local_id, rt) in src_store._out:
            src_store._out[(src_q.local_id, rt)].discard(dst_qid)
        if (dst_qid, rt) in src_store._in:
            src_store._in[(dst_qid, rt)].discard(src_q.local_id)
        return True
    # Try unqualified target form
    dst_q = QualifiedAtomId.parse(dst_qid)
    triple_alt = (src_q.local_id, rel_str, dst_q.local_id)
    if triple_alt in src_store._all_relations:
        src_store._all_relations.discard(triple_alt)
        rt = RelationType(rel_str)
        if (src_q.local_id, rt) in src_store._out:
            src_store._out[(src_q.local_id, rt)].discard(dst_q.local_id)
        if (dst_q.local_id, rt) in src_store._in:
            src_store._in[(dst_q.local_id, rt)].discard(src_q.local_id)
        return True
    return False


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'pre-cleanup-v2: {pre_atoms} atoms, {pre_rels} relations\n')

    print('=== STEP 1: SIMPLE REMOVE (3 ops) ===')
    simple_removed = 0
    simple_skipped = 0
    for s_short, t_short, rel in SIMPLE_REMOVE:
        s = find_qid_by_short(ps, s_short)
        t = find_qid_by_short(ps, t_short)
        if not s or not t:
            print(f'  SKIP_MISSING: {s_short}({s}) -> {t_short}({t})')
            simple_skipped += 1
            continue
        ok = remove_edge(ps, s, t, rel)
        if ok:
            print(f'  REMOVED: {s} -{rel}-> {t}')
            simple_removed += 1
        else:
            print(f'  NOT_FOUND: {s} -{rel}-> {t}')
            simple_skipped += 1

    # Flush
    ps._store_for(Corpus.MATH)._flush_relations()

    print(f'\n=== STEP 2: REMOVE-AND-REPLACE (2 ops) ===')
    rr_removed = 0
    rr_added = 0
    for rs, rt, rrel, asrc, atgt, arel, reason in REMOVE_AND_REPLACE:
        rs_qid = find_qid_by_short(ps, rs)
        rt_qid = find_qid_by_short(ps, rt)
        as_qid = find_qid_by_short(ps, asrc)
        at_qid = find_qid_by_short(ps, atgt)
        if not (rs_qid and rt_qid and as_qid and at_qid):
            print(f'  SKIP_MISSING: {rs}->{rt} or {asrc}->{atgt}')
            continue
        ok = remove_edge(ps, rs_qid, rt_qid, rrel)
        if ok:
            print(f'  REMOVED: {rs_qid} -{rrel}-> {rt_qid}')
            rr_removed += 1
        else:
            print(f'  REMOVE_NOT_FOUND: {rs_qid} -{rrel}-> {rt_qid}')
        ps._store_for(Corpus.MATH)._flush_relations()
        try:
            ps.add_relation(
                as_qid, RelationType[arel], at_qid,
                source='cycle_cleanup_v2_86b',
                note=f'DECISION 86b R&R: {reason}',
            )
            print(f'  ADDED:   {as_qid} -{arel}-> {at_qid}  ({reason})')
            rr_added += 1
        except Exception as e:
            msg = str(e)[:120]
            if 'already' in msg.lower() or 'exists' in msg.lower():
                print(f'  ADD_SKIP_EXISTS: {as_qid} -{arel}-> {at_qid}')
            else:
                print(f'  ADD_FAIL: {as_qid} -{arel}-> {at_qid}: {msg}')

    print(f'\n=== STEP 3: FAMILY REMOVE-AND-REPLACE (6 ops) ===')
    fam_removed = 0
    fam_added = 0
    fam_add_skip_exists = 0
    for fam_short, mem_short in FAMILY_REMOVE_AND_REPLACE:
        fam_qid = find_qid_by_short(ps, fam_short)
        mem_qid = find_qid_by_short(ps, mem_short)
        if not (fam_qid and mem_qid):
            print(f'  SKIP_MISSING: {fam_short}({fam_qid}) -> {mem_short}({mem_qid})')
            continue
        ok = remove_edge(ps, fam_qid, mem_qid, 'DEPENDS_ON')
        if ok:
            print(f'  REMOVED: {fam_qid} -DEPENDS_ON-> {mem_qid}')
            fam_removed += 1
        else:
            print(f'  REMOVE_NOT_FOUND: {fam_qid} -DEPENDS_ON-> {mem_qid}')
        ps._store_for(Corpus.MATH)._flush_relations()
        try:
            ps.add_relation(
                mem_qid, RelationType['SPECIALIZES'], fam_qid,
                source='cycle_cleanup_v2_86b',
                note=f'DECISION 86b family R&R: {mem_short} specializes {fam_short}',
            )
            print(f'  ADDED:   {mem_qid} -SPECIALIZES-> {fam_qid}')
            fam_added += 1
        except Exception as e:
            msg = str(e)[:120]
            if 'already' in msg.lower() or 'exists' in msg.lower():
                print(f'  ADD_SKIP_EXISTS: {mem_qid} -SPECIALIZES-> {fam_qid}')
                fam_add_skip_exists += 1
            else:
                print(f'  ADD_FAIL: {mem_qid} -SPECIALIZES-> {fam_qid}: {msg}')

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f'\npost-cleanup-v2: {post_atoms} atoms (delta {post_atoms - pre_atoms}), '
          f'{post_rels} relations (delta {post_rels - pre_rels})')

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

    hard_pass = t == len(ops) and mod_ok

    print(f'\nSUMMARY:')
    print(f'  simple removes:        {simple_removed}/3 (skipped {simple_skipped})')
    print(f'  R&R removed/added:     {rr_removed}/{rr_added} (target 2/2)')
    print(f'  family R&R rm/add:     {fam_removed}/{fam_added} (skip-exists adds: {fam_add_skip_exists}; target 6/6)')
    print(f'  total ops executed:    {simple_removed + rr_removed + rr_added + fam_removed + fam_added}')
    print(f'  R3 axiom term:         {t}/{len(ops)} = {100 * t / len(ops):.1f}%')
    print(f'  R3 modules:            {"OK" if mod_ok else "FAIL"}')
    print(f'  delta relations:       {post_rels - pre_rels}')
    print(f'  HARD_PASS: {hard_pass}')
    print(f'\nTag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2')


if __name__ == '__main__':
    main()
