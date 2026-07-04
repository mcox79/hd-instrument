# Pre-reg: Encoder Migration Step 1b v3 -- GLOBAL (landmark) RKD objective; R1 rescue for the full-scale HARD_FAIL

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED BEFORE the intermediate-scale (mid) validation run. FULL is DEFERRED (not dispatched; gated on the mid recovery result + Director/USER decision).
Cell: `experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`
Anchor: `encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1` (mid suffix `_mid`, smoke suffix `_smoke`).
Supersedes-objective: v2 cell `experiments/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1_core.py` (v2 KEPT unchanged; v3 is a NEW cell).
Design input: `notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (R1 is the lead).

Prior-work check (substrate concept-query, USER-locked): query "global landmark anchor
relational distillation objective encoder pairwise geometry scale" returns ONLY WordNet
lexical atoms (top: entity 'distillation' cosine=0.3662; 'relational' 0.3486) -- i.e. the
"substrate knows nothing" dictionary baseline, NOT a prior arc CELL. No prior experiment
cell on a global/landmark RKD objective exists at cosine>0.30. GENUINELY NOVEL: v3 swaps
the v2 in-batch [batch x batch] RKD target for a [batch x L] landmark-frame target; no
rediscovery. Prior-work check: [NONE at cosine>0.30 among arc cells; only WordNet lexical].

## Confirmed diagnosis (do NOT re-litigate; from the rescue note)

FULL HARD_FAIL is REAL and FAIR (eval verified; teacher normalized local AND remote -> no
bug). Root cause = the OBJECTIVE does not scale:
- v2 RKD target = in-batch `x@x.T` (512x512) over 160k+ concepts. Pairwise coverage
  batch/V drops 6.4% (smoke 3k) -> 0.32% (full 178k), a 20x drop; graded near-neighbor
  pairs co-occur in a batch ~1e-5/step -> graded geometry NEVER supervised at scale.
- DENSE_SIGN (NO sparsifier) ALSO collapsed 0.825(3k) -> 0.368(178k) MEASURED@diagnosis.
  So the failure is the LEARNED MAP / OBJECTIVE, not the block-STE sparsifier.
- Not under-training: rkd converged (lr fully decayed ~1e-12), 13x more teacher-draws/
  concept at full yet WORSE held generalization.

## Hypothesis

Supervising graded geometry against a FIXED global landmark frame (independent of random
in-batch co-occurrence) recovers the semantic geometry at scale. Specifically: with the
GLOBAL LANDMARK RKD objective, the DENSE_SIGN readout at INTERMEDIATE scale (~40k concepts)
RECOVERS to ~0.80 spearman, whereas the matched-config in-batch objective plateaus at the
scale-limited ~0.37-0.64 (MEASURED@diagnosis). If DENSE recovers -> the objective fix works
and the sparse BLOCK code re-check + FULL are justified. If DENSE does NOT recover -> the
global objective is insufficient; report and do NOT proceed to FULL.

## The objective change (EXACTLY this; everything else = v2, preserved)

Per training step (GLOBAL objective):
- Landmark/anchor frame: a FIXED set of L train-concept indices (random anchor frame;
  `land_idx = randperm(n_tr)[:L]`, seeded). L = 4096 at mid (8192 full; 1024 smoke).
- Frame codes `frame_n` [L, N_DIM]: the student's OWN landmark codes (hard block-STE),
  re-encoded no_grad + DETACHED every REFRESH steps (mid 50) and cached; a cheap
  projection basis, at most REFRESH steps stale (negligible vs total steps).
- Teacher target `Tland = Xbatch @ Xland.T` [B, L] (both teacher rows unit-norm -> cosine).
- `l_rkd = mean( (s_n @ frame_n.T - Tland)^2 )`. Every batch concept supervised against L
  global coordinates every step. THEORETICAL@ Johnson-Lindenstrauss: matching each concept's
  L>=~N_DIM landmark-cosine-profile to the teacher's reproduces the teacher pairwise geometry,
  so near-neighbours (near-identical profiles) are transitively pulled together WITHOUT needing
  to co-occur in a batch.
- InfoNCE term, MLP student, block-STE, SBC algebra, warmup+cosine LR = UNCHANGED from v2.
- `--objective in_batch` reproduces the v2 objective VERBATIM (the controlled baseline).
- Optional composed lever `--cluster-frac` (neighbour-clustered batches from the existing
  semi-hard mining) is available but DEFAULT 0.0 so the mid validation isolates the
  landmark-RKD effect cleanly.

## Validation design (the load-bearing deliverable): run_mode = mid

Trains BOTH objectives at MATCHED config on the local 43905-concept cache
(`bge_large_v2_name_43905_8a40445a.npz`; held 0.10 cap 5000 -> train ~39515, held ~4390 =
~40k, the INTERMEDIATE scale between the 3k smoke and 178k full). Single seed 7.
MID_STEPS 1800, batch 512, L 4096, refresh 50. DENSE-spearman trajectory logged every 300
steps (shows the recovery curve + whether DENSE plateaued by step 1800). Reports per arm:
GLOBAL_DENSE, INBATCH_DENSE (the recovery discriminator), GLOBAL_BLOCK_K128,
INBATCH_BLOCK_K128, CHARPOS, RANDOM_BLOCK spearman; keyed J5 + shuffled + RANDOM_BLOCK
pos-control (algebra integrity, untouched by the objective).

## Bands (mid recovery discriminator; primary metric = DENSE_SIGN spearman)

- global_dense = GLOBAL_DENSE spearman_all; inbatch_dense = INBATCH_DENSE spearman_all;
  delta = global_dense - inbatch_dense.
- **RECOVERED (HARD_PASS)**: global_dense >= 0.75 AND delta >= 0.15. -> objective fix works;
  clears the bar to justify the sparse re-check + a GPU FULL (Director/USER decision).
- **PARTIAL (MIDDLE_BAND)**: global_dense in [0.64, 0.75) AND delta >= 0.05. -> DENSE improved
  but short of the ~0.80 target; marginal, USER/Director call (more steps / K revisit).
- **NOT_RECOVERED (HARD_FAIL)**: else. -> global objective insufficient; do NOT proceed to FULL.
- Integrity controls (checked first; algebra untouched by objective): RANDOM_BLOCK keyed
  J5 >= 0.98 (else HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH); shuffled_key GLOBAL_BLOCK
  acc<=0.05 & hit_any<=0.10 (else HARD_FAIL_SHUFFLED_KEY_LEAK).

PREDICTIONS (tagged):
- in-batch DENSE at ~40k: [0.37, 0.64] MEASURED@`notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (diagnosis, cited off-disk).
- global DENSE at ~40k: [0.75, 0.83] HYPOTHESIZED@this prereg (DENSE geometry forms fast --
  v2 3k-smoke DENSE=0.8251 MEASURED@`data/exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1_smoke/metrics.json`;
  the global frame supplies graded supervision every step at scale). recovery_delta >= 0.15 HYPOTHESIZED.
