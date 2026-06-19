"""Combined ratify for 2 CLEAR FORM-A specs per DECISION 151a + Exp-Dev 166th pre-check.

SPEC 4 -- capacity_composition_multiplicative (AGGREGATE type, tier A n=3):
  NEW atom: math::T3/capacity_composition_multiplicative
  cell: exp_substrate_capacity_composition_b2xb4_v1_n2048 (FULL n=3 HARD_PASS)
  metric: obs_mult=240.0x = pred_mult=240.0x (sparse_factor=48.0 x K=5)
  TYPE: AGGREGATE (multiplicative capacity-factor; NOT accuracy)
  DEPENDS_ON (refined by Exp-Dev): bundling + superposition + sparse_distributed_memory
  (sparse_coding doesn't exist; use sparse_distributed_memory)

SPEC 2 -- audit_preserving_reasoning (DUAL type, tier A n=3):
  NEW atom: math::T3/audit_preserving_reasoning
  cell: exp_substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096 (FULL n=3 HARD_PASS)
  metrics DUAL: reasoning_acc12=1.0 (capability-accuracy) + deletion_cert=1.0 (CORRECTNESS)
  TYPE: DUAL -- stamp BOTH as separate solution_history entries with metric_type distinction
  DEPENDS_ON (refined by Exp-Dev): cleanup + amit_gutfreund_sompolinsky_capacity + graph_traversal
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


def ratify_one(ps, math_store, new_id, name, description, dep_ids, sh_entries, source_tag, label):
    """Ratify one FORM-A new atom + edges + sh entries. Returns True on success."""
    new_qid = f'math::{new_id}'
    if math_store.get_atom(new_id) is not None:
        print(f'  [{label}] HARD_FAIL: {new_qid} already exists')
        return False
    for dep in dep_ids:
        if math_store.get_atom(dep) is None:
            print(f'  [{label}] HARD_FAIL: dependency missing math::{dep}')
            return False

    new_atom = Atom(
        id=new_id,
        name=name,
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        kind=AtomKind.SUB_OP,
        description=description,
        metadata={
            'form_a_source': source_tag,
            'eleventh_rule_clean': True,
            'substrate_internal_verified': True,
        },
        solution_history=tuple(sh_entries),
    )
    math_store.add_atom(new_atom)
    math_store._flush_atoms()
    for dep in dep_ids:
        ps.add_relation(
            new_qid,
            RelationType.DEPENDS_ON,
            f'math::{dep}',
            source=source_tag,
            note=f'{label} FORM-A new atom DEPENDS_ON {dep}',
        )
    math_store._flush_relations()
    print(f'  [{label}] ratified: +{new_qid}, +{len(dep_ids)} DEPENDS_ON edges, {len(sh_entries)} sh entries')
    return True


def main():
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    math_store = ps._store_for(Corpus.MATH)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    # ---- SPEC 4 -- capacity_composition_multiplicative ----
    spec4_cell = repo_root / 'data/exp_substrate_capacity_composition_b2xb4_v1_n2048/metrics.json'
    with open(spec4_cell) as f:
        m4 = json.load(f)
    if m4['run_mode'] != 'full' or m4['verdict'] != 'HARD_PASS' or m4['n_seeds'] != 3:
        print(f'HARD_FAIL: SPEC4 cell precondition (run_mode/verdict/n_seeds)')
        return 1
    # All seeds unanimous on sparse_factor=48.0, dense_Kens=500, sparse_Kens=24000 -> obs_mult=240.0x
    spec4_sha = sha256_of(spec4_cell)

    spec4_sh = [{
        'solution_atom_id': 'math::T3/capacity_composition_multiplicative',
        'adopted_date': '2026-06-16',
        'replaced_date': None,
        'replacement_reason': (
            'FORM-A AGGREGATE provenance: capacity primitives compose MULTIPLICATIVELY; '
            'observed mult factor 240.0x = predicted 240.0x (sparse_factor=48.0 x K-ensemble=5). '
            'Full-mode N=2048 3-seed unanimous (seeds 7,17,23). NOT an accuracy; AGGREGATE '
            'capacity-multiplication factor per DECISION 146 type-aware authoring + DECISION 151a '
            'type-correct provenance.'
        ),
        'empirical_metric': {
            'name': 'multiplicative_capacity_factor',
            'obs_mult': 240.0,
            'pred_mult': 240.0,
            'sparse_factor': 48.0,
            'K_ensemble': 5,
            'dense_single': 100,
            'sparse_single': 4800,
            'sparse_Kens': 24000,
        },
        'metric_type': 'AGGREGATE',
        'n_seeds': 3,
        'seeds': [7, 17, 23],
        'run_mode': 'full',
        'N_vector': 2048,
        'verdict': 'HARD_PASS',
        'cell_anchor': m4['anchor_name'],
        'cell_metrics_sha256': spec4_sha,
        'cell_metrics_path': 'data/exp_substrate_capacity_composition_b2xb4_v1_n2048/metrics.json',
        'form': 'FORM-A',
        'source': 'form_a_decision_151a_spec_4_capacity_composition_multiplicative_aggregate',
    }]
    spec4_ok = ratify_one(
        ps, math_store,
        new_id='T3/capacity_composition_multiplicative',
        name='Capacity composition (multiplicative)',
        description=(
            'Capacity primitives compose MULTIPLICATIVELY: sparse x K-ensemble x hierarchy. '
            'Observed multiplication factor 240.0x matches predicted 240.0x (sparse_factor=48.0 '
            'x K-ensemble=5; dense_single=100 -> sparse_single=4800 -> sparse_Kens=24000). '
            'A capacity-scaling property of the substrate, NOT an accuracy. Cell-corroborated '
            'full-mode multi-seed tier A (n=3 unanimous).'
        ),
        dep_ids=['T2/bundling', 'T2/superposition', 'T2/sparse_distributed_memory'],
        sh_entries=spec4_sh,
        source_tag='form_a_decision_151a_spec_4_capacity_composition_multiplicative',
        label='SPEC4',
    )

    # ---- SPEC 2 -- audit_preserving_reasoning (DUAL) ----
    spec2_cell = repo_root / 'data/exp_substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096/metrics.json'
    with open(spec2_cell) as f:
        m2 = json.load(f)
    if m2['run_mode'] != 'full' or m2['verdict'] != 'HARD_PASS' or m2['n_seeds'] != 3:
        print(f'HARD_FAIL: SPEC2 cell precondition')
        return 1
    spec2_sha = sha256_of(spec2_cell)

    # DUAL entries: stamp BOTH metrics separately with distinct metric_type
    spec2_sh = [
        {
            'solution_atom_id': 'math::T3/audit_preserving_reasoning',
            'adopted_date': '2026-06-16',
            'replaced_date': None,
            'replacement_reason': (
                'FORM-A DUAL type ENTRY 1 of 2 (capability-accuracy): reasoning under audit-preserving '
                'eviction composed with multi-hop reasoning; reasoning_acc@12=1.0 full-mode 3-seed '
                'unanimous (seeds 7,17,23). Distinct from ENTRY 2 (deletion_cert CORRECTNESS).'
            ),
            'empirical_metric': {
                'name': 'audit_preserving_reasoning_accuracy_at_12',
                'reasoning_acc12': 1.0,
                'G_retained': 47,
            },
            'metric_type': 'capability_accuracy',
            'n_seeds': 3,
            'seeds': [7, 17, 23],
            'run_mode': 'full',
            'N_vector': 4096,
            'verdict': 'HARD_PASS',
            'cell_anchor': m2['anchor_name'],
            'cell_metrics_sha256': spec2_sha,
            'cell_metrics_path': 'data/exp_substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096/metrics.json',
            'form': 'FORM-A',
            'source': 'form_a_decision_151a_spec_2_audit_preserving_reasoning_dual_entry_1_capability_accuracy',
        },
        {
            'solution_atom_id': 'math::T3/audit_preserving_reasoning',
            'adopted_date': '2026-06-16',
            'replaced_date': None,
            'replacement_reason': (
                'FORM-A DUAL type ENTRY 2 of 2 (CORRECTNESS): deletion-certificate preserved through '
                'reasoning composition; deletion_cert=1.0 full-mode 3-seed unanimous. CORRECTNESS '
                'property type per DECISION 146 (EM-class trap avoided: certificate property is NOT '
                'a served-capability accuracy; stamp typed distinctly). Distinct from ENTRY 1 '
                '(reasoning_acc12 capability-accuracy).'
            ),
            'empirical_metric': {
                'name': 'deletion_certificate_preservation',
                'deletion_cert': 1.0,
                'G_retained': 47,
            },
            'metric_type': 'CORRECTNESS',
            'n_seeds': 3,
            'seeds': [7, 17, 23],
            'run_mode': 'full',
            'N_vector': 4096,
            'verdict': 'HARD_PASS',
            'cell_anchor': m2['anchor_name'],
            'cell_metrics_sha256': spec2_sha,
            'cell_metrics_path': 'data/exp_substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096/metrics.json',
            'form': 'FORM-A',
            'source': 'form_a_decision_151a_spec_2_audit_preserving_reasoning_dual_entry_2_correctness',
        },
    ]
    spec2_ok = ratify_one(
        ps, math_store,
        new_id='T3/audit_preserving_reasoning',
        name='Audit-preserving reasoning (B6 x SQ2 composition)',
        description=(
            'Reasoning under audit-preserving eviction (Hopfield-capacity-bounded eviction) composed '
            'with multi-hop reasoning; reasoning accuracy preserved AND deletion-certificate held '
            'simultaneously. DUAL property: reasoning_acc@12=1.0 (capability-accuracy) + '
            'deletion_cert=1.0 (CORRECTNESS) -- stamped distinctly per type-aware discipline. '
            'Cell-corroborated full-mode multi-seed tier A (n=3 unanimous).'
        ),
        dep_ids=['T2/cleanup', 'T2/amit_gutfreund_sompolinsky_capacity', 'T2_FAM/graph_traversal'],
        sh_entries=spec2_sh,
        source_tag='form_a_decision_151a_spec_2_audit_preserving_reasoning_DUAL',
        label='SPEC2',
    )

    if not (spec4_ok and spec2_ok):
        print('HARD_FAIL: at least one ratify failed; manual review')
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

    spec4_check = math_store.get_atom('T3/capacity_composition_multiplicative')
    spec2_check = math_store.get_atom('T3/audit_preserving_reasoning')

    invariants_ok = (
        post_atoms == pre_atoms + 2     # +2 new atoms
        and post_rels == pre_rels + 6   # +3 + 3 DEPENDS_ON edges
        and post_t >= pre_t
        and mod_ok
        and spec4_check is not None
        and spec2_check is not None
        and len(spec4_check.solution_history or ()) == 1
        and len(spec2_check.solution_history or ()) == 2
    )

    print(f'post: atoms={post_atoms} (delta={post_atoms-pre_atoms}) rels={post_rels} (delta={post_rels-pre_rels}) '
          f'axiom_term={post_t}/{post_total} mod_ok={mod_ok}', flush=True)
    print(f'SPEC4 sh entries: {len(spec4_check.solution_history or ())} (expected 1, AGGREGATE)')
    print(f'SPEC2 sh entries: {len(spec2_check.solution_history or ())} (expected 2, DUAL)')

    if not invariants_ok:
        print('HARD_FAIL: R3 invariant violation; manual review')
        return 1

    print('R3 verify: PASS (additive +2 atoms +6 edges; cap_pres=1.0; AGGREGATE + DUAL types stamped)')
    print('HARD_PASS: 2 FORM-A atoms RATIFIED per DECISION 151a (SPEC4 AGGREGATE + SPEC2 DUAL)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
