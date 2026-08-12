"""One-shot ledger append for two 2026-06-28 atomization gaps.

Gap 1: Higher_order_TOM v2 reframed CLOSED-negative (test-design-limited)
   - 2x-witness evidence: v1 MIDDLE_BAND flat-depth (3 seeds) + v2 HARD_FAIL_FLAT_DEPTH_PROFILE
   - Honest negative: the test-design at 4 locations cannot discriminate recursive depth;
     the bound is on the INSTRUMENT (4-loc cleanup-attractor ceiling), not a substrate
     capability disproof. Need v3 with larger N_LOCATIONS + per-level distractor scaling
     to actually characterize higher-order TOM as a function of recursion depth.
   - 2x-drill discipline satisfied: v1 + v2 are two separate mechanism-class drills
     (per-trial-independent v1 vs interleaved-chains v2); both surfaced the SAME flat-depth
     ceiling at ~0.70-0.80. The closure is on test-design-limited; substrate capability
     itself remains uncharacterized at this depth regime.

Gap 2: role_tagged_compositional MM ruling (Skunkworks 2026-06-25)
   - Already ruled MM (by-construction-saturation: label-driven encoder pre-fuses
     same-category instances into shared category basis at construction time).
   - HYBRID arm 1.000/1.000/1.000 cv=0 across 3 seeds; mechanism trace confirms
     6x lift attributable 100% to encoder, 0% to role-binding composition.
   - Subsidiary direction-correct finding: clustered-vs-ortho +0.167 mean (USER
     intuition direction-correct but not chain-grade at n=3 seeds x 8 heldout).
   - cert_increment_delta: 0 (MM not chain-grade)

Both writes use cert_ledger_writer.build_*_row helpers with strict A5 gating
(expected_cert_n_pre == expected_cert_n_post == 630, both delta=0 entries).
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_honest_negative_row,
    build_measured_mechanism_row,
)


def write_gap_1_higher_order_tom_v2_reframed_honest_negative():
    """Atom id chosen for filename-contains discoverability + 2x-witness phrasing."""
    atom_id = (
        'math::T3/EXP_substrate_higher_order_tom_recursive_v2_reframed_'
        'HONEST_NEGATIVE_test_design_limited_4_loc_cleanup_attractor_ceiling_'
        'flat_depth_profile_2x_witness_v1_MB_and_v2_HF_max_depth_var_0p030_'
        'lt_0p05_threshold_pos_control_0p75_lt_0p95_target_mb_cells_21_of_32_'
        'capacity_floor_not_substrate_depth_disproof_v3_needs_larger_N_LOCATIONS_'
        'and_per_level_distractor_scaling_2026-06-28'
    )
    row = build_honest_negative_row(
        atom_id=atom_id,
        cell_commit='c9484c52',
        verdict='HARD_FAIL_FLAT_DEPTH_PROFILE_smoke_no_full_dispatch_per_prereg_STOP',
        notes_path=(
            'notes/exp_dev_tom_recursive_v2_reframed_smoke_'
            'HARD_FAIL_FLAT_DEPTH_PROFILE_2026-06-28.md'
        ),
        metrics_path=(
            'data/exp_substrate_higher_order_tom_recursive_v2_reframed_smoke/'
            'metrics.json'
        ),
        cert_class='pre_reg_miss_proven_bound',
        atomized_by='skunkworks_audit_only_atomization_gap_close_2026-06-28',
        verified_off_data=True,
        note=(
            'tom_recursive_v2_reframed_closure_2x_witness_DRILL_2_OF_2_v1_MB_'
            'flat_depth_and_v2_HF_flat_depth_both_test_design_limited_4_loc_'
            'cleanup_attractor_ceiling_substrate_capability_NOT_disproven_'
            'needs_v3_instrument_with_larger_N_LOCATIONS_per_level_distractor_'
            'scaling_or_higher_rank_tensor_encoder_per_pre_reg_STOP_rule_'
            'NO_full_dispatch_issued'
        ),
    )
    h = append_cert_ledger_row(
        row,
        expected_cert_n_pre=630,
        expected_cert_n_post=630,
    )
    return atom_id, h


def write_gap_2_role_tagged_compositional_mm():
    """MM ruling already established 2026-06-25; ledger transcription only."""
    atom_id = (
        'math::T3/EXP_substrate_role_tagged_compositional_generalization_on_'
        'concept_KG_v1_MEASURED_MECHANISM_by_construction_saturation_label_'
        'driven_encoder_carries_lift_HYBRID_1p000_cv_0p000_3seeds_NO_ROLES_'
        '0p167_ORTHO_0p167_CLUSTERED_0p333_GRAMMATICAL_0p083_role_binding_'
        'neutral_encoder_pre_fuses_category_basis_at_construction_'
        'subsidiary_clustered_vs_ortho_0p167_direction_correct_USER_intuition_'
        'not_chain_grade_at_n3seeds_x_8heldout_2026-06-25'
    )
    row = build_measured_mechanism_row(
        atom_id=atom_id,
        cell_commit='n/a-skunkworks-2026-06-25-tier-ruling-transcription',
        verdict=(
            'HARD_PASS_CHAIN_GRADE_from_cell_REVISED_to_MEASURED_MECHANISM_by_'
            'skunkworks_by_construction_saturation_label_driven_encoder_HYBRID_'
            '1p000_cv_0p000_3seeds_attributable_100pct_encoder_0pct_role_binding'
        ),
        notes_path=(
            'notes/skunkworks_tier_ruling_cell5_role_tagged_compgen_KG_'
            '2026-06-25.md'
        ),
        metrics_path=(
            'data/exp_substrate_role_tagged_compositional_generalization_on_'
            'concept_KG_v1/metrics.json'
        ),
        atomized_by='skunkworks_audit_only_atomization_gap_close_2026-06-28',
        note=(
            'role_tagged_compositional_MM_ledger_transcription_from_'
            'skunkworks_tier_ruling_2026-06-25_by_construction_saturation_'
            'label_driven_encoder_writes_category_equivalence_class_pre_fuses_'
            'heldout_with_trained_via_shared_basis_B_c_within_cat_cosine_0p894_'
            'cross_cat_0p000_HYBRID_uses_orthogonal_role_codebook_not_clustered_'
            'role_binding_machinery_neutral_lift_NOT_chain_grade_for_role_'
            'tagged_compositional_architectural_win_subsidiary_clustered_vs_'
            'ortho_direction_correct_for_USER_role_clustering_intuition_'
            'follow_up_cell_needs_label_driven_no_role_diagnostic_arm_'
            'encoder_blind_variant_and_cross_category_heldout_design'
        ),
    )
    h = append_cert_ledger_row(
        row,
        expected_cert_n_pre=630,
        expected_cert_n_post=630,
    )
    return atom_id, h


def main():
    print('=' * 72)
    print('cert_ledger atomization gap close 2026-06-28')
    print('=' * 72)

    print('\n[Gap 1] Higher_order_TOM v2 reframed honest_negative')
    aid1, h1 = write_gap_1_higher_order_tom_v2_reframed_honest_negative()
    print(f'  atom_id: {aid1}')
    print(f'  row_hash: {h1}')
    print('  cert_increment_delta: 0 (honest_negative; CERT N unchanged)')

    print('\n[Gap 2] role_tagged_compositional MM transcription')
    aid2, h2 = write_gap_2_role_tagged_compositional_mm()
    print(f'  atom_id: {aid2}')
    print(f'  row_hash: {h2}')
    print('  cert_increment_delta: 0 (MM; CERT N unchanged)')

    print('\nBOTH WRITES COMPLETE; CERT N=630 unchanged (both delta=0).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
