# Pre-reg: stage2_dim_f_batched_qps_at_commercial_M_v1

Date: 2026-07-02
Author: hdi_exp_dev (spawned by hdi_research)
Anchor slug: `stage2_dim_f_batched_qps_at_commercial_M_v1`
Chunked seeds: 7, 13, 19 (three sibling cells; META_RULE_H CARDINALITY unit per seed)

## Motivation

Sonnet Dim F drill
(`notes/research_dim_f_throughput_scaling_batch_qps_2026-07-02.md`) established
a THEORETICAL prediction chain:

- Sequential (batch=1) QPS at M=500k on torch.cuda: ~590 QPS
  MEASURED@`data/exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v5_kernel_active_fraction_seed_7/metrics.json`
  (per-arm wall_s at M=500k REPL arm; QPS = n_queries / wall_s).
- Batch B=64 predicted QPS: ~19,000 QPS (32x speedup)
  THEORETICAL@Sonnet_drill Rank 1 batch-linear-scaling regime.
- M3 100-user shard requires 3000 QPS; sequential FAILS the requirement,
  B=32-64 batching PASSES with 6x margin THEORETICAL@Sonnet_drill.

Missing evidence: does batched dispatch actually deliver near-linear scaling?
This cell is the empirical closure. Positive result -> M3 Phase 1 deployment
at 100-user scale is viable; direct deployment-engineering answer.

## Prior work (substrate-KB concept-query, 2026-07-02)

`bash tools/substrate_query.sh "batched QPS throughput scaling streaming attention batch size dispatch"`

Top-5 hits at cosine 0.31-0.37: all generic LLM-batching notes and one
encoder-throughput pre-test. NONE measure substrate primitive batched QPS.
This cell is genuinely novel per USER substrate-KB-first discipline.

## Design

Regime: N=8192, M=500k, V=256, backend=torch.cuda, adaptive_beta per M
(reuse cortex_hippo v5 primitive `gpu_generated_streaming_readout`).

- M=500k because (a) hippo v5 chain-grade evidence exists at exactly this M
  (MEASURED@ v5 selftest gates M=500k) — anchors comparison to the sequential
  590-QPS baseline; (b) too big for M=1M on RTX 4090 without INT8 aggressive
  quant that would confound the timing-scaling measurement.
