"""
A5-gated atomization -- Skunkworks MAKE-OR-BREAK landed-VET of Encoder Migration
Step 1b v3c (PAIRED FULL-178k global(landmark)-RKD-only vs in_batch-RKD-only,
nce_weight=0 for both arms, best-by-full-held-eval checkpoint selection, 2 seeds).
2026-07-04.

CELL: experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py
      (commit 94062aeccdc0381067a8f889f2050d1edb5373b4)
DATA: data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_7/metrics.json
      data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_13/metrics.json
      SSH byte-verified 2026-07-04 vs remote C:/dev/hd-instrument (host resolved via
      `ssh marsh@home` after D:/AI/hd-instrument path did not exist remotely --
      Get-FileHash SHA256 identical both files, both seeds).
PREREG: preregs/2026-07-04_exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1.md
Both seeds landed verdict=HARD_FAIL (FALSE_WIN_ALGEBRA_GLOBAL: keyed J5 0.133/0.317 < 0.90).

===================== INDEPENDENT RECOMPUTE (off metrics.json per_unit/recovery/train_diag, NOT verdict_msg alone) =====================
cardinality_ok: 10/10 both seeds, unit_failures=[] both. arms_differ_verified via distinct sha256
  (6 arm-code digests, all distinct, both seeds). delta_dense_best recomputed
  (global_dense_best - inbatch_dense_best) matches file's recovery.delta_dense_best exactly, both seeds.
Positive control FIRST (auditor discipline): keyed::RANDOM_BLOCK::J5 acc_at1=1.0 both seeds (>=0.98 gate,
  PASS) -- SBC-lossless prior holds before trusting anything else. Negative control
  shuffled_key::GLOBAL_BLOCK::J5 acc_at1=0.0/hit_any=0.0 both seeds -- no key leak.
Eval fairness: n_held=17790/n_train=160109 (teacher_n_concepts=177899, HELD_FRAC=0.10), disjoint via one
  np.random.default_rng(seed).permutation split (train slice then held slice, no overlap by construction).
  _keyed_unit performs a REAL bind(key_j,code_j) sum-over-J=5 -> unbind(key_q) -> chunked argmax cleanup
  against the FULL held codebook (17790 codes) -- genuine SBC algebra roundtrip, not degenerate (confirmed
  by direct code read of v3._keyed_unit; shuffled-key negative control correctly returns ~0, RANDOM_BLOCK
  positive control correctly returns 1.0).

FINDING 1 -- LANDMARK (GLOBAL) OBJECTIVE CONFIRMED DROPPABLE (2 seeds, 2 independent corroborating metrics):
  GLOBAL_BLOCK keyed@J5 acc_at1 = 0.1333 (seed7) / 0.3167 (seed13), both << 0.90 gate -- genuinely broken
  algebra (not test artifact: identical _keyed_unit/_random_block_codes/_chunked_cleanup_argmax construction
  used for INBATCH_BLOCK, which passes 1.0/1.0 both seeds using the SAME codebook-cleanup mechanism).
  INDEPENDENT corroboration via a SEPARATE per_unit metric never used in the verdict gate:
  ret_agree10 (top-10 retrieval-neighbor overlap vs teacher) for GLOBAL_BLOCK = 0.0148 (seed7) / 0.0262
  (seed13) -- near-chance-collapsed, consistent with the algebra failure (two independent measurements of
  "is this code functionally useful for retrieval/composition" agree it is not), vs INBATCH_BLOCK
  ret_agree10 = 0.1837/0.2659 (weak but an order of magnitude higher).
  delta_dense_best (global_dense_best - inbatch_dense_best) = -0.0238 (seed7) / -0.0692 (seed13): GLOBAL
  underperforms INBATCH on raw DENSE spearman in BOTH seeds (negative delta both times), directly
  contradicting H1 (landmark-necessary) and confirming H2 (landmark adds nothing / actively worse here).
  DISPOSITION: MM_STANDARD, 2 FULL seeds, corroborated by 2 independent metrics (keyed-algebra AND
  retrieval-agreement, neither derived from the other) -- clean signal, not a single-metric coincidence.
  The cell's own HARD_FAIL verdict (FALSE_WIN_ALGEBRA_GLOBAL) is confirmed CORRECT and CONSISTENT with a
  second, independent line of evidence.

FINDING 2 -- "IN_BATCH HITS THE ENCODER GOALS" CLAIM REFUTED ON RIGOR (make-or-break check; the load-bearing
  audit result of this VET):
  (a) BEST-CHECKPOINT INFLATION, CONFIRMED. Both arms' "best" DENSE numbers sit atop trajectories with a
  measured NEGATIVE step-vs-dense_full trend, not a stable plateau:
    seed7:  GLOBAL  pearson(step,dense)=-0.877 spearman=-0.853 (STRONG decline)
            INBATCH pearson(step,dense)=-0.813 spearman=-0.825 (STRONG decline)
    seed13: GLOBAL  pearson(step,dense)=-0.077 spearman=-0.245 (weak/noisy, still negative-leaning)
            INBATCH pearson(step,dense)=-0.281 spearman=-0.490 (moderate decline)
  best-to-final decline (recomputed from recovery.{global,inbatch}_traj):
    GLOBAL:  seed7 0.8528->0.6514 (-0.2014, -23.6% rel); seed13 0.8262->0.6191 (-0.2071, -25.1% rel)
    INBATCH: seed7 0.8766->0.7587 (-0.1179, -13.4% rel); seed13 0.8954->0.7696 (-0.1259, -14.1% rel)
  best-checkpoint step_frac: GLOBAL always frac=0.083 (step150/1800, earliest eligible eval point, both
  seeds); INBATCH frac=0.25 (step450, seed7) / 0.083 (step150, seed13) -- i.e. best-of-13 selection is
  consistently picking an EARLY point on a trajectory that keeps declining afterward, in both arms, both
  seeds. The cell's own trajectory-shape gate (_peak_then_decline) computes the "peak" over the RAW
  dense_traj INCLUDING the untrained step-0 entry (confirmed by direct code read: `vals = [(r["step"],
  r[key]) for r in traj ...]` with no min_step_for_best filter applied inside _peak_then_decline) -- since
  step0's untrained-network score (~0.956, both arms, both seeds) is always the highest value in the
  trajectory in this regime, "global_peak_decline"/"inbatch_peak_decline" are TRUE by construction for
  every arm/seed here and the HARD_PASS branch of the cell's own verdict logic (which requires
  `not peak_decline`) is structurally unreachable given this arc's established step-0-artifact behavior --
  a design gotcha independent of, and in addition to, the FALSE_WIN_ALGEBRA failure that actually fired.
  (b) REPRODUCIBILITY GAP: v3b's OWN NCE_ZERO/GLOBAL run (same nominal config: objective=global, nce=0,
  batch=128, steps=1800, seed=7 -- MEASURED@data/exp_encoder_migration_step1b_v3b_nce_ablation_dense_
  recovery_diagnostic_v1/metrics.json:recovery.nce_zero_dense_final) reports FINAL-step (not best-selected)
  dense=0.7336. v3c's seed7 GLOBAL FINAL-step dense=0.6514 -- a 0.082 (11% relative) gap between two runs
  of the nominally IDENTICAL config/seed. This is independent evidence that single-run point estimates in
  this training regime (whether best-selected or final-step) are not tightly reproducible even holding
  seed/config fixed (plausible sources: GPU non-determinism in the absence of torch.backends.cudnn.
  deterministic, or RNG-consumption-order differences between v3b's multi-arm battery script and v3c's
  2-arm script -- not resolved here, flagged as an open question).
  (c) CONFOUNDED 0.368->0.89 COMPARISON. v2 FULL's in_batch DENSE_SIGN=0.3683 (MEASURED@data/exp_encoder_
  migration_step1b_v2_mlp_distill_concept_encoder_v1/metrics.json, steps=40000, batch=512, nce_weight=0.5,
  FINAL-step only, no best-of-N tracking existed in that cell) is NOT a clean single-variable comparison
  point against v3c's in_batch DENSE(best)=0.877/0.895 (steps=1800 [22x FEWER], batch=128 [4x smaller],
  nce_weight=0, best-of-13-checkpoint-selected). At least 4 variables changed simultaneously (nce_weight,
  steps, batch, checkpoint-selection policy). The clean, single-axis NCE ablation that DOES exist in this
  arc (v3b SECONDARY, GLOBAL objective only, batch/steps/selection-policy held fixed, MM_STANDARD single-
  seed per prior VET) showed a genuine isolated NCE effect (+0.465); that clean result has never been run
  for the IN_BATCH objective at matched step budgets, so "NCE removal explains in_batch's rise" is
  UNVERIFIED -- the observed strong within-run decline trend in v3c's own in_batch trajectory (measured
  above) is at least as consistent with "in_batch still degrades with more steps; v3c simply stopped at
  1800 (vs v2's 40000) and best-of-13-selected a pre-decline point" as with "NCE removal alone fixed it."
  (d) METRIC RECONCILIATION, GAP CONFIRMED. The stated encoder goal (project_encoder_goals memory doc,
  USER-CONFIRMED 2026-07-04) is raw COSINE similarity to the correct/gold answer (~0.54 baseline -> 0.85
  target), NOT Spearman rank-correlation over a large randomly-sampled pair set. The reported "0.877-0.895"
  numbers ARE spearman_all over n_pairs_sampled=399986/399963 mostly-DISSIMILAR random pairs (only
  hi80_n=217-242 of those, ~0.05-0.06%, have teacher/gold cosine>=0.80 -- i.e. are "genuinely similar,
  goal-relevant" pairs). Rank-agreement over a sample dominated by trivially-far-apart pairs is a
  substantially easier target than the stated goal. The two per_unit metrics closer to the actual goal:
    hi80_cos (raw cosine among gold-similar pairs) shows real miscalibration: hi80_calib_err ranges
    0.017-0.142 across the 4 arm-seed combos (student cosine over/under-shoots the teacher's own value by
    up to 14 points on the very subset the goal cares about, small n=217-242).
    ret_agree10 (top-10 retrieval-neighbor overlap, arguably the single closest proxy to "does the
    substrate retrieve the right memory") = INBATCH_DENSE 0.1455(seed7)/0.6742(seed13) -- a 4.6x
    seed-to-seed swing; INBATCH_BLOCK 0.1837(seed7)/0.2659(seed13); GLOBAL_BLOCK collapses to
    0.0148/0.0262 (near-chance, corroborating Finding 1). By the metric closest to the stated goal, NEITHER
    arm demonstrates a stable, high-confidence "hits 0.85" result; INBATCH is weak-to-moderate and highly
    seed-unstable, not a converged ~0.85-equivalent capability.
  NET: the make-or-break "capability breakthrough" framing is REFUTED. What DOES survive, corroborated and
  genuine: (i) INBATCH_BLOCK's keyed-algebra roundtrip is real and passes cleanly both seeds (1.000/1.000)
  -- a genuine positive on encoder goal #4 (algebra must survive) for the in_batch/nce-off configuration
  specifically; (ii) the landmark/global objective is genuinely worse, not better, on this config (Finding
  1). What does NOT survive: any claim that in_batch-RKD-only-nce-off has been shown to STABLY reach
  ~0.85-equivalent semantic quality by the metric the USER's goal actually specifies.

CROSS-ARC OVERLAP CHECK (USER-locked 2026-07-01): bash tools/substrate_query.sh "best checkpoint selection
  cherry pick declining trajectory noisy training encoder distillation landmark objective in-batch RKD
  reproducibility" -> top hit cosine=0.3135, notes/research_drill_LoRA_retrieval_degradation_3x_deep_
  2026-06-06.md ("training-objective mismatch: SFT loss vs retrieval eval metric are different objectives
  -- pre-register loss/eval compatibility"). Read directly: this is a DIFFERENT lineage (LoRA/CELL-5
  SFT-vs-retrieval-metric mismatch, June 6) addressing TRAINING-LOSS-vs-EVAL-METRIC gradient compatibility,
  not the same mechanism as this VET's findings (checkpoint-selection cherry-pick from a volatile/declining
  trajectory, PLUS choice-of-eval-proxy-metric within evaluation, i.e. spearman-over-random-pairs vs
  cosine-on-gold-similar-pairs). ADJACENT IN SPIRIT (both are "the number you're looking at is not the
  number that matters") but a DISTINCT mechanism and a genuinely new case study for this encoder-distillation
  lineage -- not a full rediscovery. Filed with this note per the discipline.
"""
import json
import os
import time
import tempfile

