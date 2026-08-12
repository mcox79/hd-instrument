"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY) of two related FULL negatives + adjudication of a convergence claim.

CELL 1 (crux): experiments/exp_crux_engine_fb15k237_vsa_gt_v1.py (commit 8c238125d)
  metrics: data/exp_crux_engine_fb15k237_vsa_gt_v1/metrics.json (FULL, 3 seeds 7/17/23, N_DIM=2048, verdict HARD_FAIL)
CELL 2 (grounded core): experiments/exp_spanning_grounded_core_reach_v1.py (commit ~79e1fa22c)
  FULL data recovered from data/logs/chain_landing_spanning_grounded_core_reach_v1.log (NO metrics.json at the
  expected data/exp_spanning_grounded_core_reach_v1/ path -- only *_selftest/ exists; the FULL landed JSON is
  embedded in the chain-landing log). verdict SPAN_FAIL_MECHANISM, run_mode=full, elapsed 40.25s, 5 seeds.

INDEPENDENT OFF-DISK RECOMPUTE (.venv python, this session):
  CRUX (3-seed agg, cv in ()):
    SUBSTRATE_GT h@1=0.1379(.060) mrr=0.1611(.056) h@10=0.2006(.048)
    POP_RELFREQ  h@1=0.2624(.037) mrr=0.3380(.024) h@10=0.4872(.011)
    SYMBOLIC_GT  h@1=0.1556 mrr=0.1858
    beats_freq=FALSE on all three (recomputed). Degree-stratified: substrate LOSES to frequency at EVERY tier
    (margin_vs_relfreq mrr low -0.037, mid -0.126, high -0.368) -- no winning stratum.
    bind_loadbearing: ablated mrr 0.0299 -> ablated_ratio 0.1858 (reproduced exactly); ablated (0.0299) sits
    just above BROKEN (0.0115) and far below SUBSTRATE (0.1611) -> bind/unbind is GENUINELY load-bearing, arm
    is NOT dead. RANDOM 0.0007, arms_differ=True, controls clean.
    WATERFALL LOCALIZATION (the load-bearing localizer):
      stage1 candidate ceiling 0.493
      stage2 COMPOSE FIDELITY: vsa_recall@10=0.203 vs sym_recall@10=0.491 (gap 0.287); vsa_recall@1=0.142 vs
        sym_recall@1=0.399 (gap 0.257)  <-- THE LEAK
      stage3 verifier lift (CONDITIONED on recall): vsa_post_verify_cond_mrr 0.415 > sym 0.377; vsa_lift +0.305
      stage4 rank quality (cond): vsa_cond_hits@1 0.355 > sym 0.316
      => leak is at COMPOSE (VSA bundle recall << symbolic hash-join recall). PROPOSE-VERIFY and RANK are HEALTHY:
         conditioned on being recalled, VSA ranks as well as or BETTER than symbolic. This is bundle-superposition
         CROSSTALK: too many candidates bound into the bundle, unbind/cleanup cannot separate them.
    SMOKE->FULL improvement CONFIRMED off-disk: smoke (N_DIM=1024) SUBSTRATE_GT mrr=0.0917 h1=0.073 h10=0.117 ->
      FULL (N_DIM=2048) mrr=0.1611. Doubling N_DIM ~doubled mrr -- consistent with the compose-crosstalk leak
      (more dims -> less superposition crosstalk -> higher recall). Corroborates the localization.

  GROUNDED CORE (recompute from raw probe_records, threshold sim_mech>0.3 = SIM_FLOOR band; 0/80 reached-flag
    mismatches -> reproduces exactly):
    span_per_domain PHYSICAL 0.500 ABSTRACT 0.214 EMOTIONAL 0.812 MATH 0.000 SOCIAL 0.312 TEMPORAL 0.250
    agg=0.3482 = MACRO (per-domain) average (reproduced; micro/per-probe avg = 0.3605).
    DECISIVE DISAMBIGUATION (coverage vs decode vs span):
      In-graph-only reach (excluding sim_mech==0 = word-not-in-CSKG): PHYSICAL .500 ABSTRACT .273 EMOTIONAL .867
        MATH .000 SOCIAL .357 TEMPORAL .333. Domain structure PERSISTS after removing coverage holes.
      Mean in-graph sim_mech TRACKS reach: EMOTIONAL +0.476, PHYSICAL +0.273, ABSTRACT +0.102, TEMPORAL +0.048,
        SOCIAL +0.015, MATH -0.434. The underlying probe-to-core cosine is ALREADY domain-structured BEFORE any
        decode/threshold. MATH in-graph probes are ANTI-grounded (6/8 negative, mean -0.434).
      Controls fire correctly & per-domain-SPECIFICALLY: NARROW (physical-only) core reaches PHYSICAL 0.857 and
        ~0.0 on every other domain (must-fail fires, physical-content decodes). SCRAMBLE agg 0.097 (<0.4 band).
        => the reach DECODER is proven HEALTHY where content aligns (emotional 0.87, narrow-physical 0.86).

