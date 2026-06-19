"""Atom-prose corrections per DECISION 149g FINAL CLOSE.

Two corrections (Phase-A-tail; not Phase-B blockers):
  1. PP-367_unified_algebra_lang_math: TYPE-MISFRAME (value holds full 5-seed but
     "1.000 x3" mis-types algebraic-correctness error-bounds as capability-accuracy;
     EM-class type-aware authoring trap per DECISION 146).
  2. PP-217_path_A_LLM_enhancement + RETRIEVAL_kb_fact_extensions: 11th-rule scope-flag
     (LLM-hybrid; explicitly NOT substrate-on-its-own).

Per Skunkworks 149g FINAL CLOSE + DECISION 152 REVISED + 19th-rule discipline both
directions (audit catches drift AND verifies honesty; aggregate MOSTLY HONEST not systematic rot).

Atomic transaction: 3 atom-prose updates + R3 invariant verify.
Substrate state delta: 0 atoms / 0 relations (description-only updates).
"""
from __future__ import annotations
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import Corpus


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


def update_atom_description(ps, qid_str, new_description, type_label_check):
    """Update an atom's description in place. Returns True on success."""
    qid = QualifiedAtomId.parse(qid_str)
    store = ps._store_for(qid.corpus)
    atom = store.get_atom(qid.local_id)
    if atom is None:
        print(f'HARD_FAIL: {qid_str} missing')
        return False
    old_desc = atom.description or ''
    new_atom = replace(atom, description=new_description)
    store.add_atom(new_atom)
    store._flush_atoms()
    check = store.get_atom(qid.local_id)
    if type_label_check not in (check.description or ''):
        print(f'HARD_FAIL: {qid_str} type-label not found in new description')
        return False
    print(f'  updated {qid_str}: len(old)={len(old_desc)} -> len(new)={len(check.description)}')
    return True


def main():
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    # ---- Correction 1: PP-367 TYPE-MISFRAME ----
    pp367_desc = (
        'Substrate unified language+math+cross-domain algebra: KL=150 language + KM=150 math '
        'coexist in shared N=4096 codebook. COMBO-3 unified-API algebraic theorem confirmed '
        '(full-mode N=4096, 5-seed [7,17,23,31,41]): identity error-bounds d1d2d3_err=0, '
        'k3_err<1e-4, cndc_err=0, cert_err=0, matvecs<=5 -- algebraic CORRECTNESS (NOT a 1.000 '
        'capability-accuracy). Confirms domain agnosticism via algebraic identity preservation; '
        'NL+math share the same substrate algebra. (Prior prose "language_recall 1.000 + '
        'math_recall 1.000 + cross_domain_recall 1.000" type-misframed correctness error-bounds '
        'as accuracy recall metrics; corrected per DECISION 149g FINAL CLOSE + DECISION 146 '
        'type-aware authoring discipline; EM-class type-misframe avoidance.)'
    )
    ok1 = update_atom_description(
        ps, 'concept::PP-367_unified_algebra_lang_math',
        pp367_desc,
        type_label_check='algebraic CORRECTNESS (NOT a 1.000 capability-accuracy)',
    )

    # ---- Correction 2: PP-217 LLM-hybrid relabel ----
    pp217_desc = (
        '[LLM-HYBRID; 11th-rule out-of-scope for substrate-on-its-own capability tally] '
        'Substrate fact recall augmented with an LLM-rerank path. Cosine cleanup-baseline + '
        'LLM-rerank yields ~0.85 at kb10K. NOT a substrate-only result; LLM-rerank is the '
        'augmentation. The substrate-only-equivalent path is the separate PP-225 fp32 head '
        '0.996 at kb100K (substrate-on-its-own). Per DECISION 149g + Skunkworks 149g audit + '
        '11th rule: HYBRID capabilities labeled distinctly and excluded from substrate-on-its-own '
        'tally to avoid the lap3_rotate-class learned-layer scope creep.'
    )
    ok2 = update_atom_description(
        ps, 'concept::PP-217_path_A_LLM_enhancement',
        pp217_desc,
        type_label_check='LLM-HYBRID; 11th-rule out-of-scope',
    )

    # ---- Correction 3: RETRIEVAL_kb_fact_extensions LLM-hybrid scope flag ----
    kbext_desc = (
        '[Mixed scope: contains LLM-HYBRID sub-component; see PP-217 relabel] '
        'Substrate KB-fact retrieval extensions beyond PP-225 (kb100K Tier-A 0.996 substrate-only). '
        'Includes PP-217 Path A LLM enhancement at kb10K cosine cleanup baseline (LLM-HYBRID; '
        'out-of-scope for substrate-on-its-own per 11th rule) + KB-shard storage cycle 224 '
        'tiered baseline + projected future kb500K+ retrieval. Pattern: cosine -> fhrr_unbind '
        'transition expected at scale. (Substrate-only sub-components stand; LLM-hybrid '
        'sub-components flagged distinctly per DECISION 149g + 11th rule.)'
    )
    ok3 = update_atom_description(
        ps, 'concept::RETRIEVAL_kb_fact_extensions',
        kbext_desc,
        type_label_check='Mixed scope: contains LLM-HYBRID sub-component',
    )

    if not (ok1 and ok2 and ok3):
        print('HARD_FAIL: at least one prose correction failed')
        return 1

    # Post-snapshot + R3 verify
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

    invariants_ok = (
        post_atoms == pre_atoms
        and post_rels == pre_rels
        and post_t == pre_t
        and post_total == pre_total
        and mod_ok
    )

    print(f'post: atoms={post_atoms} rels={post_rels} axiom_term={post_t}/{post_total} mod_ok={mod_ok}', flush=True)

    if not invariants_ok:
        print('HARD_FAIL: R3 invariant violation')
        return 1

    print('R3 verify: PASS (description-only updates; cap_pres=1.0; axiom_term unchanged)')
    print('HARD_PASS: 3 atom-prose corrections RATIFIED per DECISION 149g FINAL CLOSE')
    return 0


if __name__ == '__main__':
    sys.exit(main())
