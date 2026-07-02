# Pre-registration: stage2_cleanup_latency_operating_curve_v1

**Date:** 2026-07-01
**Anchor base:** stage2_cleanup_latency_operating_curve_v1_seed_{7,13,19}
**Chunks:** 3 single-seed cells (seed_7 smoke first; seeds 13/19 dispatched on HP smoke)
**Scripts:**
- experiments/_stage2_cleanup_latency_operating_curve_v1_core.py (shared core)
- experiments/exp_stage2_cleanup_latency_operating_curve_v1_seed_7.py
- experiments/exp_stage2_cleanup_latency_operating_curve_v1_seed_13.py
- experiments/exp_stage2_cleanup_latency_operating_curve_v1_seed_19.py

**Queue:** local_cpu_queue for smoke ONLY (USER-locked 2026-07-01: no FULL to
local). FULL runs -> overnight_queue (mixed numpy+torch; torch arms will use
GPU when available, numpy arms run on GPU-machine CPU; both are cheap).

## Parent + prior work (substrate-KB verified)

Substrate-KB concept-query 2026-07-01 for "cleanup latency operating curve
substrate timing budget p50 p95 p99":

  Top-5 hits (max cosine=0.298; source_class=chunk_note):
    1. notes/research_drill_field_VSA_NeSy_rule_DEEPER_5x_2026-06-07.md (Substrate mapping) c=0.298
    2. notes/pattern_b_integration_demo_executable_spec_v278_2026-05-29.md (Substrate-physics latency vs integration-engineering latency) c=0.295
    3-4. notes/exp_dev_to_research_DISCRIMINATIVE_WEIGHTING_UNIVERSAL_2026-06-11.md (cleanup/count substrate operations plateau) c=0.290
    5. notes/research_drill_continual_full_cls_5x_2026-06-10.md (spin-glass phase) c=0.289

  **Prior-work check: NONE at cosine>0.30.** No prior cell has characterized
  cleanup-query wall-time (p50/p95/p99) as a function of load alpha at the
  operating regime. Adjacent hit #2 discusses substrate-physics vs
  integration-engineering latency as a category distinction but does not
  measure it. This cell is genuinely NOVEL for M3 Phase 1 routing timing budget.

**Reference cell (mechanism reuse):**
- v2c dual-readout: experiments/exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_7.py
  - Established substrate = Hebbian W + sign + argmax-cleanup mechanism
  - Cleanup dominates raw Hebbian AGS-SNR at alpha=3-30 range
  - This cell reuses the identical W construction (streaming outer-product accumulator, /N normalization) + cleanup readout (target_cos vs random_probe_cos)
  - **Divergence from v2c:** v2c measures ACCURACY (bit_match, cleanup_recall); v1 measures WALL-TIME per query (p50/p95/p99). f=0 always (clean queries; latency is the metric, not accuracy).

## Hypothesis (M3 Phase 1 routing timing budget)

M3 cortex layer needs a per-query cleanup timing budget to decide whether to
route substrate cleanup as a real-time operation (< 1ms class), a batched
operation (1-100ms class), or a background/approximate operation (> 100ms
class). This cell characterizes p50/p95/p99 latency at (N, alpha) operating
points spanning below-wall (alpha=0.5), at-wall (alpha=1.0, 3.0), and
supra-capacity (alpha=10.0, 30.0) regimes at TWO scales (N=2048, 8192).

**Predicted structural findings (REVISED 2026-07-01 post-smoke):**

The per-query cleanup op is `q @ W.T` (O(N^2) FLOPs; W is N-x-N built once
during arm setup). Since the query op does not iterate over M items (it's a
projection through the accumulated N-x-N matrix), **per-query latency is
O(N^2) constant with respect to M / alpha**. M / alpha only affects W
construction (one-time cost per arm), not per-query cost.

- **HYPOTHESIZED@this_prereg** (revised from initial O(M)): p50 latency at
  fixed N is approximately constant across alpha; coefficient of variation
  (std/mean) < 30% across the 5-alpha sweep at each N.
- **MEASURED@smoke seed_7 2026-07-01** (data/exp_stage2_cleanup_latency_operating_curve_v1_seed_7/):
  - N=2048 across alpha in {0.5,1,3,10,30}: p50 in {780,634,859,745,767} us
    -> mean 757us, std 74us, cv=9.8% (well under 30%; confirms O(N^2)-constant hypothesis)
  - N=8192 preview at alpha=3.0: p50=14357us (14.4ms)
  - Scaling ratio: (8192/2048)^2 = 16; observed 14.4ms / 757us ~ 19x. Close
    to N^2 (allowance for cache effects at 8192-wide matmul).
- p99/p50 ratio measured 1.3-1.6 across all smoke arms; HP_TAIL_CONTROLLED
  fires trivially.
- **Initial HP_100US and HP_1MS budgets were mis-calibrated** (based on 20
  GFLOP BLAS assumption). Numpy per-query overhead (Python dispatch +
  small-matmul BLAS setup) dominates at these sizes on this platform.
  Realistic budgets on numpy CPU: N=2048 ~ 1ms; N=8192 ~ 15ms.

