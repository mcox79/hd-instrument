# Pre-registration: stage2_commercial_M_latency_percentiles_v1

**Date:** 2026-07-01
**Anchor base:** stage2_commercial_M_latency_percentiles_v1_seed_{7,13,19}
**Chunks:** 3 single-seed cells (seed_7 smoke first on local_cpu; seeds 13/19 dispatched full to overnight_queue on HP smoke)
**Scripts:**
- experiments/_stage2_commercial_M_latency_percentiles_v1_core.py (shared core)
- experiments/exp_stage2_commercial_M_latency_percentiles_v1_seed_7.py
- experiments/exp_stage2_commercial_M_latency_percentiles_v1_seed_13.py
- experiments/exp_stage2_commercial_M_latency_percentiles_v1_seed_19.py

**Queue:** overnight_queue (GPU) for FULL — need torch.cuda for the M3 SLA measurement. Smoke on local_cpu_queue (USER-locked 2026-07-01: no FULL on local).

**Timeout:** 3600s per seed FULL (compute: numpy at M=1M builds W in ~30-60s + 1000 queries at ~5-15ms per query = ~5-15s of measurement = ~1-2min per numpy arm; torch_cpu similar; torch_cuda per-query ~1ms so ~1s measurement + build; 9 arms total ~10-20 minutes wall; timeout 3600s adds 6x safety margin for cold cache / device transfer costs at M=1M / possible GPU contention).

## Parent + prior work (substrate-KB verified)

Substrate-KB concept-query 2026-07-01 for "commercial M latency percentiles wall time SLA cortex round-trip":

  Top-5 hits (max cosine=0.245; source_class=chunk_note):
    1. notes/research_to_exp_dev_zkl_methodology_3_pretests_AUTHORIZE_2026-06-07.md (Wall time) c=0.245
    2. notes/research_to_exp_dev_HEAD_TO_HEAD_EXTENDED_7B_70B_2026-06-11.md (Commercial framing) c=0.245
    3. notes/research_drill_substrate_speculative_decoding_5x_2026-06-09.md (7.4 Commercial value) c=0.235
    4-5. notes/research_drill_aesthetic_theory_substrate_2x_2026-06-10.md, notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md c=0.234, 0.232

**Prior-work check: NONE at cosine>0.30.** No prior cell has measured substrate cleanup-query wall-time at commercial M scales {100k, 500k, 1M} × backend {numpy, torch_cpu, torch_cuda} for the M3 Phase 1 real-time SLA question. This cell is genuinely NOVEL. Companion to `stage2_cleanup_latency_operating_curve_v1` (v1) which established M-invariance of per-query op at N=2048/8192 with alpha sweep.

**Reference cells (mechanism reuse):**
- v2c dual-readout: `exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_7.py` — established substrate cleanup mechanism (Hebbian W + sign + argmax-cleanup) and that cleanup dominates raw Hebbian.
- cleanup_latency v1: `exp_stage2_cleanup_latency_operating_curve_v1_seed_{7,13,19}.py` — established per-query op is O(N^2) constant in M/alpha at (N=2048, N=8192). This cell CONFIRMS that finding at commercial-M and adds the torch.cuda backend measurement critical for M3 SLA.
- hippo v5 commercial: `exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v5_kernel_active_fraction_seed_{7,13,19}.py` — validated commercial-M substrate at N=8192 with M ∈ {100k, 500k, 1M} on GPU.

## Hypothesis (M3 Phase 1 SLA baseline)

M3 cortex layer will make per-turn routing decisions that include a substrate lookup + cleanup as a subroutine. To promise **real-time** conversational response at commercial scale, we need to characterize p50/p95/p99 wall latency of the full cortex round-trip cleanup at M ∈ {100k, 500k, 1M} for each backend M3 might deploy on.

**Predicted structural findings:**

Per-query op is `q @ W.T` — O(N^2) in N, INDEPENDENT of M (only W-build depends on M). Confirmed by cleanup_latency v1 CG (cv < 10% across alpha sweep at fixed N). We predict this M-invariance holds at N=8192 commercial-M regime.