MATH_ATOMS = "d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl"
META_ATOMS = "d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = "d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl"

TS = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS))

ANCHOR7 = "encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_seed7"
ANCHOR13 = "encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_seed13"
METRICS7 = "data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_7/metrics.json"
METRICS13 = "data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_13/metrics.json"
CELL_SRC = "experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py"
CELL_COMMIT = "94062aeccdc0381067a8f889f2050d1edb5373b4"
PREREG = "preregs/2026-07-04_exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1.md"

math_atom_landmark_droppable = {
    "id": ("math::MM_STANDARD_v3c_LANDMARK_GLOBAL_OBJECTIVE_CONFIRMED_DROPPABLE_2seed_FULL178k_"
           "corroborated_by_keyed_algebra_AND_retrieval_agreement_GLOBAL_BLOCK_keyed_J5_0p133_0p317_"
           "both_lt_0p90_ret_agree10_0p0148_0p0262_near_chance_negative_delta_dense_best_neg0p024_"
           "neg0p069_both_seeds_H2_confirmed_H1_falsified_2026-07-04"),
    "name": ("MATH landmark/global-frame RKD objective CONFIRMED DROPPABLE vs plain in-batch RKD once "
             "NCE is off, at FULL-178k scale, 2 seeds, corroborated by TWO independent metrics (keyed "
             "SBC-algebra roundtrip AND top-10 retrieval-agreement, neither derived from the other)."),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_measured_mechanism",
    "description": (
        "MM_STANDARD (2 FULL seeds, corroborated): at the FULL-178k concept-encoder distillation scale "
        "(batch=128, steps=1800, nce_weight=0.0 for both arms, best-by-full-held-eval checkpoint "
        "selection), the GLOBAL (fixed-landmark-frame) RKD objective is confirmed WORSE than plain "
        "in-batch RKD, refuting H1 (landmark objective is load-bearing) and confirming H2 (landmark adds "
        "nothing / actively hurts here). RECOMPUTE (off metrics.json['per_unit'] and ['recovery'], both "
        "seeds, independent of verdict_msg): GLOBAL_BLOCK keyed::J5 acc_at1 = 0.13333334028720856 (seed7) "
        "/ 0.3166666626930237 (seed13), both far below the 0.90 FALSE_WIN_ALGEBRA gate, using the IDENTICAL "
        "_keyed_unit/_random_block_codes/_chunked_cleanup_argmax construction that gives INBATCH_BLOCK "
        "1.0/1.0 on the same held codebook (17790 codes) -- not a test-design artifact (positive control "
        "keyed::RANDOM_BLOCK::J5 acc_at1=1.0 both seeds; negative control shuffled_key::GLOBAL_BLOCK::J5 "
        "acc_at1=0.0 both seeds). INDEPENDENT corroboration via a metric never used in the verdict gate: "
        "ret_agree10 (top-10 retrieval-neighbor overlap vs teacher, per_unit field, unrelated construction "
        "to the keyed-algebra unit) for GLOBAL_BLOCK = 0.014828555368184016 (seed7) / 0.026194491287240888 "
        "(seed13) -- near-chance-collapsed, vs INBATCH_BLOCK ret_agree10=0.18367060146147768 (seed7) / "
        "0.2658909499718906 (seed13), an order of magnitude higher. delta_dense_best (recomputed as "
        "global_dense_best - inbatch_dense_best, matches file's recovery.delta_dense_best exactly both "
        "seeds) = -0.023793385016926072 (seed7) / -0.0692288528853594 (seed13): GLOBAL underperforms "
        "INBATCH on raw DENSE spearman in BOTH seeds. Cardinality 10/10 both seeds, unit_failures=[] both, "
        "arms_differ_verified via 6 distinct sha256 digests both seeds. The cell's own filed verdict "
        "(HARD_FAIL, FALSE_WIN_ALGEBRA_GLOBAL) is CONFIRMED correct and additionally corroborated by a "
        "second independent line of evidence (retrieval-agreement) that was not part of the gate logic. "
        "ACTIONABLE: drop the landmark/global-frame objective as the production distillation objective; "
        "the simpler in-batch RKD (once NCE is off) is the better-performing and only-algebra-passing arm "
        "of the two tested here. This does NOT by itself establish in-batch-RKD-only as production-ready -- "
        "see the companion bounded-characterization atom (best-checkpoint-inflation + metric-mismatch "
        "concerns filed separately) before promoting a production recommendation."
    ),
    "aliases": ["v3c_landmark_objective_droppable", "global_RKD_worse_than_inbatch_RKD_FULL178k",
                "encoder_distill_landmark_frame_confirmed_unnecessary"],
    "metadata": {
        "record_class": "experiment_measured_mechanism_2seed_corroborated",
        "term_class": "ENCODER_MIGRATION_STEP1B_LANDMARK_OBJECTIVE_DROPPABLE",
        "cert_status": "mm_standard_2seed_corroborated_measured_mechanism",
        "cert_class": "MM_STANDARD_landmark_objective_confirmed_droppable_2seed_dual_metric_corroboration",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_v3c_make_or_break_audit",
        "anchor_seed7": ANCHOR7, "anchor_seed13": ANCHOR13,
        "cell_source_path": CELL_SRC, "cell_commit": CELL_COMMIT, "prereg_path": PREREG,
        "raw_metrics_path_seed7": METRICS7, "raw_metrics_path_seed13": METRICS13,
        "ssh_byte_verify": "sha256 identical local vs remote (C:/dev/hd-instrument), both seed files, 2026-07-04",
        "run_mode": "full", "seeds": [7, 13], "device": "cuda",
        "verdict_on_disk_both_seeds": "HARD_FAIL (FALSE_WIN_ALGEBRA_GLOBAL)",
        "recompute_check": {
            "cardinality": "10/10 both seeds, unit_failures=[]",
            "positive_control": {"unit": "keyed::RANDOM_BLOCK::J5", "acc_at1": 1.0, "gate": ">=0.98",
                                 "result": "PASS both seeds"},
            "negative_control": {"unit": "shuffled_key::GLOBAL_BLOCK::J5", "acc_at1": 0.0,
                                 "gate": "<=0.05/<=0.10", "result": "PASS no leak both seeds"},
            "global_block_keyed_j5_acc": {"seed7": 0.13333334028720856, "seed13": 0.3166666626930237},
            "global_block_ret_agree10": {"seed7": 0.014828555368184016, "seed13": 0.026194491287240888},
            "inbatch_block_ret_agree10": {"seed7": 0.18367060146147768, "seed13": 0.2658909499718906},
            "delta_dense_best": {"seed7": -0.023793385016926072, "seed13": -0.0692288528853594},
            "delta_recompute_match": "exact both seeds (recomputed global_dense_best - inbatch_dense_best "
                                     "vs file recovery.delta_dense_best)",
        },
        "cross_arc_overlap_check_2026_07_04_USER_locked": (
            "no cosine>0.30 hit against this SPECIFIC finding (landmark-vs-inbatch objective comparison); "
            "see companion meta atom for the adjacent-but-distinct 0.3135 hit on a different mechanism "
            "(training-loss-vs-eval-metric mismatch, June 6 LoRA lineage)."
        ),
        "cert_increment_delta": 1,
    }
}

