"""DECISION 109b-2: Phase 3 Sub-batch 1 Tier 1B -- 4 convention-dup MERGEs with cross-store cleanup.

Per Director DECISION 109b-2 + Skunkworks 108a vet + 109a spurious-drop ruling.

4 merges:
  math::T3/viterbi_decoder            -> math::T3/viterbi_decoding (canonical)
  math::T3/forward_algorithm_atom     -> math::T3/forward_algorithm
  math::T3/backward_algorithm_atom    -> math::T3/backward_algorithm
  math::T1/shannon_entropy_atom       -> math::T1/shannon_entropy

Per merge:
  - For each incident edge: re-point to canonical (idempotent skip-exists) UNLESS:
    * Self-loop with canonical (drop)
    * Spurious-drop edge per 109a ruling (drop)
    * HAS_USERS auto-reverse (skip; regenerates from USES)
  - ps.remove_atom(delete) cascades within-math
  - cross_store_cleanup primitive (105c) for cross-store dangling

Spurious drops per 109a ruling:
  forward_algorithm_atom -DEPENDS_ON-> viterbi_decoding (sibling, not dependency)
  backward_algorithm_atom -DEPENDS_ON-> forward_algorithm (DUAL is the correct relation)
  viterbi_decoder -DEPENDS_ON-> brownian_motion (already gone post-Tier-1A but check)
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import RelationType, Corpus
from tools.substrate_cross_store_cleanup_v1 import cross_store_cleanup


# (delete_qid, canonical_qid, [spurious-drop (src_qid, rel_str, tgt_qid)])
MERGES = [
    ('math::T3/viterbi_decoder', 'math::T3/viterbi_decoding',
     [('math::T3/viterbi_decoder', 'DEPENDS_ON', 'math::T1/brownian_motion')]),
    ('math::T3/forward_algorithm_atom', 'math::T3/forward_algorithm',
     [('math::T3/forward_algorithm_atom', 'DEPENDS_ON', 'math::T3/viterbi_decoding')]),
    ('math::T3/backward_algorithm_atom', 'math::T3/backward_algorithm',
     [('math::T3/backward_algorithm_atom', 'DEPENDS_ON', 'math::T3/forward_algorithm')]),
    ('math::T1/shannon_entropy_atom', 'math::T1/shannon_entropy',
     []),
]


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


def merge_atom(ps, delete_qid, canonical_qid, spurious_drops):
    """Re-point all incident edges from delete_qid to canonical_qid, then delete + cross-store cleanup."""
    spurious_set = set()
    for sd_src, sd_rel, sd_tgt in spurious_drops:
        spurious_set.add((sd_src, sd_rel, sd_tgt))
        sd_src_local = QualifiedAtomId.parse(sd_src).local_id if '::' in sd_src else sd_src
        sd_tgt_local = QualifiedAtomId.parse(sd_tgt).local_id if '::' in sd_tgt else sd_tgt
        spurious_set.add((sd_src_local, sd_rel, sd_tgt))
        spurious_set.add((sd_src, sd_rel, sd_tgt_local))
        spurious_set.add((sd_src_local, sd_rel, sd_tgt_local))

    incident = []
    for src, rel, tgt in list(ps.iter_all_relations()):
        if (matches_endpoint(src, delete_qid)
                or matches_endpoint(tgt, delete_qid)):
            incident.append((src, rel.name, tgt))

    added = 0
    skipped = 0
    for src, rel_name, tgt in incident:
        # Skip HAS_USERS auto-reverses (regenerate on USES add)
        if rel_name == 'HAS_USERS':
            skipped += 1
            continue
        # Replace delete endpoint with canonical
        new_src = canonical_qid if matches_endpoint(src, delete_qid) else src
        new_tgt = canonical_qid if matches_endpoint(tgt, delete_qid) else tgt
        # Self-loop after merge? skip
        if matches_endpoint(new_src, canonical_qid) and matches_endpoint(new_tgt, canonical_qid):
            skipped += 1
            continue
        # Spurious drop?
        if (src, rel_name, tgt) in spurious_set:
            skipped += 1
            print(f'    SPURIOUS_DROP: {src} -{rel_name}-> {tgt}')
            continue
        # Add new canonical-targeted edge (idempotent)
        try:
            ps.add_relation(new_src, RelationType[rel_name], new_tgt,
                            source='phase3_tier_1B_109b2',
                            note=f'DECISION 109b-2 merge: was {src} -{rel_name}-> {tgt}')
            added += 1
        except Exception as e:
            msg = str(e)[:100]
            if 'already' in msg.lower() or 'exists' in msg.lower():
                skipped += 1
            else:
                print(f'    ADD_FAIL: {new_src} -{rel_name}-> {new_tgt}: {msg}')

    # Delete atom (cascades within-math)
    ok = ps.remove_atom(delete_qid, source='phase3_tier_1B_109b2',
                        note='DECISION 109b-2 Tier 1B convention-dup MERGE')

    # Cross-store cleanup
    cleaned = cross_store_cleanup(ps, delete_qid, execute=True)

    return added, skipped, len(cleaned), ok


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'pre-tier-1B: {pre_atoms} atoms, {pre_rels} relations, axiom_term {pre_t}/{pre_total}\n')

    total_added = 0
    total_skipped = 0
    total_cross_cleaned = 0
    deleted = 0
    for del_qid, canon_qid, drops in MERGES:
        print(f'=== MERGE: {del_qid} -> {canon_qid} ===')
        if not any(f'{a.corpus.value}::{a.id}' == del_qid for a in ps.all_atoms()):
            print(f'  SKIP: {del_qid} not present')
            continue
        if not any(f'{a.corpus.value}::{a.id}' == canon_qid for a in ps.all_atoms()):
            print(f'  ABORT: canonical {canon_qid} not present')
            return
        added, skipped, xcleaned, ok = merge_atom(ps, del_qid, canon_qid, drops)
        print(f'  re-points added:    {added}')
        print(f'  re-points skipped:  {skipped}')
        print(f'  cross-store clean:  {xcleaned}')
        print(f'  atom deleted:       {ok}')
        if ok:
            deleted += 1
        total_added += added
        total_skipped += skipped
        total_cross_cleaned += xcleaned
        print()

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)
    print(f'post-tier-1B: {post_atoms} atoms (delta {post_atoms - pre_atoms}), '
          f'{post_rels} relations (delta {post_rels - pre_rels}), '
          f'axiom_term {post_t}/{post_total}')

    # Final dangling scan
    print(f'\n=== final dangling scan ===')
    deleted_qids = {m[0] for m in MERGES}
    deleted_locals = {QualifiedAtomId.parse(q).local_id for q in deleted_qids}
    dangling = []
    for src, rel, tgt in ps.iter_all_relations():
        for d in deleted_qids | deleted_locals:
            if src == d or tgt == d:
                dangling.append((src, rel.name, tgt))
                break
    print(f'  dangling refs: {len(dangling)} (must be 0)')
    for d in dangling[:5]:
        print(f'    {d}')

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
        deleted == len(MERGES)
        and not dangling
        and post_t == post_total
        and mod_ok
    )

    print(f'\nSUMMARY:')
    print(f'  atoms deleted:     {deleted}/{len(MERGES)}')
    print(f'  re-points added:   {total_added}')
    print(f'  re-points skipped: {total_skipped}')
    print(f'  cross-store clean: {total_cross_cleaned}')
    print(f'  dangling refs:     {len(dangling)}')
    print(f'  axiom_term:        {post_t}/{post_total} (pre: {pre_t}/{pre_total})')
    print(f'  modules:           {"OK" if mod_ok else "FAIL"}')
    print(f'  delta atoms:       {post_atoms - pre_atoms}')
    print(f'  delta relations:   {post_rels - pre_rels}')
    print(f'  HARD_PASS:         {hard_pass}')
    print(f'\nTag: PHASE_3_SUBBATCH_1_TIER_1B_4_MERGES')


if __name__ == '__main__':
    main()
