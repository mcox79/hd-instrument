"""Skunkworks 2026-06-25 -- A5-gated back-fill batch (9 items).

USER-approved cert-ledger back-fill: "Yes I want a cert ledger back fill - I am
sick of us rediscovering old experiments." Full auto authorized.

TIER RULING NOTE: notes/skunkworks_back_fill_batch_2026-06-25.md
DIRECTOR ROUTING: notes/director_to_skunkworks_cert_trail_backfill_tasks_2026-06-25.md

QUEUE (9 items, atomize-order respects idempotency + cert delta accuracy):

  1. math::T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL
     honest_negative; delta=0; full 3 seeds; mechanism refuted

  2. math::T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL
     honest_negative; delta=0; full 3 seeds; depth-degrades

  3. math::T3/EXP_substrate_refuse_gate_near_domain_v2_chain_grade
     chain_grade; delta=+1; full 3 seeds; mechanism honest at envelope V_REL_IN=8

  4. (NESS envelope SKIP; already in Store + ledger CERT 592 since 2026-06-20)

  5. math::T3/EXP_capacity_sweet_spot_v1_cpu_v1_MM
     measured_mechanism; delta=0; OVERRIDE from Director's chain-grade framing
     (selector degenerate: picks sel_f=0.01 for every task; v2 already MM)

  6. math::T3/EXP_substrate_per_cluster_stratified_extraction_with_random_control_v1_smoke_MM
     measured_mechanism; delta=0; OVERRIDE from Director's chain-grade framing
     (smoke + n_seeds=1; cannot chain-grade at this rigor)

  7. math::T3/EXP_sparse_onset_higher_loads_followup_cpu_v1_MM
     measured_mechanism; delta=0; smoke + n_seeds=1; Director already framed MM

  8a. meta::T3/META_M4_consolidation_K_THRESH_1_writes_answer_tuple_by_construction_saturated
      meta_rule; delta=0; ATOM-ONLY back-fill (ledger row exists; idempotency-aware)

  8b. meta::T3/META_M5_cross_cell_baseline_compare_requires_chain_construction_match
      meta_rule; delta=0; ATOM-ONLY back-fill (ledger row exists)

  9. meta::T3/META_BARRIER_1_TRIPLE_NEGATIVE_substrate_native_multihop_3_for_3_REFUTED_2_hop_ceiling_permanent
     meta_rule; delta=0; META composition (consolidation_v3 + pointer_chain_v2 + WM_scaffolded)

EXPECTED:
  CERT N: 594 -> 595 (+1 for refuse_gate v2 chain_grade)
  math atoms: +6 new (3 HARD_FAIL/MM/chain_grade + 3 older MM)
  meta atoms: +3 new (M4 + M5 back-fill + BARRIER_1_TRIPLE_NEGATIVE)
  ledger rows: +7 new (8a/8b idempotency-skip)

DISCIPLINES HONORED:
  - Verify-off-data: every cited number recomputed from per_seed via .venv statistics
  - Verify-the-referent: NESS already-in-ledger caught; M4/M5 ledger-only state confirmed
  - Q-discipline: 1.000 results checked for saturation (refuse_gate envelope; per_cluster
    stratified perfect-by-construction-of-arm1; capacity v1 selector-degeneracy)
  - Fix #28: 3 Director chain-grade claims overridden to MM after per-arm verification
  - Symmetric anti-negativity: chain_grade UP (refuse_gate v2) vs MM DOWN (3 demotions)
    at same rigor
  - A5 PRE/POST snapshot; round-trip verify per atom; partial-recovery semantics
  - Idempotency: skip atoms already present; ledger idempotency via _ts_stripped match
  - Foreground execution (Fix #20); no subprocess pipes
  - Path-scoped commits (caller-side)
  - ASCII only
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path("D:/AI/hd-instrument").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
    build_honest_negative_row,
    build_measured_mechanism_row,
)


STORE_ROOT = Path("D:/AI/hd-instrument/data/substrate_index")
ATOMIZED_BY = "skunkworks_back_fill_batch_2026-06-25"
NOTES_PATH = "notes/skunkworks_back_fill_batch_2026-06-25.md"

METRICS_CONS_V3 = "data/exp_substrate_multihop_consolidation_v3_proper_test_heldout_fix/metrics.json"
METRICS_WM = "data/exp_substrate_multihop_wm_scaffolded_v1/metrics.json"
METRICS_REFUSE_V2 = "data/exp_substrate_refuse_gate_near_domain_v2/metrics.json"
METRICS_CAPACITY_V1 = "data/exp_capacity_sweet_spot_v1_cpu_v1/metrics.json"
METRICS_PCLUSTER_SMOKE = "data/exp_substrate_per_cluster_stratified_extraction_with_random_control_v1_smoke/metrics.json"
METRICS_SPARSE_ONSET = "data/exp_sparse_onset_higher_loads_followup_cpu_v1/metrics.json"


# ============================================================================
# Atom 1: consolidation v3 HARD_FAIL
# ============================================================================

def build_atom_consolidation_v3_hard_fail() -> Atom:
    return Atom(
        id="T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL",
        name=(
            "Substrate multihop consolidation v3 HELDOUT_FIX -- HARD_FAIL "
            "(mechanism refuted: consolidated -> ~0%, unconsolidated -> 100% "
            "matching naive; consol_held_max=0.400 vs naive=0.850; K=50 "
            "'best' is arithmetic of fewer-classes-touched, not consolidation "
            "working; Barrier 1 closer; first of triple-negative)"
        ),
        description=(
            "Substrate-native multi-hop closure attempt via compound-predicate "
            "consolidation (consolidator stores R_compound=p1*p2 when "
            "co-occurrence count exceeds K_THRESH; query routes to compound). "
            "v3 fixed v1/v2 bugs: v1 had perfect-by-construction CONS_IMMEDIATE "
            "K_THRESH=1 (stores test answer; META_M4); v2 had nan heldout "
            "(make_two_hop_chains exhausted V_C before generating heldout); "
            "v3 uses 3 chain classes (HIGH/MID/LOW) at frequencies "
            "[100, 10, 2] training vs [30, 15, 5] heldout with DISJOINT s "
            "values so consolidator never sees heldout chain compositions. "
            "NAIVE arm uses separate single-class chain set (beta-sweep "
            "apples-to-apples regime).\n\n"
            "PER-SEED HELDOUT_OVERALL (3 seeds [7, 17, 23], independently "
            "recomputed off per_seed via .venv statistics):\n"
            "  arm_naive_hard_2hop      mean=0.8500  per_seed=[0.845, 0.905, 0.800]\n"
            "                           cv=0.062\n"
            "  arm_consol_kthr_1_ctrl   mean=0.0067  per_seed=[0.020, 0.000, 0.000]\n"
            "                           cv=1.732 (near-zero)\n"
            "  arm_consol_kthr_3        mean=0.1067  per_seed=[0.120, 0.100, 0.100]\n"
            "                           cv=0.108\n"
            "  arm_consol_kthr_10       mean=0.1067  per_seed=[0.120, 0.100, 0.100]\n"
            "                           cv=0.108\n"
            "  arm_consol_kthr_50       mean=0.4000  per_seed=[0.400, 0.400, 0.400]\n"
            "                           cv=0.000\n"
            "  arm_hybrid_kthr_3+clean  mean=0.1067  per_seed=[0.120, 0.100, 0.100]\n"
            "                           cv=0.108\n\n"
            "TRAINING_OVERALL all consol arms saturate ~1.000 (K=50 0.994); "
            "the consolidator memorizes training. The HELDOUT failure is the "
            "load-bearing finding.\n\n"
            "SMOKING-GUN PER-CLASS HELDOUT (mean across seeds):\n"
            "  arm   | HIGH consol? | HIGH held | MID consol? | MID held | LOW consol? | LOW held\n"
            "  K=1   | YES          | 0.000     | YES         | 0.022    | YES         | 0.000\n"
            "  K=3   | YES          | 0.000     | YES         | 0.022    | NO          | 1.000\n"
            "  K=10  | YES          | 0.000     | YES         | 0.022    | NO          | 1.000\n"
            "  K=50  | YES          | 0.000     | NO          | 1.000    | NO          | 1.000\n\n"
            "PATTERN: consolidated class -> ~0% heldout; unconsolidated class "
            "-> 100% (naive 2hop path survives). K=50 'best' 0.400 is "
            "mechanically (1 destroyed HIGH x 30/50 + 2 untouched MID,LOW x "
            "20/50) / 1 = 0.400. K=50 wins by DOING the consolidation "
            "primitive LESS.\n\n"
            "RAILS FIRED:\n"
            "  NAIVE_OUT_OF_BAND(0.850 not in [0.62, 0.68]) -- v2 band copied; "
            "v3 V_C=600 + V_P=6 multi-class regime makes 2hop easier (M2/M6 "
            "rail-derivation debt; NOT a substrate finding).\n"
            "  KTHR_GATING_NOT_DIFFERENTIATING(train spread 0.006 < 0.10) -- "
            "all consol arms saturate training; this confirms K-thresh gates "
            "which classes get the operator but the operator DESTROYS heldout "
            "generalization regardless.\n\n"
            "WHY HARD_FAIL NOT MIDDLE_BAND OR MM:\n"
            "  - Pre-reg HP_break_heldout>=0.85 (FAIL: max=0.400, margin 0.45).\n"
            "  - Pre-reg HP_heldout>=0.75 (FAIL: max=0.400, margin 0.35).\n"
            "  - Pre-reg HF_near_naive_delta=0.03 (FIRED: 0.850 - 0.400 = "
            "0.450 >> 0.03 floor).\n"
            "  - Per-class breakdown rules out 'rail miss invalidates "
            "comparison' (the consolidated class HELDOUT is exactly 0% "
            "regardless of rail calibration).\n"
            "  - Per-class breakdown rules out 'by-construction-saturation "
            "hiding signal' (the UN-consolidated classes are at 100%; if the "
            "primitive worked, they would NOT be at 100% -- they would be at "
            "the consolidator's processed signal which never appears).\n"
            "  - 0/3 seeds show any positive consolidation lift on any "
            "consolidated class. Mechanism refuted, not undersized.\n\n"
            "BARRIER 1 CONTEXT (triple-negative same day, after this batch):\n"
            "  This cell is one of THREE substrate-native multi-hop closures "
            "tested 2026-06-25, all HARD_FAIL:\n"
            "    (1) consolidation v3 (THIS atom; compound-predicate via K-thresh)\n"
            "    (2) pointer_chain_hybrid_v2 (atomized morning 2026-06-25; "
            "external-index-style routing via substrate-atom pointers)\n"
            "    (3) wm_scaffolded_v1 (this batch; PFC+hippocampus composition\n"
            "        with WM slot holding cleaned intermediate)\n"
            "  Together refute substrate-native multi-hop generalization at "
            "production-scale random-bipolar isotropic regime via three "
            "independent mechanisms. Substrate-product definition unchanged: "
            "2-hop chain-grade memory + composition + retrieval + audit; "
            "multi-hop requires external PFC scaffold OR feature-share "
            "cortical analog (different cell).\n\n"
            "WHAT THIS DOES NOT SHOW (honest scope):\n"
            "  - Does NOT refute consolidation at OTHER regimes (anisotropic "
            "encoder, structured corpus, learned attention over compound "
            "predicates).\n"
            "  - Does NOT test consolidator-as-AUGMENTATION (keep naive path "
            "+ add consolidated path + ensemble); revival angle for Research.\n"
            "  - Does NOT test consolidation with explicit s-generalization "
            "training (currently consolidator binds to specific s instances).\n"
            "  - Does NOT refute semantic-consolidation under feature-share "
            "cortical analog (different cell).\n\n"
            "TIER: HARD_FAIL / honest_negative; delta=0 (proven NEGATIVE "
            "bound). Counts as proven negative for Barrier 1 substrate-native "
            "multi-hop via compound-predicate consolidation mechanism."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "pre_reg_miss_proven_bound",
            "verdict": (
                "HARD_FAIL_consolidation_v3_HELDOUT_FIX_3seeds_7_17_23_N_8192_"
                "V_C_600_V_P_6_3_classes_HIGH_MID_LOW_freqs_train_100_10_2_"
                "heldout_30_15_5_DISJOINT_s_NAIVE_2hop_mean_0p850_per_seed_"
                "0p845_0p905_0p800_cv_0p062_CONSOL_K1_mean_0p007_K3_mean_0p107_"
                "K10_mean_0p107_K50_mean_0p400_HYBRID_mean_0p107_per_class_"
                "smoking_gun_consolidated_0p000_unconsolidated_100p000_K50_"
                "best_0p400_arithmetic_of_fewer_classes_touched_NOT_consolidation_"
                "working_0_of_3_seeds_positive_lift_on_any_consolidated_class_"
                "rails_NAIVE_OUT_OF_BAND_M2_M6_debt_KTHR_GATING_NOT_DIFFERENTIATING_"
                "training_saturated_HP_break_heldout_FAIL_HP_heldout_FAIL_HF_near_"
                "naive_delta_FIRED_0p450_margin_mechanism_refuted_not_undersized_"
                "barrier_1_first_of_triple_negative_with_pointer_chain_v2_HARD_"
                "FAIL_morning_and_WM_scaffolded_HARD_FAIL_same_batch"
            ),
            "cell_commit": "subconsv3-heldout-fix",
            "metrics_path": METRICS_CONS_V3,
            "prereg_path": None,
            "notes_path": NOTES_PATH,
            "ruling_note_partner": (
                "notes/skunkworks_tier_ruling_consolidation_v3_HARD_FAIL_"
                "2026-06-25.md (original ruling from same day; this batch "
                "atomizes the gap that ruling never closed in Store + ledger)"
            ),
            "verified_off_data": (
                "Cert-owner read per_seed directly from metrics.json via .venv "
                "statistics. Per-seed NAIVE: [0.845, 0.905, 0.800] mean 0.8500 "
                "cv 0.062. Per-seed CONSOL_K1: [0.020, 0.000, 0.000] mean "
                "0.0067. Per-seed K3: [0.120, 0.100, 0.100] mean 0.1067 cv "
                "0.108. Per-seed K10: identical 0.1067. Per-seed K50: [0.400, "
                "0.400, 0.400] mean 0.4000 cv 0.000. Per-seed HYBRID: 0.1067. "
                "Per-class HELDOUT verified by reading per_seed[i].arm_consol_"
                "kthr_K.top1_HELDOUT_PER_CLASS for each seed/K combination: "
                "consolidated_classes -> ~0%, unconsolidated_classes -> 100% "
                "uniformly across all 3 seeds. K=50 arithmetic verified: "
                "(0*30 + 1*15 + 1*5)/50 = 0.400 = observed mean. Pre-reg "
                "bands HP_break>=0.85 / HP_heldout>=0.75 / HF=0.03 / sanity "
                "[0.62,0.68] / kthr1 train>=0.95 / gating_diff_min=0.10 read "
                "from config_version string and verified against per-arm "
                "observations. Zero LLM forward calls at inference verified "
                "per per_seed[i]._llm_forward_calls_at_inference=0."
            ),
            "honest_scope": (
                "HARD_FAIL at pre-reg band on compound-predicate consolidation "
                "via K-threshold gating at random-bipolar isotropic regime "
                "(V_C=600 V_P=6 N=8192 3 chain classes HIGH/MID/LOW). DOES "
                "show mechanism HURTS (consolidated -> 0% vs naive 0.850; "
                "delta -0.85) AND fails on EVERY consolidated class across "
                "EVERY K-threshold AND fails on 0/3 seeds. DOES NOT refute "
                "consolidation at other regimes (anisotropic encoder, "
                "structured corpus, learned attention over compound "
                "predicates). DOES NOT test consolidator-as-AUGMENTATION "
                "(revival angle for Research). DOES NOT refute semantic-"
                "consolidation under feature-share cortical analog (different "
                "cell). The 'NAIVE 0.85 out of band [0.62, 0.68]' rail fire "
                "is rail-derivation debt (M2/M6); v2 band copied without "
                "re-derivation; v3 regime changed; does NOT invalidate the "
                "mechanism refutation (per-class consolidated->0% is regime-"
                "independent)."
            ),
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 8192,
            "V_C": 600,
            "NAIVE_V_P": 2,
            "CONSOL_V_P": 6,
            "chain_classes": [["HIGH"], ["MID"], ["LOW"]],
            "freqs_train": [100, 10, 2],
            "freqs_held": [30, 15, 5],
            "K_GRID": [1, 3, 10, 50],
            "naive_n_chains": 200,
            "naive_heldout_mean": 0.8500,
            "naive_heldout_per_seed": [0.845, 0.905, 0.800],
            "naive_heldout_cv": 0.062,
            "consol_K1_mean": 0.0067,
            "consol_K3_mean": 0.1067,
            "consol_K10_mean": 0.1067,
            "consol_K50_mean": 0.4000,
            "hybrid_mean": 0.1067,
            "consol_max_heldout": 0.4000,
            "naive_vs_consol_max_delta": -0.4500,
            "smoking_gun_per_class_consolidated_pct": "~0%",
            "smoking_gun_per_class_unconsolidated_pct": "100% (naive 2hop survives)",
            "pre_reg_bands": {
                "HP_break_heldout": ">=0.85 (FAIL: max 0.400)",
                "HP_heldout": ">=0.75 (FAIL: max 0.400)",
                "HF_near_naive_delta": "=0.03 (FIRED: 0.450)",
                "naive_sanity": "[0.62, 0.68] (FIRED 0.850; rail debt)",
                "kthr1_train_high_saturate": ">=0.95 (PASS 1.000)",
                "gating_diff_min": "=0.10 (FIRED 0.006; training saturated)",
            },
            "rails_fired": [
                "NAIVE_OUT_OF_BAND_rail_derivation_debt_M2_M6",
                "KTHR_GATING_NOT_DIFFERENTIATING_training_saturated",
            ],
            "barrier_1_context": (
                "First of triple-negative for substrate-native multi-hop at "
                "production-scale isotropic regime. Composes with "
                "pointer_chain_hybrid_v2_HARD_FAIL (morning 2026-06-25) + "
                "wm_scaffolded_v1_HARD_FAIL (this batch) for "
                "META_BARRIER_1_TRIPLE_NEGATIVE (atomized in this batch)."
            ),
            "composes_with": [
                "T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_HARD_FAIL",
                "T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL",
                "T3/META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
                "T3/META_M4_consolidation_K_THRESH_1_writes_answer_tuple_by_construction_saturated",
                "T3/META_M5_cross_cell_baseline_compare_requires_chain_construction_match",
                "T3/META_M6_NAIVE_baseline_must_be_derived_not_copied_from_prior_cells",
                "T3/META_BARRIER_1_TRIPLE_NEGATIVE_substrate_native_multihop_3_for_3_REFUTED_2_hop_ceiling_permanent",
            ],
            "cites": [
                "Fix_28_verify_per_arm_per_class_not_verdict_msg_framing",
                "Fix_28_per_class_breakdown_rules_out_rail_miss_invalidates",
                "USER_route_negatives_to_research_2x_3x_revival_drills",
                "Director_routed_back_fill_cert_trail_integrity_2026-06-25",
                "USER_quote_back_fill_prevents_rediscovery_2026-06-25",
                "consolidation_v3_original_ruling_atom_write_gap_caught",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
        },
        aliases=[],
    )


# ============================================================================
# Atom 2: WM-scaffolded multi-hop HARD_FAIL
# ============================================================================

def build_atom_wm_scaffolded_hard_fail() -> Atom:
    return Atom(
        id="T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL",
        name=(
            "Substrate multihop WM-scaffolded v1 -- HARD_FAIL "
            "(WM scaffold reduces to pointer-chain at production scale; "
            "WM_2HOP=0.425 vs baseline 0.650 = -22.5pp HURTS; per-hop "
            "survival ~0.70 compounding to 0.035 at depth 10; third of "
            "Barrier 1 triple-negative)"
        ),
        description=(
            "Substrate-native multi-hop closure attempt via WM-scaffolded "
            "composition. Mechanism: PFC + hippocampus brain analog -- each "
            "hop reads a cleaned scaffold intermediate (E[next_idx] written "
            "through WM slot), aiming to prevent geometric error compounding "
            "observed in pointer_chain v2 (same morning 2026-06-25, also "
            "HARD_FAIL). Baseline arm uses beta-sweep rail [0.62, 0.68] "
            "sanity (matches pointer_chain v2 baseline regime).\n\n"
            "PER-SEED (3 seeds [7, 17, 23], independently recomputed off "
            "per_seed via .venv statistics; mean / pstdev / sample-cv reported):\n"
            "  arm_baseline_hrr_2hop     mean=0.6500  per_seed=[0.605, 0.670, 0.675]\n"
            "                            cv=0.060  baseline_sanity 1/3 breach\n"
            "                            (seed 7 = 0.605 below [0.62, 0.68])\n"
            "  arm_wm_scaffolded_2hop    mean=0.4250  per_seed=[0.485, 0.375, 0.415]\n"
            "                            cv=0.131  (Director spec cited 0.107)\n"
            "  arm_wm_scaffolded_5hop    mean=0.1217  per_seed=[0.145, 0.110, 0.110]\n"
            "                            cv=0.166  (Director spec cited 0.136)\n"
            "  arm_wm_scaffolded_10hop   mean=0.0350  per_seed=[0.040, 0.035, 0.030]\n"
            "                            cv=0.143  (Director spec cited 0.117)\n\n"
            "(cv-arithmetic difference between cert-owner and Director "
            "framing: Director appears to have used pstdev; cert-owner uses "
            "statistics.stdev (sample). Both confirm HARD_FAIL; difference "
            "is sub-percentage-point on the verdict-determining margin.)\n\n"
            "KEY LIFTS (paired same-N, same-regime; substrate-product framing):\n"
            "  WM_2HOP - baseline = 0.425 - 0.650 = -0.2250 (WM HURTS by 22.5pp)\n"
            "  WM_5HOP - WM_2HOP  = 0.122 - 0.425 = -0.303 (depth-degrades)\n"
            "  WM_10HOP - WM_2HOP = 0.035 - 0.425 = -0.390 (compounding decay)\n\n"
            "PER-STEP ACCURACY (per_seed[0].arm_wm_scaffolded_10hop.per_step_acc):\n"
            "  [0.69, 0.485, 0.31, 0.205, 0.145, 0.10, 0.07, 0.065, 0.04, 0.04]\n"
            "  per-hop survival ~0.70; compounding 0.70^10 ~ 0.028; matches "
            "observed 0.035. The WM scaffold does NOT upgrade per-hop "
            "cleanup fidelity; it merely structures the chain via slot "
            "binding -- but slot-bound cleanup at production scale loses "
            "~30% per hop to crosstalk, same as the unscaffolded pointer-"
            "chain mechanism.\n\n"
            "MECHANISM EQUIVALENCE with pointer_chain v2:\n"
            "  pointer_chain v2 5hop = 0.1220 vs WM 5hop = 0.1217 (essentially "
            "identical)\n"
            "  pointer_chain v2 10hop = 0.0350 vs WM 10hop = 0.0350 (identical)\n"
            "  Conclusion: at this regime, the WM-slot scaffold adds zero "
            "discriminative information over pointer-chain hybrid. Both are "
            "limited by per-hop cleanup fidelity (~0.70) which is a substrate "
            "primitive constraint, not a composition-architecture choice.\n\n"
            "RAILS:\n"
            "  baseline_sanity [0.62, 0.68]: 1/3 breach DOWNWARD (seed 7 = "
            "0.605). Same regime variance pattern as pointer_chain v2 "
            "baseline (cited in META_M6); mitigation = n_seeds>=10 OR "
            "widened band. Direction of breach (downward) makes baseline "
            "mean 0.650 LOWER than ideal -- if anything, this makes WM look "
            "BETTER than it would at the calibrated band. Even so, WM 0.425 "
            "underperforms by 22pp.\n"
            "  HP_2hop>=0.80 (FAIL: 0.425, margin 0.375)\n"
            "  HP_5hop>=0.50 (FAIL: 0.122, margin 0.378)\n"
            "  HP_10hop>=0.20 (FAIL: 0.035, margin 0.165)\n"
            "  HP_cv<=0.07 (FAIL: 0.131 / 0.166 / 0.143; 2-2.4x over cap)\n"
            "  HF_5hop<0.15 (FIRED: 0.122 < 0.15 -- floor breached)\n\n"
            "BARRIER 1 CONTEXT (third of triple-negative):\n"
            "  This is the THIRD substrate-native multi-hop closure HARD_FAIL "
            "in two days. Together with consolidation v3 (this batch) and "
            "pointer_chain v2 (morning 2026-06-25), the substrate-native "
            "multi-hop generalization is REFUTED at production-scale random-"
            "bipolar isotropic regime via three independent mechanisms:\n"
            "    (1) compound-predicate consolidation (K-thresh gating)\n"
            "    (2) pointer-chain hybrid (external-index-via-substrate)\n"
            "    (3) WM-scaffold (PFC slot binding)\n"
            "  2-hop ceiling is now substrate-product PERMANENT at this regime. "
            "Multi-hop reasoning routes via external scaffold (PFC analog at "
            "LLM-level) OR feature-share cortical analog (different cell, "
            "anisotropic encoder).\n\n"
            "ZERO-LLM-CALLS-AT-INFERENCE: verified per per_seed[i]."
            "_llm_forward_calls_at_inference=0 across all 3 seeds. Substrate-"
            "only-decode gate PASSES; the failure is on substrate-native "
            "capability, not LLM-contamination.\n\n"
            "WHAT THIS DOES NOT SHOW (honest scope):\n"
            "  - Does NOT test WM-scaffold at OTHER regimes (anisotropic "
            "encoder may give better per-hop cleanup; larger N may upgrade "
            "fidelity).\n"
            "  - Does NOT test WM-scaffold with explicit per-hop confidence "
            "gating (e.g., refuse-when-WM-slot-confidence-low; revival angle "
            "for Research).\n"
            "  - Does NOT refute WM as a primitive (single-slot WM is "
            "chain-grade per working_memory_hrr_slots_PRODUCTION_v1); only "
            "refutes WM-as-multi-hop-scaffold at this regime.\n\n"
            "TIER: HARD_FAIL / honest_negative; delta=0 (proven NEGATIVE "
            "bound). Counts as proven negative for Barrier 1 substrate-native "
            "multi-hop via WM-scaffold mechanism."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "HONEST_NEGATIVE",
            "cert_status": "honest_negative",
            "cert_class": "pre_reg_miss_proven_bound",
            "verdict": (
                "HARD_FAIL_WM_SCAFFOLD_SAME_REGIME_AS_POINTER_V2_3seeds_7_17_"
                "23_N_8192_V_C_200_BASELINE_V_P_2_WM_V_P_10_K_SET_20_baseline_"
                "mean_0p650_per_seed_0p605_0p670_0p675_1of3_seeds_sanity_"
                "breach_seed7_0p605_below_0p62_lower_bound_WM_2HOP_mean_0p425_"
                "per_seed_0p485_0p375_0p415_cv_0p131_WM_5HOP_mean_0p122_cv_"
                "0p166_WM_10HOP_mean_0p035_cv_0p143_WM_HURTS_baseline_minus_"
                "22p5pp_per_hop_survival_0p70_compounding_to_0p028_matches_"
                "observed_0p035_mechanism_equivalent_to_pointer_chain_v2_at_"
                "production_scale_zero_LLM_calls_inference_substrate_only_"
                "decode_PASSES_HP_2hop_FAIL_HP_5hop_FAIL_HP_10hop_FAIL_HP_cv_"
                "FAIL_HF_5hop_FIRED_third_of_barrier_1_triple_negative_with_"
                "consolidation_v3_and_pointer_chain_v2_2_hop_ceiling_substrate_"
                "product_permanent_at_isotropic_regime"
            ),
            "cell_commit": "wm_scaffolded_v1_full",
            "metrics_path": METRICS_WM,
            "prereg_path": "preregs/2026-06-25_substrate_multihop_wm_scaffolded_v1.md",
            "notes_path": NOTES_PATH,
            "verified_off_data": (
                "Cert-owner read per_seed directly via .venv statistics. "
                "Baseline per_seed [0.605, 0.670, 0.675] mean 0.6500 cv "
                "0.060; WM_2HOP per_seed [0.485, 0.375, 0.415] mean 0.4250 "
                "cv 0.131 (Director cited 0.107 likely pstdev); WM_5HOP "
                "per_seed [0.145, 0.110, 0.110] mean 0.1217 cv 0.166 "
                "(Director 0.136); WM_10HOP per_seed [0.040, 0.035, 0.030] "
                "mean 0.0350 cv 0.143 (Director 0.117). cv difference is "
                "sample-vs-population stdev choice; both confirm HARD_FAIL. "
                "Per-step accuracy seed 7 read from per_seed[0].arm_wm_"
                "scaffolded_10hop.per_step_acc: [0.69, 0.485, 0.31, 0.205, "
                "0.145, 0.10, 0.07, 0.065, 0.04, 0.04]. per-hop survival "
                "0.70 compounding to 0.70^10 = 0.028 matches observed 0.035. "
                "Mechanism-equivalence with pointer_chain v2 verified by "
                "cross-cell number match (both 5hop 0.122; both 10hop "
                "0.035). Zero-LLM-calls verified per per_seed[i]."
                "_llm_forward_calls_at_inference=0 across all 3 seeds."
            ),
            "honest_scope": (
                "HARD_FAIL at pre-reg band on WM-scaffold multi-hop "
                "mechanism at random-bipolar isotropic regime (V_C=200 "
                "WM_V_P=10 BASELINE_V_P=2 N=8192 K_SET=20 hop_depths "
                "[2,5,10]). DOES show mechanism HURTS (-22.5pp vs baseline) "
                "AND depth-degrades to 0.035 at 10 hops matching geometric "
                "decay 0.70^10. DOES NOT refute WM as a primitive "
                "(working_memory_hrr_slots_PRODUCTION_v1 is chain-grade for "
                "single-slot K<=32). DOES NOT test WM-scaffold at "
                "anisotropic encoder or higher N. DOES NOT test per-hop "
                "confidence gating revival angle. Mechanism-equivalence "
                "with pointer_chain v2 (both ~0.122 at 5hop) indicates the "
                "constraint is per-hop cleanup fidelity (substrate "
                "primitive), not the composition-architecture choice."
            ),
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 8192,
            "V_C": 200,
            "BASELINE_V_P": 2,
            "WM_V_P": 10,
            "K_SET": 20,
            "hop_depths": [2, 5, 10],
            "baseline_mean": 0.6500,
            "baseline_per_seed": [0.605, 0.670, 0.675],
            "baseline_cv": 0.060,
            "baseline_sanity_breach_seeds": 1,
            "baseline_sanity_breach_direction": "downward_seed7_0p605",
            "wm_2hop_mean": 0.4250,
            "wm_2hop_per_seed": [0.485, 0.375, 0.415],
            "wm_2hop_cv": 0.131,
            "wm_5hop_mean": 0.1217,
            "wm_5hop_per_seed": [0.145, 0.110, 0.110],
            "wm_5hop_cv": 0.166,
            "wm_10hop_mean": 0.0350,
            "wm_10hop_per_seed": [0.040, 0.035, 0.030],
            "wm_10hop_cv": 0.143,
            "per_step_acc_seed7_10hop": [0.69, 0.485, 0.31, 0.205, 0.145, 0.10, 0.07, 0.065, 0.04, 0.04],
            "per_hop_survival_ratio_approx": 0.70,
            "wm_vs_baseline_2hop_lift": -0.2250,
            "pointer_chain_v2_5hop_reference": 0.1220,
            "pointer_chain_v2_10hop_reference": 0.0350,
            "wm_vs_pointer_chain_equivalent": True,
            "pre_reg_bands": {
                "HP_2hop": ">=0.80 (FAIL 0.425)",
                "HP_5hop": ">=0.50 (FAIL 0.122)",
                "HP_10hop": ">=0.20 (FAIL 0.035)",
                "HP_cv": "<=0.07 (FAIL 0.131-0.166)",
                "HP_partial_5hop": ">=0.30 (FAIL 0.122)",
                "HP_partial_10hop": ">=0.10 (FAIL 0.035)",
                "mid_5hop": "[0.15, 0.30] (FIRED below at 0.122)",
                "HF_5hop": "<0.15 (FIRED at 0.122)",
                "baseline_sanity": "[0.62, 0.68] (1/3 breach seed7=0.605)",
            },
            "barrier_1_context": (
                "Third of triple-negative for substrate-native multi-hop at "
                "production-scale isotropic regime. Composes with "
                "consolidation_v3_HARD_FAIL (this batch) + pointer_chain_"
                "hybrid_v2_HARD_FAIL (morning 2026-06-25) for "
                "META_BARRIER_1_TRIPLE_NEGATIVE (atomized in this batch)."
            ),
            "composes_with": [
                "T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL",
                "T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_HARD_FAIL",
                "T3/EXP_working_memory_hrr_slots_PRODUCTION_v1_DOES_NOT_REFUTE_WM_primitive",
                "T3/META_M6_NAIVE_baseline_must_be_derived_not_copied_from_prior_cells",
                "T3/META_BARRIER_1_TRIPLE_NEGATIVE_substrate_native_multihop_3_for_3_REFUTED_2_hop_ceiling_permanent",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_not_summary_verdict_text",
                "USER_route_negatives_to_research_2x_3x_revival_drills",
                "Director_routed_back_fill_cert_trail_integrity_2026-06-25",
                "USER_quote_back_fill_prevents_rediscovery_2026-06-25",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
        },
        aliases=[],
    )


# ============================================================================
# Atom 3: refuse-gate v2 chain_grade
# ============================================================================

def build_atom_refuse_gate_v2_chain_grade() -> Atom:
    return Atom(
        id="T3/EXP_substrate_refuse_gate_near_domain_v2_chain_grade",
        name=(
            "Substrate refuse-gate near-domain v2 -- HARD_PASS_BOTH_WORK "
            "(audit-relation-check ALONE closes the medqa-style failure: "
            "NEAR refuse=1.000 / cv=0.000 / 3 seeds full; substrate-product "
            "audit-device design point; envelope V_RELATIONS_IN<=~50 at N=8192)"
        ),
        description=(
            "Substrate-native refuse-gate for the NEAR-DOMAIN-MIXED failure "
            "mode (in-domain subject + out-of-domain relation -- the medqa "
            "case where a question about an in-domain entity uses a relation "
            "the substrate has no library entry for). v1 was saturation-"
            "designed (corpus made it trivially separable); v2 fixes the "
            "corpus design + tests four arms:\n"
            "  (a) AUDIT_NAIVE_ALONE: subject-only audit (sim against "
            "W_subjects >= 0.40). Reproduces the medqa failure -- naive "
            "audit cannot catch out-of-domain relations on in-domain "
            "subjects.\n"
            "  (b) AUDIT_RELATION_CHECK: subject AND relation audit (sims "
            "against W_subjects AND W_relations_in, both >= 0.40). Smarter "
            "audit alone.\n"
            "  (c) INTENT_ALONE: relation classifier confidence (sim against "
            "relation_in_prototypes >= 0.03). Substrate-native intent "
            "classification without subject audit.\n"
            "  (d) AUDIT_NAIVE+INTENT: composition of (a)+(c). Tests whether "
            "intent classifier rescues naive audit's medqa failure.\n\n"
            "PER-SEED NEAR_DOMAIN_MIXED refuse_rate (3 seeds [11, 13, 19], "
            "independently recomputed off per_seed via .venv statistics):\n"
            "  arm_audit_naive_alone    refuse=[0.00, 0.00, 0.00] mean=0.000\n"
            "                           cv=0.000 (MEDQA failure reproduced)\n"
            "  arm_audit_relation_check refuse=[1.00, 1.00, 1.00] mean=1.000\n"
            "                           cv=0.000 (smarter audit closes gap)\n"
            "  arm_intent_alone         refuse=[1.00, 0.96, 1.00] mean=0.987\n"
            "                           cv=0.023 (intent alone closes)\n"
            "  arm_audit_naive+intent   refuse=[1.00, 0.96, 1.00] mean=0.987\n"
            "                           cv=0.023 (composition closes; same as intent)\n\n"
            "SANITY (PURE_IN_DOMAIN answer + PURE_OUT_OF_DOMAIN refuse) across "
            "all arms: all 1.000 or 0.993 (within sanity); no spurious refuse "
            "on in-domain queries and no spurious answer on out-of-domain. "
            "MEDQA failure (audit_naive NEAR refuse=0.000) reproduced as "
            "designed for v2.\n\n"
            "PRE-REG VERDICT: HARD_PASS_BOTH_WORK branch fires: "
            "AUDIT_RELATION_CHECK NEAR refuse=1.000 >= 0.70 AND "
            "AUDIT_NAIVE_PLUS_INTENT NEAR refuse=0.987 >= 0.70 (both meet "
            "the >= 0.70 floor with margin). Per pre-reg: 'pick the simpler' "
            "-- audit-relation-check is the substrate-product refuse-gate "
            "design.\n\n"
            "Q-DISCIPLINE SATURATION CHECK ON 1.000 RESULT:\n"
            "  Mechanism honest: arm_audit_relation_check does max(W_relations_"
            "in @ rel_vec) >= 0.40 where W_relations_in is the 8-relation "
            "in-library (V_RELATIONS_IN=8 at N=8192 with random bipolar). "
            "NEAR_DOMAIN_MIXED queries use OUT-domain relations sampled "
            "from out_relation_atoms (separate bipolar random library, NOT "
            "in W_relations_in).\n"
            "  Noise floor at N=8192: sqrt(2/8192) ~ 0.016, well below "
            "threshold 0.40.\n"
            "  Out-of-library random bipolar relations therefore yield "
            "max-sim ~0 reliably -> refuse=1.000 is mechanically correct, "
            "NOT by-construction-saturation.\n"
            "  ENVELOPE CAVEAT: mechanism works because V_RELATIONS_IN=8 "
            "is small + out_relation_atoms are random bipolar. At larger "
            "V_RELATIONS_IN, false-refuse rate on in-library relations would "
            "grow (the in-domain relations also have ~0 cross-sim, but at "
            "V_REL_IN=10K-100K some random in-library relation will "
            "accidentally hit threshold). Operating envelope: V_RELATIONS_IN "
            "<= ~50 at N=8192 with random bipolar; structured/learned "
            "relations would shift this bound up.\n\n"
            "CERT-GRADE CONDITIONS MET:\n"
            "  - 3 seeds full (n_seeds=3, run_mode='full')\n"
            "  - cv=0.000 across seeds (audit-relation-check arm)\n"
            "  - 100 queries per category per seed (300 NEAR queries total)\n"
            "  - Sanity rails passed (PURE_IN answer=1.000, PURE_OUT "
            "refuse=1.000)\n"
            "  - Pre-reg discriminator NEAR refuse >= 0.70 met by 1.000 "
            "with margin 0.30\n"
            "  - MEDQA failure reproduced on naive-alone arm (confirms "
            "test setup is honest -- discriminator can fail; it does fail "
            "on the wrong arm)\n"
            "  - Zero LLM forward calls at inference verified per per_seed\n\n"
            "STRATEGIC ROLE: Audit-device substrate-product layer. The "
            "substrate-product positioning had 'audit refuse' listed but "
            "only the broader graph-health refuse mechanism was chain-"
            "grade (refuse_gate_5_graph_health_cpu_v1). This atom closes "
            "the second axis: subject+relation-library audit closes the "
            "medqa-style 'in-domain subject + out-of-domain relation' "
            "failure mode. Together with graph-health refuse (capacity-"
            "saturation) and CSP uncertainty quantification, the audit "
            "device now has 3+ chain-grade refuse mechanisms covering "
            "distinct failure modes.\n\n"
            "WHAT THIS DOES NOT SHOW (honest scope):\n"
            "  - Does NOT test at V_RELATIONS_IN > 50 (operating envelope "
            "caveat above).\n"
            "  - Does NOT test structured/learned relations (substrate-"
            "owned encoder Path C lane); random-bipolar relations are the "
            "test setup. Anisotropic-encoder lane may shift envelope.\n"
            "  - Does NOT test substrate self-detection of refuse calibration "
            "drift across continual learning (next-cycle question).\n\n"
            "TIER: chain_grade / pre_reg_pass; delta=+1 (cert N 594 -> 595)."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "verdict": (
                "HARD_PASS_BOTH_WORK_AUDIT_RELATION_CHECK_NEAR_DOMAIN_refuse_"
                "1p000_cv_0p000_3seeds_11_13_19_N_8192_V_C_IN_600_V_C_OUT_"
                "600_V_REL_IN_8_V_REL_OUT_8_100_queries_per_category_AUDIT_"
                "NAIVE_ALONE_PURE_IN_answer_1p000_PURE_OUT_refuse_1p000_NEAR_"
                "refuse_0p000_MEDQA_failure_reproduced_AUDIT_RELATION_CHECK_"
                "ALL_3_categories_1p000_cv_0p000_INTENT_ALONE_NEAR_0p987_cv_"
                "0p023_AUDIT_NAIVE_PLUS_INTENT_NEAR_0p987_cv_0p023_per_reg_"
                "HP_BOTH_WORK_pick_simpler_audit_relation_check_is_substrate_"
                "product_design_envelope_V_REL_IN_lte_50_at_N_8192_random_"
                "bipolar_noise_floor_0p016_threshold_0p40_out_of_library_"
                "reliable_refuse_NOT_by_construction_saturation_zero_LLM_"
                "calls_verified_second_axis_of_audit_device_substrate_"
                "product_layer_alongside_graph_health_refuse_and_CSP"
            ),
            "cell_commit": "refuse_gate_v2_full",
            "metrics_path": METRICS_REFUSE_V2,
            "prereg_path": "preregs/2026-06-25_substrate_refuse_gate_near_domain_v2.md",
            "notes_path": NOTES_PATH,
            "verified_off_data": (
                "Cert-owner read per_seed directly via .venv statistics. "
                "arm_audit_naive_alone NEAR refuse [0.00, 0.00, 0.00] mean "
                "0.000 cv 0.000 (MEDQA failure reproduced). "
                "arm_audit_relation_check NEAR refuse [1.00, 1.00, 1.00] "
                "mean 1.000 cv 0.000. arm_intent_alone NEAR refuse [1.00, "
                "0.96, 1.00] mean 0.987 cv 0.023. arm_audit_naive_plus_"
                "intent NEAR refuse [1.00, 0.96, 1.00] mean 0.987 cv 0.023. "
                "Sanity verified per per_seed[i].arm_X.per_category."
                "PURE_IN_DOMAIN.answer_rate (all 1.000) and "
                "PURE_OUT_OF_DOMAIN.refuse_rate (1.000 / 0.98 / 1.000 for "
                "intent; 1.000 for others). Mechanism verified honest by "
                "reading experiments/exp_substrate_refuse_gate_near_domain_"
                "v2.py: arm_audit_relation_check does max(sims) check "
                "against W_relations_in (8-atom library, random bipolar at "
                "N=8192); NEAR_DOMAIN_MIXED uses out_relation_atoms "
                "(separate bipolar library, NOT in W_relations_in). Noise "
                "floor sqrt(2/8192) ~ 0.016 << threshold 0.40 -> refuse "
                "outcome mechanically correct, not by-construction. Zero "
                "LLM calls verified per per_seed[i]._llm_forward_calls_at_"
                "inference=0 across all 3 seeds."
            ),
            "honest_scope": (
                "Chain-grade at audit-relation-check refuse mechanism at "
                "V_RELATIONS_IN=8 N=8192 random-bipolar regime, 100 queries "
                "per category per seed, 3 seeds. DOES show smarter audit "
                "(subject + relation library check) closes the medqa-style "
                "NEAR_DOMAIN_MIXED failure that subject-only audit cannot "
                "catch. DOES NOT extend to V_RELATIONS_IN > ~50 at this N "
                "(operating envelope caveat). DOES NOT test structured/"
                "learned relations (anisotropic encoder Path C lane). DOES "
                "NOT test refuse calibration drift across continual learning."
            ),
            "n_seeds": 3,
            "seeds": [11, 13, 19],
            "N_DIM": 8192,
            "V_C_IN": 600,
            "V_C_OUT": 600,
            "V_RELATIONS_IN": 8,
            "V_RELATIONS_OUT": 8,
            "n_queries_per_category": 100,
            "categories": ["PURE_IN_DOMAIN", "PURE_OUT_OF_DOMAIN", "NEAR_DOMAIN_MIXED"],
            "in_cats": ["animals", "geography", "tools"],
            "out_cats": ["medical", "legal", "financial"],
            "thresholds": {
                "SUBJECT_AUDIT_THR": 0.40,
                "RELATION_AUDIT_THR": 0.40,
                "INTENT_CONF_THR": 0.03,
            },
            "key_metrics": {
                "near_audit_naive_alone_mean": 0.000,
                "near_audit_naive_alone_cv": 0.000,
                "near_audit_relation_check_mean": 1.000,
                "near_audit_relation_check_cv": 0.000,
                "near_intent_alone_mean": 0.987,
                "near_intent_alone_cv": 0.023,
                "near_audit_naive_plus_intent_mean": 0.987,
                "near_audit_naive_plus_intent_cv": 0.023,
                "pure_in_answer_all_arms": 1.000,
                "pure_out_refuse_min": 0.980,
                "medqa_failure_reproduced_naive": True,
            },
            "q_discipline_check": {
                "result_1p000_suspect": True,
                "noise_floor_at_N_8192_random_bipolar": "sqrt(2/N) ~ 0.016",
                "threshold_RELATION_AUDIT_THR": 0.40,
                "out_of_library_max_sim_expected": "~0",
                "by_construction_saturation": False,
                "envelope_caveat": "V_RELATIONS_IN <= ~50 at N=8192; larger V_REL would accidentally hit threshold",
            },
            "pre_reg_bands": {
                "sanity_pure_in": ">=0.85 (PASS 1.000)",
                "sanity_pure_out": ">=0.85 (PASS 0.980-1.000)",
                "HP_near": ">=0.70 (PASS audit_relation_check 1.000; audit+intent 0.987)",
                "MEDQA_audit_refuse": "<0.50 (PASS reproduced 0.000)",
                "HP_deep_fail": "<0.50 (PASS none fail)",
                "cv": "<=0.07 (PASS audit_relation 0.000; intent 0.023)",
            },
            "envelope_operating_point": {
                "V_RELATIONS_IN_max_safe_at_N_8192": "~50",
                "encoder": "random_bipolar",
                "regime": "isotropic",
                "extension_path": "anisotropic_encoder_or_learned_relations_shifts_envelope_up",
            },
            "strategic_role": (
                "Second axis of substrate-product audit-device layer. "
                "Audit-device now has 3+ chain-grade refuse mechanisms "
                "covering distinct failure modes: (a) audit-based (this "
                "atom, in-domain-subject + out-of-domain-relation), (b) "
                "graph-health (capacity saturation, refuse_gate_5_graph_"
                "health_cpu_v1), (c) CSP uncertainty quantification (csp_"
                "first_ship_v1). Closes the medqa-style failure mode in the "
                "substrate-product positioning."
            ),
            "composes_with": [
                "T3/EXP_refuse_gate_5_graph_health_cpu_v1",
                "T3/EXP_csp_first_ship_v1",
                "T3/EXP_a1_substrate_intent_classifier_v1",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_per_seed",
                "Q_discipline_suspect_1p000_results_verify_envelope",
                "Director_routed_back_fill_cert_trail_integrity_2026-06-25",
                "USER_quote_back_fill_prevents_rediscovery_2026-06-25",
                "BIAS_17_envelope_caveat_explicit_in_atom_metadata",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
        },
        aliases=[],
    )


# ============================================================================
# Atom 5: capacity_sweet_spot v1 -- MM (OVERRIDE from Director chain-grade)
# ============================================================================

def build_atom_capacity_sweet_spot_v1_mm() -> Atom:
    return Atom(
        id="T3/EXP_capacity_sweet_spot_v1_cpu_v1_MM",
        name=(
            "Capacity sweet spot v1 -- MEASURED_MECHANISM "
            "(SKUNKWORKS OVERRIDE of Director chain-grade framing: "
            "selector picks sel_f=0.01 for EVERY task -- degenerate, NOT "
            "adaptive; v2 already MM proving fixed f=0.01 never beaten; "
            "v1 is first observation of broad-sweet-spot phenomenon; "
            "Fix #28 inflated-claim pattern caught)"
        ),
        description=(
            "Load-adaptive sparsity-f selector v1: picks sparsity f from "
            "measured target_alpha via cited alpha_c(f) (cell a3f473dd). "
            "Cell verdict_msg framing: 'HARD_PASS f-adaptivity beats both "
            "dense-default and fixed-f by >=10pct on >=2 high-load tasks; "
            "no-degrade, fallback, seed-robust CV<0.15'.\n\n"
            "SKUNKWORKS OVERRIDE per Fix #28 (verify per-arm not verdict_msg):\n"
            "  Per-task sel_f picks (read off detail.per_task):\n"
            "    lowload (target_alpha=0.1):    sel_f=0.01\n"
            "    midload (target_alpha=0.5):    sel_f=0.01\n"
            "    highload (target_alpha=1.5):   sel_f=0.01\n"
            "    veryhigh (target_alpha=3.0):   sel_f=0.01\n"
            "    out_of_envelope (alpha=12.0):  sel_f=1.0 (FALLBACK)\n"
            "  The selector picks sel_f=0.01 for EVERY in-envelope task. "
            "It is NOT adaptive across loads -- it is DEGENERATE on the "
            "always-sparsest-f choice.\n\n"
            "Per-task recall comparison:\n"
            "  lowload:    rec_default=0.000 rec_naive=1.000 rec_selector=1.000\n"
            "  midload:    rec_default=0.000 rec_naive=1.000 rec_selector=1.000\n"
            "  highload:   rec_default=0.000 rec_naive=0.805 rec_selector=1.000\n"
            "  veryhigh:   rec_default=0.000 rec_naive=0.019 rec_selector=1.000\n"
            "  out_of_env: rec_default=0.000 rec_naive=1.000 rec_selector=0.000\n\n"
            "The 'selector beats fixed-f' claim is mechanically:\n"
            "  - 'fixed-f' in the cell is f=0.05 (rec_naive).\n"
            "  - 'selector' is sel_f=0.01 (sparser -> more capacity at high "
            "load).\n"
            "  - So at highload (alpha=1.5), sel_f=0.01 (selector) beats "
            "f=0.05 (rec_naive=0.805) by 19.5pp; at veryhigh, sparser "
            "beats by 98.1pp.\n"
            "  - But picking f=0.01 ALWAYS (skipping the selector entirely) "
            "would yield the same result -- the selector adds zero value "
            "because the SWEET-SPOT IS BROAD: f=0.01 is the right answer at "
            "every load in this envelope.\n\n"
            "V2 SUPERSEDES THIS FRAMING:\n"
            "  exp_capacity_sweet_spot_v2_cpu_v1 (also atomized: math::T3/"
            "EXP_capacity_sweet_spot_v2_cpu_v1, provenance_quality=MEASURED_"
            "MECHANISM) makes this explicit: 'earns_keep=False; never-beaten=["
            "f=0.010]; broad sweet-spot -> fixed sparsest-f suffices -> no "
            "selection value (capacity OR cue-noise cost)'. v2 added cue-"
            "noise (flip=0.3) cost expecting it would create a narrow sweet-"
            "spot; it did not. The honest characterization is MEASURED_"
            "MECHANISM (the selection machinery is mechanically correct -- "
            "sel_f varies with target_alpha for OTHER alpha ranges -- but "
            "earns no selection value in the substrate-product operating "
            "envelope tested).\n\n"
            "WHY MEASURED_MECHANISM NOT HARD_FAIL:\n"
            "  The selector mechanism is honest: it does pick sel_f based "
            "on measured target_alpha via a published curve (a3f473dd). It "
            "just happens that in the envelope tested, the curve says "
            "'always pick the sparsest f'. The mechanism CAN be measured "
            "(no NaN spokes, no instrument bugs); it measures its own "
            "broad-sweet-spot character cleanly.\n\n"
            "WHY NOT CHAIN_GRADE (OVERRIDE):\n"
            "  Director's spec framed as 'HARD_PASS chain-grade candidate' "
            "based on verdict_msg ('beats fixed-f by >=10pct on >=2 high-"
            "load tasks'). Per Fix #28 (verify per-arm, not verdict_msg "
            "framing): the per-arm sel_f shows the selector is degenerate "
            "in this envelope; the claim is technically true but the "
            "selection adds no value. Atomizing as chain-grade would inflate "
            "the cert count with a primitive that does nothing the substrate-"
            "product can't already do with a fixed sparsest-f. v2's "
            "MEASURED_MECHANISM tier is the honest level for this primitive.\n\n"
            "WHAT THIS DOES NOT SHOW (honest scope):\n"
            "  - Does NOT refute load-adaptive selection at OTHER cost "
            "regimes (high cue-noise, structured corpus, anisotropic "
            "encoder may create narrower sweet-spots where selection earns "
            "its keep).\n"
            "  - Does NOT test target_alpha sweeps outside [0.1, 3.0]; the "
            "selector DOES vary in the out-of-envelope fallback case.\n"
            "  - Does NOT replace v2 as the canonical characterization; v2 "
            "explicitly tests cost-induced sweet-spot narrowing and confirms "
            "broad-sweet-spot.\n\n"
            "TIER: MEASURED_MECHANISM (mechanism characterization, CERT-"
            "neutral, delta=0). First observation of broad-sweet-spot for "
            "sparsity-f selection at the substrate operating envelope."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verdict": (
                "MEASURED_MECHANISM_capacity_sweet_spot_v1_SKUNKWORKS_OVERRIDE_"
                "of_Director_chain_grade_framing_selector_picks_sel_f_0p01_"
                "for_every_task_lowload_midload_highload_veryhigh_DEGENERATE_"
                "not_adaptive_broad_sweet_spot_v2_already_MM_proving_fixed_"
                "f_0p01_never_beaten_earns_keep_False_within_0p019_of_oracle_"
                "Fix_28_inflated_claim_pattern_caught_first_observation_of_"
                "broad_sweet_spot_phenomenon_v2_supersedes_framing_with_cue_"
                "noise_flip_0p3_cost_added_did_not_create_narrow_sweet_spot"
            ),
            "cell_commit": "capacity_sweet_spot_v1_cpu_v1",
            "metrics_path": METRICS_CAPACITY_V1,
            "prereg_path": None,
            "notes_path": NOTES_PATH,
            "verified_off_data": (
                "Cert-owner read per_unit + detail.per_task directly via "
                ".venv json.load. sel_f per task: lowload=0.01, midload=0.01, "
                "highload=0.01, veryhigh=0.01, out_of_envelope=1.0 "
                "(FALLBACK). rec_selector per task: lowload=1.000, midload="
                "1.000, highload=1.000, veryhigh=1.000, out_of_envelope="
                "0.000. rec_naive (fixed f=0.05) per task: lowload=1.000, "
                "midload=1.000, highload=0.805, veryhigh=0.019, out=1.000. "
                "n_seeds=3 per task; worst_seed_cv=0.0. selector_seed_cv all "
                "0.0 -- mechanism is deterministic given target_alpha. v2 "
                "metrics inspected at data/exp_capacity_sweet_spot_v2_cpu_"
                "v1/metrics.json: verdict='MEASURED_MECHANISM'; earns_keep="
                "False; never-beaten=[f=0.010]; broad sweet-spot confirmed "
                "with cue-noise flip=0.3 cost added (no narrowing). v2 atom "
                "exists at math::T3/EXP_capacity_sweet_spot_v2_cpu_v1 with "
                "provenance_quality='MEASURED_MECHANISM'."
            ),
            "honest_scope": (
                "MEASURED_MECHANISM for sparsity-f selection at substrate "
                "operating envelope target_alpha in [0.1, 3.0]. DOES show "
                "selector is mechanically correct (picks per published "
                "alpha_c(f) curve from a3f473dd). DOES show selector is "
                "DEGENERATE in this envelope (always picks sparsest f=0.01). "
                "DOES NOT refute load-adaptive selection at OTHER cost "
                "regimes (high cue-noise, structured corpus, anisotropic "
                "encoder may yet create narrow sweet-spots). v2 supersedes "
                "for canonical characterization (cue-noise tested, broad-"
                "sweet-spot confirmed)."
            ),
            "n_seeds": 3,
            "N_DIM": 8192,
            "n_tasks": 5,
            "tasks": ["lowload", "midload", "highload_DISC", "veryhigh_DISC", "out_of_envelope_FALLBACK"],
            "target_alphas": [0.1, 0.5, 1.5, 3.0, 12.0],
            "sel_f_per_task": {"lowload": 0.01, "midload": 0.01, "highload_DISC": 0.01, "veryhigh_DISC": 0.01, "out_of_envelope_FALLBACK": 1.0},
            "selector_degenerate_in_envelope": True,
            "selector_always_picks_sparsest_f": 0.01,
            "rec_selector_per_task": {"lowload": 1.000, "midload": 1.000, "highload_DISC": 1.000, "veryhigh_DISC": 1.000, "out_of_envelope_FALLBACK": 0.000},
            "rec_naive_per_task": {"lowload": 1.000, "midload": 1.000, "highload_DISC": 0.805, "veryhigh_DISC": 0.019, "out_of_envelope_FALLBACK": 1.000},
            "rec_default_per_task": {"lowload": 0.000, "midload": 0.000, "highload_DISC": 0.000, "veryhigh_DISC": 0.000, "out_of_envelope_FALLBACK": 0.000},
            "worst_seed_cv": 0.000,
            "skunkworks_override_reason": "Director chain-grade framing per verdict_msg; per-arm sel_f shows selector degenerate in envelope; v2 already MM",
            "v2_supersedes_framing": "math::T3/EXP_capacity_sweet_spot_v2_cpu_v1",
            "composes_with": [
                "T3/EXP_capacity_sweet_spot_v2_cpu_v1",
                "T3/EXP_sparse_alpha_fine_sweep_below_004_v1",
                "T3/EXP_sparse_onset_higher_loads_followup_cpu_v1_MM",
                "META_FIX_28_VERIFY_PER_ARM_METRICS_NOT_SUMMARY_VERDICT_TEXT",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_not_verdict_msg_framing",
                "Q_discipline_default_under_claim_let_cert_owner_tier_up",
                "Director_routed_back_fill_cert_trail_integrity_2026-06-25",
                "v2_companion_atom_already_MM_supersedes_framing",
                "symmetric_anti_negativity_honest_downward_correction_at_same_rigor",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
        },
        aliases=[],
    )


# ============================================================================
# Atom 6: per_cluster_stratified smoke -- MM (OVERRIDE from Director chain-grade)
# ============================================================================

def build_atom_per_cluster_stratified_smoke_mm() -> Atom:
    return Atom(
        id="T3/EXP_substrate_per_cluster_stratified_extraction_with_random_control_v1_smoke_MM",
        name=(
            "Per-cluster stratified extraction with random control v1 SMOKE "
            "-- MEASURED_MECHANISM (SKUNKWORKS OVERRIDE of Director chain-"
            "grade framing: run_mode=smoke + n_seeds=1 cannot chain-grade; "
            "random-control discriminator IS valid; upgrade path = re-"
            "dispatch full + n_seeds>=3)"
        ),
        description=(
            "Substrate-native per-cluster stratified extraction with random "
            "control discriminator. ARM1 (stratified): pick sp tokens per "
            "cluster; covers concept space. ARM2 (random control at matched "
            "budget): pick sp total tokens uniformly random; measures whether "
            "the stratification adds value over random-at-budget.\n\n"
            "PER-SP RESULTS (single seed, smoke regime):\n"
            "  sp=10:    arm1_cov=1.000  arm2_cov=0.477  discrim=0.523\n"
            "  sp=100:   arm1_cov=1.000  arm2_cov=0.436  discrim=0.564\n"
            "  sp=1000:  arm1_cov=1.000  arm2_cov=0.457  discrim=0.543\n\n"
            "Discriminator: arm1 - arm2 >= 0.40 at sp=1000. Pre-reg HP: "
            "arm1>=0.95 AND arm2<=0.50 AND discrim>0.40 AND cv<=0.05. All "
            "pre-reg HP gates pass at single seed.\n\n"
            "SKUNKWORKS OVERRIDE per BIAS-14 (production-scale instrument "
            "calibration) + symmetric anti-negativity:\n"
            "  - run_mode=smoke (NOT full)\n"
            "  - n_seeds=1 (NOT 3+)\n"
            "  - n_tok=5000 (smoke-scale dataset)\n"
            "  - total_budget=243 per sp setting\n"
            "  - Director's spec framed as 'chain-grade-candidate' based on "
            "verdict_msg HARD_PASS. Per Fix #28 + chain-grade definition "
            "requiring multi-seed CV check at production scale: cannot "
            "chain-grade evidence from n_seeds=1 smoke. The mechanism IS "
            "honest (random control fails as expected; stratified holds; "
            "discriminator valid); the evidence-rigor tier is MEASURED_"
            "MECHANISM, not chain-grade.\n\n"
            "Q-DISCIPLINE CHECK ON 1.000 RESULT:\n"
            "  arm1_cov=1.000 is perfect-by-construction-of-arm1 -- "
            "stratified sampling by definition covers strata. The "
            "discriminator is arm2 vs arm1 (NOT arm1 alone), so the 1.000 "
            "saturation does NOT invalidate the mechanism evidence; arm2 "
            "discrimination (0.457 at sp=1000) is the load-bearing number "
            "and is well below saturation.\n\n"
            "UPGRADE PATH TO CHAIN-GRADE:\n"
            "  Re-dispatch at run_mode=full + n_seeds>=3 + production-scale "
            "n_tok (e.g., 50000+) + multi-cluster-count sweep + cv check on "
            "arm1, arm2, and discrim independently. Currently MIDDLE_BAND-"
            "candidate at production scale; the smoke evidence is encouraging "
            "but does NOT close chain-grade.\n\n"
            "WHAT THIS DOES NOT SHOW (honest scope):\n"
            "  - Does NOT chain-grade-verify the random-control discriminator "
            "at production scale (n_seeds=1 single-shot).\n"
            "  - Does NOT test at varying n_clusters (single configuration).\n"
            "  - Does NOT test discrim cv across seeds (single seed).\n\n"
            "TIER: MEASURED_MECHANISM (mechanism characterization, smoke + "
            "single-seed evidence; CERT-neutral, delta=0). Upgrade path to "
            "chain-grade via full-mode multi-seed re-dispatch."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verdict": (
                "MEASURED_MECHANISM_per_cluster_stratified_random_control_v1_"
                "SMOKE_SKUNKWORKS_OVERRIDE_of_Director_chain_grade_framing_"
                "run_mode_smoke_n_seeds_1_cannot_chain_grade_at_this_rigor_"
                "random_control_discriminator_IS_valid_arm1_cov_1p000_arm2_"
                "cov_0p457_at_sp1000_discrim_0p543_pre_reg_HP_arm1_gte_0p95_"
                "arm2_lte_0p50_discrim_gt_0p40_cv_lte_0p05_all_PASS_at_single_"
                "seed_smoke_n_tok_5000_total_budget_243_BIAS_14_production_"
                "scale_instrument_calibration_upgrade_path_re_dispatch_full_"
                "mode_n_seeds_gte_3_n_tok_50000_plus_multi_cluster_sweep_cv_"
                "check_arm1_arm2_discrim_independently_arm1_1p000_perfect_by_"
                "construction_of_arm1_discriminator_arm2_vs_arm1_load_bearing_"
                "Q_discipline_clean"
            ),
            "cell_commit": "per_cluster_stratified_random_control_v1_smoke",
            "metrics_path": METRICS_PCLUSTER_SMOKE,
            "prereg_path": None,
            "notes_path": NOTES_PATH,
            "verified_off_data": (
                "Cert-owner read metrics.json directly via .venv json.load. "
                "run_mode='smoke', n_seeds=1, n_tok=5000, total_budget=243. "
                "Per-sp via detail.by_sp: sp=10 (arm1=1.000, arm2=0.4774, "
                "discrim=0.5226), sp=100 (1.000, 0.4362, 0.5638), sp=1000 "
                "(1.000, 0.4568, 0.5432). arm1_min_coverage=1.000, "
                "arm2_coverage_sp1000=0.4568, discrimination_sp1000=0.5432, "
                "worst_cv=0.000 (single seed -> trivially 0). Pre-reg "
                "verified at detail.pre_reg: arm1>=0.95 AND arm2<=0.50 AND "
                "discrim>0.40 AND cv<=0.05; all PASS at single seed. "
                "Discriminator mechanism: arm2 random-at-budget FAILS while "
                "arm1 stratified holds; arm1=1.000 is perfect-by-construction-"
                "of-stratification but discriminator is arm1-arm2 which is "
                "non-saturated at 0.543."
            ),
            "honest_scope": (
                "MEASURED_MECHANISM at smoke regime (n_seeds=1, n_tok=5000) "
                "for per-cluster stratified extraction with random control "
                "discriminator. DOES show the mechanism is honest (random "
                "control fails at 0.457; stratified holds at 1.000; "
                "discriminator 0.543 well above 0.40 floor). DOES NOT "
                "chain-grade-verify at production scale (single seed; smoke "
                "dataset size). Upgrade path = re-dispatch full + n_seeds>=3 "
                "+ n_tok>=50000."
            ),
            "n_seeds": 1,
            "n_tok": 5000,
            "total_budget": 243,
            "run_mode": "smoke",
            "by_sp": {
                "sp10": {"arm1_cov": 1.000, "arm2_cov": 0.4774, "discrim": 0.5226},
                "sp100": {"arm1_cov": 1.000, "arm2_cov": 0.4362, "discrim": 0.5638},
                "sp1000": {"arm1_cov": 1.000, "arm2_cov": 0.4568, "discrim": 0.5432},
            },
            "arm1_min_coverage": 1.000,
            "arm2_coverage_sp1000": 0.4568,
            "discrimination_sp1000": 0.5432,
            "worst_cv_single_seed": 0.000,
            "skunkworks_override_reason": "Director chain-grade framing per HARD_PASS verdict; run_mode=smoke + n_seeds=1 cannot chain-grade per BIAS-14",
            "upgrade_path_to_chain_grade": "re-dispatch full + n_seeds>=3 + n_tok>=50000 + multi-cluster sweep + cv check arm1/arm2/discrim independently",
            "q_discipline_check": {
                "arm1_1p000_perfect_by_construction": True,
                "discriminator_arm1_minus_arm2": 0.543,
                "discriminator_not_saturated": True,
                "load_bearing_number": "arm2_coverage_at_random_budget_0p457",
            },
            "composes_with": [
                "T3/EXP_substrate_per_cluster_stratified_extraction_v1",
                "META_FIX_28_VERIFY_PER_ARM_METRICS_NOT_SUMMARY_VERDICT_TEXT",
                "BIAS_14_production_scale_instrument_calibration",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_not_verdict_msg_framing",
                "BIAS_14_production_scale_instrument_calibration",
                "symmetric_anti_negativity_smoke_n_seeds_1_cannot_chain_grade",
                "Director_routed_back_fill_cert_trail_integrity_2026-06-25",
                "Q_discipline_default_under_claim",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
        },
        aliases=[],
    )


# ============================================================================
# Atom 7: sparse_onset_higher_loads followup -- MM (agrees with Director MM)
# ============================================================================

def build_atom_sparse_onset_higher_loads_mm() -> Atom:
    return Atom(
        id="T3/EXP_sparse_onset_higher_loads_followup_cpu_v1_MM",
        name=(
            "Sparse onset higher-loads followup v1 -- MEASURED_MECHANISM "
            "(theoretical-limit boundary refinement; located alpha_c(f) "
            "for f=[0.02, 0.03, 0.04, 0.05, 0.10] at LOADS<=8 monotonic "
            "Willshaw rise; f=[0.002, 0.005, 0.01] still capped>=LB)"
        ),
        description=(
            "Extends a3f473dd sparse super-capacity to higher LOADS<=8 to "
            "LOCATE the onset alpha_c(f) -- the critical load beyond which "
            "sparse-pattern auto-associative recall fails. Boundary-"
            "refinement measurement; substrate-product role = informing "
            "operating envelope at high-load tasks.\n\n"
            "RESULTS (single seed, smoke regime, N=2048):\n"
            "  alpha_c per f (LOADS [0.1, 0.4, 0.7, 1.0, 1.5, 2.5, 4.0, "
            "6.0, 8.0], recall>=0.95):\n"
            "    f=0.002   alpha_c=8.0   (CAPPED at lower-bound; need higher LOADS to locate)\n"
            "    f=0.005   alpha_c=8.0   (CAPPED at lower-bound)\n"
            "    f=0.010   alpha_c=8.0   (CAPPED at lower-bound)\n"
            "    f=0.020   alpha_c=4.0   LOCATED\n"
            "    f=0.030   alpha_c=2.5   LOCATED\n"
            "    f=0.040   alpha_c=1.5   LOCATED\n"
            "    f=0.050   alpha_c=1.0   LOCATED\n"
            "    f=0.100   alpha_c=0.4   LOCATED\n\n"
            "Monotonic Willshaw rise: as f decreases, alpha_c rises (more "
            "capacity per unit fan-in). Seed-stable cv<=0.05 (single seed -> "
            "trivially 0). Preserves the >= LB flag for f<=0.01 to allow "
            "future higher-LOADS extension to LOCATE these properly.\n\n"
            "MEASURED_MECHANISM tier appropriate for boundary-refinement "
            "work; not a capability claim. The alpha_c(f) curve is published "
            "by Willshaw (sparse associative memory theory); this cell "
            "empirically reproduces + extends to higher LOADS for substrate-"
            "product operating envelope calibration.\n\n"
            "STRATEGIC ROLE: Theoretical-limit measurement; cites by "
            "capacity_sweet_spot v1 + v2 selectors (which read alpha_c(f) "
            "to pick sel_f). The empirical alpha_c(f) curve from THIS atom "
            "is what those selectors use; the broad-sweet-spot finding from "
            "capacity_sweet_spot v2 is a downstream consequence of the "
            "alpha_c(f) curve's shape.\n\n"
            "WHAT THIS DOES NOT SHOW (honest scope):\n"
            "  - Does NOT chain-grade-verify (single seed, smoke).\n"
            "  - Does NOT locate alpha_c for f<=0.01 (capped at lower-bound).\n"
            "  - Does NOT measure at N other than 2048.\n"
            "  - Does NOT test under cue-noise (clean K-of-N writes).\n\n"
            "TIER: MEASURED_MECHANISM (theoretical-limit boundary refinement; "
            "CERT-neutral, delta=0)."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verdict": (
                "MEASURED_MECHANISM_sparse_onset_higher_loads_followup_v1_"
                "boundary_refinement_located_alpha_c_for_f_0p02_0p03_0p04_"
                "0p05_0p10_at_LOADS_lte_8_monotonic_Willshaw_rise_seed_stable_"
                "cv_lte_0p05_single_seed_smoke_N_2048_f_0p002_0p005_0p010_"
                "still_capped_lower_bound_preserved_for_future_higher_LOADS_"
                "extension_alpha_c_f0p020_4p0_f0p030_2p5_f0p040_1p5_f0p050_"
                "1p0_f0p100_0p4_extends_a3f473dd_sparse_super_capacity_"
                "C2_chunked_eq_unchunked_verified_substrate_product_operating_"
                "envelope_calibration_for_capacity_sweet_spot_selectors"
            ),
            "cell_commit": "sparse_onset_higher_loads_followup_v1",
            "metrics_path": METRICS_SPARSE_ONSET,
            "prereg_path": None,
            "notes_path": NOTES_PATH,
            "verified_off_data": (
                "Cert-owner read metrics.json + detail.alpha_c_by_f via "
                ".venv json.load. run_mode='smoke', n_seeds=1, N=2048. "
                "alpha_c per f verified: f=0.002 8.0 capped, f=0.005 8.0 "
                "capped, f=0.010 8.0 capped, f=0.020 4.0 located, f=0.030 "
                "2.5 located, f=0.040 1.5 located, f=0.050 1.0 located, "
                "f=0.100 0.4 located. Monotonic-over-located=True (alpha_c "
                "rises 0.4 -> 1.0 -> 1.5 -> 2.5 -> 4.0 as f decreases). "
                "worst_seed_cv=0.0 (single seed). Config-matched to "
                "a3f473dd: FLIP=0.05, Nmatch, k-of-N, W-free-sign((s@P.T)@P-"
                "s*diag), recall>=0.95. Cites a3f473dd + 7315be3c_crosstalk_"
                "capacity_law as compositional context."
            ),
            "honest_scope": (
                "MEASURED_MECHANISM at smoke regime (n_seeds=1, N=2048) for "
                "alpha_c(f) boundary refinement. DOES locate alpha_c for "
                "f=[0.02, 0.03, 0.04, 0.05, 0.10]. DOES NOT locate alpha_c "
                "for f=[0.002, 0.005, 0.01] (capped at LOADS<=8 lower "
                "bound; need higher LOADS extension). DOES NOT chain-grade-"
                "verify (single seed). DOES NOT test at N other than 2048 "
                "or under cue-noise."
            ),
            "n_seeds": 1,
            "N_DIM": 2048,
            "FRACS": [0.002, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.1],
            "LOADS": [0.1, 0.4, 0.7, 1.0, 1.5, 2.5, 4.0, 6.0, 8.0],
            "alpha_c_per_f": {
                "f0.002": {"value": 8.0, "capped_lower_bound": True},
                "f0.005": {"value": 8.0, "capped_lower_bound": True},
                "f0.010": {"value": 8.0, "capped_lower_bound": True},
                "f0.020": {"value": 4.0, "capped_lower_bound": False},
                "f0.030": {"value": 2.5, "capped_lower_bound": False},
                "f0.040": {"value": 1.5, "capped_lower_bound": False},
                "f0.050": {"value": 1.0, "capped_lower_bound": False},
                "f0.100": {"value": 0.4, "capped_lower_bound": False},
            },
            "located_f": [0.02, 0.03, 0.04, 0.05, 0.1],
            "still_capped_f": [0.002, 0.005, 0.01],
            "monotonic_over_located": True,
            "worst_seed_cv": 0.0,
            "config_match": "a3f473dd:FLIP0.05/Nmatch/kofN/Wfree-sign((s@P.T)@P-s*diag)/recall>=0.95",
            "composes_with": [
                "T3/EXP_sparse_alpha_fine_sweep_below_004_v1",
                "T3/EXP_crosstalk_capacity_law_v1",
                "T3/EXP_capacity_sweet_spot_v1_cpu_v1_MM",
                "T3/EXP_capacity_sweet_spot_v2_cpu_v1",
            ],
            "cites": [
                "sparse_alpha_fine_sweep_below_004_v1",
                "7315be3c_crosstalk_capacity_law",
                "Willshaw_sparse_associative_memory_theory",
                "Director_routed_back_fill_cert_trail_integrity_2026-06-25",
                "MEASURED_MECHANISM_tier_appropriate_for_boundary_refinement",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
        },
        aliases=[],
    )


# ============================================================================
# Atoms 8a + 8b: META_M4 + META_M5 back-fill (ledger rows already exist)
# ============================================================================

def build_atom_meta_m4_consolidation_kthresh_1_saturation() -> Atom:
    return Atom(
        id="T3/META_M4_consolidation_K_THRESH_1_writes_answer_tuple_by_construction_saturated",
        name=(
            "META M4: consolidation arms with K_THRESH=1 that write the test "
            "answer tuple directly into W are by-construction saturated; "
            "cannot be chain-grade for the source barrier they claim to close"
        ),
        description=(
            "RULE (cert-discipline, CERT-neutral): consolidation arms with "
            "K_THRESH=1 that write the test answer tuple (s, R_compound=p1*p2, "
            "o) directly into W for EVERY query at train time are by-"
            "construction saturated. Their top1 ~ 1.000 is mechanically "
            "1-hop recall of a 1-hop atom they just wrote, NOT chain-recall "
            "of the underlying 2-hop chain. They CANNOT be chain-grade for "
            "the source barrier they claim to close (multi-hop generalization).\n\n"
            "RATIONALE: K_THRESH governs which classes get the consolidation "
            "operator applied. K_THRESH=1 means EVERY class is consolidated, "
            "which (at certain regimes) means the consolidator writes a "
            "compound predicate s -> R_compound -> o for every chain it sees. "
            "Querying with the chain's (s, R_compound) endpoints then "
            "retrieves o via direct 1-hop recall of a 1-hop atom that was "
            "just stored. This is topologically identical to U1 chain-grade "
            "1-hop primitive recall, NOT chain composition.\n\n"
            "OBSERVED INSTANCE (consolidation_v1 multihop_consolidation_"
            "memory_v1, ruling notes/skunkworks_tier_ruling_cell3_cell4_"
            "consolidation_2026-06-25.md): CONS_IMMEDIATE arm K_THRESH=1 "
            "top1=1.000 3/3 seeds; W stores s, R_compound=p1p2, o for every "
            "test query at train time. capacity M=800 over N=8192 well below "
            "saturation, yet CONS_IMMEDIATE perfect -- recall not chain.\n\n"
            "DISCRIMINATOR (cell-author MUST include): held-out chains whose "
            "R1, R2 pair frequencies are NOT visible at consolidation time. "
            "If the cell does NOT include such a discriminator, the "
            "CONS_IMMEDIATE arm at K_THRESH=1 should be skunkworks-"
            "subclassified to MEASURED_MECHANISM (by-construction saturation), "
            "regardless of cell-author HARD_PASS framing.\n\n"
            "SCOPE: applies to all cells that test consolidation with "
            "K_THRESH=1 AND a consolidate-immediate operator AND no held-out-"
            "from-consolidator chain set. Does NOT apply to cells where "
            "K_THRESH>1 (gates which classes consolidate, partial application) "
            "OR cells where heldout chains have DISJOINT s values from "
            "training (consolidation_v3 fixed this; v3 became HARD_FAIL "
            "because the per-class breakdown showed consolidated->0%).\n\n"
            "COMPOSES WITH:\n"
            "  - META_M5 (cross-cell baseline compare requires chain-"
            "construction match): the K_THRESH=1 saturation only matters "
            "in cross-cell comparison if the baseline comparator was at "
            "a different regime.\n"
            "  - META_M6 (NAIVE baseline must be derived not copied): the "
            "rail-derivation discipline that catches the regime drift in "
            "the first place.\n"
            "  - META_M2 (tight rail from different config can mask "
            "direction-correct lift): adjacent rail-discipline rule.\n\n"
            "VALIDATED BY: consolidation_v1 + consolidation_v3 + multihop_"
            "consolidation_v2 trajectory. v1 HARD_PASS at CONS_IMMEDIATE=1.000 "
            "was a perfect-by-construction (the consolidator was queried on "
            "data it had just stored). v3 with disjoint-s heldout exposed the "
            "operator destroys generalization wherever applied. This rule "
            "is the methodology takeaway codifying the v1->v3 trajectory.\n\n"
            "TIER: META rule (CERT-neutral, delta=0)."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline_meta",
            "rule_id": "M4",
            "rule_category": "by_construction_saturation_detection",
            "rule_name": "consolidation_K_THRESH_1_writes_answer_tuple_by_construction_saturated",
            "rule_text": (
                "Consolidation arms with K_THRESH=1 that write the test "
                "answer tuple (s, R_compound, o) directly into W for EVERY "
                "query at train time are by-construction saturated. Their "
                "top1 ~ 1.000 is mechanically 1-hop recall of a 1-hop atom "
                "they just wrote, NOT chain-recall of the underlying 2-hop "
                "chain. Cell author MUST include held-out chains with R1, "
                "R2 pair frequencies NOT visible at consolidation time OR "
                "skunkworks-subclassifies to MEASURED_MECHANISM."
            ),
            "rebuttal_check_for_skunkworks_landed_VET": (
                "If cell tests consolidation with K_THRESH=1 AND a "
                "consolidate-immediate operator AND no held-out-from-"
                "consolidator chain set: the CONS_IMMEDIATE arm top1 is "
                "by-construction saturated. Subclassify to MEASURED_"
                "MECHANISM regardless of cell-author HARD_PASS framing. "
                "Verify by reading cell's consolidator write logic: does it "
                "store (s, R_compound, o) for the same s that appears in "
                "test queries? If yes -> saturation."
            ),
            "observed_instances": [
                ("multihop_consolidation_memory_v1 (2026-06-24): CONS_IMMEDIATE "
                 "K_THRESH=1 top1=1.000 3/3 seeds; W stores s, R_compound, o "
                 "for every test query at train time; subclassified to MM"),
                ("multihop_consolidation_v3_proper_test_heldout_fix (2026-06-25, "
                 "this back-fill batch): v3 FIXED v1's saturation via disjoint-s "
                 "heldout; v3 became HARD_FAIL because consolidator destroys "
                 "generalization wherever applied; trajectory v1 MM -> v3 "
                 "HARD_FAIL codifies the rule"),
            ],
            "composes_with": [
                "T3/META_M5_cross_cell_baseline_compare_requires_chain_construction_match",
                "T3/META_M6_NAIVE_baseline_must_be_derived_not_copied_from_prior_cells",
                "T3/META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
                "T3/EXP_substrate_multihop_consolidation_memory_v1_MM",
                "T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL",
            ],
            "validated_by": (
                "consolidation_v1 + consolidation_v2 + consolidation_v3 "
                "trajectory; v1 HARD_PASS at CONS_IMMEDIATE=1.000 was perfect-"
                "by-construction; v3 with disjoint-s heldout exposed the "
                "operator destroys generalization; this rule codifies the "
                "v1->v3 methodology takeaway."
            ),
            "ledger_row_pre_exists": True,
            "ledger_row_timestamp": 1782398467.548709,
            "ledger_row_atomized_by": "skunkworks_tier_ruling_cell3_cell4_consolidation_2026-06-25",
            "atom_back_filled_by": ATOMIZED_BY,
            "atom_back_fill_reason": "ledger_row_existed_but_atom_write_step_skipped_in_original_flow_phase3_cert_trail_integrity_back_fill",
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
            "cites": [
                "skunkworks_tier_ruling_cell3_cell4_consolidation_2026-06-25_original",
                "consolidation_v3_HARD_FAIL_2026-06-25_codifies_rule",
                "Director_routed_back_fill_cert_trail_integrity_2026-06-25",
                "phase3_cert_trail_integrity_atoms_jsonl_ledger_consistency_gap",
            ],
        },
        aliases=[],
    )


def build_atom_meta_m5_cross_cell_chain_construction_match() -> Atom:
    return Atom(
        id="T3/META_M5_cross_cell_baseline_compare_requires_chain_construction_match",
        name=(
            "META M5: cross-cell baseline comparisons require chain-"
            "construction match, not just V_C/V_P/N/K_SET match"
        ),
        description=(
            "RULE (cert-discipline, CERT-neutral): cross-cell baseline "
            "comparisons require chain-construction match (make_chains "
            "signature byte-for-byte), NOT just V_C / V_P / N / K_SET "
            "match. make_chains with fixed p1=0, p2=1 single-predicate "
            "pair SATURATES pair-density at n_chains_per_pair = n_chains. "
            "make_chains with UNIFORM p1, p2 spreads n_chains over "
            "V_P*(V_P-1) pairs at n_chains_per_pair = n_chains / (V_P * "
            "(V_P-1)). At V_P=10, the uniform case is 90x less dense per "
            "pair than the fixed-pair case. Same N, same V_C, same K_SET "
            "-> different naive baselines.\n\n"
            "OBSERVED INSTANCE: resonator_softchain_beta_sweep BASELINE_HARD "
            "0.65 (fixed-pair p1=0/p2=1) vs multihop_consolidation_v1 NAIVE "
            "0.847 (uniform pair) -- SAME V_C, V_P, N, K_SET, 15pp regime "
            "drift apples-to-oranges. Cell author copied the 0.65 sanity "
            "rail without checking the chain-construction match.\n\n"
            "DISCRIMINATOR (cell-author MUST do): match make_chains "
            "signature byte-for-byte when comparing baselines across cells. "
            "If make_chains differs (uniform vs fixed-pair vs structured vs "
            "any other variant), the baseline values are NOT comparable -- "
            "regenerate the baseline at the current cell's make_chains "
            "signature OR use a closed-form derivation that explicitly "
            "models the chain-construction density.\n\n"
            "SCOPE: applies to all cells with a NAIVE / baseline arm that "
            "compares against a prior-cell's published baseline value. Does "
            "NOT apply to within-cell baseline arms (no cross-cell comparison) "
            "OR cells using fresh-derived bands per META_M6.\n\n"
            "COMPOSES WITH:\n"
            "  - META_M4 (consolidation K_THRESH=1 by-construction "
            "saturation): the K_THRESH check addresses saturation INSIDE a "
            "cell; this rule (M5) addresses comparability ACROSS cells.\n"
            "  - META_M6 (NAIVE baseline must be derived not copied): the "
            "derivation-provenance rule that catches THIS rule's failure "
            "mode at pre-reg time.\n"
            "  - META_M2 (tight rail from different config can mask "
            "direction-correct lift): adjacent rail-discipline rule.\n\n"
            "VALIDATED BY: resonator_softchain_beta_sweep vs multihop_"
            "consolidation_v1 cross-cell discrepancy; M5 rule codified the "
            "methodology takeaway that became standing discipline.\n\n"
            "TIER: META rule (CERT-neutral, delta=0)."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline_meta",
            "rule_id": "M5",
            "rule_category": "cross_cell_baseline_comparability",
            "rule_name": "cross_cell_baseline_compare_requires_chain_construction_match",
            "rule_text": (
                "Cross-cell baseline comparisons require chain-construction "
                "match (make_chains signature byte-for-byte), NOT just V_C "
                "/ V_P / N / K_SET match. Different make_chains variants "
                "(fixed-pair vs uniform vs structured) produce different "
                "naive baselines at identical V/N/K -- regime drift between "
                "cells is apples-to-oranges. Match make_chains signature OR "
                "regenerate baseline at current cell's signature OR use "
                "closed-form derivation that explicitly models chain-"
                "construction density."
            ),
            "rebuttal_check_for_skunkworks_landed_VET": (
                "If cell's NAIVE baseline is copied from a prior cell's "
                "published value AND make_chains signatures differ (fixed-"
                "pair vs uniform vs structured): the baseline values are "
                "NOT comparable. Verify by reading both cells' make_chains "
                "and checking p1/p2 sampling strategy + n_chains/n_pairs "
                "density. If different -> reject the baseline copy."
            ),
            "observed_instances": [
                ("resonator_softchain_beta_sweep BASELINE_HARD=0.65 (fixed-pair "
                 "p1=0/p2=1) vs multihop_consolidation_v1 NAIVE=0.847 (uniform "
                 "p1, p2 over V_P=10) -- SAME V_C, V_P, N, K_SET, 15pp regime "
                 "drift apples-to-oranges; cell author copied 0.65 sanity rail "
                 "without chain-construction match check"),
            ],
            "density_arithmetic": {
                "fixed_pair_n_chains_per_pair": "n_chains (saturated single pair)",
                "uniform_n_chains_per_pair_V_P_10": "n_chains / 90",
                "density_ratio_uniform_vs_fixed_V_P_10": "1/90 = 0.0111",
                "expected_baseline_drift_at_V_P_10": "15pp+ at this density ratio",
            },
            "composes_with": [
                "T3/META_M4_consolidation_K_THRESH_1_writes_answer_tuple_by_construction_saturated",
                "T3/META_M6_NAIVE_baseline_must_be_derived_not_copied_from_prior_cells",
                "T3/META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
            ],
            "validated_by": (
                "resonator_softchain_beta_sweep vs multihop_consolidation_v1 "
                "cross-cell discrepancy; M5 rule codified the methodology "
                "takeaway that became standing rail-discipline."
            ),
            "ledger_row_pre_exists": True,
            "ledger_row_timestamp": 1782398467.5497184,
            "ledger_row_atomized_by": "skunkworks_tier_ruling_cell3_cell4_consolidation_2026-06-25",
            "atom_back_filled_by": ATOMIZED_BY,
            "atom_back_fill_reason": "ledger_row_existed_but_atom_write_step_skipped_in_original_flow_phase3_cert_trail_integrity_back_fill",
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
            "cites": [
                "skunkworks_tier_ruling_cell3_cell4_consolidation_2026-06-25_original",
                "resonator_softchain_beta_sweep_baseline_0p65_fixed_pair",
                "multihop_consolidation_v1_NAIVE_0p847_uniform_pair",
                "Director_routed_back_fill_cert_trail_integrity_2026-06-25",
                "phase3_cert_trail_integrity_atoms_jsonl_ledger_consistency_gap",
            ],
        },
        aliases=[],
    )


# ============================================================================
# Atom 9: META_BARRIER_1_TRIPLE_NEGATIVE
# ============================================================================

def build_atom_meta_barrier_1_triple_negative() -> Atom:
    return Atom(
        id="T3/META_BARRIER_1_TRIPLE_NEGATIVE_substrate_native_multihop_3_for_3_REFUTED_2_hop_ceiling_permanent",
        name=(
            "META BARRIER_1_TRIPLE_NEGATIVE: substrate-native multi-hop "
            "generalization at production-scale random-bipolar isotropic "
            "regime is REFUTED across three independent mechanisms "
            "(consolidation v3 + pointer-chain v2 + WM-scaffolded v1); "
            "2-hop ceiling is substrate-product PERMANENT at this regime"
        ),
        description=(
            "RULE (substrate-product positioning, CERT-neutral META "
            "composition): substrate-native multi-hop generalization at "
            "production-scale random-bipolar isotropic regime is REFUTED "
            "across three independent mechanisms in two days (2026-06-24 "
            "/ 2026-06-25). The 2-hop ceiling is substrate-product "
            "PERMANENT at this regime.\n\n"
            "TRIPLE NEGATIVE (all three atomized):\n"
            "  (1) math::T3/EXP_substrate_multihop_consolidation_v3_proper_"
            "test_heldout_fix_HARD_FAIL\n"
            "      Mechanism: compound-predicate consolidation via K-thresh "
            "gating. Result: consolidated class -> ~0% heldout; "
            "unconsolidated class -> 100% (naive 2hop survives). 0/3 seeds "
            "positive lift on any consolidated class.\n\n"
            "  (2) math::T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_"
            "baseline_rail_fixed_HARD_FAIL\n"
            "      Mechanism: pointer-chain hybrid (external-index-via-"
            "substrate atoms holding pointers). Result: pointer_2hop=0.425 "
            "vs baseline 0.650 = mechanism HURTS by 22pp; depth-retention "
            "10/2=0.0824 (compounding decay).\n\n"
            "  (3) math::T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL\n"
            "      Mechanism: WM-slot scaffold (PFC analog binding cleaned "
            "intermediates). Result: WM_2hop=0.425 (identical to pointer-"
            "chain), WM_10hop=0.035 (matches geometric decay 0.70^10). "
            "Mechanism-equivalent to pointer-chain.\n\n"
            "WHY ALL THREE: each mechanism addresses a DIFFERENT angle of "
            "the multi-hop problem:\n"
            "  - Consolidation: STORE the compound predicate so retrieval "
            "is 1-hop. Failed: at heldout disjoint-s chains, the "
            "consolidator's compound predicate doesn't generalize.\n"
            "  - Pointer-chain: USE substrate atoms as pointer-keys for "
            "external-index-style routing. Failed: per-hop cleanup "
            "fidelity (~0.70) compounds geometrically; not improved by "
            "indirection.\n"
            "  - WM-scaffold: CLEAN per-hop intermediates via WM slot "
            "binding. Failed: WM scaffold reduces to pointer-chain at "
            "production scale; cleanup fidelity is the constraint, not "
            "the scaffold architecture.\n\n"
            "ROOT-CAUSE CONVERGENCE: all three fail because per-hop "
            "cleanup fidelity at random-bipolar isotropic regime is ~0.70 "
            "(geometric decay 0.70^N). No composition-architecture choice "
            "can rescue this -- the constraint is on the substrate "
            "primitive (cleanup), not on the composition.\n\n"
            "SUBSTRATE-PRODUCT IMPLICATION (load-bearing):\n"
            "  Substrate-product definition is unchanged: 2-hop chain-"
            "grade memory + composition + retrieval + audit + uncertainty "
            "+ refuse. Multi-hop reasoning requires:\n"
            "    (a) External scaffold (PFC analog at LLM-level routing) "
            "OR\n"
            "    (b) Feature-share cortical analog (anisotropic encoder, "
            "different cell; substrate-owned encoder Path C lane).\n"
            "  The MOAT story shifts: substrate provides 2-hop chain-grade "
            "+ continual learning + refuse-gate primitives; multi-hop is "
            "delegated to external orchestration. This is consistent with "
            "brain: hippocampal CA3 chain-recall is bounded; PFC + "
            "neocortex do the multi-hop composition.\n\n"
            "WHAT THIS DOES NOT REFUTE (honest scope):\n"
            "  - Multi-hop at OTHER regimes: anisotropic encoder (Path C), "
            "structured corpus, learned attention over compound predicates "
            "or pointer keys. The triple-negative is specific to random-"
            "bipolar isotropic at production scale.\n"
            "  - Semantic consolidation under feature-share cortical "
            "analog: different cell, untested in this triple-negative.\n"
            "  - WM primitive (single-slot): working_memory_hrr_slots_"
            "PRODUCTION_v1 is chain-grade for K<=32; WM-scaffold failure "
            "is on multi-hop composition, not on WM itself.\n"
            "  - External-scaffold-routed multi-hop: substrate-product can "
            "still do multi-hop via LLM-orchestrated routing of 2-hop "
            "substrate calls; this triple-negative refutes substrate-native "
            "multi-hop, not orchestrated.\n\n"
            "RAIL-DISCIPLINE LATERAL COMPOSITION: composes with the rail-"
            "discipline triple (META_M2 + META_M5 + META_M6) which provide "
            "the methodology-side closure (rail-derivation provenance + "
            "regime-match + chain-construction match) for HOW to verify "
            "negative findings without rail-induced confound. The "
            "BARRIER_1_TRIPLE_NEGATIVE is the SCIENTIFIC-side closure of "
            "the same arc: three independent mechanism HARD_FAILs all "
            "verified clean of rail-induced confound (per-class smoking "
            "guns on consolidation v3; mechanism-equivalence on pointer-"
            "chain v2 vs WM-scaffold; M6 rail-derivation discipline "
            "applied throughout).\n\n"
            "TIER: META composition rule (CERT-neutral, delta=0). Counts "
            "as a substrate-product permanent classification for the "
            "operating envelope tested."
        ),
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": "META_RULE_CERT_NEUTRAL",
            "cert_status": "meta_rule",
            "cert_class": "discipline_meta",
            "rule_id": "BARRIER_1_TRIPLE_NEGATIVE",
            "rule_category": "substrate_product_permanent_classification",
            "rule_name": "substrate_native_multihop_3_for_3_REFUTED_2_hop_ceiling_permanent",
            "rule_text": (
                "Substrate-native multi-hop generalization at production-"
                "scale random-bipolar isotropic regime is REFUTED across "
                "three independent mechanisms (compound-predicate "
                "consolidation, pointer-chain hybrid, WM-scaffold). All "
                "three fail because per-hop cleanup fidelity at this "
                "regime is ~0.70 (geometric decay 0.70^N). No composition-"
                "architecture choice rescues this. 2-hop ceiling is "
                "substrate-product permanent at this regime. Multi-hop "
                "reasoning routes via external scaffold (PFC analog at "
                "LLM-level) OR feature-share cortical analog (anisotropic "
                "encoder, different cell)."
            ),
            "rebuttal_check_for_skunkworks_landed_VET": (
                "Future substrate-native multi-hop cells at random-bipolar "
                "isotropic regime: refuse-dispatch per Fix #26 (recent "
                "HARD_FAIL re-dispatch forbidden) UNLESS revision is "
                "fundamentally different (anisotropic encoder, structured "
                "corpus, learned attention). Default rule: route to "
                "anisotropic-encoder lane (Path C) for revival angles."
            ),
            "triple_negative_atoms": [
                "math::T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL",
                "math::T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_HARD_FAIL",
                "math::T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL",
            ],
            "root_cause_convergence": (
                "All three fail because per-hop cleanup fidelity at random-"
                "bipolar isotropic regime is ~0.70 (geometric decay 0.70^N). "
                "Constraint is on substrate primitive (cleanup), not on "
                "composition architecture."
            ),
            "per_hop_survival_ratio_at_isotropic_regime": 0.70,
            "regime": "random_bipolar_isotropic_N_8192",
            "substrate_product_implication": (
                "Substrate-product definition unchanged: 2-hop chain-grade "
                "+ composition + retrieval + audit + uncertainty + refuse. "
                "Multi-hop requires external PFC-analog scaffold OR "
                "feature-share cortical analog (anisotropic encoder)."
            ),
            "rail_discipline_lateral_composition": (
                "Composes with META_M2 + META_M5 + META_M6 (rail-discipline "
                "triple) which provide methodology-side closure. The "
                "BARRIER_1_TRIPLE_NEGATIVE is the scientific-side closure "
                "of the same arc."
            ),
            "composes_with": [
                "T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL",
                "T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_HARD_FAIL",
                "T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL",
                "T3/META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
                "T3/META_M4_consolidation_K_THRESH_1_writes_answer_tuple_by_construction_saturated",
                "T3/META_M5_cross_cell_baseline_compare_requires_chain_construction_match",
                "T3/META_M6_NAIVE_baseline_must_be_derived_not_copied_from_prior_cells",
            ],
            "honest_scope": (
                "Triple-negative is specific to random-bipolar isotropic "
                "regime at production scale (V_C=200-600, V_P=2-10, N=8192, "
                "K_SET=20). Does NOT refute multi-hop at OTHER regimes "
                "(anisotropic encoder, structured corpus, learned "
                "attention) or via external orchestration. Does NOT refute "
                "WM as a primitive (single-slot WM is chain-grade for "
                "K<=32). Does NOT refute semantic consolidation under "
                "feature-share cortical analog (different cell)."
            ),
            "revival_angles_for_research": [
                "anisotropic_encoder_Path_C_lane_substrate_owned",
                "structured_corpus_with_learned_attention_over_compound_predicates",
                "consolidator_as_AUGMENTATION_not_replacement_ensemble_with_naive",
                "WM_with_per_hop_confidence_gating_refuse_when_slot_low_confidence",
                "external_orchestrator_PFC_analog_routes_2_hop_substrate_calls",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "era": "comprehensive_program_phase3_glassbox",
            "cites": [
                "consolidation_v3_HARD_FAIL_atomized_this_batch_2026-06-25",
                "pointer_chain_v2_HARD_FAIL_atomized_morning_2026-06-25",
                "wm_scaffolded_v1_HARD_FAIL_atomized_this_batch_2026-06-25",
                "rail_discipline_triple_META_M2_M5_M6_methodology_closure",
                "Fix_26_recent_HARD_FAIL_re_dispatch_forbidden_unless_fundamentally_different",
                "USER_quote_back_fill_prevents_rediscovery_2026-06-25",
                "Director_routed_back_fill_cert_trail_integrity_2026-06-25",
                "Substrate_product_MOAT_2_hop_chain_grade_plus_continual_learning_plus_refuse",
                "Multi_hop_routes_to_external_orchestration_brain_PFC_CA3_analog",
            ],
        },
        aliases=[],
    )


# ============================================================================
# Main: A5-gated batch write
# ============================================================================

def main() -> int:
    store = PartitionedStore(STORE_ROOT)

    # ---- PRE snapshot ----
    pre_stats = store.stats()
    pre_parts = pre_stats.get('partitions', {})
    pre_math = pre_parts.get('math', {}).get('n_atoms', 0)
    pre_meta = pre_parts.get('meta', {}).get('n_atoms', 0)

    from tools.cert_ledger_writer import _cert_count, _axiom_count, _cap_pres_ok
    pre_cert = _cert_count(store)
    pre_ax = _axiom_count(store)
    pre_cap = _cap_pres_ok()

    print("=" * 72)
    print("BACK-FILL BATCH 2026-06-25 -- A5-gated 9-item atomize")
    print("=" * 72)
    print("PRE-snapshot:")
    print(f"  total_atoms: {pre_stats.get('total_atoms')}")
    print(f"  math.n_atoms: {pre_math}")
    print(f"  meta.n_atoms: {pre_meta}")
    print(f"  CERT N: {pre_cert}")
    print(f"  axiom: {pre_ax}")
    print(f"  cap_pres: {'6/6' if pre_cap else 'FAIL'}")
    assert pre_ax == 206, f"PRE axiom drift: {pre_ax} != 206"
    assert pre_cap, "PRE cap_pres FAIL"
    print()

    # ---- Build all atoms ----
    atoms_to_write = [
        # (atom, expected cert_status for round-trip verify, ledger row builder kw)
        (
            build_atom_consolidation_v3_hard_fail(),
            "honest_negative",
            "math",
            {
                "builder": "honest_negative",
                "delta": 0,
                "cell_commit": "subconsv3-heldout-fix",
                "verdict_short": "HARD_FAIL_consolidation_v3_heldout_fix",
                "metrics_path": METRICS_CONS_V3,
                "cert_class": "pre_reg_miss_proven_bound",
                "note": "consolidation_v3_HARD_FAIL_back_fill_2026-06-25",
            },
        ),
        (
            build_atom_wm_scaffolded_hard_fail(),
            "honest_negative",
            "math",
            {
                "builder": "honest_negative",
                "delta": 0,
                "cell_commit": "wm_scaffolded_v1_full",
                "verdict_short": "HARD_FAIL_WM_scaffolded_v1",
                "metrics_path": METRICS_WM,
                "cert_class": "pre_reg_miss_proven_bound",
                "note": "wm_scaffolded_v1_HARD_FAIL_back_fill_2026-06-25",
            },
        ),
        (
            build_atom_refuse_gate_v2_chain_grade(),
            "chain_grade",
            "math",
            {
                "builder": "chain_grade",
                "delta": 1,
                "cell_commit": "refuse_gate_v2_full",
                "verdict_short": "HARD_PASS_BOTH_WORK_refuse_gate_v2_chain_grade_audit_relation_check",
                "metrics_path": METRICS_REFUSE_V2,
                "cv": 0.000,
                "cert_class": "pre_reg_pass",
                "note": "refuse_gate_v2_chain_grade_second_axis_audit_device_back_fill_2026-06-25",
            },
        ),
        (
            build_atom_capacity_sweet_spot_v1_mm(),
            "measured_mechanism",
            "math",
            {
                "builder": "mm",
                "delta": 0,
                "cell_commit": "capacity_sweet_spot_v1_cpu_v1",
                "verdict_short": "MM_capacity_sweet_spot_v1_SKUNKWORKS_OVERRIDE_selector_degenerate",
                "metrics_path": METRICS_CAPACITY_V1,
                "note": "capacity_sweet_spot_v1_MM_OVERRIDE_back_fill_2026-06-25",
            },
        ),
        (
            build_atom_per_cluster_stratified_smoke_mm(),
            "measured_mechanism",
            "math",
            {
                "builder": "mm",
                "delta": 0,
                "cell_commit": "per_cluster_stratified_random_control_v1_smoke",
                "verdict_short": "MM_per_cluster_stratified_smoke_SKUNKWORKS_OVERRIDE_smoke_n1",
                "metrics_path": METRICS_PCLUSTER_SMOKE,
                "note": "per_cluster_stratified_smoke_MM_OVERRIDE_back_fill_2026-06-25",
            },
        ),
        (
            build_atom_sparse_onset_higher_loads_mm(),
            "measured_mechanism",
            "math",
            {
                "builder": "mm",
                "delta": 0,
                "cell_commit": "sparse_onset_higher_loads_followup_v1",
                "verdict_short": "MM_sparse_onset_higher_loads_followup_v1_alpha_c_boundary_refinement",
                "metrics_path": METRICS_SPARSE_ONSET,
                "note": "sparse_onset_higher_loads_MM_back_fill_2026-06-25",
            },
        ),
        (
            build_atom_meta_m4_consolidation_kthresh_1_saturation(),
            "meta_rule",
            "meta",
            {
                "builder": "skip_ledger",  # ledger row already exists
                "delta": 0,
                "cell_commit": None,
                "verdict_short": None,
                "metrics_path": None,
                "note": "META_M4_atom_back_fill_ledger_row_pre_exists_idempotency_skip_2026-06-25",
            },
        ),
        (
            build_atom_meta_m5_cross_cell_chain_construction_match(),
            "meta_rule",
            "meta",
            {
                "builder": "skip_ledger",  # ledger row already exists
                "delta": 0,
                "cell_commit": None,
                "verdict_short": None,
                "metrics_path": None,
                "note": "META_M5_atom_back_fill_ledger_row_pre_exists_idempotency_skip_2026-06-25",
            },
        ),
        (
            build_atom_meta_barrier_1_triple_negative(),
            "meta_rule",
            "meta",
            {
                "builder": "meta_composition",
                "delta": 0,
                "cell_commit": ATOMIZED_BY,
                "verdict_short": "META_BARRIER_1_TRIPLE_NEGATIVE_substrate_native_multihop_3_for_3_REFUTED",
                "metrics_path": "META_RULE_no_metrics_path",
                "note": "META_BARRIER_1_TRIPLE_NEGATIVE_composition_consolidation_v3_pointer_chain_v2_wm_scaffolded_back_fill_2026-06-25",
            },
        ),
    ]

    # ---- Collision check (idempotency) ----
    print("Collision check (idempotency):")
    for atom, expected_status, corpus_name, _ in atoms_to_write:
        qid = f"{atom.corpus.value}::{atom.id}"
        exists = store.has_atom(qid)
        print(f"  {qid}  exists={exists}")
    print()

    # ---- Atom writes (skip if exists) ----
    print("Writing atoms (skip if exists)...")
    write_count = 0
    skip_count = 0
    for atom, expected_status, corpus_name, ledger_meta in atoms_to_write:
        qid = f"{atom.corpus.value}::{atom.id}"
        if store.has_atom(qid):
            print(f"  SKIP (exists): {qid}")
            skip_count += 1
        else:
            store.add_atom(atom, source=ATOMIZED_BY, note=ledger_meta["note"])
            print(f"  WROTE: {qid}")
            write_count += 1
    print(f"  Wrote {write_count}, skipped {skip_count} of {len(atoms_to_write)} atoms.")
    print()

    # ---- Verify-load round-trip ----
    print("Verify-load round-trip (fresh PartitionedStore from disk)...")
    store2 = PartitionedStore(STORE_ROOT)
    for atom, expected_status, corpus_name, _ in atoms_to_write:
        qid = f"{atom.corpus.value}::{atom.id}"
        loaded = store2.get_atom(qid)
        if loaded is None:
            print(f"FATAL: round-trip load failed for {qid}")
            return 3
        loaded_status = loaded.metadata.get("cert_status")
        if loaded_status != expected_status:
            print(f"FATAL: cert_status mismatch on {qid}: got {loaded_status!r}, expected {expected_status!r}")
            return 3
        print(f"  {qid} round-trip OK (cert_status={loaded_status})")
    print()

    # ---- POST snapshot ----
    post_stats = store2.stats()
    post_parts = post_stats.get('partitions', {})
    post_math = post_parts.get('math', {}).get('n_atoms', 0)
    post_meta = post_parts.get('meta', {}).get('n_atoms', 0)
    post_cert = _cert_count(store2)
    post_ax = _axiom_count(store2)
    post_cap = _cap_pres_ok()
    print("POST-snapshot:")
    print(f"  total_atoms: {post_stats.get('total_atoms')}")
    print(f"  math.n_atoms: {post_math}  (delta {post_math - pre_math:+d})")
    print(f"  meta.n_atoms: {post_meta}  (delta {post_meta - pre_meta:+d})")
    print(f"  CERT N: {post_cert}  (delta {post_cert - pre_cert:+d}; expected +1 for refuse_gate v2)")
    print(f"  axiom: {post_ax}")
    print(f"  cap_pres: {'6/6' if post_cap else 'FAIL'}")
    assert post_ax == 206, f"POST axiom drift: {post_ax} != 206"
    assert post_cap, "POST cap_pres FAIL"
    print()

    # ---- Cert ledger writes ----
    # Only for items whose ledger row does NOT already exist (skip META_M4, META_M5).
    #
    # CERT-N invariant for ledger phase: atom-writes have ALREADY changed live CERT N
    # (atom add for refuse_gate_v2 chain_grade is what moved CERT N from 594 -> 595).
    # The ledger row is a RECORD of that prior cert change; the `cert_increment_delta`
    # in the row body is the HISTORICAL delta. Live CERT N does NOT change between
    # ledger writes (only Store add_atom changes it). So expected_pre and expected_post
    # for each ledger append are BOTH the current post-atom-write CERT N (= post_cert).
    print("Appending cert_ledger rows...")
    ledger_writes = 0
    ledger_skips = 0
    for atom, _, _, ledger_meta in atoms_to_write:
        qid = f"{atom.corpus.value}::{atom.id}"
        builder = ledger_meta["builder"]
        if builder == "skip_ledger":
            print(f"  SKIP LEDGER (pre-exists): {qid}")
            ledger_skips += 1
            continue

        delta = ledger_meta["delta"]
        cell_commit = ledger_meta["cell_commit"]
        verdict_short = ledger_meta["verdict_short"]
        metrics_path = ledger_meta["metrics_path"]
        note = ledger_meta["note"]

        if builder == "honest_negative":
            row = build_honest_negative_row(
                atom_id=qid,
                cell_commit=cell_commit,
                verdict=verdict_short,
                notes_path=NOTES_PATH,
                metrics_path=metrics_path,
                cert_class=ledger_meta.get("cert_class", "pre_reg_miss_proven_bound"),
                atomized_by=ATOMIZED_BY,
                note=note,
            )
        elif builder == "chain_grade":
            row = build_chain_grade_ruling_row(
                atom_id=qid,
                cell_commit=cell_commit,
                verdict=verdict_short,
                notes_path=NOTES_PATH,
                metrics_path=metrics_path,
                cv=ledger_meta.get("cv"),
                cert_class=ledger_meta.get("cert_class", "pre_reg_pass"),
                atomized_by=ATOMIZED_BY,
                note=note,
            )
        elif builder == "mm":
            row = build_measured_mechanism_row(
                atom_id=qid,
                cell_commit=cell_commit,
                verdict=verdict_short,
                notes_path=NOTES_PATH,
                metrics_path=metrics_path,
                atomized_by=ATOMIZED_BY,
                note=note,
            )
        elif builder == "meta_composition":
            # Hand-built meta_rule row (use measured_mechanism cert_status + discipline_meta
            # cert_class, per Cell 2 v5 / cell3_cell4 atomize precedent for META rules in
            # ledger; atom-level cert_status='meta_rule' preserved in atoms.jsonl)
            row = {
                "ts": None,
                "op": "cert_ruling",
                "atom_id": qid,
                "cert_status": "measured_mechanism",
                "cert_class": "discipline_meta",
                "verified_off_data": True,
                "atomized_by": ATOMIZED_BY,
                "cell_commit": cell_commit,
                "verdict": verdict_short,
                "cert_increment_delta": delta,
                "cv": None,
                "referent_pointer": {
                    "notes_path": NOTES_PATH,
                    "metrics_path": metrics_path,
                    "atom_qualified_id": qid,
                },
                "supersedes": None,
                "note": note,
            }
        else:
            raise ValueError(f"unknown builder {builder!r} for {qid}")

        # Live CERT N already reflects the atom-write changes; ledger is record-keeping
        h = append_cert_ledger_row(
            row,
            expected_cert_n_pre=post_cert,
            expected_cert_n_post=post_cert,
        )
        print(f"  Ledger row for {qid}: hash={h}  historical_delta={delta:+d}  (live CERT N stable at {post_cert})")
        ledger_writes += 1

    print(f"  Wrote {ledger_writes} ledger rows, skipped {ledger_skips} (pre-exist).")
    print()

    # ---- Summary ----
    print("=" * 72)
    print("A5 BACK-FILL BATCH COMPLETE")
    print("=" * 72)
    print(f"Atoms landed: {write_count}/{len(atoms_to_write)} (skipped {skip_count} as pre-existing)")
    print(f"Ledger rows added: {ledger_writes} (skipped {ledger_skips} as pre-existing)")
    print(f"CERT N: {pre_cert} -> {post_cert}  (delta {post_cert - pre_cert:+d})")
    print(f"axiom: {post_ax} (stable at 206)")
    print(f"cap_pres: {'6/6' if post_cap else 'FAIL'}")
    print()
    print("Q-discipline overrides applied (Skunkworks):")
    print("  capacity_sweet_spot_v1   chain_grade -> MEASURED_MECHANISM (selector degenerate)")
    print("  per_cluster_stratified   chain_grade -> MEASURED_MECHANISM (smoke + n_seeds=1)")
    print()
    print("Verify-the-referent caught (Skunkworks):")
    print("  NESS envelope - already in Store + ledger (Director re-audit miss)")
    print()
    print("Path-scoped commit pattern (caller-side):")
    print("  git add -f data/substrate_index/math/atoms.jsonl")
    print("  git add -f data/substrate_index/meta/atoms.jsonl")
    print("  git add -f data/substrate_index/meta/cert_ledger.jsonl")
    print("  git add notes/skunkworks_back_fill_batch_2026-06-25.md")
    print("  git add tools/skunkworks_back_fill_batch_2026-06-25.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
