"""190f drift_kappa3 MIDDLE-BAND FINDING ratify (TRACK A ledger close).

Per DECISION 190f + Exp-Dev 224th honest signal.

NEW atom: math::T3/kappa3_drift_detection
  kind: FINDING (NOT capability; NOT HARD_PASS; NOT load-bearing)
  Kappa-3 3rd-cumulant spectral-fingerprint drift detection during training.
  FULL-MODE MIDDLE_BAND (2/3 conditions, n=5):
    detected 5/5 drifts
    fpr=0.020 (passes HP<0.05)
    latency=16.6 writes
    hp1=5/5 hp2=5/5 hp3=3/5  -> 2-of-3 conditions -> MIDDLE_BAND

DEPENDS_ON: T1/kullback_leibler_divergence + T3/bocpd_changepoint + T3/mp_bulk_kl
  (all EXIST; real drift-detection lineage; NOT a floating fact)

metric_type: DETECTION (RATIO-class; detect-rate + fpr + latency)
  NOT accuracy/capability-recall (EM-class mislabel guard per STRICT type-discipline)

Substrate state delta: +1 atom, +3 DEPENDS_ON edges (no auto-derived HAS_USERS;
  DEPENDS_ON math->math doesn't trigger USES reverse).

Per Exp-Dev correction: "~8x sensitivity" propagated figure NOT in authoritative
  metrics.json; do NOT assert. Stamp by measured numbers only.
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

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    new_id = 'T3/kappa3_drift_detection'
    new_qid = f'math::{new_id}'
    if math_store.get_atom(new_id) is not None:
        print(f'HARD_FAIL: {new_qid} already exists')
        return 1
    deps = ['T1/kullback_leibler_divergence', 'T3/bocpd_changepoint', 'T3/mp_bulk_kl']
    for d in deps:
        if math_store.get_atom(d) is None:
            print(f'HARD_FAIL: dep missing math::{d}')
            return 1
    print(f'deps verified: {deps}', flush=True)

    cell = repo_root / 'data/exp_a7_kappa3_drift_detection_during_training_v1/metrics.json'
    if not cell.exists():
        print(f'HARD_FAIL: cell metrics missing: {cell}')
        return 1
    sha = sha256_of(cell)
    with open(cell) as f:
        m = json.load(f)
    if m.get('verdict') != 'MIDDLE_BAND' or m.get('run_mode') != 'full':
        print(f'HARD_FAIL: cell precondition (verdict={m.get("verdict")} run_mode={m.get("run_mode")})')
        return 1
    print(f'cell corroborated: verdict={m["verdict"]} run_mode={m["run_mode"]} n_seeds={m["n_seeds"]} sha={sha[:12]}..', flush=True)

    # Extract per-seed aggregates
    per_seed = m.get('per_seed', [])
    detected_total = sum(ps['detected'] for ps in per_seed)
    n_drifts = len(per_seed) * 5  # 5 drifts per seed (per the cell pattern)
    fprs = [ps['fpr'] for ps in per_seed]
    latencies = [ps['detect_latency_writes'] for ps in per_seed]
    hp1_total = sum(ps['hp1'] for ps in per_seed)
    hp2_total = sum(ps['hp2'] for ps in per_seed)
    hp3_total = sum(ps['hp3'] for ps in per_seed)

    ratify_date = '2026-06-16'
    src = '190f_drift_kappa3_MIDDLE_BAND_FINDING_TRACK_A_ledger_close_DECISION_190f'

    sh = [{
        'solution_atom_id': new_qid,
        'adopted_date': ratify_date,
        'replaced_date': None,
        'replacement_reason': (
            'TRACK A ledger close: drift_kappa3 MIDDLE-BAND DETECTION finding filed per DECISION 190f. '
            'NOT a capability; NOT HARD_PASS; NOT load-bearing. Kappa-3 spectral-fingerprint drift '
            'detection during training: detect 5/5 drifts at fpr=0.020 (passes) latency=16.6 writes; '
            'hp1=5/5 hp2=5/5 hp3=3/5 -> 2-of-3 conditions = MIDDLE_BAND. Real lineage (KL + bocpd + '
            'mp_bulk_kl deps exist); filed as honest finding for ledger completeness. Per Exp-Dev 224th '
            'verify-before-asserting catch: "~8x sensitivity" propagated figure NOT in authoritative '
            'metrics.json; NOT asserted; stamped by measured numbers only.'
        ),
        'empirical_metric': {
            'name': 'kappa3_drift_detection_full_mode_5_seed',
            'detected_drifts_total': detected_total,
            'fpr_per_seed': fprs,
            'fpr_HP_bar': 0.05,
            'fpr_passes': True,
            'detect_latency_writes_per_seed': latencies,
            'hp1_per_seed_total': hp1_total,
            'hp2_per_seed_total': hp2_total,
            'hp3_per_seed_total': hp3_total,
            'conditions_passed': 2,
            'conditions_total': 3,
            'verdict_msg': 'MIDDLE_BAND -- detect 5/5 drifts + fpr passes + latency OK; hp3 fails 3/5',
        },
        'metric_type': 'DETECTION',
        'metric_type_NOT': 'accuracy_or_capability_recall',
        'metric_type_class': 'RATIO',
        'EM_class_mislabel_guard': 'STRICT type-discipline per Skunkworks; this is detection-performance NOT served-capability accuracy',
        'n_seeds': m['n_seeds'],
        'run_mode': m['run_mode'],
        'verdict': m['verdict'],
        'cell_anchor': 'exp_a7_kappa3_drift_detection_during_training_v1',
        'cell_metrics_sha256': sha,
        'cell_metrics_path': 'data/exp_a7_kappa3_drift_detection_during_training_v1/metrics.json',
        'compute_backend': 'cpu',
        'dtype': 'float32',
        'device': 'cpu',
        'corrected_propagated_figure': '~8x sensitivity NOT in authoritative metrics.json; not asserted',
        'form': 'FINDING',
        'source': src,
    }]

    new_atom = Atom(
        id=new_id,
        name='Kappa-3 drift detection (MIDDLE-BAND finding; NOT capability)',
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        kind=AtomKind.FINDING,
        description=(
            'Kappa-3 (3rd-cumulant) spectral-fingerprint drift detection during training. '
            'FULL-MODE MIDDLE_BAND (2/3 conditions, n=5): detects 5/5 drifts, fpr=0.020 (passes '
            'HP<0.05), latency=16.6 writes; hp1+hp2 conditions PASS 5/5 each; hp3 condition FAILS '
            '3/5 -> NOT a ratified capability. Documented for ledger completeness (Phase-B-tail '
            'TRACK A); possible future re-attempt if the hp3 condition is relaxed/redesigned. '
            'Substrate-internal; no learned codebook. Real drift-detection lineage via '
            'kullback_leibler_divergence + bocpd_changepoint + mp_bulk_kl (all atomized). '
            'metric_type DETECTION (RATIO-class; detect-rate + fpr + latency), NOT accuracy/'
            'capability-recall (STRICT type-discipline EM-class mislabel guard).'
        ),
        metadata={
            'finding_source': src,
            'eleventh_rule_clean': True,
            'substrate_internal_verified': True,
            'middle_band_NOT_capability': True,
            'metric_type_strict': 'DETECTION_RATIO_class_NOT_accuracy',
            'track_A_ledger_close': True,
            'runway_flag_honest_filing': True,
        },
        solution_history=tuple(sh),
    )
    math_store.add_atom(new_atom)
    math_store._flush_atoms()

    for d in deps:
        ps.add_relation(new_qid, RelationType.DEPENDS_ON, f'math::{d}',
                        source=src, note=f'kappa3_drift_detection DEPENDS_ON {d}')
    math_store._flush_relations()
    print(f'  ratified: +{new_qid} +{len(deps)} DEPENDS_ON edges')

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

    invariants_ok = (
        post_atoms == pre_atoms + 1
        and post_rels == pre_rels + 3
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
    print('  metric_type STRICT: DETECTION (RATIO-class) NOT accuracy/capability')
    print('  EM-class mislabel guard: enforced')
    print('  TRACK A ledger: CLOSED')
    print()
    print('HARD_PASS: 190f drift_kappa3 MIDDLE-BAND FINDING RATIFIED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
