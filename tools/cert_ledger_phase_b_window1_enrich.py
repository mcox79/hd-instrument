"""Phase B window-1 (2026-06-15 to 2026-06-21) prose-enrichment of cert_ledger.jsonl.

Reads existing seeded ledger rows + appends cert_relabel rows (one per (atom_qualified_id,
note) pair) that fill notes_path / verified_off_data / cert_class / ts from the parsed
landed-VET / atomize / SCHEMA-VET notes in the window.

Heuristic discipline (per proposal Section 6 fragility flag + Director cross-check):
- verified_off_data = TRUE only when the note explicitly says "verified off (the) data",
  "verified off per_unit", "independently verified", "independent recompute", "verified off
  the data", "verify off DATA, not reports", "off per_unit", "off the per_unit",
  "re-derived from per_unit", "ASCII recompute matched". DEFAULT to NULL.
- supersedes points to the Phase-A seeded row by (atom_id, op, atomized_by) tuple. Phase A
  rows are line-anchored; we compute a stable hash from the seeded row's content.
- ts derived from note-file mtime as the fallback (since audit.jsonl is empty for these).
- This is a CURATED prose-extract: I read each note before writing the row, NOT a regex
  auto-parse over all 577 in-window notes. ~25-30 high-value notes give the highest signal-
  to-noise.

Pre/Post A5 gate:
- PRE: CERT N from Store == 583 (or current); axiom 206; cap_pres 6/6
- WRITE: append rows via os.replace-of-tmp (full-file rewrite of existing + appended)
- POST: re-load Store; CERT N unchanged (relabels are delta-0); ledger row count == prev + N_new

Run:
    .venv/Scripts/python.exe tools/cert_ledger_phase_b_window1_enrich.py
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore


LEDGER_PATH = Path('data/substrate_index/meta/cert_ledger.jsonl')
NOTES_DIR = Path('notes')


def cert(p):
    return sum(1 for a in p.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def axiom_count(p):
    return sum(
        1 for a in p.all_atoms()
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def modlive():
    import importlib
    return all(
        hasattr(importlib.import_module(m), s) for m, s in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ]
    )


def cap_pres_str():
    return '6/6' if modlive() else 'FAIL'


def row_hash(row):
    """Stable hash of a ledger row for supersedes chains."""
    canonical = json.dumps(row, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode('ascii')).hexdigest()[:16]


def note_mtime_ts(note_path):
    """Get file mtime as ts fallback.

    note_path is a string like 'notes/<file>.md' (already includes the dir prefix);
    use as a relative Path directly.
    """
    p = Path(note_path)
    if p.exists():
        return float(int(p.stat().st_mtime))
    return None


# ============================================================================
# CURATED CERT EXTRACTIONS from 2026-06-15..2026-06-21 landed-VET notes.
#
# Each entry was MANUALLY parsed from the named note. verified_off_data set
# conservatively per the proposal Section 6 fragility flag.
#
# Fields:
#   atom_id_substr: substring to match the seeded Phase A row's atom_qualified_id
#   notes_path: the committed VET note in notes/
#   verified_off_data: TRUE only if the note explicitly asserts verify-off-data; else NULL
#   cert_class: pre_reg_pass / post_hoc_pass / mechanism_characterization / pre_reg_miss_proven_bound
#               / discipline_meta / data_attribution / infra_record
#   cell_commit: 8-12 char git SHA if the note cites one; else None
#   verdict_override: if the note refines the seeded verdict (rare); else None
#   cv: float if the note cites a seed-CV; else None
#   note_tag: 1-line ASCII discipline tag (no prose)
#   manually_reviewed: TRUE if this entry was part of the manual-review-pass sample
# ============================================================================

ENRICHMENTS = [
    # (1) CERT 579 b_alpha_broad + partof_broad pull-up family
    {
        'atom_id_substr': 'T3/EXP_b_alpha_broad_v2_denser_preview',
        'notes_path': 'notes/skunkworks_to_all_CERT_579_landed_VET_PASS_confirmed_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_miss_proven_bound',  # MIDDLE_BAND pull-up under chain-grade tag
        'cell_commit': None,
        'note_tag': 'cert_579_4atom_pullup_metrics_source_measured_graph_bfs_held_out_single_writer_window_held',
        'manually_reviewed': True,
    },
    {
        'atom_id_substr': 'T3/EXP_b_alpha_broad_v3_2level',
        'notes_path': 'notes/skunkworks_to_all_CERT_579_landed_VET_PASS_confirmed_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_miss_proven_bound',
        'cell_commit': None,
        'note_tag': 'cert_579_4atom_pullup_metrics_source_measured_graph_bfs_held_out_single_writer_window_held',
        'manually_reviewed': True,
    },
    {
        'atom_id_substr': 'T3/EXP_partof_broad_after',
        'notes_path': 'notes/skunkworks_to_all_CERT_579_landed_VET_PASS_confirmed_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_pass',  # HARD_PASS in note
        'cell_commit': None,
        'note_tag': 'cert_579_4atom_pullup_partof_broad_after_HARD_PASS_measured_graph_bfs_held_out',
        'manually_reviewed': True,
    },
    {
        'atom_id_substr': 'T3/EXP_partof_broad_before',
        'notes_path': 'notes/skunkworks_to_all_CERT_579_landed_VET_PASS_confirmed_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_miss_proven_bound',
        'cell_commit': None,
        'note_tag': 'cert_579_4atom_pullup_partof_broad_before_MIDDLE_BAND_measured_graph_bfs_held_out',
        'manually_reviewed': True,
    },

    # (2) CERT 580 ConceptNet Track-B knowledge_graph
    {
        'atom_id_substr': 'T3/EXP_conceptnet_kg_inference_transfer_cpu_v1',
        'notes_path': 'notes/skunkworks_to_all_CONCEPTNET_CERT580_landed_VET_PASS_TrackB_COMPLETE_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_miss_proven_bound',  # HARD_FAIL primary + HARD_PASS fact_fab sub
        'cell_commit': '8046977b0292',
        'note_tag': 'cert_580_track_b_kg_honest_negative_fact_fab_bound_HARD_PASS_substrate_underperforms_bge_singlehop',
        'manually_reviewed': True,
    },

    # (3) CERT 583 = 3-MM promote + ConceptNet
    {
        'atom_id_substr': 'T3/EXP_a1_8a_4channel',
        'notes_path': 'notes/skunkworks_to_all_3MM_promote_landed_VET_PASS_CERT583_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'mechanism_characterization',  # ATTRIBUTION = MM
        'cell_commit': None,
        'note_tag': 'cert_583_3mm_pq_promote_attribution_measured_torch_gpu_key_metrics_present',
        'manually_reviewed': False,
    },
    {
        'atom_id_substr': 'T3/EXP_a1v2_ratio_profile',
        'notes_path': 'notes/skunkworks_to_all_3MM_promote_landed_VET_PASS_CERT583_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'mechanism_characterization',
        'cell_commit': None,
        'note_tag': 'cert_583_3mm_pq_promote_attribution_measured_torch_gpu',
        'manually_reviewed': False,
    },
    {
        'atom_id_substr': 'T3/EXP_a1_multihop_provenance',
        'notes_path': 'notes/skunkworks_to_all_3MM_promote_landed_VET_PASS_CERT583_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'mechanism_characterization',
        'cell_commit': None,
        'note_tag': 'cert_583_3mm_pq_promote_a1_multihop_band_exists_n_seeds_1_single_seed_not_robust_WIN',
        'manually_reviewed': False,
    },

    # (4) CERT 586 continual-writes pull-up (HARD_PASS, region-scoped honest)
    {
        'atom_id_substr': 'T3/EXP_a8_continual_writes_no_catastrophic_forgetting_v1',
        'notes_path': 'notes/skunkworks_to_all_continual_writes_CERT586_landed_VET_PASS_first_pullup_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_pass',
        'cell_commit': 'b7dde459c4fe',
        'note_tag': 'cert_586_first_value_coverage_pullup_no_catastrophic_forgetting_alpha_0p30_measured_cliff_seed_std_0p000',
        'manually_reviewed': True,
    },

    # (5) CERT 587 conformal_splitcp (MIDDLE_BAND honest BOUND)
    {
        'atom_id_substr': 'T3/EXP_conformal_splitcp_cpu_v1',
        'notes_path': 'notes/skunkworks_to_all_conformal_CERT587_landed_VET_PASS_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_miss_proven_bound',  # honest BOUND
        'cell_commit': 'df0e61a31620',  # from existing seed row
        'note_tag': 'cert_587_2nd_value_coverage_pullup_distribution_free_coverage_set_size_tight_multi_class_loose_binary',
        'manually_reviewed': True,
    },

    # (6) CERT 588 q_b1_ab_iterate swap (HARD_PASS, integration-FAIL on I4/I5 then re-VET)
    {
        'atom_id_substr': 'T3/EXP_q_b1_ab_iterate_3arm_v1_n16384',
        'notes_path': 'notes/skunkworks_to_expdev_qb1_swap_landed_VET_INTEGRATION_FAIL_I4_I5_2_field_fixes_on_AB_atom_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_pass',  # HARD_PASS chain-grade; I4/I5 metadata-fix only, no cert change
        'cell_commit': None,
        'note_tag': 'cert_588_q_b1_chain_depth_cleanup_between_hops_d293_5of5_seeds_capint_proven_bound_locked',
        'manually_reviewed': True,
    },

    # (7) CERT 589 phase4b multistep pull-up (HARD_PASS, I1/I3/I5 clean)
    {
        'atom_id_substr': 'T3/EXP_phase4b_multistep_pull_up_v2_cpu_v1',
        'notes_path': 'notes/skunkworks_to_expdev_orchestrator_phase4b_CERT589_landed_VET_PASS_first_fullcycle_pullup_DONE_2026-06-19.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_pass',  # HARD_PASS, is_bound=False, integration-PASS
        'cell_commit': None,
        'note_tag': 'cert_589_first_value_coverage_pullup_full_cycle_integration_pass_492',
        'manually_reviewed': True,
    },

    # (8) CERT 589 LEVER 4 multiplicative_composition_lever_v1_cpu_v1 (chain-grade-ELIGIBLE depth-axis refuse-gate)
    {
        'atom_id_substr': 'T3/EXP_multiplicative_composition_lever_v1_cpu_v1',
        'notes_path': 'notes/skunkworks_to_expdev_testbed_cc_orch_research_LEVER_4_landed_VET_CHAINGRADE_ELIGIBLE_depth_refuse_gate_4layer_witness_CERT_589_2026-06-20.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_pass',
        'cell_commit': '232a679c',
        'note_tag': 'cert_589_lever_4_depth_axis_refuse_gate_robust_at_high_fab_loads_K_max_calibrated_per_load_chain_grade_eligible',
        'manually_reviewed': False,
    },

    # (9) CERT 591 glass-box-KV learned projection (HARD_PASS, post Phase A snapshot)
    {
        'atom_id_substr': 'T3/EXP_kv_learned_projection_v1',
        'notes_path': 'notes/skunkworks_to_all_7_glassbox_KV_LANDED_my_invariant_CONFIRMS_CERT_591_TRUE_HARD_PASS_0_phantoms_2026-06-20.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_pass',
        'cell_commit': None,  # phase A had no cell_sha for this
        'note_tag': 'cert_591_glassbox_kv_learned_contrastive_projection_pythia_2p8b_heldout_recall_0p83_0p96_disjoint_split_shuffled_control',
        'manually_reviewed': True,
    },

    # (10) CERT 590 CSP first ship (HARD_PASS, 8.42x speedup, non-regressing-by-proof)
    {
        'atom_id_substr': 'T3/EXP_csp_first_ship_v1',
        'notes_path': 'notes/skunkworks_to_all_CSP_PHASE1_milestone_COMPLETE_my_invariant_check_CONFIRMS_CERT_590_TRUE_HARD_PASS_2026-06-20.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_pass',
        'cell_commit': None,
        'note_tag': 'cert_590_first_phase1_0to1_ship_csp_warm_start_8p42x_speedup_no_recall_degrade_non_regressing_proof_8_dependents',
        'manually_reviewed': True,
    },

    # (11) refuse-gate #5 (b) graph-health -- STRONG, chain-grade-ELIGIBLE pending 2 residuals
    # No cell-atom in seed (yet to atomize) -- skip; tracked via the note's residuals.

    # (12) LEVER 1.5 v1 -> NOT chain-grade (non-adaptive selector, no sweet-spot)
    # v1 cell pq=SMOKE_ONLY likely; not in seed. Check.
    # Atomized as MM in v2 only -- v2 atom may not be in seed either. Skip auto-match; surface
    # as window-1 debt instead.

    # (13) CERT 583 pythia desat (HARD_PASS, EARNED chain-grade)
    {
        'atom_id_substr': 'T3/EXP_pythia_kv_desat_v2',
        'notes_path': 'notes/skunkworks_to_orchestrator_research_expdev_cc_all_PYTHIA_DESAT_LANDED_VET_CERT_583_EARNED_prelim_direction_correction_2026-06-21.md',
        'verified_off_data': True,
        'cert_class': 'pre_reg_pass',  # HARD_PASS chain-grade EARNED
        'cell_commit': 'bfcc0af7',
        'note_tag': 'cert_583_first_earned_upward_pythia_desat_v2_sigma_0p5_can_fail_6_sizes_monotone_size_crowding_negative_random_margin_correctly_interpreted',
        'manually_reviewed': True,
    },

    # (14) dense KV envelope MM (now chain-grade-at-bound GATED on calibration follow-up)
    {
        'atom_id_substr': 'T3/EXP_dense_projected_KV_envelope_v1',
        'notes_path': 'notes/skunkworks_to_research_expdev_cc_orch_LANDED_VET_dense_KV_envelope_MM_now_chain_grade_at_bound_GATED_on_calibration_plus_learned_key_followup_2026-06-21.md',
        'verified_off_data': True,
        'cert_class': 'mechanism_characterization',  # MM, CERT-neutral
        'cell_commit': None,
        'note_tag': 'mm_dense_kv_envelope_m_indep_superposition_c_codebook_lift_random_keys_upper_bound_substrate_chain_grade_gated_pythia_followup',
        'manually_reviewed': True,
    },

    # (15) continual_write_label_free_importance_v1 MM (scope-locating; B-info-theoretic limit confirmed)
    {
        'atom_id_substr': 'T3/EXP_continual_write_label_free_importance_v1',
        'notes_path': 'notes/skunkworks_to_expdev_research_cc_orch_CONTINUAL_WRITE_landed_VET_MM_atomized_v4_optional_2026-06-21.md',
        'verified_off_data': True,
        'cert_class': 'mechanism_characterization',
        'cell_commit': '7f39f342',
        'note_tag': 'mm_label_free_importance_works_iff_access_correlated_workload_b_info_theoretic_limit',
        'manually_reviewed': False,
    },

    # (16) flagship sparse projected KV LBUILD MM honest-negative (capacity-via-sparsification FAILS)
    {
        'atom_id_substr': 'T3/EXP_flagship_sparse_projected_KV_LBUILD_v1',
        'notes_path': 'notes/skunkworks_to_research_orchestrator_expdev_cc_all_FLAGSHIP_LBUILD_landed_VET_HONEST_NEGATIVE_atomized_revival_dense_projected_pivot_2026-06-21.md',
        'verified_off_data': True,
        'cert_class': 'mechanism_characterization',  # MM honest-negative
        'cell_commit': 'c13268e2',
        'note_tag': 'mm_honest_negative_flagship_sparsification_fails_capacity_recall_pivot_to_dense_projected_kv_cert591',
        'manually_reviewed': False,
    },

    # (17) 5 hidden-positives: 3 reclassified -> MM (CERT 588 -> 585 DEMOTE)
    # These are DEMOTE events. Per proposal Section 1, op=cert_demote with delta=-1.
    # Affected atoms: continual_learning_empirical_10e9x / drosophila_mb_sparsity / data_attribution_counterfactual_rpe
    # These are now MM in seed (Phase A seed read them as MM via Store provenance_quality);
    # however the seed gives them cert_status=measured_mechanism with delta=0. The DEMOTE
    # event happened BEFORE Phase A seed (the Store flag already reflects post-demote state).
    # So these atoms' "demote history" lives in the note only -- no row-state change needed,
    # just an enrichment row with notes_path/cert_class.
    {
        'atom_id_substr': 'T3/EXP_substrate_continual_learning_empirical_10e9x_v1',
        'notes_path': 'notes/skunkworks_to_research_cc_orch_expdev_testbed_HIDDEN_POSITIVES_landed_VET_3of5_MM_CERT_585_2_HELD_2026-06-21.md',
        'verified_off_data': True,
        'cert_class': 'mechanism_characterization',
        'cell_commit': '76a4e7b7235b',
        'note_tag': 'mm_genuine_27x_speedup_zero_forget_pythia_160m_3seed_1000x_was_large_llm_aspiration_wrong_bar_demote_reclassified',
        'manually_reviewed': False,
    },
    {
        'atom_id_substr': 'T3/EXP_substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu',
        'notes_path': 'notes/skunkworks_to_research_cc_orch_expdev_testbed_HIDDEN_POSITIVES_landed_VET_3of5_MM_CERT_585_2_HELD_2026-06-21.md',
        'verified_off_data': True,
        'cert_class': 'mechanism_characterization',
        'cell_commit': '912a228fc8ee',
        'note_tag': 'mm_genuine_robust_f0p05_plus_0p142_3of3_seeds_middle_anchored_on_best_f0p01_only_2of3_partial_reclassified',
        'manually_reviewed': False,
    },
    {
        'atom_id_substr': 'T3/EXP_substrate_data_attribution_counterfactual_rpe_v1_n4096',
        'notes_path': 'notes/skunkworks_to_research_cc_orch_expdev_testbed_HIDDEN_POSITIVES_landed_VET_3of5_MM_CERT_585_2_HELD_2026-06-21.md',
        'verified_off_data': True,
        'cert_class': 'mechanism_characterization',
        'cell_commit': 'ecc6306bc3b8',
        'note_tag': 'mm_cpe_rho_0p694_matches_tracin_baseline_0p693_at_4p16x_speedup_HARD_PASS_ge_0p8_unachievable_by_either_wrong_bar',
        'manually_reviewed': False,
    },

    # (18) Sparse-#2 reframe -- 8x@f0.10/20x@f0.02 genuine, "1.4x was a miscite"
    # Atom T3/EXP_substrate_sparse_recall_capacity_a3f473dd (a3473dd commit). Check seed.
    # Skip auto-match if not in seed -- surface as window debt.

    # (19) pythia-KV v3.1 HARD_FAIL honest-negative
    # Atom not in Phase A seed (pre-CERT 591 honest-negative).

    # (20) CERT 574 Item-4 reconcile (v2.1 round-trip-survival PASS)
    # AUDIT_LESSON family atoms; the relevant cert event is metadata-hygiene, not a cell-atom.

    # (21) I1 de-integration (1c1)
    # Smoke-only atoms moved out of Track-A; no chain-grade event.

    # (22) Witness #4 inst-240 self-referential
    # AUDIT_LESSON atom (silent-loss family); not in seed as cell-atom.

    # (23) no-Goodhart re-bind (5 conceptual_references)
    # AUDIT_LESSON / METHODOLOGY_RULE bind hygiene; no cell-atom cert event.
]


def find_seeded_row(atom_id_substr, rows):
    """Find the first Phase A seeded row whose atom_qualified_id contains the substr."""
    for r in rows:
        if atom_id_substr in (r.get('atom_id') or ''):
            return r
    return None


def main():
    print('=' * 72)
    print('Phase B window-1 (2026-06-15..2026-06-21) prose-enrichment')
    print('=' * 72)

    # ---------------- A5 PRE ----------------
    print('\n[PRE-GATE]')
    S = PartitionedStore(Path('data/substrate_index'))
    pre_cert = cert(S)
    pre_ax = axiom_count(S)
    pre_cap = cap_pres_str()
    pre_n = sum(1 for _ in S.all_atoms())
    print(f'  CERT N = {pre_cert}')
    print(f'  axiom_count = {pre_ax}')
    print(f'  cap_pres = {pre_cap}')
    print(f'  total atoms = {pre_n}')
    assert pre_ax == 206, f'axiom_count != 206 (got {pre_ax})'
    assert pre_cap == '6/6', f'cap_pres != 6/6 (got {pre_cap})'
    print('  PRE-GATE PASS')

    if not LEDGER_PATH.exists():
        print(f'  ABORT: ledger does not exist at {LEDGER_PATH}; run Phase A first')
        sys.exit(1)

    # ---------------- LOAD EXISTING ROWS ----------------
    print('\n[LOAD existing ledger]')
    existing_rows = []
    for line in LEDGER_PATH.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        existing_rows.append(json.loads(line))
    print(f'  Loaded {len(existing_rows)} existing rows')

    pre_audit_debt = sum(1 for r in existing_rows if r.get('verified_off_data') in (None, False))
    pre_notes_null = sum(
        1 for r in existing_rows
        if (r.get('referent_pointer') or {}).get('notes_path') is None
    )
    print(f'  audit-debt-queue size (verified_off_data null/false): {pre_audit_debt}')
    print(f'  rows with notes_path null: {pre_notes_null}')

    # ---------------- BUILD ENRICHMENT ROWS ----------------
    print('\n[BUILD enrichment rows]')
    new_rows = []
    stats = {
        'matched': 0,
        'unmatched': 0,
        'verified_off_data_true': 0,
        'verified_off_data_null': 0,
        'cert_class_counts': {},
        'ts_from_mtime': 0,
        'ts_null': 0,
        'cell_commit_backfilled': 0,
    }
    unmatched_atom_ids = []

    for entry in ENRICHMENTS:
        substr = entry['atom_id_substr']
        seeded = find_seeded_row(substr, existing_rows)
        if seeded is None:
            stats['unmatched'] += 1
            unmatched_atom_ids.append(substr)
            print(f'  UNMATCHED: {substr} (no Phase A seed row)')
            continue
        stats['matched'] += 1

        # supersedes = hash of the seeded row (prior identity per Phase A convention)
        supersedes_hash = row_hash(seeded)

        # ts from note mtime
        ts = note_mtime_ts(entry['notes_path'])
        if ts is not None:
            stats['ts_from_mtime'] += 1
        else:
            stats['ts_null'] += 1

        # cell_commit backfill if available
        new_cell_commit = entry.get('cell_commit') or seeded.get('cell_commit')
        if entry.get('cell_commit') and not seeded.get('cell_commit'):
            stats['cell_commit_backfilled'] += 1

        # verified_off_data
        vod = entry.get('verified_off_data')
        if vod is True:
            stats['verified_off_data_true'] += 1
        else:
            stats['verified_off_data_null'] += 1

        cc = entry.get('cert_class')
        stats['cert_class_counts'][cc] = stats['cert_class_counts'].get(cc, 0) + 1

        # Construct cert_relabel row
        # cert_status + cert_increment_delta are PRESERVED from the seeded row (relabels are CERT-neutral)
        relabel = {
            'ts': ts,
            'op': 'cert_relabel',
            'atom_id': seeded['atom_id'],
            'cert_status': seeded['cert_status'],  # preserved
            'cert_class': cc,  # NEW from prose
            'verified_off_data': vod,  # NEW from prose
            'atomized_by': 'skunkworks_phase_b_window1',
            'cell_commit': new_cell_commit,
            'verdict': seeded.get('verdict'),
            'cert_increment_delta': 0,  # relabel is always delta-0
            'cv': entry.get('cv'),
            'referent_pointer': {
                'notes_path': entry['notes_path'],  # NEW from prose
                'metrics_path': (seeded.get('referent_pointer') or {}).get('metrics_path'),
                'atom_qualified_id': seeded['atom_id'],
            },
            'supersedes': supersedes_hash,
            'note': entry['note_tag'],
        }
        new_rows.append(relabel)

    print(f'  Matched {stats["matched"]} / Unmatched {stats["unmatched"]}')
    print(f'  verified_off_data: true={stats["verified_off_data_true"]} / null={stats["verified_off_data_null"]}')
    print(f'  ts: from_mtime={stats["ts_from_mtime"]} / null={stats["ts_null"]}')
    print(f'  cell_commit backfilled: {stats["cell_commit_backfilled"]}')
    print(f'  cert_class distribution:')
    for cc, n in sorted(stats['cert_class_counts'].items(), key=lambda x: -x[1]):
        print(f'    {cc}: {n}')
    if unmatched_atom_ids:
        print(f'  UNMATCHED atom_id substrings (surfaced as window-1 debt):')
        for s in unmatched_atom_ids:
            print(f'    - {s}')

    # ---------------- WRITE ----------------
    print('\n[WRITE]')
    if not new_rows:
        print('  No new rows to write; exiting')
        return

    all_rows = existing_rows + new_rows
    tmp = LEDGER_PATH.with_suffix('.jsonl.tmp.' + str(os.getpid()))
    with tmp.open('w', encoding='ascii', newline='\n') as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=True) + '\n')
    os.replace(tmp, LEDGER_PATH)
    print(f'  Appended {len(new_rows)} cert_relabel rows; total ledger rows = {len(all_rows)}')

    # ---------------- A5 POST ----------------
    print('\n[POST-GATE]')
    S2 = PartitionedStore(Path('data/substrate_index'))  # re-load to catch NULL-seam
    post_cert = cert(S2)
    post_ax = axiom_count(S2)
    post_cap = cap_pres_str()
    post_n = sum(1 for _ in S2.all_atoms())
    print(f'  CERT N = {post_cert} (delta: {post_cert - pre_cert})')
    print(f'  axiom_count = {post_ax}')
    print(f'  cap_pres = {post_cap}')
    print(f'  total atoms = {post_n} (delta: {post_n - pre_n})')

    assert post_cert == pre_cert, 'CERT delta != 0 (Phase B relabel is CERT-neutral)'
    assert post_ax == 206, f'axiom drift {post_ax}'
    assert post_cap == '6/6', f'cap_pres drift {post_cap}'
    assert post_n == pre_n, f'atom-count drift'

    # Ledger roundtrip
    reloaded = []
    for line in LEDGER_PATH.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        reloaded.append(json.loads(line))
    assert len(reloaded) == len(all_rows), f'reload count mismatch: {len(reloaded)} vs {len(all_rows)}'
    # sum of cert_increment_delta unchanged (relabels = 0)
    sum_delta = sum(r.get('cert_increment_delta') or 0 for r in reloaded)
    pre_sum = sum(r.get('cert_increment_delta') or 0 for r in existing_rows)
    assert sum_delta == pre_sum, f'sum(cert_increment_delta) changed: {pre_sum} -> {sum_delta} (Phase B should be 0-net)'

    post_audit_debt = sum(1 for r in reloaded if r.get('verified_off_data') in (None, False))
    post_notes_null = sum(
        1 for r in reloaded
        if (r.get('referent_pointer') or {}).get('notes_path') is None
    )

    print('  POST-GATE PASS')
    print(f'\n  Audit-debt-queue: {pre_audit_debt} -> {post_audit_debt} (delta: -{pre_audit_debt - post_audit_debt})')
    print(f'  Notes-path-null: {pre_notes_null} -> {post_notes_null} (delta: -{pre_notes_null - post_notes_null})')

    print('\n' + '=' * 72)
    print('Phase B window-1 enrichment COMPLETE')
    print('=' * 72)


if __name__ == '__main__':
    main()
