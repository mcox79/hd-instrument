# Pre-registration: gap4_cold_storage_no_combine_v1

**Date:** 2026-06-26
**Anchor:** gap4_cold_storage_no_combine_v1
**Queue:** remote_cpu_queue (USER directed; traveling)
**N:** 4096, **Seeds:** [11, 13, 19], **Cycles:** 2500
**ENCODER_PROVENANCE:** SUBSTRATE_NATIVE

## Scientific question

Cell B (REM homeostasis global downscale W *= 0.99) HARD_FAILed across three schedules — multiplicative downscale destroyed the dwindling-but-precious old tail. USER reframe: substrate should NEVER delete weights. Move stale + low-importance weights to a separate W_cold matrix (exact strength preserved forever), and aggressively norm-normalize (not multiplicatively downscale) W_active. Brain-lit basis: Liu Neuron 2024 (engram silencing not deletion), Yang Nature 2025 (systems consolidation reorganizes circuitry), Li 2017 NComms (REM-spine pruning selective to new uncaptured spines). Database analog: HotRAP LSM-tree tiered storage; SEDM merge-and-recycle.

Does relocating low-activity weights from W_active to a separate exact-preserved W_cold matrix (and replacing destructive downscale with norm-normalize) close Cell B's HARD_FAIL_DESTROYS_OLDER and deliver measurable drift reduction at substrate scale?

## Pre-registered bands

**HARD-PASS_COLD_STORAGE_WORKS (all 4 conditions):**
- best cold-storage arm `final_forget` <= 0.10 on old patterns
- best cold-storage arm `integrity` (W_active norm bounded within target) >= 0.90
- `drift_reduction` (baseline_final_forget - best_cold_final_forget) >= 0.30 absolute
- best cold-storage arm `cv` across seeds <= 0.07

**HARD-PASS_PARTIAL:** `drift_reduction` >= 0.20 abs but not all HP conditions met.

**MIDDLE_BAND:** `drift_reduction` in (0.05, 0.20) -- mechanism real but smaller than predicted.

**HARD-FAIL_COLD_STORAGE_DOESNT_HELP:** `drift_reduction` <= 0.05 (matches baseline; cold-storage architecture not effective).

Bands LOCKED at module init via assert; sacrosanct both ways per envelope-fail-band discipline.

## Arms (4 per Research drill handoff)

- **ARM_BASELINE_NO_DOWNSCALE**: rail; reproduces Cell A/B BASELINE drift (no downscale, no migration). Establishes the "no-intervention" forget curve at alpha=0.61.
- **ARM_GLOBAL_DOWNSCALE_99_100**: reproduces Cell B HARD_FAIL pattern (W *= 0.99 every cycle). Sanity check that we still observe the failure mode locally.
- **ARM_COLD_STORAGE_NO_COMBINE**: the test. W_active + W_cold; K_migrate=500 (scan cadence); K_threshold=2000 (staleness); IMPORTANCE_THRESHOLD=0.10; norm-normalize W_active at first migration to target = init_norm * 1.10.
- **ARM_COLD_STORAGE_TAU_500**: different migration threshold (K_threshold=500; tighter staleness). Tests parameter sensitivity.

Discriminator: cold-storage arms should beat BASELINE drift by >= 0.30 AND beat GLOBAL_DOWNSCALE pattern by even more (the latter is expected to be catastrophic at alpha=0.61).

## Calibration rationale

Drift Cell B HARD_FAIL (3 schedules), Cell A NREM replay MIDDLE_BAND (drift_red=0.067). Research drill prediction P_deflated=0.50 (HotRAP + SEDM + Tonegawa-engram lit precedents; novel three-tier composition at substrate scale).

Anchor numerics: at N=4096, 2500 cycles = alpha=0.610 (~4.4x Hopfield capacity, alpha_c=0.138). Research drill: 'baseline cliffs around alpha=0.61' — discriminating regime. HARD_PASS_FORGET_CEILING=0.10 is moderate (90% retention; less tight than TWO_TIER's 0.05 because cold-storage doesn't promote-and-merge, just relocates). HARD_PASS_DRIFT_REDUCTION=0.30 ensures cold-storage genuinely improves over baseline (not noise-level). HARD_PASS_INTEGRITY_FLOOR=0.90 is the load-bearing implementation check: W_active normalization must keep the matrix from drifting more than 10% off target — if it drifts, the substitute-for-downscale is broken. CV ceiling 0.07 inherits from Cell A NREM replay / TWO_TIER (same continual-cycles class).

The random-target tau_500 ablation isolates K_threshold sensitivity: if both cold arms perform equivalently, the architecture is robust to threshold choice; if only one wins, threshold matters.

## N-suffix section

Anchor name does NOT contain _n<N> suffix (PROT-018 rule: omit suffix when N=N_default-for-cell; the cell's production N=4096 is canonical for the continual-cycles class; matches sibling TWO_TIER cell). Both smoke and FULL use identical N=4096 per META_M7 capacity-sensitive-dims rule. Only N_CYCLES, RECALL_PROBE_M, CHECKPOINT_INTERVAL, K_MIGRATE, K_THRESHOLD, and SEEDS change between smoke and full.

## Timeout estimate (Fix #17 measurement strict)

Reference: NREM-replay v1 smoke wall ~24.4s for N=1024, 500 cycles, 4 arms, 1 seed = ~6.1s per arm-per-500cyc-N1024.

Scaling to N=4096, 2500 cycles, 4 arms, 3 seeds:
- per-cycle work dominates by N^2 (W @ state matmul); cycle count linear.
- per-arm wall (N=4096, 2500 cycles, baseline) ~ 6.1 * (4096/1024)^2 * (2500/500) = 6.1 * 16 * 5 = 488s ~ 8 min.
- Cold-storage arms also do periodic migration scan: score-importance per atom-so-far at K_migrate=500 (5 migration events) = O(N^2 * cap) per event; estimated +30% per cold arm = ~640s.
- Per-seed total = 2 * 488s baseline-class + 2 * 640s cold-class = ~2250s ~ 38 min.
- Three seeds = ~115 min ~ 2 hr.
- Add 50% safety margin: ~3 hr.
- This is below PROT-019 4-hr floor for _n>=4096 — but anchor name has NO _n suffix, so PROT-019 does not apply.

**timeout_s = 14400 (4 hr)** — gives generous safety + matches sibling TWO_TIER (consistent cap for the class). _seed_checkpoint imported (PROT-021 satisfied). Routes to remote_cpu_queue per USER directive (traveling).

**Smoke-derived measurement REQUIRED before final timeout commit**: cell-author runs smoke; measures per-(arm, seed) wall; recomputes timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^1.0 * (FULL_seeds/smoke_seeds) * (FULL_cycles/smoke_cycles)). If smoke extrapolation exceeds 4 hr, REVISE timeout or split arms.

Per-arm sub-checkpoint (NESS-hang prevention USER 2026-06-26): _write_arm_partial after each arm completes; caps a single hang to 1 arm-run of compute (~8-11 min).

Sub-cycle progress: print every CHECKPOINT_INTERVAL (250 cycles) cycle => liveness signal ~once per ~50s under nominal load.
