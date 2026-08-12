"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY, XHIGH) of conceptnet_rerank_parity_multiseed_v1 -- TWO deliverables.

CELL: experiments/exp_conceptnet_rerank_parity_multiseed_v1.py (commit 1c7911d94)
METRICS: data/exp_conceptnet_rerank_parity_multiseed_v1/metrics.json (run_mode=full, HARD_PASS, 5 seeds 20260619-23, 1019.8s)
PREREG: preregs/2026-07-08_conceptnet_rerank_parity_multiseed_v1.md

INDEPENDENT OFF-DISK RECOMPUTE (this session, .venv python off per_seed[] -- matched cell EXACTLY):
  RB per-seed  [0.5236,0.5064,0.4335,0.4421,0.4335] mean 0.4678 std(ddof0) 0.0391
  RRF per-seed [0.5708,0.6009,0.5622,0.5665,0.5494] mean 0.5700
  HARD per-seed[0.5365,0.5579,0.5622,0.5408,0.5408] mean 0.5476
  BGE seed-invariant 0.48498 (std 0.0); closure 1.000 all seeds; floor 0.0515 all seeds
  A: RRF lift vs RB = +0.1021, 5/5 seeds positive (min lift +0.047), paired t(df=4)=6.83 (p~0.002); cv(RRF)=0.030
     RRF also beats BGE_alone +0.085 (0.570 vs 0.485). rerank_headroom mean 0.232 (fires>0.03); rerank_identity False.
  B: diff RB-BGE = -0.0172; pooled McNemar b=242 c=262 stat 0.716 p=0.397 (per-seed p 0.26-0.71 recomputed identical);
     determinism_ok True (self-test order-indep W byte-identical + W rebuilt twice bit-identical).

TIER DECISIONS (independent of cell verdict; cell agrees):
  (A) SEM_RERANK -> CHAIN_GRADE WIN. Post-hoc BGE rerank of the DECORRELATED RANDOM_BEAM shortlist lifts
      Hits@10 +0.102 over the substrate beam, 5/5 seeds, paired-significant, tight cv 0.030, WITHOUT the
      SEM_BEAM collapse (0.502->0.227). Constructive confirmation of correlation-hurts-capacity DECOUPLE:
      store stays near-orthogonal, semantics enters ONLY at post-hoc rerank. REVIVES the SEM_BEAM HARD_FAIL
      negative into a net positive. cert_delta CG +1.
      HONEST FRAMING (locked): this is a HYBRID (substrate beam + BLACK-BOX BGE at rerank), NOT the
      substrate alone beating an LLM. The FUSION (RRF) beats BOTH components (RB 0.468, BGE 0.485, RRF 0.570).
      The +0.085 over BGE is real (structural beam-rank prior complements semantic rank) but single-dataset.
  (B) CG-PARITY firm-up -> MM_STANDARD (firms the June-19 MM_TENTATIVE parity atom; does NOT reach CG). The
      determinism confound (PYTHONHASHSEED) that made June-19 TENTATIVE is RESOLVED (order-independent W,
      verified), and it is now 5-seed with paired McNemar. BUT the pre-committed CG_PARITY band requires
      std(RB)<=0.03 and std(RB)=0.0391 FAILS it -> MM_PARITY stands. cert_delta 0 (MM->MM firm-up, no new CG).
      Point estimate diff = -0.017 (RB slightly BELOW BGE) but McNemar p=0.397 -> genuine within-noise
      NON-difference, NOT a loss (symmetric anti-negativity: do NOT manufacture SUBSTRATE_LOSES; p>>0.05).
      EXPLICIT REJECTION of promotion: the June-19 atom's revival criterion #3 ("|margin|<per-seed sigma ->
      CG") is LITERALLY met (0.017<0.039) but is a FLAWED criterion -- a NOISIER substrate trivially
      satisfies |margin|<sigma, so it perversely rewards variance. The new cell's stricter std(RB)<=0.03
      gate is the correct standard for a chain-grade tie and it is NOT met. Honest: parity holds in the
      NON-DISTINGUISHABILITY sense but the substrate's own code-draw variance (RB swings 0.433-0.524, cv
      0.083) is too high to call it a firm chain-grade tie; and the 5-seed mean actually sits below BGE.