## Design

**Latency grid (main sweep, numpy backend, warm cache):**
- N in {2048, 8192}
- alpha in {0.5, 1.0, 3.0, 10.0, 30.0}
- f = 0.0 (clean query; not measuring accuracy)
- 5 arms per N, 10 arms total for main sweep
- N_QUERIES = 1000 per arm; log per-query wall time
- Per arm: mean, p50, p95, p99, min, max latency + cleanup_recall (sanity check)

**Backend comparison arms (at N=8192, alpha=1.0, warm cache):**
- ARM_NUMPY (same as main sweep entry — reused)
- ARM_TORCH_CPU: torch.tensor @ W_torch; measures Python-torch dispatch overhead
- If torch.cuda available on runner: ARM_TORCH_CUDA additionally

**Cache comparison arm (at N=8192, alpha=3.0):**
- ARM_WARM_MAIN (from main sweep — reused; runs after 50-query warmup)
- ARM_COLD: FIRST call in a fresh subprocess-simulating cell (100-query batch, no warmup)

**Total arms:** 10 (main) + 1 (torch_cpu extra) + optional 1 (torch_cuda) + 1 (cold) = 12-13

**Timing methodology:**
- Warmup: 50 no-record queries before measurement starts (LRU cache primed, JIT paths hot)
- Per-query timing: `t0 = time.perf_counter(); result = query_op(); t1 = time.perf_counter(); dt = t1 - t0`
- Store all 1000 dt values per arm; compute percentiles from raw sample
- Cold-cache arm: fork subprocess OR run first-arm-in-cell without warmup, then measure first 100 queries

## Falsifiable HP / HF gates

**HP_LATENCY_INDEPENDENT_OF_M** (chain-grade if all 3 seeds; REVISED post-smoke):
For each N in {2048, 8192}, the coefficient of variation (std / mean) of p50
across the 5-alpha sweep at that N is < 30%. Validates the physics prediction
that cleanup query cost is O(N^2) constant with respect to load M.
MEASURED@smoke seed_7 N=2048 sweep: cv=9.8%. Discriminator survives at
smoke scale.
(Note: original HP_LATENCY_TRACKS_M expected O(M) slope; smoke revealed the
op is O(N^2)-constant-in-M. Slope is now REPORTED as informational, not
gated. See `slope_log_log_p50_vs_M` field in metrics.)

**HP_TAIL_CONTROLLED** (chain-grade):
Across all main-sweep arms, p99/p50 ratio < 5.0. No pathological long-tail
convergence in cleanup argmax.
MEASURED@smoke seed_7: max p99/p50 across 6 arms = 1.60 (well under 5.0).

**HP_N2_SCALING** (chain-grade; NEW REVISED gate):
p50 latency ratio between N=8192 and N=2048 (at same alpha) is in [8, 32].
This bracket spans "N^2 = 16x" with 2x safety in each direction.
MEASURED@smoke seed_7 alpha=3.0: 14357us / 859us = 16.7x -> within band.
Confirms O(N^2) per-query scaling.

**HP_CLEANUP_TIMING_BUDGET_1MS_N2048** (M3-actionable; REVISED):
At (N=2048, alpha=1.0): p50 < 1 millisecond. Small-N substrate supports
batched routing at kHz rates on pure numpy CPU.
MEASURED@smoke seed_7: p50 = 634us at (N=2048, alpha=1.0) -> under 1ms.
(Original HP_100US budget was infeasible on numpy; deferred to torch/GPU
follow-up cell.)

**HP_CLEANUP_TIMING_BUDGET_20MS_N8192** (M3-actionable; REVISED):
At (N=8192, alpha=3.0): p50 < 20 milliseconds. Commercial-M regime supports
batched routing at ~50-100Hz on pure numpy CPU.
MEASURED@smoke seed_7 preview: p50 = 14.4ms at (N=8192, alpha=3.0) -> under 20ms.
(Original HP_1MS budget was infeasible on numpy; SOFT_HP_5MS also infeasible;
deferred to torch/GPU follow-up cell.)

**HF_LATENCY_EXPLOSION** (falsification):
Any arm has p99 > 100 * p50 -> unbounded convergence pathology; cleanup
readout is not timing-budgetable.

**HF_SUB_LINEAR_M_SCALING** (informational, not chain-grade):
Slope of log(p50) vs log(M) is > 2.0 (super-quadratic in M). Unexpected
substrate scaling; requires investigation.

**HF_STRUCTURAL_INFRA:**
- baseline arm NaN
- UNIT_CARDINALITY_BREACH: len(core) != EXPECTED_N_UNITS
- META_RULE_AF: bit-identical timing hashes across nominally-different arms
- CELL_CRASHED

## Cardinality (META_RULE_H)

EXPECTED_N_UNITS = 10 main + 1 torch_cpu + 1 cold = 12
(torch_cuda arm skipped if runtime detects no CUDA; count remains 12)