- **HYPOTHESIZED@this_prereg** (from cleanup_latency v1 CG): numpy p50 at M=1M ≈ numpy p50 at M=100k (per-query op M-independent). Ratio in [0.5, 5.0].
- **HYPOTHESIZED@this_prereg** (from hippo v5 commercial + BLAS-GPU FLOP scaling): torch.cuda p50 at N=8192, M=any commercial in {~0.1-5 ms} range (single 8192×8192 matmul on modern GPU is ~1e8 FLOPs / ~10 TFLOP/s = 10 us; measured wall dominated by kernel-launch + sync overhead, ~0.1-1 ms).
- **HYPOTHESIZED@this_prereg**: torch.cuda beats numpy at M=1M by >2× (HP threshold 0.5×). At smaller M numpy might be competitive due to launch overhead.
- **HYPOTHESIZED@this_prereg** (from cleanup_latency v1 measured): numpy p50 at N=8192 ~15ms (cleanup_latency v1 seed_7 preview arm MEASURED@data/exp_stage2_cleanup_latency_operating_curve_v1_seed_7/metrics.json: preview p50 = 14357us at N=8192 alpha=3.0).
- **THEORETICAL@perf_counter monotonic ns**: noise floor of the timer is negligible vs measured p50 (100 ns << 100 us minimum expected).

**M3 SLA verdict rule:**
- If `HP_M1M_UNDER_100MS` fires: M3 can promise real-time (< 100 ms per query) substrate lookup at M=1M with torch.cuda backend.
- If it doesn't fire but numpy is < 1 s at M=1M: M3 must batch/chunk/downsample OR use GPU-mandatory deployment.
- If `HF_M1M_INFEASIBLE` fires: substrate cannot serve commercial-M real-time; M3 must use approximate/partition-routed lookup.

## Design

**Latency grid (FULL):**
- N = 8192 (fixed; M3 baseline)
- M ∈ {100_000, 500_000, 1_000_000}
- backend ∈ {numpy, torch_cpu, torch_cuda}
- 3 × 3 = 9 arms per seed
- WARMUP_QUERIES = 100; N_QUERIES = 1000 recorded per arm
- 3 seeds ({7, 13, 19}) via chunked single-seed cells

**Cardinality (META_RULE_H):** EXPECTED_N_UNITS = 9 per seed. `cardinality_ok = true` if `len(per_arm) >= 9` (backends without CUDA still produce an arm-row marked `arm_status = UNAVAILABLE`, which counts toward cardinality but is excluded from HP evaluation).

**Query op:** `cleanup_query_<backend>(q, W, target_val_n, probe_n) -> (hit, target_cos)` — identical mechanism to v2c and cleanup_latency v1.
  - numpy: `np.sign(q.astype(f32) @ W.T)`; norm+dot for target_cos.
  - torch_cpu: same via torch tensor ops.
  - torch_cuda: same but with `torch.cuda.synchronize()` before AND after so wall time captures full kernel completion (not launch-only).

**Streaming W build:** never materialize >4096 rows of keys/vals at once. Cost ~O(M × N) build FLOPs but only ~4096×N = 32M floats resident at a time (~256 MB at f64). W itself is N×N f32 = 8192×8192 × 4 B = 256 MB.

**Smoke design (Discriminator-must-survive-scale pattern A + C):**
- FULL N=8192 KEPT at smoke (not shrunk) — the discriminator is per-query wall time and it depends on N.
- Single M = 100k (already commercial regime; drops 500k and 1M).
- Two backends (numpy + torch_cpu) + one PREVIEW torch_cuda arm at M=100k.
- N_QUERIES = 50 (enough for stable p50; too few for stable p99 — smoke reports numbers, not full verdict).
- Smoke discriminator-fires check: cross-backend hash divergence (arms differ; not bit-identical) + at least one measured p50 > 10 µs (not sub-timer-resolution).
- Smoke expected wall: numpy M=100k W-build ~5-10s, per-query ~15ms × 50 = ~1s; torch_cpu similar; PREVIEW cuda ~1-5s total. Estimated smoke total wall ~30-60s on local_cpu (no CUDA); ~10-30s on runner with CUDA.

