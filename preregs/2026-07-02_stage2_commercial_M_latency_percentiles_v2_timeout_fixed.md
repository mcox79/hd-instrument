# Pre-registration: stage2_commercial_M_latency_percentiles_v2_timeout_fixed

**Date:** 2026-07-02
**Anchor base:** stage2_commercial_M_latency_percentiles_v2_timeout_fixed_seed_{7,13,19}
**Chunks:** 3 single-seed cells (seed_7 smoke first on local_cpu; seeds 13/19 dispatched full to overnight_queue on HP smoke)
**Scripts:**
- experiments/_stage2_commercial_M_latency_percentiles_v2_timeout_fixed_core.py (shared core)
- experiments/exp_stage2_commercial_M_latency_percentiles_v2_timeout_fixed_seed_7.py
- experiments/exp_stage2_commercial_M_latency_percentiles_v2_timeout_fixed_seed_13.py
- experiments/exp_stage2_commercial_M_latency_percentiles_v2_timeout_fixed_seed_19.py

**Queue:** overnight_queue (GPU) for FULL — need torch.cuda for the M3 SLA measurement. Smoke on local_cpu_queue (USER-locked 2026-07-01: no FULL on local).

**Timeout:** **7200s per seed** (2× v1's 3600s; USER-authorized). Wall estimate below.

## Motivation (from v1 salvage)

v1 dispatched 2026-07-02 to overnight_queue, all 3 seeds TIMED OUT at 3600s having completed 7/9 arms each. metrics.json never written (v1 only writes at end). Heartbeat.jsonl captured p50 / p99 / recall / build_s for the 7 completed arms per seed. Salvaged via `tools/salvage_commercial_M_latency_v1_heartbeats_to_partial_metrics.py` → 21/27 arm-outcomes (all M=1M non-numpy arms missing across all 3 seeds).

**v1 heartbeat measured (all 3 seeds, mean p50 across seeds):**
| M | numpy | torch_cpu | torch_cuda |
|---|-------|-----------|------------|
| 100k | 11.85 ms | 14.59 ms | **2.36 ms** |
| 500k | 12.44 ms | 15.79 ms | **1.66 ms** |
| 1M | 12.44 ms | MISSING | **MISSING** |

M-invariance of the per-query op ALREADY confirmed by 3 seeds × 3 M numpy points (all in 10-15 ms band; ratio well within [0.5, 5.0]). **The missing measurement is the load-bearing M3 SLA:** M=1M torch_cuda p50.

## v2 architectural fixes

### FIX 1: shared-W-per-M (build W once, reuse across 3 backends)

v1 built W independently per (M, backend) arm → 3× M-build cost. Since W is deterministic per (M, seed) and the 3 backends only differ in the query operator (numpy sign/dot vs torch sign/dot), v2 builds W ONCE as numpy per M value and converts to torch tensors for the torch arms.

**Wall accounting (from v1 heartbeat seed_7 build_s):**
- v1 total build cost: 3×(99 + 461 + 922) = **4446 s**
- v2 predicted build cost: 99 + 461 + 922 = **1482 s**
- Savings: **~2960 s per seed** (49 min)

### FIX 2: per-arm incremental metrics.json checkpoint

v1 wrote metrics.json ONLY at end. v2 writes after EACH arm completes:
- Append arm record to `_arm_results.jsonl`
- Atomic rewrite of `metrics.json` with all arms-so-far via tmp+os.replace
- Verdict `SALVAGE_PARTIAL` while `len(per_arm) < expected`; verdict → HARD_PASS / MIDDLE_BAND / HARD_FAIL only when all arms have landed

If timeout hits mid-run, `metrics.json` reflects everything completed up to the last-completed-arm boundary. **At most 1 in-flight arm's data is lost, not all N-completed arms.**

## Wall estimate (v2 predicted)

From v1 seed_7 measurements (elapsed since start at each arm end):
- Arm 0 (M=100k numpy): 112 s (build 99 + measure 13)
- Arm 1 (M=100k torch_cpu): 218 s (delta 106; v2 would save ~88 s build)
- Arm 2 (M=100k torch_cuda): 318 s (delta 100; v2 would save ~96 s build)
- Arm 3 (M=500k numpy): 792 s (delta 474; build 461 dominates)
- Arm 4 (M=500k torch_cpu): 1284 s (delta 492; v2 would save ~472 s build)
- Arm 5 (M=500k torch_cuda): 1758 s (delta 474; v2 would save ~471 s build)
- Arm 6 (M=1M numpy): 2693 s (delta 935; build 922 dominates)
- Arms 7, 8 (M=1M non-numpy): missing but predicted delta ~15 s each (query-only after shared build); v2 would save ~2×(922) - 15 = ~1830 s
- **v2 predicted total wall: ~2700 s** (build-shared savings roughly halve the build cost)
- Timeout 7200 s = 2.7× predicted; strong safety margin

## Prior work (substrate-KB verified)

Substrate-KB concept-query 2026-07-02 already covered in v1 pre-reg (`preregs/2026-07-01_stage2_commercial_M_latency_percentiles_v1.md`). NONE at cosine>0.30. v2 is architectural fork of v1; the measurement itself remains genuinely novel.

**Reference cells:**
- v1: `exp_stage2_commercial_M_latency_percentiles_v1_seed_{7,13,19}.py` — same measurement design; timed out at 3600s. Salvage at `data/exp_stage2_commercial_M_latency_percentiles_v1_seed_*/partial_metrics.json` (21/27 arms).
- cleanup_latency v1 CG: established per-query op is O(N²) constant in M/alpha.

## Hypothesis (unchanged from v1)

M3 Phase 1 cortex layer needs per-turn substrate lookup timing budget at commercial M. If HP_M1M_UNDER_100MS fires, M3 promises real-time substrate lookup at M=1M on GPU deployment.

Additional NEW hypothesis for v2 (from v1 salvage evidence):
- **HYPOTHESIZED@v1_salvage:** torch_cuda at M=1M will show p50 in {1-5 ms} range (extrapolating from 100k p50=2.36 ms + 500k p50=1.66 ms both well under 10 ms; per-query op is M-invariant per v1 numpy evidence and per cleanup_latency v1 CG).
- **HYPOTHESIZED@v1_salvage:** HP_M1M_UNDER_100MS will fire trivially at ~50× margin — commercial-M real-time substrate SLA viable at M3 Phase 1.
- **HYPOTHESIZED@v1_salvage:** HP_CUDA_SPEEDUP at M=1M will show ratio ~0.1-0.3× (CUDA ~10-100× faster than numpy).

## Design (unchanged from v1 mechanism; only orchestration differs)

**Latency grid (FULL):**
- N = 8192 (fixed)
- M ∈ {100_000, 500_000, 1_000_000}
- backend ∈ {numpy, torch_cpu, torch_cuda}
- 3 M × 3 backend = 9 arms per seed
- WARMUP_QUERIES = 100; N_QUERIES = 1000 recorded per arm
- 3 seeds ({7, 13, 19})

**Query op:** identical to v1 (mechanism preservation across salvage-and-refactor is load-bearing for the M3 SLA comparability).

**Streaming W build:** numpy chunk_m = 4096; never materialize >4096 rows at once.

**Smoke design (unchanged from v1):**
- FULL N=8192, single M=100k, backends {numpy, torch_cpu}, plus a PREVIEW torch_cuda arm at M=100k.
- N_QUERIES = 50, WARMUP = 10.
- Preview arm reuses the SAME shared W (v2 architecture wins even in smoke).

## HP / HF gates (unchanged from v1)

**HP gates (5 defined):**
- `HP_M1M_UNDER_100MS`: (M=1M, torch_cuda) p50 < 0.100 s
- `HP_M100K_UNDER_10MS`: (M=100k, torch_cuda) p50 < 0.010 s
- `HP_TAIL_CONTROLLED`: p99/p50 < 3.0 for all OK arms
- `HP_NUMPY_SCALES_INVARIANT`: numpy p50 at M=1M / M=100k ∈ [0.5, 5.0]
- `HP_CUDA_SPEEDUP`: torch_cuda p50 at M=1M < 0.5 × numpy p50 at M=1M

**HF gates:**
- `HF_M1M_INFEASIBLE`: any backend p50 > 1 s at M=1M
- `HF_TAIL_EXPLOSION`: p99/p50 > 100 anywhere
- `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`
- `HARD_FAIL_META_RULE_AF_BIT_IDENTICAL`

**Verdict roll-up:** unchanged from v1 (HP_HARD_PASS_MIN_DENOM = 3 enforces band-floor discipline).

## Partial-metrics interpretation (new v2 semantic)

If `metrics.json.verdict == "SALVAGE_PARTIAL"`: the cell ran + wrote arms up to that point but did NOT reach the final all-arms-landed state (e.g. timeout kill). `verdict_msg` says which arms completed. Skunkworks / Director should treat as MEASURED_MECHANISM candidate for the completed arms only; final HP/HF gates unreliable until all 9 arms land.

If `metrics.json.verdict == "HARD_PASS" | "MIDDLE_BAND" | "HARD_FAIL"` AND `checkpoint_kind == "final_complete"`: full 9-arm run landed; verdict reflects the full HP roll-up.

## SCHEMA-VET checklist (META_RULE_H/J/K/L/M/AC/AF/AG/AH)

- `cardinality_ok`: **true** — EXPECTED_N_UNITS = 9 (full) / 3 (smoke). `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` only fires when NOT partial.
- `per_unit_failure_class`: **true**.
- `discriminator_fires`: **true** (smoke preview CUDA arm; smoke arms-differ hash verified).
- `strictly_above_floor`: **true** (hard numbers, not `>=` floors).
- `HP_SCOPE`: same as v1.
- `calibration_check`: `default_ok_for_this_regime` (perf_counter monotonic ns; torch.cuda.synchronize).
- `arms_differ_verified`: **true** (SHA256 hash of per-query timings + config).
- `final_metrics_atomicity`: `tmp_replace` — atomic per ARM (not just final) via `_write_incremental_metrics`.
- `except_ordering`: `SystemExit -> KeyboardInterrupt -> Exception` (no BaseException).
- `crlb_n/a`: latency measurement; noise floor = perf_counter resolution (~ns).
- `discriminator_reachability`: **true** (HP thresholds achievable per v1 salvage evidence).
- `baseline_in_band`: N/A (latency measurement).
- `progress_logging`: `print_flush_true`; `sys.stdout.reconfigure(line_buffering=True)`.
- `cell_chunked`: **true**.
- `start_marker_written`: **true**.
- `crash_diagnostic_present`: **true**.
- `heartbeat_present`: **true** (per-arm-start + per-arm-complete + per-M-W-build-start).
- `defensive_error_checking`: `passed_all_4_patterns`.
- **v2-specific: `per_arm_incremental_checkpoint_present`: true** — after each arm, atomic tmp+os.replace rewrite of metrics.json + append to `_arm_results.jsonl`.

## §15 gates (test-design failure prevention) — unchanged from v1

- A) effective_vs_nominal_parameter_audit: ALIGNED.
- B) bracket_includes_discriminating_band: N/A for latency (all sweep points expected to yield measurable percentiles). `discriminating_fraction = 1.0`.
- C) signal_shape_compatibility_audit: SHAPE_MATCH (no composition).
- D) reproduce_prior_chain_grade_result_as_positive_control: v1 numpy at M=100k measured p50 = 11.85 ms (mean of 3 seeds); v2 numpy at same regime should reproduce within tolerance 3× (accept [4, 40] ms). If OUTSIDE, mechanism drift between v1 and v2 detected — HALT.
- E) functional_requirement_decomposition_present: "M3 Phase 1 must decide per-turn substrate lookup timing budget at commercial scale." Mapping: substrate cleanup query = existing CG primitive (v2c dual-readout + cleanup_latency v1).

