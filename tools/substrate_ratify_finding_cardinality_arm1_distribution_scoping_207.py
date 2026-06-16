"""207 cardinality ARM-1 distribution-scoping FINDING ratify.

Per DECISION 207 (Director ENDORSES) + Skunkworks VET ENDORSED honest-negative + Exp-Dev
232nd per-sibling adjudication.

NEW atom: concept::FINDING_cardinality_arm1_distribution_scoping
  kind: FINDING (NOT capability; NOT HARD_PASS; NOT load-bearing)
  ARM-1 cardinality capabilities are DISTRIBUTION-SCOPED to their original regime
  (n_distinct[1,9)/mult[1,4)/VOCAB=120/ROLES=4); the FROZEN operator does NOT achieve
  ARM-1-grade HARD_PASS bars on shifted distribution (n_distinct[2,13)/mult[1,6)/
  VOCAB=200/ROLES=5).

DEPENDS_ON:
  math::T3/cleanup_distinct_count (ratified ARM-1 operator; the FROZEN mechanism)
  concept::CAP_cardinality_recall_exact_count_single_role (ratified ARM-1 CAP; documents
    its scope-limit)
  concept::CAP_cardinality_quantifier_most (ratified ARM-1 CAP; documents its scope-limit)

metric_type: GENERALIZATION_TRANSFER (RMSE + accuracy + margin; NOT capability-recall)

Substrate state delta: +1 FINDING atom, +3 DEPENDS_ON edges.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
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
    math_store = ps._store_for(Corpus.MATH)
    concept_store = ps._store_for(Corpus.CONCEPT)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    new_id = 'FINDING_cardinality_arm1_distribution_scoping'
    new_qid = f'concept::{new_id}'
    if concept_store.get_atom(new_id) is not None:
        print(f'HARD_FAIL: {new_qid} already exists')
        return 1

    # Math dep
    if math_store.get_atom('T3/cleanup_distinct_count') is None:
        print('HARD_FAIL: math::T3/cleanup_distinct_count missing')
        return 1
    # Concept deps
    for c in ['CAP_cardinality_recall_exact_count_single_role', 'CAP_cardinality_quantifier_most']:
        if concept_store.get_atom(c) is None:
            print(f'HARD_FAIL: concept::{c} missing')
            return 1
    print('deps verified: math::T3/cleanup_distinct_count + 2 concept::CAP_cardinality_* atoms', flush=True)

    cell = repo_root / 'data/exp_cardinality_generalization_stage1_190c_2026-06-16/metrics.json'
    if not cell.exists():
        print(f'HARD_FAIL: cell metrics missing: {cell}')
        return 1
    sha = sha256_of(cell)
    with open(cell) as f:
        m = json.load(f)
    if m.get('run_mode') != 'full' or m.get('n_seeds') != 5:
        print(f'HARD_FAIL: cell precondition (run_mode={m.get("run_mode")} n_seeds={m.get("n_seeds")})')
        return 1
    print(f'cell corroborated: run_mode={m["run_mode"]} n_seeds={m["n_seeds"]} elapsed_s={m.get("elapsed_s"):.1f} sha={sha[:12]}..', flush=True)

    r = m['results']
    src = '207_190c_RESULTS_FINDING_cardinality_arm1_distribution_scoping_HONEST_NEGATIVE_generalization'

    sh = [{
        'solution_atom_id': new_qid,
        'adopted_date': '2026-06-16',
        'replaced_date': None,
        'replacement_reason': (
            'TRACK A/Phase-C-tail FINDING: ARM-1 cardinality capabilities are DISTRIBUTION-SCOPED. '
            'Per-sibling adjudication on full-mode generalization probe (operator FROZEN at ARM-1 '
            'CLEANUP_THRESH=0.30; distribution SHIFTED VOCAB 120->200, ROLES 4->5, n_distinct '
            '[1,9)->[2,13), mult [1,4)->[1,6)): BOTH siblings MIDDLE_BAND at N=4096. exact-count C2 '
            'RMSE 5.60 (>>1.0 bar; HONEST NEGATIVE for generalization; mechanism directionally '
            'transfers 14x C1 reduction but absolute precision degrades on harder distribution); '
            'most(A>B) C2 acc 0.775 (margin 0.232 CLEARS but acc<0.80 bar; close MIDDLE). NEITHER '
            'sibling clears HARD_PASS generalization. ARM-1 capabilities stay scoped to original '
            'regime; mechanism is real but distribution-bounded. N-scaling helps monotonically '
            '(higher N may close at untested 8192; NOT CLAIMED). Per DECISION 207b filing.'
        ),
        'empirical_metric': {
            'name': 'cardinality_arm1_distribution_scoping_per_sibling',
            'exact_count_N_2048': {
                'C0': r['2048']['exact_count']['c0'],
                'C1': r['2048']['exact_count']['c1'],
                'C2': r['2048']['exact_count']['c2'],
                'C2_std': r['2048']['exact_count']['c2_std'],
                'verdict': r['2048']['exact_count']['verdict'],
            },
            'exact_count_N_4096': {
                'C0': r['4096']['exact_count']['c0'],
                'C1': r['4096']['exact_count']['c1'],
                'C2': r['4096']['exact_count']['c2'],
                'C2_std': r['4096']['exact_count']['c2_std'],
                'verdict': r['4096']['exact_count']['verdict'],
            },
            'most_N_2048': {
                'C1': r['2048']['most']['c1'],
                'C2': r['2048']['most']['c2'],
                'C2_std': r['2048']['most']['c2_std'],
                'verdict': r['2048']['most']['verdict'],
                'drift': r['2048']['most']['drift'],
            },
            'most_N_4096': {
                'C1': r['4096']['most']['c1'],
                'C2': r['4096']['most']['c2'],
                'C2_std': r['4096']['most']['c2_std'],
                'margin': r['4096']['most']['c2'] - r['4096']['most']['c1'],
                'verdict': r['4096']['most']['verdict'],
                'drift': r['4096']['most']['drift'],
            },
            'arm1_HARD_PASS_bars': {
                'exact_count_RMSE_max': 1.0,
                'exact_count_RMSE_reduction_min': 2.0,
                'most_acc_min': 0.8,
                'most_margin_min': 0.2,
            },
            'arm1_original_distribution': {'VOCAB': 120, 'ROLES': 4, 'n_distinct': '[1,9)', 'mult': '[1,4)'},
            'shifted_distribution': m['distribution'],
            'overall_verdict': 'HONEST_NEGATIVE_for_clean_generalization_BOTH_siblings_MIDDLE_BAND',
            'directional_positives': 'mechanism transfers C2 beats both controls; N-scaling improves monotonically',
            'untested_extrapolation': 'higher N (e.g. 8192) MIGHT close; NOT claimed; flagged as future direction',
        },
        'metric_type': 'GENERALIZATION_TRANSFER',
        'metric_type_NOT': 'capability_recall',
        'metric_type_class': 'RMSE_plus_accuracy_plus_margin',
        'EM_class_mislabel_guard': 'STRICT type-discipline; this is generalization-transfer NOT served-capability accuracy',
        'n_seeds': m['n_seeds'],
        'run_mode': m['run_mode'],
        'operator_cleanup_thresh_LOCKED': m['operator_cleanup_thresh_LOCKED'],
        'generalization_NOT_refit': True,
        'gold_firewalled': '22nd_rule_gold_generated_at_eval_time_never_ingested',
        'verdict': 'HONEST_NEGATIVE_for_generalization',
        'cell_anchor': m['anchor_name'],
        'cell_metrics_sha256': sha,
        'cell_metrics_path': 'data/exp_cardinality_generalization_stage1_190c_2026-06-16/metrics.json',
        'compute_backend': m.get('compute_backend', 'cpu'),
        'dtype': m.get('dtype', 'float64'),
        'device': 'cpu',
        'elapsed_s': m.get('elapsed_s'),
        'form': 'FINDING',
        'source': src,
    }]

    new_atom = Atom(
        id=new_id,
        name='Cardinality ARM-1 distribution-scoping (HONEST NEGATIVE generalization finding)',
        corpus=Corpus.CONCEPT,
        tier=Tier.TIER_2_PRIMITIVE,
        kind=AtomKind.FINDING,
        description=(
            'ARM-1 cardinality capabilities (cleanup_distinct_count T3 + exact_count_single_role '
            'CAP + quantifier_most CAP) are DISTRIBUTION-SCOPED to their original regime '
            '(n_distinct[1,9)/mult[1,4)/VOCAB=120/ROLES=4). The FROZEN operator does NOT achieve '
            'ARM-1-grade HARD_PASS bars on the shifted distribution (n_distinct[2,13)/mult[1,6)/'
            'VOCAB=200/ROLES=5): exact-count C2 RMSE 5.60 at N=4096 (>>1.0 bar; 14x C1 reduction '
            'but absolute precision degrades), most(A>B) acc 0.775 at N=4096 (margin 0.232 clears '
            'but acc<0.80 HARD_PASS bar). Mechanism DIRECTIONALLY transfers (C2 beats both controls '
            'everywhere; cleanup_distinct_count is real generalizing-in-direction primitive NOT '
            'overfit). N-scaling helps monotonically (higher N may close; UNTESTED at N>4096; NOT '
            'CLAIMED). HONEST NEGATIVE for clean generalization per DECISION 207 + Exp-Dev 232nd + '
            'Skunkworks VET ENDORSED. Substrate-internal; gold firewalled at eval-time (22nd rule). '
            'FINDING (NOT capability; NOT HARD_PASS); ARM-1 capabilities UNCHANGED (cap_pres=1.0).'
        ),
        metadata={
            'finding_source': src,
            'eleventh_rule_clean': True,
            'substrate_internal_verified': True,
            'finding_NOT_capability': True,
            'metric_type_strict': 'GENERALIZATION_TRANSFER_NOT_capability_recall',
            'documents_scope_limit_of_ARM1': True,
            'distribution_bounded': True,
            'mechanism_directional_transfer': True,
        },
        solution_history=tuple(sh),
    )
    concept_store.add_atom(new_atom)
    concept_store._flush_atoms()

    # DEPENDS_ON edges: 1 math + 2 concept
    deps_full = [
        ('math', 'T3/cleanup_distinct_count'),
        ('concept', 'CAP_cardinality_recall_exact_count_single_role'),
        ('concept', 'CAP_cardinality_quantifier_most'),
    ]
    for corpus_str, dep_id in deps_full:
        ps.add_relation(new_qid, RelationType.DEPENDS_ON, f'{corpus_str}::{dep_id}',
                        source=src, note=f'FINDING DEPENDS_ON {dep_id}')
    concept_store._flush_relations()
    print(f'  ratified: +{new_qid} +{len(deps_full)} DEPENDS_ON edges')

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

    new_check = concept_store.get_atom(new_id)

    invariants_ok = (
        post_atoms == pre_atoms + 1
        and post_rels >= pre_rels + 3
        and post_t >= pre_t
        and mod_ok
        and new_check is not None
        and len(new_check.solution_history or ()) == 1
        and new_check.kind == AtomKind.FINDING
    )

    print(f'post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} (+{post_rels-pre_rels}) '
          f'axiom_term={post_t}/{post_total} mod_ok={mod_ok}')

    if not invariants_ok:
        print('HARD_FAIL: R3 invariant violation')
        return 1

    print()
    print('R3 verify: PASS (additive +1 FINDING atom +3 DEPENDS_ON edges; cap_pres=1.0)')
    print('  metric_type STRICT: GENERALIZATION_TRANSFER NOT capability-recall')
    print('  HONEST NEGATIVE preserved: per-sibling MIDDLE_BAND; NO manufactured transfer claim')
    print()
    print('HARD_PASS: 207 FINDING_cardinality_arm1_distribution_scoping RATIFIED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
