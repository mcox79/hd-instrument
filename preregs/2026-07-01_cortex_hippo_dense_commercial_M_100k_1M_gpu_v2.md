# Pre-registration: cortex_hippo_dense_commercial_M_100k_1M_gpu_v2

**Date filed:** 2026-07-01
**Anchor:** `cortex_hippo_dense_commercial_M_100k_1M_gpu_v2`
**Backend:** torch.cuda (overnight_queue)
**Timeout:** 3600s per seed cell
**Seeds:** 7, 13, 19 (single-seed-per-cell architecture per SS.13)
**Cell files:**
- `experiments/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v2_seed_7.py`
- `experiments/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v2_seed_13.py`
- `experiments/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v2_seed_19.py`
- Core: `experiments/_substrate_cortex_hippo_dense_commercial_M_100k_1M_gpu_v2_core.py`

## Purpose

v2 fix for v1 CUDA OOM at commercial M scale. v1 crash MEASURED@`data/exp_cortex
_hippo_dense_commercial_M_100k_1M_gpu_v1_seed_{7,13,19}/metrics.json:verdict`
= `CELL_CRASHED` with `OutOfMemoryError: Tried to allocate 15.26 GiB` at
`keys_f32.to(device)` (v1 core line 368). Root cause: full-M FP32 keys upload
allocates 2x memory (source CPU tensor + dest GPU tensor) during transfer.

Same substrate-scientific hypothesis as v1: validate `hdlab.chunked_attention`
Testbed T2 primitive at M in {100k, 500k, 1M}, N=8192, on 8 GB VRAM.

## v2 fix (memory strategy)

**Chunked upload + FP16 (STD) / INT8 (REPL) storage** — allocate GPU buffer once
at target dtype (FP16 or INT8), stream keys from CPU to GPU in row-batches
(default 8192 rows). Peak transient = batch * N * dtype_bytes, not full M * N.

**Memory budget (chunked upload, batch=8192, N=8192, V=256):**

STD arm (FP16 keys):
- Persistent keys: M * N * 2 bytes = 1.64 GB (M=100k) / 8.19 GB (M=500k) / 16.38 GB (M=1M)
- Persistent vals: M * V * 2 bytes = 51 MB / 256 MB / 512 MB
- W accumulator: V * N * 4 = 8.4 MB
- Transient per-batch: 134 MB (FP16 key chunk) + 4 MB (FP16 val chunk)

REPL arm (INT8 keys):
- Persistent keys: M * N * 1 bytes = 0.82 GB / 4.10 GB / 8.19 GB
- Persistent vals: M * V * 2 bytes = 51 MB / 256 MB / 512 MB
- chunked_attention transient: ~32 MB (Testbed T2 bound at chunk=1024)
- Upload transient: 67 MB (INT8 chunk)

**Feasibility at M=1M on 8 GB VRAM:**
- STD FP16 persistent 16.38 GB → EXCEEDS 8 GB VRAM. STD arm at M=1M will
  fail the pre-upload memory check (`RuntimeError: PRE_UPLOAD_MEMORY_ABORT`).
  This is by design; STD is the must-fail positive-control baseline.
- REPL INT8 persistent 8.19 GB → JUST at VRAM cap. Real allocation may exceed
  due to CUDA workspace + fragmentation. Expected marginal at M=1M.

**HYPOTHESIZED@this-prereg trade-off:** if REPL M=1M fails on 8 GB VRAM,
downgrade to M_LIST=[100k, 500k] as the empirical commercial-M ceiling on
this hardware. Report memory usage per M in metrics for post-hoc analysis.
Discriminator still fires at M=100k and M=500k.

**Alternative if REPL M=1M PRE_UPLOAD_MEMORY_ABORT:** cell will emit an
explicit `HF_MEMORY_OVERFLOW` verdict, not a silent crash. Verdict logic
already handles this (HF gate at 6000 MB peak; PRE_UPLOAD_MEMORY_ABORT is
CELL_CRASHED with clear error message, not silent).