HARNESS VALIDITY (all pass): closure oracle 1.000 all seeds; arms_differ(RB vs BGE) True (distinct rank
  digests); cardinality 5/5 (cardinality_ok True); per-item logging present (PerItemLogger); self-test OK
  (determinism order-indep + subgraph==j19 + rerank promote/outside/identity + McNemar). NOT saturation-
  vacuous (closure ceiling 1.0, RB 0.47, headroom 0.23; rerank_identity False). NOT joint-gate (single
  Hits@10 metric, paired per-item same candidate sets). NOT flattering-reconciliation (RB and rerank share
  the SAME beam/candidate sets by design -- correct paired control, not a same-config confound).

CROSS-ARC OVERLAP CHECK (substrate_query, mandatory): top hit cosine=0.288 ('correlated', wordnet) < 0.30;
  next 'Substrate multi-hop retrieval' 0.280 -- NO prior arc cell at cosine>0.30 for POST-HOC BGE-rerank
  over a decorrelated substrate beam -> GENUINELY NOVEL (constructive side of correlation-hurts-capacity).
  v1 SEM_BEAM injected semantics INTO the store (HF 0.227); this keeps the store decorrelated and reranks
  post-hoc -> different mechanism, not a rediscovery.

PARENTS:
  HF_PARENT (SEM_BEAM structural negative, T3): the negative this deliverable-A revives.
  PARITY_PARENT (June-19 RANDOM_BEAM-vs-BGE MM_TENTATIVE): deliverable B AMENDS/firms this (MM_TENTATIVE ->
    MM_STANDARD; determinism + multi-seed resolved; still capped at MM by std gate). NOT superseded.
  correlation-hurts-capacity reference: the principle both deliverables operationalize.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_08_conceptnet_rerank_parity_multiseed_A_CG_B_MM_STANDARD"
CELL_COMMIT = "1c7911d94"
TS = 1783485282.331876
TS_ISO = "2026-07-08T04:34:42Z"
SESSION = "2026-07-08_conceptnet_rerank_parity_multiseed_landed_vet"

HF_PARENT = ("math::T3/EXP_conceptnet_semantic_seeded_beam_composition_v1_HARD_FAIL_HONEST_NEGATIVE_"
             "STRUCTURAL_semantic_seeding_ACTIVELY_HARMFUL_correlation_hurts_capacity_CONFIRM_SEM_BEAM_"
             "hits10_0p227_le_max_closure_1p000_bge_0p494_nontriv_lift_neg0p738_RANDOM_beats_SEM_BOTH_"
             "regimes_K1_0p481_gt_0p227_BEAM_0p502_gt_0p227_edge_cos_sem_0p204_rand_0p002_semantic_"
             "correlated_seeds_collide_associative_store_drop_capacity_vs_near_orthogonal_random_seeds_"
             "controls_ALL_fire_semantic_fires_gate_d_repro_scramble_collapses_SCRAM_0p073_arms_differ_"
             "distinct_digests_positive_control_closure_oracle_1p000_harness_works_NOT_test_design_"
             "failure_HF_STRUCTURAL_composes_correlated_key_capacity_rho_sweep_v1_3seed_CG_Lowe_1998_2026_07_07")
PARITY_PARENT = ("math::T3/EXP_conceptnet_semantic_seeded_beam_composition_v1_SECONDARY_MEASURED_MECHANISM_"
                 "TENTATIVE_GLASS_BOX_substrate_native_RANDOM_BEAM_at_PARITY_with_BGE_encoder_on_multi_hop_"
                 "composition_hits10_0p502_vs_0p494_margin_plus0p0086_4_of_466_items_WITHIN_NOISE_unpaired_"
                 "z_0p26_McNemar_worstcase_chi2_2p25_p_0p13_run_to_run_swing_0p0196_2pp_gt_margin_PARITY_"
                 "NOT_BEAT_NOT_beats_an_LLM_BGE_is_encoder_zero_external_embedding_transparent_mechanism_"
                 "AUROC_0p852_more_robust_discriminator_but_bge_AUROC_NOT_on_disk_ge_bge_unverifiable_"
                 "FIX28_MM_TENTATIVE_single_nondeterministic_run_needs_multiseed_fixedseed_rerun_2026_07_07")
CORR_HURTS_REF = "reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08"

