# Pre-reg: Encoder Migration Step 1b v3c -- FULL-178k PAIRED tie-breaker (global-RKD-only vs in_batch-RKD-only, nce_weight=0, 2 seeds)

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED before dispatch.
Core cell: `experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py`
Per-seed wrappers (CHUNKED single-seed-per-cell): `experiments/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_7.py`, `experiments/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_13.py`
Anchors: `encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_seed7`, `..._seed13` (smoke suffix `_smoke` on each).
Parent cells: v3 (`..._v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`), v3b (`..._v3b_nce_ablation_dense_recovery_diagnostic_v1_core.py`, not imported -- single-hop dependency on v3 only).

## Prior-work check (substrate concept-query, USER-locked)

Query: "global landmark objective RKD-only NCE weight zero full scale distillation encoder paired
comparison" -> top hit cosine=0.291 ('destructive_distillation', WordNet), all others <=0.2754.
NONE at cosine>0.30 among arc cells (only WordNet/FrameNet lexical baseline). GENUINELY NOVEL: no
prior cell runs the paired global-RKD-only-vs-in_batch-RKD-only comparison with best-checkpoint
selection and a 2-seed replicate.

## Confirmed diagnosis chain (do not re-litigate)

- v2 FULL (in_batch, nce=0.5): DENSE_SIGN collapsed 0.825(3k)->0.368(178k)
  MEASURED@notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md.
- v3 mid (global vs in_batch, nce=0.5): HARD_FAIL, global DENSE 0.521 vs in_batch 0.568
  MEASURED@data/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_mid/metrics.json.
- v3b (batch-ratio-match sweep + NCE ablation): PRIMARY tier HARD_FAIL (confounded by nce=0.5 on
  both arms). SECONDARY tier (NCE ablation, GLOBAL objective only, decisive batch=128) DECISIVE:
  NCE_ZERO (nce=0.0) DENSE=0.7336 vs NCE_CURRENT (nce=0.5) DENSE=0.2687 (delta +0.465)
  MEASURED@data/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1/metrics.json:recovery.

## CACHE-RESOLUTION FINDING (VERIFIED@this prereg, 2026-07-04)

v3b's own "mid" run's landed metrics.json shows `device="cuda"`,
`teacher_cache="bge_large_v2_name_177899_54f7cf6a.npz"`, `teacher_n_concepts=177899`,
`n_train=172899` -- i.e. v3b's "mid" run auto-resolved (`v3._resolve_teacher_cache` picks the
LARGEST `bge_large_v2_name_*.npz` match) to the FULL 177899-concept cache on the machine it
actually ran on (remote GPU), NOT the intended ~40k-concept MID-scale cache its own docstring
narrative claims. So v3b's NCE_ZERO=0.7336 number IS ALREADY a genuine FULL-178k number at
batch=128/steps=1800, not a MID proxy. Locally, only up to a 43905-concept cache exists (verified
via `ls data/substrate_index/cached_indices/`); the 177899 cache exists ONLY on the remote host
(verified via `ssh marsh@home` PowerShell Test-Path: True, 1355319709 bytes, confirmed the largest
`bge_large_v2_name_1*` candidate present remotely, 2026-07-04). This cell PINS the exact filename
(`data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz`) as the production
default when `run_mode == "full"` (removing auto-resolve-largest ambiguity for a "definitive" run);
smoke mode always auto-resolves against whatever is largest LOCALLY (the 43905 cache), since the
pinned file does not exist on the local dev box.

## Coordinator course-correction (2026-07-04, mid-authoring)

The dispatching Director/coordinator, after an independent Skunkworks-VET read of the SAME cache-
resolution fact above, redirected this cell's scope from its initial batch=512/steps=40000/
single-seed plan to:

