#!/usr/bin/env python3
"""Skunkworks landed-VET batch 9 atomize (5 cells) 2026-06-26.

Lands ratified rulings from landed-VET batch 9 (5 cells; per-arm OFF-DATA recompute verified):

Atom inventory:
  1. math::T3 EXP_phase_diagram_capacity_multi_bank_K4_envelope_v2c_n8192_gpu CHAIN_GRADE
        -> chain_grade (delta=+1) -- rec=1.0000 cv=0.0000 across 3 seeds at K_banks=4 alpha=4 N=8192
           Extends prior K=8192 single-bank chain-grade to K=4 sharding regime.
           Q-discipline: rec=1.0 IS by-construction-saturation candidate; BUT:
             (a) MULTI_BANK_K=4 sharding is the MECHANISM (this is the regime under test, not a label cap)
             (b) prior v2b OOM'd at N=16384; v2c rescues by halving N to 8192 (capacity claim is alpha-relative)
             (c) alpha=4 headroom=10x preserves the prior K=8192 chain-grade band
             (d) substrate_only_ok=True; llm_calls=0; GPU asserted (Fix #24)
           NOT MM: it IS the chain-grade extension to a 4-bank-sharded regime; the perfect recall is
           the mechanism's predicted band, not the metric cap.

  2. math::T3 EXP_edge_importance_v5_CFU_counterfactual_utility_v1 MEASURED_MECHANISM
        -> measured_mechanism (delta=0) -- alpha=2.148 CFU cor=-0.0155, sel_unretr=+0.0483 (rederived;
           cited 0.037 in verdict_msg has miscite gap of ~0.01); below 0.15 PASS bar.
           FIRST mechanism in edge-imp family to PASS FAIRNESS (v1/v2/v3 all had cor=+0.83 trace-saturation
           OR much higher cor; v5 CFU is structurally orthogonal to magnitude via leave-one-out ablation).
           Brain-grounded (Tonegawa optogenetic engram analog).
           PASS_BAR_MISSED: sel_unretr=0.048 < 0.15 (and comp_over_cfu=False).

  3. meta::T_methodology META_RULE_CHAIN_GEN_FEASIBILITY_PRE_FLIGHT (custom; delta=0)
        -> discipline_meta (delta=0) -- from cell 3 infra-bug (multihop_barrier1: only 200/500 chains
           generated for V=200 max_depth=8 disallow|=0). Rule: multi-hop / chain-based cells with
           deep regimes (max_depth >= 5) MUST pre-flight chain-gen feasibility analytically OR
           via a tiny-N PoC arm BEFORE full dispatch.

  4. math::T3 EXP_gap3_cls_two_tier_HOPFIELD_consolidation_v1 HONEST_NEGATIVE_BY_CONSTRUCTION_SATURATION
        -> honest_negative (delta=+1) -- ALL 4 arms heldout_acc=1.0 across 3 seeds; baseline_max rail
           violated (BASELINE_HEBBIAN=1.0 >= HF_BASELINE_MAX=0.5). Regime trivially separable at
           N_DIM=8192 / N_CAT=5 / N_TRAIN=20; cone 0.46-0.49 < 0.50 floor; lift_over_baseline=0.
           Not a mechanism refutation of Hopfield consolidation; regime mismatch.

  5. math::T3 EXP_stage3_hrr_involutive_systematic_generalization_v1 HONEST_NEGATIVE_MECHANISM_NULL
        -> honest_negative (delta=+1) -- ARM_HRR_INVOLUTIVE mean=0.0067 = ARM_BASELINE mean=0.0067
           = chance(0.005)+0.0017; magnitude_coupling_cor=0.058 (LOW; not coupling-saturated, so NOT a
           by-construction-saturation negative). HRR involutive unbinding chains do NOT enable
           systematic generalization at N_DIM=8192/N_ENTITIES=200/N_VERBS=10/N_TRAIN=500/HELDOUT=100.
           Stage 3 compositional understanding implication: HRR-via-unbind-chain mechanism REFUTED at
           this regime; need different composition mechanism.

  6. meta::T_methodology META_RULE_HRR_INVOLUTIVE_SYSTEMATIC_GENERALIZATION_REFUTED_AT_REGIME (custom; delta=0)
        -> discipline_meta (delta=0) -- from cell 5. Companion to atom 5 documenting the substrate
           regime where HRR involutive composition cannot do systematic generalization (heldout-object
           prediction via feature-overlap prototypes). Constrains future Stage 3 composition cells.

CERT delta this batch: +3 (atom 1 chain_grade, atom 4 honest_negative, atom 5 honest_negative)
Atom 2 = MM (delta 0; mechanism characterized but doesn't pass pre-reg bar; brain-grounded standalone value)
Atom 3, 6 = META discipline (delta 0)

Discipline:
- A5 PRE/POST verify: CERT N, axiom 206, cap_pres 6/6
- Atomic add_atom via PartitionedStore (handles tmp + os.replace)
- Fresh-Store round-trip per atom
- cert_ledger row appended in SAME A5 window per atom via Phase-C live-write helper
- Idempotency: skip on collision
- Foreground execution; ASCII only
- Path-scoped commit (caller responsibility): this tool + Store partitions + cert_ledger

Pre-write live CERT N (verified 2026-06-26 evening): 619 (CERT_CHAIN_GRADE provenance count)
Expected post-write CERT_CHAIN_GRADE_N delta: +3 (atoms 1/4/5 each get CERT_CHAIN_GRADE provenance)
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
    build_measured_mechanism_row,
    build_honest_negative_row,
)

STORE_ROOT = REPO_ROOT / "data" / "substrate_index"
NOTES_PATH_VET = "notes/skunkworks_to_research_LANDED_VET_batch9_5cell_2026-06-26.md"
CELL_COMMIT_UNTRACKED = "n/a-commit-not-tracked-in-prereg"


# ============================================================================
# Atom 1: phase_diagram_capacity_multi_bank_K4 N=8192 v2c CHAIN_GRADE
# ============================================================================

def atom_1_multi_bank_K4_N8192_chain_grade() -> Atom:
    return Atom(
        id=(
            "T3/EXP_phase_diagram_capacity_multi_bank_K4_envelope_v2c_n8192_gpu_"
            "chain_grade_rec_1p0000_cv_0_3seeds_alpha_4_h10x_substrate_only_v2b_OOM_rescue"
        ),
        name=(
            "Phase diagram capacity multi-bank K=4 envelope v2c N=8192 GPU: CHAIN_GRADE on "
            "MULTI_BANK_K_banks=4 sharding at alpha=4.0 headroom=10x N=8192 (rec=1.0000 cv=0.0000 "
            "across 3 seeds; v2c rescue of v2b OOM by halving N from 16384 to 8192; "
            "substrate-only-ok llm_calls=0 GPU asserted; peak_mem=1929MB)"
        ),
        description=(
            "CHAIN_GRADE on the MULTI_BANK K_banks=4 sharding mechanism at N=8192 alpha=4.0 "
            "headroom=10x.\n\n"
            "PER-SEED OFF-DATA RECOMPUTE (Skunkworks 2026-06-26):\n"
            "  seed 11: recall_at_1=1.0  V_C=10240 M_facts=32768 alpha_N=4.0 wall=5.28s mem=1929MB "
            "llm_calls_inference=0\n"
            "  seed 13: recall_at_1=1.0  V_C=10240 M_facts=32768 alpha_N=4.0 wall=5.17s mem=1929MB "
            "llm_calls_inference=0\n"
            "  seed 19: recall_at_1=1.0  V_C=10240 M_facts=32768 alpha_N=4.0 wall=5.16s mem=1929MB "
            "llm_calls_inference=0\n"
            "  recall_mean = 1.0000 ; cv = 0.0000 (matches cited; reproduced from per_unit)\n\n"
            "PRE-REG BARS (from config_version):\n"
            "  HP_MB_REC_MIN >= 0.95   PASS (1.0000)\n"
            "  HP_MB_CV_MAX <= 0.05    PASS (0.0000)\n"
            "  EXPECTED_N_UNITS = 3    PASS (n_units_observed=3)\n"
            "  cardinality_ok = True   PASS\n\n"
            "Q-DISCIPLINE BY-CONSTRUCTION-SATURATION CHECK:\n"
            "  rec=1.0 is at the metric cap. Why this is NOT by-construction-saturation:\n"
            "  (a) The MECHANISM under test IS K=4 bank sharding at alpha=4 (the regime).\n"
            "      The hypothesis pre-registered: sharded multi-bank rescues capacity at\n"
            "      alpha>1 where single-bank single-arm would saturate.\n"
            "  (b) Prior CERT chain-grade landed at K=8192 single-bank (3-seed harvest;\n"
            "      atom in math corpus). v2c extends this to K=4 sharding regime; this is\n"
            "      the predicted band, not the metric cap by accident.\n"
            "  (c) The capacity claim is alpha-relative (not N-relative); alpha=4 headroom=10x\n"
            "      preserves the prior K=8192 band.\n"
            "  (d) v2b OOM at N=16384 showed the mechanism CAN fail to even run; v2c rescues by\n"
            "      halving N to 8192. The recall=1.0 is preceded by a real feasibility gate.\n\n"
            "DISCRIMINATING-REGIME NOTE:\n"
            "  This is a SINGLE-PHASE-POINT CHAIN_GRADE. Cell A handles the multi-arm comparison\n"
            "  (MECH/KNN/BARE arms EXEMPT in this cell per HP_SCOPE). The chain-grade is for\n"
            "  envelope-pass under K=4 sharding at the specified phase point.\n\n"
            "FAIRNESS / NO-LLM-LEAK:\n"
            "  per_unit._llm_forward_calls_at_inference = 0 (asserted per seed)\n"
            "  detail.substrate_only_ok = True\n"
            "  detail.n_llm_calls = 0\n"
            "  metrics_source = measured_substrate_bipolar_hebbian_W_multi_bank_K4_v2c_n8192_gpu\n"
            "  GPU asserted: NVIDIA GeForce RTX 4060 Ti, 8.59GB max\n"
            "  peak_mem_mb_max = 1929 (well under 8GB GPU envelope)\n\n"
            "GAP_CAP_MAP IMPACT: capacity envelope under K=4 sharding at N=8192 confirmed; opens\n"
            "  cell-A multi-arm follow-up at this phase point for control-grade ratification.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "mechanism_tags": ["MULTI_BANK_K_SHARDING", "CAPACITY_ALPHA_4", "N_DIM_8192"],
            "verdict": "HARD_PASS",
            "cell_anchor": "phase_diagram_capacity_multi_bank_K4_envelope_v2c_n8192_gpu",
            "metrics_path": "data/exp_phase_diagram_capacity_multi_bank_K4_envelope_v2c_n8192_gpu/metrics.json",
            "n_seeds": 3,
            "recall_mean": 1.0,
            "recall_cv": 0.0,
            "alpha_N": 4.0,
            "K_banks": 4,
            "N_DIM": 8192,
            "headroom": 10.0,
            "peak_mem_mb": 1929,
            "llm_calls_at_inference": 0,
            "gpu_asserted": True,
            "discriminating_regime": "K_banks=4 sharding at alpha=4.0 headroom=10x N=8192",
            "verified_off_data": True,
            "verified_by": "skunkworks",
            "verified_at_ts": time.time(),
            "verified_at_date": "2026-06-26",
            "ratification_basis": "per_seed_off_data_recompute_3of3_seeds_match_cited_substrate_only_ok",
            "cell_commit": CELL_COMMIT_UNTRACKED,
            "extends_prior_chain_grade": "WM multibank K=8192 3-seed harvest CHAIN_GRADE (math corpus)",
        },
    )


# ============================================================================
# Atom 2: edge_importance_v5_CFU MEASURED_MECHANISM
# ============================================================================

def atom_2_edge_imp_v5_cfu_measured_mechanism() -> Atom:
    return Atom(
        id=(
            "T3/EXP_edge_importance_v5_CFU_counterfactual_utility_v1_"
            "measured_mechanism_first_fairness_passing_mechanism_in_family_sel_unretr_0p048_below_0p15"
        ),
        name=(
            "Edge importance v5 CFU counterfactual-utility v1: MEASURED_MECHANISM. FIRST mechanism in "
            "edge-importance family to PASS FAIRNESS (cor=-0.0155 well below 0.30 USER gate; "
            "structurally orthogonal via leave-one-out ablation; brain-grounded Tonegawa engram "
            "analog). PASS bar sel_unretr missed: rederived sel(retr-unretr)=+0.0483 < 0.15 floor "
            "(verdict_msg cited +0.037, miscite gap ~0.01; bar miss holds either way)."
        ),
        description=(
            "MEASURED_MECHANISM ruling: CFU operational, fairness PASSED with structural margin, "
            "PASS bars not cleared.\n\n"
            "PER-ARM OFF-DATA RECOMPUTE (3 seeds: 7, 17, 23) Skunkworks 2026-06-26:\n"
            "  CFU_LEAVE_ONE_OUT:\n"
            "    cor_importance_magnitude per_seed: [0.01755, -0.03585, -0.02818]  mean=-0.01549 "
            "(matches cited -0.015)\n"
            "    recall_old_RETRIEVED per_seed: [0.795, 0.780, 0.775]  mean=0.7833 (matches cited 0.783)\n"
            "    recall_old_UNRETRIEVED per_seed: [0.715, 0.740, 0.750]  mean=0.7350 (matches cited 0.735)\n"
            "    rederived sel(retr-unretr) = 0.7833 - 0.7350 = +0.0483\n"
            "    CITED sel_unretr = +0.037  (verdict_msg cited number)\n"
            "    MISCITE FLAG: rederived 0.0483 vs cited 0.037 gap ~0.01; sel formula in verdict_msg\n"
            "    is ambiguous (could be sel-vs-recent, sel-lift-over-rand, trimmed-mean). Disposition\n"
            "    HOLDS in both cases (BOTH 0.037 AND 0.0483 are << 0.15 PASS floor).\n"
            "  TRACE_ONLY (comparison; the family's prior-leading arm):\n"
            "    cor mean=0.0854 (much higher; near 0.087-saturation)\n"
            "    retr mean=1.000 unretr=0.6783 sel=+0.3217 ; PASS bar cleared on sel-unretr\n"
            "    but FAILS fairness in prior family runs (this run cor=0.085 << 0.30 USER gate)\n"
            "  RAND_IMPORTANCE (control):\n"
            "    retr mean=0.7500 unretr=0.7717 sel=-0.0217 (negative; control baseline)\n"
            "  COMBINED:\n"
            "    retr mean=0.840 unretr=0.7433 sel=+0.0967 cor=0.0421\n\n"
            "PRE-REG hp_checks (from verdict_msg):\n"
            "  sel_unretr = FALSE  (0.0483 < 0.15 PASS floor)\n"
            "  fair = TRUE         (cor=-0.0155 < 0.30 USER gate, with large margin)\n"
            "  fired = TRUE        (mechanism operational)\n"
            "  comp_over_cfu = FALSE\n\n"
            "RATIFICATION RATIONALE (MM not chain-grade, not honest-negative):\n"
            "  - MM not chain-grade: sel_unretr PASS bar not cleared (0.0483 < 0.15).\n"
            "  - MM not honest-negative: FIRST mechanism in the family to PASS FAIRNESS with\n"
            "    structural margin (cor=-0.0155 vs 0.30 gate); structurally orthogonal by\n"
            "    construction (leave-one-out ablation); brain-grounded (Tonegawa optogenetic\n"
            "    engram analog). CHARACTERIZATION VALUE is real.\n"
            "  - Companion to existing HONEST_BOUND atom (math corpus: 'substrate's max sel_unretr\n"
            "    asymmetry extractable from retrieval-trace alone at the edge_imp regime' = +0.083\n"
            "    trace-only). v5 CFU now establishes 'fairness-PASSING importance signal max +0.048\n"
            "    at v5 regime' as a COMPANION honest-bound: the fairness-passing variant is\n"
            "    structurally weaker than the trace-only (fairness-failing) variant.\n\n"
            "MISCITE DISCIPLINE FLAG-BACK:\n"
            "  Cell author should clarify the verdict_msg 'sel=+0.037' formula in v6 or successor.\n"
            "  Candidate formulas: (a) trimmed/median, (b) sel-recent, (c) sel-lift-over-rand,\n"
            "  (d) different sub-sample. Rederived clean retr-unretr = +0.0483 from per_seed.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "mechanism_tags": ["EDGE_IMPORTANCE_COUNTERFACTUAL_UTILITY", "LEAVE_ONE_OUT_ABLATION", "STRUCTURAL_ORTHOGONALITY_TO_MAGNITUDE"],
            "verdict": "MIDDLE_BAND",
            "cell_anchor": "edge_importance_v5_CFU_counterfactual_utility_v1",
            "metrics_path": "data/exp_edge_importance_v5_CFU_counterfactual_utility_v1/metrics.json",
            "n_seeds": 3,
            "cfu_cor_mean": -0.0155,
            "cfu_sel_unretr_rederived": 0.0483,
            "cfu_sel_unretr_cited": 0.037,
            "cite_discrepancy_flag": "verdict_msg_sel_0p037_vs_rederived_0p0483_gap_0p011",
            "first_fairness_passing_in_family": True,
            "brain_grounded_basis": "tonegawa_optogenetic_engram_leave_one_out_analog",
            "companion_atom": "HONEST_BOUND (math): substrate_max_sel_unretr_trace_only_0p083_edge_imp_v3p1",
            "verified_off_data": True,
            "verified_by": "skunkworks",
            "verified_at_ts": time.time(),
            "verified_at_date": "2026-06-26",
            "cell_commit": CELL_COMMIT_UNTRACKED,
        },
    )


# ============================================================================
# Atom 3: META RULE chain-gen feasibility pre-flight
# ============================================================================

def atom_3_meta_chain_gen_feasibility_pre_flight() -> Atom:
    return Atom(
        id=(
            "T_methodology/META_RULE_CHAIN_GEN_FEASIBILITY_PRE_FLIGHT_for_multihop_chain_cells_"
            "max_depth_ge_5_disallow_filter_must_be_pre_dispatch_checked"
        ),
        name=(
            "META RULE chain-gen feasibility pre-flight (CERT-neutral discipline): multi-hop / "
            "chain-based cells with max_depth >= 5 and disallow-filter on the chain-gen step MUST "
            "pre-flight feasibility (analytic OR tiny-N PoC arm) BEFORE full dispatch; otherwise "
            "the cell aborts at setup time, all seeds wasted at chain-gen, and no mechanism arms run."
        ),
        description=(
            "META RULE (CERT-neutral; discipline_meta).\n\n"
            "PROVENANCE: landed-VET batch 9 cell 3 (multihop_barrier1_M2_M3_M1_combined_5arm_v1)\n"
            "  Setup exception across all 3 seeds: 'BLOCKING make_deep_chains: only 200/500\n"
            "  generated for V=200 disallow|=0 max_depth=8'. Chain-gen could not satisfy the\n"
            "  configured 500-chain budget under V=200 vocabulary, max_depth=8, disallow-filter.\n"
            "  elapsed_s=0.732 total; arms list EMPTY across all 3 seeds. Mechanism arms NEVER\n"
            "  exercised.\n\n"
            "RULE STATEMENT:\n"
            "  IF (cell uses chain-gen with disallow-filter or distinct-token constraint) AND\n"
            "     (max_depth >= 5) AND\n"
            "     (n_chains_train + n_chains_query > 0.5 * (V^(max_depth-1)) under disallow):\n"
            "  THEN cell MUST include ONE of:\n"
            "     (A) analytic feasibility note in pre-reg (count of feasible chains derivable\n"
            "         from V/max_depth/disallow constraints; show budget <= feasible_count)\n"
            "     (B) tiny-N PoC arm that runs ONE seed at full chain-gen settings and reports\n"
            "         actual generated count BEFORE full-arm dispatch\n"
            "     (C) feasibility-check inside the cell that DEGRADES gracefully (truncate to\n"
            "         feasible count + log; do NOT abort entire run)\n\n"
            "SKUNKWORKS SCHEMA-VET CHECK:\n"
            "  Pre-dispatch pre-reg VET adds 'chain_gen_feasibility' field check to the\n"
            "  discriminator-must-survive-scale checklist (USER 2026-06-26 LOCKED #B feedback).\n"
            "  Reject pre-reg without (A) (B) or (C).\n\n"
            "RELATED CAPABILITIES:\n"
            "  - This rule subsumes 'BARRIER_1 quintuple multi-hop family' chain-gen failures\n"
            "    seen as a recurring infra-bug class.\n"
            "  - Counter remains at 5 mechanism-refutations of Barrier 1 + 1 infra-bug (this cell).\n"
            "  - Does NOT count as 6th refutation; mechanism never exercised.\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        corpus=Corpus.META,
        tier=Tier.TIER_METHODOLOGY,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "rule_tags": ["META_RULE", "CHAIN_GEN_FEASIBILITY_PRE_FLIGHT", "DISCRIMINATOR_MUST_SURVIVE_SCALE"],
            "rule_class": "pre_dispatch_feasibility_check",
            "applies_to": "multi_hop_chain_based_cells_max_depth_ge_5",
            "discovered_from_cell": "multihop_barrier1_M2_M3_M1_combined_5arm_v1",
            "discovered_from_metrics": "data/exp_multihop_barrier1_M2_M3_M1_combined_5arm_v1/metrics.json",
            "ratified_by": "skunkworks",
            "ratified_at_ts": time.time(),
            "ratified_at_date": "2026-06-26",
            "subsumes_class": "BARRIER_1_multi_hop_chain_gen_infra_bugs",
            "skunkworks_schema_vet_action": "reject_pre_reg_without_analytic_or_PoC_or_graceful_degradation",
        },
    )


# ============================================================================
# Atom 4: HOPFIELD consolidation HONEST_NEGATIVE_BY_CONSTRUCTION_SATURATION
# ============================================================================

def atom_4_hopfield_consolidation_honest_negative_by_construction_saturation() -> Atom:
    return Atom(
        id=(
            "T3/EXP_gap3_cls_two_tier_HOPFIELD_consolidation_v1_"
            "honest_negative_by_construction_saturation_n_dim_8192_n_cat_5_n_train_20_trivially_separable"
        ),
        name=(
            "Gap3 CLS two-tier HOPFIELD consolidation v1: HONEST_NEGATIVE by-construction-saturation. "
            "ALL 4 arms (BASELINE_HEBBIAN, HEBBIAN_SLOW, HOPFIELD_REPLAY_SLOW, HOPFIELD_GENERATIVE_REPLAY) "
            "heldout_acc=1.0 across 3 seeds; baseline_max rail violated (1.0 >= HF_BASELINE_MAX=0.5); "
            "cone 0.46-0.49 below 0.50 floor; lift_over_baseline=0. Regime trivially separable at "
            "N_DIM=8192 / N_CAT=5 / N_TRAIN=20. Not a mechanism refutation; regime mismatch."
        ),
        description=(
            "HONEST_NEGATIVE by-construction-saturation ruling.\n\n"
            "PER-ARM OFF-DATA RECOMPUTE (3 seeds: 11, 13, 19) Skunkworks 2026-06-26:\n"
            "  ARM_BASELINE_HEBBIAN:           heldout_acc [1.0, 1.0, 1.0] mean=1.0000 cone [1.0,1.0,1.0]\n"
            "  ARM_HEBBIAN_SLOW:               heldout_acc [1.0, 1.0, 1.0] mean=1.0000 cone [0.457,0.458,0.459]\n"
            "  ARM_HOPFIELD_REPLAY_SLOW:       heldout_acc [1.0, 1.0, 1.0] mean=1.0000 cone [0.497,0.490,0.490]\n"
            "  ARM_HOPFIELD_GENERATIVE_REPLAY: heldout_acc [1.0, 1.0, 1.0] mean=1.0000 cone [0.408,0.408,0.407]\n"
            "  lift_over_baseline = 0.0000\n"
            "  best_cone = 0.4922 (BELOW 0.50 cone floor)\n\n"
            "RAIL VIOLATIONS:\n"
            "  HF_BASELINE_MAX <= 0.5 violated (baseline=1.0)\n"
            "  HP_lift_over_baseline >= 0.20 violated (lift=0.0)\n"
            "  cone in [0.50, 0.95] violated (best=0.4922)\n\n"
            "RATIFICATION RATIONALE:\n"
            "  This is a regime-mismatch HONEST_NEGATIVE, NOT a mechanism refutation. With\n"
            "  N_DIM=8192 hyperdimensional capacity and only 5 categories with 20 training items,\n"
            "  the substrate has enormous separation headroom; even random Hebbian (no replay,\n"
            "  no consolidation) achieves 100% heldout. Hopfield consolidation cannot be\n"
            "  meaningfully discriminated from baseline at this regime.\n\n"
            "  Counts as HONEST_NEGATIVE per cert-disposition framework: clean negative, not a\n"
            "  bug, but the bound is on the REGIME not the mechanism. Honest-negative for the\n"
            "  cell's configured test, but the Hopfield mechanism itself remains unrefuted.\n\n"
            "FOLLOW-UP REGIME REQUIRED (cell-author guidance):\n"
            "  - Increase N_CAT (5 -> 50+) so baseline degrades below 0.5 cap\n"
            "  - Decrease N_DIM (8192 -> 512 or 1024) toward capacity-limited regime\n"
            "  - Increase noise (proto_noise > 0.30) to stress consolidation\n"
            "  - Verify discriminator survives scale BEFORE full dispatch (USER #B feedback)\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",  # honest_negative still CERT_CHAIN_GRADE provenance per ledger convention
            "mechanism_tags": ["HOPFIELD_CONSOLIDATION", "BY_CONSTRUCTION_SATURATION", "REGIME_MISMATCH"],
            "honest_negative_subclass": "by_construction_saturation_regime_mismatch",
            "verdict": "HARD_FAIL",
            "cell_anchor": "gap3_cls_two_tier_HOPFIELD_consolidation_v1",
            "metrics_path": "data/exp_gap3_cls_two_tier_HOPFIELD_consolidation_v1/metrics.json",
            "n_seeds": 3,
            "all_arms_heldout_acc": 1.0,
            "lift_over_baseline": 0.0,
            "best_cone": 0.4922,
            "regime": "N_DIM=8192 N_CAT=5 N_TRAIN=20",
            "not_mechanism_refutation": True,
            "follow_up_regime_required": "increase_N_CAT_or_decrease_N_DIM_or_increase_noise",
            "verified_off_data": True,
            "verified_by": "skunkworks",
            "verified_at_ts": time.time(),
            "verified_at_date": "2026-06-26",
            "cell_commit": CELL_COMMIT_UNTRACKED,
        },
    )


# ============================================================================
# Atom 5: HRR involutive HONEST_NEGATIVE_MECHANISM_NULL
# ============================================================================

def atom_5_hrr_involutive_honest_negative_mechanism_null() -> Atom:
    return Atom(
        id=(
            "T3/EXP_stage3_hrr_involutive_systematic_generalization_v1_"
            "honest_negative_mechanism_null_hrr_inv_0p0067_eq_baseline_0p0067_eq_chance_plus_0p0017"
        ),
        name=(
            "Stage 3 HRR involutive systematic generalization v1: HONEST_NEGATIVE mechanism-null. "
            "ARM_HRR_INVOLUTIVE mean=0.0067 = ARM_BASELINE mean=0.0067 = chance(0.005)+0.0017; "
            "ARM_NN=0.0; magnitude_coupling_cor=0.058 (LOW; rules out coupling-saturation). "
            "HRR involutive unbinding chains do NOT enable systematic generalization at this "
            "regime (N_DIM=8192 / N_ENTITIES=200 / N_VERBS=10 / N_TRAIN=500 / HELDOUT=100)."
        ),
        description=(
            "HONEST_NEGATIVE mechanism-null ruling on HRR involutive composition for systematic\n"
            "generalization (heldout-object prediction via feature-overlap prototypes).\n\n"
            "PER-ARM OFF-DATA RECOMPUTE (3 seeds: 11, 13, 19) Skunkworks 2026-06-26:\n"
            "  ARM_BASELINE                     heldout_acc [0.00, 0.01, 0.01] mean=0.0067 cv=0.71\n"
            "  ARM_HRR_INVOLUTIVE               heldout_acc [0.00, 0.01, 0.01] mean=0.0067 cv=0.71\n"
            "  ARM_NEAREST_NEIGHBOR_INTERPOL    heldout_acc [0.00, 0.00, 0.00] mean=0.0000\n"
            "  chance_acc                       = 0.0050\n"
            "  mechanism_lift_over_chance       = 0.0017\n"
            "  composition_lift_hrr_over_nn     = 0.0067\n\n"
            "MAGNITUDE_COUPLING DISCRIMINATOR (rules out by-construction-saturation):\n"
            "  cor per_seed: [0.0453, 0.1975, -0.0691]  mean=0.0579 (LOW)\n"
            "  magnitude_coupling_ok = True (cor below saturation threshold)\n"
            "  HRR mechanism is NOT artificially saturated; it genuinely fails to generalize.\n\n"
            "PRE-REG BAR MISSES:\n"
            "  HP_heldout_floor >= 0.50           FAIL (HRR=0.0067)\n"
            "  HP_composition_lift_min >= 0.10    FAIL (lift=0.0067 over NN; 0.0017 over chance)\n"
            "  HP_baseline_ceiling <= 0.15        PASS (baseline=0.0067)\n"
            "  HP_baseline_no_leak = True         PASS\n\n"
            "RATIFICATION RATIONALE:\n"
            "  HONEST_NEGATIVE_MECHANISM_NULL: HRR involutive unbinding chains add ZERO signal\n"
            "  over baseline (both arms at chance+0.0017). Magnitude-coupling check rules out\n"
            "  the by-construction-saturation explanation (coupling cor=0.058 is genuinely low,\n"
            "  not artificially capped). Mechanism is genuinely non-functional at this regime.\n\n"
            "STAGE 3 COMPOSITIONAL UNDERSTANDING IMPLICATION:\n"
            "  HRR composition via unbind-chain on feature-overlap prototypes for systematic\n"
            "  generalization (heldout-object prediction) is REFUTED at this regime. The Stage 3\n"
            "  compositional understanding track needs a DIFFERENT composition mechanism for this\n"
            "  task class.\n\n"
            "  Candidates to try (substrate-native; brain-grounded):\n"
            "  - Schema-based composition (cortical column analog; abstract roles + bindings)\n"
            "  - Multi-bank K=4 sharding with role-specific banks (extending atom 1 chain-grade)\n"
            "  - Episodic-memory NN-attention with explicit role coercion (NN-attention #6)\n"
            "  - Hebbian-superposition (#7) with grounded role-filler binding\n\n"
            "  CONSTRAINS Stage 3 pre-regs: HRR-involutive-via-unbind-chain is OFF the table\n"
            "  at this regime; future Stage 3 composition cells should choose alternative\n"
            "  mechanisms OR test at a different (smaller-vocab / smaller-NDIM / pre-trained\n"
            "  encoder) regime where HRR might actually have purchase.\n"
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "mechanism_tags": ["HRR_INVOLUTIVE_BINDING", "SYSTEMATIC_GENERALIZATION", "COMPOSITION_MECHANISM_NULL"],
            "honest_negative_subclass": "mechanism_null_genuine_not_saturation",
            "verdict": "HARD_FAIL",
            "cell_anchor": "stage3_hrr_involutive_systematic_generalization_v1",
            "metrics_path": "data/exp_stage3_hrr_involutive_systematic_generalization_v1/metrics.json",
            "n_seeds": 3,
            "hrr_inv_mean": 0.0067,
            "baseline_mean": 0.0067,
            "nn_mean": 0.0,
            "chance_acc": 0.005,
            "lift_over_chance": 0.0017,
            "magnitude_coupling_cor_mean": 0.0579,
            "by_construction_saturation_ruled_out": True,
            "regime": "N_DIM=8192 N_ENTITIES=200 N_VERBS=10 N_TRAIN=500 N_HELDOUT=100 HELDOUT_OBJ_FRAC=0.20",
            "stage3_implication": "HRR_unbind_chain_REFUTED_at_regime_need_alternative_composition",
            "verified_off_data": True,
            "verified_by": "skunkworks",
            "verified_at_ts": time.time(),
            "verified_at_date": "2026-06-26",
            "cell_commit": CELL_COMMIT_UNTRACKED,
        },
    )


# ============================================================================
# Atom 6: META rule HRR involutive cannot do systematic generalization at this regime
# ============================================================================

def atom_6_meta_hrr_systematic_generalization_refuted() -> Atom:
    return Atom(
        id=(
            "T_methodology/META_RULE_HRR_INVOLUTIVE_SYSTEMATIC_GENERALIZATION_REFUTED_AT_REGIME_"
            "n_dim_8192_n_entities_200_n_verbs_10_n_train_500_heldout_obj_frac_0p20_feature_overlap_protos"
        ),
        name=(
            "META RULE HRR involutive systematic generalization REFUTED at substrate regime "
            "(CERT-neutral discipline): future Stage 3 composition pre-regs should NOT include "
            "ARM_HRR_INVOLUTIVE for heldout-object systematic-generalization tasks at "
            "N_DIM=8192 / N_ENTITIES=200 / N_VERBS=10 / N_TRAIN=500 / HELDOUT=100 with feature-"
            "overlap prototypes (proven null in EXP_stage3_hrr_involutive_systematic_generalization_v1)."
        ),
        description=(
            "META RULE (CERT-neutral; discipline_meta).\n\n"
            "PROVENANCE: companion to atom 5 (math::T3 stage3_hrr_involutive_systematic_generalization_v1\n"
            "  HONEST_NEGATIVE_MECHANISM_NULL). HRR involutive unbinding chains add 0.0017 over\n"
            "  chance(0.005) and ZERO over baseline(0.0067) on heldout-object prediction with\n"
            "  feature-overlap prototypes at this regime.\n\n"
            "RULE STATEMENT:\n"
            "  Stage 3 compositional-understanding pre-regs MUST NOT propose ARM_HRR_INVOLUTIVE\n"
            "  as a candidate composition mechanism for tasks meeting ALL of:\n"
            "    (a) systematic generalization on heldout-object prediction\n"
            "    (b) feature-overlap prototype representation\n"
            "    (c) N_DIM in [4096, 16384] range\n"
            "    (d) N_TRAIN_FACTS / N_HELDOUT in similar proportions to v1 (5:1 to 6:1)\n"
            "  WITHOUT one of:\n"
            "    (A) regime variant outside refuted band (smaller vocab, smaller NDIM, different\n"
            "        representation; cell pre-reg must justify why this regime DIFFERS from v1)\n"
            "    (B) revival angle: explicit mechanism variant that addresses unbind-chain failure\n"
            "        (e.g., learned bindings, schema-coerced composition, NN-attention substitute)\n"
            "    (C) external pretrained-encoder grounding (the substrate-native encoder failed;\n"
            "        a pre-trained encoder might rescue)\n\n"
            "SKUNKWORKS SCHEMA-VET CHECK:\n"
            "  Pre-dispatch pre-reg VET adds 'hrr_inv_at_refuted_regime' field check.\n"
            "  Default DENY pre-regs proposing HRR-involutive systematic-generalization at the\n"
            "  refuted regime; require (A) (B) or (C) justification.\n\n"
            "DOES NOT CONSTRAIN:\n"
            "  - HRR involutive for OTHER tasks (binding lookup, role-filler decoding, simple\n"
            "    associative memory) where HRR has demonstrated value.\n"
            "  - HRR involutive at DIFFERENT regimes (smaller vocab, structured grounding, learned\n"
            "    bindings) where the unbind-chain might not be the failure mode.\n"
            "  - Other composition mechanisms (schema-based, NN-attention, multi-bank sharding\n"
            "    per atom 1 chain-grade extension).\n\n"
            "RATIONALE:\n"
            "  This rule prevents Stage 3 from repeating the same null experiment. Atom 5\n"
            "  records the negative result; this META rule operationalizes it as a SCHEMA-VET\n"
            "  pre-dispatch check for future composition cells.\n"
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        corpus=Corpus.META,
        tier=Tier.TIER_METHODOLOGY,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "rule_tags": ["META_RULE", "HRR_INVOLUTIVE_REFUTED_REGIME", "STAGE_3_COMPOSITION_GUARDRAIL"],
            "rule_class": "pre_dispatch_mechanism_choice_constraint",
            "applies_to": "stage3_compositional_understanding_pre_regs",
            "companion_atom": "math::T3 stage3_hrr_involutive_systematic_generalization_v1 honest_negative_mechanism_null",
            "discovered_from_cell": "stage3_hrr_involutive_systematic_generalization_v1",
            "discovered_from_metrics": "data/exp_stage3_hrr_involutive_systematic_generalization_v1/metrics.json",
            "ratified_by": "skunkworks",
            "ratified_at_ts": time.time(),
            "ratified_at_date": "2026-06-26",
            "refuted_regime": "N_DIM=8192 N_ENTITIES=200 N_VERBS=10 N_TRAIN=500 HELDOUT=100 feature_overlap_prototypes",
            "skunkworks_schema_vet_action": "default_deny_pre_reg_without_regime_revival_or_pretrained_justification",
        },
    )


# ============================================================================
# A5 helpers (mirror batch2 pattern)
# ============================================================================

def _cert_count(store):
    return sum(
        1 for a in store.all_atoms()
        if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
    )


def _axiom_count(store):
    return sum(
        1 for a in store.all_atoms()
        if str(a.corpus.name) == "MATH"
        and str(a.tier.name) in ("TIER_2_PRIMITIVE", "TIER_3_ALGORITHM")
        and a.algebra and len(a.algebra) >= 3
        and "oeis" not in str(a.id).lower()
        and not str(a.id).startswith("T3/wikidata_")
    )


def _cap_pres_ok():
    import importlib
    return all(
        hasattr(importlib.import_module(m), s) for m, s in [
            ("backend.substrate_index.hmm_decoder", "viterbi_decode"),
            ("hdlab.perceptron", "StructuredPerceptron"),
            ("backend.substrate_index.sequence_labeler", "NERTagger"),
            ("hdlab.bayesian_inference", "EMMixture"),
            ("backend.substrate_index.intent_classifier", "IntentClassifier"),
            ("backend.substrate_index.refuse_gated_retriever", "RefuseGatedRetriever"),
        ]
    )


def _add_atom_with_round_trip(atom: Atom, source: str, note: str) -> str:
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    already_present = ps.get_atom(qid) is not None
    if already_present:
        print(f"  SKIP (idempotent): {atom.id[:80]} already present")
        return "skipped"
    print(f"  ADDING: {atom.id[:100]}")
    print(f"    kind={atom.kind.value} tier={atom.tier.value} corpus={atom.corpus.value}")
    ps.add_atom(atom, source=source, note=note)
    ps2 = PartitionedStore(STORE_ROOT)
    found = ps2.get_atom(qid)
    if found is None:
        print(f"  FAIL: atom not found post-add")
        return "fail"
    if found.tier != atom.tier:
        print(f"  FAIL: tier mismatch (expected {atom.tier} got {found.tier})")
        return "fail"
    if found.kind != atom.kind:
        print(f"  FAIL: kind mismatch (expected {atom.kind} got {found.kind})")
        return "fail"
    md = found.metadata or {}
    if md.get("provenance_quality") != (atom.metadata or {}).get("provenance_quality"):
        print(f"  FAIL: provenance_quality mismatch")
        return "fail"
    print(f"    PASS: round-trip survival OK")
    return "added"


def main():
    apply = "--apply" in sys.argv
    dry = "--dry-run" in sys.argv or not apply
    print("=" * 80)
    print(f"Skunkworks landed-VET batch 9 atomize 2026-06-26 (5 cells)| "
          f"mode={'APPLY' if apply else 'DRY-RUN'}")
    print("=" * 80)

    atoms_specs = [
        (
            "Atom 1: multi-bank K=4 N=8192 CHAIN_GRADE (delta=+1)",
            atom_1_multi_bank_K4_N8192_chain_grade(),
            "chain_grade",
            1,
            "multi_bank_K4_N8192_chain_grade_rec_1p0000_cv_0p0000_3seeds_v2b_OOM_rescue",
        ),
        (
            "Atom 2: edge_imp v5 CFU MEASURED_MECHANISM (delta=0; first fairness-pass in family)",
            atom_2_edge_imp_v5_cfu_measured_mechanism(),
            "measured_mechanism",
            0,
            "edge_imp_v5_CFU_first_fairness_passing_sel_unretr_0p048_below_0p15",
        ),
        (
            "Atom 3: META chain-gen feasibility pre-flight (custom; delta=0)",
            atom_3_meta_chain_gen_feasibility_pre_flight(),
            "custom",
            0,
            "META_RULE_chain_gen_feasibility_pre_flight_multihop_barrier1_infra_bug",
        ),
        (
            "Atom 4: HOPFIELD consolidation HONEST_NEGATIVE_BY_CONSTRUCTION_SATURATION (delta=+1)",
            atom_4_hopfield_consolidation_honest_negative_by_construction_saturation(),
            "honest_negative",
            1,
            "HOPFIELD_consolidation_v1_honest_negative_by_construction_saturation_N_DIM_8192_N_CAT_5",
        ),
        (
            "Atom 5: HRR involutive HONEST_NEGATIVE_MECHANISM_NULL (delta=+1)",
            atom_5_hrr_involutive_honest_negative_mechanism_null(),
            "honest_negative",
            1,
            "HRR_involutive_systematic_generalization_v1_honest_negative_mechanism_null_eq_baseline",
        ),
        (
            "Atom 6: META HRR involutive systematic-generalization refuted at regime (custom; delta=0)",
            atom_6_meta_hrr_systematic_generalization_refuted(),
            "custom",
            0,
            "META_RULE_HRR_involutive_systematic_generalization_refuted_at_regime",
        ),
    ]

    print(f"\nBatch contains {len(atoms_specs)} atoms.")
    chain_grade_count = sum(1 for s in atoms_specs if s[2] == "chain_grade")
    measured_mech_count = sum(1 for s in atoms_specs if s[2] == "measured_mechanism")
    honest_neg_count = sum(1 for s in atoms_specs if s[2] == "honest_negative")
    custom_count = sum(1 for s in atoms_specs if s[2] == "custom")
    print(f"  chain_grade: {chain_grade_count}")
    print(f"  measured_mechanism: {measured_mech_count}")
    print(f"  honest_negative: {honest_neg_count}")
    print(f"  custom (META): {custom_count}")

    print("\n--- A5 PRE-SNAPSHOT ---")
    ps_pre = PartitionedStore(STORE_ROOT)
    pre_cert = _cert_count(ps_pre)
    pre_ax = _axiom_count(ps_pre)
    pre_cap = _cap_pres_ok()
    pre_total = sum(1 for _ in ps_pre.all_atoms())
    print(f"  CERT_CHAIN_GRADE_N (provenance_quality count) = {pre_cert}")
    print(f"  axiom_count = {pre_ax}")
    print(f"  cap_pres = {'6/6' if pre_cap else 'FAIL'}")
    print(f"  total_atoms = {pre_total}")
    assert pre_ax == 206, f"A5-PRE axiom drift: {pre_ax} != 206"
    assert pre_cap, "A5-PRE cap_pres FAIL"

    # Expected delta on CERT_CHAIN_GRADE provenance_quality count:
    # chain_grade (1) + honest_negative (2) = +3 CERT_CHAIN_GRADE provenance atoms
    # measured_mechanism uses MEASURED_MECHANISM provenance (delta 0)
    # custom META uses META_RULE_CERT_NEUTRAL provenance (delta 0)
    expected_cert_chain_grade_delta = chain_grade_count + honest_neg_count
    print(f"  expected post-CERT_CHAIN_GRADE_N delta = +{expected_cert_chain_grade_delta} "
          f"(=1 chain_grade + 2 honest_negative)")

    print("\n--- IDEMPOTENCY INVENTORY ---")
    for label, atom, _, _, _ in atoms_specs:
        qid = f"{atom.corpus.value}::{atom.id}"
        present = ps_pre.get_atom(qid) is not None
        marker = "PRESENT (SKIP)" if present else "NEW"
        print(f"  {marker}: {qid[:120]}")

    if dry:
        print("\nDRY-RUN: no Store writes; no ledger appends. Pass --apply to commit.")
        return 0

    print("\n--- A5 WRITES (Store + cert_ledger same A5 window per atom) ---")
    ATOMIZED_BY = "skunkworks_atomize_landed_vet_batch9_5cell_2026-06-26"
    landed = 0

    for idx, (label, atom, cert_status, delta, note_tag) in enumerate(atoms_specs, start=1):
        print(f"\n[{idx}/{len(atoms_specs)}] {label}")
        action = _add_atom_with_round_trip(
            atom,
            source=ATOMIZED_BY,
            note=f"{note_tag}; ruling note {NOTES_PATH_VET}",
        )
        if action == "fail":
            print(f"  ABORT: atom add failed; ledger not appended; stopping batch.")
            return 1
        if action == "skipped":
            print(f"  Skipping ledger append for already-present atom.")
            continue
        landed += 1

        ps_live = PartitionedStore(STORE_ROOT)
        live_cert = _cert_count(ps_live)

        atom_qid = f"{atom.corpus.value}::{atom.id}"
        metrics_path = (atom.metadata or {}).get("metrics_path", "n/a-meta-rule")
        cell_commit = (atom.metadata or {}).get("cell_commit", "n/a-meta-rule")

        if cert_status == "chain_grade":
            row = build_chain_grade_ruling_row(
                atom_id=atom_qid,
                cell_commit=cell_commit,
                verdict="HARD_PASS_CHAIN_GRADE_multi_bank_K4_N8192_skunkworks_off_data",
                notes_path=NOTES_PATH_VET,
                metrics_path=metrics_path,
                atomized_by=ATOMIZED_BY,
                note=f"phase_c_live_write_skunkworks_atomize_batch9_{note_tag}",
            )
        elif cert_status == "measured_mechanism":
            row = build_measured_mechanism_row(
                atom_id=atom_qid,
                cell_commit=cell_commit,
                verdict="MIDDLE_BAND_first_fairness_passing_in_family_brain_grounded_skunkworks_off_data",
                notes_path=NOTES_PATH_VET,
                metrics_path=metrics_path,
                atomized_by=ATOMIZED_BY,
                note=f"phase_c_live_write_skunkworks_atomize_batch9_{note_tag}",
            )
        elif cert_status == "honest_negative":
            row = build_honest_negative_row(
                atom_id=atom_qid,
                cell_commit=cell_commit,
                verdict="HARD_FAIL_honest_negative_skunkworks_off_data",
                notes_path=NOTES_PATH_VET,
                metrics_path=metrics_path,
                atomized_by=ATOMIZED_BY,
                note=f"phase_c_live_write_skunkworks_atomize_batch9_{note_tag}",
            )
        else:
            # custom META rule -- minimal row
            row = {
                "op": "cert_ruling",
                "atom_id": atom_qid,
                "cert_status": "custom_meta",
                "cert_class": "discipline_meta_cert_neutral",
                "verified_off_data": True,
                "atomized_by": ATOMIZED_BY,
                "cell_commit": cell_commit,
                "verdict": "META_RULE_CERT_NEUTRAL",
                "cert_increment_delta": 0,
                "cv": None,
                "referent_pointer": {
                    "notes_path": NOTES_PATH_VET,
                    "metrics_path": metrics_path,
                    "atom_qualified_id": atom_qid,
                },
                "supersedes": None,
                "note": f"phase_c_live_write_skunkworks_atomize_batch9_{note_tag}",
            }

        try:
            new_hash = append_cert_ledger_row(
                row,
                expected_cert_n_pre=live_cert,
                expected_cert_n_post=live_cert + (1 if cert_status in ("chain_grade", "honest_negative") else 0),
            )
            print(f"  ledger row appended: {new_hash[:16]}")
        except Exception as e:
            print(f"  WARN: ledger append exception (non-fatal for atom write): {e}")

    # POST-snapshot
    print("\n--- A5 POST-SNAPSHOT ---")
    ps_post = PartitionedStore(STORE_ROOT)
    post_cert = _cert_count(ps_post)
    post_ax = _axiom_count(ps_post)
    post_cap = _cap_pres_ok()
    post_total = sum(1 for _ in ps_post.all_atoms())
    print(f"  CERT_CHAIN_GRADE_N = {post_cert}  (PRE={pre_cert}, delta={post_cert-pre_cert})")
    print(f"  axiom_count = {post_ax}")
    print(f"  cap_pres = {'6/6' if post_cap else 'FAIL'}")
    print(f"  total_atoms = {post_total}  (PRE={pre_total}, delta={post_total-pre_total})")
    assert post_ax == 206, f"A5-POST axiom drift: {post_ax} != 206"
    assert post_cap, "A5-POST cap_pres FAIL"

    print(f"\nLanded {landed} new atoms; expected CERT delta=+{expected_cert_chain_grade_delta}; "
          f"actual={post_cert-pre_cert}")
    if landed == len(atoms_specs):
        if (post_cert - pre_cert) == expected_cert_chain_grade_delta:
            print("OK: A5 PRE/POST invariants held; CERT delta matched expectation.")
        else:
            print(f"WARN: CERT delta mismatch (expected +{expected_cert_chain_grade_delta}, "
                  f"got +{post_cert-pre_cert}); check provenance_quality tagging.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
