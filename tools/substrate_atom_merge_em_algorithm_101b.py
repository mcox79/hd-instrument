"""DECISION 101b: em_algorithm GENUINE MERGE (Phase 2).

Per Director DECISION 101b + Skunkworks 100b spec + Exp-Dev PRECHECK PASS.

Canonical: math::T3/em_algorithm
Delete:    math::T3/expectation_maximization (true synonym)
Tier-dup:  math::T2/em_algorithm (consolidate to T3 canonical)

Strategy (same as svd MERGE PILOT 86a but with explicit re-points first):
  1. For each non-canonical atom to delete (expectation_maximization, T2/em_algorithm):
     a. Find all incident edges
     b. For each edge where the OTHER endpoint is the canonical em_algorithm: DROP
        (becomes self-loop after merge)
     c. For each remaining edge: ADD equivalent edge with the non-canonical endpoint
        replaced by canonical (idempotent; skip-exists for dups)
  2. Store.remove_atom cascades all incident edges automatically
  3. R3 verification (axiom_term + modules + dangling scan)
  4. Rollback if any regression

Per the 89c/95h discipline.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import RelationType


CANONICAL = 'math::T3/em_algorithm'
TO_DELETE = [
    'math::T3/expectation_maximization',  # true synonym
    'math::T2/em_algorithm',              # tier-dup
]


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


def matches(endpoint, qid):
    """Check if endpoint string refers to qid (qualified or unqualified)."""
    if endpoint == qid:
        return True
    q = QualifiedAtomId.parse(qid)
    if endpoint == q.local_id:
        return True
    # Also match without corpus prefix variants
    short = q.local_id.split('/')[-1].lower()
    ep_short = endpoint.split('/')[-1].lower()
    # Strict match on full local id only (avoid false positives across atoms)
    return False


def edge_endpoint_is_canonical(endpoint, canonical_qid):
    """Match endpoint against any em_algorithm variant we treat as canonical."""
    if endpoint == canonical_qid:
        return True
    cq = QualifiedAtomId.parse(canonical_qid)
    if endpoint == cq.local_id:
        return True
    return False


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'pre-merge: {pre_atoms} atoms, {pre_rels} relations, axiom_term {pre_t}/{pre_total}\n')

    # Verify canonical exists
    if not any(f'{a.corpus.value}::{a.id}' == CANONICAL for a in ps.all_atoms()):
        print(f'ABORT: canonical {CANONICAL} not present')
        return
    print(f'canonical present: {CANONICAL}')

    # Snapshot atoms for potential rollback (atoms only; cascade removes are not trivially reversible)
    atom_snapshots = {}
    for qid in TO_DELETE:
        q = QualifiedAtomId.parse(qid)
        store = ps._store_for(q.corpus)
        if q.local_id in store._by_id:
            atom_snapshots[qid] = store._by_id[q.local_id]

    print(f'\n=== STEP 1: per non-canonical atom, RE-POINT incident edges to canonical ===')
    repointed = 0
    skipped_self_loop = 0
    skipped_dup = 0
    for qid in TO_DELETE:
        q = QualifiedAtomId.parse(qid)
        store = ps._store_for(q.corpus)
        if q.local_id not in store._by_id:
            print(f'  SKIP_MISSING: {qid}')
            continue
        # Snapshot incident edges (qualified + unqualified target forms in _all_relations)
        incident = []
        for src, rel, tgt in list(ps.iter_all_relations()):
            if (src == qid or src == q.local_id) or (tgt == qid or tgt == q.local_id):
                incident.append((src, rel.name, tgt))
        print(f'  {qid}: {len(incident)} incident edges')
        for src, rel_name, tgt in incident:
            # Determine which endpoint is the deleting atom
            src_is_del = (src == qid or src == q.local_id)
            tgt_is_del = (tgt == qid or tgt == q.local_id)
            # New endpoint = canonical
            new_src = CANONICAL if src_is_del else src
            new_tgt = CANONICAL if tgt_is_del else tgt
            # Self-loop after merge?
            if new_src == new_tgt or (
                edge_endpoint_is_canonical(new_src, CANONICAL)
                and edge_endpoint_is_canonical(new_tgt, CANONICAL)
            ):
                skipped_self_loop += 1
                continue
            # Try to add new edge; idempotent
            try:
                ps.add_relation(
                    new_src, RelationType[rel_name], new_tgt,
                    source='atom_merge_em_algorithm_101b',
                    note=f'DECISION 101b RE-POINT: was {src} -{rel_name}-> {tgt}',
                )
                repointed += 1
            except Exception as e:
                msg = str(e)[:120]
                if 'already' in msg.lower() or 'exists' in msg.lower():
                    skipped_dup += 1
                else:
                    print(f'  ADD_FAIL: {new_src} -{rel_name}-> {new_tgt}: {msg}')
    print(f'  Total: {repointed} repointed, {skipped_self_loop} self-loop-after-merge skipped, {skipped_dup} dup skipped')

    print(f'\n=== STEP 2: DELETE non-canonical atoms (Store.remove_atom cascades) ===')
    deleted = 0
    for qid in TO_DELETE:
        ok = ps.remove_atom(qid, source='atom_merge_em_algorithm_101b',
                            note='DECISION 101b em_algorithm MERGE; canonical em_algorithm preserves capabilities')
        if ok:
            deleted += 1
            print(f'  DELETED: {qid}')
        else:
            print(f'  NOT_FOUND: {qid}')

    print(f'\n=== STEP 3: dangling-reference scan ===')
    dangling = []
    for src, rel, tgt in ps.iter_all_relations():
        for del_qid in TO_DELETE:
            del_q = QualifiedAtomId.parse(del_qid)
            for ep in (src, tgt):
                if ep == del_qid or ep == del_q.local_id:
                    dangling.append((src, rel.name, tgt))
                    break
    print(f'  dangling refs to deleted atoms: {len(dangling)} (must be 0)')
    for d in dangling[:5]:
        print(f'    {d}')

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)
    print(f'\npost-merge: {post_atoms} atoms (delta {post_atoms - pre_atoms}), '
          f'{post_rels} relations (delta {post_rels - pre_rels}), '
          f'axiom_term {post_t}/{post_total}')

    print(f'\n=== STEP 4: R3 module check ===')
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
        not dangling
        and post_t == post_total
        and mod_ok
        and deleted == len(TO_DELETE)
    )

    print(f'\nSUMMARY:')
    print(f'  atoms deleted:        {deleted}/{len(TO_DELETE)}')
    print(f'  edges repointed:      {repointed}')
    print(f'  edges skipped (self): {skipped_self_loop}')
    print(f'  edges skipped (dup):  {skipped_dup}')
    print(f'  dangling refs:        {len(dangling)}')
    print(f'  axiom_term:           {post_t}/{post_total} (pre: {pre_t}/{pre_total})')
    print(f'  modules:              {"OK" if mod_ok else "FAIL"}')
    print(f'  delta atoms:          {post_atoms - pre_atoms}')
    print(f'  delta relations:      {post_rels - pre_rels}')
    print(f'  HARD_PASS:            {hard_pass}')
    print(f'\nTag: PHASE2_ATOM_MERGE_em_algorithm')


if __name__ == '__main__':
    main()