1. **THE TIE-BREAKER arm**: in_batch-RKD-only (nce=0) AT v3b's EXACT config (batch=128, steps=1800,
   same seed/split/mining convention as v3b) -- the one arm v3b never ran (its ablation arms were
   GLOBAL-objective-only). If in_batch-RKD-only ALSO reaches ~0.73 DENSE, the landmark/global
   objective adds nothing over the simpler in_batch baseline once NCE is off, and the landmark
   mechanism should be dropped as unnecessary complexity. If in_batch-RKD-only collapses (near-
   neighbor pairs still essentially never co-occur at a 128-batch over 172899 train concepts), the
   landmark objective is genuinely validated as the load-bearing fix.
2. **GLOBAL-RKD-only re-trained as the matched control** in the SAME process/split/mining (not
   merely cited from v3b), so its BLOCK (sparse) number is measured directly -- v3b computed BLOCK
   for its ablation arms into `per_unit` but never surfaced it into the headline `recovery{}` dict.
3. **BLOCK reported alongside DENSE for BOTH arms** -- BLOCK toward 0.85 is the real target metric
   (sparsity costs ~0.01-0.05 per the prior sparse-fidelity-frontier finding); DENSE alone is not
   the final answer.
4. **2 seeds** (seed=7 matching v3b for direct comparability; seed=13 the replicate) -- Skunkworks
   flagged v3b's nce=0 finding as single-seed (tiered MM_STANDARD, not yet chain-grade-promotable).
5. **Mid-training checkpoints SAVED** (every 300 steps, `CKPT_EVERY_STEPS_FULL`) and preserved
   (never deleted) so a later capacity/peak diagnostic can re-run the pre-decline analysis.