- global BLOCK at ~40k: reported but NOT the primary gate. May still lag DENSE (block-STE
  convergence needs more steps; v2 3k-smoke DENSE 0.825 vs BLOCK 0.645). The sparse re-check
  (R2 brain dense-first-then-sparsify) is a SEPARATE follow-up if DENSE recovers.

## SCHEMA-VET / META_RULE fields

- cardinality_ok: true. EXPECTED_N_UNITS_MID = 9 (6 semantic {GLOBAL_BLOCK, GLOBAL_DENSE,
  INBATCH_BLOCK, INBATCH_DENSE, RANDOM_BLOCK, CHARPOS} + keyed GLOBAL_BLOCK J5 + keyed
  RANDOM_BLOCK J5 pos-ctrl + shuffled GLOBAL_BLOCK J5). Verdict counts per_unit; shortfall
  -> HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- arms_differ_verified: true (sha256 over the 5 code matrices + CHARPOS; MEASURED distinct in
  the tiny-scale dry-run).
- final_metrics_atomicity: "tmp_replace" (write_metrics helper; atomic os.replace).
- except-discipline: except SystemExit/KeyboardInterrupt re-raise before except Exception;
  no bare except; no `except BaseException` (grep gate PASSED); per-unit failure_class (META_RULE_J).
- crlb_floor_computed: 0.901 attenuation bound at K_BLOCKS=128 (crlb_formula_reference:
  r_max = sigma_teacher / sqrt(sigma_teacher^2 + 0.25/K), K=128 -> 0.901) THEORETICAL@v2 prereg.
  The objective does NOT change the CRLB (bound is on the K-block quantization channel). The
  mid PRIMARY metric is the DENSE readout (no block quantization) so CRLB does not gate it;
  the RECOVERED bar (0.75) is on the achievable side for DENSE. discriminator_reachability: true.
- baseline_in_band (META_RULE_AG): the discriminator is a RECOVERY DELTA between two matched
  objectives, NOT an absolute baseline. The dry-run confirms the discriminator does NOT
  trivially fire at small scale (1742 concepts: global DENSE 0.8425 vs in-batch 0.862,
  delta=-0.02 -> correctly NOT_RECOVERED because small scale is NOT the failure regime).
  It fires ONLY at the scale where in-batch collapses. RANDOM_BLOCK spearman ~0.00 (floor
  control), CHARPOS ~0.54-0.60 (baseline) both in (0.05, 0.95) at the dry-run.