# ============================== DELIVERABLE A -- CHAIN_GRADE WIN ==============================
atom_A = {
    "id": (
        "math::CHAIN_GRADE_conceptnet_rerank_parity_multiseed_v1_DELIVERABLE_A_SEM_RERANK_WIN_REVIVES_"
        "SEM_BEAM_HARD_FAIL_correlation_hurts_capacity_DECOUPLE_CONSTRUCTIVE_post_hoc_BGE_rerank_of_"
        "DECORRELATED_RANDOM_BEAM_shortlist_lifts_hits10_plus0p102_over_substrate_beam_RRF_0p570_vs_RB_"
        "0p468_5of5_seeds_positive_min_lift_plus0p047_paired_t_df4_6p83_p_0p002_cv_0p030_NO_COLLAPSE_"
        "unlike_SEM_BEAM_0p502_to_0p227_store_stays_near_orthogonal_semantics_ONLY_at_post_hoc_rerank_"
        "top25_shortlist_HARD_and_RRF_both_win_HARD_0p548_rerank_headroom_0p232_fires_identity_False_ALSO_"
        "beats_BGE_alone_plus0p085_fusion_gt_both_components_HYBRID_not_substrate_alone_beats_LLM_BGE_is_"
        "black_box_at_rerank_single_dataset_conceptnet_N8192_determinism_pinned_closure_oracle_1p000_"
        "arms_differ_True_5of5_cardinality_ok_commit_1c7911d94_2026-07-08"
    ),
    "name": (
        "DELIVERABLE A CHAIN_GRADE WIN: post-hoc BGE rerank of a DECORRELATED substrate beam lifts "
        "ConceptNet multi-hop Hits@10 +0.102 over RANDOM_BEAM (RRF 0.570 vs 0.468, 5/5 seeds, paired "
        "t=6.83) WITHOUT the SEM_BEAM collapse -- constructive confirmation of correlation-hurts-capacity "
        "DECOUPLE; revives the SEM_BEAM HARD_FAIL. HYBRID (uses black-box BGE at rerank), not substrate-alone."
    ),
    "corpus": "math",
    "tier": "CHAIN_GRADE",
    "kind": "experiment_landed_vet",
    "cert_status": "chain_grade_win_revives_sem_beam_hard_fail_correlation_hurts_capacity_decouple_constructive",
    "cert_class": (
        "post_hoc_semantic_rerank_of_a_decorrelated_substrate_native_beam_lifts_multi_hop_retrieval_without_"
        "the_collapse_that_kills_semantic_seeded_store_codes_HYBRID_fusion_beats_both_substrate_beam_and_"
        "BGE_alone_single_dataset_conceptnet"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, XHIGH) of deliverable A of exp_conceptnet_rerank_parity_multiseed_v1 "
        "(commit 1c7911d94; 5-seed FULL 20260619-23, N_DIM=8192, BEAM_K=6, KHOP=4, RERANK_K=25, RRF_K0=60; "
        "elapsed 1019.8s). CLAIM VERIFIED off-disk (independent .venv recompute matched the cell exactly): "
        "reranking the top-25 RANDOM_BEAM shortlist by BGE cosine (SEM_RERANK) lifts Hits@10 over the plain "
        "substrate beam. SEM_RERANK_RRF mean 0.5700 vs RANDOM_BEAM mean 0.4678 -> lift +0.1021; positive in "
        "5/5 seeds (per-seed RRF lift 0.047/0.094/0.129/0.125/0.116, min +0.047 > +0.03 WIN threshold); "
        "paired t(df=4)=6.83 (p~0.002); cross-seed cv(RRF)=0.030. SEM_RERANK_HARD (BGE fully replaces "
        "substrate order in the shortlist) also wins (mean 0.5476, +0.080). CRITICALLY: NO COLLAPSE -- this "
        "is the SEM_BEAM can-fail alternative (v1 semantic-seeded store collapsed 0.502->0.227). Here the "
        "store codes stay DECORRELATED (near-orthogonal random) and semantics enters ONLY as a post-hoc "
        "reorder of the substrate shortlist -- the store/composition codes are never semantic-seeded. This "
        "is the CONSTRUCTIVE confirmation of correlation-hurts-capacity DECOUPLE (" + CORR_HURTS_REF + "): "
        "correlate the store -> collapse (SEM_BEAM HF); decouple (store random, semantics at rerank) -> "
        "net lift. rerank_headroom mean 0.232 (fires, >0.03: 23% of with-path true tails sit in top-25 but "
        "not top-10 -- genuine room the rerank exploits); rerank_identity=False (rerank actually reorders, "
        "not a vacuous identity). HONEST FRAMING (locked, anti-inflation): SEM_RERANK is a HYBRID (substrate "
        "beam + BLACK-BOX BGE cosine at rerank), NOT the glass-box substrate ALONE beating an LLM. The RRF "
        "FUSION beats BOTH components (RANDOM_BEAM 0.468, BGE_ALONE 0.485, RRF 0.570): +0.102 over the beam "
        "AND +0.085 over BGE alone -- the substrate beam supplies a structural-reachability candidate prior "
        "that complements BGE's semantic rank, and RRF fuses the two. The +0.085-over-BGE is real and "
        "consistent across all 5 seeds but is SINGLE-DATASET (ConceptNet), single N_DIM (8192), single "
        "split; generalization to other corpora/encoders is an expansion criterion, not shown. HARNESS: "
        "closure oracle 1.000 all seeds (valid); arms_differ(RB vs BGE)=True (distinct rank digests); "
        "cardinality 5/5; determinism_ok=True; self-test OK. NOT saturation-vacuous (closure 1.0 ceiling, "
        "RB 0.47, ample headroom); NOT joint-gate (single Hits@10, paired per-item on identical candidate "
        "sets); NOT flattering-reconciliation (RB and SEM_RERANK share the SAME beam/candidate sets -- the "
        "correct paired control). CROSS-ARC OVERLAP: top hit cosine 0.288 < 0.30 -> genuinely novel."
    ),
    "provenance": {
        "cell": "experiments/exp_conceptnet_rerank_parity_multiseed_v1.py",
        "commit": CELL_COMMIT,
        "prereg": "preregs/2026-07-08_conceptnet_rerank_parity_multiseed_v1.md",
        "metrics_path": "data/exp_conceptnet_rerank_parity_multiseed_v1/metrics.json",
        "seeds": [20260619, 20260620, 20260621, 20260622, 20260623],
        "run_mode": "full",
        "elapsed_s": 1019.8,
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute off per_seed[]: RRF mean 0.5700, RB mean 0.4678, lift +0.1021, "
            "5/5 seeds positive (min +0.047), paired t(df=4)=6.83, cv(RRF)=0.030; RRF-vs-BGE +0.085; "
            "headroom mean 0.232, identity False. Mechanism inspected: rerank_true_rank (cell line 226-257) "
            "reorders ONLY the top-RERANK_K substrate shortlist by BGE cosine (HARD) or RRF of substrate+BGE "
            "rank (RRF); store codes (E_rand random bipolar) never touched. self-test OK (order-indep W, "
            "rerank promote/outside/identity, McNemar)."
        ),
    },
    "verified_numbers": {
        "RANDOM_BEAM_per_seed": [0.5236051502145923, 0.5064377682403434, 0.4334763948497854,
                                 0.44206008583690987, 0.4334763948497854],
        "RANDOM_BEAM_mean": 0.4678111587982833,
        "SEM_RERANK_RRF_per_seed": [0.5708154506437768, 0.6008583690987125, 0.5622317596566524,
                                    0.5665236051502146, 0.5493562231759657],
        "SEM_RERANK_RRF_mean": 0.5699570815450643,
        "SEM_RERANK_HARD_mean": 0.5476394849785408,
        "BGE_ALONE_mean": 0.48497854077253216,
        "RRF_lift_vs_RANDOM_BEAM": 0.10214592274678103,
        "RRF_lift_per_seed": [0.0472, 0.0944, 0.1288, 0.1245, 0.1159],
        "RRF_pos_seeds": 5,
        "RRF_lift_min": 0.0472,
        "RRF_paired_t_df4": 6.83,
        "RRF_paired_t_p_approx": 0.0024,
        "RRF_cross_seed_cv": 0.0299,
        "RRF_lift_vs_BGE_alone": 0.0850,
        "rerank_headroom_mean": 0.23175965665236048,
        "rerank_fires": True,
        "rerank_identity": False,
        "closure_hits10_mean": 1.0,
        "random_floor_hits10": 0.05150214592274678,
        "arms_differ_rb_vs_bge": True,
    },
    "can_fail_discriminator_verdict": (
        "FIRES against a REAL can-fail alternative: the COLLAPSE band (best-rerank <= RB-0.05) is the "
        "SEM_BEAM prior (semantic-seeded store collapsed 0.502->0.227). Here best-rerank = RB+0.102 (opposite "
        "of collapse); rerank_headroom 0.232>0.03 confirms the rerank has genuine room (not vacuous "
        "identity); rerank_identity=False confirms it actually reorders. Discriminator could have fired "
        "COLLAPSE and did not."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "Cell 'A WIN' and director 'genuine WIN' CONFIRMED off-disk (lift +0.102, 5/5 seeds, paired "
        "t=6.83) -- upheld, no inflation found.",
        "SCOPE LOCK: this is a HYBRID (substrate beam + black-box BGE at rerank), NOT 'substrate beats "
        "the encoder'. The RRF fusion beats BOTH components; the +0.085 over BGE is the genuinely new part "
        "(structural beam prior complements semantic rank) but is single-dataset/single-N_DIM. Do NOT let "
        "this atom inflate to a glass-box-alone-beats-LLM claim.",
        "The primary pre-registered question (beat RANDOM_BEAM without collapse) is answered YES; the "
        "beat-BGE result is a bonus, correctly framed as fusion>components not substrate>LLM.",
    ],
    "revival_to_broader_scope_criterion": (
        "This CG is scoped to ConceptNet multi-hop at N_DIM=8192. Expansion criterion: replicate the "
        "post-hoc-rerank lift on >=1 other corpus/relation-set AND/OR with a different (non-BGE) semantic "
        "reranker to show the DECOUPLE mechanism generalizes beyond ConceptNet+BGE. Ablation criterion: "
        "sweep RERANK_K to confirm the win is not knife-edge on shortlist size (HARD and RRF both winning "
        "at K=25 is supporting but not a sweep)."
    ),
    "composes": [HF_PARENT, PARITY_PARENT, CORR_HURTS_REF],
    "revives_negative": HF_PARENT,
    "cross_arc_overlap_check": (
        "top hit cosine=0.288 ('correlated', wordnet) < 0.30; 'Substrate multi-hop retrieval' 0.280 -- NO "
        "prior arc cell at cosine>0.30 for post-hoc BGE-rerank over a decorrelated substrate beam. Genuinely "
        "novel: the CONSTRUCTIVE side of correlation-hurts-capacity (SEM_BEAM tested the destructive side)."
    ),
    "anchor": "conceptnet_rerank_parity_multiseed_v1",
    "cell_commit": CELL_COMMIT,
    "seeds": [20260619, 20260620, 20260621, 20260622, 20260623],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "post-hoc BGE rerank of decorrelated substrate beam lifts ConceptNet Hits@10 +0.102 over beam 5/5 seeds no collapse",
        "SEM_RERANK revives SEM_BEAM HARD_FAIL: decouple store (random) from semantics (rerank) -> net positive",
        "RRF fusion 0.570 beats both RANDOM_BEAM 0.468 and BGE_alone 0.485; HYBRID not substrate-alone-beats-LLM",
        "constructive confirmation of correlation-hurts-capacity decouple principle chain-grade single-dataset",
    ],
}
atom_A["added_atom_id"] = atom_A["id"]

