"""
A5-gated atomization -- Skunkworks landed-VET of Encoder Migration Step 1b v3b
(batch-ratio-match sweep PRIMARY + NCE-weight ablation SECONDARY), MID scale,
single seed=7. 2026-07-04.

CELL: experiments/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1_core.py
      (commit 84044e6f3)
DATA: data/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1/metrics.json
      run_mode=mid, seed=7, device=cuda, n_units=19/19, unit_failures=0.
PREREG: preregs/2026-07-04_exp_encoder_migration_step1b_v3b_batch_ratio_nce_ablation_dense_recovery_diagnostic_v1.md

===================== INDEPENDENT RECOMPUTE (Skunkworks, off per_unit + cell source, NOT verdict_msg) =====================
Integrity gates (all verified off metrics.json['per_unit'], not the recovery/summary block):
  cardinality_ok: n_units=19==expected_n_units=19, unit_failures=[].
  positive control FIRST (auditor discipline): keyed::RANDOM_BLOCK::J5 acc_at1=1.0 hit_any_member=1.0
    (n_trials=60) -- clears SBC-lossless prior (>=0.98 gate) BEFORE trusting anything else.
  negative control: shuffled_key::B128_GLOBAL_BLOCK::J5 acc_at1=0.0 hit_any_member=0.0 -- no key leak.
  arms_differ_verified=True (sha256 over all 16 arm-code matrices distinct, META_RULE_AF, code-enforced
    RuntimeError on any duplicate -- did not fire).
  H1 vs H2 (real degradation vs quick-eval subsample noise): b512_global_quick_vs_full_traj_corr=0.99954,
    h1_h2_verdict=H1_REAL_DEGRADATION -- the oscillating dense trajectory under nce_weight=0.5 is a REAL
    training-dynamics phenomenon, not quick-eval measurement noise.
  eval fairness (secondary ablation): n_held=5000 (=min(round(177899*HELD_FRAC=0.10), MID_HELD_CAP=5000)
    from v3 constants, matches top-level n_held field exactly); ALL final per-arm units (sweep arms AND
    ablation arms) call the identical v3._semantic_unit(..., Xhe, Xhe, 0, full_final_pairs=400000, seed+3)
    -- same held set, same pair-sample size, same seed -> literally the same 400k held pairs scored for
    every arm. No held/train leakage (he_idx sliced after tr_idx from one np.random.default_rng(seed)
    permutation of the 177899-concept teacher cache; land_idx drawn only from tr_idx). CONFIRMED FAIR.
  single-axis isolation (secondary): ablation arms (NCE_ZERO, NCE_DECAY40) and the reused NCE_CURRENT
    reference (=B128_GLOBAL) share decisive_batch=128, objective="global", seed=7, land_idx, refresh_every,
    steps=1800 -- verified in cell source (_train_student_diag calls at lines ~719-742): the ONLY thing that
    differs across {NCE_CURRENT, NCE_ZERO, NCE_DECAY40} is the nce_weight_fn passed in. Clean single-axis
    ablation, confirmed by direct code read (not just docstring claim).

SECONDARY (NCE-weight ablation) recompute, off per_unit directly:
  B128_GLOBAL_DENSE (=NCE_CURRENT, nce_weight=0.5 const) spearman_all = 0.26872242802875473
  NCE_ZERO_DENSE   (nce_weight=0.0 const, RKD-only)       spearman_all = 0.7335884335345263
  NCE_DECAY40_DENSE (nce_weight 0.5->0 anneal from step 720) spearman_all = 0.5127543402335915
  ablation_delta (recomputed) = 0.7335884335345263 - 0.26872242802875473 = 0.46486600550577157
    (file's recovery.ablation_delta_final = 0.46486600550577156 -- matches to float precision, PASS)
  best_ablation_final=0.7336 >= ABLATION_HP_DENSE_FINAL(0.70) AND delta=0.4649 >= ABLATION_HP_DELTA(0.15)
    -> TAIL_CORRUPTION_CONFIRMED_RECOVERED verdict reproduces exactly off the per-arm numbers.
  PASS. This is a genuine, clean, well-isolated finding: a constant nce_weight=0.5 contrastive term
  materially corrupts the distilled dense-recovery geometry late in training (RKD converges by ~step
  700-900 per all trajectories; the constant-weight NCE term keeps pushing after that and visibly degrades
  dense score for the rest of training in every nce=0.5 arm). Zeroing or decaying the term recovers most
  (NCE_ZERO: +0.465) or partial (NCE_DECAY40: +0.244) of the loss.
  CAVEAT: single seed (seed=7 only, MID scale). No cross-seed cv is computable. Tiered MM_STANDARD with an
  explicit single-seed flag, not inflated to CG; a second seed replicate is the natural expansion path.

PRIMARY (batch-ratio-match sweep) recompute + mechanism-class determination, off per_unit + cell SOURCE:
  decisive_global_dense (B128_GLOBAL_DENSE) = 0.26872242802875473 (matches file)
  decisive_inbatch_dense (B128_INBATCH_DENSE) = 0.4659925448741608 (matches file)
  decisive_delta (recomputed) = 0.26872242802875473 - 0.4659925448741608 = -0.19727011684540607
    (file's recovery.decisive_delta = -0.19727011684540607 -- EXACT match, PASS)
  HARD_FAIL verdict machinery itself reproduces correctly off the per-arm numbers (thresholds/gating logic
  in _verdict_diag are internally consistent with the filed verdict). The verdict-LOGIC is not broken.

  QUESTION: is the HARD_FAIL a clean negative (a), a MID-cannot-substitute-for-FULL design limit (b), or
  confounded by the constant NCE term (c)? DETERMINED BY DIRECT CODE READ (not inference from the docstring's
  own hedge, which already flagged "or another confound is present" as an open possibility -- this VET
  resolves that open question to a CONFIRMED fact):
    - Cell source (_train_student_diag call site, run_diag loop over `for B in batch_sweep: for obj_key, obj
      in (("GLOBAL","global"),("INBATCH","in_batch")):`) passes `_nce_weight_current` (v3.LAM_NCE=0.5 CONST,
      never 0, never decayed) for ALL 8 sweep arms (B512/256/128/64 x GLOBAL/INBATCH). This is NOT a
      hypothesis -- it is what the code does, confirmed by reading the training-loop wiring directly.
    - The SECONDARY's own clean ablation (same decisive batch=128, same objective=global) proves nce_weight=
      0.5 costs 0.465 dense-spearman relative to nce_weight=0 (0.269 vs 0.734), and every nce=0.5 trajectory
      in the file shows large non-monotonic oscillation with best_step=0 for literally every arm (peak dense
      score occurs before any effective training; net effect of nce=0.5 training is degradation from that
      peak) -- confirmed as REAL (not eval noise) via the H1/H2 check above.
    - Consequence: EVERY arm in the primary 8-arm sweep is trained under the identical corrupting term the
      secondary indicts. The "decisive_delta" (global worse than in_batch by 0.197 at B=128) and the
      cross-batch trend metrics (inbatch_degradation, trend_corr) are measured entirely inside a training
      regime dominated by nce=0.5 tail-corruption dynamics, not on clean RKD-only geometry. The two RKD
      objectives (GLOBAL: fixed-landmark-frame supervision; IN_BATCH: within-batch pairwise supervision) are
      not guaranteed to interact identically with that corrupting term -- IN_BATCH's RKD term and the NCE
      term both draw structure from the SAME current batch, while GLOBAL's RKD term is anchored to an
      independent fixed frame; a differential interaction with the shared corrupting term is a live,
      untested alternative explanation for the observed delta, fully independent of the intended
      coverage-ratio-collapse mechanism.
    - Additionally (secondary confound layer, noted not scored): the l_nce term's in-batch negative logits
      (`lg_i = s_n@s_n.T` over the CURRENT batch, computed identically regardless of `objective`) mean batch
      size ALSO modulates NCE strength/negative-count directly, independent of the intended RKD-coverage-ratio
      mechanism -- so the CROSS-BATCH trend readings (inbatch_degradation, trend_corr) carry a second,
      unswept nuisance axis beyond the same-batch decisive-delta comparison.
  DETERMINATION: PRIMARY category = (c) CONFOUNDED BY THE NCE TERM, confirmed structurally (not speculative).
  This is NOT category (a) -- it cannot be read as a clean "landmark/global objective does not help"
  negative, because both arms share the identical corrupting term proven (by the cell's own secondary) to
  materially distort the very metric being compared. It is also not simply category (b) (MID-vs-FULL scale
  limitation) -- that question remains untested here, since the coverage-ratio hypothesis was never tried
  under a clean (nce=0 or decayed) regime at any scale in this cell.
  DISPOSITION: PRIMARY HARD_FAIL as filed on disk is technically internally consistent (verdict-logic
  reproduces exactly off the per-arm numbers, no crash, cardinality_ok, controls pass) but its INTERPRETATION
  ("landmark objective does not help") is INVALID due to the confirmed confound. Per symmetric
  anti-negativity (do not inflate negatives, same as positives): this must NOT be filed as a proven negative
  and must NOT count against the landmark/global-objective hypothesis. cert_increment_delta=0 for the
  primary; no math-corpus atom is filed for it (would be a false-negative inflation into the ledger).
  ACTIONABLE CONSEQUENCE: the coverage-ratio-collapse hypothesis (global vs in_batch across batch sizes) has
  NOT yet been cleanly tested at any scale; it needs the NCE term ablated/decayed in the sweep itself before
  it can discriminate anything. This VET result is therefore net-SUPPORTIVE of the already-dispatched
  NCE-off FULL run being the correct next step (not evidence to deprioritize the landmark-objective line).

CROSS-ARC OVERLAP CHECK (USER-locked 2026-07-01): bash tools/substrate_query.sh "constant NCE contrastive
  weight tail corruption RKD distillation checkpoint select batch coverage ratio landmark objective" ->
  top hits cosine 0.332/0.325/0.324/0.324 (generic FrameNet/WordNet ontology entities: Cognitive_connection,
  distillation, copulative_conjunction, consecutive_operation -- vocabulary-overlap only, not empirical
  findings) and cosine 0.318 note "Alternative 2: InfoNCE contrastive distillation (already routed)" from
  notes/research_drill_cell3_distillation_alternatives_2x_2026-06-07.md -- read directly: this is a JUNE-7
  PRE-EXPERIMENT PLANNING doc for a DIFFERENT lineage (CELL-3 student distilled from Llama-1B teacher,
  compared against bge-small, all numbers P_theoretical/P_empirical PREDICTIONS not measurements), unrelated
  teacher/pipeline to this BGE-large-v2/landmark-RKD/v3b lineage. NOT a prior arc-cell rediscovery. Genuinely
  novel finding for this lineage.

DESIGN-CANNOT-REMANUFACTURE note: the confound determination above is a code-level structural fact (same
  nce_weight_fn object passed to every sweep arm), not a statistical artifact of an unpaired/noisy
  discriminator -- distinct failure mode from the retired paired-trials cross-term family, filed here as its
  own meta rule (compound-loss ablation-completeness), not a re-application of the paired-trials rule.
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

ANCHOR = "encoder_migration_step1b_v3b_batch_ratio_match_nce_ablation_dense_recovery_v1_mid"
METRICS = f"data/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1/metrics.json"
CELL_SRC = "experiments/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1_core.py"
CELL_COMMIT = "84044e6f3"
PREREG = "preregs/2026-07-04_exp_encoder_migration_step1b_v3b_batch_ratio_nce_ablation_dense_recovery_diagnostic_v1.md"

math_atom = {
    "id": ("math::MEASURED_MECHANISM_v3b_NCE_CONSTANT_WEIGHT_TAIL_CORRUPTS_DISTILLED_DENSE_RECOVERY_"
           "single_seed7_MID_nce_current_0p5_const_dense_0p269_vs_nce_zero_RKD_only_dense_0p734_delta_"
           "0p465_nce_decay40_partial_0p513_clean_single_axis_ablation_same_decisive_batch128_same_"
           "objective_global_same_held_n5000_same_400k_pair_sample_seed_no_eval_leak_H1_real_degradation_"
           "quick_full_traj_corr_0p9995_2026-07-04"),
    "name": ("MATH constant nce_weight=0.5 contrastive tail CORRUPTS distilled dense-recovery geometry "
             "(single-seed MID, clean ablation). NCE_CURRENT(0.5 const) dense=0.269 vs NCE_ZERO(RKD-only) "
             "dense=0.734, delta +0.465; NCE_DECAY40 (anneal 0.5->0 from step 720/1800) partial dense=0.513, "
             "delta +0.244. Same decisive_batch=128/objective=global/seed=7/held-set n=5000/400k-pair eval "
             "budget across all three arms -- clean single-axis (nce-weight-only) ablation, verified off "
             "per_unit + cell source, not the recovery/summary block."),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record_measured_mechanism",
    "description": (
        "MM_STANDARD (single-seed caveat) measurement: a constant-weight (lambda=0.5) InfoNCE contrastive "
        "term, added on top of an RKD (relational-knowledge-distillation) landmark-frame objective for a "
        "BGE-large-v2 concept-encoder distillation student (MLP, 4096-dim block-quantized output, 177899-"
        "concept teacher cache, MID scale train~172899/held=5000), materially corrupts the student's final "
        "dense-spearman agreement with the teacher's pairwise structure late in training. "
        "RECOMPUTE (off metrics.json['per_unit'], independent of recovery/summary/verdict_msg): "
        "B128_GLOBAL_DENSE (this arm doubles as NCE_CURRENT, nce_weight=0.5 const) spearman_all=0.26872242802875473; "
        "NCE_ZERO_DENSE (nce_weight=0.0 const, RKD-only) spearman_all=0.7335884335345263; "
        "NCE_DECAY40_DENSE (nce_weight anneals 0.5->0 linearly from step 0.4*1800=720) spearman_all=0.5127543402335915. "
        "ablation_delta recomputed = 0.7335884335345263-0.26872242802875473 = 0.46486600550577157, matches file's "
        "recovery.ablation_delta_final=0.46486600550577156 to float precision. TAIL_CORRUPTION_CONFIRMED_RECOVERED "
        "verdict reproduces exactly against the prereg's own bands (best_ablation>=0.70 AND delta>=0.15). "
        "FAIRNESS/ISOLATION (verified off cell source, not docstring claim): all three arms (NCE_CURRENT=reused-"
        "B128_GLOBAL, NCE_ZERO, NCE_DECAY40) share decisive_batch=128, objective='global', seed=7, land_idx, "
        "refresh_every=50, steps=1800 -- the ONLY difference is the nce_weight_fn passed to _train_student_diag. "
        "Eval uses the SAME held set (n_held=5000 = min(round(177899*HELD_FRAC0.10), MID_HELD_CAP5000), no "
        "train/held index overlap by construction) and the SAME v3._semantic_unit(..., full_final_pairs=400000, "
        "seed+3) call for every final arm -- literally the same 400k held pairs scored for every arm, no eval "
        "leakage. Positive control (keyed RANDOM_BLOCK J5 acc_at1=1.0) clears its own floor FIRST (auditor "
        "discipline) before trusting the null; negative control (shuffled_key acc_at1=0.0) shows no key leak; "
        "cardinality_ok (19/19 units, 0 failures); arms_differ_verified via sha256 (META_RULE_AF, all distinct). "
        "H1-vs-H2 settled for the reference trajectory: quick-vs-full dense correlation=0.99954, "
        "H1_REAL_DEGRADATION -- the oscillating trajectories under nce=0.5 are genuine training dynamics, not "
        "quick-eval subsample noise. "
        "MECHANISM: RKD converges by roughly step 700-900 in every trajectory (rkd loss term plateaus); the "
        "constant-weight NCE gradient keeps pushing after that point and visibly degrades dense agreement for "
        "the remainder of training whenever nce_weight stays at 0.5 (every such arm shows best_step=0, i.e. "
        "peak dense score occurs before/at the first training step and net training under nce=0.5 only "
        "degrades from there); zeroing the term (NCE_ZERO) or decaying it after the RKD-plateau point "
        "(NCE_DECAY40) recovers most (+0.465) or partial (+0.244) of the loss. "
        "CAVEAT (honest, not inflated): single seed (seed=7), MID scale only -- no cross-seed cv is computable "
        "from this landing. Tiered MM_STANDARD with an explicit single-seed flag rather than promoted to CG; "
        "a second-seed MID replicate (or the seed=7 FULL-scale run) confirming the same qualitative ordering "
        "(NCE_ZERO >> NCE_CURRENT, NCE_DECAY40 intermediate) is the natural path to full multi-seed confidence."
    ),
    "aliases": ["v3b_nce_tail_corruption_confirmed_recovered", "encoder_distill_NCE_constant_weight_tail_corruption",
                "RKD_plateau_NCE_gradient_overshoot_MID_single_seed"],
    "metadata": {
        "record_class": "experiment_measured_mechanism_single_seed",
        "term_class": "ENCODER_MIGRATION_STEP1B_NCE_TAIL_CORRUPTION",
        "cert_status": "mm_standard_single_seed_measured_mechanism",
        "cert_class": "MM_STANDARD_nce_constant_weight_tail_corruption_confirmed_recovered_single_seed",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_v3b_nce_confound_and_tail_corruption",
        "anchor": ANCHOR,
        "cell_source_path": CELL_SRC,
        "cell_commit": CELL_COMMIT,
        "prereg_path": PREREG,
        "raw_metrics_path": METRICS,
        "run_mode": "mid", "seed": 7, "device": "cuda", "n_seeds": 1,
        "verdict_on_disk": "HARD_FAIL (gates on the PRIMARY batch-ratio-match sweep only; the ablation_verdict "
                           "sub-field TAIL_CORRUPTION_CONFIRMED_RECOVERED is the secondary finding filed here)",
        "recompute_check": {
            "method": "read per_unit list directly (19 semantic/keyed/shuffled_key entries), recomputed "
                       "ablation_delta and decisive_delta from those raw spearman_all values, cross-checked "
                       "cell source (_train_student_diag call sites) for single-axis isolation, independent of "
                       "recovery block or verdict_msg text",
            "nce_current_dense": 0.26872242802875473, "nce_zero_dense": 0.7335884335345263,
            "nce_decay40_dense": 0.5127543402335915,
            "ablation_delta_recomputed": 0.46486600550577157,
            "ablation_delta_file": 0.46486600550577156,
            "match": "exact to float precision",
            "h1_h2_check": {"b512_global_quick_vs_full_traj_corr": 0.9995439726283971,
                            "verdict": "H1_REAL_DEGRADATION"},
            "positive_control": {"unit": "keyed::RANDOM_BLOCK::J5", "acc_at1": 1.0, "hit_any_member": 1.0,
                                 "n_trials": 60, "gate": ">=0.98", "result": "PASS"},
            "negative_control": {"unit": "shuffled_key::B128_GLOBAL_BLOCK::J5", "acc_at1": 0.0,
                                 "hit_any_member": 0.0, "gate": "<=0.05/<=0.10", "result": "PASS no leak"},
            "cardinality": "19/19 units, unit_failures=[]",
        },
        "single_seed_caveat": True,
        "expansion_to_full_confidence": "second seed at MID scale (or the seed=7 FULL-scale run already "
                                        "planned) confirming NCE_ZERO >> NCE_CURRENT ordering with cross-seed "
                                        "cv < 0.20",
        "cross_arc_overlap_check_2026_07_04_USER_locked": (
            "substrate_query top hits cosine 0.332/0.325/0.324/0.324 (generic FrameNet/WordNet vocabulary "
            "matches, not empirical findings) and cosine 0.318 note 'Alternative 2: InfoNCE contrastive "
            "distillation (already routed)' from notes/research_drill_cell3_distillation_alternatives_2x_"
            "2026-06-07.md -- read directly: a June-7 PRE-EXPERIMENT PLANNING doc for an unrelated lineage "
            "(CELL-3/Llama-1B-teacher vs bge-small comparison, all numbers are P_theoretical/P_empirical "
            "PREDICTIONS, not measurements). NOT a prior arc-cell rediscovery; genuinely novel for this "
            "BGE-large-v2/landmark-RKD/v3b lineage."
        ),
        "cert_increment_delta": 1,
    }
}

meta_atom = {
    "id": ("meta::META_compound_loss_ablation_completeness_MANDATORY_when_using_a_multi_term_objective_"
           "loss_eq_A_plus_w_times_B_as_an_arm_comparison_discriminator_the_nuisance_term_B_weight_must_"
           "be_ablated_or_swept_too_not_held_constant_case_study_v3b_batch_ratio_match_sweep_ALL_8_arms_"
           "shared_nce_weight_0p5_const_the_SAME_term_the_cells_own_secondary_ablation_shows_costs_0p465_"
           "dense_spearman_PRIMARY_HARD_FAIL_confound_class_c_confirmed_by_direct_code_read_not_speculative_"
           "verdict_should_not_count_as_a_proven_negative_on_the_swept_axis_2026-07-04"),
    "name": ("META compound-loss ablation-completeness MANDATORY: when a multi-term training objective "
             "(loss = A_of_interest + w*B_nuisance) is used to run an arm-comparison sweep on axis-of-"
             "interest A, the nuisance term B's weight must ALSO be ablated/swept (or zeroed) in that same "
             "sweep if a companion measurement shows B materially distorts the metric -- otherwise every arm "
             "shares the identical confound and the sweep cannot discriminate the intended mechanism from "
             "differential arm-by-B interaction. Case study: v3b encoder distillation batch-ratio-match "
             "sweep (global-landmark-RKD vs in-batch-RKD objective, x4 batch sizes) ran ALL 8 arms at "
             "constant nce_weight=0.5; the cell's OWN secondary ablation shows nce_weight=0.5 costs 0.465 "
             "dense-spearman vs nce_weight=0. The PRIMARY HARD_FAIL is therefore CONFOUNDED (category c), "
             "not a clean negative on the landmark-objective hypothesis -- confirmed by direct code read "
             "(same nce_weight_fn object passed to every sweep arm), not mere speculation."),
    "corpus": "meta",
    "tier": "T4",
    "kind": "methodology_rule",
    "description": (
        "MM_STANDARD methodology rule (new; distinct from and does not supersede the 2026-07-04 "
        "paired-trials-mandatory rule, which addresses UNPAIRED statistical-noise cross-terms -- this rule "
        "addresses a STRUCTURAL shared-nuisance confound present even in a fully paired/deterministic-per-arm "
        "design). RULE: before trusting an arm-comparison sweep run under a multi-term loss (loss = "
        "A_of_interest + w*B_nuisance, w held CONSTANT across all swept arms), check whether any companion "
        "measurement (an ablation of B) shows B materially affects the metric being compared. If so, the "
        "sweep on A is confounded until B is also ablated/zeroed/decayed within that same sweep design -- "
        "holding w(B) constant does NOT make the A-comparison clean merely because w(B) is identical across "
        "arms, because A and B can interact DIFFERENTLY (non-additively) across the arms of A (e.g. one arm's "
        "A-mechanism draws structure from the same source B's gradient competes over, another arm's does "
        "not) -- confirm or exclude this via code-level trace of the loss construction, not via docstring "
        "assertion or verdict-message hedge text alone. "
        "CASE STUDY (verified via direct code read of experiments/exp_encoder_migration_step1b_v3b_nce_"
        "ablation_dense_recovery_diagnostic_v1_core.py, commit 84044e6f3): the PRIMARY discriminator "
        "(batch-ratio-match sweep: {512,256,128,64} batch x {global-landmark-RKD, in-batch-RKD} objective, "
        "8 arms) trains every arm via _train_student_diag(..., _nce_weight_current, ...) where "
        "_nce_weight_current always returns v3.LAM_NCE=0.5 CONSTANT -- confirmed at the training-loop call "
        "site, not inferred. The SAME cell's SECONDARY ablation (NCE_ZERO vs NCE_CURRENT at the decisive "
        "batch=128) shows nce_weight=0.5 costs 0.465 dense-spearman relative to nce_weight=0 (0.269 vs 0.734), "
        "and every nce=0.5 trajectory shows large non-monotonic oscillation with best_step=0 (peak dense "
        "score at/before the first effective training step; training only degrades thereafter under nce=0.5), "
        "confirmed as REAL (not quick-eval noise) via a quick-vs-full trajectory correlation check (0.9995, "
        "H1_REAL_DEGRADATION). The two RKD objectives interact with the batch-local NCE term differently by "
        "construction: IN_BATCH's RKD term and the NCE term's in-batch negatives (lg_i = s_n@s_n.T over the "
        "CURRENT batch, computed identically regardless of objective) both draw structure from the same "
        "current batch, while GLOBAL's RKD term is anchored to an independent fixed landmark frame -- a "
        "differential A-B interaction is a live, untested alternative explanation for the observed "
        "decisive_delta (-0.197, global worse than in_batch at B=128), fully independent of the intended "
        "coverage-ratio-collapse mechanism the sweep was designed to test. Batch size ALSO directly modulates "
        "NCE strength/negative-count via that same lg_i term (independent of the intended RKD-coverage-ratio "
        "mechanism), so the cross-batch trend metrics (inbatch_degradation, trend_corr) carry a SECOND unswept "
        "nuisance axis beyond the same-batch decisive-delta comparison. "
        "CONSEQUENCE FOR THE FILED VERDICT: the v3b PRIMARY HARD_FAIL "
        "(BATCH_RATIO_MATCH_DID_NOT_CONFIRM, MEASURED@data/exp_encoder_migration_step1b_v3b_nce_ablation_"
        "dense_recovery_diagnostic_v1/metrics.json:recovery) is internally consistent (verdict-logic "
        "reproduces exactly off the per-arm numbers, cardinality_ok, controls pass, no crash) but its "
        "INTERPRETATION as a clean negative on the landmark/global-objective hypothesis is INVALID. Per "
        "symmetric anti-negativity (Fix#28 discipline extended to confounds, not just to inflation): this "
        "must NOT be filed or treated as a proven negative and must NOT count against the landmark-objective "
        "line. cert_increment_delta=0 was assigned to the primary (no math-corpus atom filed for it) to avoid "
        "a false-negative inflation into the ledger. The cell's own docstring already hedged toward this "
        "('...or another confound is present') -- this rule converts that hedge into a CONFIRMED, code-level "
        "fact and generalizes the lesson for future compound-loss discriminator cells. "
        "ACTIONABLE: the coverage-ratio-collapse hypothesis (global-landmark vs in-batch RKD objective across "
        "batch sizes) has NOT yet been cleanly tested at any scale; any re-run of this sweep family must "
        "ablate or decay the nuisance loss term (here: nce_weight) within the sweep itself before the "
        "sweep's delta/trend metrics can be trusted as evidence about the swept axis. This VET is therefore "
        "net-SUPPORTIVE of dispatching a clean (NCE-off) re-run rather than evidence to deprioritize the "
        "landmark-objective line."
    ),
    "aliases": ["compound_loss_ablation_completeness_rule", "shared_nuisance_term_confound_arm_comparison",
                "v3b_NCE_confound_primary_HARD_FAIL_invalidated"],
    "metadata": {
        "record_class": "methodology_rule_confound_detection",
        "cert_status": "mm_standard_methodology_rule",
        "cert_class": "MM_STANDARD_META_RULE_compound_loss_ablation_completeness",
        "cert_ts": TS_ISO,
        "verified_off_data": True,
        "atomized_by": "skunkworks_landed_VET_2026-07-04_v3b_nce_confound_and_tail_corruption",
        "anchor": ANCHOR,
        "cell_source_path": CELL_SRC,
        "cell_commit": CELL_COMMIT,
        "raw_metrics_path": METRICS,
        "primary_verdict_on_disk": "HARD_FAIL",
        "primary_verdict_disposition": "CONFOUNDED_INCONCLUSIVE (category c); NOT a proven negative; "
                                       "cert_increment_delta=0; no math-corpus atom filed for the primary",
        "composes_with_atoms": [math_atom["id"]],
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
        "atomized_by": "skunkworks_landed_VET_2026-07-04_v3b_nce_confound_and_tail_corruption",
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
    tag = "2026-07-04_v3b_nce_confound_and_tail_corruption"
    n_math = a5_append(MATH_ATOMS, math_atom)
    print(f"[atomize] math MM_STANDARD (single-seed) NCE-tail-corruption atom appended; math lines={n_math}")
    n_meta = a5_append(META_ATOMS, meta_atom)
    print(f"[atomize] meta MM_STANDARD META rule (compound-loss ablation completeness) appended; meta lines={n_meta}")
    ledger_append(math_atom, tag)
    ledger_append(meta_atom, tag)
    print("[atomize] DONE 2 atoms + 2 ledger entries; A5-gated (tmp+os.replace+verify-load+json-integrity); matching TS_ISO")
    print("[atomize] NET CERT DELTA: CG 0, MM +2 (math secondary MM_STANDARD single-seed, meta rule MM_STANDARD), HF 0")
    print("[atomize] PRIMARY (batch-ratio-match sweep) HARD_FAIL: CONFOUNDED_INCONCLUSIVE, cert_increment_delta=0, "
          "NOT filed as a proven negative")
