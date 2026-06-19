"""E2 re-typing: REPLACE the RELATES+dropped-role edges with first-class typed rel_types (TRACK-3; Skunkworks ruling 4).

Per [[reference_store_drops_relation_edge_metadata]]: relation_role on a RELATES edge is SILENTLY DROPPED on flush
(3-tuple persistence). Making the role the REL_TYPE persists it -> edge-queryable. This REPLACES (not duplicates) the
4 known role-bearing RELATES edges with STRENGTHENS / MECHANISM_FOR (the roles previously only on source-atom metadata).

Skunkworks cert-condition: old RELATES REPLACED not duplicated (same endpoints, type changed; 0-phantom preserved; no
double-edge). All within-corpus (MATH); LOCAL ids. Scoped + idempotent + gated. ASCII-only. No LLM.
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Corpus, RelationType, Relation

# (src_local, tgt_local) -> new typed RelationType  (all MATH within-corpus; the role was on source-atom metadata)
RETYPE = {
    ('T3/EXP_a1v2_ratio_profile_v1', 'T3/EXP_a1_8a_4channel_attribution_v1'): RelationType.MECHANISM_FOR,
    ('T3/EXP_a1v2_ratio_profile_v1', 'T3/EXP_active_gating_8a_break_even_v1_measured'): RelationType.MECHANISM_FOR,
    ('T3/EXP_a1_8a_4channel_attribution_v1', 'T3/EXP_active_gating_8a_break_even_v1_measured'): RelationType.MECHANISM_FOR,
    ('T3/EXP_c1_entmax_envelope_sweep_v2', 'T3/EXP_substrate_C1_entmax_alpha_readout_v1'): RelationType.STRENGTHENS,
}


def module_liveness_ok() -> bool:
    import importlib
    return all(
        hasattr(importlib.import_module(m), s)
        for m, s in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ]
    )


def axiom_term_count(ps) -> int:
    return sum(
        1 for a in ps.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def _flush_with_retry(cstore, attempts=12):
    for attempt in range(attempts):
        try:
            cstore._flush_relations()
            return True
        except PermissionError:
            time.sleep(0.3 * (attempt + 1))
    return False


def main() -> int:
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE: axiom_term={pre_axiom}  cap_pres={pre_mod}')
    if not pre_mod or pre_axiom != 206:
        print('PRE-GATE FAIL. Halt.')
        return 1

    math = ps._store_for(Corpus.MATH)
    pre_rel = len(math._all_relations)
    retyped, skipped = [], []
    for (src, tgt), new_rt in RETYPE.items():
        # 0-phantom: both endpoints must exist
        if ps.get_atom(f'math::{src}') is None or ps.get_atom(f'math::{tgt}') is None:
            print(f'PHANTOM-SKIP: {src} -> {tgt} (endpoint missing)')
            skipped.append((src, tgt))
            continue
        old = (src, RelationType.RELATES.value, tgt)
        new = (src, new_rt.value, tgt)
        if new in math._all_relations and old not in math._all_relations:
            print(f'ALREADY-TYPED (idempotent): {src} -{new_rt.value}-> {tgt}')
            continue
        # discard the old RELATES triple (+ its _out/_in indexing)
        if old in math._all_relations:
            math._all_relations.discard(old)
            math._out[(src, RelationType.RELATES)].discard(tgt)
            math._in[(tgt, RelationType.RELATES)].discard(src)
        # add the typed edge (proper indexing)
        math._index_relation(Relation(src_id=src, tgt_id=tgt, rel_type=new_rt))
        retyped.append((src, new_rt.value, tgt))

    if not _flush_with_retry(math):
        print('HARD_FAIL: os.replace race on relations flush.')
        return 3

    # verify-the-referent (fresh reload): typed present + RELATES gone (replace-not-duplicate)
    ps2 = PartitionedStore(Path('data/substrate_index'))
    math2 = ps2._store_for(Corpus.MATH)
    post_rel = len(math2._all_relations)
    post_axiom = axiom_term_count(ps2)
    ok = True
    for (src, tgt), new_rt in RETYPE.items():
        if (src, tgt) in skipped:
            continue
        has_typed = (src, new_rt.value, tgt) in math2._all_relations
        has_old = (src, RelationType.RELATES.value, tgt) in math2._all_relations
        print(f'  {src} -> {tgt}: typed({new_rt.value})={has_typed}  old_RELATES_gone={not has_old}')
        if not has_typed or has_old:
            ok = False
    print(f'POST: relations {pre_rel} -> {post_rel} (retyped {len(retyped)}; replace-not-add -> count delta ~0)  axiom_term={post_axiom}')
    if not ok or post_axiom != 206:
        print('HARD_FAIL: re-type verify failed (typed missing OR old RELATES still present OR axiom_term moved).')
        return 2
    print('=' * 72)
    print(f'E2 re-typing complete: {len(retyped)} RELATES -> first-class typed (STRENGTHENS/MECHANISM_FOR); replace-not-duplicate; axiom_term 206')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
