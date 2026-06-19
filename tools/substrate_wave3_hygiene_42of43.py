"""Wave 3 hygiene cleanup: 42/43 cleared per Exp-Dev re-pre-check.

Per Skunkworks Wave 3 spec + Exp-Dev 147th honest signal:
  ITEM A: spurious SPECIALIZES category_type (6 bare + 3 rescue-then-remove)
  ITEM B: spurious DEPENDS_ON metric_space (29 bare + 5 rescue-then-remove)
  HOLD: wright_fisher_process (INSTANCE_OF not in forward-walk set; strand-risk)

rescue_then_remove semantics: ADD rescue FIRST then REMOVE.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import RelationType, Corpus


WORKLIST = Path('data/substrate_index/skunkworks_wave3_hygiene_removal_worklist_2026-06-16.jsonl')
HOLD = set()  # was {'wright_fisher_process'}; Skunkworks amended to rescue_then_remove +DEPENDS_ON markov_chain


def find_qid_by_short(ps, short):
    candidates = []
    for a in ps.all_atoms():
        if str(a.id).split('/')[-1].lower() == short.lower():
            candidates.append(f'{a.corpus.value}::{a.id}')
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    math_first = [c for c in candidates if c.startswith('math::')]
    if math_first:
        return math_first[0]
    return candidates[0]


def to_qid(ps, ref):
    """Resolve bare 'T2/x' to full 'math::T2/x' via store lookup."""
    if '::' in ref:
        return ref
    short = ref.split('/')[-1]
    # Try MATH first
    for a in ps.all_atoms():
        if a.id == ref and a.corpus == Corpus.MATH:
            return f'math::{a.id}'
    return find_qid_by_short(ps, short)


def remove_edge(ps, src_qid, dst_qid, rel_str):
    src_q = QualifiedAtomId.parse(src_qid)
    src_store = ps._store_for(src_q.corpus)
    rt = RelationType(rel_str)
    dst_local = QualifiedAtomId.parse(dst_qid).local_id if '::' in dst_qid else dst_qid
    for triple in [(src_q.local_id, rel_str, dst_qid), (src_q.local_id, rel_str, dst_local)]:
        if triple in src_store._all_relations:
            src_store._all_relations.discard(triple)
            tgt = triple[2]
            if (src_q.local_id, rt) in src_store._out:
                src_store._out[(src_q.local_id, rt)].discard(tgt)
            if (tgt, rt) in src_store._in:
                src_store._in[(tgt, rt)].discard(src_q.local_id)
            return True
    return False


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
    print(f'pre: {pre_atoms} / {pre_rels} / {pre_t}/{pre_total}\n')

    entries = []
    with open(WORKLIST) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            e = json.loads(line)
            # Skip meta/separator entries (any key starting with _)
            if any(k.startswith('_') for k in e.keys()):
                continue
            entries.append(e)
    print(f'loaded {len(entries)} worklist entries\n')

    removed = 0
    rescued = 0
    held = 0
    failed = 0
    for e in entries:
        src_short = e['src'].split('/')[-1]
        if src_short.lower() in HOLD:
            print(f'  HOLD: {e["src"]} (strand-risk per Exp-Dev)')
            held += 1
            continue

        src_qid = to_qid(ps, e['src'])
        dst_qid = to_qid(ps, e['dst'])
        if not src_qid or not dst_qid:
            print(f'  MISSING_ATOM: {e["src"]} or {e["dst"]}')
            failed += 1
            continue

        action = e['action']
        if action == 'rescue_then_remove':
            # ADD rescue first; rescue_add src is implicit = parent src
            rescue = e['rescue_add']
            rqid_src = src_qid  # parent entry's src
            rqid_dst = to_qid(ps, rescue['dst'])
            try:
                ps.add_relation(rqid_src, RelationType[rescue['rel']], rqid_dst,
                                source='wave3_hygiene_142a',
                                note=f'Wave 3 rescue: {e.get("reason", "")[:80]}')
                rescued += 1
                print(f'  RESCUE: {rqid_src} -{rescue["rel"]}-> {rqid_dst}')
            except Exception as ex:
                msg = str(ex)[:100]
                if 'already' not in msg.lower() and 'exists' not in msg.lower():
                    print(f'  RESCUE_FAIL: {ex}')
                    failed += 1
                    continue
            ps._store_for(QualifiedAtomId.parse(rqid_src).corpus)._flush_relations()
        # REMOVE
        ok = remove_edge(ps, src_qid, dst_qid, e['rel'])
        if ok:
            removed += 1
            print(f'  REMOVED: {src_qid} -{e["rel"]}-> {dst_qid}')
        else:
            print(f'  NOT_FOUND: {src_qid} -{e["rel"]}-> {dst_qid}')
            failed += 1
        ps._store_for(QualifiedAtomId.parse(src_qid).corpus)._flush_relations()

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)

    import importlib
    mod_ok = all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])

    hard_pass = post_t == post_total and mod_ok and failed == 0
    print(f'\nSUMMARY: removed={removed}, rescued={rescued}, held={held}, failed={failed}')
    print(f'state: {pre_atoms}->{post_atoms}; {pre_rels}->{post_rels} (delta {post_rels-pre_rels})')
    print(f'axiom_term: {post_t}/{post_total}; modules: {"OK" if mod_ok else "FAIL"}')
    print(f'HARD_PASS: {hard_pass}')


if __name__ == '__main__':
    main()
