"""DECISION 79a: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v1 - FIRST non-additive workstream.

Per Director DECISION 79a:
- Apply 9 edge REMOVALS (resolve direction-ambiguous 2-cycles per Skunkworks vet)
- Apply 1 INVERSE_PAIR re-type for fhrr_bind <-> fhrr_unbind (remove both
  DEPENDS_ON; add INVERSE_PAIR)
- R3 invariants must HOLD or IMPROVE
- ROLLBACK if any capability_preservation regression

This is the substrate's FIRST removal-based workstream. Atomic discipline.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import RelationType


# (src_short, dst_short) -- direction TO REMOVE (the sound KEEP is the reverse)
REMOVALS = [
    ('singular_value_decomposition', 'pseudoinverse'),
    ('graph_topology', 'bipartite_graph'),
    ('partial_derivative', 'gradient'),
    ('metric_space', 'euclidean_distance'),
    ('derivative', 'gradient'),
    ('conditional_probability', 'bayes_rule'),
    ('measure_space', 'probability_space'),
    ('gradient', 'gradient_descent'),
    ('inner_product', 'cosine_similarity'),
]

INVERSE_PAIR_RETYPE = [
    # Remove both DEPENDS_ON; add INVERSE_PAIR (genuine mutual inverses)
    ('fhrr_bind', 'fhrr_unbind'),
]


def find_qid_by_short(ps, short):
    for a in ps.all_atoms():
        if str(a.id).split('/')[-1].lower() == short.lower():
            return f'{a.corpus.value}::{a.id}'
    return None


def remove_edge(ps, src_qid, dst_qid, rel_str='DEPENDS_ON'):
    """Direct removal from underlying store (Store doesn't expose remove_relation publicly)."""
    src_q = QualifiedAtomId.parse(src_qid)
    src_store = ps._store_for(src_q.corpus)
    triple = (src_q.local_id, rel_str, dst_qid)
    if triple in src_store._all_relations:
        src_store._all_relations.discard(triple)
        return True
    # Try unqualified target form
    dst_q = QualifiedAtomId.parse(dst_qid)
    triple_alt = (src_q.local_id, rel_str, dst_q.local_id)
    if triple_alt in src_store._all_relations:
        src_store._all_relations.discard(triple_alt)
        return True
    return False


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_atoms = len(ps.all_atoms())
    print(f'pre-cleanup: {pre_atoms} atoms, {pre_rels} relations\n')

    # Pre-cleanup snapshot for R3 verification
    print('=== STEP 1: edge removals ===')
    removed = 0
    not_found = 0
    for src_short, dst_short in REMOVALS:
        src_qid = find_qid_by_short(ps, src_short)
        dst_qid = find_qid_by_short(ps, dst_short)
        if not src_qid or not dst_qid:
            print(f'  SKIP_MISSING: {src_short} or {dst_short}')
            not_found += 1
            continue
        ok = remove_edge(ps, src_qid, dst_qid)
        if ok:
            print(f'  REMOVED: {src_qid} -DEPENDS_ON-> {dst_qid}')
            removed += 1
        else:
            print(f'  NOT_FOUND: {src_qid} -DEPENDS_ON-> {dst_qid}')
            not_found += 1

    # Flush math store
    ps._store_for(ps._store_for.__self__.all_atoms()[0].corpus if False else __import__('backend.substrate_index.schema', fromlist=['Corpus']).Corpus.MATH)._flush_relations()

    print(f'\\n=== STEP 2: INVERSE_PAIR re-type (fhrr_bind <-> fhrr_unbind) ===')
    bind_qid = find_qid_by_short(ps, 'fhrr_bind')
    unbind_qid = find_qid_by_short(ps, 'fhrr_unbind')
    pair_removed = 0
    if bind_qid and unbind_qid:
        # Remove both DEPENDS_ON directions
        for src, dst in ((bind_qid, unbind_qid), (unbind_qid, bind_qid)):
            if remove_edge(ps, src, dst, 'DEPENDS_ON'):
                pair_removed += 1
                print(f'  REMOVED DEPENDS_ON: {src} -> {dst}')

        # Flush before add
        from backend.substrate_index.schema import Corpus
        ps._store_for(Corpus.MATH)._flush_relations()

        # Add INVERSE_PAIR... but check if RelationType has INVERSE_PAIR
        try:
            inv_pair = RelationType['INVERSE_PAIR']
            # Symmetric
            for src, dst in ((bind_qid, unbind_qid), (unbind_qid, bind_qid)):
                try:
                    ps.add_relation(src, inv_pair, dst,
                                    source='cycle_cleanup_v1_79a',
                                    note='DECISION 79a INVERSE_PAIR re-type; genuine mutual inverses')
                    print(f'  ADDED INVERSE_PAIR: {src} <-> {dst}')
                except Exception as e:
                    print(f'  ADD_FAIL: {str(e)[:80]}')
        except KeyError:
            # Fallback: use DUAL or EQUIVALENT_UNDER
            try:
                rel = RelationType['DUAL']
                for src, dst in ((bind_qid, unbind_qid), (unbind_qid, bind_qid)):
                    try:
                        ps.add_relation(src, rel, dst,
                                        source='cycle_cleanup_v1_79a',
                                        note='DECISION 79a INVERSE_PAIR via DUAL fallback')
                        print(f'  ADDED DUAL: {src} <-> {dst}')
                    except Exception:
                        pass
            except KeyError:
                print(f'  WARN: neither INVERSE_PAIR nor DUAL in schema; INVERSE_PAIR re-type SKIPPED')

    # Final R3 verification
    print(f'\\n=== STEP 3: R3 verification ===')
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_atoms = len(ps.all_atoms())
    print(f'atoms: {pre_atoms} -> {post_atoms}')
    print(f'relations: {pre_rels} -> {post_rels}  (delta: {post_rels - pre_rels})')

    # Axiom termination check
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
        seen={s}; f=[s]
        for _ in range(d):
            n=[]
            for x in f:
                if x in axioms: return True
                for t in forward.get(x, []):
                    if t not in seen: seen.add(t); n.append(t)
            f=n
            if not f: break
        return any(x in axioms for x in seen)
    ops = [a for a in ps.all_atoms()
           if str(a.corpus.name)=='MATH'
           and str(a.tier.name) in ('TIER_2_PRIMITIVE','TIER_3_ALGORITHM')
           and a.algebra and len(a.algebra) >= 3
           and 'oeis' not in str(a.id).lower()
           and not str(a.id).startswith('T3/wikidata_')]
    t = sum(1 for op in ops if terminates(f'math::{op.id}'))
    print(f'axiom termination: {t}/{len(ops)} = {100*t/len(ops):.1f}%')

    # Module imports
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
    print(f'Tier 1+2 modules: {"ALL OK" if mod_ok else "FAIL -- ROLLBACK CANDIDATE"}')

    print(f'\\nSUMMARY:')
    print(f'  edges removed: {removed} (of {len(REMOVALS)} target)')
    print(f'  inverse-pair dual-direction removed: {pair_removed}')
    print(f'  R3 axiom term: {t}/{len(ops)}')
    print(f'  R3 modules: {"OK" if mod_ok else "FAIL"}')
    print(f'\\nTag: SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v1')


if __name__ == '__main__':
    main()