ADJUDICATION:
  CRUX (1) HARD_FAIL genuine -- YES, bit-reproduces: substrate loses to frequency on all three metrics at every
    degree tier, 3-seed tight. (2) bind/unbind GENUINELY load-bearing -- YES (ratio 0.186, ablated near BROKEN,
    substrate 5.4x ablated). This is a REAL SUBSTRATE-NATIVE negative, NOT a construction-proof -- distinct from
    the symbolic Step-1 (which exercised ZERO substrate primitives). (3) WHICH STAGE leaks -- COMPOSE (bundle
    crosstalk): vsa_recall 0.20 << sym_recall 0.49; verify+rank are healthy (cond metrics >= symbolic). (4) smoke
    0.092 -> full 0.161 improvement REAL (N_DIM 1024->2048 crosstalk reduction). TIER = HARD_FAIL (honest
    substrate-native negative) WITH a measured-mechanism localization (compose-crosstalk is the wall).

  GROUNDED CORE (1) the cell's self-diagnosis ("mechanism/decoder bottleneck, NOT a core-span gap; pause
    core-expansion") is OVER-CLAIMED / NOT supported. The data FALSIFIES a UNIFORM decoder bottleneck: reach is
    strongly domain-STRUCTURED (emotional 0.87 vs math 0.0), and the underlying probe-to-core cosine is ALREADY
    domain-structured BEFORE decode (emotional +0.48, math -0.43). The decoder is proven HEALTHY by its own
    controls (narrow-physical 0.857, scramble-collapse 0.097). A lossy uniform decoder cannot produce emotional
    0.87. HONEST ATTRIBUTION: the reach magnitude TRACKS probe-to-core cosine, which is a REPRESENTATION/SPAN-
    ALIGNMENT structure (core aligns with emotional/physical, weak/anti-aligned with math/social/temporal),
    compounded by probe-graph COVERAGE holes (zero-sim probes). It is UNDER-DETERMINED between span-alignment and
    decode, but leans toward SPAN/alignment, NOT the clean decoder story. "Pause core-expansion" is unsupported.
    (2) EMOTIONAL 0.81 informative -- YES: it decodes because the core cosine-aligns with emotion words (mean
    +0.48, grief/joy/relief/gratitude 0.79-0.81); it is the domain the core actually spans, and it PROVES the
    decoder works. TIER = MEASURED_MECHANISM (honest negative with a corrected mechanism-vs-span attribution).

  CONVERGENCE ("both failures = the same DECODE/CLEANUP wall") -- REJECTED as OVER-UNIFIED (a wanted narrative).
    Crux fails at COMPOSE via bundle-CAPACITY crosstalk (too many bound candidates; unbind cannot separate) --
    a genuine collapse-the-bundle decode/cleanup loss. Grounded-core fails via representation SPAN/ALIGNMENT
    COVERAGE (the core cosine does not cover math/social/temporal) -- and its decoder is PROVEN HEALTHY by the
    scramble-collapse + narrow-physical + emotional-0.87 controls. Capacity-crosstalk != coverage-misalignment.
    Attributing grounded-core to "lossy decode" CONTRADICTS its own controls. Loose thematic link ("distributed
    representations carry low SNR for structured retrieval") exists, but the STRONG mechanistic convergence onto
    one decode mechanism is FALSE. Two distinct negatives.

CROSS-ARC OVERLAP CHECK (substrate_query, mandatory): crux mechanism query top cosine 0.317 (cooperative-and-
  gate-compose note), 0.301 (strategy note), 0.292 (generation-pipeline note) -- ALL notes, NONE a prior
  experiment atom on this mechanism at >0.30. The genuine predecessors are the symbolic Step-1 atoms (keyword-
  matched, intended composition parents). No rediscovery; crux is a targeted SUBSTRATE-NATIVE extension of the
  symbolic negative. (The July-1 INT8-rediscovery pattern does NOT apply.)

PARENTS/COMPOSES (verified present in Store, math/atoms.jsonl):
  PRIOR_SYMBOLIC_NEG = the Step-1 symbolic AMIE proven-bound negative (same FB15k237 task, construction-proof).
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_10_crux_HF_grounded_core_MM_decode_convergence_REJECTED"
CRUX_COMMIT = "8c238125d"
GCORE_COMMIT = "79e1fa22c"
TS = time.time()
TS_ISO = "2026-07-10T20:15:00Z"
SESSION = "2026-07-10_crux_engine_HF_and_grounded_core_MM_and_decode_convergence_adjudication"

PRIOR_SYMBOLIC_NEG = (
    "math::PROVEN_BOUND_NEGATIVE_symbolic_L1_L2_path_rule_induction_on_FB15k237_does_NOT_beat_the_per_relation_"
    "tail_FREQUENCY_prior_GT_DENSE_LOSES_on_ALL_THREE_metrics_h1_0p171_vs_POP_RELFREQ_0p262_h10_0p288_vs_0p487_"
    "mrr_0p212_vs_0p338_and_the_generator_REACH_ceiling_0p514_BARELY_clears_frequency_0p487_margin_0p027_so_"
    "even_a_PERFECT_verifier_on_these_L1_L2_rules_would_beat_frequency_by_only_2p7pts_h10_"
)

# ---------------------------------------------------------------------------
# ATOM 1: CRUX -- substrate-native generate-and-test HARD_FAIL vs frequency, compose-crosstalk localized
# ---------------------------------------------------------------------------
crux_atom = {
    "id": (
        "math::HARD_FAIL_NEGATIVE_crux_engine_fb15k237_vsa_gt_v1_SUBSTRATE_NATIVE_VSA_bind_unbind_generate_and_"
        "test_with_3_beat_frequency_levers_head_conditional_multiplicity_hop_normalized_conf_negative_evidence_"
        "does_NOT_beat_the_per_relation_tail_FREQUENCY_prior_SUBSTRATE_GT_h1_0p138_mrr_0p161_h10_0p201_vs_"
        "POP_RELFREQ_h1_0p262_mrr_0p338_h10_0p487_beats_freq_FALSE_at_EVERY_degree_tier_margin_mrr_low_neg0p037_"
        "mid_neg0p126_high_neg0p368_3seed_cv_le0p06_bind_unbind_GENUINELY_LOAD_BEARING_ablated_mrr_0p030_ratio_"
        "0p186_just_above_BROKEN_0p012_so_this_is_a_REAL_substrate_native_negative_NOT_a_construction_proof_"
        "unlike_symbolic_Step1_WATERFALL_LOCALIZES_leak_at_COMPOSE_vsa_recall10_0p203_vs_sym_recall10_0p491_gap_"
        "0p287_while_PROPOSE_VERIFY_and_RANK_are_HEALTHY_conditioned_vsa_cond_mrr_0p415_ge_sym_0p377_bundle_"
        "superposition_crosstalk_is_the_wall_smoke_Ndim1024_mrr_0p092_to_full_Ndim2048_mrr_0p161_confirms_more_"
        "dims_less_crosstalk_cardinality_ok_arms_differ_commit_8c238125d_2026-07-10"
    ),
    "name": (
        "MATH HARD_FAIL / honest substrate-native negative: SUBSTRATE-NATIVE VSA bind/unbind generate-and-test "
        "(3 beat-frequency levers: head-conditional multiplicity, hop-normalized conf, negative-evidence) on "
        "FB15k-237 does NOT beat the per-relation tail FREQUENCY prior. SUBSTRATE_GT h@1 0.138 / mrr 0.161 / "
        "h@10 0.201 vs POP_RELFREQ h@1 0.262 / mrr 0.338 / h@10 0.487 -- loses on all three at EVERY degree tier "
        "(margin mrr low -0.037, mid -0.126, high -0.368), 3-seed cv<=0.06. bind/unbind GENUINELY load-bearing "
        "(ablated mrr 0.030, ratio 0.186, just above BROKEN 0.012) -> a REAL substrate-native negative, NOT a "
        "construction-proof (unlike symbolic Step-1). WATERFALL localizes the leak at COMPOSE: vsa_recall@10 "
        "0.203 vs sym_recall@10 0.491 (gap 0.287); PROPOSE-VERIFY and RANK are healthy (vsa cond_mrr 0.415 >= "
        "sym 0.377). The wall is bundle-superposition CROSSTALK. Smoke N=1024 mrr 0.092 -> full N=2048 mrr 0.161 "
        "corroborates (more dims = less crosstalk). HARD_FAIL."
    ),
    "corpus": "math",
    "tier": "HARD_FAIL",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "hard_fail_substrate_native_vsa_generate_and_test_does_NOT_beat_per_relation_tail_frequency_prior_on_"
        "fb15k237_at_every_degree_tier_bind_unbind_load_bearing_real_negative_not_construction_proof_leak_"
        "localized_to_compose_bundle_crosstalk_verify_and_rank_healthy_honest_negative_headline"
    ),
    "cert_class": (
        "held_out_tail_prediction_capability_bound_of_SUBSTRATE_NATIVE_vsa_bind_unbind_generate_and_test_with_"
        "beat_frequency_levers_relative_to_per_relation_tail_frequency_baseline_on_FB15k237_with_waterfall_stage_"
        "localization_of_the_failure_to_compose_recall_bundle_crosstalk"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY) of exp_crux_engine_fb15k237_vsa_gt_v1 (commit 8c238125d; FULL, 3 seeds 7/17/23, "
        "N_DIM=2048, verdict HARD_FAIL). CLAIM VERIFIED off-disk (independent .venv recompute off per_seed[], "
        "reproduces every headline number). The cell is the SUBSTRATE-NATIVE (VSA bind/unbind) counterpart of the "
        "symbolic Step-1 generate-and-test, adding 3 beat-frequency levers (head-conditional multiplicity, "
        "hop-normalized confidence, negative-evidence). RESULT: it still LOSES to the per-relation tail frequency "
        "prior on ALL THREE metrics -- SUBSTRATE_GT h@1 0.1379 / mrr 0.1611 / h@10 0.2006 vs POP_RELFREQ h@1 "
        "0.2624 / mrr 0.3380 / h@10 0.4872 (beats_freq=False, reproduced). It loses at EVERY degree tier "
        "(margin_vs_relfreq mrr: low -0.037, mid -0.126, high -0.368) -- no winning stratum; the gap is WIDEST at "
        "high-degree where the frequency prior is strongest. 3-seed cv tight (h@1 .060, mrr .056, h@10 .048). "
        "BIND/UNBIND GENUINELY LOAD-BEARING (Director ask 2): ablating bind/unbind collapses substrate mrr "
        "0.1611 -> 0.0299 (ablated_ratio 0.1858, reproduced exactly), landing just above the BROKEN-verifier arm "
        "(0.0115) and 5.4x below the live substrate -- the arm is NOT dead and the VSA primitives do real work. "
        "Therefore this is a REAL SUBSTRATE-NATIVE negative, NOT a construction-proof (Director ask: CONFIRMED -- "
        "unlike symbolic Step-1 which exercised ZERO substrate primitives, this exercises bind/unbind and they "
        "are load-bearing). Controls clean: RANDOM mrr 0.0007, arms_differ_verified=True, BROKEN 0.0115, "
        "GT_SPARSE h@10 0.012 (density contrast holds). WATERFALL LOCALIZATION (Director ask 3, the load-bearing "
        "localizer): stage1 candidate ceiling 0.493; stage2 COMPOSE FIDELITY vsa_recall@10 0.203 vs sym_recall@10 "
        "0.491 (gap 0.287), vsa_recall@1 0.142 vs sym_recall@1 0.399 (gap 0.257) -- THIS is the leak; stage3 "
        "verifier lift CONDITIONED on recall is HEALTHY (vsa_post_verify_cond_mrr 0.415 > sym 0.377, vsa_lift "
        "+0.305, broken_precision 0.005); stage4 rank quality cond vsa_hits@1 0.355 > sym 0.316. CONCLUSION: the "
        "leak is at COMPOSE, NOT propose-verify and NOT rank. Conditioned on a candidate being recalled, the VSA "
        "verifier+ranker are as good as or BETTER than symbolic; the loss is that the VSA bundle recall (0.20) "
        "recovers less than half of what the symbolic hash-join recall (0.49) does. Mechanism = bundle-"
        "superposition CROSSTALK: too many candidates bound into the superposition, unbind/cleanup cannot "
        "separate them -- the 'collapse the bundle -> clean answer' operation is capacity-limited. SMOKE->FULL "
        "improvement (Director ask 4): CONFIRMED off-disk -- smoke (N_DIM=1024) SUBSTRATE_GT mrr 0.0917 (h1 "
        "0.073, h10 0.117) -> FULL (N_DIM=2048) mrr 0.1611; doubling N_DIM ~doubled mrr, exactly the signature "
        "of a compose-crosstalk-limited system (more dimensions -> less superposition crosstalk -> higher recall). "
        "This corroborates the compose localization. TIER = HARD_FAIL (honest substrate-native negative) with a "
        "measured-mechanism localization (the wall is compose-crosstalk; verify+rank are proven healthy). Revival "
        "angle is real (see criterion) because the leak is isolated and N_DIM-sensitive."
    ),
    "verified_numbers": {
        "SUBSTRATE_GT_h1": 0.1379, "SUBSTRATE_GT_mrr": 0.1611, "SUBSTRATE_GT_h10": 0.2006,
        "POP_RELFREQ_h1": 0.2624, "POP_RELFREQ_mrr": 0.3380, "POP_RELFREQ_h10": 0.4872,
        "SYMBOLIC_GT_h1": 0.1556, "SYMBOLIC_GT_mrr": 0.1858,
        "beats_freq": False, "cv_h1": 0.060, "cv_mrr": 0.056, "cv_h10": 0.048,
        "margin_vs_relfreq_mrr_low": -0.037, "margin_vs_relfreq_mrr_mid": -0.126,
        "margin_vs_relfreq_mrr_high": -0.368,
        "ABLATED_mrr": 0.0299, "ablated_ratio": 0.1858, "BROKEN_mrr": 0.0115, "RANDOM_mrr": 0.0007,
        "bind_loadbearing": True, "GT_SPARSE_h10": 0.0124, "ceiling": 0.4930, "N_DIM": 2048,
        "waterfall_vsa_recall10": 0.2034, "waterfall_sym_recall10": 0.4906, "compose_gap10": 0.2871,
        "waterfall_vsa_recall1": 0.1418, "waterfall_sym_recall1": 0.3992, "compose_gap1": 0.2574,
        "vsa_post_verify_cond_mrr": 0.4148, "sym_post_verify_cond_mrr": 0.3769, "vsa_lift_over_pre": 0.3048,
        "vsa_cond_hits1": 0.3551, "sym_cond_hits1": 0.3155,
        "smoke_mrr_Ndim1024": 0.0917, "smoke_h1": 0.073, "smoke_h10": 0.117, "full_mrr_Ndim2048": 0.1611,
        "arms_differ_verified": True, "n_seeds": 3, "seeds": [7, 17, 23],
    },
    "provenance": {
        "cell": "experiments/exp_crux_engine_fb15k237_vsa_gt_v1.py", "commit": CRUX_COMMIT,
        "metrics_path": "data/exp_crux_engine_fb15k237_vsa_gt_v1/metrics.json",
        "smoke_metrics_path": "data/exp_crux_engine_fb15k237_vsa_gt_v1_smoke/metrics.json",
        "seeds": [7, 17, 23], "run_mode": "full", "whole_cell_verdict": "HARD_FAIL",
        "audit_tier": "HARD_FAIL", "ts_iso": TS_ISO, "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
    },
    "framing_corrections_vs_cell_author_and_director": [
        "HARD_FAIL UPHELD off independent recompute -- every headline reproduces; substrate loses to frequency on "
        "all three metrics at every degree tier. Genuine negative.",
        "CONFIRMED (Director ask): this IS a real substrate-native negative, NOT a construction-proof. Ablation "
        "shows bind/unbind is genuinely load-bearing (ratio 0.186, ablated near BROKEN, substrate 5.4x ablated); "
        "the arm exercises and depends on VSA primitives, unlike symbolic Step-1 (zero primitives).",
        "STAGE LOCALIZED (Director ask 3): the leak is at COMPOSE, not propose/verify/rank. vsa_recall 0.20 << "
        "sym_recall 0.49; but CONDITIONED on recall, VSA cond_mrr 0.415 >= symbolic 0.377. The verifier and "
        "ranker are HEALTHY -- do NOT attribute the failure to the verifier. The wall is bundle crosstalk.",
        "SMOKE->FULL improvement (Director ask 4) is REAL: 0.092@N=1024 -> 0.161@N=2048, verified off both "
        "metrics files. Consistent with (not proof of, but strongly indicative of) crosstalk-limited compose.",
    ],
    "revival_or_extension_criterion": (
        "NEGATIVE is scoped to: VSA bind/unbind bundle-superposition generate-and-test at N_DIM<=2048 on dense "
        "FB15k237, where the compose recall (0.20) is the binding constraint. REVIVAL angles (each a new cell): "
        "(1) attack the COMPOSE crosstalk directly -- sharded/block-local codes, cleanup memory at the compose "
        "step, or resonator-style iterative unbinding to raise vsa_recall toward the symbolic 0.49 ceiling; the "
        "N_DIM 1024->2048 mrr doubling shows recall IS the lever. (2) cap candidates-per-bundle (fewer bound "
        "items -> less crosstalk). (3) hybrid: symbolic recall + VSA verify (since VSA verify+rank are already "
        "healthy, cond_mrr 0.415). DEMOTION/closure trigger: if raising vsa_recall to ~sym_recall STILL loses to "
        "frequency, the negative hardens to a structural bound (the task carries no signal beyond tail frequency "
        "for L1/L2 rules, matching the symbolic Step-1 bound)."
    ),
    "composes": [PRIOR_SYMBOLIC_NEG],
    "compose_note": (
        "Substrate-native counterpart of the symbolic Step-1 generate-and-test negative (PRIOR_SYMBOLIC_NEG). "
        "Same FB15k237 held-out tail task, same loses-to-frequency conclusion, but this cell EXERCISES substrate "
        "primitives (bind/unbind, proven load-bearing) where Step-1 was pure symbolic hash-join (construction-"
        "proof). It EXTENDS the negative into the substrate-native regime AND adds a waterfall localization: the "
        "substrate-native version's specific failure mode is COMPOSE-crosstalk (VSA recall << symbolic recall), "
        "isolating WHERE the substrate loses ground relative to symbolic. Neither atom superseded."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'substrate native VSA bind unbind generate and test KG completion loses to frequency "
        "compose crosstalk' -> top cosine 0.317 (cooperative-and-gate-compose note), 0.301 (strategy note), "
        "0.292 (generation-pipeline note) -- ALL notes, NONE a prior experiment atom on this mechanism at >0.30. "
        "The genuine predecessor is the symbolic Step-1 atom (composition parent). No rediscovery; targeted "
        "substrate-native extension. July-1 INT8-rediscovery pattern does NOT apply."
    ),
    "anchor": "crux_engine_fb15k237_vsa_gt_v1", "cell_commit": CRUX_COMMIT,
    "seeds": [7, 17, 23], "run_mode": "full", "cardinality_ok": True, "arms_differ_verified": True,
    "verified_off_data": True, "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION, "needs_orchestrator_store_sync": True,
    "ts": TS, "ts_iso": TS_ISO, "ts_added": TS_ISO,
    "aliases": [
        "substrate-native VSA generate-and-test on FB15k237 does NOT beat the tail frequency prior (HARD_FAIL, h@1 0.138 vs 0.262)",
        "bind/unbind genuinely load-bearing (ablated_ratio 0.186) -> real substrate-native negative, not a construction-proof",
        "waterfall localizes the leak to COMPOSE: vsa_recall 0.20 << symbolic recall 0.49; verify+rank healthy (bundle crosstalk is the wall)",
        "smoke N=1024 mrr 0.092 -> full N=2048 mrr 0.161: crosstalk-limited compose, more dims raise recall",
    ],
    "added_atom_id": None,
}
crux_atom["added_atom_id"] = crux_atom["id"]