## HP / HF gates (envelope + fail bands)

**HP gates (5 defined; evaluated only when applicable arms present):**

- `HP_M1M_UNDER_100MS`: at (M=1M, backend=torch_cuda) p50_s < 0.100. Applicable iff CUDA arm ran.
- `HP_M100K_UNDER_10MS`: at (M=100k, backend=torch_cuda) p50_s < 0.010. Applicable iff CUDA arm ran.
- `HP_TAIL_CONTROLLED`: for ALL OK arms, p99_s / p50_s < 3.0. Always applicable (need >=1 OK arm).
- `HP_NUMPY_SCALES_INVARIANT`: numpy p50 at M=1M / numpy p50 at M=100k ∈ [0.5, 5.0]. Applicable iff both numpy arms ran. Confirms per-query op is M-invariant (per cleanup_latency v1 CG finding).
- `HP_CUDA_SPEEDUP`: torch_cuda p50 at M=1M < 0.5 × numpy p50 at M=1M. Applicable iff both arms ran.

**HF gates:**
- `HF_M1M_INFEASIBLE`: any backend p50_s > 1.0 at M=1M — commercial-M cortex latency budget blown.
- `HF_TAIL_EXPLOSION`: p99_s / p50_s > 100 anywhere — heavy-tail pathology.
- `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`: `len(per_arm) < EXPECTED_N_UNITS`.
- `HARD_FAIL_META_RULE_AF_BIT_IDENTICAL`: any two OK arms produce identical timings_hash.

**Verdict roll-up:**
- `hp_denom` = number of HP gates that evaluated to True/False (n/a excluded).
- `hp_true` = count that fired.
- If any HF fires → `HARD_FAIL`.
- Else if `hp_true == hp_denom` (all evaluable HP fired) → `HARD_PASS`.
- Else if `hp_true >= hp_denom - 1` AND `hp_denom >= 3` → `HARD_PASS` (edge case: 4/5).
- Else if `hp_true >= max(1, hp_denom / 2)` → `MIDDLE_BAND`.
- Else → `MIDDLE_BAND`.

## SCHEMA-VET checklist (META_RULE_H/J/K/L/M/AC/AF/AG/AH)

- `cardinality_ok`: **true** — EXPECTED_N_UNITS = 9 (full) / 3 (smoke) counted; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H fires if breached.
- `per_unit_failure_class`: **true** — per-arm `failure_class` populated on Exception; UNAVAILABLE state distinguished from FAILED for CUDA-absence.
- `discriminator_fires`: **true** — smoke includes CUDA preview arm at M=100k; smoke arms-differ hash verified.
- `strictly_above_floor`: **true** — HP thresholds are hard numbers (100 ms / 10 ms / 3.0 / [0.5, 5.0] / 0.5×), not `>= floor`.
- `HP_SCOPE`: HP_M1M_UNDER_100MS & HP_M100K_UNDER_10MS scoped to torch_cuda arms only. HP_TAIL_CONTROLLED applies to ALL OK arms. HP_NUMPY_SCALES_INVARIANT & HP_CUDA_SPEEDUP scoped to numpy / torch_cuda ratio arms.
- `calibration_check`: `default_ok_for_this_regime` — `time.perf_counter()` is monotonic ns-resolution; `torch.cuda.synchronize()` before AND after ensures kernel completion; no adaptive tuning.
- `arms_differ_verified`: **true** — SHA256 of concatenated timings + (M, N, backend-hash) per arm; verdict checks uniqueness.
- `final_metrics_atomicity`: `tmp_replace` — write `metrics.json.tmp`, `os.replace` to final.
- `except_ordering`: `SystemExit -> KeyboardInterrupt -> Exception` (no BaseException) in main; per-arm try wraps only Exception + distinguishes availability errors from real failures.
- `crlb_n/a`: latency measurement; noise floor = perf_counter resolution (~ns). HP thresholds are policy targets not statistical estimates; no CRLB applies. Declared explicitly per META_RULE_L / capacity-feasibility rule.
- `discriminator_reachability`: **true** — HP thresholds achievable (100 ms is ~1000× a single 8192×8192 matmul on GPU; 10 ms similarly).
- `baseline_in_band`: N/A — this is a latency measurement, not accuracy. All arms measure timing; discriminator is arms_differ + measurement_real.
- `progress_logging`: `print_flush_true` — every 200 queries prints progress; `sys.stdout.reconfigure(line_buffering=True)` at cell start.
- `cell_chunked`: **true** — 3 single-seed cells.
- `start_marker_written`: **true** — `_write_start_marker` at core `run_seed` entry.
- `crash_diagnostic_present`: **true** — `_write_crash_metrics` in seed wrapper `main()`.
- `heartbeat_present`: **true** — `emit_heartbeat` per-arm start + per-arm-complete.
- `defensive_error_checking`: `passed_all_4_patterns`.

