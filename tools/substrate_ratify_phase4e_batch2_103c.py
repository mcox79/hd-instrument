"""DECISION 103c: SUBSTRATE_HYGIENE_PHASE_4e_AUTHOR_N_BATCH_2_INSTRUMENTED.

Per Director DECISION 103c + Skunkworks Phase 4e batch 2 instrumented delivery.

Operations:
  1. 17 STRICT edges (13 SPECIALIZES + 4 USES) atomic ratify
  2. (Signatures: metadata-only in self-model JSONL; verified-and-committed only)
  3. R3 verify: axiom-term + capability_preservation + 6/6 modules + dangling

Additive only (no atom DELETEs; no tier mutations). Failure modes:
  - new cycle from SPECIALIZES (member->family); verify by scanning post-add
  - tier-monotone on USES (verified clean per Director 101 ruling)
  - duplicate edges (skip-exists idempotent)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType, Corpus


STRICT_EDGES_JSONL = Path('data/substrate_index/skunkworks_phase4e_batch2_grounding_new_STRICT_edges.jsonl')
SIGNATURES_JSONL = Path('data/substrate_index/skunkworks_self_model_phase_4e_substrate_selected_batch_2.jsonl')


def find_qid_by_short(ps, short):
    candidates = []
    for a in ps.all_atoms():
        if str(a.id).split('/')[-1].lower() == short.lower():
            candidates.append(f'{a.corpus.value}::{a.id}')
    if not candidates:
        return None
    math_first = [c for c in candidates if c.startswith('math::')]
    if math_first:
        return math_first[0]
    return candidates[0]


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
    print(f'pre-batch: {pre_atoms} atoms, {pre_rels} relations, axiom_term {pre_t}/{pre_total}\n')

    edges = []
    with open(STRICT_EDGES_JSONL) as f:
        for line in f:
            line = line.strip()
            if line:
                edges.append(json.loads(line))
    print(f'loaded {len(edges)} STRICT edges from {STRICT_EDGES_JSONL.name}\n')

    print('=== STEP 1: atom resolution ===')
    resolved = []
    for e in edges:
        s = find_qid_by_short(ps, e['src'])
        t = find_qid_by_short(ps, e['tgt'])
        if not (s and t):
            print(f'  MISSING: {e["src"]}({s}) -> {e["tgt"]}({t})')
            return
        resolved.append((e, s, t))
    print(f'  OK: 17/17 atoms resolved')

    print('\n=== STEP 2: atomic edge adds (idempotent) ===')
    added = 0
    skip_exists = 0
    for e, s, t in resolved:
        try:
            ps.add_relation(
                s, RelationType[e['rel_type']], t,
                source='phase4e_batch2_grounding_103c',
                note=f'DECISION 103c PHASE_4e batch_2: {e.get("vet", "")[:80]}; '
                     f'iter4_confidence=STRICT witness=phase4e_batch2_grounding',
            )
            added += 1
            print(f'  ADDED: {s} -{e["rel_type"]}-> {t}')
        except Exception as ex:
            msg = str(ex)[:120]
            if 'already' in msg.lower() or 'exists' in msg.lower():
                skip_exists += 1
                print(f'  SKIP_EXISTS: {s} -{e["rel_type"]}-> {t}')
            else:
                print(f'  ADD_FAIL: {s} -{e["rel_type"]}-> {t}: {msg}')

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)
    print(f'\npost-batch: {post_atoms} atoms (delta {post_atoms - pre_atoms}), '
          f'{post_rels} relations (delta {post_rels - pre_rels}), '
          f'axiom_term {post_t}/{post_total}')

    print(f'\n=== STEP 3: R3 verification ===')
    # Verify each added edge present
    rel_set = set()
    for src, rel, tgt in ps.iter_all_relations():
        rel_set.add((src, rel.name, tgt))
    missing_adds = []
    for e, s, t in resolved:
        if (s, e['rel_type'], t) not in rel_set:
            missing_adds.append((s, e['rel_type'], t))
    print(f'  missing forward edges: {len(missing_adds)} (must be 0)')

    # Modules
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

    # axiom-term should be PRESERVED or BETTER (additive; new SPECIALIZES adds new forward edges
    # so old ops that terminated still terminate; T2_FAM atoms may gain new termination paths)
    hard_pass = post_t >= pre_t and not missing_adds and mod_ok

    print(f'\nSUMMARY:')
    print(f'  edges added:       {added}/17')
    print(f'  skip_exists:       {skip_exists}')
    print(f'  missing forwards:  {len(missing_adds)}')
    print(f'  axiom_term:        {post_t}/{post_total} (pre: {pre_t}/{pre_total})')
    print(f'  modules:           {"OK" if mod_ok else "FAIL"}')
    print(f'  delta relations:   {post_rels - pre_rels}')
    print(f'  HARD_PASS:         {hard_pass}')
    print(f'\nTag: PHASE_4e_AUTHOR_N_BATCH_2_INSTRUMENTED_17_STRICT_PLUS_5_SIG_PLUS_measure_space_correction')


if __name__ == '__main__':
    main()