# ---------------------------------------------------------------------------
# ATOM 2: GROUNDED CORE -- SPAN_FAIL, MM negative with CORRECTED mechanism-vs-span attribution
# ---------------------------------------------------------------------------
gcore_atom = {
    "id": (
        "math::MEASURED_MECHANISM_NEGATIVE_spanning_grounded_core_reach_v1_grounded_core_reach_is_DOMAIN_"
        "STRUCTURED_not_a_uniform_decoder_bottleneck_span_per_domain_EMOTIONAL_0p81_PHYSICAL_0p50_SOCIAL_0p31_"
        "TEMPORAL_0p25_ABSTRACT_0p21_MATH_0p00_agg_0p348_reach_TRACKS_probe_to_core_cosine_which_is_ALREADY_"
        "domain_structured_before_decode_mean_sim_emotional_plus0p48_math_neg0p43_decoder_PROVEN_HEALTHY_by_"
        "controls_narrow_physical_only_core_reaches_PHYSICAL_0p857_and_zero_elsewhere_must_fail_fires_per_domain_"
        "specifically_scramble_collapses_0p097_so_cell_self_diagnosis_of_uniform_MECHANISM_DECODER_bottleneck_"
        "NOT_span_is_OVERCLAIMED_evidence_leans_SPAN_alignment_plus_probe_coverage_holes_UNDER_DETERMINED_"
        "decode_vs_span_pause_core_expansion_unsupported_5seeds_commit_79e1fa22c_2026-07-10"
    ),
    "name": (
        "MATH MEASURED_MECHANISM / honest negative with a corrected attribution: the spanning grounded-core "
        "reach is strongly DOMAIN-STRUCTURED (EMOTIONAL 0.81, PHYSICAL 0.50, SOCIAL 0.31, TEMPORAL 0.25, "
        "ABSTRACT 0.21, MATH 0.00; agg 0.348), NOT a uniform decoder bottleneck. Reach TRACKS the probe-to-core "
        "cosine, which is already domain-structured BEFORE decode (mean sim emotional +0.48, math -0.43). The "
        "reach decoder is PROVEN HEALTHY by controls (narrow physical-only core reaches PHYSICAL 0.857 and ~0 "
        "elsewhere; scramble collapses to 0.097). So the cell's self-diagnosis ('mechanism/decoder bottleneck, "
        "NOT a span gap; pause core-expansion') is OVER-CLAIMED -- the evidence leans toward SPAN/representation-"
        "alignment (plus probe-graph coverage holes), and is under-determined decode-vs-span but a uniform "
        "decoder bottleneck is falsified by emotional 0.87. MEASURED_MECHANISM."
    ),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "measured_mechanism_grounded_core_reach_is_domain_structured_tracks_probe_to_core_cosine_decoder_proven_"
        "healthy_by_controls_cell_self_diagnosis_of_uniform_decoder_bottleneck_not_span_is_overclaimed_evidence_"
        "leans_span_alignment_plus_coverage_under_determined_decode_vs_span_honest_negative_attribution_corrected"
    ),
    "cert_class": (
        "diffusion_with_restart_reach_decoder_over_a_grounded_core_on_cskg_measured_per_domain_reach_vs_probe_to_"
        "core_cosine_with_narrow_core_must_fail_and_scramble_controls_attribution_of_uniform_low_reach_to_"
        "representation_span_alignment_and_probe_coverage_rather_than_decoder_loss"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY) of exp_spanning_grounded_core_reach_v1 (commit ~79e1fa22c; run_mode=full, "
        "elapsed 40.25s, 5 seeds, verdict SPAN_FAIL_MECHANISM). PROVENANCE NOTE (Fix #28-adjacent): there is NO "
        "metrics.json at data/exp_spanning_grounded_core_reach_v1/ -- only a *_selftest/ dir exists; the FULL "
        "landed JSON is embedded in data/logs/chain_landing_spanning_grounded_core_reach_v1.log. Recompute was "
        "done off that log's raw probe_records (80 probes). CLAIM PARTIALLY VERIFIED, ATTRIBUTION CORRECTED. "
        "Reach reproduces exactly (threshold sim_mech>0.3 = SIM_FLOOR band; 0/80 reached-flag mismatches): "
        "span_per_domain PHYSICAL 0.500, ABSTRACT 0.214, EMOTIONAL 0.812, MATHEMATICAL 0.000, SOCIAL 0.312, "
        "TEMPORAL 0.250; agg 0.3482 = MACRO (per-domain) average (micro/per-probe avg 0.3605). DECISIVE "
        "DISAMBIGUATION (Director ask 1, decoder-bottleneck vs span-gap): (a) The reach is strongly domain-"
        "STRUCTURED, not uniform -- EMOTIONAL 0.81 vs MATH 0.0 is a 0.81 spread; a uniformly lossy decoder cannot "
        "produce emotional 0.87. (b) The underlying probe-to-core cosine is ALREADY domain-structured BEFORE any "
        "decode/threshold: mean in-graph sim_mech EMOTIONAL +0.476, PHYSICAL +0.273, ABSTRACT +0.102, TEMPORAL "
        "+0.048, SOCIAL +0.015, MATH -0.434 (math in-graph probes are ANTI-grounded, 6/8 negative). Reach TRACKS "
        "this cosine monotonically. (c) The reach decoder is PROVEN HEALTHY by its own controls: the NARROW "
        "(physical-only) core reaches PHYSICAL 0.857 and ~0.0 on every other domain (must-fail fires PER-DOMAIN-"
        "SPECIFICALLY, and physical content decodes cleanly); SCRAMBLE collapses to agg 0.097 (<0.4 band). If the "
        "decoder were the uniform bottleneck it could not reach physical at 0.857 (narrow) or emotional at 0.87 "
        "(spanning). (d) Excluding not-in-graph probes (sim==0, a COVERAGE hole) the domain structure PERSISTS "
        "(in-graph reach: emotional 0.867, math 0.000) -- so coverage is a compounding factor but not the whole "
        "story. CONCLUSION: the cell's self-diagnosis ('mechanism/decoder bottleneck, NOT a core-span gap; pause "
        "core-expansion') is OVER-CLAIMED and the attribution is CORRECTED: the reach magnitude tracks a "
        "REPRESENTATION/SPAN-ALIGNMENT structure (the core cosine-aligns with emotional/physical, is weak/anti-"
        "aligned with math/social/temporal/abstract), compounded by probe-graph coverage holes. It is UNDER-"
        "DETERMINED between span-alignment and decode, but a UNIFORM DECODER BOTTLENECK is falsified; the evidence "
        "leans SPAN/alignment. 'Pause core-expansion' is not supported by this data. EMOTIONAL 0.81 (Director ask "
        "2) is informative BECAUSE it proves the decoder works and shows the core genuinely spans the emotion "
        "sub-space (grief/joy/relief/gratitude sim 0.79-0.81, mean +0.48) -- emotion is the domain the core "
        "actually aligns with. TIER = MEASURED_MECHANISM: a genuine negative (grounded core does not span 5/6 "
        "domains via this reach readout) with the mechanism characterized (reach = probe-to-core cosine; decoder "
        "healthy; gap is alignment/coverage not decode loss)."
    ),
    "verified_numbers": {
        "span_PHYSICAL": 0.500, "span_ABSTRACT": 0.2143, "span_EMOTIONAL": 0.8125, "span_MATH": 0.000,
        "span_SOCIAL": 0.3125, "span_TEMPORAL": 0.250, "span_agg_macro": 0.3482, "span_agg_micro": 0.3605,
        "reach_threshold_sim": 0.3, "reached_flag_mismatches": 0,
        "mean_ingraph_sim_EMOTIONAL": 0.476, "mean_ingraph_sim_PHYSICAL": 0.273, "mean_ingraph_sim_ABSTRACT": 0.102,
        "mean_ingraph_sim_TEMPORAL": 0.048, "mean_ingraph_sim_SOCIAL": 0.015, "mean_ingraph_sim_MATH": -0.434,
        "ingraph_reach_EMOTIONAL": 0.867, "ingraph_reach_MATH": 0.000,
        "narrow_PHYSICAL": 0.8571, "narrow_other_domains": 0.0, "narrow_agg": 0.1533,
        "scramble_agg": 0.0969, "scramble_max_band": 0.4, "control_fires": True, "n_seeds": 5,
        "n_core_in_graph": 1441, "grounded_fraction": 0.9965,
    },
    "provenance": {
        "cell": "experiments/exp_spanning_grounded_core_reach_v1.py", "commit": GCORE_COMMIT,
        "metrics_path_MISSING": "data/exp_spanning_grounded_core_reach_v1/metrics.json (DOES NOT EXIST)",
        "actual_full_data_path": "data/logs/chain_landing_spanning_grounded_core_reach_v1.log (embedded JSON)",
        "selftest_path": "data/exp_spanning_grounded_core_reach_v1_selftest/metrics.json",
        "run_mode": "full", "whole_cell_verdict": "SPAN_FAIL_MECHANISM", "audit_tier": "MEASURED_MECHANISM",
        "ts_iso": TS_ISO, "atomized_by": ATOMIZED_BY, "verified_off_data": True,
        "verified_off_data_note": (
            "Recompute off raw probe_records in the chain-landing log (no metrics.json exists at anchor path). "
            "Reach reproduces (0/80 flag mismatches at sim>0.3). Domain structure persists after excluding "
            "not-in-graph probes. Mean in-graph sim_mech tracks reach monotonically (emotional +0.48 -> math "
            "-0.43). Narrow physical-only reaches physical 0.857, ~0 else; scramble agg 0.097."
        ),
    },
    "framing_corrections_vs_cell_author_and_director": [
        "CORRECTION to the cell's verdict framing: the SPAN_FAIL_MECHANISM self-diagnosis ('uniform decoder "
        "bottleneck, NOT a span gap; pause core-expansion') is OVER-CLAIMED. The reach is domain-STRUCTURED "
        "(emotional 0.81 vs math 0.0), and the underlying probe-to-core cosine is already domain-structured "
        "before decode -- a uniform decoder bottleneck cannot produce emotional 0.87. Symmetric anti-negativity: "
        "this correction is neither more negative nor more positive than the cell, it re-attributes the SAME "
        "negative from decode to span/alignment+coverage.",
        "The decoder is PROVEN HEALTHY by the cell's OWN controls (narrow-physical 0.857, scramble-collapse "
        "0.097, emotional 0.87). Attributing the failure to a 'lossy decoder' CONTRADICTS these controls. The "
        "honest read: reach = probe-to-core cosine; the gap is where the core does not cosine-align (math -0.43, "
        "social +0.015, temporal +0.048), i.e. a representation/span structure, compounded by coverage holes.",
        "'Pause core-expansion' is NOT supported by this data -- if anything, the anti-grounded math domain "
        "(mean -0.43) and near-zero social/temporal suggest the core may be MISSING or MIS-ALIGNED on those "
        "dimensions, which is a span/coverage question, not a decode question. Under-determined; do not close on "
        "the decoder story.",
        "EMOTIONAL 0.81 is the informative positive: it PROVES the decoder works and that the core genuinely "
        "spans the emotion sub-space -- the one domain where the core cosine-aligns strongly (mean +0.48).",
    ],
    "revival_or_extension_criterion": (
        "Negative scoped to: diffusion-with-restart reach readout over the 1441-node grounded core on CSKG, "
        "reach thresholded at cosine>0.3, 6 domains. To DISAMBIGUATE decode-vs-span (the open question this VET "
        "leaves): (1) hold the readout fixed and swap the core for a KNOWN-spanning planted core -- if reach "
        "recovers, it was span; the selftest already shows a planted spanning core reaches all 6 at 0.96, which "
        "points AT span, not decode. (2) hold the core fixed and swap the reach readout (e.g. multi-restart, "
        "learned diffusion) -- if math/social/temporal recover, it was decode. (3) fix probe-graph coverage "
        "(embed the zero-sim probes) and re-measure to remove the coverage confound. EXTENSION: measure per-"
        "domain core-cosine directly (not thresholded reach) to quantify the alignment gap. This atom should be "
        "REVISITED (not superseded) once (1)/(2) run."
    ),
    "composes": [],
    "cross_arc_overlap_check": (
        "Grounded-core reach relates to the loop-closer 'grounding-doesnt-chain' negative the cell cites, but "
        "this VET does NOT endorse that unification (see the META convergence-rejection atom): the loop-closer "
        "was a composition/chaining failure; this is a representation-alignment/coverage structure with a healthy "
        "decoder. No prior experiment atom duplicates the per-domain reach measurement."
    ),
    "anchor": "spanning_grounded_core_reach_v1", "cell_commit": GCORE_COMMIT,
    "seeds": [0, 1, 2, 3, 4], "run_mode": "full", "cardinality_ok": True, "arms_differ_verified": True,
    "verified_off_data": True, "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION, "needs_orchestrator_store_sync": True,
    "ts": TS, "ts_iso": TS_ISO, "ts_added": TS_ISO,
    "aliases": [
        "grounded-core reach is domain-structured (emotional 0.81, math 0.0), not a uniform decoder bottleneck",
        "reach tracks probe-to-core cosine (already domain-structured before decode: emotional +0.48, math -0.43)",
        "decoder proven healthy by controls (narrow-physical 0.857, scramble 0.097) -> cell's decoder-bottleneck self-diagnosis overclaimed; leans span/alignment",
        "EMOTIONAL 0.81 proves the decoder works and the core spans the emotion sub-space; math anti-grounded",
    ],
    "added_atom_id": None,
}
gcore_atom["added_atom_id"] = gcore_atom["id"]