## §15 gates (test-design failure prevention)

- **A) effective_vs_nominal_parameter_audit:** ALIGNED. `M` is a nominal sweep axis; `M` also determines the effective number of items stored in W. W is built from M outer products, so effective M = nominal M. No sweep-vs-primitive misalignment.
- **B) bracket_includes_discriminating_band:** N/A for latency (no accuracy band). Instead the equivalent is: HP thresholds are in the reachable region per HYPOTHESIZED numbers above (predicted CUDA p50 ~0.1-5 ms vs threshold 100 ms = well below; predicted numpy p50 ~15 ms M-invariant vs threshold [0.5×, 5×] = expected inside band). `discriminating_fraction = 1.0` (all sweep points expected to yield measurable percentiles).
- **C) signal_shape_compatibility_audit:** cleanup_query_<backend> is a single-primitive per-arm measurement; no composition. `verdict: SHAPE_MATCH` (numpy array → sign → dot; torch tensor → sign → dot; equivalent).
- **D) reproduce_prior_chain_grade_result_as_positive_control:** cleanup_latency v1 CG at N=8192, alpha=3.0 (M=24576), backend=numpy: MEASURED@data/exp_stage2_cleanup_latency_operating_curve_v1_seed_7/metrics.json p50 ~ 14 ms. This cell's numpy arm at (N=8192, M=100k) should show p50 in same ballpark (M-invariant hypothesis). Tolerance: 3× (accept anywhere in [5, 45] ms; wider than 0.10 because the reference alpha=3 M=24576 vs our M=100k differs; if M-invariant, must be roughly same). If OUTSIDE, HP_NUMPY_SCALES_INVARIANT likely fails, which is the actual test.
- **E) functional_requirement_decomposition_present:** Functional requirement — "M3 Phase 1 must decide the per-turn substrate lookup timing budget at commercial scale." Mapping: substrate cleanup query = existing chain-grade primitive (v2c dual-readout + cleanup_latency v1). This cell adds a scale + backend measurement not previously done.

## Files

- `experiments/_stage2_commercial_M_latency_percentiles_v1_core.py`
- `experiments/exp_stage2_commercial_M_latency_percentiles_v1_seed_7.py`
- `experiments/exp_stage2_commercial_M_latency_percentiles_v1_seed_13.py`
- `experiments/exp_stage2_commercial_M_latency_percentiles_v1_seed_19.py`
- `preregs/2026-07-01_stage2_commercial_M_latency_percentiles_v1.md` (this file)

## Dispatch plan

1. Smoke (this cycle): `local_cpu_queue` seed_7 with `--smoke`. Expected wall ~30-60s. Verify arms differ, at least one measured p50 > 10 µs, no HF.
2. If smoke HARD_PASS or MIDDLE_BAND (with sensible timing numbers): commit + hand off to Orchestrator for `overnight_queue` dispatch of all 3 seeds (GPU needed for torch_cuda arm; seed_7/13/19 in parallel).
3. Landed FULL: Skunkworks VET tier per HP fire count + HF gates.
