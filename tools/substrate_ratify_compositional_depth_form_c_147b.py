"""TIER-3 compositional_depth FORM-C ratify (DECISION 147b).

Skunkworks SPEC + Exp-Dev pre-check CLEAR + Testbed PRECHECK_FLAG (smoke-mode disclosure) RESOLVED.

CAPABILITY: concept::PP-compositional_depth_retrieval (live)
MECHANISM:  math::T2/cleanup (v3.0 per-level cascading cleanup; existing in atom's solution_history)
METRIC:     K10=1.00 K15=1.00 K20=1.00 (novel-chain composition, G=2 held-out)
TYPE:       CAPABILITY-RECALL (not synthetic-recovery) -- Skunkworks + Exp-Dev confirmed
CELL:       exp_substrate_compositional_generalization_K10_to_K20_v1_n4096 (HARD_PASS)
STAMP CAVEATS (honest disclosure per Skunkworks ACK):
  - n_seeds = 1 (SINGLE-SEED; NOT multi-seed Tier-A; distinct from PP-364 n=5)
  - run_mode = smoke (NOT full-mode; despite cell name _n4096)
  - N_vector = 1024 (smoke override; NOT 4096 as cell name implies)
Form: ADD FORM-C entry to PP-compositional_depth_retrieval solution_history (additive).
"""
from __future__ import annotations
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId


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

    cap_qid = QualifiedAtomId.parse('concept::PP-compositional_depth_retrieval')
    cleanup_qid = QualifiedAtomId.parse('math::T2/cleanup')

    concept_store = ps._store_for(cap_qid.corpus)
    math_store = ps._store_for(cleanup_qid.corpus)
    cap = concept_store.get_atom(cap_qid.local_id)
    cleanup = math_store.get_atom(cleanup_qid.local_id)

    for label, a in [('PP-compositional_depth_retrieval', cap), ('math::T2/cleanup', cleanup)]:
        if a is None:
            print(f'HARD_FAIL: {label} missing in-store')
            return 1
    print('atoms verified: PP-compositional_depth_retrieval + math::T2/cleanup EXIST', flush=True)

    cell_py = repo_root / 'experiments/exp_substrate_compositional_generalization_K10_to_K20_v1_n4096.py'
    cell_metrics = repo_root / 'data/exp_substrate_compositional_generalization_K10_to_K20_v1_n4096/metrics.json'
    for p in [cell_py, cell_metrics]:
        if not p.exists():
            print(f'HARD_FAIL: cell artifact missing: {p}')
            return 1

    cell_py_sha = sha256_of(cell_py)
    cell_metrics_sha = sha256_of(cell_metrics)

    with open(cell_metrics) as f:
        m = json.load(f)

    # ---- corroborate metric values (sharpened principle: read metrics, never name) ----
    per_seed_0 = m['per_seed'][0]
    k10 = per_seed_0.get('K10')
    k15 = per_seed_0.get('K15')
    k20 = per_seed_0.get('K20')
    g_chains = per_seed_0.get('G_chains')
    n_seeds = m.get('n_seeds')
    run_mode = m.get('run_mode')
    n_vector = m.get('N')
    verdict = m.get('verdict')

    if not (k10 == 1.0 and k15 == 1.0 and k20 == 1.0):
        print(f'HARD_FAIL: K10/K15/K20 not all 1.0 (read: {k10}/{k15}/{k20})')
        return 1
    if g_chains != 2:
        print(f'HARD_FAIL: G_chains != 2 (read: {g_chains})')
        return 1
    if verdict != 'HARD_PASS':
        print(f'HARD_FAIL: verdict != HARD_PASS (read: {verdict})')
        return 1
    if n_seeds != 1:
        print(f'WARN: n_seeds expected 1 (single-seed per spec), got {n_seeds}')
    print(f'metric corroboration: K10={k10} K15={k15} K20={k20} G_chains={g_chains} '
          f'n_seeds={n_seeds} run_mode={run_mode} N={n_vector} verdict={verdict}', flush=True)

    # ---- build FORM-C lift entry with full honest disclosure ----
    ratify_date = '2026-06-16'
    form_c_source = 'form_c_decision_147b_skunkworks_release_n1_single_seed_stamp_accepted'

    form_c_entry = {
        'solution_atom_id': str(cleanup_qid),
        'adopted_date': ratify_date,
        'replaced_date': None,
        'replacement_reason': (
            'FORM-C capability-recall provenance attach: novel-chain composition K10=K15=K20=1.0 '
            'with G=2 held-out generalization; per-binding cascading cleanup mechanism (v3.0 cliff '
            'crossing). Type-verify CONFIRMED capability-recall (not synthetic-recovery; novel-chain '
            'composition is held-out generalization, not trained-item recovery). '
            'HONEST DISCLOSURE: n_seeds=1 SINGLE-SEED stamp (NOT multi-seed Tier-A like PP-364); '
            'cell ran in smoke mode at N=1024 (not full-mode N=4096 as cell name implies); '
            'distinct compositional axis (chain-length K10-K20) from existing depth axis (L1-L8); '
            'optional later strengthening via multi-seed cell wave14_compositional_holdout_rehab_n8192.'
        ),
        'empirical_metric': {
            'name': 'novel_chain_composition_recall',
            'K10': k10,
            'K15': k15,
            'K20': k20,
            'G_chains': g_chains,
        },
        'metric_type': 'capability_recall',
        'n_seeds': n_seeds,
        'run_mode': run_mode,
        'N_vector': n_vector,
        'verdict': verdict,
        'cell_anchor': m.get('anchor_name'),
        'cell_py_sha256': cell_py_sha,
        'cell_metrics_sha256': cell_metrics_sha,
        'cell_metrics_path': 'data/exp_substrate_compositional_generalization_K10_to_K20_v1_n4096/metrics.json',
        'form': 'FORM-C',
        'source': form_c_source,
    }

    # ---- idempotency guard ----
    existing = list(cap.solution_history or ())
    if any(e.get('source') == form_c_source for e in existing):
        print('HARD_FAIL: FORM-C entry already present; abort')
        return 1

    new_sh = tuple(existing) + (form_c_entry,)
    cap_new = replace(cap, solution_history=new_sh)

    concept_store.add_atom(cap_new)
    concept_store._flush_atoms()

    # ---- post-snapshot + R3 verify ----
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

    cap_check = ps._store_for(cap_qid.corpus).get_atom(cap_qid.local_id)
    sh_check = cap_check.solution_history or ()
    landed = sum(1 for e in sh_check if e.get('source') == form_c_source)

    invariants_ok = (
        post_atoms == pre_atoms
        and post_rels == pre_rels
        and post_t == pre_t
        and post_total == pre_total
        and mod_ok
        and landed == 1
    )

    print(f'post: atoms={post_atoms} rels={post_rels} axiom_term={post_t}/{post_total} '
          f'mod_ok={mod_ok} form_c_entries_landed={landed}', flush=True)

    if not invariants_ok:
        print('HARD_FAIL: R3 invariant violation')
        return 1

    print('R3 verify: PASS (additive; cap_pres=1.0; axiom_term unchanged; FORM-C entry landed with honest disclosure)')
    print('HARD_PASS: TIER-3 compositional_depth FORM-C capability-recall provenance RATIFIED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
