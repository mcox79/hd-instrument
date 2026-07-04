# Pre-reg: Encoder Migration Step 1b v3b -- batch-ratio-match sweep + NCE-weight ablation + full-held DENSE-trajectory diagnostic

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED BEFORE the intermediate-scale (mid) dispatch. Design revised in-session after the R1 paired MID verdict landed (see "Reframe" section) -- supersedes this cell's original NCE-only design (never dispatched to mid; only smoke-tested).

Cell: `experiments/exp_encoder_migration_step1b_v3b_nce_ablation_dense_recovery_diagnostic_v1_core.py`
Anchor: `encoder_migration_step1b_v3b_batch_ratio_match_nce_ablation_dense_recovery_v1` (mid suffix `_mid`, smoke suffix `_smoke`).
Parent cell: `experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py` (commit 6662c5717). Does NOT touch the parent's output dirs (`data/exp_encoder_migration_step1b_v3_..._v1_mid/`, `data/substrate_concept_encoder_v1b_v3global_mid/`); own artifact dirs under `substrate_concept_encoder_v1b_v3b_batch_ratio{_smoke,_mid}`.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01): query "contrastive NCE loss ablation tail degradation checkpoint selection distillation RKD geometry" -> top hit cosine=0.4443, generic FrameNet/WordNet lexical entries (`Duration_relation`, `distillation`), NOT a prior arc cell. Query "checkpoint selection best held eval early stop training peak degrade" -> top hit cosine=0.2783, BELOW the 0.30 threshold (WordNet lexical + one LoRA-distillation research-drill chunk about a DIFFERENT failure class -- SFT/RP objective mismatch, not co-occurrence-rate or nce-weight ablation). Prior-work check: [NONE at cosine>0.30 among arc cells; only generic KB lexical entries]. GENUINELY NOVEL: no prior cell addresses NCE-weight ablation, full-held trajectory instrumentation, or batch/N coverage-ratio matching for this encoder lineage.

## R1 paired-verdict result (do not re-litigate; the reframe trigger)

The R1 GLOBAL-vs-IN_BATCH paired MID run (seed=7, ~40k concepts, batch=512, 1800 steps) landed HARD_FAIL: global DENSE 0.521 / BLOCK 0.511 vs in_batch DENSE 0.568 / BLOCK 0.524 (delta -0.047/-0.013) MEASURED@`data/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_mid/metrics.json:recovery`. Global did NOT beat in_batch. In-training quick-eval trajectory (1500-held subsample, 60k pairs) showed peak-then-decline for the global arm: 0.740@step1200 -> 0.716@step1500 (declining) MEASURED@same path:train_diag.global.dense_traj, while the loss telemetry showed rkd (geometry) loss plateaued ~0.22 from ~step700 while nce (contrastive) loss kept falling 0.51->0.456 through the tail MEASURED@same path:train_diag.global.

## Diagnosis: MID (as originally run) was UNDERPOWERED, not a real negative

The in-batch RKD failure mode the landmark objective targets is a near-neighbor CO-OCCURRENCE-RATE problem: the in-batch target is the batch's own `[B,B]` teacher-cosine matrix, so a specific near-neighbor pair only gets gradient signal when BOTH items land in the same batch in the same step. For i.i.d.-with-replacement batch draws of size B from V train items, single-item coverage is `B/V` and pairwise co-occurrence probability is approximately `(B/V)^2`.

- FULL (cited@this cell's v3 parent docstring, "over 160k+ concepts"; N_full=160000): coverage = 512/160000 = 0.32%. Pairwise co-occurrence ~ 1.02e-5/step (matches the parent docstring's cited "~1e-5/step" almost exactly).
- MID as R1 ran it (N_train_mid=39515, batch=512): coverage = 512/39515 = 1.296%.

VERIFIED@this prereg (independently recomputed, not merely copied from the Director spawn context):
```
coverage(B/V) full    = 0.0032
coverage(B/V) mid@512 = 0.01296
mid/full coverage ratio          = 4.05x
mid/full pairwise (B/V)^2 ratio  = 16.4x
```
At MID-as-run, the in-batch objective sees 4x the per-item coverage and 16.4x the pairwise near-neighbor co-occurrence rate of FULL. Its failure mode barely fires at that ratio -- both arms land in the same ~0.52-0.57 band because there is nothing scale-dependent to rescue. This is an UNDERPOWERED test, not evidence the landmark objective is wrong.

