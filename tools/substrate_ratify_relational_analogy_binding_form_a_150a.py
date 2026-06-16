"""TIER-2 FORM-A relational_analogy_binding ratify (DECISION 150a).

Skunkworks SPEC + Exp-Dev pre-check CLEAR + Director DECISION 150a GO.

NEW atom: math::T3/relational_analogy_binding (sub_op, T3)
  A:B::C:D proportional analogy via relational role-filler binding + cleanup, composing over
  deep (L3) composite items; recovers target hits1_l3=1.0 (within 10pp of atomic). Substrate-internal
  (no learned codebook; 11th-rule clean per Exp-Dev 164th).

DEPENDS_ON:
  T2/role_filler_binding (relational binding primitive)
  T2/fhrr_bind (vector binding primitive)
  T2_FAM/cleanup_retrieval (cleanup family for composite recovery)

Corroboration cell: exp_comp24_analogical_at_l3_cpu_v1 (HARD_PASS run_mode=FULL n_seeds=1)
  hits1_l3=1.0 hits1_l1=1.0 gap=0.0 (verdict bar >=0.85; measured 1.0)

3-of-3 gate:
  (1) cap_pres = 1.0 (additive new atom + DEPENDS_ON edges)
  (2) re-expressibility = composes role_filler_binding + fhrr_bind + cleanup_retrieval
  (3) closes-a-gap = within-domain analogy capability gap (cross-domain stays RETRACTED P9 confound)

Substrate state delta: +1 atom, +3 DEPENDS_ON edges.

11th-rule discipline: corroboration cell verified substrate-internal (no learned RotatE/codebook);
lap3_rotate_analogy EXCLUDED per DECISION 150a (50th audit-discipline instance type candidate).
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


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

    new_id = 'T3/relational_analogy_binding'
    new_qid = f'math::{new_id}'
    math_store = ps._store_for(Corpus.MATH)

    if math_store.get_atom(new_id) is not None:
        print(f'HARD_FAIL: {new_qid} already exists; abort')
        return 1

    dep_ids = ['T2/role_filler_binding', 'T2/fhrr_bind', 'T2_FAM/cleanup_retrieval']
    for dep in dep_ids:
        if math_store.get_atom(dep) is None:
            print(f'HARD_FAIL: dependency missing in-store: math::{dep}')
            return 1
    print(f'deps verified: {dep_ids}', flush=True)

    cell_metrics = repo_root / 'data/exp_comp24_analogical_at_l3_cpu_v1/metrics.json'
    cell_py = repo_root / 'experiments/exp_comp24_analogical_at_l3_cpu_v1.py'
    if not cell_metrics.exists():
        print(f'HARD_FAIL: cell metrics missing: {cell_metrics}')
        return 1

    cell_metrics_sha = sha256_of(cell_metrics)
    cell_py_sha = sha256_of(cell_py) if cell_py.exists() else None

    with open(cell_metrics) as f:
        m = json.load(f)

    if m.get('run_mode') != 'full':
        print(f'HARD_FAIL: cell not run_mode=full (read {m.get("run_mode")})')
        return 1
    if m.get('verdict') != 'HARD_PASS':
        print(f'HARD_FAIL: cell verdict != HARD_PASS')
        return 1
    hits1_l3 = m['per_seed'][0]['hits1_l3']
    hits1_l1 = m['per_seed'][0]['hits1_l1']
    gap = m['per_seed'][0]['gap']
    if hits1_l3 != 1.0:
        print(f'HARD_FAIL: hits1_l3 != 1.0 (read {hits1_l3})')
        return 1
    print(f'corroboration: hits1_l3={hits1_l3} hits1_l1={hits1_l1} gap={gap} verdict_bar=0.85 run_mode=full n_seeds=1', flush=True)

    ratify_date = '2026-06-16'
    src = 'form_a_decision_150a_relational_analogy_binding_within_domain_substrate_internal'

    sh_entry = {
        'solution_atom_id': new_qid,
        'adopted_date': ratify_date,
        'replaced_date': None,
        'replacement_reason': (
            'FORM-A capability-recall provenance: within-domain analogy (A:B::C:D) over deep L3 '
            'composite items via relational role-filler binding + cleanup. Measured hits1_l3=1.0 '
            'hits1_l1=1.0 gap=0.0 (verdict bar >=0.85; substantially exceeded). Full-mode n=1 '
            'single-seed (tier B; weaker than PP-364 n=5 + K10-K20 3-seed but stronger than smoke). '
            '11th-RULE CLEAN: cell substrate-internal (no learned RotatE/codebook; lap3_rotate_analogy '
            'EXCLUDED per DECISION 150a + Skunkworks 164th + Exp-Dev 164th). Cross-domain analogy '
            'stays RETRACTED P9 confound; do NOT conflate.'
        ),
        'empirical_metric': {
            'name': 'within_domain_analogy_hits1',
            'hits1_l3': hits1_l3,
            'hits1_l1': hits1_l1,
            'gap': gap,
            'verdict_bar': 0.85,
        },
        'metric_type': 'capability_recall',
        'n_seeds': m.get('n_seeds'),
        'run_mode': m.get('run_mode'),
        'verdict': m.get('verdict'),
        'cell_anchor': m.get('anchor_name'),
        'cell_py_sha256': cell_py_sha,
        'cell_metrics_sha256': cell_metrics_sha,
        'cell_metrics_path': 'data/exp_comp24_analogical_at_l3_cpu_v1/metrics.json',
        'form': 'FORM-A',
        'source': src,
    }

    new_atom = Atom(
        id=new_id,
        name='Relational analogy binding (A:B::C:D over composites)',
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        kind=AtomKind.SUB_OP,
        description=(
            'A:B::C:D proportional analogy via relational role-filler binding + cleanup, composing '
            'over deep (L3) composite items. Recovers analogy target at hits1_l3=1.0 within-domain '
            '(gap from atomic L1=0.0; substantially exceeds verdict bar >=0.85). Substrate-internal '
            'mechanism (no learned codebook; relational binding + cleanup composes over composites). '
            'Closes the within-domain analogy capability gap; cross-domain stays retracted (P9 confound).'
        ),
        metadata={
            'literature': 'substrate-internal; per-binding relational analogy at composite depth',
            'form_a_source': src,
            'eleventh_rule_clean': True,
            'substrate_internal_verified': True,
        },
        solution_history=(sh_entry,),
    )

    math_store.add_atom(new_atom)
    math_store._flush_atoms()

    for dep in dep_ids:
        ps.add_relation(
            new_qid,
            RelationType.DEPENDS_ON,
            f'math::{dep}',
            source='form_a_decision_150a_relational_analogy_binding',
            note='Relational analogy binding composes role-filler/vector binding with cleanup',
        )
    math_store._flush_relations()

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

    new_check = math_store.get_atom(new_id)
    sh_landed = len(new_check.solution_history or ()) if new_check else 0
    # Fixed predicate: match src qualified form
    edges_check = sum(
        1 for s, r, t in ps.iter_all_relations()
        if (s == new_id or s == new_qid)
        and r.name == 'DEPENDS_ON'
        and any(d in t for d in ['role_filler_binding', 'fhrr_bind', 'cleanup_retrieval'])
    )

    invariants_ok = (
        post_atoms == pre_atoms + 1
        and post_rels == pre_rels + 3
        and post_t >= pre_t
        and post_total == pre_total + 1
        and mod_ok
        and sh_landed == 1
        and edges_check == 3
    )

    print(f'post: atoms={post_atoms} (delta={post_atoms-pre_atoms}) rels={post_rels} (delta={post_rels-pre_rels}) '
          f'axiom_term={post_t}/{post_total} mod_ok={mod_ok} sh_landed={sh_landed} edges={edges_check}', flush=True)

    if not invariants_ok:
        print('HARD_FAIL: R3 invariant violation')
        return 1

    print('R3 verify: PASS (FORM-A additive new-atom; +1 atom +3 edges; cap_pres=1.0; sh entry materialized)')
    print('HARD_PASS: TIER-2 relational_analogy_binding FORM-A RATIFIED per DECISION 150a')
    return 0


if __name__ == '__main__':
    sys.exit(main())