math_atom_bounded_characterization = {
    "id": ("math::MEASURED_MECHANISM_v3c_INBATCH_RKD_ONLY_NCE_OFF_FULL178k_BOUNDED_CHARACTERIZATION_"
           "make_or_break_breakthrough_claim_REFUTED_best_ckpt_selected_from_declining_trajectory_"
           "pearson_step_dense_neg0p88_neg0p81_neg0p08_neg0p28_4_combos_ret_agree10_seed_unstable_"
           "0p146_to_0p674_4p6x_swing_metric_is_spearman_over_mostly_dissimilar_pairs_not_cosine_to_"
           "gold_goal_target_algebra_genuinely_passes_1p000_both_seeds_2026-07-04"),
    "name": ("MATH bounded characterization: the v3c in_batch-RKD-only-nce-off FULL-178k 'best DENSE "
             "0.877-0.895' headline number does NOT represent a stable, goal-equivalent capability. "
             "Genuine positive: keyed-algebra passes cleanly both seeds. Not genuine: the DENSE/BLOCK "
             "spearman 'recovery' is best-of-13-checkpoint-selected from a declining trajectory and "
             "measured with a proxy metric materially easier than the stated 0.85-cosine-to-gold goal."),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_measured_mechanism",
    "description": (
        "MEASURED_MECHANISM (proven-bound tier, 2 FULL seeds): make-or-break audit REFUTES the "
        "'in_batch-RKD-only-nce-off hits the encoder goals' framing on 4 independent rigor checks, off "
        "metrics.json recovery.{global,inbatch}_traj (13-point dense trajectory, dense_eval_every=150) "
        "and per_unit (hi80_cos/hi80_calib_err/ret_agree10 fields), NOT the verdict_msg. "
        "(1) BEST-CHECKPOINT INFLATION CONFIRMED: pearson(step, dense_full) over the eligible (step>0) "
        "trajectory window = seed7 GLOBAL -0.877 / INBATCH -0.813 (strong decline), seed13 GLOBAL -0.077 "
        "/ INBATCH -0.281 (weaker/noisier, still negative-leaning). Recomputed best-to-final decline: "
        "GLOBAL seed7 0.8528->0.6514 (-23.6% rel), seed13 0.8262->0.6191 (-25.1% rel); INBATCH seed7 "
        "0.8766->0.7587 (-13.4% rel), seed13 0.8954->0.7696 (-14.1% rel). GLOBAL's best-step is always "
        "frac=0.083 (earliest eligible eval point, step150/1800) both seeds; INBATCH's best-step is "
        "frac=0.25 (seed7) or 0.083 (seed13) -- best-of-13 selection is consistently drawn from an EARLY "
        "point on a trajectory that continues declining afterward, both arms, both seeds. Direct code "
        "read of _peak_then_decline (core cell, no min_step_for_best filter applied inside the helper) "
        "confirms the cell's own trajectory-shape gate computes 'peak' over the RAW trajectory INCLUDING "
        "the untrained step-0 entry (~0.956 both arms/seeds, always the global max in this regime), making "
        "'not peak_decline' -- required for the cell's own HARD_PASS branch -- structurally unreachable "
        "here regardless of the FALSE_WIN_ALGEBRA outcome; a design gotcha additional to, not the cause "
        "of, the fired HARD_FAIL. "
        "(2) REPRODUCIBILITY GAP: v3b's own NCE_ZERO/GLOBAL run (objective=global, nce=0, batch=128, "
        "steps=1800, seed=7 -- nominally IDENTICAL config) reports FINAL-step dense=0.7335884335345263 "
        "(MEASURED@data/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1/"
        "metrics.json). v3c seed7 GLOBAL final-step dense=0.6513596956724832 -- an 0.0822 (11% relative) "
        "gap between two nominally-identical-seed/config runs, unresolved here (candidate causes: GPU "
        "non-determinism absent explicit determinism flags, or RNG-consumption-order differences between "
        "v3b's 10-arm battery script and v3c's 2-arm script). Evidence that single-run point estimates "
        "(best OR final) in this training regime are not tightly reproducible even holding seed/config "
        "fixed. "
        "(3) 0.368->0.89 COMPARISON CONFOUNDED: v2 FULL in_batch DENSE_SIGN=0.3683089683860061 "
        "(MEASURED@data/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1/metrics.json; "
        "steps=40000, batch=512, nce=0.5, FINAL-step only, no best-of-N tracking existed) differs from "
        "v3c's in_batch DENSE(best) on 4 simultaneously-changed variables (nce_weight, steps [22x fewer], "
        "batch [4x smaller], + a checkpoint-selection policy that did not exist in v2) -- NOT a clean "
        "single-variable NCE-removal comparison. The clean single-axis NCE ablation that DOES exist in "
        "this arc (v3b secondary, GLOBAL objective only) has never been run for the IN_BATCH objective at "
        "matched step budgets; 'NCE removal explains in_batch's rise' is UNVERIFIED. v3c's own in_batch "
        "trajectory already shows a real declining trend within just 1800 steps (see (1)), at least as "
        "consistent with 'in_batch still degrades with more steps, this run simply stopped early and "
        "best-of-13-selected a pre-decline point' as with a clean NCE-driven fix. "
        "(4) METRIC RECONCILIATION GAP CONFIRMED: the stated encoder goal (project_encoder_goals memory "
        "doc, USER-CONFIRMED 2026-07-04) is raw COSINE similarity to the correct/gold answer (~0.54 -> "
        "0.85 target), not Spearman rank-correlation over a large randomly-sampled pair set. Reported "
        "0.877-0.895 numbers are spearman_all over n_pairs_sampled~=400k mostly-DISSIMILAR random pairs "
        "(only hi80_n=217-242, ~0.05-0.06%, have teacher cosine>=0.80, i.e. are goal-relevant-similar "
        "pairs). Closer goal-proxies from the SAME per_unit data show real gaps: hi80_calib_err (student "
        "cosine vs teacher cosine on the gold-similar subset) ranges 0.017-0.142 across the 4 arm-seed "
        "combos; ret_agree10 (top-10 retrieval-neighbor overlap, arguably the closest single proxy to "
        "'does the substrate retrieve the right memory') = INBATCH_DENSE 0.1455(seed7)/0.6742(seed13) -- "
        "a 4.6x seed-to-seed swing -- INBATCH_BLOCK 0.1837(seed7)/0.2659(seed13). By the metric closest to "
        "the actual stated goal, in_batch is weak-to-moderate and highly seed-unstable, not a converged "
        "~0.85-equivalent capability. "
        "WHAT SURVIVES (genuine, not refuted): INBATCH_BLOCK keyed::J5 acc_at1=1.0 both seeds (real, "
        "corroborated bind/unbind roundtrip pass -- encoder goal #4 'algebra must survive' is genuinely "
        "met for this specific in_batch/nce-off configuration). This is the one solid positive from this "
        "cell; everything else claimed as a 'breakthrough' (stable 0.85-equivalent semantic quality) does "
        "NOT survive this audit. "
        "TIER RATIONALE: filed as MEASURED_MECHANISM (proven-bound), not HARD_FAIL, because the cell's own "
        "verdict (HARD_FAIL) already stands and is correct on its own terms (FALSE_WIN_ALGEBRA_GLOBAL); "
        "this atom's job is to prevent an INFLATED reading of the non-gating in_batch DENSE/BLOCK numbers "
        "from propagating as a false capability win. Not filed as a proven negative either -- in_batch's "
        "algebra genuinely passes and its DENSE numbers, while inflated, are not zero; a longer/more "
        "granular re-run designed to resolve items (1)-(4) is the honest next step, not a closure."
    ),
    "aliases": ["v3c_makeorbreak_breakthrough_refuted", "inbatch_rkd_bounded_characterization_not_stable",
                "checkpoint_selection_inflation_case_study_v3c", "spearman_vs_cosine_to_gold_metric_gap_v3c"],
    "metadata": {
        "record_class": "experiment_measured_mechanism_bounded_characterization",
        "cert_status": "measured_mechanism_bounded_characterization_breakthrough_claim_refuted",
        "cert_class": "MEASURED_MECHANISM_v3c_inbatch_headline_number_inflated_not_stable_capability",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_v3c_make_or_break_audit",
        "anchor_seed7": ANCHOR7, "anchor_seed13": ANCHOR13,
        "cell_source_path": CELL_SRC, "cell_commit": CELL_COMMIT, "prereg_path": PREREG,
        "raw_metrics_path_seed7": METRICS7, "raw_metrics_path_seed13": METRICS13,
        "run_mode": "full", "seeds": [7, 13], "device": "cuda",
        "recompute_check": {
            "trend_pearson_step_vs_dense": {"seed7_global": -0.877, "seed7_inbatch": -0.813,
                                            "seed13_global": -0.077, "seed13_inbatch": -0.281},
            "best_to_final_decline_pct": {"global_seed7": -23.6, "global_seed13": -25.1,
                                          "inbatch_seed7": -13.4, "inbatch_seed13": -14.1},
            "v3b_vs_v3c_global_final_reproducibility_gap": {
                "v3b_nce_zero_final_seed7": 0.7335884335345263,
                "v3c_global_final_seed7": 0.6513596956724832,
                "gap": 0.0822287378620431},
            "ret_agree10_seed_instability": {"inbatch_dense_seed7": 0.1455, "inbatch_dense_seed13": 0.6742,
                                             "swing_ratio": 4.63},
            "hi80_calib_err_range": [0.017, 0.142],
            "hi80_n_fraction_of_sampled_pairs": "~217-242 / ~400000 (~0.055%)",
        },
        "composes_with_atoms": [math_atom_landmark_droppable["id"]],
        "cross_arc_overlap_check_2026_07_04_USER_locked": (
            "cosine=0.3135 (above 0.30) on notes/research_drill_LoRA_retrieval_degradation_3x_deep_2026-06-06.md "
            "training-loss-vs-eval-metric mismatch lesson -- read directly, DIFFERENT lineage/mechanism "
            "(SFT-vs-retrieval gradient-direction pre-registration, not checkpoint-selection cherry-pick "
            "or within-eval proxy-metric choice); adjacent in spirit, not a rediscovery. See companion "
            "meta atom."
        ),
        "cert_increment_delta": 1,
    }
}

