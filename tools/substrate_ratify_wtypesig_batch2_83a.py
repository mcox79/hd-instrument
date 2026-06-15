"""DECISION 83a: atomic ratify 8 STRICT W-TYPE-SIG edges (Phase 4a batches 3+4).

Skunkworks existence-checked all 24 candidates (per DECISION 78 lesson; no 0-new
over-claim repeat); 8 GENUINELY NEW + 5 ALREADY EXIST + 11 direction-questionable
(future cycle-cleanup batch 2).

Inputs: data/substrate_index/skunkworks_wtypesig_new_edges_v1.jsonl
Tag: PHASE3_PHASE4_W_TYPE_SIG_RATIFY_BATCH_2

Substrate's FIRST real STRICT growth via Phase 4a self-model lever.
The predicted compounding pattern from DECISION 78 ('new operators yield new
edges') empirically realized.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


JSONL = Path('data/substrate_index/skunkworks_wtypesig_new_edges_v1.jsonl')


def find_qid_by_short(ps, short):
    for a in ps.all_atoms():
        if str(a.id).split('/')[-1].lower() == short.lower():
            return f'{a.corpus.value}::{a.id}'
    return None


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_atoms = len(ps.all_atoms())
    print(f'pre-ratify: {pre_atoms} atoms, {pre_rels} relations\n')

    edges = []
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if line:
                edges.append(json.loads(line))
    print(f'loaded {len(edges)} edges from {JSONL}\n')

    print('=== STEP 1: atom existence check ===')
    resolved = []
    missing = []
    for e in edges:
        src = e['src']; tgt = e['tgt']
        s_qid = find_qid_by_short(ps, src)
        t_qid = find_qid_by_short(ps, tgt)
        if s_qid and t_qid:
            resolved.append((e, s_qid, t_qid))
            print(f'  OK: {src} -{e["rel_type"]}-> {tgt}')
        else:
            missing.append((e, s_qid, t_qid))
            print(f'  MISSING_ATOM: src={src}({s_qid}) tgt={tgt}({t_qid})')

    if missing:
        print(f'\nABORT: {len(missing)} atom(s) missing; cannot proceed atomically')
        return

    print(f'\n=== STEP 2: relation type validation ===')
    rel_types = {}
    for e, s_qid, t_qid in resolved:
        rt_name = e['rel_type']
        try:
            rt = RelationType[rt_name]
            rel_types[(e['src'], e['tgt'])] = rt
            print(f'  OK: {rt_name} -> {rt.name}')
        except KeyError:
            print(f'  FAIL: rel_type {rt_name} not in enum')
            return

    print(f'\n=== STEP 3: idempotent add (skip if exists) ===')
    added = 0
    skipped = 0
    for e, s_qid, t_qid in resolved:
        rt = rel_types[(e['src'], e['tgt'])]
        try:
            ps.add_relation(
                s_qid, rt, t_qid,
                source='wtypesig_batch2_83a',
                note=f'DECISION 83a W_TYPE_SIG STRICT existence-checked Phase4a; '
                     f'witness=W_TYPE_SIG iter4_confidence=STRICT; {e.get("reason", "")}',
            )
            added += 1
            print(f'  ADDED: {e["src"]} -{rt.name}-> {e["tgt"]}')
        except Exception as ex:
            msg = str(ex)[:120]
            if 'already' in msg.lower() or 'exists' in msg.lower():
                skipped += 1
                print(f'  SKIP_EXISTS: {e["src"]} -{rt.name}-> {e["tgt"]}')
            else:
                print(f'  ADD_FAIL: {e["src"]} -> {e["tgt"]}: {msg}')

    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_atoms = len(ps.all_atoms())
    print(f'\npost-ratify: {post_atoms} atoms, {post_rels} relations (delta: {post_rels - pre_rels})')

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

    print(f'\nSUMMARY:')
    print(f'  edges added:        {added} (of {len(resolved)} target)')
    print(f'  edges skip-exists:  {skipped}')
    print(f'  R3 axiom term:      {t}/{len(ops)} = {100 * t / len(ops):.1f}%')
    print(f'  R3 modules:         {"OK" if mod_ok else "FAIL"}')
    print(f'  delta relations:    {post_rels - pre_rels}')
    print(f'\nTag: PHASE3_PHASE4_W_TYPE_SIG_RATIFY_BATCH_2')


if __name__ == '__main__':
    main()