batch=128/steps=1800 MATCH v3b exactly (not this cell's superseded batch=512/steps=40000 plan) so
this is an apples-to-apples completion of v3b's ablation table at ALREADY-confirmed full scale --
also much cheaper ("GPU is fast": v3b's own 10-arm battery at this exact regime landed in 662.99s
wall-clock on cuda).

## Hypothesis (framed as the tie-breaker)

H1 (landmark objective is load-bearing): in_batch-RKD-only DENSE stays well below global-RKD-only's
~0.73 at this config (near-neighbor pairs still essentially never co-occur even at batch=128 over
172899 train concepts) -- the fixed landmark frame is genuinely necessary.
H2 (landmark objective adds nothing once NCE is off): in_batch-RKD-only ALSO reaches comparably
high DENSE (~0.65+) -- the earlier in-batch collapse was primarily an NCE-term pathology, not a
coverage-ratio pathology, and the simpler in_batch objective suffices once NCE is removed.

## Design (exactly what changes vs v3b; everything else preserved)

- objective in {global, in_batch}, BOTH at `nce_weight=0.0` (RKD-only for both -- the v3b-winning
  ablation config, applied here to in_batch for the FIRST time in this lineage).
- batch=128 (v3b's `DECISIVE_BATCH_MID`), steps=1800 (`v3.MID_STEPS`), landmarks=4096
  (`v3.N_LANDMARKS_MID`), refresh=50 (`v3.FRAME_REFRESH_MID`), teacher cache pinned to the
  177899-concept file (see cache-resolution finding).
- PAIRED trial discipline (USER-locked 2026-07-04): both arms share the SAME teacher split (seed
  permutation), SAME mining shards, SAME landmark indices (global arm), SAME student init
  (`torch.manual_seed(seed)` inside `_make_student`) -- only the objective differs.
- Best-by-full-held-eval CHECKPOINT SELECTION (genuinely new vs v3b, which only ever reported the
  FINAL step's value despite tracking a best-score field): periodic full-held DENSE eval every 150
  steps (13 eval points over 1800 steps, matching v3b's own `MID_DENSE_EVAL_EVERY_DIAG` cadence);
  the highest-scoring eligible checkpoint per arm is reloaded and used to encode the FINAL
  DENSE+BLOCK+keyed+shuffled numbers (not the final-step model).
- ANTI-GAMING floor on best-checkpoint eligibility: eval points before `MIN_STEP_FRAC_FOR_BEST *
  steps` (5% = step 90) are excluded from "best" selection. Rationale: every arm in every prior
  cell this arc shows DENSE ~0.95-0.96 at step~0 (an untrained random-Gaussian MLP + sign-code
  readout approximates a random-hyperplane LSH/SimHash, known to roughly preserve cosine-similarity
  RANK before any training) -- naive best-over-all-checkpoints would trivially "win" via the
  untrained-network artifact rather than genuine training. The UNCONSTRAINED all-time best (incl.
  step~0) is ALSO logged per arm as a transparency field.
- FALSE_WIN_ALGEBRA gate (restored from v3's FULL-mode dual-gate, applied to BOTH arms here): if
  either arm's BLOCK code's own KEYED (correct-key) roundtrip accuracy at J=5 is < 0.90, HARD_FAIL
  regardless of the semantic spearman numbers -- a degenerate/non-composable BLOCK code makes any
  "BLOCK spearman toward 0.85" claim meaningless. NOT gated at smoke scale (60 steps / V_train=3000
  does not reliably crystallize block-STE one-hot structure; same precedent as v3b's own smoke
  gate, which also omits this check).
- Peak-then-decline TRAJECTORY-SHAPE gate (not a rigid step-fraction rule): HARD_PASS additionally
  requires the winning (global) arm's trajectory NOT show a >=0.03 peak-to-final decline -- v3b's
  own NCE_ZERO trajectory fluctuates in a healthy 0.65-0.83 band with its single highest sample
  early (step150) yet ends respectably (0.731, no collapse); a rigid "best must be in the second
  half" rule would wrongly demote that as a "fleeting early spike" when it plainly is not.

## Bands (PRIMARY gate: DENSE recovery + global-vs-inbatch delta, per-arm)

Numeric floors per `research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md`'s own
falsifiable-prediction table (written to gate exactly this class of dispatch); delta floor per the
v3/v3b lineage's established recovery-delta convention.

- Integrity gates (checked FIRST, override everything below):
  - RANDOM_BLOCK keyed J5 acc_at1 >= 0.98, else `HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH`.
  - shuffled_key(GLOBAL_BLOCK) acc_at1 <= 0.05 AND hit_any_member <= 0.10, else
    `HARD_FAIL_SHUFFLED_KEY_LEAK`.
  - GLOBAL_BLOCK keyed J5 acc_at1 >= 0.90 AND INBATCH_BLOCK keyed J5 acc_at1 >= 0.90, else
    `HARD_FAIL_FALSE_WIN_ALGEBRA_{GLOBAL,INBATCH}`.
- **HARD_PASS**: `global_dense_best >= 0.75` AND `(global_dense_best - inbatch_dense_best) >= 0.15`
  AND global's trajectory does NOT show a >=0.03 peak-then-decline. HYPOTHESIZED@ranked-levers
  drill + v3/v3b delta convention.
- **MIDDLE_BAND**: `global_dense_best >= 0.60` AND `delta >= 0.05`, OR the HARD_PASS numeric floors
  clear but the peak-then-decline trajectory-shape check fails (recovery achieved only via a
  best-checkpoint rescue of an otherwise-declining run).
- **HARD_FAIL**: `global_dense_best < 0.60` OR `delta < 0.05` -- either the RKD-only fix does not
  reproduce here (reproducibility concern vs v3b's own NCE_ZERO=0.7336), or in_batch-RKD-only
  reaches comparably high DENSE too (H2 confirmed: landmark objective adds nothing; DROP it as the
  load-bearing mechanism and escalate to Rank 2 objective-family swap per the ranked-levers drill).

BLOCK (sparse) numbers for both arms are reported in the same `recovery{}` dict
(`global_block_best`, `inbatch_block_best`) as the secondary target-metric readout (not a separate
gate beyond the FALSE_WIN_ALGEBRA integrity check above).

## SCHEMA-VET / META_RULE fields

- cardinality_ok: true. `EXPECTED_N_UNITS_FULL = 10` (6 semantic {GLOBAL_DENSE, GLOBAL_BLOCK,
  INBATCH_DENSE, INBATCH_BLOCK, RANDOM_BLOCK, CHARPOS} + keyed {RANDOM_BLOCK, GLOBAL_BLOCK,
  INBATCH_BLOCK} J5 + shuffled GLOBAL_BLOCK J5). Verdict counts `per_unit`; shortfall ->
  `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- arms_differ_verified: true (sha256 over all 5 code matrices incl. CHARPOS; self-test additionally
  asserts GLOBAL and IN_BATCH student WEIGHTS diverge even at nce_weight=0 for both, bitwise).
- final_metrics_atomicity: "tmp_replace" (`write_metrics` helper + checkpoint `os.replace`).
- except-discipline: `except SystemExit`/`KeyboardInterrupt` re-raise before `except Exception`; no
  bare `except:`; no `except BaseException:` (grep gate PASSED on core + both seed wrappers);
  per-unit failure_class instrumentation (META_RULE_J).
- crlb_floor_computed: 0.901 (`r_max = sigma_teacher / sqrt(sigma_teacher^2 + 0.25/K)`, K=128)
  THEORETICAL@v2/v3/v3b prereg, unchanged (this cell changes only nce_weight + checkpoint-selection
  policy, not the K-block quantization channel). discriminator_reachability: true.
- baseline_in_band (META_RULE_AG): CHARPOS ret_agree10 checked in (0.05, 0.95) at verdict time.
- discriminator-survives-scale: option (B) analytical justification (SAME physics argument already
  accepted twice this arc): smoke's tiny V_train=3000 cannot reproduce a meaningful coverage effect
  at batch=128; smoke validates MACHINERY ONLY (both arms train end-to-end, best-ckpt tracking +
  reload fires, arms differ, all 10 eval units execute, cardinality holds -- MEASURED@local smoke
  run below). The actual "does in_batch-RKD-only collapse or hold at the true 177899-concept
  corpus" question can only be answered by running it at that V -- that IS this dispatch.
- calibration_check: "default_ok_for_this_regime" (identical hyperparameters to the validated
  v3/v3b lineage; only nce_weight for in_batch, checkpoint-selection policy, and the 2-seed
  replicate change).
- cell_chunked: true (ONE seed per cell file, per this role's canonical instruction file section 13
  -- a runner-death on one seed's process does not lose the sibling seed).
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics +
  traceback, atomic, in BOTH the core and each seed wrapper's own outer guard). heartbeat_present:
  true (`_heartbeat.jsonl` every 200 train steps + per eval unit).
- defensive_error_checking: "passed_all_4_patterns".
- progress_logging: "print_flush_true" (every 200-step train block + DENSE-traj + per-unit eval
  logs flush=True; `sys.stdout.reconfigure(line_buffering=True)` at each wrapper's `main()` entry).
  Not formally required (`timeout_s < 1800` per-seed-cell) but applied anyway for auditability.
- Section 15 gates: sweep_alignment_verdict N/A (no swept parameter; objective + seed are fixed
  arms/replicates, not a sweep axis). composition_edges: encoder(BLOCK code) -> SBC bind/unbind:
  SHAPE_MATCH (unchanged from v3/v3b). positive_control_arms: RANDOM_BLOCK keyed_roundtrip
  reproduces the SBC-lossless prior at this exact regime (tol 0.02 at J5, matching v3b's own
  positive control). functional_requirements: FR1 preserve teacher semantic geometry at true FULL
  scale -> the tie-breaker comparison itself; FR2 exact sparsity -> BLOCK architecture (unchanged);
  FR3 invertible composition -> SBC (unchanged, gated by the restored FALSE_WIN_ALGEBRA check); FR4
  novel-concept encodability -> MLP student (unchanged); FR5 restartability -> mining shards + per-
  arm train ckpt, seed-isolated via `run_tag`; FR6 storage: sharded per-concept codes.

## Compute architecture

Class (a) batched-GPU (`overnight_queue`). Per-batch work is batched torch matmul (MLP fwd/bwd,
[batch x L] and [batch x batch] cosine, chunked mining) -- NOT per-phase-point Python loops.
Sequential over the two objectives (global then in_batch) within EACH seed-cell process, by design
(controlled paired comparison sharing split/mining/landmarks). The two seeds are SEPARATE cell
dispatches (CHUNKED single-seed-per-cell), queued to the same single-runner `overnight_queue` and
so execute sequentially at the runner level regardless. Storage strategy: sharded (FR6). Local
smoke runs on CPU (SMOKE-only-local rule; MEASURED wall ~64-97s per run, small variance across
runs, for 2 arms x 60 steps on a 3000-concept local cache).

## Timeout

`v3b`'s own measured wall-clock for this EXACT config (batch=128 among its sweep, steps=1800, on
the SAME 177899-concept cache, on cuda) is 662.99s total for a 10-arm battery (8 batch-sweep arms +
2 NCE-ablation arms) MEASURED@data/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1/metrics.json:elapsed_s.
This cell trains only 2 arms (GLOBAL, INBATCH) at the CHEAPEST batch tier in that battery
(batch=128), plus mining (shared one-time cost, same V) and 10 eval units (fewer/lighter than
v3b's 19) -- expected wall well under v3b's 662.99s per seed-cell. A literal apply of the standard
`timeout_s = ceil(1.5 * smoke_wall_s * ...)` formula is NOT used here because local smoke runs on
CPU (MEASURED 64-97s) while production runs on the remote GPU (cuda) -- mixing a CPU baseline with
a GPU scale-up in the SAME formula would produce an unreliable number in the wrong direction (CPU
smoke over-estimates GPU full-run cost per-step, while V/step scale-up under different device
classes doesn't decompose cleanly). Using v3b's own directly-comparable GPU measurement as the
anchor instead: `--timeout 3600` (1 hour) per seed-cell, giving >=5x safety margin over the
expected sub-battery cost, checkpointed every 300 steps (`CKPT_EVERY_STEPS_FULL`) so a timeout-kill
loses at most one arm's partial progress, not the whole run, and is resumable on re-dispatch.
PROT-021 (checkpoint-mandatory >=14400s) does not apply at this timeout tier but is satisfied
regardless (genuine per-arm resume via `_seed_checkpoint` + in-cell `torch.save`/`os.replace`
checkpointing).

## Artifacts

- `data/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_seed7/metrics.json`
  (verdict + recovery{} incl. DENSE+BLOCK for both arms + per_unit + train_diag with dense_traj).
- `data/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_seed13/metrics.json`
  (same structure, seed=13).
- `data/substrate_concept_encoder_v1b_v3c_full_paired_seed7/` and `..._seed13/`: mining shards +
  `_ckpt_{GLOBAL,INBATCH}.pt` (resumable train state) + `_ckpt_best_{GLOBAL,INBATCH}.pt` (best-
  checkpoint state_dict, PRESERVED for the requested capacity/peak re-diagnostic).

## Halt conditions

Training loss NaN/Inf -> CELL_CRASHED with failure_class=NAN_LOSS. Any eval unit exception ->
recorded failure_class + FAIL_LOUD (no silent continue). Teacher cache missing/id-count mismatch ->
hard abort before training. Landmark selection empty for global objective -> ValueError before
training (self-test-verified). Best-checkpoint file corrupt on resume -> falls back to retraining
that arm from scratch (WARN logged), matching v3b's own ckpt-resume failure-handling convention.

## Decision routing (post-landing)

- HARD_PASS or the H1 branch of HARD_FAIL/MIDDLE_BAND (in_batch clearly worse than global) ->
  landmark objective validated as load-bearing; proceed toward the sparsify-after-geometry plan
  (R2 in the encoder rescue sequencing) using the GLOBAL-RKD-only config.
- HARD_FAIL via the H2 branch (in_batch-RKD-only comparably high) -> landmark objective adds
  nothing over plain in_batch once NCE is off; drop the landmark mechanism, re-run the simpler
  in_batch-RKD-only config as the production path, and report the simplification back to Research.
- Either way: report the tie-breaker delta as the headline result per the coordinator's request; DO
  NOT auto-dispatch further cells (report back for Director/USER decision on next lever).
