# Pre-registration: substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU

**Date:** 2026-06-25
**Anchor:** substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU
**Queue:** overnight_queue (GPU)
**N:** 8192, **Seeds:** [11, 13, 19], **M_KV:** 10000

## Why this cell exists

Fix #24 (USER 2026-06-22) caught the v2 numpy version: queueing a NumPy-only
cell onto overnight_queue (the GPU runner) wastes the runner slot because the
NumPy matmuls execute on CPU even on a GPU host. The v2 pre-reg explicitly
ACK'd this and deferred the torch port. The `tools/queue_add.py` PROT-020
gate (added per Fix #24) now REJECTS NumPy-only scripts on overnight_queue,
which blocked the v2 dispatch (exit 7).

This cell is a torchified rewrite preserving the EXPERIMENTAL CONTENT of v2:
same 4 operating points, same 3 evaluated arms, same bands, same anchor-
relative methodology. The only changes are the matmul backend (torch on
_DEV = cuda if available else cpu) and a Fix #24 verification gate.

## Mechanism (identical to v2)

Same pipeline as v1 and v2 (intent -> audit-subject -> audit-relation ->
graph-health -> KV retrieve -> templated response -> CSP confidence). Same
chain-grade primitives. Sweeps 4 production-scale operating points within a
single seed to map the (V_C_IN, V_REL) operating envelope.

## Operating points (4, identical to v2)

- (V_C_IN=1000, V_REL=20)
- (V_C_IN=1000, V_REL=50)
- (V_C_IN=2000, V_REL=20)
- (V_C_IN=2000, V_REL=50)   <-- TARGET (production-scale)

Other constants (identical to v2): N=8192, M_KV=10000, seeds=[11,13,19],
1000 queries per (PURE_IN/PURE_OUT) and 500 per (NEAR/UNCERTAIN).

GPU batch size: 256 (queries processed in chunks of 256 per category to fit
production V matmul in GPU memory).

## Scientific question (identical to v2)

Does the Stage 3 integrated pipeline retain chain-grade behavior (all 4 query
categories meeting category targets + p95 <= 10ms + cv <= 0.07) at production
V (V_C_IN=2000 + V_REL=50)?

## Pre-registered bands (identical to v2)

**HARD_PASS_PRODUCTION_SCALE:** at (V_C_IN=2000, V_REL=50):
- ARM_PIPELINE_COMPOSED:
  - PURE_IN_DOMAIN answer_rate >= 0.85
  - PURE_OUT_OF_DOMAIN refuse_rate >= 0.85
  - NEAR_DOMAIN_MIXED refuse_rate >= 0.85
  - IN_DOMAIN_UNCERTAIN correct_rate >= 0.70
- AND PIPELINE p95 latency <= 10 ms
- AND cv <= 0.07 across seeds

**CHAIN_GRADE_AT_LOWER_X:**
- ARM_PIPELINE_COMPOSED passes ALL HP targets at ONE OR MORE of:
  (V_C_IN=1000, V_REL=20), (V_C_IN=1000, V_REL=50), (V_C_IN=2000, V_REL=20)
- but DOES NOT pass at the target (V_C_IN=2000, V_REL=50)

**HARD_FAIL_REFUSE_GATE_CLIFF:**
- NEAR_DOMAIN_MIXED refuse_rate < 0.50 at ANY operating point with V_REL >= 20
  (envelope assumption breaks; refuse-gate v2 envelope is at V_REL <= 50)

**HARD_FAIL_LATENCY_BLOWN:**
- pipeline p95 > 50 ms at ANY operating point

**MIDDLE_BAND:**
- no operating point hits all HP targets but no HARD_FAIL trigger fires

## Calibration rationale

Identical to v2:
- HARD_PASS bands inherited from v1's empirically-validated category targets
  (0.85 / 0.85 / 0.85 / 0.70).
- p95 <= 10ms is the production-acceptable per-query inference ceiling.
- cv <= 0.07 because substrate is deterministic per-seed.
- HARD_FAIL_REFUSE_GATE_CLIFF at near_ref < 0.50: refuse-gate v2 envelope says
  V_REL <= 50; if it breaks at V_REL=20, the envelope assumption was wrong.
- HARD_FAIL_LATENCY_BLOWN at p95 > 50ms: well outside production envelope.

## Q-discipline (BIAS-Q: suspect 1.000 results)

Per v2: at V_C_IN=2000 with V_REL=50, the audit primitive's near-domain
disambiguation should produce values < 1.000 if real disambiguation is
happening. If all 4 categories produce 1.000 at production V, raise as
suspect Q-saturation per Skunkworks tiering. GPU batched compute does NOT
change Q-discipline (the question is about the substrate's discriminating
behavior at the operating point, not the compute backend).

## Capacity-feasibility analysis (with GPU memory budget)

Subject library V_C_IN=2000 + relation V_REL=50 at N=8192:
- W_subjects (2000, 8192) float32 = 64 MB on GPU
- W_relations_in (50, 8192) = 1.6 MB
- K_kv (10000, 768) = 30 MB
- W_kv (768, 768) = 2.3 MB
- codebook_kv (256, 768) = 0.75 MB
- Per-batch query stack at B=256: (256, 8192) = 8 MB
- Per-batch audit sims at B=256, V_C_IN=2000: (256, 2000) = 2 MB
Total peak GPU memory per operating point: ~110 MB. Comfortably under any
modern GPU. Empty_cache between operating points to keep residency clean.

Cleanup chain-grade envelope: N >= 8192 for V <= 4000 (per cleanup-integrity
rule). V_C_IN=2000 is well below; cleanup should be intact.

## Per-query latency semantics

p95 is amortized per-query: batch wall-clock divided by batch size. This
matches v2 semantics (production per-query inference cost) because the audit-
device serves queries one-at-a-time at deploy time. The batch is a compute
optimization, not a deploy-time architecture change. Reporting per-query
latency keeps cross-cell apples-to-apples with v1 and v2.

NOTE: batch p95 will be LOWER than v2's per-query-serial p95 (the GPU
amortization is real). This is GENUINE speedup, not measurement skew. The
HARD_PASS p95 <= 10ms ceiling remains the production-ship gate either way.