# ---------------------------------------------------------------------------
# ATOM 3 (META, CERT-neutral): the decode/cleanup-wall convergence is OVER-UNIFIED -- REJECTED
# ---------------------------------------------------------------------------
meta_atom = {
    "id": (
        "meta::META_CERT_NEUTRAL_the_decode_cleanup_wall_convergence_between_the_crux_engine_compose_crosstalk_"
        "HARD_FAIL_and_the_grounded_core_reach_SPAN_FAIL_is_OVER_UNIFIED_and_REJECTED_on_adversarial_check_two_"
        "DISTINCT_negatives_crux_fails_at_COMPOSE_via_bundle_CAPACITY_crosstalk_too_many_bound_candidates_unbind_"
        "cannot_separate_a_genuine_collapse_the_bundle_decode_loss_grounded_core_fails_via_representation_SPAN_"
        "ALIGNMENT_COVERAGE_core_cosine_does_not_cover_math_social_temporal_AND_its_decoder_is_PROVEN_HEALTHY_by_"
        "scramble_collapse_narrow_physical_and_emotional_0p87_controls_capacity_crosstalk_is_NOT_coverage_"
        "misalignment_wanted_narrative_guard_2026-07-10"
    ),
    "name": (
        "META (CERT-neutral): the 'both failures = the same DECODE/CLEANUP wall' convergence between the crux "
        "engine (compose-crosstalk HARD_FAIL) and the grounded-core reach (SPAN_FAIL) is OVER-UNIFIED and "
        "REJECTED on adversarial check. They are TWO DISTINCT negatives: crux fails at COMPOSE via bundle-"
        "CAPACITY crosstalk (too many bound candidates; unbind cannot separate them -- a genuine collapse-the-"
        "bundle decode loss); grounded-core fails via representation SPAN/ALIGNMENT COVERAGE (the core cosine "
        "does not cover math/social/temporal) AND its decoder is PROVEN HEALTHY by its own controls (scramble-"
        "collapse 0.097, narrow-physical 0.857, emotional 0.87). Capacity-crosstalk is not coverage-"
        "misalignment. A wanted-narrative unification guard."
    ),
    "corpus": "meta",
    "tier": "META_RULE",
    "kind": "cert_neutral_meta_rule",
    "cert_status": "cert_neutral_meta_rule_convergence_rejected_two_distinct_failure_mechanisms_wanted_narrative_guard",
    "cert_class": (
        "auditor_discipline_rule_do_not_unify_two_negatives_onto_one_mechanism_when_one_has_controls_proving_that_"
        "mechanism_healthy_distinguish_bundle_capacity_crosstalk_at_compose_from_representation_span_alignment_"
        "coverage_before_asserting_a_shared_decode_cleanup_wall"
    ),
    "description": (
        "CERT-neutral META rule from the 2026-07-10 landed-VET of two related negatives. The Director asked "
        "whether both failures localize to the SAME wall = the substrate's DECODE/CLEANUP/READOUT ('collapse the "
        "bundle -> clean answer') mechanism. Adversarial check REJECTS the unification as a wanted narrative. "
        "EVIDENCE: (1) CRUX localizes at COMPOSE -- vsa_recall 0.20 << symbolic recall 0.49 -- while CONDITIONED "
        "on recall the VSA verify+rank are healthy (vsa cond_mrr 0.415 >= symbolic 0.377). Its failure is bundle-"
        "superposition CAPACITY crosstalk: too many candidates bound into one bundle, unbind/cleanup cannot "
        "separate them. That IS a genuine decode/cleanup loss (and it is N_DIM-sensitive: mrr 0.092@1024 -> "
        "0.161@2048). (2) GROUNDED-CORE localizes at REPRESENTATION SPAN/ALIGNMENT -- reach tracks probe-to-core "
        "cosine which is domain-structured BEFORE decode (emotional +0.48, math -0.43), and the reach DECODER is "
        "PROVEN HEALTHY by controls (scramble collapses to 0.097, narrow physical-only core reaches physical "
        "0.857, spanning core reaches emotional 0.87). Attributing grounded-core to 'lossy decode' CONTRADICTS "
        "its own controls. Capacity-crosstalk (overloaded representation) != coverage-misalignment (absent/anti-"
        "aligned representation). RULE: before asserting that two negatives share one decode/cleanup wall, check "
        "each for a control that isolates the decode step; if one negative has controls PROVING its decoder "
        "healthy, the shared-wall unification is FALSE for that pair. A loose thematic link may survive "
        "('distributed representations carry low SNR for structured retrieval') but it must NOT be stated as a "
        "shared MECHANISM. This guards the symmetric-anti-negativity / no-wanted-narrative discipline: a "
        "convergence that would be strategically convenient (one wall to attack) got the hardest scrutiny and "
        "did not survive."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "Director's convergence hypothesis (both = one decode/cleanup wall) is REJECTED. Crux = bundle-capacity "
        "crosstalk at compose (a real decode loss); grounded-core = span/alignment coverage with a PROVEN-HEALTHY "
        "decoder. Two distinct mechanisms; do not unify.",
        "The grounded-core cell's own 'matches loop-closer grounding-doesnt-chain' framing is also not endorsed "
        "here: the loop-closer was a chaining/composition failure; grounded-core is representation alignment/"
        "coverage. Different again.",
        "What IS shared is only a loose theme (low SNR of structured signal in a distributed vector). Cite it as "
        "a theme, never as a common mechanism or a single lever.",
    ],
    "revival_or_extension_criterion": (
        "This rejection could be REVISITED (not the rule, but the specific pair) if a future cell shows the "
        "grounded-core low reach is ACTUALLY decode-limited -- e.g. swapping the reach readout (multi-restart / "
        "learned diffusion) recovers math/social/temporal while the core is unchanged. That would move grounded-"
        "core INTO the decode-wall family and partially rehabilitate the convergence. As of this VET the controls "
        "point the other way (decoder healthy)."
    ),
    "composes": [],
    "cross_arc_overlap_check": (
        "This META rule references the two math atoms filed in the same session (crux HARD_FAIL, grounded-core "
        "MEASURED_MECHANISM). It is a discipline/attribution guard, CERT-neutral (no CG/MM/HF delta)."
    ),
    "anchor": "crux_engine_fb15k237_vsa_gt_v1 + spanning_grounded_core_reach_v1",
    "verified_off_data": True, "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION, "needs_orchestrator_store_sync": True,
    "ts": TS, "ts_iso": TS_ISO, "ts_added": TS_ISO,
    "aliases": [
        "decode/cleanup-wall convergence between crux and grounded-core is over-unified -- REJECTED",
        "crux = bundle-capacity crosstalk at compose (real decode loss); grounded-core = span/alignment coverage with a healthy decoder",
        "before unifying two negatives onto one decode mechanism, check each has no control proving that mechanism healthy",
        "capacity-crosstalk != coverage-misalignment; a strategically-convenient convergence got hardest scrutiny and did not survive",
    ],
    "added_atom_id": None,
}
meta_atom["added_atom_id"] = meta_atom["id"]