- calibration_check: "default_ok_for_this_regime" (semi-hard band [0.3,0.6], K-sparsity, LR
  schedule all inherited from validated v2; the ONLY change is the RKD target matrix).
- discriminator survives scale: this cell IS the discriminator-survives-scale test -- the
  recovery delta is measured AT the intermediate scale where the in-batch objective is
  KNOWN to fail (not deferred to FULL). The dry-run showed the discriminator is not vacuous.
- cell_chunked: false (mid trains two objectives sequentially in one process; each is
  train-ckpt resumable every 300 steps + mining-shard resumable; a timeout re-dispatch resumes).
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED +
  traceback, atomic). heartbeat_present: true (_heartbeat.jsonl every 100 train steps + per eval unit).
- defensive_error_checking: "passed_all_4_patterns".
- progress_logging: "print_flush_true" (every train step block + DENSE-traj + per-unit eval
  logs flush=True; sys.stdout line_buffered at main() entry).
- run_mode wiring: --run-mode {self_test,smoke,mid,full}; --mid override; --objective
  {global,in_batch} for smoke/full (mid runs BOTH by design). Post-run run_mode is recorded
  in metrics (run_mode:"mid").

## Section 15 gates

- sweep_alignment_verdict: ALIGNED (no swept parameter has a divided/effective value; the
  landmark count L is a fixed design constant, not a discriminator axis).
- discriminating_fraction: N/A (recovery discriminator is a two-point objective comparison,
  not a sweep); the dry-run confirms the two objectives are distinguishable in principle and
  the discriminator is NOT saturated at small scale.
- composition_edges: encoder(block code [K,L]) -> SBC bind/unbind: SHAPE_MATCH (unchanged
  from v2; algebra path untouched by the objective).
- positive_control_arms: RANDOM_BLOCK keyed_roundtrip reproduces SBC-lossless prior at THIS
  regime (tol 0.02 at J5); the in_batch objective arm reproduces the v2 objective verbatim
  (positive control that the baseline is the SAME code path as v2, isolating the delta).
- functional_requirements: FR1 preserve teacher semantic geometry AT SCALE -> global landmark
  RKD (the fix). FR2 exact sparsity -> block architecture (unchanged). FR3 invertible
  composition -> SBC (unchanged). FR4 novel-concept encodability -> MLP student (unchanged).
  FR5 restartability -> mining shards + train ckpt. FR6 storage: sharded per-concept codes.

## Compute architecture

Class (c) mixed with justification. The mid VALIDATION runs on LOCAL CPU (SMOKE-only-local
rule; the recovery diagnostic must run locally before any GPU spend). Per-batch work is
batched torch matmul (MLP fwd/bwd, [batch x L] and [batch x batch] cosine, chunked mining) --
NOT per-phase-point Python loops. Sequential over the two objectives (global then in_batch)
by design (controlled comparison in one metrics.json). Local-CPU is justified because this
is the pre-GPU validation gate, wall ~1.5-2.5h at 1800 steps x 2 students on 12 threads,
checkpoint-resumable. The FULL run (DEFERRED) is class (a) batched-GPU (overnight_queue via
Orchestrator) and is NOT dispatched by this prereg. Storage strategy: sharded (FR6).

## Timeout

MID: local direct run (no queue), estimated wall ~1.5-2.5h CPU (2 x 1800-step MLP students
at batch 512 + ~40k mining + 9 eval units). Checkpoint-resumable (train ckpt every 300 steps
+ mining shards) so an interruption resumes. FULL (DEFERRED): would be `--timeout 14400` (4h)
on GPU per the v2 estimate, but is NOT dispatched here -- gated on the mid recovery verdict.

## Artifacts

- `data/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_mid/metrics.json`
  (verdict + recovery{} block + per_unit + train_diag with DENSE trajectories).
- `data/substrate_concept_encoder_v1b_v3global_mid/_ckpt_block_{global,in_batch}.pt` (resumable),
  `_mine_shards/` (mining shards).

## Halt conditions

Training loss NaN/Inf -> CELL_CRASHED with failure_class=NAN_LOSS. Any eval unit exception
-> recorded failure_class + FAIL_LOUD (no silent continue). Teacher cache missing/id-count
mismatch -> hard abort before training. Landmark selection empty for global objective ->
ValueError before training.

## Decision routing (post-mid)

- RECOVERED -> hand back to Director/USER: objective fix validated; next = (a) sparse BLOCK
  re-check (does BLOCK follow DENSE with more block-STE steps?) + (b) a single GPU FULL of the
  global objective at 178k (Director routes to Orchestrator; ONCE-per-stage GPU rule). NOT
  auto-dispatched by exp_dev.
- PARTIAL/NOT_RECOVERED -> report the number; do NOT dispatch FULL; route back to Research for
  the next lever (R2/R3/R4 or landmark-count / k-means-frame / step-budget revisit).
