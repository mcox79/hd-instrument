# Research drill: how to TRAIN a graded global-top-k / Sparse-GSBC code to cash its ceiling

Date: 2026-07-04
Type: notes memo (de-risk drill, NO dispatch)
Owner: Director (research lane)
Scope: the #1 open risk on the primary encoder path after the 8x-drill convergence
(block-argmax -> graded global-top-k / Sparse-GSBC, ref arXiv:2303.13957 Frady/Kleyko/Rahimi).

## The question (one line)
The format switch is settled and zero-training already beats block-argmax by +0.086-0.111 ret_agree10
with algebra intact (keyed@J5=1.0). The OPEN RISK: training must cash the code's much higher CEILING
(~0.7-0.9 vs block-argmax 0.43) -- our block-argmax training reached only 47% of its 0.43 ceiling
because per-block-argmax is a nasty gradient surface. So: HOW do we TRAIN the graded code well?

## Prior-work check (substrate KB + notes arc)
- Substrate concept-query `"graded global top-k sparse block code GSBC training gradient estimator"`:
  max cosine 0.3213 (generic WordNet "graded"/"gradient"; nearest note = `wave14e_hierarchical_composition_research.md`
  "Sparse block codes" 0.2861). => NO substrate atom on a graded-GSBC TRAINING recipe. Novel territory.
- Direct prior arc (2026-07-04, this concept): the 8x deep drill that CHOSE this code
  (`research_drill_brain_5x_angle{1,2,3}_*`, `research_drill_coding_theory_sparse_retrieval_global_wta_flyhash_5x`,
  `research_drill_magnitude_preserving_sparse_code_5x_angle3`, `scour_prior_work_sparse_retrieval_at_2pct_inventory`);
  the lever ladder (`research_drill_sparse_distill_fidelity_lever_ladder_2026-07-04`, ranked B=discrete-gradient
  fidelity > A=capacity); the calibration-recovery drill (`research_5x_drill_regime_switch_calibration_recovery_2026-07-04`,
  A2 isotonic + absolute-cosine anchor); `research_drill_encoder_gradient_feedback_2x_2026-06-07`;
  the cardinality drill (OPQ + rank-aware-loss levers).
- This memo is the FOLLOW-THROUGH: the 8x drill settled WHICH code; this settles HOW to train it.
  It does NOT re-litigate the format choice.

## Load-bearing operational facts (verified on disk, this arc -- these dominate the recipe)
1. `train_loss_floored=True` on EVERY block-argmax arm incl the HARD_STE control (objective is FIT, retrieval
   still low). => capacity/objective-fit is NOT the bottleneck. The gap is the gradient<->quantization interaction.
   (Kills lever A; confirms lever B = discrete-gradient fidelity.)
2. The annealed-STE run (`exp_encoder_v6_annealed_ste_fidelity_k128_v1`: per-block softmax(|z|/tau)*sign,
   tau cosine-annealed 2.0->0.1, + 0.5*soft/hard-consistency MSE) UNLOCKED rich geometry: dense readout
   0.169 -> 0.65 (both seeds, FINAL-step > bestval so NOT inflation). The ESTIMATOR demonstrably learns the
   geometry. It FAILED only because block-argmax could not CARRY the annealed dense-shaped geometry into the
   deployed sparse code (delta_B = -0.16/-0.18 on the hard code; k-WTA rank-cap / dense->block bandwidth).
   => The graded global-top-k code REMOVES exactly that carrier bottleneck.