meta_atom_checkpoint_and_metric = {
    "id": ("meta::META_best_checkpoint_selection_from_small_number_of_coarse_eval_points_can_cherry_pick_"
           "transient_peak_from_declining_trajectory_cross_seed_agreement_of_MAX_statistic_does_NOT_"
           "establish_stability_PLUS_goal_metric_verification_rank_correlation_over_random_pairs_is_NOT_"
           "equivalent_to_cosine_to_gold_when_goal_is_stated_as_raw_cosine_case_study_v3c_encoder_2026-07-04"),
    "name": ("META rule (2-part, MM_TENTATIVE): (a) best-of-N checkpoint selection over a small number of "
             "coarse eval points can cherry-pick a transient peak from a declining/volatile trajectory; "
             "tight cross-seed agreement of the SELECTED MAX does not establish the underlying process is "
             "stable, since max-order-statistics compress variance regardless of true stability. (b) when "
             "a capability goal is stated as raw cosine-to-gold-similarity, a Spearman rank-correlation "
             "over a large randomly-sampled (mostly-dissimilar) pair set is NOT the same metric and can "
             "overstate apparent capability -- check the goal-relevant high-similarity subset directly "
             "(raw cosine + calibration error) and a retrieval-agreement metric before treating a "
             "rank-correlation number as evidence the goal is met."),
    "corpus": "meta",
    "tier": "T4",
    "kind": "methodology_rule",
    "description": (
        "MM_TENTATIVE methodology rule (case study 1 of a needed 2 more independent catches before "
        "MM_STANDARD, per this ledger's established promotion convention). "
        "PART (a) CHECKPOINT-SELECTION-BIAS: when a cell reports a 'best-checkpoint' result selected via "
        "argmax over a SMALL number of coarse-grained eval points (here: 13 points, spaced 150 steps apart "
        "over 1800 total steps) on a metric whose trajectory shows real non-monotonic behavior or decline "
        "(confirmed via pearson/spearman correlation of step-vs-metric within the eligible window, not "
        "eyeballing), the SELECTED value is a max-order-statistic, not a converged/stable value. A tight "
        "cross-seed cv on that max-order-statistic does NOT validate stability -- max statistics naturally "
        "have compressed variance relative to the underlying process being sampled, so 2-seed agreement on "
        "a best-of-13-selected value is much weaker evidence than 2-seed agreement on the FINAL (fully-"
        "trained, non-selected) value would be. A trajectory-shape gate intended to catch this (e.g. "
        "peak-then-decline vs the eligible best) must exclude any known-artifact reference point (e.g. an "
        "untrained-network step-0 spike) from the PEAK computation itself, not just from best-checkpoint "
        "ELIGIBILITY -- computing peak-then-decline over the raw trajectory (including the excluded-from-"
        "eligibility step-0 point) makes the gate structurally vacuous if that excluded point is always "
        "the trajectory max, as verified here (both arms, both seeds). "
        "CASE STUDY (v3c encoder distillation, verified via direct code read of experiments/exp_encoder_"
        "migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py, commit "
        "94062aeccdc0381067a8f889f2050d1edb5373b4, function _peak_then_decline): the reported in_batch-RKD-"
        "only DENSE(best)=0.877-0.895 is drawn from a trajectory with pearson(step,dense)=-0.81 to -0.28 "
        "(3 of 4 arm-seed combos strongly-to-moderately negative), and the eligible-best-to-final decline "
        "is 13-25% relative across all 4 arm-seed combos measured -- i.e. the reported headline numbers "
        "are NOT stable plateaus. "
        "PART (b) GOAL-METRIC-FIDELITY: when a capability goal is stated in a specific metric (here: raw "
        "cosine similarity to a correct/gold answer, per project_encoder_goals memory doc, USER-CONFIRMED "
        "2026-07-04, '~0.54 cosine today -> 0.85 target'), a DIFFERENT metric computed over a broader "
        "evaluation set (here: Spearman rank-correlation over ~400k randomly-sampled pairs, of which only "
        "~0.05-0.06% are actually gold-similar / goal-relevant) is a materially EASIER target and must NOT "
        "be treated as equivalent without checking the goal-relevant subset directly. Before citing a "
        "rank-correlation number against a stated raw-similarity or retrieval-accuracy goal, decompose the "
        "eval and check: (i) the raw-value metric restricted to the goal-relevant subset (here: hi80_cos / "
        "hi80_calib_err, gold-cosine>=0.80 subset) and (ii) a retrieval-style agreement metric (here: "
        "ret_agree10, top-K neighbor overlap) -- both were ALREADY being computed and logged by this cell "
        "(per_unit fields) but were not the field cited as the headline discriminator. CASE STUDY: v3c's "
        "hi80_calib_err ranges 0.017-0.142 (meaningful miscalibration on the goal-relevant subset) and "
        "ret_agree10 for the same 'winning' arm ranges 0.1455-0.6742 across seeds (4.6x swing) -- neither "
        "supports a confident 'hits 0.85' reading despite the headline spearman sitting at 0.877-0.895. "
        "ADJACENT-BUT-DISTINCT from the June-6 LoRA lineage's training-loss-vs-eval-metric pre-registration "
        "rule (cosine=0.3135 hit, notes/research_drill_LoRA_retrieval_degradation_3x_deep_2026-06-06.md): "
        "that rule is about TRAINING LOSS gradient-direction compatibility with the eval metric; this rule "
        "is about CHOICE OF EVAL PROXY METRIC within evaluation (not training), plus the independently-"
        "distinct checkpoint-selection-bias mechanism in part (a). Both share the family resemblance 'the "
        "number you are citing is not the number that matters' -- filed as a related-but-separate case "
        "study per the cross-arc-overlap discipline, not a rediscovery. "
        "ACTIONABLE: before promoting any best-checkpoint-selected or rank-correlation-only result to "
        "CHAIN_GRADE, require (1) a step-vs-metric trend statistic (pearson/spearman) demonstrating no "
        "significant decline in the eligible window, or an explicit acknowledgment that the reported value "
        "is a peak not a plateau; (2) the FINAL (non-selected) value reported alongside the best value, "
        "always; (3) when a stated goal specifies a particular metric or a particular subset (e.g. "
        "'similar-pairs cosine' or 'retrieval accuracy'), that EXACT metric/subset computed and reported, "
        "not a proxy from a broader/easier population."
    ),
    "aliases": ["checkpoint_selection_bias_max_statistic_rule", "goal_metric_fidelity_rank_corr_vs_cosine_rule",
                "v3c_peak_then_decline_gate_vacuous_step0_artifact_gotcha"],
    "metadata": {
        "record_class": "methodology_rule_inflation_and_metric_mismatch_detection",
        "cert_status": "mm_tentative_methodology_rule",
        "cert_class": "MM_TENTATIVE_META_RULE_checkpoint_selection_bias_and_goal_metric_fidelity",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_v3c_make_or_break_audit",
        "cell_source_path": CELL_SRC, "cell_commit": CELL_COMMIT,
        "raw_metrics_path_seed7": METRICS7, "raw_metrics_path_seed13": METRICS13,
        "composes_with_atoms": [math_atom_bounded_characterization["id"], math_atom_landmark_droppable["id"]],
        "promotion_path": "MM_TENTATIVE -> MM_STANDARD after 2 more independent catches of either sub-part "
                          "(a) or (b) in a different cell/lineage, per this ledger's established convention "
                          "(see meta::T4/META_auditor_discipline_...Fix28_pre_landing_atomization... "
                          "2026-07-04 for the precedent pattern).",
        "cert_increment_delta": 1,
    }
}