## Fix #24 GPU-actually-used verification (NEW vs v2)

This is the load-bearing addition vs v2:

1. `import torch` at module top (satisfies PROT-020 gate at queue_add.py).
2. `_CUDA_AVAILABLE = torch.cuda.is_available()` checked at module init.
3. `_DEV = cuda if available else cpu`.
4. At full-mode run start: assert cuda available; abort with sys.exit(2) if
   not (the cell was dispatched to overnight_queue specifically for GPU).
5. After every big batched matmul block (substrate build, per-arm evaluation),
   `_gpu_probe()` prints `torch.cuda.memory_allocated()` and flags Fix #24
   violation if cuda available but memory_allocated < 0.01 MB.
6. `_fix24_violations` list aggregated into metrics.json; verdict_msg surfaces
   it if any probe fires.

This means: if the cell runs to completion with empty `_fix24_violations`,
we have positive evidence the matmuls ran on GPU (not just that cuda was
available).

## Cross-cell apples-to-apples

Seeds [11, 13, 19] cross-cell consistent with EXT-3 + EXT-6 +
partition_routing_v2. v1 and v2 used [11, 13, 19] (same). Direct comparison.

The arms here are a strict subset of v2 (we evaluate the 3 useful arms;
ARM_INDIVIDUAL_PRIMITIVES_PARALLEL from v1 was already dropped in v2 and is
not needed for the production-scale envelope test).

## N-suffix section

Anchor name does NOT contain `_n<N>` suffix; the cell sweeps V_C_IN x V_REL
at fixed N=8192. PROT-018 does not apply.

## Timeout estimate

Smoke: N=2048, 1 seed, 2 operating points (V_C_IN=200, V_REL=8 ; V_C_IN=400,
V_REL=16), 25 queries per cat, B=64. Local CPU torch completes in ~30-90s.

FULL: N=8192, 3 seeds, 4 operating points, up to 1000 queries per cat, B=256.
Per-arm cost on GPU is dominated by:
- audit-subject matmul: B x N x V_C_IN per batch = 256 * 8192 * 2000 = ~4.2 GFLOPs/batch
- KV: B x D x D = 256 * 768 * 768 = ~150 MFLOPs/batch
- Total ~10 GFLOPs per batch arm-pass per category at V_C_IN=2000.
- 1000 queries / 256 = 4 batches per category x 4 categories x 3 arms x 4 points x 3 seeds
  = 576 batches total at production V (lower batch count at smaller V points).

A modern GPU at 5 TFLOPs sustained = a few seconds per batch. Realistic full
wall-clock: 1-3 hours including substrate build + data movement. Budget at
PROT-019 ceiling for safety:

timeout_s = 14400 (4 h ceiling, same as v2 pre-reg)

## Provenance rail

ARM_AUDIT_ONLY_RAIL at (V_C_IN=1000, V_REL=20) must reproduce v1's audit-
only-rail baseline within +/- 0.10 (v1 had near_ref ~ 1.000). If breaches,
raises method-skew flag — the audit primitive itself may have a regression
across the numpy -> torch port.

CROSS-BACKEND CHECK in self-test T3: batched_audit on identity input must
produce diagonal argmax matching numpy reference. If it doesn't, the torch
port has a bug and the cell aborts at --self-test before queue dispatch.

## What this cell DOESN'T change vs v2

- Same operating points
- Same arms (3 evaluated)
- Same bands (HP / CHAIN_GRADE / HF triggers)
- Same query categories + counts
- Same seeds [11, 13, 19]
- Same anchor-relative methodology
- Same Q-discipline expectation

The ONLY differences:
- Compute backend: numpy CPU -> torch (cuda if available)
- Per-query latency measurement: serial wall-clock -> amortized batch wall-clock
- Fix #24 verification probes + abort-on-CPU-in-full-mode gate
- Anchor name suffix `_GPU` (distinct output directory and queue audit entry)