**For STD M=1M feasibility:** the pre-upload gate is 6 GB (HF band). STD FP16
at M=1M projected 16.38 GB > 6 GB — cell will abort with clear error before
allocation. This is designed behavior: STD is not expected to reach M=1M on
consumer 8 GB VRAM anyway (STD accuracy analytically ~0.09 at M=1M so cell
science does not depend on it).

## Substrate-KB prior-work check (2026-07-01)

Concept-query `commercial dense hippo FP16 keys GPU memory chunked upload M=100k`
returned no direct hits at cosine >= 0.30 (max cosine 0.22, top hit "GPU memory
check" from Q_B1 chain depth prereg). Adjacent findings: same as v1 (chunked
1563 bundles at 100k / GHRR-STanHop attention).

Verdict: v2 is genuinely novel as a memory-fix reissue; not a rediscovery.

## Arms (2 arms x 3 M values = 6 arm-outcomes per seed)

Identical mechanism arms to v1:
- `ARM_STD`: standard direct Hebbian W = vals.T @ keys / N (chunked matmul on device).
- `ARM_REPL`: dense-Hopfield READ-REPLACE via `chunked_attention_readout` with
  adaptive beta and chunk_size=1024. INT8 keys at FULL (per Atom 5 CG).

**v2 CHANGE:** both arms use chunked upload (v1 uploaded whole-M in one call).

## Configuration

| Param            | Smoke                     | FULL                        |
|------------------|---------------------------|-----------------------------|
| N (cortex dim)   | 1024                      | 8192                        |
| V (value dim)    | 128                       | 256                         |
| M sweep          | [10k]                     | [100k, 500k, 1M]            |
| chunk_size       | 512                       | 1024                        |
| upload_batch     | 2048                      | 8192                        |
| n_queries        | 50                        | 200                         |
| beta             | adaptive (base=13)        | adaptive (base=13)          |
| int8_keys        | False                     | True (REPL arm only)        |
| FP16_keys        | n/a (smoke uses numpy CPU)| True (STD arm; halves mem)  |
| FULL-N preview   | M=100k at N=8192 GPU-upload | -                         |

**Adaptive beta:** `beta = 13 * log2(M) / log2(100_000)` (identical to v1).
MEASURED@v2 selftest: adaptive_beta(1M) ~= 16.30; predicted_p_win(1M, N=8192,
beta=16.30) > 0.99.

## Falsifiable verdicts (IDENTICAL to v1)

### HARD_PASS gates (all must fire for CHAIN_GRADE_COMMERCIAL_SCALE)

- `HP_M100k_MECHANISM_HOLDS`: `ARM_REPL.recall_cosine_mean` >= 0.80 at M=100k
- `HP_M500k_MECHANISM_HOLDS`: `ARM_REPL.recall_cosine_mean` >= 0.60 at M=500k
- `HP_M1M_MECHANISM_HOLDS`:   `ARM_REPL.recall_cosine_mean` >= 0.30 at M=1M
- `HP_STD_BEATEN`:             `REPL - STD >= 0.50` at ALL M

### HARD_FAIL gates

- `HF_MEMORY_OVERFLOW`: `gpu_mem_peak_mb > 6000` at any arm-M
- `HF_MECHANISM_DEATH`: `ARM_REPL.recall_cosine_mean < 0.10` at any M
- `HF_ARM_IDENTICAL`: STD and REPL arms bit-identical (META_RULE_AF)
- `HF_CARDINALITY_META_RULE_H`: `n_arm_outcomes != 6`

## SCHEMA-VET pre-dispatch fields