ledger_A = {
    "ts": TS, "ts_iso": TS_ISO, "atom_id": atom_A["id"], "corpus": "math",
    "tier": "CHAIN_GRADE",
    "disposition": "chain_grade_win_deliverable_A_sem_rerank_revives_sem_beam_correlation_hurts_decouple",
    "cert_status": "chain_grade_hybrid_rerank_lift_no_collapse_constructive_decouple_confirmation",
    "cert_class": (
        "post_hoc_semantic_rerank_of_decorrelated_substrate_beam_lifts_multi_hop_retrieval_without_collapse_"
        "fusion_beats_both_components_hybrid_single_dataset"
    ),
    "cert_increment_delta": 1,
    "cert_delta": {"CG": 1, "MM": 0, "HF": 0},
    "cert_delta_note": (
        "CG +1: NEW chain-grade positive. SEM_RERANK_RRF lifts ConceptNet multi-hop Hits@10 +0.102 over "
        "RANDOM_BEAM (5/5 seeds, paired t=6.83, cv 0.030) and +0.085 over BGE_alone WITHOUT the SEM_BEAM "
        "collapse -- constructive confirmation of correlation-hurts-capacity DECOUPLE. HYBRID (substrate "
        "beam + black-box BGE at rerank), scoped single-dataset (ConceptNet, N=8192). Revives HF_PARENT "
        "(SEM_BEAM) into a net positive. Needs orchestrator Store-sync (atoms.jsonl append)."
    ),
    "verified_off_data": True,
    "anchor": "conceptnet_rerank_parity_multiseed_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [HF_PARENT, PARITY_PARENT, CORR_HURTS_REF],
    "revives_negative": HF_PARENT,
}