- INT8 keys enabled (matches v5 REPL arm's chain-grade condition).
- Warmup: 20 batched dispatches per condition (JIT / cudnn algo selection).
- Measurement: 200 batched dispatches per condition; report total_wall_s +
  effective_qps + per-batch p50/p95/p99 wall_s.

Swept axis: `batch_size` in {1, 4, 16, 64, 256} — 5 conditions.

CARDINALITY (META_RULE_H): EXPECTED_N_UNITS = 5 batch x 1 seed per cell x 3
cells = 15 arm-outcomes total. Per-cell (single seed) EXPECTED_N_UNITS = 5.

## Discriminator regime + AG baseline-in-band

This is a THROUGHPUT MEASUREMENT cell, not a recall/mechanism-differentiation
cell. AG (baseline_in_band 0.05-0.95) does not apply — arms differ in
throughput not accuracy. Recall must be positive-control >= 0.80 at every
batch size (proves the primitive worked at each B); if recall degrades with
B, that's an HF (batching broke the mechanism).

Declared exemption: `arms_differ_exempted: [("B=1", "B=1")]` — self-pair
trivially identical. All (B_i, B_j) pairs where i != j MUST differ in
per-batch wall_s (bit-identical arm_hash across different batch sizes = bug).

## Predicted numbers (THEORETICAL @ Sonnet Dim F drill)

- B=1:   ~590 QPS  (baseline; matches hippo v5 sequential wall_s at M=500k)
- B=4:   ~2,300 QPS (~4x)
- B=16:  ~9,000 QPS (~16x; may start showing sub-linear)
- B=64:  ~19,000 QPS (~32x; drill's central prediction)
- B=256: ~30,000 QPS (~50x; kernel-launch overhead should be amortized; may
  bump into memory bandwidth ceiling)

All numbers THEORETICAL@Sonnet_drill_Rank1. HYPOTHESIZED here in pre-reg;
MEASURED after cell lands.

## HARD_PASS (HP) gates

- **HP_BATCH_LINEAR**: `QPS(B=64) / QPS(B=1) >= 32` — near-linear scaling
  confirmed; the drill's central prediction holds.
- **HP_100USER_SHARD**: `QPS(B=64) >= 3000` — M3 100-user shard viable per
  drill's deployment threshold.
- **HP_MEMORY_CONTROLLED**: `memory_peak_mb <= 200` at B=256 — streaming keeps
  peak GPU memory M-independent even under batching (the primitive claim).
- **HP_TAIL_CONTROLLED**: `p99/p50 < 3.0` at each batch size — tail latency
  stable; no runaway outliers signaling GC/kernel-launch pathology.

## HARD_FAIL (HF) gates

- **HF_BATCH_PLATEAUS_EARLY**: `QPS(B=64) / QPS(B=1) < 8` — batch scaling
  breaks the drill prediction; deployment engineering will be harder.
- **HF_1000USER_INFEASIBLE**: `QPS(B=256) < 5000` — M3 can't scale beyond
  ~100 users on RTX 4090 without new work.
- **HF_MECHANISM_DEATH**: any batch condition `recall_cosine_mean < 0.80` —
  batching broke the substrate mechanism.
- **HF_MEMORY_BLOWUP**: `memory_peak_mb > 1000` at any B — streaming
  M-independence claim violated.
- **HF_CARDINALITY_META_RULE_H**: n_arm_outcomes != EXPECTED_N_UNITS (per seed).

MIDDLE_BAND: 8 <= QPS(B=64)/QPS(B=1) < 32 — sub-linear but useful; report
speedup honestly, deployment engineering needs adjustment.

## CRLB / feasibility

Not a noise-floor cell. `crlb_n/a: "throughput measurement; timing scaling
prediction from kernel-launch amortization theory (Little's law + batched
GEMM regime), not a signal-to-noise recovery task."`

Positive-control reachability: hippo v5 CG at M=500k REPL demonstrates the
primitive achieves recall >= 0.80 at B=1 equivalent (n_queries=200 dispatched
as a single batch). Cell must reproduce this at B=1 within tolerance 0.10 as
its FIRST arm (Gate D).

## Composition / adapter audit (Gate C)

Single primitive (gpu_generated_streaming_readout) invoked at varying
batch_size (n_queries in the spec). No composition edges. SHAPE_MATCH.

## Sweep alignment (Gate A)

Swept param `batch_size` maps directly to the primitive's `n_queries`
argument. Effective batch_size == nominal batch_size. `sweep_alignment_verdict: ALIGNED`.

## Discriminating band (Gate B)

Prediction: QPS scaling factor `QPS(B)/QPS(1)` at points {1, 4, 16, 64, 256}
predicted at {1, 4, 15, 32, 50}. Band of interest: `[8, 40]` for
speedup-vs-plateau discrimination. Points 4/15/32 (three of five) land in
band. `discriminating_fraction: 0.60`.

## Positive-control reproducer (Gate D)

Arm `B=1` at M=500k must produce recall in tolerance 0.10 of hippo v5
MEASURED value at M=500k REPL: expected recall > 0.80. This is the primitive
reproducer. If it fails, downstream batch arms are suspect.

`positive_control_arms`:
- arm: `B=1_at_M=500k_reproducer`
- primitive: gpu_generated_streaming_readout, mode=attention
- cited prior atom: hippo v5 M=500k REPL (verify at metrics_path)
- cited prior metric: recall_cosine_mean >= 0.80
- test regime: N=8192, M=500k, V=256, INT8 keys, adaptive_beta
- tolerance: 0.10
- if_outside_tolerance: `HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH`
- `regime_extension_audit`: SHAPE_MATCH (identical primitive, identical
  regime; batch size varied as n_queries within primitive's supported range)

## Functional requirements (Gate E)

- FR1: Substrate READ throughput at commercial M with batched dispatch.
  Primitive: `gpu_generated_streaming_readout` (Atom 22 LLN CG-extended;
  cortex_hippo v5 chain-grade at M=500k).
- FR2: Kernel-launch overhead amortization at batch size >= 32.
  Primitive: same; streaming architecture already amortizes launch cost per
  chunk (~488 chunks/query at chunk=1024 M=500k). Batching adds Q-axis
  amortization at query level.
- FR3: Peak GPU memory M-independence under batching. Primitive claim:
  peak GPU footprint scales with `chunk_size * (N + V) + Q * (N + V)`, not
  M. Batching multiplies the Q term. Testable via memory_peak_mb.

## Cell-template mandates

- `arms_differ_verified: true` at smoke gate (hash across B values must differ).
- `arms_differ_exempted: [("B=1","B=1")]` — trivial self-pair only.
- `final_metrics_atomicity: "tmp_replace"` (per META_RULE_AH).
- `except SystemExit: raise` before `except Exception`.
- Numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@.
- `cell_chunked: true` (3 sibling seed cells).
- `start_marker_written: true`.
- `crash_diagnostic_present: true`.
- `heartbeat_present: true` (per-condition tick).
- `progress_logging: "print_flush_true"`.
- `calibration_check: "default_ok_for_this_regime"` (adaptive_beta pass-through
  from hippo v5 primitive; matches v5 selftest gate regime; batching does not
  change the mechanism, only the dispatch pattern).
- `discriminator_reachability: true` (predicted speedup range 1x-50x at 5
  sweep points spans the discriminating band).
- `baseline_in_band: n/a` — throughput cell, not accuracy-differentiation.
- `discriminator_survives_scale: true` (measurement is AT full-N=8192,
  M=500k; the target regime, not a scaled-down proxy).

## Cardinality

`EXPECTED_N_UNITS = 5` per seed cell. FULL: 3 sibling cells * 5 = 15 units.
SMOKE: single seed=7 cell running 5 batch sizes at M=500k = 5 units (same
regime as FULL; timing measurement is by construction at full scale).

## Timeout budget

THEORETICAL estimate per seed:
- Warmup 20 + measurement 200 = 220 batched dispatches per B.
- B=1: 220 * (200 queries / 590 QPS) = ~75s.
- B=4: 220 * (batch_wall ~= 0.087s) = ~19s.
- B=16: 220 * (batch_wall ~= 0.089s) = ~20s.
- B=64: 220 * (batch_wall ~= 0.105s) = ~23s.
- B=256: 220 * (batch_wall ~= 0.30s) = ~66s.
- Overhead: primitive warmup + selftest + cell overhead ~30s.
- Total per seed: ~230s; add 5x slack for cold-cache/first-run + selftest
  gates -> 1200s ~= 20min per seed.
- Selected timeout: 3600s per seed (generous 3x above estimate; cheap
  timing cell shouldn't burn queue slot if it hangs).

## Queue

overnight_queue (GPU torch.cuda required for the primitive; INT8 keys +
kernel-active meter both cuda-only).

## Verdict logic summary

```
verdict = HARD_FAIL if any HF gate fires (memory blowup, mechanism death,
                                          cardinality breach)
        else HARD_PASS if ALL 4 HP gates satisfied (linear scaling AND
                                                    100user shard viable AND
                                                    memory controlled AND
                                                    tail controlled)
        else MIDDLE_BAND (report speedup ratio + which HP gates missed)
```
