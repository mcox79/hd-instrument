"""Skunkworks cert-routing: enc1_structured_n_lift_v1 HARD_FAIL + Shannon-floor META.

Cell `enc1_structured_n_lift_v1` (data/exp_enc1_structured_n_lift_v1/metrics.json) is
the encoder-side 5-arm sweep dispatched per
`notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md` to discriminate
dimension-lift vs structural-encoding rescue of the cleanup-ceiling at
N_DIM=512, M=200, sigma=1.5.

PRE-REG FALSIFIER EXPLICITLY FIRED (research note, line 61):
  "HARD_FAIL ALL 4 NON-BASELINE ARMS at sigma=1.5: the substrate's cleanup-ceiling
   at this regime is a fundamental information-theoretic floor, not a mechanism
   gap. At sigma=1.5 with M=200 the cue's signal-to-noise is below recoverable
   threshold regardless of encoder geometry. Action: META atom
   `cleanup_ceiling_at_sigma_1.5_M_200_is_Shannon_floor_not_mechanism`."

PER-ARM RESULTS (Fix #28 verify per-arm not verdict_msg framing):
  ARM_BASELINE_N512:           recall=0.020 cv=0.354 std=0.0071    HARD_FAIL
  ARM_DENSE_N4096:             recall=0.027 cv=0.088 std=0.0024    HARD_FAIL
  ARM_SPARSE_FANIN_K5_N4096:   recall=0.018 cv=0.680 std=0.0125    HARD_FAIL
  ARM_MEDIAN_SUB_N512:         recall=0.025 cv=0.566 std=0.0141    HARD_FAIL
  ARM_MEDIAN_SUB_SPARSE_N4096: recall=0.023 cv=0.101 std=0.0024    HARD_FAIL
All 5 arms below HARD_PASS bar of 0.20 at sigma=1.5. Discriminating-regime gate:
BOTH_NULL (neither pure dimension lift nor sparse-fan-in clears). Sanity at
sigma=0: all 5 arms recall=1.000 (cell implementation verified clean).
FULL 3 seeds (7, 17, 23), N_EVAL=200, wall=1.27s.

RULINGS (2 atoms, delta=0):

  1. honest_negative (delta=0): T3/EXP_enc1_structured_n_lift_v1_HN
     Pre-reg falsifier #1 explicitly fired. 4 encoder-side mechanism arms tested
     (dimension lift, sparse-fan-in K=5, median-subtract, composition); all
     HARD_FAIL at sigma=1.5. Sanity (sigma=0 all-arms recall=1.000) verified.
     5th HARD_FAIL cleanup arm-family rejected at this regime (counting baseline
     as 1; the 4 new arms add 4 encoder-side mechanism families to the prior
     4 decoder-side ones).

  2. measured_mechanism (delta=0; META): T3/META_cleanup_ceiling_shannon_floor_
     substrate_operating_envelope_sigma_leq_1p0_2026-06-23
     Cross-cell load-bearing META: 9 mechanism families now exhausted at the
     SAME regime (N_DIM=512, M=200, sigma=1.5). Four decoder-side (att1 v1
     Hopfield-iter, att1 v2 Krotov-dense, OMP sparse-coding, multi-bump CAN)
     + four encoder-side (dense N=4096 dimension lift, sparse-fan-in K=5
     N=4096, median-subtract N=512, median-subtract + sparse N=4096) + 1
     baseline (dense N=512). All HARD_FAIL recall <= 0.027 < 0.04 (HARD_FAIL
     bar). The argmax baseline at this regime IS the asymptotic cleanup-
     ceiling. Substrate-product implication: at sigma >= 1.5 with M=200
     N_DIM=512, the cleanup ceiling is fundamentally Shannon-floor / info-
     theoretic, NOT addressable by either decoder-side OR encoder-side
     mechanism change at the standard family-taxonomy tested. Substrate
     operating envelope = sigma <= 1.0 for cleanup. Pivot lever to upstream
     noise-reduction at SOURCE (encoder upgrade pythia-160m -> 1B-2.8B per
     n10 conclusion, OR contrastive learning to compress signal into low-
     noise subspace) rather than mechanism-search at sigma=1.5.

CERT-OWNER TIER DECISION FOR THE NEW META:
  By-construction-saturation tiering + Fix #28 default-under-claim: I rule
  MM tier, NOT chain-grade. Strict honest scope: '9 representative mechanism
  families exhausted at THIS regime' is strong load-bearing evidence of
  Shannon-floor character AT THIS (N=512, M=200, sigma=1.5) point. Not yet
  tested: (a) learned encoder (Foldiak anti-Hebb / Krotov BTSP / contrastive),
  (b) different M (att1 v2 at M=50 same sigma showed argmax=0.093 = 4x lift,
  so the floor IS M-dependent), (c) sub-bipolar signal injection. Chain-grade
  would require ruling those out as well. MM with operating-envelope framing
  is the honest tier; the decision rule (stop chasing sigma=1.5 mechanism-
  search, pivot upstream to signal-source) is load-bearing regardless of tier.

PRIOR META POSITION (composes, does NOT supersede):
  T3/META_cleanup_ceiling_is_encoder_bound_at_N512_high_noise_M_over_N_0p39_2026-06-23
  was a correct intermediate finding: decoder-side family is exhausted, pivot
  upstream to encoder. The prior META's decision rule was followed (we DID
  route to encoder side via enc1). The new META is what the encoder-side route
  discovered: even the encoder route fails at sigma=1.5. The two METAs compose
  monotonically. New META lists prior META in composes_with. supersedes=None.

DISCIPLINES HONORED:
  - A5 PRE/POST snapshot at start + end (one window for both writes)
  - Fix #28: per-arm metrics read directly from metrics.json, not verdict_msg
  - by-construction-saturation tiering (MM when at metric ceiling regardless of
    bands; here: 9-family exhaustion at SAME regime = strong but not yet chain-
    grade evidence for "Shannon floor across ALL substrate-meaningful encoders")
  - honest_negative for ENC1: cell fails its own load-bearing pre-reg arms +
    explicit falsifier #1 fired in research note
  - cert-owner default under-claim per Fix #28
  - Idempotency: skip atoms already in Store
  - Foreground execution (Fix #20)
  - ASCII-only
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_measured_mechanism_row,
    build_honest_negative_row,
)


STORE_ROOT = Path("data/substrate_index")
ATOMIZED_BY = "skunkworks_atomize_enc1_shannon_floor_meta_2026-06-23"


# ============================================================================
# 1. enc1_structured_n_lift_v1 -- HONEST_NEGATIVE
#    (5-arm encoder-side sweep; all non-baseline arms HARD_FAIL; sanity clean)
# ============================================================================

def build_enc1_structured_n_lift_honest_negative() -> Atom:
    return Atom(
        id="T3/EXP_enc1_structured_n_lift_v1_HN",
        name=(
            "enc1 structured N-lift encoder-side cleanup sweep -- HONEST_NEGATIVE "
            "(FULL 3 seeds; all 4 non-baseline arms HARD_FAIL at sigma=1.5; pre-reg "
            "falsifier #1 fired)"
        ),
        description=(
            "Encoder-side 5-arm sweep dispatched per encoder-side-cleanup-ceiling-"
            "break research note 2026-06-23 to discriminate dimension-lift vs "
            "structural-encoding (sparse-fan-in / median-subtract) rescue of the "
            "cleanup-ceiling at parent regime N_DIM=512, M=200, sigma=1.5 (where "
            "4 decoder-side mechanism families had previously failed). FULL 3 seeds "
            "(7, 17, 23) at N_EVAL=200 per seed, 5 sigmas [0.0, 0.5, 1.0, 1.5, 2.0]. "
            "Wall time: 1.27 s. "
            "Per-arm results at discriminator sigma=1.5 (mean across 3 seeds): "
            "ARM_BASELINE_N512 recall=0.020 cv=0.354 std=0.0071 (reproduces parent "
            "HARD_FAIL baseline ~0.023); ARM_DENSE_N4096 recall=0.027 cv=0.088 std="
            "0.0024 (pure JL dimension lift; +0.007 over baseline, well below HARD_"
            "PASS=0.20); ARM_SPARSE_FANIN_K5_N4096 recall=0.018 cv=0.680 std=0.0125 "
            "(cerebellar GC analog; BELOW baseline); ARM_MEDIAN_SUB_N512 recall="
            "0.025 cv=0.566 std=0.0141 (fly-LSH; near baseline); ARM_MEDIAN_SUB_"
            "SPARSE_N4096 recall=0.023 cv=0.101 std=0.0024 (composition; near "
            "baseline). All 5 arms < 0.04 HARD_FAIL bar. Discriminating-regime "
            "gate: BOTH_NULL (neither pure dimension lift nor sparse-fan-in clears "
            "HARD_PASS). Sanity at sigma=0.0: all 5 arms recall = 1.000 across all "
            "3 seeds (cell implementation verified clean -- atom recovery is by "
            "construction at zero noise). \n\n"
            "PRE-REG FALSIFIER #1 EXPLICITLY FIRED (per research note 2026-06-23, "
            "line 61): 'HARD_FAIL ALL 4 NON-BASELINE ARMS at sigma=1.5: substrate's "
            "cleanup-ceiling at this regime is a fundamental information-theoretic "
            "floor, not a mechanism gap. At sigma=1.5 with M=200 the cue's signal-"
            "to-noise is below recoverable threshold regardless of encoder geometry. "
            "Action: META atom cleanup_ceiling_at_sigma_1.5_M_200_is_Shannon_floor.' "
            "This atom is the cell-level HN; the META atom (this batch) carries the "
            "cross-cell synthesis. \n\n"
            "Composes with prior 4 decoder-side HN atoms (att1 v1, att1 v2, OMP, "
            "multi-bump CAN) + the prior encoder-bound META 2026-06-23. Verified-"
            "off-data: per-seed per-arm recall + basin_robustness in metrics.json "
            "across all 3 seeds."
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
                "HONEST_NEGATIVE_FULL_3seeds_all_4_non_baseline_encoder_arms_HARD_"
                "FAIL_at_sigma_1p5_BASELINE_0p020_DENSE_4096_0p027_SPARSE_FANIN_K5_"
                "4096_0p018_MEDIAN_SUB_512_0p025_MEDIAN_SUB_SPARSE_4096_0p023_all_"
                "below_HARD_PASS_0p20_and_below_HARD_FAIL_0p04_regime_BOTH_NULL_"
                "sanity_sigma_0_all_arms_recall_1p000_implementation_clean_pre_reg_"
                "falsifier_1_explicitly_fired_Shannon_floor"
            ),
            "cell_commit": "overnight_2026-06-22_plus_encoder_side_drill_2026-06-23",
            "metrics_path": "data/exp_enc1_structured_n_lift_v1/metrics.json",
            "notes_path": "notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md",
            "verified_off_data": (
                "cert-owner re-derived from metrics.json across all 3 seeds (7, 17, "
                "23). Aggregated recall_discriminator_mean at sigma=1.5: ARM_BASELINE_"
                "N512=0.0200 (per-seed 0.010/0.025/0.025), ARM_DENSE_N4096=0.0267 "
                "(per-seed 0.025/0.030/0.025), ARM_SPARSE_FANIN_K5_N4096=0.0183 "
                "(per-seed 0.035/0.015/0.005), ARM_MEDIAN_SUB_N512=0.0250 (per-seed "
                "0.045/0.015/0.015), ARM_MEDIAN_SUB_SPARSE_N4096=0.0233 (per-seed "
                "0.025/0.025/0.020). CV values: 0.354, 0.088, 0.680, 0.566, 0.101. "
                "All 5 arms < HARD_PASS=0.20 AND < HARD_FAIL_BAR=0.04. Sanity at "
                "sigma=0: every arm every seed recall=1.000 (basin_robustness '0.0' "
                "key = 1.000 across all 15 (arm, seed) combos). discriminating_"
                "regime_call='BOTH_NULL'; n_hard_pass_arms=0; n_hard_fail_nonbaseline_"
                "arms=4; sanity_sigma0_recall_all_1_0_ok=True. zero_llm_calls_at_"
                "inference=True. config_version baked. Pre-reg bands (per arm vs "
                "ARM_BASELINE_N512=0.023): HARD_PASS arm_recall >= 0.20 + CV <= 0.30; "
                "HARD_FAIL arm_recall <= 0.04; MIDDLE_BAND 0.04-0.20. Every non-"
                "baseline arm satisfies HARD_FAIL: 0.0267, 0.0183, 0.0250, 0.0233 all "
                "<= 0.04. Cell verdict HARD_FAIL is honest and load-bearing. Cell "
                "verdict_msg explicitly cites Shannon-floor candidate framing."
            ),
            "honest_scope": (
                "FULL 3-seed encoder-side 5-arm sweep at substrate-mine regime "
                "N_DIM_BASELINE=512, N_DIM_LIFT=4096, K_SPARSE=5, M=200, N_EVAL=200, "
                "sigmas=[0,0.5,1,1.5,2]. Pure-numpy CPU matmul (no LLM at inference; "
                "n_llm=0 verified). DOES rule that 4 encoder-side mechanism families "
                "(JL dimension lift, sparse-fan-in cerebellar K=5, fly-LSH median-"
                "subtract, composition median-sub + sparse) fail to lift argmax-"
                "baseline cleanup recall above HARD_FAIL bar at N_DIM=512 M=200 "
                "sigma=1.5. DOES NOT rule: learned-encoder (Foldiak anti-Hebb, "
                "Krotov BTSP, contrastive); different M; different N_DIM; richer "
                "per-atom signal payload (sub-bipolar precision). DOES NOT prove "
                "the cleanup-ceiling is Shannon-floor at all configs -- only that "
                "the 9-family-exhaustion at THIS regime is consistent with Shannon-"
                "floor framing. Substrate operating envelope conclusion (sigma <= "
                "1.0 for cleanup) follows from the META composing this HN with the "
                "prior 4 decoder-side HNs."
            ),
            "n_seeds": 3,
            "seeds": [7, 17, 23],
            "N_DIM_BASELINE": 512,
            "N_DIM_LIFT": 4096,
            "K_SPARSE": 5,
            "M": 200,
            "N_EVAL": 200,
            "discriminator_sigma": 1.5,
            "sigmas_tested": [0.0, 0.5, 1.0, 1.5, 2.0],
            "arms": [
                "ARM_BASELINE_N512",
                "ARM_DENSE_N4096",
                "ARM_SPARSE_FANIN_K5_N4096",
                "ARM_MEDIAN_SUB_N512",
                "ARM_MEDIAN_SUB_SPARSE_N4096",
            ],
            "recall_discriminator_mean_BASELINE_N512": 0.020,
            "recall_discriminator_mean_DENSE_N4096": 0.0267,
            "recall_discriminator_mean_SPARSE_FANIN_K5_N4096": 0.0183,
            "recall_discriminator_mean_MEDIAN_SUB_N512": 0.025,
            "recall_discriminator_mean_MEDIAN_SUB_SPARSE_N4096": 0.0233,
            "hard_pass_bar": 0.20,
            "hard_fail_bar": 0.04,
            "n_hard_pass_arms": 0,
            "n_hard_fail_nonbaseline_arms": 4,
            "discriminating_regime_call": "BOTH_NULL",
            "sanity_sigma0_recall_all_1_0_ok": True,
            "elapsed_s_total": 1.27,
            "run_mode": "full",
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "pre_reg_falsifier_fired": "FALSIFIER_1_HARD_FAIL_ALL_4_NON_BASELINE_ARMS_at_sigma_1p5_Shannon_floor",
            "composes_with": [
                "T3/EXP_att1_iterative_attractor_cleanup_v1_HN",
                "T3/EXP_omp_sparse_coding_cleanup_v1_HN",
                "T3/EXP_multi_bump_can_ensemble_cleanup_v1_HN",
                "T3/META_cleanup_ceiling_is_encoder_bound_at_N512_high_noise_M_over_N_0p39_2026-06-23",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_not_verdict_msg_framing",
                "USER_empowered_to_experiment_where_lit_says_dismissed_2026-06-22",
                "Litwin_Kumar_2017_optimal_synaptic_connectivity",
                "Cayco_Gajic_2017_PMC5729189_cerebellar_GC",
                "Dasgupta_Stevens_Navlakha_2017_fly_LSH",
                "Foldiak_1990_anti_Hebbian_decorrelation",
                "Johnson_Lindenstrauss_lemma",
                "CERT_591_dense_projected_KV",
                "research_encoder_side_cleanup_ceiling_break_2026-06-23",
                "research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23_parent",
            ],
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# 2. META atom: Shannon-floor substrate operating envelope sigma <= 1.0
#    (9 mechanism families exhausted; composes prior encoder-bound META)
# ============================================================================

def build_meta_cleanup_ceiling_shannon_floor() -> Atom:
    return Atom(
        id="T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0_2026-06-23",
        name=(
            "META cleanup-ceiling is Shannon-floor at N_DIM=512 M=200 sigma=1.5; "
            "substrate operating envelope sigma <= 1.0 (9 mechanism families "
            "exhausted: 4 decoder + 4 encoder + baseline)"
        ),
        description=(
            "CROSS-CELL LOAD-BEARING META FINDING (super-META; composes the prior "
            "encoder-bound META 2026-06-23 monotonically without superseding). \n\n"
            "Nine mechanism families have now been independently rejected at the "
            "SAME substrate regime (N_DIM=512, M=200, M/N=0.39, sigma=1.5, N_EVAL "
            "in 50-200) across BOTH decoder-side AND encoder-side taxonomies:\n"
            "  DECODER-SIDE (4 families; prior META):\n"
            "    1. att1 v1 iterative-attractor Hopfield-style soft (HONEST_NEGATIVE)\n"
            "    2. att1 v2 Krotov-dense pseudo-energy (HONEST_NEGATIVE)\n"
            "    3. OMP sparse-coding K1/K2/K4 (HONEST_NEGATIVE)\n"
            "    4. Multi-bump CAN ensemble (HONEST_NEGATIVE)\n"
            "  ENCODER-SIDE (4 families + 1 baseline; new this batch via enc1):\n"
            "    5. ARM_BASELINE_N512 dense bipolar codebook (reproduces parent fail)\n"
            "    6. ARM_DENSE_N4096 JL random-projection dimension lift\n"
            "    7. ARM_SPARSE_FANIN_K5_N4096 cerebellar-GC analog sparse-fan-in\n"
            "    8. ARM_MEDIAN_SUB_N512 fly-LSH-style median-subtract preprocess\n"
            "    9. ARM_MEDIAN_SUB_SPARSE_N4096 composition (median-sub + sparse-"
            "fan-in)\n\n"
            "All 9 arms HARD_FAIL: recall <= 0.027 < HARD_FAIL_bar 0.04 < HARD_PASS_"
            "bar 0.20 across all measured cells. The argmax baseline at this regime "
            "IS the asymptotic cleanup-ceiling regardless of decoder OR encoder "
            "structure across the standard family taxonomies. The pre-registered "
            "falsifier (research note 2026-06-23 line 61) explicitly fired:\n"
            "  'HARD_FAIL ALL 4 NON-BASELINE ARMS at sigma=1.5: substrate's cleanup-\n"
            "   ceiling at this regime is a fundamental information-theoretic floor,\n"
            "   not a mechanism gap. At sigma=1.5 with M=200 the cue's signal-to-\n"
            "   noise is below recoverable threshold regardless of encoder geometry.'\n\n"
            "SUBSTRATE OPERATING ENVELOPE (load-bearing decision rule):\n"
            "  - Substrate's cleanup-mechanism envelope is sigma <= 1.0 at N_DIM=512 "
            "M=200. At sigma=1.5+ with this storage ratio, NO mechanism in the tested "
            "9-family taxonomy lifts above argmax-noise-floor.\n"
            "  - Decision rule: stop dispatching mechanism-search cells (either "
            "decoder OR encoder taxonomy) at the sigma=1.5 high-noise stress regime. "
            "Pivot lever to NOISE-REDUCTION AT SOURCE upstream of substrate ingest:\n"
            "    (a) Encoder UPGRADE (pythia-160m -> 1B / 2.8B per n10 conclusion) "
            "to lower per-dimension noise BEFORE substrate sees the signal.\n"
            "    (b) Contrastive learning to compress per-atom signal into a low-"
            "noise subspace (CERT 591-style projection but with more aggressive "
            "margin maximization).\n"
            "    (c) Sub-bipolar precision (float-valued payload) to inject richer "
            "per-atom signal at ingest; orthogonal to the 9 tested mechanism "
            "families.\n"
            "  - Future decoder OR encoder mechanism proposals at sigma=1.5 must "
            "EITHER (i) test at a DIFFERENT regime where the floor is shown to be "
            "elsewhere (e.g. M=50 with sigma=1.5 where argmax=0.093 = 4x lift), OR "
            "(ii) test a mechanism family OUTSIDE the 9 already exhausted (learned "
            "encoder, sub-bipolar payload, BTSP-style relative-floor).\n\n"
            "RELATION TO PRIOR ENCODER-BOUND META (2026-06-23, ledger row 673):\n"
            "  Prior META concluded: '4 decoder families exhausted -> cleanup-"
            "ceiling is structurally encoder-bound at this regime; pivot upstream "
            "to encoder side.' That conclusion was CORRECT and the decision rule "
            "WAS followed (enc1 was the encoder-side route). The new META is what "
            "the encoder-side route DISCOVERED: even the encoder route fails at "
            "sigma=1.5 across the standard structural-encoder taxonomy. The two "
            "METAs COMPOSE MONOTONICALLY:\n"
            "  - Prior META: 'decoder-bound? NO; pivot upstream to encoder.'\n"
            "  - New META: 'encoder routed; further upstream hits info-theoretic "
            "floor; envelope sigma <= 1.0; pivot further upstream to signal source.'\n"
            "  supersedes=None. Prior META lives in composes_with. Prior META "
            "remains valid AS-IS (its scope was decoder-side exhaustion + indicated "
            "encoder-side next move; both are still true).\n\n"
            "CERT-OWNER TIER DECISION (MM not chain-grade):\n"
            "  Per Fix #28 default-under-claim + by-construction-saturation tiering: "
            "9-family exhaustion at THIS regime is strong load-bearing evidence of "
            "Shannon-floor character AT THIS (N=512, M=200, sigma=1.5) POINT. Not "
            "yet tested as part of the exhaustion taxonomy:\n"
            "  (a) Learned encoder (Foldiak anti-Hebb / Krotov BTSP / contrastive)\n"
            "  (b) Different M (M=50 same sigma already shows argmax=0.093 = 4x "
            "lift; floor IS M-dependent, not purely sigma-dependent)\n"
            "  (c) Sub-bipolar / float-valued signal payload\n"
            "Chain-grade-tier would require ruling those out as well. MM with "
            "operating-envelope framing is the honest tier; the decision rule "
            "(stop sigma=1.5 mechanism-search; pivot upstream to signal source) "
            "is load-bearing regardless of tier.\n\n"
            "ARC-CONCLUSION STATUS: This META is the load-bearing arc-conclusion "
            "of the cleanup-ceiling-break drill that started with att1 in mid-arc "
            "and concluded with enc1 this turn. Substrate operating envelope is now "
            "empirically circumscribed for the cleanup-task family at the parent "
            "regime."
        ),
        kind=AtomKind.EXPERIMENT_RECORD,
        tier=Tier.TIER_3_ALGORITHM,
        corpus=Corpus.MATH,
        algebra=None,
        metadata={
            "provenance_quality": "MEASURED_MECHANISM",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "meta_atom": True,
            "super_meta": True,
            "verdict": (
                "META_cleanup_ceiling_Shannon_floor_at_N_DIM_512_M_200_sigma_1p5_"
                "substrate_operating_envelope_sigma_leq_1p0_9_mechanism_families_"
                "exhausted_4_decoder_att1_v1_att1_v2_OMP_multi_bump_CAN_plus_4_"
                "encoder_dense_N_4096_sparse_fanin_K5_N_4096_median_sub_N_512_"
                "composition_plus_baseline_all_HARD_FAIL_recall_lt_0p03_lt_HARD_"
                "FAIL_0p04_argmax_IS_the_cleanup_ceiling_at_this_regime_pre_reg_"
                "falsifier_1_explicitly_fired_decision_rule_stop_sigma_1p5_mechanism_"
                "search_pivot_upstream_to_signal_source_encoder_upgrade_pythia_to_"
                "1B_2p8B_contrastive_subbipolar_payload_tier_MM_not_chain_grade_per_"
                "Fix_28_default_under_claim_3_untested_families_learned_encoder_"
                "different_M_subbipolar_payload"
            ),
            "cell_commit": "overnight_2026-06-22_plus_encoder_side_drill_2026-06-23",
            "metrics_path": "cross_atom_synthesis_5_HN_referent_atoms",
            "notes_path": "notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md",
            "verified_off_data": (
                "cert-owner cross-cell synthesis from 5 referent HONEST_NEGATIVE atoms "
                "(4 decoder-side from prior META + 1 new encoder-side this batch), "
                "each independently audited via Fix #28 per-arm metrics reads:\n"
                "  (1) att1_iterative_attractor_cleanup_v1_HN: best_att1_lift=0.000 "
                "vs argmax baseline; all 3 ATT1 arms tie or underperform argmax at "
                "N_DIM=512 M=200 sigma=1.5 (smoke + revival).\n"
                "  (2) att1_v2_krotov_dense_cleanup_v1_HN: Krotov dense-attractor "
                "variant rejected same regime; lift below noise floor.\n"
                "  (3) omp_sparse_coding_cleanup_v1_HN: best OMP arm K1 lift=-0.008 "
                "vs argmax 0.0233; all 3 OMP arms underperform at sigma=1.5. Sanity "
                "OMP_K1==argmax at sigma=0 clean.\n"
                "  (4) multi_bump_can_ensemble_cleanup_v1_HN: best multi-bump K4 "
                "0.1 lift=+0.002 vs argmax 0.0267 within noise (cv=0.42); K=1 sanity "
                "== argmax exactly; only 1 of 7 multi-bump arms exceeds argmax (by "
                "below 1-sigma); cert-owner override of Director MM rec per Fix #28 "
                "default-under-claim.\n"
                "  (5) enc1_structured_n_lift_v1_HN (this batch): 5-arm encoder-side "
                "sweep BASELINE_N512=0.020, DENSE_N4096=0.027, SPARSE_FANIN_K5=0.018, "
                "MEDIAN_SUB_N512=0.025, MEDIAN_SUB_SPARSE_N4096=0.023; all 5 < HARD_"
                "FAIL bar 0.04 at sigma=1.5; sanity sigma=0 recall=1.000 all arms; "
                "pre-reg falsifier #1 explicitly fired.\n"
                "Common regime: N_DIM_BASE=512 M=200 M/N=0.39 discriminator_sigma="
                "1.5 N_EVAL in 50-200. Mechanism-family span covers BOTH the "
                "standard decoder-side taxonomy (iterative soft-attractor, dense "
                "pseudo-energy, sparse residual fitting, bump-aggregation ensemble) "
                "AND the standard encoder-side taxonomy (dimension lift via JL, "
                "cerebellar sparse-fan-in, fly-LSH median-subtract, composition). "
                "All 9 arms (4 dec + 4 enc + baseline) HARD_FAIL. Cross-cell pattern "
                "consistent + not seed-noise + spans 2 taxonomies. The argmax-noise-"
                "floor IS the asymptotic cleanup-ceiling at this regime. "
                "PRE-REG FALSIFIER FIRED: research note 2026-06-23 line 61 explicitly "
                "registered 'HARD_FAIL ALL 4 NON-BASELINE ARMS at sigma=1.5' as the "
                "Shannon-floor-not-mechanism falsifier; the cell hit precisely this "
                "outcome."
            ),
            "honest_scope": (
                "Cross-cell super-META synthesis covering 9 mechanism families "
                "(4 decoder-side + 4 encoder-side + 1 baseline) at the SAME regime "
                "N_DIM=512 M=200 M/N=0.39 sigma=1.5. Substrate-product implication: "
                "cleanup-ceiling at this regime is Shannon-floor / information-"
                "theoretic, NOT addressable by either decoder-side OR encoder-side "
                "mechanism change at the standard family taxonomy. Substrate "
                "operating envelope sigma <= 1.0 for cleanup at this M/N. "
                "DOES NOT generalize to other regimes: at N_DIM=4096+ default or "
                "different M or different M/N ratio the Shannon-floor location "
                "shifts (att1 v2 at M=50 same sigma already showed argmax=0.093 = "
                "4x lift, demonstrating M-dependence of the floor). DOES NOT prove "
                "the cleanup-ceiling is Shannon-floor across ALL substrate-meaningful "
                "encoder configurations -- only that the 9 representative mechanism "
                "families fail at THIS regime. DOES NOT close 3 family-taxonomy "
                "branches still open: learned encoder (Foldiak / Krotov BTSP / "
                "contrastive), different M, and sub-bipolar / float-valued signal "
                "payload. DOES strongly imply that cleanup-improvement effort at "
                "sigma >= 1.5 should pivot UPSTREAM to signal source (encoder upgrade "
                "or contrastive compression of signal into low-noise subspace) until "
                "evidence is brought that the regime is mechanism-bound at a "
                "different M/N/sigma."
            ),
            "regime_N_DIM": 512,
            "regime_M": 200,
            "regime_M_over_N": 0.39,
            "regime_sigma": 1.5,
            "regime_N_EVAL": "50_to_200_across_referent_cells",
            "referent_HN_atoms": [
                "T3/EXP_att1_iterative_attractor_cleanup_v1_HN",
                "T3/EXP_att1_v2_krotov_dense_cleanup_v1_HN",
                "T3/EXP_omp_sparse_coding_cleanup_v1_HN",
                "T3/EXP_multi_bump_can_ensemble_cleanup_v1_HN",
                "T3/EXP_enc1_structured_n_lift_v1_HN",
            ],
            "rejected_decoder_mechanism_families": [
                "iterative_soft_attractor_Hopfield_style",
                "dense_pseudo_energy_attractor_Krotov_style",
                "sparse_residual_fitting_OMP",
                "bump_aggregation_ensemble_multi_bump_CAN",
            ],
            "rejected_encoder_mechanism_families": [
                "dense_baseline_N_512_bipolar_codebook",
                "JL_random_projection_dimension_lift_N_4096",
                "cerebellar_GC_sparse_fan_in_K_5_N_4096",
                "fly_LSH_median_subtract_preprocess_N_512",
                "composition_median_subtract_plus_sparse_fan_in_N_4096",
            ],
            "still_untested_family_branches": [
                "learned_encoder_Foldiak_anti_Hebb_Krotov_BTSP_contrastive",
                "different_M_regime_e_g_M_50_argmax_0p093_at_same_sigma_1p5",
                "sub_bipolar_float_valued_signal_payload",
            ],
            "operating_envelope_finding": "substrate_cleanup_sigma_leq_1p0_at_N_DIM_512_M_200",
            "decision_rule": (
                "stop_dispatching_mechanism_search_cells_at_sigma_1p5_high_noise_stress_"
                "regime_pivot_lever_to_noise_reduction_at_source_upstream_of_substrate_"
                "ingest_encoder_upgrade_pythia_160m_to_1B_or_2p8B_per_n10_conclusion_or_"
                "contrastive_learning_compress_signal_into_low_noise_subspace_or_sub_"
                "bipolar_richer_payload"
            ),
            "shape_analog_to_prior_META": "T3/META_cleanup_ceiling_is_encoder_bound_at_N512_high_noise_M_over_N_0p39_2026-06-23",
            "supersedes": None,
            "supersedes_reasoning": (
                "DOES NOT supersede the prior encoder-bound META 2026-06-23 (ledger "
                "row 673). Prior META's scope was 4-decoder-family exhaustion + "
                "indicated encoder-side next move; both conclusions remain valid. "
                "New META composes monotonically: prior identified the indicated "
                "next move (encoder side); new reports what that move discovered "
                "(further upstream hits info-theoretic floor; envelope sigma<=1.0). "
                "Both METAs live as separate atoms; new lists prior in composes_with."
            ),
            "pre_reg_falsifier_fired": (
                "falsifier_1_research_note_2026_06_23_line_61_HARD_FAIL_ALL_4_NON_"
                "BASELINE_ARMS_at_sigma_1p5_Shannon_floor_not_mechanism_gap_fired_"
                "as_pre_registered"
            ),
            "zero_llm_calls_at_inference": True,
            "composes_with": [
                "T3/EXP_att1_iterative_attractor_cleanup_v1_HN",
                "T3/EXP_omp_sparse_coding_cleanup_v1_HN",
                "T3/EXP_multi_bump_can_ensemble_cleanup_v1_HN",
                "T3/EXP_enc1_structured_n_lift_v1_HN",
                "T3/META_cleanup_ceiling_is_encoder_bound_at_N512_high_noise_M_over_N_0p39_2026-06-23",
                "T3/META_storage_chain_item3_eff_rank_limited_at_projection_step_decode_algebra_rescue_family_exhausted_2026-06-22",
            ],
            "cites": [
                "Fix_28_verify_per_arm_metrics_not_verdict_msg_framing",
                "Fix_28_default_under_claim_let_cert_come_from_data_not_framing",
                "by_construction_saturation_tiering",
                "USER_empowered_to_experiment_where_lit_says_dismissed_2026-06-22",
                "USER_strategic_phase_diagram_action_data_survives_transformations_2026-06-22",
                "research_encoder_side_cleanup_ceiling_break_2026-06-23",
                "research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23",
                "Litwin_Kumar_2017_optimal_synaptic_connectivity",
                "Dasgupta_Stevens_Navlakha_2017_fly_LSH",
                "Foldiak_1990_anti_Hebbian_decorrelation",
                "Krotov_Hopfield_2026_BTSP",
                "Johnson_Lindenstrauss_lemma",
                "CERT_591_dense_projected_KV",
            ],
            "atomized_by": ATOMIZED_BY,
        },
    )


# ============================================================================
# Helpers (mirrors prior batch's safe_add_with_ledger)
# ============================================================================

def safe_add_with_ledger(atom: Atom, ledger_row_builder: str, source: str, note: str,
                         notes_path: str, metrics_path: str, cv, verdict_text: str,
                         atom_id_full: str, cell_commit: str, expected_delta: int):
    ps = PartitionedStore(STORE_ROOT)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"  SKIP (idempotent): {atom.id} already present.")
    else:
        print(f"  ADDING atom: {atom.id}")
        ps.add_atom(atom, source=source, note=note)
        ps2 = PartitionedStore(STORE_ROOT)
        atoms = list(ps2.all_atoms())
        found = next((a for a in atoms if a.id == atom.id), None)
        if found is None:
            print("  FAIL: atom not found post-add")
            return (False, None)
        md = found.metadata or {}
        expected_pq = (atom.metadata or {}).get("provenance_quality")
        if md.get("provenance_quality") != expected_pq:
            print(f"  FAIL: pq mismatch (expected {expected_pq}, got {md.get('provenance_quality')})")
            return (False, None)
        print(f"  PASS: round-trip OK (pq={expected_pq})")

    ps_live = PartitionedStore(STORE_ROOT)
    live_cert = sum(
        1 for a in ps_live.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )

    if ledger_row_builder == "measured_mechanism":
        row = build_measured_mechanism_row(
            atom_id=atom_id_full, cell_commit=cell_commit, verdict=verdict_text,
            notes_path=notes_path, metrics_path=metrics_path,
            atomized_by=ATOMIZED_BY, note=note,
        )
    elif ledger_row_builder == "honest_negative":
        row = build_honest_negative_row(
            atom_id=atom_id_full, cell_commit=cell_commit, verdict=verdict_text,
            notes_path=notes_path, metrics_path=metrics_path,
            cert_class="pre_reg_miss_proven_bound",
            atomized_by=ATOMIZED_BY, note=note, verified_off_data=True,
        )
    else:
        raise ValueError(f"unknown builder: {ledger_row_builder}")

    print(
        f"  appending cert-ledger row (op={row['op']} status={row['cert_status']} "
        f"delta={row['cert_increment_delta']})"
    )
    try:
        h = append_cert_ledger_row(
            row,
            expected_cert_n_pre=live_cert,
            expected_cert_n_post=live_cert,
        )
        print(f"  row_hash={h}")
        return (True, h)
    except Exception as e:
        print(f"  FAIL: ledger append errored: {e}")
        return (False, None)


# ============================================================================
# Main
# ============================================================================

ATOM_PLAN = [
    (
        build_enc1_structured_n_lift_honest_negative,
        "honest_negative",
        "notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md",
        "data/exp_enc1_structured_n_lift_v1/metrics.json",
        None,
        "HONEST_NEGATIVE_FULL_3seeds_all_4_non_baseline_encoder_arms_HARD_FAIL_at_sigma_1p5_BASELINE_N512_0p020_DENSE_N4096_0p027_SPARSE_FANIN_K5_N4096_0p018_MEDIAN_SUB_N512_0p025_MEDIAN_SUB_SPARSE_N4096_0p023_regime_BOTH_NULL_sanity_sigma_0_recall_1p000_all_arms_clean_pre_reg_falsifier_1_fired",
        "overnight_2026-06-22_plus_encoder_side_drill_2026-06-23",
        0,
        "enc1_structured_n_lift_v1_HONEST_NEGATIVE_FULL_3seeds_seeds_7_17_23_N_DIM_BASE_512_N_DIM_LIFT_4096_K_SPARSE_5_M_200_N_EVAL_200_sigma_1p5_5arm_encoder_sweep_BASELINE_0p020_DENSE_4096_0p027_SPARSE_FANIN_K5_0p018_MEDIAN_SUB_512_0p025_MEDIAN_SUB_SPARSE_4096_0p023_all_5_arms_lt_HARD_FAIL_bar_0p04_lt_HARD_PASS_bar_0p20_discriminating_regime_BOTH_NULL_neither_dimension_nor_sparse_fan_in_clears_sanity_sigma_0_all_arms_recall_1p000_implementation_clean_wall_1p27s_zero_llm_calls_pre_reg_falsifier_1_HARD_FAIL_ALL_4_NON_BASELINE_ARMS_explicitly_fired_Shannon_floor_candidate_5th_encoder_side_cleanup_arm_family_rejected_after_4_decoder_side_HN_atoms_composes_prior_encoder_bound_META_2026_06_23",
    ),
    (
        build_meta_cleanup_ceiling_shannon_floor,
        "measured_mechanism",
        "notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md",
        "cross_atom_synthesis_5_HN_referent_atoms",
        None,
        "META_cleanup_ceiling_Shannon_floor_substrate_operating_envelope_sigma_leq_1p0_9_mechanism_families_exhausted_4_decoder_plus_4_encoder_plus_baseline_at_N_DIM_512_M_200_sigma_1p5_pre_reg_falsifier_1_fired_decision_rule_pivot_upstream_to_signal_source",
        "overnight_2026-06-22_plus_encoder_side_drill_2026-06-23",
        0,
        "META_cleanup_ceiling_Shannon_floor_substrate_operating_envelope_sigma_leq_1p0_2026_06_23_super_meta_9_mechanism_families_exhausted_4_decoder_att1_v1_Hopfield_iter_att1_v2_Krotov_dense_OMP_sparse_coding_multi_bump_CAN_plus_4_encoder_dense_N_4096_sparse_fanin_K5_N_4096_median_sub_N_512_composition_plus_baseline_dense_N_512_all_HARD_FAIL_recall_lt_0p03_lt_HARD_FAIL_bar_0p04_at_N_DIM_512_M_200_M_over_N_0p39_sigma_1p5_argmax_IS_the_cleanup_ceiling_at_this_regime_pre_reg_falsifier_1_research_note_2026_06_23_line_61_explicitly_fired_substrate_operating_envelope_sigma_leq_1p0_decision_rule_stop_sigma_1p5_mechanism_search_pivot_upstream_to_noise_reduction_at_signal_source_encoder_upgrade_pythia_160m_to_1B_2p8B_or_contrastive_low_noise_subspace_or_sub_bipolar_payload_3_family_branches_still_open_learned_encoder_different_M_sub_bipolar_payload_MM_not_chain_grade_per_Fix_28_default_under_claim_supersedes_None_composes_monotonically_with_prior_encoder_bound_META_2026_06_23",
    ),
]


def main() -> int:
    if "--apply" not in sys.argv:
        print("DRY: pass --apply to mutate Store + ledger.")
        print(f"Plan: {len(ATOM_PLAN)} atomizations")
        for i, item in enumerate(ATOM_PLAN, 1):
            builder, lb, _, _, _, _, _, delta, _ = item
            a = builder()
            print(f"  {i}. {a.id}  pq={a.metadata['provenance_quality']}  ledger_op={lb}  delta=+{delta if delta>0 else 0}")
        return 0

    ps = PartitionedStore(STORE_ROOT)
    atoms_pre = list(ps.all_atoms())
    n_atoms_pre = len(atoms_pre)
    cert_pre = sum(
        1 for a in atoms_pre
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print(f"A5-PRE: n_atoms={n_atoms_pre} CERT N={cert_pre}")
    expected_delta_atoms = len(ATOM_PLAN)
    expected_delta_cert = sum(d for _, _, _, _, _, _, _, d, _ in ATOM_PLAN)
    print(f"Expected delta: atoms +{expected_delta_atoms}; CERT +{expected_delta_cert}")
    print()

    row_hashes = []
    for i, item in enumerate(ATOM_PLAN, 1):
        builder, lb, notes_path, metrics_path, cv, verdict_text, cell_commit, delta, ledger_note = item
        atom = builder()
        atom_id_full = f"{atom.corpus.value}::{atom.id}"
        print(f"=== {i}/{len(ATOM_PLAN)}: {atom.id}  (pq={atom.metadata['provenance_quality']} delta=+{delta})")
        ok, h = safe_add_with_ledger(
            atom, lb,
            source=ATOMIZED_BY,
            note=ledger_note,
            notes_path=notes_path,
            metrics_path=metrics_path,
            cv=cv,
            verdict_text=verdict_text,
            atom_id_full=atom_id_full,
            cell_commit=cell_commit,
            expected_delta=delta,
        )
        if not ok:
            print(f"ABORT at item {i}")
            return 1
        row_hashes.append((atom.id, h))
        print()

    ps_post = PartitionedStore(STORE_ROOT)
    atoms_post = list(ps_post.all_atoms())
    n_atoms_post = len(atoms_post)
    cert_post = sum(
        1 for a in atoms_post
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )
    print("=" * 72)
    print(f"A5-POST: n_atoms={n_atoms_post} (delta +{n_atoms_post - n_atoms_pre}, expected +{expected_delta_atoms})")
    print(f"         CERT N={cert_post} (delta +{cert_post - cert_pre}, expected +{expected_delta_cert})")
    print("=" * 72)
    print("Row hashes:")
    for aid, h in row_hashes:
        print(f"  {h}  {aid}")

    if (n_atoms_post - n_atoms_pre) != expected_delta_atoms:
        print("WARNING: atom count drift")
        return 1
    if (cert_post - cert_pre) != expected_delta_cert:
        print("WARNING: CERT count drift")
        return 1
    print("A5 invariants PRESERVED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
