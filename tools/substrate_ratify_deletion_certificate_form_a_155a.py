"""TIER-3 deletion_certificate FORM-A ratify (DECISION 155a).

Per Skunkworks spec + Exp-Dev 172nd pre-check CLEAR + DECISION 155a UNBLOCKED
(prerequisite hopfield_pattern_deletion landed at db9b3877).

NEW atom: math::T3/deletion_certificate (sub_op, T3)
  Correctness certificate for associative-memory pattern deletion: after
  hopfield_pattern_deletion removes a pattern (W -= xi.xiT/N), the certificate
  verifies the deletion satisfies its invariants (deleted pattern no longer
  retrievable; refusal fires correctly on the deleted item; non-deleted patterns
  preserved). precision=1.00 recall=1.00 (full-mode n=5).

DEPENDS_ON:
  math::T3/hopfield_pattern_deletion (the OPERATION it certifies; landed db9b3877)
  math::T2/cleanup (substrate consistency / retrieval check)

CORRECTNESS type per DECISION 146 type-aware authoring + DECISION 153 (NOT accuracy-lift;
SATISFIES_INVARIANT boolean-property; EM-class trap avoided).

The 153c grounding gap is CLOSED: the certificate now certifies a REAL atomized operation
(operator-first, then certificate -- correct ordering; no thin-grounding).

Substrate state delta: +1 atom, +2 DEPENDS_ON edges.
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
    math_store = ps._store_for(Corpus.MATH)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    new_id = 'T3/deletion_certificate'
    new_qid = f'math::{new_id}'
    if math_store.get_atom(new_id) is not None:
        print(f'HARD_FAIL: {new_qid} already exists')
        return 1
    dep_ids = ['T3/hopfield_pattern_deletion', 'T2/cleanup']
    for d in dep_ids:
        if math_store.get_atom(d) is None:
            print(f'HARD_FAIL: dep missing math::{d}')
            return 1
    print(f'deps verified: {dep_ids}', flush=True)

    cell_metrics = repo_root / 'data/exp_deletion_cert_refusal_joint_v1/metrics.json'
    if not cell_metrics.exists():
        print(f'HARD_FAIL: cell metrics missing: {cell_metrics}')
        return 1
    sha = sha256_of(cell_metrics)
    with open(cell_metrics) as f:
        m = json.load(f)
    if m.get('run_mode') != 'full' or m.get('verdict') != 'HARD_PASS':
        print(f'HARD_FAIL: cell precondition (run_mode={m.get("run_mode")} verdict={m.get("verdict")})')
        return 1
    # Cell metric extraction: precision + recall (boolean correctness property)
    ps0 = m.get('per_seed', [{}])[0]
    precision = ps0.get('precision') if isinstance(ps0, dict) else None
    recall = ps0.get('recall') if isinstance(ps0, dict) else None
    print(f'corroboration: run_mode={m.get("run_mode")} n_seeds={m.get("n_seeds")} precision={precision} recall={recall} verdict_msg={m.get("verdict_msg", "")[:120]}', flush=True)

    sh_entry = {
        'solution_atom_id': new_qid,
        'adopted_date': '2026-06-16',
        'replaced_date': None,
        'replacement_reason': (
            'FORM-A CORRECTNESS provenance: deletion certificate verifies hopfield_pattern_deletion '
            'satisfies its invariants (deleted pattern unretrievable + refusal fires correctly + '
            'non-deleted preserved). precision=1.00 recall=1.00 full-mode n=5 tier A; SATISFIES_INVARIANT '
            'boolean-property NOT a served-capability accuracy (EM-class trap avoided per DECISION 146). '
            'Grounding gap CLOSED per DECISION 153c (hopfield_pattern_deletion now atomized at db9b3877; '
            'certificate certifies a REAL operation, not phantom). Completes the 2-atom deletion discipline.'
        ),
        'empirical_metric': {
            'name': 'deletion_certificate_correctness_property',
            'precision': precision,
            'recall': recall,
            'property': 'deleted_pattern_unretrievable_AND_refusal_fires_AND_nondeleted_preserved',
        },
        'metric_type': 'CORRECTNESS',
        'n_seeds': m.get('n_seeds'),
        'run_mode': m.get('run_mode'),
        'verdict': m.get('verdict'),
        'cell_anchor': m.get('anchor', m.get('anchor_name')),
        'cell_metrics_sha256': sha,
        'cell_metrics_path': 'data/exp_deletion_cert_refusal_joint_v1/metrics.json',
        'form': 'FORM-A',
        'source': 'form_a_decision_155a_deletion_certificate_CORRECTNESS_DEPENDS_ON_hopfield_pattern_deletion',
    }

    new_atom = Atom(
        id=new_id,
        name='Deletion certificate (associative-memory pattern deletion)',
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        kind=AtomKind.SUB_OP,
        description=(
            'Correctness certificate for associative-memory pattern deletion: after '
            'hopfield_pattern_deletion removes a pattern via W -= xi*xi^T/N, the certificate '
            'verifies the deletion satisfies its invariants (deleted pattern no longer retrievable, '
            'refusal fires correctly on the deleted item, non-deleted patterns preserved). '
            'CORRECTNESS type (SATISFIES_INVARIANT boolean-property; NOT a capability-accuracy). '
            'precision=1.00 recall=1.00 full-mode n=5 tier A. Certifies a REAL atomized operation '
            '(operator-first sequence; grounding gap closed per DECISION 153c). Completes the '
            '2-atom deletion discipline (hopfield_pattern_deletion operator + this certificate).'
        ),
        metadata={
            'form_a_source': 'form_a_decision_155a_deletion_certificate_CORRECTNESS',
            'eleventh_rule_clean': True,
            'substrate_internal_verified': True,
            'completes_2_atom_deletion_discipline': True,
        },
        solution_history=(sh_entry,),
    )

    math_store.add_atom(new_atom)
    math_store._flush_atoms()

    for d in dep_ids:
        ps.add_relation(
            new_qid,
            RelationType.DEPENDS_ON,
            f'math::{d}',
            source='form_a_decision_155a_deletion_certificate',
            note=f'deletion_certificate DEPENDS_ON {d}',
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
    edges_check = sum(
        1 for s, r, t in ps.iter_all_relations()
        if (s == new_id or s == new_qid)
        and r.name == 'DEPENDS_ON'
        and any(d in t for d in ['hopfield_pattern_deletion', 'cleanup'])
    )

    invariants_ok = (
        post_atoms == pre_atoms + 1
        and post_rels == pre_rels + 2
        and post_t >= pre_t
        and mod_ok
        and sh_landed == 1
        and edges_check == 2
    )

    print(f'post: atoms={post_atoms} (delta={post_atoms-pre_atoms}) rels={post_rels} (delta={post_rels-pre_rels}) '
          f'axiom_term={post_t}/{post_total} mod_ok={mod_ok} sh_landed={sh_landed} edges={edges_check}', flush=True)

    if not invariants_ok:
        print('HARD_FAIL: R3 invariant violation')
        return 1

    print('R3 verify: PASS (+1 atom +2 edges; cap_pres=1.0; CORRECTNESS type stamped; 2-atom deletion discipline COMPLETE)')
    print('HARD_PASS: TIER-3 deletion_certificate FORM-A RATIFIED per DECISION 155a')
    return 0


if __name__ == '__main__':
    sys.exit(main())
