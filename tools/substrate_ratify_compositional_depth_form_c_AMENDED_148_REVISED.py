"""TIER-3 compositional_depth FORM-C AMENDED ratify (DECISION 148-REVISED + 148c + Skunkworks FINAL RECONCILE).

Atomic transaction:
  ENTRY A: NOVEL-CHAIN composition (K10/15/20 axis)
    cell exp_substrate_compositional_generalization_K10_to_K20_v1_n4096 (NOW full-mode after Exp-Dev rerun)
    full-mode N=4096 3-seed (seeds 7,17,23) G=8 held-out; K10/15/20=1.0; HARD_PASS
  ENTRY B: BINDING-DEPTH (L5/L8 axis) -- 3 supporting cells
    exp_comp2_depth_l5_cpu_v1: L5 recall_cleanup=1.0 vs no_cleanup=0.007; verdict bar >=0.70
    exp_comp7_depth_l8_cpu_v1: L8 recall_cleanup=1.0 vs no_cleanup=0.0; verdict bar >=0.30
    exp_comp3_cleanup_at_depth_cpu_v1: mean SNR recovery 16.13 dB/level; per-level [31.38, 22.14, 11.0, 0.0]
  ATOM PROSE CORRECTION: replace "Pre-v3.0... 1.000 depth-indep to L8" overclaim with explicit
    two-axis disclosure (NOVEL-CHAIN K=10-20 + BINDING-DEPTH L=5-8) per Skunkworks corrected prose.

Substrate state delta: atoms unchanged, relations unchanged, additive solution_history entries
+ atom description update.
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
    cap = concept_store.get_atom(cap_qid.local_id)
    if cap is None:
        print('HARD_FAIL: PP-compositional_depth_retrieval missing')
        return 1

    # Read all 4 cells
    cells = {
        'novel_chain': {
            'metrics': repo_root / 'data/exp_substrate_compositional_generalization_K10_to_K20_v1_n4096/metrics.json',
            'rel_path': 'data/exp_substrate_compositional_generalization_K10_to_K20_v1_n4096/metrics.json',
        },
        'depth_l5': {
            'metrics': repo_root / 'data/exp_comp2_depth_l5_cpu_v1/metrics.json',
            'rel_path': 'data/exp_comp2_depth_l5_cpu_v1/metrics.json',
        },
        'depth_l8': {
            'metrics': repo_root / 'data/exp_comp7_depth_l8_cpu_v1/metrics.json',
            'rel_path': 'data/exp_comp7_depth_l8_cpu_v1/metrics.json',
        },
        'cleanup_snr': {
            'metrics': repo_root / 'data/exp_comp3_cleanup_at_depth_cpu_v1/metrics.json',
            'rel_path': 'data/exp_comp3_cleanup_at_depth_cpu_v1/metrics.json',
        },
    }
    data = {}
    shas = {}
    for k, p in cells.items():
        if not p['metrics'].exists():
            print(f'HARD_FAIL: missing metrics for {k}: {p["metrics"]}')
            return 1
        with open(p['metrics']) as f:
            data[k] = json.load(f)
        shas[k] = sha256_of(p['metrics'])

    # Corroborate full-mode for all 4
    for k, d in data.items():
        if d.get('run_mode') != 'full':
            print(f'HARD_FAIL: cell {k} run_mode != full (read {d.get("run_mode")})')
            return 1
        if d.get('verdict') != 'HARD_PASS':
            print(f'HARD_FAIL: cell {k} verdict != HARD_PASS')
            return 1

    nc = data['novel_chain']
    nc_per_seed = nc['per_seed']
    nc_seeds = [s['seed'] for s in nc_per_seed]
    nc_g = nc_per_seed[0]['G_chains']
    nc_n = nc['N']
    nc_n_seeds = nc.get('n_seeds')
    if nc_n_seeds != 3 or nc_n != 4096:
        print(f'HARD_FAIL: novel_chain not at expected 3-seed N=4096 (n_seeds={nc_n_seeds}, N={nc_n})')
        return 1
    # All seeds must show K10/K15/K20 = 1.0
    for s in nc_per_seed:
        if not (s['K10'] == 1.0 and s['K15'] == 1.0 and s['K20'] == 1.0):
            print(f'HARD_FAIL: novel_chain seed {s.get("seed")} K10/15/20 != 1.0')
            return 1
    print(f'novel_chain corroborated: 3-seed seeds={nc_seeds} N={nc_n} G={nc_g} K10/15/20=1.0 all seeds', flush=True)

    l5 = data['depth_l5']
    l5_cleanup = l5['per_seed'][0]['recall_cleanup']
    l5_nocleanup = l5['per_seed'][0]['recall_nocleanup']
    l8 = data['depth_l8']
    l8_cleanup = l8['per_seed'][0]['recall_cleanup']
    l8_nocleanup = l8['per_seed'][0]['recall_nocleanup']
    snr = data['cleanup_snr']
    snr_mean = snr['per_seed'][0]['mean_recovery_db']
    snr_per_level = snr['per_seed'][0]['per_level_recovery_db']

    print(f'depth_l5 corroborated: recall_cleanup={l5_cleanup} recall_nocleanup={l5_nocleanup}', flush=True)
    print(f'depth_l8 corroborated: recall_cleanup={l8_cleanup} recall_nocleanup={l8_nocleanup}', flush=True)
    print(f'cleanup_snr corroborated: mean_recovery_db={snr_mean} per_level={snr_per_level}', flush=True)

    # Build amended FORM-C entries
    ratify_date = '2026-06-16'
    src_amended = 'form_c_decision_148_REVISED_148c_amended_full_mode_both_axes_atomic_atom_prose_correction'

    entry_A = {
        'solution_atom_id': str(cleanup_qid),
        'adopted_date': ratify_date,
        'replaced_date': None,
        'replacement_reason': (
            'FORM-C ENTRY A NOVEL-CHAIN: K10/K15/K20=1.0 full-mode N=4096 3-seed (seeds 7,17,23) '
            'G=8 held-out generalization. Capability-recall type-verified (substrate composes chains '
            'it was NOT trained on, then recovers them). Exp-Dev 161st rerun rescued the smoke 1.0 '
            'numbers as full-mode-corroborated; distinct axis from binding-depth (L1-L8). '
            'Mechanism: cascading per-level cleanup.'
        ),
        'empirical_metric': {
            'name': 'novel_chain_composition_recall',
            'K10': 1.0,
            'K15': 1.0,
            'K20': 1.0,
            'G_chains': nc_g,
            'all_seeds_unanimous': True,
        },
        'metric_type': 'capability_recall',
        'n_seeds': nc_n_seeds,
        'run_mode': 'full',
        'N_vector': nc_n,
        'seeds': nc_seeds,
        'verdict': nc['verdict'],
        'cell_anchor': nc.get('anchor_name'),
        'cell_metrics_sha256': shas['novel_chain'],
        'cell_metrics_path': cells['novel_chain']['rel_path'],
        'form': 'FORM-C',
        'source': src_amended,
    }

    entry_B = {
        'solution_atom_id': str(cleanup_qid),
        'adopted_date': ratify_date,
        'replaced_date': None,
        'replacement_reason': (
            'FORM-C ENTRY B BINDING-DEPTH: cascading per-level cleanup makes recall depth-independent. '
            'L=5 recall_cleanup=1.0 vs recall_nocleanup=0.007 (cell exp_comp2_depth_l5); '
            'L=8 recall_cleanup=1.0 vs recall_nocleanup=0.0 (cell exp_comp7_depth_l8); '
            'mechanism quantified: hierarchical cleanup recovers mean 16.13 dB SNR/level '
            '(cell exp_comp3_cleanup_at_depth, per-level [31.38, 22.14, 11.0, 0.0]). '
            'All full-mode n=1 single-seed (weaker than novel-chain 3-seed; still load-bearing '
            'because no-cleanup collapses to ~0 -- the cleanup mechanism is causal). '
            'Per Skunkworks FINAL RECONCILE: smoke 1.000 in atom prose was conflating both axes; '
            'binding-depth axis bar was >=0.70 (L5) / >=0.30 (L8), measured at full-mode 1.0/1.0 '
            'with cleanup-on.'
        ),
        'empirical_metric': {
            'name': 'binding_depth_recall_with_cleanup',
            'L5_recall_cleanup': l5_cleanup,
            'L5_recall_nocleanup': l5_nocleanup,
            'L5_verdict_bar': 0.70,
            'L8_recall_cleanup': l8_cleanup,
            'L8_recall_nocleanup': l8_nocleanup,
            'L8_verdict_bar': 0.30,
            'mean_SNR_recovery_dB_per_level': snr_mean,
            'per_level_SNR_recovery_dB': snr_per_level,
        },
        'metric_type': 'capability_recall',
        'n_seeds': 1,
        'run_mode': 'full',
        'verdict': 'HARD_PASS',
        'cell_anchors': [
            data['depth_l5'].get('anchor_name'),
            data['depth_l8'].get('anchor_name'),
            data['cleanup_snr'].get('anchor_name'),
        ],
        'cell_metrics_sha256_l5': shas['depth_l5'],
        'cell_metrics_sha256_l8': shas['depth_l8'],
        'cell_metrics_sha256_snr': shas['cleanup_snr'],
        'cell_metrics_paths': [
            cells['depth_l5']['rel_path'],
            cells['depth_l8']['rel_path'],
            cells['cleanup_snr']['rel_path'],
        ],
        'form': 'FORM-C',
        'source': src_amended,
    }

    # ATOM-PROSE CORRECTION (atomic with FORM-C ratify per DECISION 148c)
    # Includes wave14 held-out-combination HARD_FAIL context per Exp-Dev 162nd recommendation
    # (do not over-claim generalization; novel-chain composition holds, held-out-combination doesn't).
    corrected_description = (
        'Substrate compositional depth retrieval at multi-level binding. Pre-v3.0: L5 recall 0.000 '
        '(cliff; no-cleanup collapses). Post-v3.0 via cascading per-level cleanup -- TWO distinct '
        'compositional axes, both full-mode corroborated: '
        '(a) NOVEL-CHAIN composition: K10/15/20 recall=1.00 (full-mode N=4096, 3-seed [7,17,23], '
        'G=8 held-out); (b) BINDING-DEPTH (L1-L8): depth-independent under cleanup, L5 recall_cleanup=1.0 '
        '(verdict bar >=0.70) vs no_cleanup=0.007, L8 recall_cleanup=1.0 (verdict bar >=0.30) vs '
        'no_cleanup=0.000; hierarchical cleanup recovers mean 16.13 dB SNR/level (per-level '
        '[31.38, 22.14, 11.0, 0.0]). HONEST SCOPING: substrate composes novel chains robustly (K10-20) '
        'but does NOT generalize to held-out combinations (wave14_compositional_holdout + '
        'wave14_compositional_holdout_rehab_n8192 + wave14_k6 all HARD_FAIL; distinct probes). '
        '(Prior "1.000 depth-indep to L8" conflated the two axes; smoke-K10-20 rescued via full-mode '
        'rerun by Exp-Dev 161st honest signal; binding-depth corroborated by 3 full-mode cells. '
        'Per DECISION 148-REVISED + 148c + Skunkworks FINAL RECONCILE + Exp-Dev 162nd both-dimensions '
        'recommendation.)'
    )

    # Idempotency guard
    existing = list(cap.solution_history or ())
    if any(e.get('source') == src_amended for e in existing):
        print('HARD_FAIL: amended FORM-C entries already present; abort')
        return 1

    new_sh = tuple(existing) + (entry_A, entry_B)
    cap_new = replace(cap, solution_history=new_sh, description=corrected_description)

    concept_store.add_atom(cap_new)
    concept_store._flush_atoms()

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

    cap_check = concept_store.get_atom(cap_qid.local_id)
    sh_check = cap_check.solution_history or ()
    new_count = sum(1 for e in sh_check if e.get('source') == src_amended)
    prose_corrected = 'TWO distinct compositional axes' in (cap_check.description or '')

    invariants_ok = (
        post_atoms == pre_atoms
        and post_rels == pre_rels
        and post_t == pre_t
        and post_total == pre_total
        and mod_ok
        and new_count == 2
        and prose_corrected
    )

    print(f'post: atoms={post_atoms} rels={post_rels} axiom_term={post_t}/{post_total} mod_ok={mod_ok} '
          f'amended_entries={new_count} prose_corrected={prose_corrected}', flush=True)

    if not invariants_ok:
        print('HARD_FAIL: R3 invariant violation')
        return 1

    print('R3 verify: PASS (atomic amended FORM-C + atom-prose correction; cap_pres=1.0; axiom_term unchanged)')
    print('HARD_PASS: TIER-3 compositional_depth FORM-C AMENDED + atom-prose corrected RATIFIED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