def a5_append(path, atom):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_atoms_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    n_lines = 0
    found = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_lines += 1
            obj = json.loads(line)  # integrity: raises on corrupt line
            aid = obj.get("id") or obj.get("atom_id")
            if aid == atom["id"]:
                found += 1
    if found != 1:
        raise RuntimeError(f"verify-load failed: atom id found {found}x (expected 1) in {path}")
    return n_lines


def ledger_append(atom, session_tag, ledger_path=CERT_LEDGER):
    entry = {
        "ts": TS,
        "ts_iso": TS_ISO,
        "atom_id": atom["id"],
        "corpus": atom["corpus"],
        "cert_status": atom["metadata"].get("cert_status"),
        "cert_class": atom["metadata"].get("cert_class"),
        "cert_increment_delta": atom["metadata"].get("cert_increment_delta", 0),
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_v3c_make_or_break_audit",
        "landed_VET_session": session_tag,
    }
    d = os.path.dirname(ledger_path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_ledger_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if os.path.exists(ledger_path):
                with open(ledger_path, "r", encoding="utf-8") as src:
                    for line in src:
                        f.write(line)
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ledger_path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    print(f"[atomize] ts_iso={TS_ISO}")
    tag = "2026-07-04_v3c_make_or_break_audit"
    n_math1 = a5_append(MATH_ATOMS, math_atom_landmark_droppable)
    print(f"[atomize] math MM_STANDARD landmark-droppable atom appended; math lines={n_math1}")
    n_math2 = a5_append(MATH_ATOMS, math_atom_bounded_characterization)
    print(f"[atomize] math MEASURED_MECHANISM bounded-characterization (breakthrough refuted) atom "
          f"appended; math lines={n_math2}")
    n_meta = a5_append(META_ATOMS, meta_atom_checkpoint_and_metric)
    print(f"[atomize] meta MM_TENTATIVE checkpoint-selection-bias + goal-metric-fidelity rule appended; "
          f"meta lines={n_meta}")
    ledger_append(math_atom_landmark_droppable, tag)
    ledger_append(math_atom_bounded_characterization, tag)
    ledger_append(meta_atom_checkpoint_and_metric, tag)
    print("[atomize] DONE 3 atoms + 3 ledger entries; A5-gated (tmp+os.replace+verify-load+json-integrity); "
          "matching TS_ISO")
    print("[atomize] NET CERT DELTA: CG 0, MM +3 (2 math MM_STANDARD/MEASURED_MECHANISM, 1 meta "
          "MM_TENTATIVE), HF 0")
    print("[atomize] make-or-break BREAKTHROUGH CLAIM: REFUTED. Landmark objective: confirmed droppable "
          "(genuine, corroborated). In-batch-RKD-only 'hits 0.85 stably': NOT supported once "
          "best-checkpoint-selection and goal-metric-fidelity are checked off disk.")