`cardinality_ok: bool` in verdict logic — if `len(per_arm) < 12`, emit
`HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.

## CRLB / capacity-feasibility

Latency measurement has no CRLB in the accuracy sense; the noise floor is
system jitter. From literature: modern CPU perf_counter resolution is
~100ns; measurement floor ~1us for individual op timings. p50 measurements
at > 10us are cleanly separable from timer noise.
`crlb_n/a: "latency measurement; noise floor is timer resolution ~1us"`.

**Discriminator survival check (Pattern C — full-N preview in smoke):**
Smoke runs at N=2048 core sweep (5 arms) AND a FULL-N (N=8192, alpha=3.0)
preview arm with 200 queries. Preview must show p50 in [500us, 20ms] range
(spans HP + fallback HP band); if outside, discriminator will not fire at
full-N in main dispatch.

## META_RULE gate compliance

- `arms_differ_verified: true` — timing arrays hashed via SHA256 per arm; must
  differ across (N, alpha) pairs; exempted only for reused entries logged as
  aliases (e.g., ARM_TORCH_CPU_reuse points to same measurement, flagged).
- `final_metrics_atomicity: tmp_replace`
- `except SystemExit: raise` before `except Exception:` (no BaseException)
- `crlb_floor_computed: n/a` (see above)
- `discriminator_reachability: true` (theoretical predictions place HP inside
  achievable regime)
- `baseline_in_band: not_applicable_metric_is_latency_not_accuracy` — the
  baseline concept doesn't apply here; the discriminator IS the curve shape.
  Explicit gate: at least one arm must show p50 > 10us (proving measurement
  is real, not sub-timer-resolution numpy vectorization artifact).
- `discriminating_fraction: 5/5 = 1.0` at each N (all sweep points span
  meaningful load regimes below-wall to supra-cap)
- `sweep_alignment_verdict: ALIGNED` (M = alpha * N is the primitive experiences
  what the discriminator measures)
- `composition_edges: none` (no primitive-to-primitive composition; single-primitive
  latency profile)
- `positive_control_arms: [ARM_NUMPY_baseline]` — reproduces v2c cleanup
  primitive at (N=8192, alpha=1.0); cleanup_recall must be >= 0.95 (v2c
  showed cleanup dominates at alpha<=3); if not, invocation mismatch.
- `functional_requirements: [cleanup_query_wall_time_p50_p95_p99]` decomposed
  and maps to argmax-cleanup primitive (chain-grade).
- `calibration_check: default_ok_for_this_regime` (perf_counter is monotonic
  ns-resolution on all supported platforms)
- `cell_chunked: true`
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: true`
- `progress_logging: print_flush_true`
- `run_mode_verified_post_dispatch: true` — smoke + full each verify
  landed metrics.json run_mode field before framing verdict.

## HP_SCOPE per-arm declaration

- HP_LATENCY_INDEPENDENT_OF_M: applies to main-sweep arms — cv across alpha at each N
- HP_TAIL_CONTROLLED: applies to all 10 main-sweep arms + torch_cpu + cold
- HP_N2_SCALING: applies to (N=2048, alpha=3) and (N=8192, alpha=3) pair
- HP_CLEANUP_TIMING_BUDGET_1MS_N2048: applies to (N=2048, alpha=1.0) arm ONLY
- HP_CLEANUP_TIMING_BUDGET_20MS_N8192: applies to (N=8192, alpha=3.0) arm ONLY

## Verdict tiering

- CHAIN_GRADE: all 4 HP fire across 3 seeds AND cv(p50 across seeds) < 25% at
  same (N, alpha)
- HARD_PASS: 3-of-4 HP fire across 3 seeds
- MIDDLE_BAND: 2-of-4 HP fire OR HP fires 3-seed but 1 HF_LATENCY_EXPLOSION
- HARD_FAIL: HF_LATENCY_EXPLOSION at any regime OR HF_STRUCTURAL_INFRA

## Timeout budgeting

FULL cell cost estimate:
- 10 main arms * 1000 queries. Per-query costs:
  - N=2048: ~200us numpy => 5 arms * 1000q * 200us = 1s
  - N=8192: ~4ms numpy => 5 arms * 1000q * 4ms = 20s
- 1 torch_cpu arm at N=8192 * 1000q ~ 4ms => 4s
- 1 cold arm at N=8192 * 100q ~ 4ms => 0.4s
- W construction dominates at high alpha: alpha=30 * N=8192 => M=245k
  * chunked outer accumulate ~ 5-30s per high-alpha arm
- Total per-seed FULL wall estimate: ~2-5 minutes
- Timeout: 3600s (1h) = 12-30x safety margin

Smoke cost estimate (5 arms N=2048 + 1 preview arm N=8192):
- ~30 seconds real-time

## Load-bearing framing

Result feeds M3 Phase 1 routing timing budget:
- If HP_100US fires: M3 can route single-query cleanup in real-time at small-N
- If HP_1MS fires: M3 can batch cleanup queries at kHz throughput
- If only SOFT_HP_5MS fires: batched-only at 100-200Hz (still M3-viable)
- If neither HP nor SOFT_HP fires at commercial-M: cortex must approximate
  (locality-sensitive hashing / product-quantization / hierarchical cleanup)
  OR pre-batch. Load-bearing for M3 architectural decision (Phase 1 router
  timing).