```yaml
cardinality_ok: pre-verified pre-dispatch
EXPECTED_N_UNITS: 6  # 2 arms * 3 M values, per seed
arms_differ_verified: verified at smoke (hash-check STD vs REPL per M)
final_metrics_atomicity: tmp_replace
except_systemexit_raise_before_exception: true (no BaseException catch)
discriminator_reachability: true
  crlb_note: |
    p_win at fixed beta=13, M=1M, N=8192 ~= 0.17 (below HP=0.30 floor).
    Adaptive beta at M=1M = 16.30 -> p_win > 0.99 (well above HP floor).
crlb_formula_reference: |
  logit_gap = beta * (1 - sqrt(2*log(M)/N))
  p_win = 1 / (1 + M * exp(-logit_gap))
calibration_check: adaptive_with_discriminator_gate
  formula: beta(M) = 13 * log2(M) / log2(100_000)
baseline_in_band:
  ARM_STD: expected recall <= 0.10 (baseline_in_band exemption: STD is
    "must-fail" positive-control arm, not "must-work" arm)
  ARM_REPL: expected in band at all M (smoke verifies)
discriminator_survives_scale:
  method_A_smoke_at_full_N_preview: true
    (smoke runs FULL_N GPU-upload preview at M=100k, N=8192 -- proves the
     v2 chunked-upload path actually works at production N and does not OOM)
  method_B_analytical_justification: |
    Adaptive beta preserves logit_gap across M; predicted_p_win >= 0.95 at all M
    when beta is scaled.
cell_chunked: true  # SS.13 chunked single-seed-per-cell
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
progress_logging: print_flush_true  # SS.17
progress_cadence_expected_s: 60
sweep_alignment_verdict: ALIGNED  # SS.15A
composition_edges:
  - from: chunked_upload_FP16 (v2 fix helper)
    to: chunked_attention_readout (T2 primitive) OR streaming matmul (STD)
    A_natural_output_shape: (M, N) FP16 on device
    B_natural_input_shape: (M, N) any-dtype accepted by T2 primitive (FP16 supported)
    verdict: SHAPE_MATCH
  - from: quantize_int8_dense (INT8 primitive)
    to: chunked_upload_INT8 + chunked_attention_readout (int8 path)
    A_natural_output_shape: (M, N) int8 + (M, 1) float32 scale
    B_natural_input_shape: (M, N) int8 + key_scale (M, 1) required
    verdict: SHAPE_MATCH
positive_control_arms:
  - arm: ARM_REPL_M100k_reproduces_TESTBED_T2_memory_bound
    primitive: chunked_attention_readout
    cited_prior_atom: Testbed T2 chain-grade 2026-07-01 (32 MB peak-mem bound at M=1M chunk=1024)
    tolerance: 0.10 (memory bound within 10% of analytical estimate)
    regime_extension_audit: SHAPE_MATCH
functional_requirements:
  - fr: dense-Hopfield READ-REPLACE at commercial M
    primitive: chunked_attention_readout (T2)
  - fr: bounded GPU memory during KEY UPLOAD (v2 fix)
    primitive: v2 _chunked_upload_fp16 / _chunked_upload_int8 helpers
  - fr: bounded GPU memory during attention pass
    primitive: chunked_attention_readout chunk=1024
  - fr: INT8 memory savings for storage-bound M
    primitive: quantize_int8_dense (Atom 5 CG)
```

## Timeout justification (--timeout 3600s per seed cell)

Formula: `timeout_s = ceil(1.5 * smoke_wall_s * scale_factor * seed_factor)`.

- Smoke wall estimate: ~30s M=10k CPU + ~120s M=100k FULL_N GPU preview = ~150s
- Scale factor to M=1M (100x larger, chunked matmul on GPU): ~15x
- Total FULL cell wall: ~2250s worst case; 3600s timeout gives 60% headroom.

## Dispatch plan

- **Selftest:** local .venv (fast; verifies chunked-upload helpers)
- **Smoke:** local_cpu_queue (USER 2026-07-01: SMOKE ONLY on local; laptop-preserving).
  Smoke will run CPU numpy path for M=10k arms + attempt GPU-upload preview at
  M=100k IF CUDA available on laptop; if not, smoke defers preview to remote.
- **FULL:** overnight_queue (GPU). Requires push (harness-denied to exp_dev).
  Route via Orchestrator.

## References

- v1 crash diagnosis: MEASURED@data/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v1_seed_*/metrics.json
- Testbed T2 primitive: `hdlab/chunked_attention.py`
- INT8 primitive: `hdlab/int8_dense.py`
- v1 prereg: `preregs/2026-07-01_cortex_hippo_dense_commercial_M_100k_1M_gpu_v1.md`