3. Calibration-collapse is the RECURRING FALSE-PASS family. OPQ (calib_err 0.006->0.47, hi80 0.83->0.37),
   KL-RANK (calib_err 0.006->0.096), and the annealed-STE dense-0.65 itself (calib_err 0.37, hi80 0.48) ALL
   lifted ret_agree10 by OVERSHOOTING teacher cosine while destroying coarse-cosine geometry (goal #2).
   META RULE (atomized): gate JOINTLY on ret_agree10 AND calib_err AND hi80_cos. A rank-lift with calibration-
   collapse is a FALSE PASS, not a win.
4. Format probe (zero-training, our data): GLOBAL_TOPK_GRADED +0.086, EXPAND2x+GLOBAL_TOPK +0.111,
   GLOBAL_TOPK_SIGN +0.058; keyed@J5=1.0000 despite 36.5% empty blocks (sign of GLOBAL survivors preserves
   SBC bind/unbind). Algebra is FORMAT-preserved, zero-training -- not a training obligation.
5. IBM/Frady (arXiv:2303.13957) confirmed: GSBC codevectors are FIXED; only a net mapping INTO the fixed code
   is trained, with a novel loss for factorizer-DECODABILITY (classification) -- NOT distillation-from-a-dense-
   teacher for retrieval geometry+calibration. So a LEARNED graded GSBC by distillation is uncharted; the
   precedent only proves a net CAN be trained to emit into a fixed SBC format.

## THE RECOMMENDED TRAINING RECIPE (ordered by leverage)

### Lever 1 (HIGHEST -- the enabling gradient fix): annealed SOFT GLOBAL-top-k estimator, straight-through to the hard graded global-top-k
- Forward (train): a GLOBAL (whole-vector, not per-block) soft-graded-sparse projection. PRIMARY = **entmax**
  (deep-spin; alpha in [1.5, 2]=sparsemax) -- it emits GRADED sparse survivors with an EXACT differentiable
  Jacobian on the support (no STE bias), and interpolates softmax<->sparsemax so we can ANNEAL soft->hard.
  Keep magnitudes (graded) for retrieval; sign of survivors carries algebra.
- Eval (deploy): the EXACT hard graded global-top-k (fixed k). entmax's support is threshold/scale-driven
  (not exact-k), so ALIGN train-op to eval-op with a **soft/hard consistency MSE to the detached hard code**
  (the exact term that already worked in v6) and anneal alpha/temperature soft->hard over training so the
  surrogate converges to the hard operator. EVAL ALWAYS ON THE HARD CODE (no train/eval cheating).
- If entmax's data-dependent sparsity drifts too far from the 2% target: fall to an exact-k
  **perturbed-top-k** (Berthet/Cordonnier perturbed optimizers) or **OT/Sinkhorn soft-top-k** (Xie et al.) --
  both enforce sum-to-k with dense gradients (more expensive; Sinkhorn iters).
- WHY #1: `train_loss_floored=True` rules out capacity/loss-fit and points squarely at the gradient<->
  quantization interaction; GLOBAL selection removes the per-block-boundary non-Lipschitz chaos that starved
  the argmax gradient; graded survivors keep the magnitude gradient (identity/entmax-Jacobian on support)
  instead of binarizing; and this is the SAME annealed estimator that ALREADY unlocked 0.65 dense geometry --
  the new code is simply a carrier that can keep it. This is re-using a PROVEN estimator on a code that can
  finally hold its output.

### Lever 2 (CO-CRITICAL -- the guard against the recurring false-pass): joint objective = graded-RKD + listwise-rank + ABSOLUTE-COSINE ANCHOR
- (a) RKD/cosine distillation on the GRADED readout (geometry backbone; keep).
- (b) ADD a LISTWISE ranking term on the top-K teacher-neighborhood -- LambdaLoss / NeuralNDCG / a soft-rank
  via differentiable sort -- to DIRECTLY target ret_agree10 (the goal metric is top-10 agreement, a listwise
  quantity). KL-RANK failed on block-argmax (+0.01) but that was CONFOUNDED: block-argmax cannot express
  graded rank. On the graded code a listwise loss finally has a code that can carry ranking.
- (c) ADD the ABSOLUTE-COSINE ANCHOR term (|cos_student - cos_teacher| on ABSOLUTE values; from the
  calibration-recovery drill) -- MANDATORY. A scale-invariant rank loss will inflate all similarities and
  reproduce the OPQ/KL/annealed-dense calibration-collapse signature. The anchor pins absolute cosine so the
  rank term cannot buy ret by overshooting. This mirrors documented ranking-similarity-regularization +
  calibration practice (RankSim; calibrated-similarity work): preserve ORDER without destroying ABSOLUTE
  similarity. The objective must mirror the JOINT gate (ret AND calib AND hi80).

### Lever 3 (schedule): anneal soft->hard; long cosine LR; weight EMA; HOLD schedule constant vs the estimator ablation
- alpha/temperature cosine-annealed soft->hard; longer cosine LR schedule; EMA of student weights.
- Keep the schedule FIXED across arms so Lever 1 is not confounded (as we did in v6). The single critical
  new hyperparameter is the ANCHOR WEIGHT (Lever 2c): it trades rank-spread vs calibration -> a small sweep
  is the one tuning that matters.

### Lever 4 (binding-aware training): DO NOT add a binding loss by default; HARD-GATE keyed@J5 instead
- Algebra is FORMAT-preserved zero-training (fact 4). So the objective stays CLEAN: no explicit bind/unbind
  term initially. Instead make keyed@J5 a HARD EVAL GATE + FALSE_WIN guard (ret AND calib AND algebra jointly,
  as the v6 iteration did). Add a cheap bind/unbind roundtrip regularizer ONLY if the soft relaxation is
  empirically found to drift the survivor SIGN structure. Rationale: a soft relaxation COULD scramble signs,
  so gate hard -- but don't pre-pay for insurance the format may not need.

## THE #1 RISK (called out)
CALIBRATION-COLLAPSE FALSE-PASS. Every ranking/geometry lever tried so far (OPQ, KL-RANK, annealed-dense)
lifted ret_agree10 by OVERSHOOTING teacher cosine and wrecking hi80_cos/calib_err. The absolute-cosine anchor
(Lever 2c) is the DESIGNED mitigation but it is UNPROVEN at closing the gap WITHOUT capping the rank gain --
the anchor weight trades rank-spread against calibration and may cap trained ret below 0.35 even though the
CODE ceiling is 0.7-0.9. Secondary risk: no published learned-GSBC-by-distillation recipe (IBM uses FIXED
codebooks + trains only a mapping-into-code for factorizer-decodability) -> the optimization landscape for a
learned graded GSBC is uncharted. Both are MITIGATED (not removed) by: zero-training already +0.086-0.111 with
the format; the annealed estimator already learning 0.65 geometry; and the IBM precedent that a net CAN be
trained to emit into a fixed SBC format.

## #1 single highest-leverage choice
Lever 1 (annealed soft GLOBAL-top-k estimator, straight-through to hard graded top-k) -- BUT it MUST ship
WITH Lever 2c (absolute-cosine anchor) or it reproduces the calibration-collapse false-pass the SAME estimator
already produced at dense-0.65. Treat 1+2c as an inseparable pair.

## De-risked probe design (for exp_dev when authorized -- NOT dispatched here)
Bit-paired nested ablation at the 2% code, 2 seeds, schedule held constant:
- ARM0 HARD_GLOBAL_TOPK (STE, no anneal) = positive control (should ~match the zero-training format lift).
- ARM1 +annealed soft-global-top-k (entmax) + soft/hard consistency  [Lever 1].
- ARM2 = ARM1 + listwise-rank + absolute-cosine anchor  [Lever 1+2].
- ARM3 = ARM2 + EXPAND2x  [+A, secondary; the format probe's best zero-train arm].
- PRIMARY GATE = JOINT: ret_agree10 (>=0.35 HARD_PASS) AND calib_err (no regression vs v3e ~0.006) AND
  hi80_cos (hold ~0.83) AND keyed@J5 (=1.0 hard gate). Log train_loss_floored + cons_last for free diagnostics.
  Report FINAL-step (not best-ckpt), disjoint VAL/TEST, step-0 excluded, determinism pinned.

## P_deflated that training cashes the ceiling to clear 0.35
**P_deflated ~= 0.44.** Reasoning (symmetric): UP-side -- the actual root cause (the code) is now fixed and
empirically de-risked zero-training (+0.086-0.111 -> ~0.31 before any training), the annealed estimator already
proved it can learn the geometry (0.65), and only ~+0.04-0.06 over the zero-training format number (or ~50% of
a 0.7 ceiling) clears 0.35 -- materially better than the ~0.25 that the block-argmax levers carried. DOWN-side --
calibration-collapse has killed 3/3 prior ranking levers and the anchor is unproven at closing the gap without
capping ret; and a learned graded GSBC by distillation is a novel synthesis with no published recipe (novel-
synthesis cap 0.50; lit-scan calibration penalty 0.15-0.25). Net: above the old 0.25, below the 0.50 novelty
cap, held down by the persistent calibration trap -> 0.44.

## Sources (generic lit-scan)
- Differentiable/soft top-k: Berthet et al. perturbed optimizers; Cordonnier et al. differentiable patch
  selection; Xie et al. differentiable top-k with optimal transport; Gumbel/relaxed subset sampling; STE +
  temperature-anneal + soft/hard-consistency mitigations. (arxiv 2206.07290; semanticscholar Xie-Dai;
  emergentmind differentiable-top-k-estimator.)
- entmax/sparsemax: Peters et al. Sparse Sequence-to-Sequence (1905.05702); Correia et al. Adaptively Sparse
  Transformers; deep-spin/entmax (exact differentiable Jacobian on support, alpha interpolation).
- Listwise ranking / distillation: LambdaLoss; ListMLE; SoftRank; NeuralNDCG (2102.07831, differentiable
  sort); ranking-order distillation teacher->student.
- Calibration/collapse: RankSim (Gong et al. 2022); calibrated-similarity work (2601.16907); cosine-similarity
  KD (CosPress).
- GSBC: Factorizers for Distributed Sparse Block Codes, arXiv:2303.13957 (FIXED codebooks; train net INTO code).
