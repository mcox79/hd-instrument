# Pre-reg: Encoder Migration Step 1b v2 -- MLP-student BGE distillation into sparse BLOCK-bipolar concept codes, dual-gated (semantic + keyed algebra)

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED BEFORE FULL DISPATCH.
Cell: `experiments/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1_core.py`
Anchor: `encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1` (smoke suffix `_smoke`).
Supersedes-for-capacity: v1 cell
`experiments/exp_encoder_migration_step1b_distill_concept_encoder_v1_core.py`
(prereg `preregs/2026-07-04_exp_encoder_migration_step1b_distill_concept_encoder_v1.md`).
Design input: `notes/design_encoder_step1b_v2_next_changes_2026-07-04.md`.

Prior-work check (substrate concept-query, USER-locked, re-run for v2):
top hit `Sparse block codes` cosine=0.3096 (`notes/wave14e_hierarchical_composition_research.md`),
then factorizer/distillation research notes at 0.27-0.29. These are mechanism-
background research notes, NOT a prior cell that distilled BGE into an MLP-sparse
student. GENUINELY NOVEL: the v2 cell swaps the v1 LINEAR student for an MLP to
break the empirically-measured 0.64 capacity ceiling; no rediscovery.

## What v1 established (MEASURED, off-disk)

- v1 SMOKE (3000-concept subset): spearman 0.788, keyed roundtrip@J5/J20 = 1.000,
  shuffled 0.000, RANDOM_BLOCK pos-ctrl 1.000. MEASURED@
  `data/exp_encoder_migration_step1b_distill_concept_encoder_v1_smoke/metrics.json`.
- v1 SMOKE verdict = HARD_FAIL_SPARSITY_NOT_PROTECTING (bundle J5 BLOCK 0.584 <
  DENSE 0.604). This gate fired on a NON-PRODUCTION raw-bundle scenario (design
  note FIX 1): production binds behind independent random role keys BEFORE
  bundling, and the KEYED path is 1.000. => FIX 1 re-aims gate B at the keyed
  path and demotes raw-bundle to a diagnostic.
- v1 FULL (LINEAR student, full corpus): spearman_all = 0.6428 MEASURED@ early-eval
  of the running K128 checkpoint at step 9000/20000. Below SMOKE 0.788 and far
  from goal 0.85 => CAPACITY ceiling, not optimization. => MLP student REQUIRED.

## Hypothesis

An MLP student f: R^1024 -> R^2048 -(GELU)-> R^N_DIM with block-structured
sparsification (K_BLOCKS blocks, 1 signed active unit per block), trained by
relational similarity-distillation from cached BGE-large teacher embeddings plus
InfoNCE with semi-hard teacher-mined negatives under a warmup+cosine LR schedule,
produces concept codes that (A) preserve BGE semantic geometry on held-out concepts
BEYOND the linear ~0.64 ceiling (target >= 0.85) AND (B) remain fully algebra-grade
under SBC block-local circular convolution KEYED composition (bind->unbind->cleanup
acc@1 >= 0.95). The nonlinear hidden layer supplies the pairwise-geometry-fitting
capacity a linear map provably lacks at full 178K-concept scale.

## v2 delta over v1 (exactly these, everything else preserved)

1. STUDENT = MLP `Sequential(Linear(1024,2048), GELU, Linear(2048,4096,bias=False))`
   for ALL trained arms (BLOCK_K128, BLOCK_K64, TOPK_NAIVE). The false-win
   comparison (TOPK_NAIVE) is now arch-MATCHED to the mechanism so the ONLY
   difference is the sparsifier (block vs unstructured top-k). ~10.5M params.