## The fix: batch-ratio-match sweep (PRIMARY new mechanism this cell adds)

Match `batch/N_train` (not absolute batch) to FULL's ratio. Since matching the linear ratio also matches its square (squaring preserves an equality), a single batch value reproduces BOTH single-item and pairwise coverage simultaneously.

```
batch_match = 512 * (N_train_mid / N_train_full) = 512 * (39515/160000) = 126.4 -> DECISIVE_BATCH_MID = 128
coverage(128/39515) = 0.324%  (within 1.2% of FULL's 0.32%)  VERIFIED@this prereg
```

`BATCH_SWEEP_MID = [512, 256, 128, 64]` trains BOTH `global` and `in_batch` objectives, PAIRED (shared split/mining/landmarks/seed=7), at every sweep point. If the in-batch failure is genuinely coverage-driven, in-batch DENSE spearman should degrade as batch shrinks toward the FULL-representative ratio while the landmark/global objective (whose supervision comes from a FIXED L=4096 landmark frame, independent of batch-size co-occurrence) stays comparatively flat. That CURVE -- not a single point -- is the evidence, and is a cheap MID-scale stand-in for an actual FULL-scale test.

Retained from the original design, now applied at (or across) the batch-ratio-matched regime:

- (A) INSTRUMENT: full-held (n=4390 entire held set; 100k-pair sample per checkpoint for cost, 400k-pair sample -- exact R1 parity -- for every final report number) dense-eval trajectory at every checkpoint (every 150 steps) for ALL 8 batch-sweep arms. Settles whether R1's quick-eval peak-then-decline was real (H1) or subsample-eval variance (H2), and whether it is GLOBAL-specific or a generic schedule artifact also affecting IN_BATCH -- reported separately at batch=512 (R1's original regime) and at the decisive batch=128.
- (B) ABLATE the NCE term at the decisive batch (global objective only): `NCE_CURRENT` (nce_weight=0.5 const -- this IS the sweep's `B128_GLOBAL` arm, reused, not re-trained), `NCE_ZERO` (nce_weight=0.0, RKD-only), `NCE_DECAY40` (nce_weight anneals 0.5->0 linearly starting at step 0.4*total=720, near the diagnosed RKD-plateau step~700 MEASURED@diagnosis via Director spawn context).
- (C) CHECKPOINT-SELECT: best-by-full-held-eval checkpoint tracked per arm (10 arms total: 8 sweep + 2 ablation-only), separate from the resumable "latest" checkpoint.

## PAIRED TRIALS discipline (USER-locked 2026-07-04)

Every (batch, objective) pair and every nce-ablation arm shares: the same teacher split (seed=7 permutation -> same tr_idx/he_idx), the same mining shards (pos_idx/semi_cands computed once, reused across all 10 training runs -- mining does not depend on batch/objective/nce-weight), the same landmark/anchor indices (global arms; `land_idx` computed once with seed+101), and the same initial student weights (`torch.manual_seed(seed)` inside `_make_student`, called identically per arm). Batch size itself is the swept axis for the primary discriminator (not held constant by construction), so cross-batch trend reads the SHAPE of degradation, not a sample-budget-matched magnitude; the within-batch GLOBAL-vs-IN_BATCH comparison at each sweep point IS sample-budget-matched (same steps=1800, same batch, same draw sequence up to the loss-arithmetic difference) and is the cleanest paired unit. The nce-ablation arms share batch=128 with `B128_GLOBAL`, isolating nce_weight identically to the original design.

## Bands

### Primary: batch-ratio-match sweep (the decisive gate)

Let `inbatch[B]`, `global[B]` = final DENSE spearman (400k-pair full-held eval) per batch. `inbatch_degradation = inbatch[512] - inbatch[64]`. `inbatch_trend_corr` = Pearson corr(batch, inbatch[B]) across the sweep (positive = smaller batch hurts in_batch, as hypothesized). `decisive_delta = global[128] - inbatch[128]`.

- **HARD_PASS** (`BATCH_RATIO_MATCH_CONFIRMS_OBJECTIVE_ADVANTAGE`): `inbatch_degradation >= 0.10` AND `inbatch_trend_corr >= 0.50` AND `decisive_delta >= 0.15` AND `global[128] >= 0.55`. -> the coverage-ratio mechanism is confirmed at MID scale; global objective fix validated; recommend FULL dispatch (Director/USER decision, ONCE-per-stage GPU rule).
- **MIDDLE_BAND** (`PARTIAL_BATCH_RATIO_SIGNAL`): `decisive_delta >= 0.05` OR `inbatch_degradation >= 0.05`. -> some signal, short of the full bar.
- **HARD_FAIL** (`BATCH_RATIO_MATCH_DID_NOT_CONFIRM`): else. -> the batch-ratio-match test at MID does not confirm the mechanism either; an actual FULL-scale test (or another lever) is needed to settle it.

All four numbers are HYPOTHESIZED@this prereg (not yet measured at these batch values); the bands are set BEFORE the mid run per envelope-fail-band discipline.

### Secondary: NCE-weight ablation at decisive batch (reported, does not gate the primary tier)

- `TAIL_CORRUPTION_CONFIRMED_RECOVERED`: `best(NCE_ZERO, NCE_DECAY40) >= 0.70` AND `delta_vs_NCE_CURRENT >= 0.15`.
- `PARTIAL_RECOVERY`: `best >= 0.60` AND `delta >= 0.05`.
- `NOT_CONFIRMED`: else.

### H1-vs-H2 (peak-then-decline, reported, does not gate)

For `B512_GLOBAL`, `B512_INBATCH`, `B128_GLOBAL` (=NCE_CURRENT), `B128_INBATCH`: `_peak_then_decline(traj, "dense_full")` with margin 0.03 (peak value minus final value, peak strictly before final step). If true for the full-held trajectory as well as the quick trajectory at the SAME arm, degradation is real (H1); if quick declines but full does not, it is subsample variance (H2, per the original design's purpose). Reported per-arm, not gated.

### Integrity controls (checked first; unaffected by batch/objective/nce-weight)

`RANDOM_BLOCK` keyed J5 `acc_at1 >= 0.98` (else `HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH`); shuffled-key on `B128_GLOBAL_BLOCK` `acc_at1 <= 0.05` and `hit_any_member <= 0.10` (else `HARD_FAIL_SHUFFLED_KEY_LEAK`).

## SCHEMA-VET / META_RULE fields

- `cardinality_ok`: true. `EXPECTED_N_UNITS = 19` both scales: 8 sweep-DENSE (4 batches x {GLOBAL,INBATCH}) + 2 decisive-batch BLOCK (GLOBAL, INBATCH) + 4 ablation ({NCE_ZERO,NCE_DECAY40} x {DENSE,BLOCK}) + RANDOM_BLOCK(1) + CHARPOS(1) = 16 semantic + keyed RANDOM_BLOCK J5(1) + keyed decisive-GLOBAL_BLOCK J5(1) + shuffled decisive-GLOBAL_BLOCK J5(1) = 3 algebra. Verdict counts `per_unit`; shortfall -> `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- `arms_differ_verified`: true (sha256 over all ~15 code matrices + CHARPOS; MEASURED distinct in both the self-test dry-run and the smoke run).
- `final_metrics_atomicity`: `"tmp_replace"` (write_metrics helper + per-checkpoint `os.replace`).
- except-discipline: `except SystemExit`/`KeyboardInterrupt` re-raise before `except Exception`; no bare `except:`; no `except BaseException` (grep gate PASSED); per-unit `failure_class` (META_RULE_J).
- `crlb_floor_computed`: 0.901 at K_BLOCKS=128 (THEORETICAL@v2/v3 prereg, unchanged -- this cell sweeps batch/objective/nce-weight, not the block-quantization channel). `discriminator_reachability`: true.
- `baseline_in_band` (META_RULE_AG): CHARPOS ret_agree10 in (0.05, 0.95) MEASURED at smoke (0.1456; see smoke result below).
- discriminator-survives-scale: SMOKE (60 steps, tiny V_train~3000, batch sweep [128,64,32,16]) validates MACHINERY ONLY -- the batch-sweep loop runs all (B,objective) combos + ablation arms without crash, arms differ, dual-trajectory logging fires, best-checkpoint tracking fires for every arm. The coverage-ratio-collapse discriminator itself needs the real train/V_train scale relationship (option B, analytical justification per DISCRIMINATOR-MUST-SURVIVE-SCALE): smoke's V_train=3000 cannot reproduce a meaningful coverage-ratio delta at these batch sizes (even batch=16 over V=3000 is a much higher relative coverage than 128/39515, let alone 512/160000). The discriminator is validated ONLY at mid scale.
- `calibration_check`: `"default_ok_for_this_regime"` (identical regime to the already-validated v3 mid prereg; only batch/objective/nce-weight are swept, all other config -- semi-hard band, K-sparsity, LR schedule, MLP architecture -- inherited unchanged from v2/v3).
- `cell_chunked`: false (single fixed seed=7 matching the R1 lineage for exact paired comparability; not a multi-seed statistical claim). `start_marker_written`: true. `crash_diagnostic_present`: true. `heartbeat_present`: true (every 100 train steps + per eval unit). `defensive_error_checking`: `"passed_all_4_patterns"`.
- `progress_logging`: `"print_flush_true"` (MANDATORY; mid `timeout_s` estimate is well over 1800s -- see Timeout section).
- HP_SCOPE: batch-sweep collapse bands apply to `{IN_BATCH across batch}` vs `{GLOBAL across batch}`; nce-ablation bands apply to `{NCE_ZERO,NCE_DECAY40}` vs `{NCE_CURRENT==B128_GLOBAL}` only; `RANDOM_BLOCK`/`CHARPOS` are integrity-only, exempt from both.

## Section 15 gates

- `sweep_alignment_verdict`: ALIGNED. The swept parameter (batch size) is the EFFECTIVE parameter every downstream primitive experiences directly (batch is consumed as-is by `torch.randint(0,V,(batch,))` and by the in-batch `[batch,batch]` cosine matrix; no upstream partition/routing divides it). No nominal-vs-effective mismatch (contrast with the V_C-sweep/multihop_v3 failure class in gate A's canonical example).
- `discriminating_fraction`: N/A in the literal sweep-accuracy sense (this is an objective-comparison discriminator, not a top-k-accuracy sweep), but the batch values were chosen via the VERIFIED coverage-ratio calculation above specifically so that `DECISIVE_BATCH_MID=128` lands in the discriminating regime (matches FULL's ratio within 1.2%), with `512` and `64` bracketing it as over-generous and under-generous controls respectively -- not a by-construction-saturated or floor sweep.
- `composition_edges`: encoder(block code / dense-sign readout) -> SBC bind/unbind: SHAPE_MATCH (unchanged from v2/v3; algebra path untouched by batch/objective/nce-weight).
- `positive_control_arms`: `RANDOM_BLOCK` keyed_roundtrip reproduces the SBC-lossless prior at THIS regime (tolerance 0.02 at J5, gate is `>=0.98`); `B128_GLOBAL` (==NCE_CURRENT) reproduces the parent v3 cell's GLOBAL objective at a DIFFERENT (matched) batch, not a blind citation -- this cell explicitly re-trains it in-process rather than citing the R1 number, satisfying Gate D's "reproduce at test regime" requirement even though the regime here (batch=128) differs deliberately from R1's batch=512.
- `functional_requirements`: FR1 preserve teacher semantic geometry AT SCALE -> global landmark RKD, now tested at a coverage-ratio-matched regime (the fix to the test). FR2 exact sparsity -> block architecture (unchanged). FR3 invertible composition -> SBC (unchanged). FR4 novel-concept encodability -> MLP student (unchanged). FR5 restartability -> mining shards (once, shared) + per-arm train ckpt + best-ckpt. FR6 storage: sharded per-concept codes.

## Compute architecture

Class (c) mixed with justification. SMOKE runs on LOCAL CPU only (per the `local_cpu_queue` = smoke-only rule). MID is NOT dispatched by this prereg -- per Director instruction (2026-07-04), the R1 mid run's local-CPU process died from resource pressure during eval (BOINC killed itself, freeing the GPU); heavy runs now route to GPU via Orchestrator, not local CPU. Per-batch work is batched torch matmul (MLP fwd/bwd, `[batch,L]` and `[batch,batch]` cosine, chunked mining) -- NOT per-phase-point Python loops. Training runs are sequential across the 10 arms within one process (controlled comparison in one metrics.json); each arm's own step loop is the batched-GPU unit. Storage strategy: sharded (FR6).

## Timeout

**SMOKE**: local CPU direct run, no queue. MEASURED@this session: 275.8s for the ORIGINAL (pre-reframe) 3-arm NCE-only smoke design (150 steps/arm, V_train=3000, batch=192); the REVISED design (10 arms: 4 batches x 2 objectives + 2 ablation, 60 steps/arm, smaller batches) is expected in the same order of magnitude or less given fewer steps per arm despite more arms -- confirmed by direct run this session (see smoke result below).

**MID** (formula-based estimate; NOT dispatched by this prereg -- Director routes to GPU):

```
per_step_cost_cpu_batch512_L4096 = 2.41 s/step   MEASURED@data/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_mid/_heartbeat.jsonl (global-objective phase, steps 0->1700)
assumed_gpu_speedup = 10-20x   HYPOTHESIZED (historic evidence: hippo v5 M=1M 6.9-13.5s/seed on torch.cuda; cleanup_latency p50=2ms on cuda; per exp_dev role-file "HW" notes)
per_step_cost_gpu_batch512 ~= 0.12-0.24 s/step
training runs (10 total; 1800 steps each): sum over 4 batches x 2 objectives (batch-proportional cost, ~0.2s @512 down to a ~0.03-0.05s kernel-launch floor @64) + 2 ablation arms @128
  ~= 1900-2000 s (~32-33 min) at the low end of the GPU-speedup estimate
mining (shared once): ~70s   MEASURED@same heartbeat file (CPU; GPU may be similar since mining is chunk-CPU-friendly)
eval units (19 units; ~53s/unit MEASURED@CPU for the expensive ret_agree10 semantic units in the v3 mid run; GPU plausibly faster): ~200-300s
TOTAL ESTIMATE: ~35-50 min at the low end, up to ~70-90 min with generous margin for GPU-speedup uncertainty, data transfer overhead, and checkpoint I/O.
```

This is a FORMULA + RANGE, not a precise measured number (no GPU run of this cell has occurred yet). Recommend Director calibrate against the FIRST GPU launch's early heartbeat (per-step cost at batch=512 in the first ~100 steps) before committing to a fixed `--timeout`; a conservative ceiling of `--timeout 10800` (3h) is recommended for the actual dispatch to accommodate the estimate's uncertainty without needing rejustification if GPU speedup is lower than hypothesized.

## Artifacts

- `data/exp_encoder_migration_step1b_v3b_batch_ratio_match_nce_ablation_dense_recovery_v1_{smoke,mid}/metrics.json` (verdict + recovery{} block with batch-sweep-by-batch dicts, ablation numbers, H1/H2 peak-decline diagnostics, per-arm trajectories + train_diag).
- `data/substrate_concept_encoder_v1b_v3b_batch_ratio{_smoke,_mid}/_ckpt_<arm>.pt` (resumable latest checkpoint per arm) + `_ckpt_best_<arm>.pt` (best-by-full-held-eval checkpoint per arm, 10 arms) + `_mine_shards/` (mining shards, computed once, shared across all 10 arms).

## Halt conditions

Training loss NaN/Inf -> CELL_CRASHED with `failure_class=NAN_LOSS` (arm-specific). Any eval-unit exception -> recorded `failure_class` + FAIL_LOUD (no silent continue). Teacher cache missing/id-count mismatch -> hard abort before training. Landmark selection empty for a global-objective arm -> `ValueError` before training (self-test-verified this raises correctly).

## Decision routing (post-mid)

- HARD_PASS (batch-ratio-match confirms) -> hand back to Director/USER: the objective fix is validated at a coverage-ratio-matched regime; next = a single GPU FULL of the global objective at true scale (Director routes to Orchestrator; ONCE-per-stage GPU rule), informed by the NCE-ablation result (use NCE_DECAY40 or NCE_ZERO config if it recovered the peak) and the best-by-full-held checkpoint (early-stop candidate).
- MIDDLE_BAND/HARD_FAIL -> report the numbers; do NOT dispatch FULL from this result alone; route back to Research for the next lever (an actual reduced-scale-but-real-N_train_full test with the SAME small absolute batch used at true FULL cardinality is the more decisive but far more expensive follow-up; or reconsider whether coverage-rate is really the operative mechanism).

## Smoke result (this session, local CPU)

See exp_dev completion report for the live smoke verdict + per-unit metrics (recorded at dispatch time in `data/exp_encoder_migration_step1b_v3b_batch_ratio_match_nce_ablation_dense_recovery_v1_smoke/metrics.json`).