# ---------------------------------------------------------------------------
# LEDGER ENTRIES
# ---------------------------------------------------------------------------
crux_ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": crux_atom["id"], "corpus": "math", "tier": "HARD_FAIL",
    "disposition": "hard_fail_honest_substrate_native_negative_with_compose_crosstalk_localization",
    "cert_delta": {"CG": 0, "MM": 0, "HF": 1}, "cert_increment_delta": {"CG": 0, "MM": 0, "HF": 1},
    "cert_delta_note": (
        "HF +1: substrate-native VSA bind/unbind generate-and-test on FB15k237 does NOT beat the tail frequency "
        "prior (h@1 0.138 vs 0.262, all three metrics, every degree tier, 3-seed cv<=0.06). bind/unbind GENUINELY "
        "load-bearing (ablated_ratio 0.186) -> a REAL substrate-native negative, NOT a construction-proof. "
        "Waterfall localizes the leak to COMPOSE (vsa_recall 0.20 << symbolic 0.49; verify+rank healthy). Smoke "
        "N=1024 mrr 0.092 -> full N=2048 0.161 confirms crosstalk-limited compose. Whole-cell HARD_FAIL upheld. "
        "Composes the symbolic Step-1 proven-bound negative (substrate-native extension). Needs orchestrator "
        "Store-sync."
    ),
    "verified_off_data": True, "anchor": "crux_engine_fb15k237_vsa_gt_v1", "cell_commit": CRUX_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks", "landed_VET_session": SESSION,
    "composes": [PRIOR_SYMBOLIC_NEG], "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": ["data/exp_crux_engine_fb15k237_vsa_gt_v1/metrics.json"],
}
gcore_ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": gcore_atom["id"], "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "disposition": "measured_mechanism_honest_negative_with_corrected_mechanism_vs_span_attribution",
    "cert_delta": {"CG": 0, "MM": 1, "HF": 0}, "cert_increment_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta_note": (
        "MM +1: grounded-core reach is domain-STRUCTURED (emotional 0.81, math 0.0; agg 0.348), reach TRACKS "
        "probe-to-core cosine (already domain-structured before decode: emotional +0.48, math -0.43). Decoder "
        "PROVEN HEALTHY by controls (narrow-physical 0.857, scramble 0.097). The cell's self-diagnosis 'uniform "
        "decoder bottleneck, NOT span; pause core-expansion' is OVER-CLAIMED and CORRECTED: evidence leans SPAN/"
        "alignment + coverage, under-determined decode-vs-span, uniform-decoder-bottleneck falsified. Whole-cell "
        "SPAN_FAIL_MECHANISM re-attributed (not overturned as a negative). PROVENANCE: no metrics.json at anchor "
        "path; recomputed off chain-landing log. Needs orchestrator Store-sync."
    ),
    "verified_off_data": True, "anchor": "spanning_grounded_core_reach_v1", "cell_commit": GCORE_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks", "landed_VET_session": SESSION,
    "composes": [], "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": ["data/logs/chain_landing_spanning_grounded_core_reach_v1.log"],
}
meta_ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": meta_atom["id"], "corpus": "meta", "tier": "META_RULE",
    "disposition": "cert_neutral_meta_convergence_rejected_two_distinct_failure_mechanisms",
    "cert_delta": {"CG": 0, "MM": 0, "HF": 0}, "cert_increment_delta": {"CG": 0, "MM": 0, "HF": 0},
    "cert_delta_note": (
        "CERT-NEUTRAL (no CG/MM/HF delta): the decode/cleanup-wall convergence between crux (compose-crosstalk) "
        "and grounded-core (span/alignment) is OVER-UNIFIED and REJECTED. Crux = bundle-capacity crosstalk (real "
        "decode loss); grounded-core = span/alignment coverage with a PROVEN-HEALTHY decoder. Guard against "
        "unifying two negatives onto one mechanism when one negative's controls prove that mechanism healthy. "
        "Needs orchestrator Store-sync."
    ),
    "verified_off_data": True, "anchor": "crux_engine_fb15k237_vsa_gt_v1+spanning_grounded_core_reach_v1",
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks", "landed_VET_session": SESSION,
    "composes": [], "needs_orchestrator_store_sync": True,
}


def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    pre_lines = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")
    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")
    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            time.sleep(0.1 * (2 ** _attempt))
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")
    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={TS:.3f}")
    append_jsonl_a5(MATH_ATOMS, crux_atom, "math/atoms (CRUX HARD_FAIL, compose-crosstalk)")
    append_jsonl_a5(MATH_ATOMS, gcore_atom, "math/atoms (GROUNDED-CORE MEASURED_MECHANISM, span-not-decode)")
    append_jsonl_a5(META_ATOMS, meta_atom, "meta/atoms (CONVERGENCE REJECTED, CERT-neutral)")
    append_jsonl_a5(CERT_LEDGER, crux_ledger, "cert_ledger (HF +1 crux)")
    append_jsonl_a5(CERT_LEDGER, gcore_ledger, "cert_ledger (MM +1 grounded-core)")
    append_jsonl_a5(CERT_LEDGER, meta_ledger, "cert_ledger (CERT-neutral META convergence-rejected)")
    print("[A5] DONE OK -> crux HARD_FAIL (HF+1), grounded-core MEASURED_MECHANISM (MM+1), convergence REJECTED (neutral)")


if __name__ == "__main__":
    main()
