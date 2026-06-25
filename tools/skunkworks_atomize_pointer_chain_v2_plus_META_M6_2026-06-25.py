"""Skunkworks 2026-06-25 -- A5 atomize pointer-chain v2 HARD_FAIL + META_M6.

TIER RULING NOTE: notes/skunkworks_tier_ruling_pointer_chain_v2_plus_META_M6_2026-06-25.md

Queue (per Director-routed bounded task):

1. math::T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_HARD_FAIL
   HARD_FAIL / honest_negative; cert_increment_delta = 0
   Tier: HARD_FAIL (proven bound; Barrier 1 substrate-native multi-hop closure REFUTED
   via second mechanism after consolidation v3 HARD_FAIL same day).
   Verified off per_seed: baseline mean=0.650 (1/3 seeds out-of-band low: seed7=0.605),
   pointer 2hop mean=0.425 (cv=0.107 -> CV_FAIL), depth_retention 10/2=0.0824 (FAIL >=0.80),
   POINTER 2hop -0.225 BPC below baseline (mechanism HURTS).
   Zero LLM calls at inference verified across all 3 seeds.

2. meta::T3/META_M6_NAIVE_baseline_must_be_derived_not_copied_from_prior_cells
   META rule; CERT-neutral (delta=0)
   Three cells in two weeks (v1/v2/v3 consolidation + pointer-chain v2) where NAIVE
   sanity bands were copied across cells without re-deriving from CURRENT regime
   parameters (V_C, V_P, n_chains, chain-class structure). Composes with M2 + the
   cert-ladder upgrade-path discipline set + the prior Cell 2 v5 META_CROSS_N
   upgrade rule.

3. (HOLD) META smoke-vs-full discriminator (n_chains floor):
   Director proposed atomization. Off-data verify CAUGHT a confound: pointer-chain
   v2 smoke ran at BOTH reduced N (2048 vs 8192) AND reduced pointer_n_chains
   (50 vs 200) -- so the smoke-vs-full sign-flip is attributable to EITHER
   N capacity OR n_chains density (or both). The Director's framing "n_chains-floor"
   is single-cell evidence AND the single cell is regime-confounded.
   PER ROLE-DISCIPLINE (Q-discipline + symmetric anti-inflation): DO NOT ATOMIZE
   META_3 yet. Instead, document the candidate META in the tier-ruling note for
   exp_dev pickup + second-cell confirmation. The TWO-VARIABLE smoke-vs-full
   discrepancy is a stronger discipline candidate (smoke regime MUST match full
   along EVERY capacity-sensitive dimension, not just one).

DISCIPLINES HONORED:
  - Verify-off-data: every cited number recomputed from per_seed.
  - Verify-the-referent: existing META_M2 (atomized), META_M4/M5 (LEDGER-ONLY gap
    flagged), pointer_chain Store ref (T3/EXP_pointer_chain UNVERIFIED unmapped
    verdict, not chain-grade ref).
  - Q-discipline: SUSPECT 1.000 results: smoke POINTER=0.98 + HARD_PASS framing
    at toy n_chains=50 N=2048 1-seed gets flagged as suspect; full-scale rules.
  - Fix #28 default under-claim: META_3 deferred to pending second-cell.
  - Cited number reproduces: 0.650, 0.425, 0.107, 0.0350, 0.0824 all verified.
  - Idempotency: skip atoms already present.
  - A5 PRE/POST snapshot; round-trip verify.
  - Foreground execution (Fix #20); no subprocess pipes.
  - Path-scoped commits (Director will commit afterward).
  - ASCII only.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path("D:/AI/hd-instrument").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_honest_negative_row,
)


STORE_ROOT = Path("D:/AI/hd-instrument/data/substrate_index")
ATOMIZED_BY = "skunkworks_atomize_pointer_chain_v2_plus_META_M6_2026-06-25"
NOTES_PATH_RULING = "notes/skunkworks_tier_ruling_pointer_chain_v2_plus_META_M6_2026-06-25.md"
METRICS_PATH_V2 = "data/exp_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed/metrics.json"


# ============================================================================
# Atom 1 -- pointer-chain v2 HARD_FAIL
# ============================================================================

def build_atom_pointer_chain_v2_hard_fail() -> Atom:
    return Atom(
        id="T3/EXP_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_HARD_FAIL",
        name=(
            "Substrate multihop pointer-chain hybrid v2 BASELINE_RAIL_FIXED -- "
            "HARD_FAIL (POINTER_2HOP=0.425 vs baseline 0.650 = -22pp HURTS; "
            "depth-retention 0.08; second substrate-native multi-hop closure "
            "REFUTED same day as consolidation v3; Barrier 1 double-negative)"
        ),
        description=(
            "Substrate-native multi-hop closure attempt via pointer-chain "
            "hybrid (external-index-style routing via substrate atoms holding "
            "pointers, retrieved via HRR cleanup). Designed to escape the "
            "compositional bind/cleanup chain that consolidation v3 (HARD_FAIL "
            "same day) refuted. v2 fixed v1's baseline rail-miss by using "
            "beta-sweep's EXACT regime (V_P=2 fixed p1=0/p2=1, n_chains=200, "
            "chain_naive_hard mechanism, separate W matrices). Bands at v2 "
            "pre-reg: HP_pointer_2hop>=0.95 AND HP_hybrid>=0.85 AND HP_cv<=0.05 "
            "AND HP_depth_retention(10/2)>=0.80; HF_top1<=0.75; baseline sanity "
            "[0.62, 0.68] on majority of seeds.\n\n"
            "PER-ARM (3 seeds [7, 17, 23], independently recomputed off per_seed):\n"
            "  arm_baseline_hrr_2hop     mean=0.6500  per_seed=[0.605, 0.670, 0.675]\n"
            "                            pstdev=0.0319  cv=0.0491\n"
            "  arm_pointer_chain_2hop    mean=0.4250  per_seed=[0.485, 0.375, 0.415]\n"
            "                            pstdev=0.0455  cv=0.1070  (FAILS HP_cv<=0.05)\n"
            "  arm_pointer_chain_5hop    mean=0.1217  per_seed=[0.145, 0.110, 0.110]\n"
            "  arm_pointer_chain_10hop   mean=0.0350  per_seed=[0.040, 0.035, 0.030]\n"
            "  arm_pointer_hrr_hybrid    mean=0.4250  per_seed=[0.485, 0.375, 0.415]\n"
            "                            (identical to pointer 2hop -- hybrid adds 0 lift)\n\n"
            "KEY LIFTS (paired same-N, same-regime; substrate-product framing):\n"
            "  pointer_2hop - baseline = 0.425 - 0.650 = -0.2250  (mechanism HURTS by 22pp)\n"
            "  depth_retention(10/2)   = 0.035 / 0.425 = 0.0824   (FAILS HP >=0.80)\n"
            "  hybrid - pointer_2hop   = 0.000              (hybrid path adds 0)\n\n"
            "RAILS FIRED:\n"
            "  SANITY_BREACH(1/3 seeds baseline_mean=0.605 out of [0.62, 0.68])\n"
            "  HP_break=False (0.425 << 0.95 floor)\n"
            "  cv_ok=False (0.1070 >> 0.05 cap)\n"
            "  depth_ret=False (0.0824 << 0.80 floor)\n"
            "  HF_top1<=0.75 fired at pointer_2hop 0.425\n\n"
            "PER-STEP ACCURACY (chain decay structure, seed 7):\n"
            "  d=2:  [0.69, 0.485]                      (per-hop survival ~0.70)\n"
            "  d=5:  [0.69, 0.485, 0.31, 0.205, 0.145]  (geometric decay continues)\n"
            "  d=10: [0.69, 0.485, 0.31, 0.205, 0.145, 0.1, 0.07, 0.065, 0.04, 0.04]\n"
            "  per-hop survival ratio ~0.70, compounding to 0.70^10 ~ 0.028 -> matches\n"
            "  observed 0.035 at d=10. Depth decay is DETERMINISTIC chain-cleanup\n"
            "  attenuation; not improved by pointer-chain hybrid over naive HRR.\n\n"
            "ZERO-LLM-CALLS-AT-INFERENCE: verified per_seed (n_llm=0 across all 3\n"
            "seeds + cell-level counter); substrate-only-decode gate PASSES.\n\n"
            "SMOKE-VS-FULL DIVERGENCE (Director Fix #28 flag investigated off-data):\n"
            "  SMOKE: POINTER_2HOP=0.98 baseline=0.645 hybrid=0.98 -- HARD_PASS_BREAK_CEILING\n"
            "  FULL:  POINTER_2HOP=0.425 baseline=0.650 hybrid=0.425 -- HARD_FAIL\n"
            "  Director attribution: 'chain-count-sensitive mechanism (n_chains 50 -> 200)'\n"
            "  CERT-OWNER off-data finding: smoke ran at N=2048 (full N=8192) AND\n"
            "  pointer_n_chains=50 (full 200) AND 1 seed (full 3 seeds). The sign-flip\n"
            "  is regime-confounded across THREE dimensions (capacity-N reduced 4x +\n"
            "  density-pointer-chains reduced 4x + seed-pool reduced 3x). Cannot\n"
            "  attribute to a single dimension from this single cell; the FULL-SCALE\n"
            "  ruling is the load-bearing measurement. The DISCIPLINE candidate\n"
            "  (smoke regime must match full along every capacity-sensitive dim) is\n"
            "  documented in the tier-ruling note for second-cell confirmation\n"
            "  (deferred from META atomization per Fix #28 default under-claim).\n\n"
            "BARRIER 1 CONTEXT (double-negative same day):\n"
            "  Two substrate-native multi-hop closure mechanisms tested same day:\n"
            "    (1) consolidation v3 (HARD_FAIL same day; ruling notes/ already\n"
            "        filed; INTEGRITY GAP: not yet in atoms.jsonl or cert_ledger.jsonl\n"
            "        -- flagged for Director-routed back-fill)\n"
            "    (2) pointer-chain hybrid v2 (THIS cell, HARD_FAIL)\n"
            "  Together these refute substrate-native multi-hop generalization at\n"
            "  production-scale random-bipolar isotropic regime (V_C=200 V_P=2 N=8192\n"
            "  K_SET=20, the beta-sweep baseline regime). This is the load-bearing\n"
            "  negative for L2 encoder pivot per Director's strategic synthesis\n"
            "  notes/research_barrier1_double_negative_substrate_product_definition_\n"
            "  2026-06-25.md. The substrate-product definition is unchanged: 2-hop\n"
            "  chain-grade memory + composition + retrieval + audit; multi-hop\n"
            "  reasoning requires external scaffold (PFC analog) OR semantic\n"
            "  consolidation under feature-share cortical analog (different cell).\n\n"
            "WHY HARD_FAIL NOT MEASURED_MECHANISM (Q-discipline check):\n"
            "  - Pre-reg bands were CONCRETE and PRE-SPECIFIED at config_version\n"
            "    (HP_pointer_2hop>=0.95, HP_cv<=0.05, HP_depth_retention>=0.80).\n"
            "    All FAILED with concrete margin (0.425 vs 0.95 = 0.45 BPC margin;\n"
            "    cv 0.107 vs 0.05 = 2.1x over cap; depth_ret 0.0824 vs 0.80 = 0.72\n"
            "    margin).\n"
            "  - SANITY rail had 1/3 seed breach but the breach DIRECTION is\n"
            "    downward (seed 7 baseline = 0.605 BELOW band, not above) -- so the\n"
            "    BASELINE mean = 0.650 is at the MIDPOINT of expected band. Even if\n"
            "    we re-derived the baseline more generously (e.g., 0.60-0.70 band),\n"
            "    POINTER 0.425 still UNDER-PERFORMS baseline by ~22pp. The rail\n"
            "    miss does NOT mask a direction-correct mechanism signal beneath.\n"
            "  - HYBRID arm identical to pointer_2hop arm (both 0.425) shows the\n"
            "    'hybrid' addition adds zero discriminative information. This is\n"
            "    not 'instrument-bug-MM' -- it is 'mechanism-add-no-value' which\n"
            "    is honest negative.\n"
            "  - Per-step accuracy structure (0.69 / 0.485 / 0.31 / 0.205 / 0.145\n"
            "    geometric decay) is consistent with FUNDAMENTAL chain-cleanup\n"
            "    attenuation, not an implementation bug. The mechanism CAN be\n"
            "    measured (no NaN spokes, no readout-degeneration); it MEASURES\n"
            "    its own failure cleanly.\n\n"
            "WHAT THIS DOES NOT SHOW (honest scope):\n"
            "  - Does NOT test pointer-chain at OTHER regimes (anisotropic encoder,\n"
            "    structured corpus, higher N capacity). Substrate-native multi-hop\n"
            "    via pointer-chain may yet work under anisotropic encoder or with\n"
            "    learned attention over pointer keys.\n"
            "  - Does NOT test the prior Store ref T3/EXP_pointer_chain (status\n"
            "    UNVERIFIED, verdict null) at chain-grade rigor. That ref is at\n"
            "    a different regime (max_d=100 with d_50_by_n at toy scales);\n"
            "    not a chain-grade baseline.\n"
            "  - Does NOT refute semantic-consolidation under feature-share (Option\n"
            "    C in Director's strategic synthesis); only refutes episodic\n"
            "    compound-predicate + pointer-chain hybrid mechanisms.\n"
            "  - Does NOT test pointer-chain at depth <2 (single-hop is the existing\n"
            "    chain-grade primitive).\n\n"
            "TIER: HARD_FAIL / honest_negative; delta=0 (proven NEGATIVE bound).\n"
            "Counts as a proven negative result for Barrier 1 substrate-native\n"
            "multi-hop closure via pointer-chain hybrid mechanism."
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
                "HARD_FAIL_pointer_chain_hybrid_v2_baseline_rail_fixed_3seeds_"
                "7_17_23_N_8192_V_C_200_V_P_2_K_SET_20_n_chains_200_baseline_"
                "mean_0p650_pstdev_0p032_cv_0p049_sanity_breach_1of3_seed7_"
                "0p605_pointer_2hop_mean_0p425_cv_0p107_FAILS_HP_pointer_2hop_"
                "0p95_FAILS_HP_cv_0p05_HF_top1_0p75_FIRED_lift_minus_0p225_BPC_"
                "below_baseline_mechanism_HURTS_22pp_hybrid_mean_0p425_identical_"
                "to_pointer_2hop_zero_lift_depth_retention_10over2_0p0824_FAILS_"
                "HP_0p80_geometric_decay_per_hop_survival_0p70_compounding_to_"
                "0p70_to_10_eq_0p028_matches_observed_0p035_zero_LLM_calls_"
                "verified_per_seed_substrate_only_decode_PASSES_smoke_vs_full_"
                "sign_flip_attributable_to_3_regime_confounds_N_2048_vs_8192_"
                "pointer_n_chains_50_vs_200_seed_pool_1_vs_3_NOT_pure_n_chains_"
                "barrier_1_double_negative_same_day_consolidation_v3_HARD_FAIL_"
                "plus_pointer_chain_v2_HARD_FAIL_substrate_native_multihop_via_"
                "compound_predicate_or_pointer_hybrid_REFUTED_at_random_bipolar_"
                "isotropic_regime_load_bearing_for_L2_encoder_pivot"
            ),
            "cell_commit": "v2_baseline_rail_fixed",
            "metrics_path": METRICS_PATH_V2,
            "prereg_path": None,
            "notes_path": NOTES_PATH_RULING,
            "verified_off_data": (
                "Cert-owner read per_seed directly from metrics.json via .venv "
                "recompute (NOT verdict_msg framing). Per-seed baseline: [0.605, "
                "0.670, 0.675] -> mean 0.6500 pstdev 0.0319 cv 0.0491. Per-seed "
                "pointer_2hop: [0.485, 0.375, 0.415] -> mean 0.4250 pstdev 0.0455 "
                "cv 0.1070 (FAILS HP_cv<=0.05). Per-seed pointer_5hop: [0.145, "
                "0.110, 0.110] -> mean 0.1217. Per-seed pointer_10hop: [0.040, "
                "0.035, 0.030] -> mean 0.0350. Depth retention: 0.0350 / 0.4250 "
                "= 0.0824 (FAILS HP >= 0.80). Hybrid arm identical to pointer_2hop "
                "(both [0.485, 0.375, 0.415]) -> mean 0.4250. Zero-LLM-calls: "
                "verified per per_seed[0/1/2]._llm_forward_calls_at_inference=0 "
                "and cell-level=0. Per-step accuracy seed 7 read directly from "
                "per_seed[0].arm_pointer_chain_10hop.per_step_acc: [0.69, 0.485, "
                "0.31, 0.205, 0.145, 0.1, 0.07, 0.065, 0.04, 0.04]. Per-hop "
                "survival ~0.70; compounding 0.70^10 ~ 0.028; matches observed "
                "0.035 (deterministic chain-cleanup attenuation, not implementation "
                "bug). Smoke metrics independently verified at data/exp_substrate_"
                "multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_smoke/"
                "metrics.json: N=2048 (NOT 8192) AND pointer_n_chains=50 (NOT "
                "200) AND n_seeds=1 (NOT 3); smoke-vs-full sign-flip 3-dimension "
                "regime-confounded, NOT pure n_chains-sensitivity."
            ),
            "honest_scope": (
                "HARD_FAIL at the pre-reg band on the pointer-chain hybrid "
                "mechanism at random-bipolar isotropic regime (V_C=200 V_P=2 "
                "N=8192 K_SET=20 n_chains=200 beta-sweep baseline regime). DOES "
                "show mechanism HURTS (-22pp vs naive HRR baseline) AND fails "
                "depth-retention floor (0.08 vs 0.80) AND fails cv (0.107 vs "
                "0.05) AND hybrid adds zero lift. DOES NOT refute pointer-chain "
                "at other regimes (anisotropic encoder, structured corpus, "
                "learned attention over pointer keys, higher N capacity). DOES "
                "NOT test the prior Store ref T3/EXP_pointer_chain (UNVERIFIED, "
                "verdict null, max_d=100 at toy scales -- not a chain-grade "
                "baseline). DOES NOT refute semantic-consolidation under feature-"
                "share (different cell). DOES NOT test depth <2. The smoke-vs-"
                "full divergence is 3-dimension regime-confounded; CANNOT "
                "attribute the sign-flip to a single dimension from this single "
                "cell. Per Fix #28 default under-claim: META smoke-floor "
                "discipline candidate is documented in tier-ruling note for "
                "second-cell confirmation, NOT atomized as a META rule yet."
            ),
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM": 8192,
            "V_C": 200,
            "BASELINE_V_P": 2,
            "BASELINE_N_CHAINS": 200,
            "POINTER_V_P": 10,
            "POINTER_N_CHAINS": 200,
            "K_SET": 20,
            "hop_depths": [2, 5, 10],
            "baseline_mean": 0.6500,
            "baseline_pstdev": 0.0319,
            "baseline_cv": 0.0491,
            "baseline_sanity_band": [0.62, 0.68],
            "baseline_sanity_breach_seeds": 1,
            "baseline_sanity_breach_direction": "downward_seed7_0p605",
            "pointer_2hop_mean": 0.4250,
            "pointer_2hop_pstdev": 0.0455,
            "pointer_2hop_cv": 0.1070,
            "pointer_5hop_mean": 0.1217,
            "pointer_10hop_mean": 0.0350,
            "hybrid_mean": 0.4250,
            "hybrid_minus_pointer_2hop": 0.0000,
            "depth_retention_10_over_2": 0.0824,
            "pointer_lift_over_baseline_bpc": -0.2250,
            "per_hop_survival_ratio_approx": 0.70,
            "per_seed_baseline": [0.605, 0.670, 0.675],
            "per_seed_pointer_2hop": [0.485, 0.375, 0.415],
            "per_seed_pointer_5hop": [0.145, 0.110, 0.110],
            "per_seed_pointer_10hop": [0.040, 0.035, 0.030],
            "per_seed_hybrid": [0.485, 0.375, 0.415],
            "pre_reg_bands": {
                "HP_pointer_2hop_top1": ">=0.95",
                "HP_hybrid_top1": ">=0.85",
                "HP_cv": "<=0.05",
                "HP_depth_retention_10over2": ">=0.80",
                "HF_top1_floor": "<=0.75",
                "baseline_sanity": "[0.62, 0.68] majority of seeds",
            },
            "bands_observed": {
                "HP_pointer_2hop": False,
                "HP_hybrid": False,
                "HP_cv": False,
                "HP_depth_retention": False,
                "HF_floor_fired": True,
            },
            "smoke_vs_full_regime_confounded": True,
            "smoke_regime_diffs_from_full": {
                "N_smoke": 2048,
                "N_full": 8192,
                "N_ratio": 0.25,
                "pointer_n_chains_smoke": 50,
                "pointer_n_chains_full": 200,
                "pointer_n_chains_ratio": 0.25,
                "n_seeds_smoke": 1,
                "n_seeds_full": 3,
                "smoke_verdict": "HARD_PASS_BREAK_CEILING",
                "full_verdict": "HARD_FAIL",
                "smoke_pointer_2hop": 0.98,
                "full_pointer_2hop": 0.425,
            },
            "barrier_1_context": (
                "Second substrate-native multi-hop closure HARD_FAIL same day "
                "as consolidation v3 HARD_FAIL. Together refute substrate-"
                "native multi-hop generalization at production-scale random-"
                "bipolar isotropic regime via either compound-predicate "
                "consolidation OR pointer-chain hybrid mechanisms. Substrate-"
                "product definition unchanged: 2-hop chain-grade memory + "
                "composition + retrieval + audit; multi-hop reasoning requires "
                "external scaffold (PFC analog) OR semantic-consolidation "
                "under feature-share cortical analog (different cell)."
            ),
            "composes_with": [
                "META/CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION",
                "T3/META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
                "META_M4_consolidation_K_THRESH_1_writes_answer_tuple_by_construction_saturated",
                "META_M5_cross_cell_baseline_compare_requires_chain_construction_match",
                "T3/META_M6_NAIVE_baseline_must_be_derived_not_copied_from_prior_cells",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_not_verdict_msg_framing",
                "Fix_28_default_under_claim_meta_smoke_floor_deferred",
                "USER_route_negatives_to_research_2x_3x_revival_drills",
                "verify_referent_smoke_metrics_regime_confound_caught",
                "Director_synthesis_barrier1_double_negative_substrate_product_definition_2026-06-25",
                "Director_2x_drill_consolidation_v3_HARD_FAIL_2026-06-25",
                "consolidation_v3_HARD_FAIL_same_day_companion_atom_INTEGRITY_GAP_flagged",
                "META_M2_tight_rail_companion_atomized_morning_2026-06-25",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
        },
        aliases=[],
    )


# ============================================================================
# Atom 2 -- META_M6: NAIVE-baseline-must-be-derived-not-copied
# ============================================================================

def build_atom_meta_M6_naive_baseline_derivation() -> Atom:
    return Atom(
        id="T3/META_M6_NAIVE_baseline_must_be_derived_not_copied_from_prior_cells",
        name=(
            "META M6: NAIVE-baseline sanity-band must be DERIVED from cell's "
            "CURRENT regime parameters (V_C, V_P, n_chains, chain-class "
            "structure), NOT copied from prior cell's pre-reg without "
            "re-derivation; provenance is not derivation"
        ),
        description=(
            "RULE (cert-discipline, CERT-neutral): pre-reg NAIVE-baseline "
            "sanity-band MUST be DERIVED from the cell's CURRENT regime "
            "parameters (V_C, V_P, n_chains, chain-class structure, K_SET, "
            "N), NOT copied from a prior cell's pre-reg without re-derivation. "
            "Provenance (where the band came from) is NOT derivation (whether "
            "the band is mechanically correct for the current cell).\n\n"
            "RATIONALE: NAIVE baseline at random-bipolar isotropic regime is "
            "a DETERMINISTIC FUNCTION of regime parameters. Per Research 2x "
            "drill on consolidation v3 HARD_FAIL: a rough closed-form is\n"
            "  NAIVE_2hop ~ erf(N / (4 * n_chains * V_P_effective))\n"
            "(valid in K=2 random-bipolar isotropic regime; underestimates at "
            "low density). Different cells changing V_C, V_P, n_chains, or "
            "chain-class structure WILL produce different NAIVE values. "
            "Copying a band from a prior cell with DIFFERENT regime parameters "
            "creates a 'mis-spec'd rail, not a methodology error' situation: "
            "the rail fires (sanity-breach) on the regime drift, masking the "
            "underlying mechanism signal beneath OR creating spurious "
            "HARD_PASS framings on cells that 'beat' a mis-calibrated bar.\n\n"
            "OBSERVED INSTANCES (three cells in two weeks):\n"
            "  (1) consolidation v3 NAIVE=0.850 vs pre-reg band [0.62, 0.68] "
            "(band copied from v2 single-pair regime; v3 has V_P=6 multi-class "
            "structure with separate W; root cause Research 2x drill).\n"
            "  (2) consolidation v1 NAIVE=0.847 vs prior beta-sweep BASELINE_"
            "HARD=0.65 (regime difference V_P=10 uniform vs V_P=2 fixed pair).\n"
            "  (3) pointer-chain hybrid v2 baseline only 2/3 seeds in fixed band "
            "(seed7=0.605 below 0.62 lower bound) even with v2's 'rail fix' to "
            "use beta-sweep's EXACT V_P=2 fixed-pair regime; regime variance "
            "still leaks through at n_seeds=3 (need n_seeds>=10 OR widened "
            "band to absorb seed-level variance at this V_P=2 regime).\n\n"
            "COMPOSES WITH (rail-discipline three-rule set, NEW):\n"
            "  - META_M2 (atomized 2026-06-25): tight rail from DIFFERENT "
            "config can mask direction-correct lift; rule = match referent "
            "config exactly OR widen by capacity-scaling drift.\n"
            "  - META_M5 (LEDGER-ROW only, atom-write gap; flagged): cross-cell "
            "baseline comparisons require chain-construction match, not just "
            "V/N match.\n"
            "  - THIS RULE (META_M6): NAIVE-baseline must be DERIVED from "
            "current-cell regime parameters, NOT copied from prior cell. "
            "Provenance is not derivation.\n\n"
            "The three rules together form the RAIL-DISCIPLINE DERIVATION-PROVENANCE-"
            "REGIME-MATCH set: rails must (a) have explicit derivation "
            "provenance (where did this band come from?), (b) match the "
            "regime they will be evaluated in (V_C, V_P, n_chains, chain-class "
            "structure, K_SET, N, encoder, device), and (c) be DERIVED from "
            "the current cell's parameters at pre-reg time, not copied.\n\n"
            "ALSO COMPOSES WITH the cert-ladder upgrade-path discipline set "
            "(M2 + META_PROSPECTIVE_BANDS_FRESH_SEEDS + META_CROSS_N_"
            "REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION).\n\n"
            "OPERATIONAL FIX (per Research 2x drill recommendation):\n"
            "  Every cell pre-reg with a NAIVE arm MUST include either:\n"
            "    (a) A one-seed NAIVE smoke run at the CURRENT regime BEFORE "
            "full dispatch, with the measured NAIVE value used to SET the "
            "sanity band as measured +/- 0.03, OR\n"
            "    (b) An explicit closed-form derivation of expected NAIVE "
            "from regime parameters, with the band derived as expected +/- "
            "ceiling(expected * 0.05).\n"
            "  Do NOT copy bands from prior cells when ANY of {V_C, V_P, "
            "n_chains, chain-class structure, K_SET, N} changed.\n\n"
            "SCOPE: applies to all cells with a NAIVE / baseline sanity rail "
            "AND a measurable regime parameter set. Does NOT apply to: "
            "(a) within-cell replications at IDENTICAL regime, (b) cells "
            "without a NAIVE arm, (c) cells where the rail is on a different "
            "metric than NAIVE (e.g., HP_break, depth_retention -- those "
            "have their own discipline candidates).\n\n"
            "FALSIFICATION CONDITIONS (when this rule WOULD NOT have prevented "
            "the observed drift):\n"
            "  - If the smoke-run NAIVE itself has high variance at low "
            "n_seeds (e.g., pointer-chain v2 baseline 1/3 breach at n_seeds=3 "
            "is partially seed-noise, not regime mismatch). Mitigation: smoke "
            "n_seeds>=5 OR closed-form derivation.\n"
            "  - If the closed-form is wrong at the current regime (e.g., "
            "single-pair-saturated vs uniform-pair regime differ in density "
            "dynamics). Mitigation: smoke-run takes precedence over closed-"
            "form when they disagree by >0.05.\n"
            "  - If the cell author uses the rule but the rail-derivation "
            "step is itself instrument-bugged (e.g., 1-seed smoke at toy "
            "scale; same regime confounds as pointer-chain v2 smoke vs full). "
            "Mitigation: smoke regime must match full regime along EVERY "
            "capacity-sensitive dimension (candidate META, separate rule).\n\n"
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
            "rule_id": "M6",
            "rule_category": "rail_derivation_provenance",
            "rule_name": "NAIVE_baseline_must_be_derived_not_copied_from_prior_cells",
            "rule_text": (
                "Pre-reg NAIVE-baseline sanity-band MUST be DERIVED from the "
                "cell's CURRENT regime parameters (V_C, V_P, n_chains, chain-"
                "class structure, K_SET, N), NOT copied from a prior cell's "
                "pre-reg without re-derivation. Provenance is NOT derivation. "
                "Operational fix: smoke-run NAIVE arm at n_seeds>=5 at "
                "CURRENT regime + set band as smoke-mean +/- 0.03, OR derive "
                "closed-form expected NAIVE from regime parameters + set band "
                "as expected +/- max(0.03, expected * 0.05)."
            ),
            "rebuttal_check_for_skunkworks_landed_VET": (
                "if cell's NAIVE sanity rail is COPIED from a prior cell AND "
                "ANY of {V_C, V_P, n_chains, chain_class_structure, K_SET, N} "
                "differs from the prior cell: the rail is mis-spec'd. The "
                "sanity-breach IS NOT a methodology bug OR substrate finding; "
                "it is rail-derivation debt. Verify the underlying NAIVE "
                "mean against a CURRENT-regime derivation before ruling "
                "HARD_FAIL or HARD_PASS."
            ),
            "naive_2hop_rough_closed_form": (
                "NAIVE_2hop ~ erf(N / (4 * n_chains * V_P_effective)) at "
                "random-bipolar isotropic K=2 regime; underestimates at low "
                "density; over-estimates when single-pair saturates a single "
                "codebook code (regime differ); empirical smoke-run takes "
                "precedence over closed-form when they disagree by >0.05."
            ),
            "observed_instances": [
                ("consolidation_v3_HELDOUT_FIX (2026-06-25): NAIVE=0.850 vs "
                 "pre-reg band [0.62, 0.68] copied from v2 single-pair regime; "
                 "v3 changed to V_P=6 multi-class with separate W; sanity rail "
                 "fired but Research 2x drill decoded as rail mis-spec, not "
                 "methodology bug -- consolidation HARD_FAIL on heldout is the "
                 "load-bearing finding"),
                ("consolidation_v1 (2026-06-24): NAIVE=0.847 vs prior beta-"
                 "sweep BASELINE_HARD=0.65; regime difference V_P=10 uniform-"
                 "sampled vs V_P=2 fixed-pair; rail expected [0.40, 0.75] "
                 "BLOWN PAST at 0.847 but REPRODUCIBILITY_DIVERGENCE not "
                 "flagged"),
                ("pointer_chain_hybrid_v2_baseline_rail_fixed (2026-06-25): "
                 "baseline mean 0.650 in band [0.62, 0.68] BUT seed7=0.605 "
                 "(1/3 seeds breach downward) -- regime variance leaks through "
                 "at n_seeds=3 even with v2's 'rail fix' to use beta-sweep "
                 "EXACT V_P=2 fixed-pair regime; mitigation = n_seeds>=10 OR "
                 "widened band to absorb seed-level variance at V_P=2"),
            ],
            "composes_with": [
                "T3/META_M2_tight_rail_from_different_config_can_mask_direction_correct_lift",
                "META_M5_cross_cell_baseline_compare_requires_chain_construction_match",
                "META_PROSPECTIVE_BANDS_FRESH_SEEDS_eliminates_retrofit_confound_v4_validation",
                "META/CROSS_N_REPLICATION_AS_DEFINITIVE_UPGRADE_CRITERION",
            ],
            "discipline_set_name": "rail_discipline_derivation_provenance_regime_match",
            "discipline_set_size": 3,
            "discipline_set_components": [
                "META_M2_rail_must_match_referent_config_OR_widen_by_capacity_scaling_drift",
                "META_M5_cross_cell_baseline_compare_requires_chain_construction_match_LEDGER_ONLY_atom_write_gap",
                "META_M6_NAIVE_baseline_must_be_derived_from_current_regime_not_copied",
            ],
            "operational_fix": (
                "Cell pre-reg must include EITHER (a) smoke-run NAIVE arm at "
                "n_seeds>=5 at CURRENT regime + band = smoke-mean +/- 0.03, "
                "OR (b) closed-form derivation of expected NAIVE + band = "
                "expected +/- max(0.03, expected * 0.05). Do NOT copy bands "
                "across cells when ANY of {V_C, V_P, n_chains, chain-class "
                "structure, K_SET, N} differs."
            ),
            "validated_by": (
                "Three observed instances in two weeks (consolidation v1, "
                "consolidation v3, pointer-chain hybrid v2) all show rail-"
                "derivation debt creating spurious or genuine sanity-breaches "
                "that obscure the load-bearing mechanism finding. The rule "
                "would have prevented all three from being framed as 'rail-"
                "miss invalidates comparison' or 'baseline reproducibility "
                "drift'."
            ),
            "falsification_conditions": [
                "smoke_NAIVE_high_variance_at_low_n_seeds_mitigation_n_seeds_gte_5_or_closed_form",
                "closed_form_wrong_at_current_regime_mitigation_smoke_takes_precedence_when_disagree_gt_0p05",
                "rail_derivation_step_itself_instrument_bugged_mitigation_smoke_regime_must_match_full_along_every_capacity_sensitive_dim_candidate_separate_rule",
            ],
            "cites": [
                "consolidation_v3_HARD_FAIL_Research_2x_drill_2026-06-25",
                "consolidation_v1_NAIVE_drift_skunkworks_cell3_cell4_ruling_2026-06-25",
                "pointer_chain_v2_baseline_rail_fixed_HARD_FAIL_2026-06-25",
                "META_M2_companion_atomized_2026-06-25",
                "META_M5_LEDGER_ONLY_atom_write_gap_flagged_2026-06-25",
                "Director_2x_drill_research_consolidation_v3_HARD_FAIL_2x_drill_2026-06-25",
                "USER_results_to_application_cadence_same_cycle_atomize_2026-06-22",
                "Fix_28_default_under_claim_meta_smoke_floor_separate_candidate_deferred",
            ],
            "atomized_by": ATOMIZED_BY,
            "atomized_date": "2026-06-25",
            "honest_scope": (
                "Applies to cells with NAIVE / baseline sanity rail + "
                "measurable regime parameter set. Does NOT apply to within-"
                "cell replications at identical regime, cells without NAIVE "
                "arm, or cells with rails on different metrics. Validated by "
                "three observed instances same week; not yet validated by a "
                "cell that DESIGNED its rail per the rule prospectively and "
                "succeeded (the cert-ladder DEFINITIVE upgrade for THIS rule "
                "is a future cell-author cycle pickup)."
            ),
        },
        aliases=[],
    )


# ============================================================================
# Main: A5-gated write
# ============================================================================

def main() -> int:
    store = PartitionedStore(STORE_ROOT)

    # ---- PRE snapshot ----
    pre_stats = store.stats()
    print("=" * 72)
    print("PRE-snapshot:")
    print(f"  total_atoms: {pre_stats.get('total_atoms')}")
    pre_parts = pre_stats.get('partitions', {})
    pre_math = pre_parts.get('math', {}).get('n_atoms', 0)
    pre_meta = pre_parts.get('meta', {}).get('n_atoms', 0)
    print(f"  math.n_atoms: {pre_math}")
    print(f"  meta.n_atoms: {pre_meta}")

    # Live CERT N
    from tools.cert_ledger_writer import _cert_count, _axiom_count, _cap_pres_ok
    pre_cert = _cert_count(store)
    pre_ax = _axiom_count(store)
    pre_cap = _cap_pres_ok()
    print(f"  CERT N (legacy CERT_CHAIN_GRADE count): {pre_cert}")
    print(f"  axiom: {pre_ax}")
    print(f"  cap_pres: {'6/6' if pre_cap else 'FAIL'}")
    assert pre_ax == 206, f"PRE axiom drift: {pre_ax} != 206"
    assert pre_cap, "PRE cap_pres FAIL"
    print()

    a1 = build_atom_pointer_chain_v2_hard_fail()
    a2 = build_atom_meta_M6_naive_baseline_derivation()

    a1_qid = f"{a1.corpus.value}::{a1.id}"
    a2_qid = f"{a2.corpus.value}::{a2.id}"

    # ---- Collision check (idempotency) ----
    a1_exists = store.has_atom(a1_qid)
    a2_exists = store.has_atom(a2_qid)
    print("Collision check:")
    print(f"  {a1_qid}  exists={a1_exists}")
    print(f"  {a2_qid}  exists={a2_exists}")
    print()

    # Partial-write recovery semantics: if an atom already exists (from a prior partial
    # run), skip the add but still attempt the ledger row append (which is itself
    # idempotent via cert_ledger_writer's whole-ledger ts-stripped match).
    if a1_exists:
        print(f"  PARTIAL-RECOVERY: atom {a1_qid} already exists; skipping add (will still attempt ledger row).")
    else:
        print(f"Writing atom 1: {a1_qid}")
        store.add_atom(a1, source=ATOMIZED_BY, note="pointer_chain_v2_HARD_FAIL_barrier1_double_negative")
    if a2_exists:
        print(f"  PARTIAL-RECOVERY: atom {a2_qid} already exists; skipping add (will still attempt ledger row).")
    else:
        print(f"Writing atom 2: {a2_qid}")
        store.add_atom(a2, source=ATOMIZED_BY, note="META_M6_NAIVE_baseline_must_be_derived_not_copied")
    print()

    # ---- Verify-load round-trip ----
    print("Verify-load round-trip (fresh PartitionedStore from disk)...")
    store2 = PartitionedStore(STORE_ROOT)
    a1_loaded = store2.get_atom(a1_qid)
    a2_loaded = store2.get_atom(a2_qid)
    if a1_loaded is None:
        print(f"FATAL: round-trip load failed for {a1_qid}")
        return 3
    if a2_loaded is None:
        print(f"FATAL: round-trip load failed for {a2_qid}")
        return 3
    expected_a1_pq = "HONEST_NEGATIVE"
    expected_a2_pq = "META_RULE_CERT_NEUTRAL"
    if a1_loaded.metadata.get("provenance_quality") != expected_a1_pq:
        print(f"FATAL: pq mismatch on {a1_qid}: got {a1_loaded.metadata.get('provenance_quality')}")
        return 3
    if a2_loaded.metadata.get("provenance_quality") != expected_a2_pq:
        print(f"FATAL: pq mismatch on {a2_qid}: got {a2_loaded.metadata.get('provenance_quality')}")
        return 3
    if a1_loaded.metadata.get("cert_status") != "honest_negative":
        print(f"FATAL: cert_status mismatch on {a1_qid}")
        return 3
    if a2_loaded.metadata.get("cert_status") != "meta_rule":
        print(f"FATAL: cert_status mismatch on {a2_qid}")
        return 3
    print(f"  {a1_qid} round-trip OK (pq={expected_a1_pq}, cert_status=honest_negative)")
    print(f"  {a2_qid} round-trip OK (pq={expected_a2_pq}, cert_status=meta_rule)")
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
    print(f"  math.n_atoms: {post_math}  (delta {post_math - pre_math:+d}; expected +1)")
    print(f"  meta.n_atoms: {post_meta}  (delta {post_meta - pre_meta:+d}; expected +1)")
    print(f"  CERT N: {post_cert}  (delta {post_cert - pre_cert:+d}; expected +0 -- both atoms cert-neutral)")
    print(f"  axiom: {post_ax}")
    print(f"  cap_pres: {'6/6' if post_cap else 'FAIL'}")
    assert post_ax == 206, f"POST axiom drift: {post_ax} != 206"
    assert post_cap, "POST cap_pres FAIL"
    # Partial-recovery semantics: deltas are 0 if atom already existed (no fresh add).
    expected_math_delta = 0 if a1_exists else 1
    expected_meta_delta = 0 if a2_exists else 1
    assert post_math == pre_math + expected_math_delta, (
        f"math delta mismatch: pre={pre_math} post={post_math} expected_delta={expected_math_delta}"
    )
    assert post_meta == pre_meta + expected_meta_delta, (
        f"meta delta mismatch: pre={pre_meta} post={post_meta} expected_delta={expected_meta_delta}"
    )
    assert post_cert == pre_cert, f"CERT drift: pre={pre_cert} post={post_cert} (both atoms should be cert-neutral)"
    print()

    # ---- Cert ledger writes ----
    print("Appending cert_ledger rows...")

    # Row 1: honest_negative for pointer-chain v2 HARD_FAIL
    row1 = build_honest_negative_row(
        atom_id=a1_qid,
        cell_commit="v2_baseline_rail_fixed",
        verdict=(
            "HARD_FAIL_pointer_chain_hybrid_v2_baseline_rail_fixed_3seeds_"
            "7_17_23_N_8192_V_C_200_V_P_2_baseline_mean_0p650_pointer_2hop_"
            "mean_0p425_cv_0p107_FAILS_HP_0p95_mechanism_HURTS_minus_22pp_"
            "depth_ret_0p0824_FAILS_HP_0p80_hybrid_identical_to_pointer_zero_"
            "lift_zero_LLM_calls_verified_smoke_vs_full_3_dim_regime_confounded_"
            "N_2048_vs_8192_pointer_n_chains_50_vs_200_seeds_1_vs_3_NOT_pure_"
            "n_chains_sensitivity_barrier_1_double_negative_with_consolidation_"
            "v3_HARD_FAIL_same_day_substrate_native_multihop_via_compound_or_"
            "pointer_REFUTED_at_random_bipolar_isotropic_regime"
        ),
        notes_path=NOTES_PATH_RULING,
        metrics_path=METRICS_PATH_V2,
        cert_class="pre_reg_miss_proven_bound",
        atomized_by=ATOMIZED_BY,
        note=(
            "HARD_FAIL_pointer_chain_v2_baseline_rail_fixed_3_seeds_"
            "verified_off_per_seed_baseline_0p650_pointer_2hop_0p425_cv_0p107_"
            "depth_retention_0p0824_hybrid_zero_lift_geometric_decay_per_hop_"
            "0p70_zero_LLM_calls_inference_substrate_only_decode_PASSES_smoke_"
            "vs_full_3_regime_confounds_caught_by_off_data_verify_barrier_1_"
            "double_negative_with_consolidation_v3_load_bearing_for_L2_encoder_"
            "pivot_substrate_product_definition_unchanged_2_hop_chain_grade_"
            "plus_composition_plus_retrieval_plus_audit_external_PFC_scaffold_"
            "OR_semantic_consolidation_feature_share_required_for_multihop"
        ),
    )
    h1 = append_cert_ledger_row(
        row1,
        expected_cert_n_pre=pre_cert,
        expected_cert_n_post=post_cert,
    )
    print(f"  Ledger row 1 (honest_negative HARD_FAIL): hash={h1}")

    # Row 2: meta_rule for META_M6
    # NOTE: cert_ledger_writer schema enforces VALID_CERT_STATUS that does NOT include
    # 'meta_rule' as a status value (it's an atom-level convention, not a ledger-status
    # convention). Per Cell 2 v5 atomize + cell3_cell4 atomize precedent: META rules in
    # the ledger use cert_status='measured_mechanism' + cert_class='discipline_meta' OR
    # 'mechanism_characterization'. The atom-level cert_status='meta_rule' is preserved
    # in atoms.jsonl + the discipline-meta cert_class disambiguates at ledger level.
    row2_raw = {
        'op': 'cert_ruling',
        'atom_id': a2_qid,
        'cert_status': 'measured_mechanism',
        'cert_class': 'discipline_meta',
        'verified_off_data': True,
        'atomized_by': ATOMIZED_BY,
        'cell_commit': ATOMIZED_BY,
        'verdict': (
            "META_M6_NAIVE_baseline_must_be_derived_from_current_regime_not_"
            "copied_from_prior_cells_three_observed_instances_consolidation_v1_"
            "v3_pointer_chain_v2_in_two_weeks_composes_with_META_M2_rail_must_"
            "match_referent_config_AND_META_M5_chain_construction_match_three_"
            "rule_rail_discipline_derivation_provenance_regime_match_set_"
            "operational_fix_smoke_run_NAIVE_n_seeds_5_at_current_regime_OR_"
            "closed_form_derivation_DO_NOT_copy_bands_when_V_C_V_P_n_chains_"
            "chain_class_K_SET_N_differ_validated_by_three_instances_NOT_yet_"
            "validated_by_prospective_dispatch_succeeding"
        ),
        'cert_increment_delta': 0,
        'cv': None,
        'referent_pointer': {
            'notes_path': NOTES_PATH_RULING,
            'metrics_path': 'META_RULE_no_metrics_path',
            'atom_qualified_id': a2_qid,
        },
        'supersedes': None,
        'note': (
            "META_M6_NAIVE_baseline_derivation_rule_CERT_neutral_delta_0_"
            "validated_by_three_observed_instances_consolidation_v1_NAIVE_"
            "0p847_vs_band_0p40_0p75_consolidation_v3_NAIVE_0p850_vs_band_"
            "0p62_0p68_pointer_chain_v2_baseline_1of3_seed7_0p605_below_"
            "0p62_lower_bound_composes_with_META_M2_M5_three_rule_set_rail_"
            "discipline_derivation_provenance_regime_match_operational_fix_"
            "two_options_smoke_run_n_seeds_gte_5_at_current_regime_band_eq_"
            "smoke_mean_pm_0p03_OR_closed_form_derivation_expected_pm_max_"
            "0p03_expected_times_0p05_DO_NOT_copy_bands_when_any_regime_"
            "param_differs_VCVPnchainschain_class_KSET_N"
        ),
    }
    h2 = append_cert_ledger_row(
        row2_raw,
        expected_cert_n_pre=post_cert,
        expected_cert_n_post=post_cert,
    )
    print(f"  Ledger row 2 (meta_rule M6): hash={h2}")
    print()

    # ---- Summary ----
    print("=" * 72)
    print("A5 atomize COMPLETE.")
    print("Atoms landed: 2")
    print(f"  1. {a1_qid}  (honest_negative HARD_FAIL; delta=0; counts as proven negative)")
    print(f"  2. {a2_qid}  (meta_rule M6; delta=0)")
    print(f"Ledger rows appended: 2")
    print(f"CERT N: {pre_cert} -> {post_cert} (delta {post_cert - pre_cert:+d})")
    print(f"axiom: {post_ax} (stable at 206)")
    print(f"cap_pres: {'6/6' if post_cap else 'FAIL'}")
    print()
    print("HEADLINE-CERT-N convention: per recent Director Cell 2 v5 framing,")
    print("the headline CERT N follows the cert_ledger.jsonl delta-sum, not the")
    print("legacy _cert_count(provenance_quality==CERT_CHAIN_GRADE) live read.")
    print("Both atoms in this batch are CERT-NEUTRAL (delta=0). The headline CERT N")
    print("(reported elsewhere as 591 after Cell 2 v5) is UNCHANGED by this batch.")
    print()
    print("INTEGRITY GAPS FLAGGED IN TIER-RULING NOTE (for Director-routed back-fill,")
    print("NOT in scope of this spawn):")
    print("  - consolidation_v3 HARD_FAIL: ruling note exists but NO atom in")
    print("    atoms.jsonl AND NO row in cert_ledger.jsonl (gap)")
    print("  - META_M4 + META_M5: cert_ledger rows landed BUT NO atoms.jsonl entries")
    print("    (atom-write step incomplete in the cell3_cell4 atomize flow)")
    print()
    print("Path-scoped commit pattern (caller-side):")
    print("  git add -f data/substrate_index/math/atoms.jsonl")
    print("  git add -f data/substrate_index/meta/atoms.jsonl")
    print("  git add -f data/substrate_index/meta/cert_ledger.jsonl")
    print("  git add notes/skunkworks_tier_ruling_pointer_chain_v2_plus_META_M6_2026-06-25.md")
    print("  git add tools/skunkworks_atomize_pointer_chain_v2_plus_META_M6_2026-06-25.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