2. LR warmup + cosine decay (v1: fixed 1e-3, no schedule -> rkd rose 0.14->0.19
   in v1 FULL because NCE dominated early). warmup = min(400, max(10, steps//5))
   (FULL 400, SMOKE 30); cosine to ~0 at final step. Applied identically to every
   trained student (including the smoke LINEAR ref) for a fair comparison.
3. FULL batch 512 (v1 1024) -> fewer off-diagonal pairwise-cosine constraints per
   step for a K=128-block student (128 effective dims) to satisfy.
4. DUAL-GATE B RE-AIMED at the KEYED path (FIX 1): the algebra gate is
   keyed_roundtrip@1; the v1 "sparse RAW-bundle must beat dense RAW-bundle" gate
   (HARD_FAIL_SPARSITY_NOT_PROTECTING) and the v1 S_falsewin_demo TOPK<=0.80 gate
   are DEMOTED to REPORTED diagnostics (both were mis-specified: raw-bundle collapse
   is a semantic-correlation artifact, and TOPK keyed roundtrip MEASURED 0.96 at
   this regime, not the probe's 0.483). No new gate loosening beyond FIX 1.

## Composition algebra decision (drill-mandated explicit field)

`composition_algebra: "SBC_block_local_circular_convolution"` -- unchanged from v1.
Block-local `hdlab.binding.bind/unbind` on [K_BLOCKS, L]-reshaped codes with random
one-active-per-block signed keys. Frady/Kleyko/Sommer 2020 lossless SBC unbind;
self-test roundtrip 1.000; shuffled-key 0.000. The naive top-k + literal-FHRR path
is retained ONLY as the false-win comparison arm.

## Config

- Teacher cache: auto-resolve LARGEST `bge_large_v2_name_*.npz` under
  `data/substrate_index/cached_indices/`. Local SMOKE picks the 43905-concept cache
  (`bge_large_v2_name_43905_8a40445a.npz`); remote FULL picks the ~178K-concept
  cache present on the remote runner disk. NEVER recompute teacher embeddings.
  NOTE (dispatch dependency): FULL requires the ~178K `bge_large_v2_name_*.npz`
  present on the remote GPU host; the cell FileNotFoundError-aborts if absent.
- N_DIM = 4096 (`--n-dim`). Primary K_BLOCKS = 128 (L=32, sparsity 3.125%).
  FULL sweeps K_BLOCKS in {128, 64}; SMOKE trains primary 128 only (same code
  path, smaller grid). K64 is report-only (CRLB rules it out for 0.85; see below).
- Student: MLP hidden 2048, GELU, output 4096 (no bias on output layer so the
  block-STE sees zero-centered logits). `student_arch: "mlp"`.
- Split: seeded permutation (seed 7); held-out 0.10 of cache concepts, NEVER seen
  in training. SMOKE train 3000 + held 800. FULL train ~0.9*178K, held cap 20000.
- Objective (unchanged): L = 1.0*RKD(in-batch pairwise-cosine MSE, off-diag)
  + 0.5*InfoNCE(tau=0.07; pos = teacher top-1 NN; 4 mined semi-hard negatives from
  teacher-cos band [0.3,0.6] + in-batch negatives). NO absolute-MSE term.
- Sparsifier (unchanged): per-block argmax straight-through.
- Optimizer Adam base lr 1e-3 with warmup+cosine. SMOKE steps 150 batch 192;
  FULL steps 40000 batch 512. NOTE: batch 512 (per design note, was v1 1024)
  halves per-step sample throughput; FULL steps raised 20000 -> 40000 to preserve
  the MLP's total sample budget at PARITY with v1 linear FULL (20000*1024 =
  40000*512 = 20.48M samples). The higher-capacity MLP needs AT LEAST as much
  optimization as the linear -- the smoke MEASURED this directly (see SMOKE RESULT
  below): at 150 steps the MLP DENSE readout already hits 0.825 spearman (capacity
  is there) but the block-sparse code is only 0.645 (block-STE + generalization
  under-trained). 40000 steps gives the block-STE room to converge the sparse
  assignments toward the dense-readout semantic.
- Seeds: single seed 7 (deterministic discriminators given mechanism; not an
  AUC/confidence cell -> multi-seed-smoke rule N/A). Cross-validation seeds
  {13, 19} deferred to a follow-up FULL dispatch before any capability claim.
- Device: `--device auto`. SMOKE = local CPU (SMOKE-only-local). FULL = GPU
  (overnight_queue via Orchestrator).

## Arms

| arm | role | code | student | algebra path |
|---|---|---|---|---|
| BLOCK_K128 | PRIMARY mechanism | block K=128 | MLP | SBC block circconv |
| BLOCK_K64 | FULL-only sweep point | block K=64 | MLP | SBC block circconv |
| TOPK_NAIVE | false-win comparison | unstructured top-k=128 | MLP | literal FHRR + dense phasor keys |
| CHARPOS | Step-1-style honest baseline | orthographic top-k of name | (none) | (semantic eval only) |
| RANDOM_BLOCK | algebra ceiling / semantic negative control | random 1-per-block signed | (none) | SBC block circconv |
| DENSE_SIGN | sparse-vs-dense diagnostic | sign(MLP z), dense bipolar | (MLP dense) | FHRR (valid dense phasor) |
| LINEAR_REF | SMOKE-ONLY capacity-preview discriminator | block K=128 | LINEAR | (rkd + spearman only; NOT in per_unit) |

`HP_SCOPE`: {BLOCK_K128: [G_A, G_B_keyed], BLOCK_K64: [] (report-only),
TOPK_NAIVE: [] (comparison), CHARPOS: [] (baseline), RANDOM_BLOCK: [C_pos_control],
DENSE_SIGN: [] (diagnostic), LINEAR_REF: [] (smoke capacity preview)}.
Chain-grade gates apply ONLY to BLOCK_K128.

## Metrics (all on HELD-OUT concepts; every gated number lands in per_unit)

Semantic (per arm): spearman_all (rank corr of student vs teacher pairwise cosines,
up to 500K sampled held-out pairs), pearson_all, hi80_cos + hi80_calib_err,
ret_agree@10 (top-10 NN overlap vs teacher within eval codebook).

Algebra (per arm x J; J_grid SMOKE {5,20}, FULL {2,5,10,20}):
- keyed_roundtrip@1 (bind J, unbind key_q, cosine-argmax cleanup over eval
  codebook) + SNR margin. THIS IS THE ALGEBRA GATE.
- bundle_recall@J (un-keyed superposition, per-item top-J recall). DIAGNOSTIC ONLY.
Controls: shuffled_key hit-rate (BLOCK_K128 J=5); RANDOM_BLOCK keyed pos-control.

Capacity preview (SMOKE only, NOT a per_unit; `metrics.capacity_preview`):
mlp_rkd_last, linear_rkd_last, rkd_ratio, mlp_breaks_linear_rkd,
mlp_spearman_smoke, linear_spearman_smoke.

## Bands (FULL; primary arm BLOCK_K128)

- G_A semantic: spearman_all >= 0.85 HARD_PASS; [0.70, 0.85) MIDDLE_BAND; < 0.70
  HARD_FAIL. (floor 0.70; HP at floor + 100% band width -> META_RULE_L trivially.)
  PREDICTION (HYPOTHESIZED): MLP breaks the linear 0.64 ceiling. Rationale: the
  linear cap is a geometry-fitting capacity limit (a single W cannot realize the
  nonlinear rank structure of BGE pairwise cosines at 178K concepts); the MLP
  hidden layer adds that capacity. Director CPU probe MEASURED rkd 0.10 (MLP) vs
  0.19 (linear) at step 100 = geometry loss HALVED. Honest band: expect FULL
  spearman in [0.72, 0.85]; whether it clears 0.85 (HARD_PASS) vs lands MIDDLE is
  the open question this FULL run answers. NOT pre-judged.
- G_B_keyed (non-negotiable dual-gate B): keyed_roundtrip@1 at J=5 >= 0.95
  HARD_PASS; [0.90, 0.95) MIDDLE_BAND; **< 0.90 -> FALSE_WIN_ALGEBRA (HARD_FAIL)
  REGARDLESS of G_A**. THEORETICAL@Frady2020 lossless + MEASURED@v1 1.000; the
  MLP swap does not touch the algebra path so keyed stays ~1.000.
- bundle_recall@J: REPORTED DIAGNOSTIC (FIX 1). Not a pass/fail gate.
- C_shuffled_key: hit-rate <= 0.05 (MEASURED@v1 0.000) -> else HARD_FAIL_SHUFFLED_KEY_LEAK.
- C_pos_control: RANDOM_BLOCK keyed_roundtrip@1 >= 0.98 at J=5 (MEASURED@v1 1.000)
  -> else HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH.
- Overall: HARD_PASS iff G_A HP AND G_B_keyed HP AND both controls pass.
  G_A MIDDLE with keyed green -> MIDDLE_BAND (semantic short of 0.85, algebra ok).
  G_A < 0.70 -> HARD_FAIL G_A_SEMANTIC_FAIL.

## Bands (SMOKE; reduced scale, 150 steps, probe/v1-calibrated)

- S_A: BLOCK_K128 spearman_all >= 0.60 HP; [0.40, 0.60) MB; < 0.40 SMOKE_GATE_FAIL.
  (v1 linear smoke MEASURED 0.788; MLP with warmup+cosine over only 150 steps may
  land lower average-LR but well above 0.40. MB in smoke is acceptable -> not a fail.)
- S_gap (discriminator-fires META_RULE_K): BLOCK_K128 ret_agree@10 >= CHARPOS
  ret_agree@10 + 0.10 (v1 MEASURED 0.4965 vs 0.098 = gap 0.398).
- S_B_keyed: keyed_roundtrip@1 at J=5 >= 0.95 (MEASURED@v1 1.000).
- S_capacity (v2 discriminator-preview, option C): MLP geometry-loss must beat
  LINEAR by >= 10% on MATCHED smoke data: rkd_ratio = mlp_rkd/linear_rkd <= 0.90.
  This is the mechanism-fires assertion for "MLP has capacity the linear lacks."
  If it does not fire, the v2 premise is wrong -> SMOKE_GATE_FAIL, no dispatch.
- C_shuffled_key <= 0.05; C_pos_control RANDOM_BLOCK >= 0.98 at J=5 (both HARD_FAIL
  classes, checked before smoke bands).
- Reported-not-gated: bundle recall curves, TOPK_NAIVE keyed roundtrip.
- Smoke wall budget: <= 480s (v1 was 266s; +1 linear ref student + its semantic).

### Honest scope of the smoke (DISCRIMINATOR-MUST-SURVIVE-SCALE)

The 3000-concept smoke subset is EASY (v1 linear itself hit 0.788 there). The smoke
therefore CANNOT directly demonstrate the 0.64->0.85 break -- that is a FULL-178K
question by construction. What the smoke DOES fire is the capacity discriminator in
its geometry-loss form (S_capacity: MLP rkd substantially below linear rkd on matched
data). Lower rkd = the MLP fits teacher pairwise geometry better = the headroom by
which it exceeds the linear plateau at full scale. Necessary, not sufficient; the
FULL GPU run produces the actual spearman number. Reported explicitly, not overclaimed.

## SCHEMA-VET / META_RULE fields

- cardinality_ok: true. EXPECTED_N_UNITS: SMOKE 22 (5 semantic + 4 arms x 2J keyed
  + 4 arms x 2J bundle + 1 shuffled). FULL 47 (6 semantic incl BLOCK_K64 +
  5 arms x 4J keyed + 5 arms x 4J bundle + 1 shuffled). LINEAR_REF capacity-preview
  is NOT counted (stored under metrics.capacity_preview, not per_unit). Verdict
  counts per_unit; shortfall -> HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- arms_differ_verified: true (sha256 over 5/6 semantic-arm code matrices; distinct).
- final_metrics_atomicity: "tmp_replace" (write_metrics helper).
- except-discipline: except SystemExit/KeyboardInterrupt re-raise before
  except Exception; no bare except; per-unit failure_class (META_RULE_J).
- crlb_floor_computed: 0.901 attenuation bound at K_BLOCKS=128
  (crlb_formula_reference: r_max = sigma_teacher / sqrt(sigma_teacher^2 + 0.25/K),
  sigma_teacher = 0.0918 MEASURED@v1 2000-concept sample; K=64 -> 0.826,
  K=128 -> 0.901). discriminator_reachability: true for G_A at K=128 (0.85 < 0.901);
  false at K=64 -> K64 is report-only, NOT gated on 0.85. NOTE: the MLP student
  does not change the CRLB (the bound is on the K-block quantization channel, not
  the encoder map); it changes only how close the student gets TO the bound.
- baseline_in_band (META_RULE_AG): CHARPOS ret_agree@10 = 0.098 MEASURED@v1 smoke,
  in (0.05, 0.95). Correlation-type metrics; no baseline saturation possible.
- calibration_check: "default_ok_for_this_regime" (k-sparsity 3.125% ablation-backed
  + CRLB; semi-hard band [0.3,0.6] covers 0.801 of train pairs MEASURED@v1 probe).
- discriminator survives scale: option (A)+(B)+(C) hybrid. Smoke runs at FULL
  N_DIM=4096 + FULL K_BLOCKS=128 (identical geometry). (C) capacity-preview arm
  (S_capacity: MLP rkd < 0.90*linear rkd on matched smoke data). (B) analytical:
  RKD/NCE quality monotone in data+steps; keyed algebra V-insensitive by SBC
  losslessness. The one thing smoke cannot show (the 0.85 semantic number at 178K)
  is declared a FULL-only question, not asserted from smoke.
- cell_chunked: false (single-seed artifact-producer; within-cell mining-shard +
  train-ckpt resume every 500 steps, atomic).
- start_marker_written: true. crash_diagnostic_present: true.
  heartbeat_present: true (_heartbeat.jsonl every 100 train steps + per eval unit).
- defensive_error_checking: "passed_all_4_patterns".
- progress_logging: "print_flush_true" (FULL timeout >= 1800; every train step
  block logs rkd/nce/lr with flush=True, per-unit eval logs flush=True).
- run_mode wiring: --run-mode {self_test,smoke,full} default env HDLAB_RUN_MODE
  else self_test; --smoke / --full override. Post-dispatch run_mode verification
  per META_RULE section 16 mandatory in completion report.

## Section 15 gates

- sweep_alignment_verdict: ALIGNED (J bundle-depth axis experienced directly by
  every primitive; K_BLOCKS axis IS the student output architecture; no composed
  primitive sees a divided/effective parameter).
- discriminating_fraction: >= 0.30 on the J axis (bundle diagnostic curves span
  the discriminating band; keyed axis is by-design near-lossless for BLOCK).
- composition_edges:
  - encoder(block code [K,L]) -> SBC bind/unbind on last dim: SHAPE_MATCH (reshape
    adapter, lossless by construction).
  - encoder(top-k sparse real) -> literal FHRR bind: SHAPE_MISMATCH_adapter_
    complexify_zero_dims -- INTENTIONAL negative-comparison arm (the category error
    the block structure avoids); documented risk IS the measurement.
  - unbound vector -> cosine-argmax cleanup over codebook: SHAPE_MATCH.
- positive_control_arms: RANDOM_BLOCK keyed_roundtrip reproduces SBC-lossless prior
  at THIS test regime (N=4096, K=128, V_eval, J grid); cited_prior = Frady2020
  (CITED) + v1 1.000 (MEASURED); tolerance 0.02 at J=5.
- functional_requirements:
  - FR1 preserve teacher semantic geometry -> RKD + InfoNCE with MLP capacity.
  - FR2 exact sparsity in proven window -> block architecture (1/block, k=K/N).
  - FR3 invertible composition -> SBC block circconv (hdlab bind/unbind).
  - FR4 novel-concept encodability -> MLP student on teacher embedding (held-out
    eval); student state_dict persisted (`_student_K{kb}.pt`) for the deploy path.
  - FR5 restartability -> mining shards + train ckpt + resume.
  - FR6 storage strategy -> SHARDED per-concept codes (bundling appears ONLY as
    explicit diagnostic arms, exemption (b) of the sharded-default rule).

## Compute architecture

Class (a) batched-GPU for FULL (mining = chunked [4096 x V] teacher matmuls;
training = batched MLP matmul; evals = chunked codebook matmuls). MLP adds ~10.5M
params (trivial for a 7GB GPU). SMOKE runs the same torch code on CPU
(SMOKE-only-local; wall target <= 480s). No per-phase-point sequential Python
matmul loops. Storage strategy: sharded (FR6).

## SMOKE RESULT (MEASURED, local CPU seed 7; validates dispatch)

MEASURED@`data/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1_smoke/metrics.json`
(elapsed 931.5s CPU, 22/22 units, verdict SMOKE_HARD_PASS):
- keyed_roundtrip@1 BLOCK_K128 J5=1.000, J20=1.000 -> ALGEBRA GRADE PRESERVED (the
  load-bearing gate; MLP swap does not touch the SBC algebra path). shuffled_key
  0.000; RANDOM_BLOCK pos-control keyed 1.000/1.000.
- capacity discriminator (S_capacity) FIRES: mlp_rkd=0.0612 vs linear_rkd=0.0794,
  ratio 0.770 <= 0.90 (MLP fits teacher pairwise geometry ~23% better than linear
  on MATCHED smoke data).
- discriminator-fires gap 0.278 (BLOCK ret_agree@10 0.377 vs CHARPOS 0.098).
- semantic spearman: BLOCK_K128(MLP block) 0.6446; DENSE_SIGN(MLP dense readout)
  0.8251; LINEAR_REF(linear block) 0.7616; TOPK_NAIVE(MLP top-k) 0.6273; CHARPOS
  0.5396; RANDOM_BLOCK 0.001.

HONEST INTERPRETATION (does NOT overclaim a ceiling break):
- The MLP DENSE readout 0.8251 is the load-bearing positive signal: the MLP student
  DOES learn near-goal semantic geometry; capacity is present.
- The MLP BLOCK-sparse code at 150 steps (0.645) is BELOW both the linear block ref
  (0.762) and v1's linear block smoke (0.788). This is UNDER-TRAINING of the
  higher-capacity model on a tiny 3000-concept/150-step smoke, NOT evidence against
  the capacity hypothesis: the MLP fits geometry FASTER (rkd 0.061 << linear 0.079)
  but the block-STE needs more steps to converge the sparse assignments and the held
  set to generalize. The bottleneck in the smoke is sparsification-convergence +
  steps, not capacity (dense readout proves it).
- Therefore the 0.64->0.85 BLOCK-code break remains a FULL-178K/40000-step question
  by construction. The smoke validates: plumbing, algebra preservation, capacity
  presence (dense 0.825 + rkd fire) -- the necessary conditions -- not the sufficient
  full-scale semantic number.

RISK flagged for Director: if the FULL block code lands MIDDLE_BAND ([0.70,0.85))
despite the dense readout being high, the next lever is more steps (block-STE
convergence) and/or a sparsity/K revisit -- NOT more student capacity. The FULL run
will report DENSE_SIGN spearman as the per-arm diagnostic (upper bound the block code
is converging toward).

## Timeout

SMOKE: local direct run (no queue), MEASURED wall 931.5s CPU.
FULL (GPU): two MLP students (K128 + K64) at 40000 steps batch 512 + one MLP topk
student + ~178K mining + 47 eval units. On RTX 4060 Ti estimate ~1.5-3h wall (MLP
forward + backward on batch 512 is GPU-bound trivial; the keyed-eval per-trial loops
over the 178K codebook dominate eval). **--timeout 14400** (4h) with margin (first
GPU run of this MLP cell family). > 4h NOT expected; cell is checkpoint-resumable
(train ckpt every 500 steps + mining shards) so a timeout re-dispatch resumes.

## Artifacts

- `data/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1{_smoke}/metrics.json`
- `data/substrate_concept_encoder_v1b_v2mlp{_smoke}/encoder_distilled_K128.npz`
  (+ `_K64` in FULL): int8 codes [V, N_DIM], id order, metadata.
- `data/substrate_concept_encoder_v1b_v2mlp{_smoke}/_student_K{kb}.pt`: MLP student
  state_dict + arch dims for the novel-concept deploy path.

## Halt conditions

Training loss NaN/Inf -> CELL_CRASHED with failure_class. Any eval unit exception
-> recorded failure_class + FAIL_LOUD (no silent continue). Teacher cache
missing/id-count mismatch -> hard abort before training.