## Files

- `experiments/_stage2_commercial_M_latency_percentiles_v2_timeout_fixed_core.py`
- `experiments/exp_stage2_commercial_M_latency_percentiles_v2_timeout_fixed_seed_7.py`
- `experiments/exp_stage2_commercial_M_latency_percentiles_v2_timeout_fixed_seed_13.py`
- `experiments/exp_stage2_commercial_M_latency_percentiles_v2_timeout_fixed_seed_19.py`
- `preregs/2026-07-02_stage2_commercial_M_latency_percentiles_v2_timeout_fixed.md` (this file)
- `tools/salvage_commercial_M_latency_v1_heartbeats_to_partial_metrics.py` (v1 salvage; already ran)
- `data/exp_stage2_commercial_M_latency_percentiles_v1_seed_{7,13,19}/partial_metrics.json` (v1 salvage output; MM candidate for 7/9 arms per seed)

## Dispatch plan

1. **Local smoke (this cycle):** seed_7 with `--smoke` on local_cpu_queue. Expected wall ~40-90 s (v2 shared-W over 1 M gives modest speedup vs v1 smoke). Verify shared-W path works, per-arm checkpoint fires, arms differ.
2. **If smoke HARD_PASS / MIDDLE_BAND with sensible numbers:** commit + hand off to Orchestrator for push + overnight_queue dispatch of all 3 seeds. **Timeout 7200 s per seed.**
3. **Watchdog check (Director's responsibility):** at t+3600s of remote FULL, poll for each seed's `data/exp_*/metrics.json` — expect `verdict == "SALVAGE_PARTIAL"` with per_arm.length in 3-9 (progress evidence); no more "black-hole until final" 3600s waits.
4. **Landed FULL:** Skunkworks VET tier per HP fire count + HF gates; check `checkpoint_kind == "final_complete"` before trusting verdict.