# ============================== DELIVERABLE B -- MM_STANDARD firm-up ==============================
atom_B = {
    "id": (
        "math::AMEND_conceptnet_rerank_parity_multiseed_v1_DELIVERABLE_B_FIRMS_June19_RANDOM_BEAM_vs_BGE_"
        "parity_from_MM_TENTATIVE_to_MM_STANDARD_determinism_confound_RESOLVED_PYTHONHASHSEED_order_indep_W_"
        "verified_5seed_paired_McNemar_but_STILL_NOT_CG_std_RB_0p0391_gt_0p03_pre_committed_gate_FAILS_"
        "MM_PARITY_diff_RB_minus_BGE_neg0p017_RB_0p468_vs_BGE_0p485_pooled_McNemar_b242_c262_p_0p397_WITHIN_"
        "NOISE_non_difference_NOT_a_loss_p_gt_0p05_symmetric_RB_swings_0p433_to_0p524_cv_0p083_code_draw_"
        "sensitive_5seed_mean_sits_BELOW_BGE_REJECT_June19_criterion3_margin_lt_sigma_FLAWED_noisier_"
        "substrate_trivially_passes_amends_PARITY_PARENT_not_superseded_cert_delta_0_commit_1c7911d94_2026-07-08"
    ),
    "name": (
        "DELIVERABLE B: firms the June-19 RANDOM_BEAM-vs-BGE parity from MM_TENTATIVE to MM_STANDARD "
        "(determinism confound resolved, 5-seed paired McNemar) but does NOT reach CG-parity -- std(RB)=0.039 "
        "> 0.03 pre-committed gate fails; within-noise NON-difference (p=0.397), not a loss. cert_delta 0."
    ),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": "mm_standard_parity_firm_up_determinism_resolved_multiseed_but_std_gate_fails_no_CG_no_new_cert",
    "cert_class": (
        "glass_box_substrate_native_RANDOM_BEAM_statistically_INDISTINGUISHABLE_from_BGE_encoder_on_conceptnet_"
        "multi_hop_hits10_within_run_to_run_and_sampling_noise_but_code_draw_variance_too_high_for_chain_grade_"
        "tie_and_5seed_mean_sits_slightly_below_BGE_PARITY_NOT_BEAT"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, XHIGH) of deliverable B of exp_conceptnet_rerank_parity_multiseed_v1 "
        "(commit 1c7911d94; 5-seed FULL 20260619-23). This AMENDS/firms the June-19 RANDOM_BEAM-vs-BGE "
        "parity atom (PARITY_PARENT, MM_TENTATIVE). OFF-DISK INDEPENDENT RECOMPUTE (matched cell exactly): "
        "RB mean 0.4678 std(ddof0) 0.0391; BGE_ALONE 0.48498 (seed-invariant); diff RB-BGE = -0.0172; "
        "pooled McNemar b=242 c=262 stat 0.716 p=0.397 (per-seed p 0.26-0.71, all recomputed identical). "
        "TWO of the June-19 revival criteria are now RESOLVED: (1) determinism_ok=True -- the PYTHONHASHSEED "
        "confound that made June-19 TENTATIVE is fixed by canonical sorted() ordering of every set feeding "
        "the order-dependent cf-RPE delta rule; verified BOTH in --self-test (build W from a scrambled edge "
        "list -> byte-identical digest to sorted order) AND in-eval (rebuild seed[0] W twice -> bit-identical "
        "digest). (2) 5-seed with paired McNemar per seed. BUT the pre-committed CG_PARITY band requires "
        "std(RB)<=0.03 AND |diff|<=0.02 AND pooled_p>0.05 AND determinism_ok; std(RB)=0.0391 > 0.03 FAILS -> "
        "MM_PARITY stands. TIER = MM_STANDARD (firm-up from MM_TENTATIVE; NOT CG; cert_delta 0). "
        "SYMMETRIC ANTI-NEGATIVITY: the point estimate diff is NEGATIVE (-0.017, RB slightly below BGE) and "
        "3/5 seeds have RB well below BGE (0.433,0.442,0.433 vs 0.485), but pooled McNemar p=0.397 >> 0.05 -> "
        "this is a genuine WITHIN-NOISE NON-DIFFERENCE, NOT a SUBSTRATE_LOSES (which requires diff<-0.05 AND "
        "p<=0.05). Do NOT manufacture a loss. EXPLICIT PROMOTION REJECTION: PARITY_PARENT's revival criterion "
        "#3 stated '|margin| < per-seed sigma across seeds -> PARITY is chain-grade'; that is LITERALLY met "
        "here (|0.017| < 0.039) BUT the criterion is FLAWED -- a noisier substrate (larger sigma) trivially "
        "satisfies |margin|<sigma, so it perversely rewards variance rather than a tight tie. The new cell's "
        "stricter std(RB)<=0.03 gate is the correct standard for a CHAIN-GRADE tie and it is NOT met (RB "
        "swings 0.433-0.524, cv 0.083 -- code-draw sensitive). Honest read: parity holds in the "
        "NON-DISTINGUISHABILITY (McNemar) sense, but the substrate beam's own code-draw variance is too high "
        "to call it a firm chain-grade tie, and the determinism-pinned canonical-order 5-seed mean (0.468) "
        "actually sits slightly below both BGE (0.485) and the June-19 point value (0.502). PARITY NOT BEAT; "
        "and NOT firm enough for CG. To reach CG-parity: reduce code-draw variance (e.g., ensemble/average "
        "over draws as the substrate estimate, or larger N_DIM) so std(RB)<=0.03 while |diff| stays <=0.02 "
        "and p>0.05. HARNESS: closure 1.000, arms_differ(RB vs BGE)=True, cardinality 5/5, determinism_ok."
    ),
    "provenance": {
        "cell": "experiments/exp_conceptnet_rerank_parity_multiseed_v1.py",
        "commit": CELL_COMMIT,
        "prereg": "preregs/2026-07-08_conceptnet_rerank_parity_multiseed_v1.md",
        "metrics_path": "data/exp_conceptnet_rerank_parity_multiseed_v1/metrics.json",
        "parent_parity_atom": PARITY_PARENT,
        "seeds": [20260619, 20260620, 20260621, 20260622, 20260623],
        "run_mode": "full",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute off per_seed[]: RB mean 0.4678 std 0.0391; BGE 0.48498; diff "
            "-0.0172; pooled McNemar b=242 c=262 p=0.397 (per-seed p identical to stored). determinism_ok "
            "verified via self-test (order-indep W byte-identical) + in-eval W-twice bit-identical. std gate "
            "0.0391>0.03 -> MM_PARITY."
        ),
    },
    "verified_numbers": {
        "RANDOM_BEAM_mean": 0.4678111587982833,
        "RANDOM_BEAM_std_ddof0": 0.03905343576335564,
        "RANDOM_BEAM_per_seed": [0.5236051502145923, 0.5064377682403434, 0.4334763948497854,
                                 0.44206008583690987, 0.4334763948497854],
        "RANDOM_BEAM_cv": 0.0835,
        "BGE_ALONE_mean": 0.48497854077253216,
        "diff_rb_minus_bge": -0.017167381974248885,
        "mcnemar_pooled_b": 242, "mcnemar_pooled_c": 262,
        "mcnemar_pooled_stat": 0.7162698412698413, "mcnemar_pooled_p": 0.3973702012891665,
        "mcnemar_per_seed_p": [0.4017, 0.7067, 0.2566, 0.3633, 0.2898],
        "determinism_ok": True,
        "cg_gate_std_threshold": 0.03,
        "cg_gate_std_actual": 0.0391,
        "cg_gate_result": "FAILS_std",
        "june19_rb_bar": 0.502, "june19_bge_bar": 0.494,
    },
    "framing_corrections_vs_cell_author_and_director": [
        "Cell 'B MM_PARITY' CONFIRMED off-disk -- correct tier, no inflation and no manufactured loss.",
        "Director framing 'ties BGE, move parity MM->CHAIN_GRADE': NOT EARNED. The tie holds only in the "
        "non-distinguishability (McNemar p=0.397) sense; std(RB)=0.039 fails the pre-committed CG std<=0.03 "
        "gate, and the determinism-pinned 5-seed mean (0.468) sits BELOW BGE (0.485) and below the June-19 "
        "0.502. It is a firm MM_STANDARD, not CG.",
        "REJECT the June-19 atom's own criterion #3 (|margin|<sigma -> CG): flawed because larger substrate "
        "variance trivially satisfies it. std(RB)<=0.03 is the correct chain-grade-tie standard.",
        "Symmetric guard: do NOT read the negative point-estimate diff as a substrate LOSS; p>>0.05.",
    ],
    "revival_to_CG_criterion": (
        "Promote MM_STANDARD -> CG_PARITY by reducing RANDOM_BEAM code-draw variance so std(RB)<=0.03 while "
        "|mean(RB)-BGE|<=0.02 and pooled McNemar p>0.05 (determinism already resolved). Options: report an "
        "ensemble/mean-over-code-draws as the substrate estimate (changes the claim to an ensemble parity), "
        "or increase N_DIM to shrink per-draw variance, or add seeds to characterize whether std tightens. "
        "Do NOT promote on the |margin|<sigma criterion (flawed)."
    ),
    "composes": [PARITY_PARENT, CORR_HURTS_REF],
    "amends_parent": PARITY_PARENT,
    "cross_arc_overlap_check": (
        "Same cell as deliverable-A CG atom; targeted firm-up of EXISTING June-19 parity (PARITY_PARENT), "
        "not a rediscovery. Overlap top hit 0.288<0.30."
    ),
    "anchor": "conceptnet_rerank_parity_multiseed_v1",
    "cell_commit": CELL_COMMIT,
    "seeds": [20260619, 20260620, 20260621, 20260622, 20260623],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "RANDOM_BEAM vs BGE parity firmed MM_TENTATIVE->MM_STANDARD determinism resolved 5-seed but not CG std 0.039>0.03",
        "within-noise non-difference McNemar p=0.397 diff -0.017 not a loss symmetric; RB mean sits below BGE",
        "reject June-19 |margin|<sigma criterion flawed noisier substrate trivially passes; std<=0.03 is correct CG-tie gate",
        "parity not beat not chain-grade code-draw variance too high cv 0.083 needs ensemble or larger N_DIM",
    ],
}
atom_B["added_atom_id"] = atom_B["id"]

