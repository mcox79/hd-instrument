"""
A5-gated atomize: Cell D cortex_hippo dense-Hopfield smoke HF closure
                  + M3 architecture meta-insight atom

Two atoms:
  (1) Cell D HF closure: dense-Hopfield ON TOP of Ha+Hc composition breaks mechanism
      (dense_gain=-0.740; HA_HC_DENSE=0.008 vs HA_HC=0.748). Beta=1.0 canonical
      wrong for M/N regime (META_RULE_M calibration_check=default_ok falsified).
      Revival: v2 dense-Hopfield as READOUT-REPLACEMENT (not composition).
  (2) M3 architecture meta-insight: cortex-hippo layer should REPLACE not COMPOSE
      cortex-Hebbian. Composes with prior M3 architecture atoms.

INDEPENDENT OFF-DATA VERIFICATION (skunkworks 2026-07-01):

Cell-author: ade5bb72; not pushed (no dispatch).
Smoke path: data/exp_cortex_hippo_dense_layer_M8192_v1_seed_7_smoke/metrics.json

Off-data smoke facts:
  run_mode=smoke; elapsed_s=22.4; cardinality_ok=True; verdict=HARD_FAIL
  verdict_msg: "HARD_FAIL: dense_gain=-0.740 < 0.05 -- dense layer is scenery, not
    discriminator. seed=7 STANDARD=1.000 HA_ONLY=0.002 HA_HC=0.748 HA_HC_DENSE=0.008
    dense_gain=-0.740 replay_gap=+0.746 alpha_simple=0.2500 backend=torch.cpu"
  beta_dense=1.0
  alpha_hopfield=0.0801
  alpha_simple=0.25
  hippo_sparsity=0.1
  calibration_check=default_ok_for_this_regime  <- FALSIFIED per message

Per-arm off-data (per verdict_msg + auditor recompute):
  STANDARD:      1.000 (full-pipeline positive control PASS at ceiling)
  HA_ONLY:       0.002 (Ha alone with no Hc / no dense = at floor)
  HA_HC:         0.748 (Ha + Hc composition WORKS at moderate)
  HA_HC_DENSE:   0.008 (Ha + Hc + Dense COMPOSITION BREAKS -- 0.748 -> 0.008)
  dense_gain = HA_HC_DENSE - HA_HC = 0.008 - 0.748 = -0.740 (DENSE HURTS 74pp)
  replay_gap = STANDARD - HA_HC = 1.000 - 0.748 = +0.746 (replay lifts 74.6pp)

Two substantive findings:

FINDING 1 (beta canonical wrong for M/N regime):
  Per message, dense recall climbs 0.008 -> 0.318 -> 0.723 -> 0.750 across
  beta in {1, 8, 32, 100} at composition mode. Plateaus at bipolar-readout
  ceiling ~0.75. Pre-reg calibration_check="default_ok_for_this_regime" is
  FALSIFIED per META_RULE_M (calibration-verification discipline).
  Adaptive beta ~ log(M) / cosine_margin required.

FINDING 2 (dense-Hopfield ON TOP of Ha+Hc is architecturally REDUNDANT):
  Per message + auditor concur: query = corrupted cortex readout LIMITS
  attention lookup. But dense-Hopfield as READOUT-REPLACEMENT (key -> attn ->
  val direct, bypassing Ha + Hc cortex-Hebbian) achieves recall=1.000 at
  beta >= 8. This mirrors STANDARD arm (1.000) which IS the full-pipeline
  positive control.

  M3 ARCHITECTURE INSIGHT: cortex-hippo layer should REPLACE not COMPOSE
  with cortex-Hebbian. This is load-bearing for M3 cortex-layer design.

RULING for atom (1):
  TIER: HARD_FAIL (honest_negative closure_dense_Hopfield_composition_wrong_composes_
  should_replace_not_compose_Ha_Hc). Cell-author correct honest-abort at smoke.
  cert_increment_delta = 0.

  REVIVAL CRITERIA:
    v2 dense-Hopfield as READOUT-REPLACEMENT (not composition):
      - key -> attn -> val direct
      - bypasses Ha + Hc cortex-Hebbian
      - target recall=1.000 at beta >= 8 (per smoke evidence)
      - positive control anchor: dense-replacement matches STANDARD arm
    OR: composition with regime-adapted beta (adaptive beta ~ log(M) / cosine_margin)
      - beta=1.0 canonical wrong; sweep required
      - would need calibration_check to fire honestly not default_ok

RULING for atom (2) - M3 architecture meta-insight:
  KIND: synthesis_meta_finding (per META synthesis pattern from 2026-07-01 earlier
  in day with binding-family capability invariance atom).
  Composes prior M3 architecture atoms:
    - project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28
    - project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30
  This atom adds: cortex-hippo layer should REPLACE not COMPOSE with cortex-Hebbian.
  cert_increment_delta = 0 (meta-finding not experiment; NOT full MM_STANDARD
  because rests on 1-seed smoke evidence; MM_TENTATIVE per prior synthesis convention).
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_cell_D_cortex_hippo_dense_HF_and_M3_architecture_meta_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

# ============================================================================
# ATOM 1: Cell D HF closure
# ============================================================================
atom_cell_D_HF = {
    "id": (
        "T3/EXP_substrate_cortex_hippo_dense_layer_M8192_v1_seed_7_smoke_HARD_FAIL_closure_"
        "dense_Hopfield_composition_ON_TOP_of_Ha_plus_Hc_WRONG_dense_gain_neg_0p740_"
        "HA_HC_DENSE_0p008_vs_HA_HC_0p748_composition_breaks_mechanism_74pp_loss_"
        "STANDARD_1p000_positive_control_at_ceiling_beta_1p0_canonical_wrong_META_RULE_M_falsified_"
        "revival_v2_dense_Hopfield_as_READOUT_REPLACEMENT_not_composition_2026-07-01"
    ),
    "name": (
        "HARD_FAIL closure Cell D cortex_hippo_dense_layer M=8192 smoke: dense-Hopfield "
        "composed ON TOP of Ha+Hc BREAKS the mechanism. HA_HC=0.748 -> HA_HC_DENSE=0.008 "
        "(dense_gain=-0.740, 74pp precision loss). STANDARD arm (full pipeline positive control) "
        "= 1.000. Beta=1.0 canonical WRONG for M/N=8192/? regime; META_RULE_M "
        "calibration_check=default_ok FALSIFIED (dense recall climbs 0.008->0.318->0.723->0.750 "
        "across beta {1,8,32,100}, plateaus at bipolar-readout ceiling ~0.75). Two substantive "
        "findings preserved: beta-canonical-wrong + dense-composition-architecturally-redundant. "
        "Revival: v2 dense-Hopfield as READOUT-REPLACEMENT (key->attn->val direct, bypassing "
        "Ha+Hc cortex-Hebbian) achieves recall=1.000 at beta>=8. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Cell D cortex_hippo_dense_layer M=8192 seed_7 smoke HARD_FAIL closure. Cell-author "
        "commit ade5bb72; not pushed (no dispatch). "
        "\n"
        "OFF-DATA verification: run_mode=smoke; elapsed_s=22.4; cardinality_ok=True; "
        "verdict=HARD_FAIL. Per-arm recall (verdict_msg + auditor recompute):\n"
        "  STANDARD:     1.000 (full-pipeline positive control PASS at ceiling)\n"
        "  HA_ONLY:      0.002 (Ha alone: at floor as expected)\n"
        "  HA_HC:        0.748 (Ha + Hc composition: works at moderate)\n"
        "  HA_HC_DENSE:  0.008 (Ha + Hc + Dense: COMPOSITION BREAKS; 0.748 -> 0.008)\n"
        "  dense_gain = HA_HC_DENSE - HA_HC = 0.008 - 0.748 = -0.740 (74pp loss)\n"
        "  replay_gap = STANDARD - HA_HC = 1.000 - 0.748 = +0.746\n"
        "Config: beta_dense=1.0, alpha_hopfield=0.0801, alpha_simple=0.25, hippo_sparsity=0.1.\n"
        "calibration_check=default_ok_for_this_regime (FALSIFIED per findings below).\n"
        "\n"
        "FINDING 1 (beta canonical WRONG for M/N regime):\n"
        "  Dense recall climbs 0.008 -> 0.318 -> 0.723 -> 0.750 across beta in {1, 8, 32, 100} "
        "at composition mode. Plateaus at bipolar-readout ceiling ~0.75. Pre-reg "
        "calibration_check=default_ok_for_this_regime FALSIFIED per META_RULE_M "
        "(calibration-verification discipline). Adaptive beta ~ log(M) / cosine_margin required.\n"
        "\n"
        "FINDING 2 (dense-Hopfield ON TOP of Ha+Hc is architecturally REDUNDANT):\n"
        "  Query = corrupted cortex readout LIMITS attention lookup. But dense-Hopfield as "
        "READOUT-REPLACEMENT (key -> attn -> val direct, bypassing Ha + Hc cortex-Hebbian) "
        "achieves recall=1.000 at beta >= 8. This mirrors STANDARD arm (1.000) which is "
        "the full-pipeline positive control. Load-bearing M3 architecture insight: "
        "cortex-hippo layer should REPLACE not COMPOSE with cortex-Hebbian.\n"
        "\n"
        "COMPOSES WITH: notes/research_5x_drill_cortex_hippo_M8192_rescue_2026-07-01.md.\n"
        "\n"
        "TIER: HARD_FAIL (honest_negative closure_dense_Hopfield_composition_wrong_should_replace_"
        "not_compose_Ha_Hc). Cell-author correct honest-abort at smoke; no FULL dispatch. "
        "cert_increment_delta = 0.\n"
        "\n"
        "REVIVAL CRITERIA:\n"
        "  (a) v2 dense-Hopfield as READOUT-REPLACEMENT (key -> attn -> val direct; bypasses "
        "Ha + Hc). Target: recall=1.000 at beta >= 8 (per smoke evidence). Positive control "
        "anchor: dense-replacement matches STANDARD arm.\n"
        "  OR (b) composition with regime-adapted beta (adaptive beta ~ log(M) / cosine_margin); "
        "beta=1.0 canonical wrong; sweep required; calibration_check must fire honestly not "
        "default_ok.\n"
        "\n"
        "M3 ARCHITECTURE IMPLICATION filed separately in companion synthesis meta-atom."
    ),
    "metadata": {
        "provenance_quality": "HARD_FAIL",
        "verdict": "HARD_FAIL",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA verification via .venv python on smoke metrics.json: run_mode=smoke; "
            "cardinality_ok=True; verdict=HARD_FAIL; dense_gain=-0.740 (74pp precision loss); "
            "HA_HC_DENSE=0.008 vs HA_HC=0.748 (composition breaks mechanism); STANDARD=1.000 "
            "(positive control ceiling); beta_dense=1.0 canonical; alpha_hopfield=0.0801; "
            "calibration_check=default_ok_for_this_regime FALSIFIED per beta-sweep evidence"
        ),
        "regime": {
            "M": 8192, "arms": ["STANDARD","HA_ONLY","HA_HC","HA_HC_DENSE"],
            "beta_dense_canonical": 1.0, "alpha_hopfield": 0.0801, "alpha_simple": 0.25,
            "hippo_sparsity": 0.1, "backend": "torch.cpu",
        },
        "cell_author_commit": "ade5bb72",
        "cell_not_pushed_no_dispatch": True,
        "smoke_metrics_path": "data/exp_cortex_hippo_dense_layer_M8192_v1_seed_7_smoke/metrics.json",
        "per_arm_recall": {
            "STANDARD":    1.000,
            "HA_ONLY":     0.002,
            "HA_HC":       0.748,
            "HA_HC_DENSE": 0.008,
        },
        "dense_gain_composition_mode": -0.740,
        "replay_gap": 0.746,
        "composition_breaks_mechanism_74pp_loss": True,
        "finding_1_beta_canonical_wrong_META_RULE_M_falsified": {
            "beta_sweep": [1, 8, 32, 100],
            "dense_recall_by_beta": [0.008, 0.318, 0.723, 0.750],
            "plateau_at_bipolar_readout_ceiling_075": True,
            "adaptive_beta_formula_needed": "log(M) / cosine_margin",
            "calibration_check_default_ok_falsified": True,
        },
        "finding_2_dense_composition_architecturally_redundant": {
            "root_cause": "query = corrupted cortex readout LIMITS attention lookup",
            "replacement_mode_recall_at_beta_ge_8": 1.000,
            "matches_STANDARD_arm": True,
            "M3_architecture_insight_composed_in_meta_atom": True,
        },
        "positive_control_STANDARD_pass_at_ceiling": True,
        "composes_with_5x_drill": "notes/research_5x_drill_cortex_hippo_M8192_rescue_2026-07-01.md",
        "revival_criteria": {
            "(a)_v2_dense_Hopfield_as_READOUT_REPLACEMENT": {
                "path": "key -> attn -> val direct; bypasses Ha + Hc cortex-Hebbian",
                "target_recall": "1.000 at beta >= 8",
                "positive_control_anchor": "match STANDARD arm",
            },
            "(b)_composition_with_regime_adapted_beta": {
                "adaptive_beta_formula": "log(M) / cosine_margin",
                "calibration_check_must_fire_honestly": True,
            },
        },
        "cert_increment_delta": 0,
        "discipline_tags": [
            "honest_negative_composition_breaks_mechanism_74pp_loss",
            "META_RULE_M_calibration_check_default_ok_falsified_by_beta_sweep",
            "META_RULE_AC_smoke_falsification_extends_to_HF_closure_ruling",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_at_smoke_cell_author_correct_abort",
            "M3_architecture_insight_dense_should_REPLACE_not_COMPOSE_composed_in_meta_atom",
            "composes_with_5x_drill_cortex_hippo_M8192_rescue",
            "positive_control_STANDARD_pass_at_ceiling_confirms_pipeline_healthy",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# ATOM 2: M3 architecture meta-insight
# ============================================================================
atom_M3_meta = {
    "id": (
        "T3/META_synthesis_M3_cortex_layer_architecture_INSIGHT_dense_Hopfield_should_REPLACE_not_COMPOSE_with_cortex_Hebbian_"
        "MM_TENTATIVE_single_seed_smoke_evidence_from_cell_D_HF_dense_gain_neg_0p740_at_composition_"
        "recall_1p000_at_replacement_beta_ge_8_matches_STANDARD_arm_positive_control_"
        "composes_with_M3_architecture_atoms_2026-06-28_and_stochastic_noise_2026-06-30_and_binding_family_invariance_2026-07-01_"
        "expansion_criteria_multi_seed_replication_replacement_mode_v2_cell_authoring_2026-07-01"
    ),
    "name": (
        "MM_TENTATIVE META SYNTHESIS M3 architecture insight: cortex-hippo dense-Hopfield "
        "layer should REPLACE not COMPOSE with cortex-Hebbian. Evidence base: Cell D smoke "
        "single-seed (composition mode HA_HC_DENSE=0.008 vs HA_HC=0.748 = 74pp loss; "
        "replacement mode key->attn->val direct achieves recall=1.000 at beta>=8 matching "
        "STANDARD arm). Load-bearing for M3 cortex-layer design. Composes with 3 prior M3 "
        "atoms (2026-06-28 architecture; 2026-06-30 stochastic noise at boundary; "
        "2026-07-01 binding-family capability invariance). TENTATIVE per single-seed smoke "
        "surface. Expansion criteria: multi-seed replication + replacement-mode v2 cell "
        "authoring + verify pattern holds at other M values. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "synthesis_meta_finding",
    "description": (
        "M3 ARCHITECTURE META-INSIGHT: cortex-hippo dense-Hopfield layer should REPLACE not "
        "COMPOSE with cortex-Hebbian at the readout stage. Composes with 3 prior M3 architecture "
        "atoms:\n"
        "  - project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28\n"
        "  - project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30\n"
        "  - META_synthesis_binding_family_capability_invariance_2026-07-01 (commit f878c151)\n"
        "\n"
        "EVIDENCE BASE (Cell D cortex_hippo_dense_layer smoke seed_7, commit ade5bb72):\n"
        "  Composition mode (dense-Hopfield ON TOP of Ha+Hc):\n"
        "    HA_HC_DENSE recall = 0.008 (74pp loss vs HA_HC = 0.748)\n"
        "    dense_gain = -0.740 (dense HURTS not helps in composition mode)\n"
        "    Root cause: query = corrupted cortex readout LIMITS attention lookup\n"
        "  Replacement mode (dense-Hopfield as READOUT-REPLACEMENT):\n"
        "    key -> attn -> val direct, bypassing Ha + Hc cortex-Hebbian\n"
        "    Recall = 1.000 at beta >= 8\n"
        "    Matches STANDARD arm (full-pipeline positive control at 1.000)\n"
        "\n"
        "SYNTHESIS CLAIM: In substrate WM cortex-layer design, the dense-Hopfield primitive "
        "should be positioned as a READOUT-REPLACEMENT for cortex-Hebbian, not as an "
        "additional composition layer. The Hebbian-then-dense composition creates a "
        "corrupted-readout bottleneck; direct key->attn->val bypasses this bottleneck.\n"
        "\n"
        "M3 ARCHITECTURAL IMPLICATION: When adding dense-Hopfield capabilities to the "
        "cortex layer above substrate, do NOT sequence as (Ha -> Hc -> Dense); DO position "
        "as (Ha -> Dense) OR (Dense direct). The composition pattern is architecturally "
        "REDUNDANT and empirically HARMFUL.\n"
        "\n"
        "EVIDENCE LIMITATIONS:\n"
        "  - Single-seed smoke evidence (Cell D not dispatched to 3-seed FULL)\n"
        "  - Only one M value tested (M=8192)\n"
        "  - Only Hopfield-family dense layers tested (not other dense-attention variants)\n"
        "  - Beta-adaptivity finding (log(M)/cosine_margin) is a hypothesis not verified\n"
        "\n"
        "TIER: MM_TENTATIVE_SYNTHESIS (mirrors 2026-07-01 binding-family invariance MM_TENTATIVE\n"
        "atom pattern; commit f878c151). Load-bearing insight but narrow evidence surface.\n"
        "cert_increment_delta = 0.\n"
        "\n"
        "EXPANSION CRITERIA for MM_STANDARD -> CG-eligibility:\n"
        "  (a) Multi-seed (3+) replication of replacement-mode recall=1.000 at beta>=8\n"
        "  (b) v2 replacement-mode cell authored + 3-seed FULL pass\n"
        "  (c) Pattern verified at other M values (M=4096, M=16384)\n"
        "  (a)+(b) -> MM_STANDARD; (a)+(b)+(c) -> CG-eligible with dedicated pre-reg\n"
        "\n"
        "DIRECTOR'S CALL FOR M3 DESIGN NOTE: this atom's architectural implication should "
        "propagate to any future cortex-layer cell authoring; Cell D v2 should be authored "
        "as replacement-mode not composition-mode."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM_TENTATIVE_SYNTHESIS",
        "verdict": "MEASURED_MECHANISM_TENTATIVE",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA verification via .venv python on Cell D smoke metrics.json: "
            "STANDARD=1.000 HA_HC=0.748 HA_HC_DENSE=0.008 dense_gain=-0.740; "
            "composition mode breaks mechanism 74pp; replacement mode (per cell-author message) "
            "achieves recall=1.000 at beta>=8 matching STANDARD arm; single-seed smoke evidence"
        ),
        "kind_notes": "SYNTHESIS_META_finding_composing_Cell_D_smoke_with_3_prior_M3_architecture_atoms",
        "composes_atoms": [
            {
                "atom_id_prefix": "T3/EXP_substrate_cortex_hippo_dense_layer_M8192_v1_seed_7_smoke_HARD_FAIL_closure",
                "commit_pending": "companion_atom_this_commit",
                "role": "evidence_source_composition_mode_breaks_replacement_mode_works",
            },
            {
                "topic_file": "project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28",
                "role": "M3_architecture_directive_cortex_layer_above_substrate",
            },
            {
                "topic_file": "project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30",
                "role": "M3_cortex_stochastic_noise_at_boundary_requirement",
            },
            {
                "atom_id_prefix": "T3/META_synthesis_binding_family_capability_invariance_capacity_axis_at_WM_regime",
                "commit": "f878c151",
                "role": "prior_MM_TENTATIVE_synthesis_pattern_reference",
            },
        ],
        "synthesis_claim": (
            "Dense-Hopfield primitive should be positioned as READOUT-REPLACEMENT for "
            "cortex-Hebbian, not as an additional composition layer. Hebbian-then-dense "
            "composition creates corrupted-readout bottleneck; direct key->attn->val "
            "bypasses this bottleneck."
        ),
        "M3_architectural_implication": (
            "When adding dense-Hopfield capabilities to cortex layer above substrate, do "
            "NOT sequence as (Ha -> Hc -> Dense); DO position as (Ha -> Dense) OR "
            "(Dense direct). Composition pattern architecturally REDUNDANT and empirically HARMFUL."
        ),
        "evidence_composition_mode_breaks": {
            "HA_HC_recall": 0.748,
            "HA_HC_DENSE_recall": 0.008,
            "dense_gain": -0.740,
            "loss_pp": 74,
            "root_cause": "query = corrupted cortex readout LIMITS attention lookup",
        },
        "evidence_replacement_mode_works": {
            "path": "key -> attn -> val direct; bypasses Ha + Hc",
            "recall_at_beta_ge_8": 1.000,
            "matches_STANDARD_arm_at_1p000": True,
        },
        "evidence_limitations": {
            "single_seed_smoke_only_Cell_D_not_dispatched_to_3_seed_FULL": True,
            "only_one_M_value_tested": "M=8192",
            "only_Hopfield_family_dense_tested": True,
            "beta_adaptivity_hypothesis_not_verified": "log(M) / cosine_margin",
        },
        "expansion_criteria_for_MM_STANDARD_and_CG_eligibility": {
            "(a)_multi_seed_3plus_replication_of_replacement_mode": "recall=1.000 at beta>=8",
            "(b)_v2_replacement_mode_cell_authored_3_seed_FULL_pass": True,
            "(c)_pattern_verified_at_other_M_values": ["M=4096","M=16384"],
            "a_plus_b_elevates_MM_TENTATIVE_to_MM_STANDARD": True,
            "a_plus_b_plus_c_enables_CG_eligibility_with_dedicated_prereg": True,
        },
        "director_note_M3_design_propagation": (
            "This atom's architectural implication should propagate to any future "
            "cortex-layer cell authoring; Cell D v2 should be authored as replacement-mode "
            "not composition-mode."
        ),
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_synthesis_composes_Cell_D_smoke_with_3_prior_M3_architecture_atoms",
            "MM_TENTATIVE_single_seed_narrow_surface_expansion_criteria_specified",
            "M3_architecture_insight_dense_Hopfield_REPLACE_not_COMPOSE_cortex_Hebbian",
            "director_note_propagate_to_future_cortex_layer_cell_authoring",
            "composes_with_binding_family_invariance_MM_TENTATIVE_synthesis_pattern_f878c151",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================================
# CERT LEDGER ROWS
# ============================================================================
_t0 = time.time()

ledger_cell_D_HF = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_cell_D_HF['id']}",
    "cert_status": "hard_fail",
    "cert_class": "honest_negative_dense_Hopfield_composition_wrong_should_replace_not_compose_Ha_Hc",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": "ade5bb72_not_pushed",
    "verdict": (
        "HARD_FAIL_smoke_seed_7_composition_breaks_mechanism_74pp_HA_HC_DENSE_0p008_vs_HA_HC_0p748_"
        "dense_gain_neg_0p740_STANDARD_1p000_positive_control_at_ceiling_"
        "beta_1p0_canonical_WRONG_META_RULE_M_calibration_check_default_ok_FALSIFIED_"
        "dense_recall_climbs_0p008_0p318_0p723_0p750_across_beta_1_8_32_100_plateaus_at_bipolar_readout_ceiling_"
        "revival_v2_dense_as_READOUT_REPLACEMENT_key_attn_val_direct_bypasses_Ha_Hc_recall_1p000_at_beta_ge_8_matches_STANDARD_"
        "M3_architecture_insight_composed_in_companion_meta_atom_this_commit"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": "notes/research_5x_drill_cortex_hippo_M8192_rescue_2026-07-01.md",
        "metrics_path": "data/exp_cortex_hippo_dense_layer_M8192_v1_seed_7_smoke/metrics.json",
        "cell_author_commit_not_pushed": "ade5bb72",
        "companion_M3_meta_atom": f"math::{atom_M3_meta['id']}",
        "atom_qualified_id": f"math::{atom_cell_D_HF['id']}",
    },
    "supersedes": None,
    "note": (
        "Cell_D_cortex_hippo_dense_layer_M8192_smoke_HF_closure_composition_breaks_mechanism_74pp_loss_"
        "HA_HC_0p748_to_HA_HC_DENSE_0p008_dense_gain_neg_0p740_STANDARD_1p000_positive_control_at_ceiling_"
        "beta_1p0_canonical_wrong_META_RULE_M_calibration_check_default_ok_falsified_beta_sweep_0p008_0p318_0p723_0p750_"
        "revival_v2_dense_as_READOUT_REPLACEMENT_key_attn_val_direct_recall_1p000_at_beta_ge_8_matches_STANDARD_"
        "composes_with_5x_drill_cortex_hippo_M8192_rescue_M3_architecture_insight_composed_in_companion_meta_atom"
    ),
}

ledger_M3_meta = {
    "ts": _t0 + 0.001,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_M3_meta['id']}",
    "cert_status": "measured_mechanism_tentative",
    "cert_class": "synthesis_meta_finding_M3_architecture_dense_Hopfield_REPLACE_not_COMPOSE",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_TENTATIVE_SYNTHESIS_M3_architecture_insight_dense_Hopfield_should_REPLACE_not_COMPOSE_cortex_Hebbian_"
        "single_seed_smoke_evidence_composition_HA_HC_DENSE_0p008_vs_HA_HC_0p748_dense_gain_neg_0p740_"
        "replacement_key_attn_val_direct_recall_1p000_at_beta_ge_8_matches_STANDARD_"
        "composes_with_3_prior_M3_atoms_architecture_2026-06-28_stochastic_noise_2026-06-30_binding_family_invariance_2026-07-01_"
        "expansion_criteria_multi_seed_replication_replacement_v2_cell_multi_M"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": "notes/research_5x_drill_cortex_hippo_M8192_rescue_2026-07-01.md",
        "companion_HF_atom": f"math::{atom_cell_D_HF['id']}",
        "composes_prior_M3_atoms": [
            "project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28",
            "project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30",
            "META_synthesis_binding_family_capability_invariance_2026-07-01_commit_f878c151",
        ],
        "atom_qualified_id": f"math::{atom_M3_meta['id']}",
    },
    "supersedes": None,
    "note": (
        "M3_architecture_meta_insight_dense_Hopfield_should_REPLACE_not_COMPOSE_cortex_Hebbian_"
        "MM_TENTATIVE_single_seed_smoke_from_Cell_D_HF_composition_mode_breaks_replacement_mode_works_"
        "composes_with_binding_family_invariance_MM_TENTATIVE_synthesis_pattern_f878c151_"
        "expansion_criteria_a_multi_seed_replication_b_replacement_v2_cell_c_multi_M_values_"
        "director_note_propagate_to_future_cortex_layer_cell_authoring_v2_replacement_not_composition"
    ),
}


# ============================================================================
# A5 write protocol
# ============================================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists()

    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row: assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row: assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text); f.flush(); os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try: os.replace(str(tmp_path), str(path)); break
        except PermissionError:
            if _attempt == 9: raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row: assert tail["id"] == new_row["id"]
    if "atom_id" in new_row: assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_cell_D_HF,          "math/atoms (Cell D cortex_hippo_dense HF)")
    append_jsonl_a5(MATH_ATOMS, atom_M3_meta,            "math/atoms (M3 architecture meta-insight MM_TENTATIVE)")
    append_jsonl_a5(CERT_LEDGER, ledger_cell_D_HF,       "cert_ledger (Cell D HF)")
    append_jsonl_a5(CERT_LEDGER, ledger_M3_meta,         "cert_ledger (M3 meta MM_TENTATIVE)")
    print(f"[A5] DONE OK")
    print(f"[A5] Cell D cortex_hippo_dense_layer: HARD_FAIL (composition breaks mechanism 74pp)")
    print(f"[A5] M3 architecture meta-insight: MM_TENTATIVE (dense should REPLACE not COMPOSE)")
    print(f"[A5] CERT delta = 0 for both")


if __name__ == "__main__":
    main()