ledger_B = {
    "ts": TS, "ts_iso": TS_ISO, "atom_id": atom_B["id"], "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "disposition": "mm_standard_parity_firm_up_determinism_resolved_multiseed_amends_June19_no_CG",
    "cert_status": "mm_standard_within_noise_parity_std_gate_fails_no_chain_grade_no_new_cert",
    "cert_class": (
        "glass_box_RANDOM_BEAM_indistinguishable_from_BGE_within_noise_but_code_draw_variance_too_high_for_"
        "chain_grade_tie_parity_not_beat"
    ),
    "cert_increment_delta": 0,
    "cert_delta": {"CG": 0, "MM": 0, "HF": 0},
    "cert_delta_note": (
        "cert_delta 0: firms the June-19 parity from MM_TENTATIVE -> MM_STANDARD (determinism confound "
        "resolved: order-independent W verified; 5-seed paired McNemar). Does NOT reach CG_PARITY: "
        "std(RB)=0.0391 > 0.03 pre-committed gate FAILS; determinism-pinned 5-seed mean 0.468 sits below "
        "BGE 0.485 (diff -0.017, McNemar p=0.397 -> within-noise non-difference, NOT a loss). MM->MM = no "
        "new CG. Amends PARITY_PARENT (not superseded). Explicitly rejects the June-19 |margin|<sigma "
        "criterion as flawed. Needs orchestrator Store-sync."
    ),
    "verified_off_data": True,
    "anchor": "conceptnet_rerank_parity_multiseed_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [PARITY_PARENT, CORR_HURTS_REF],
    "amends_parent": PARITY_PARENT,
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
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_A, "math/atoms (A: SEM_RERANK CHAIN_GRADE WIN)")
    append_jsonl_a5(CERT_LEDGER, ledger_A, "cert_ledger (A: CG +1)")
    append_jsonl_a5(MATH_ATOMS, atom_B, "math/atoms (B: parity MM_STANDARD firm-up)")
    append_jsonl_a5(CERT_LEDGER, ledger_B, "cert_ledger (B: MM firm-up, cert_delta 0)")
    print(f"[A5] DONE OK")
    print(f"[A5] A -> CHAIN_GRADE (CG +1) hybrid rerank revives SEM_BEAM | B -> MM_STANDARD firm-up (cert_delta 0)")


if __name__ == "__main__":
    main()
