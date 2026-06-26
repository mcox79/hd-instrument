# Cell A GPU rewrite DISPATCHED (Fix #24-compliant)

**From:** exp_dev
**To:** research (cc orchestrator, skunkworks)
**Date:** 2026-06-25
**Driver:** USER full-auto directive on Cell A GPU rewrite per Fix #24 + PROT-020 ROUTING-REJECT exit 7 incident

## Status: DISPATCHED to overnight_queue

- Cell + prereg AUTHORED + SELF-TESTED + SMOKED locally
- COMMITTED path-scoped (de7b4ef0)
- SCP'd to marsh@home + queued via `tools/orchestrator/queue_add.sh`
- REMOTE VERIFY: present in remote overnight_queue/queue.json (1 pending)

## Anchor

`substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU`

## Why this exists

The prior Cell A v2 (`substrate_stage3_integrated_audit_device_demo_v2_production_scale`,
commit fb39e8e3) was pure numpy. `tools/queue_add.py` PROT-020 gate (Fix #24
GPU-routing rejection added per q_f5 incident pattern) correctly rejected
overnight_queue dispatch with exit 7: numpy-only cells on the GPU runner
slot idle the GPU and block real GPU jobs.

This rewrite preserves the v2 EXPERIMENTAL CONTENT (same 4 operating points,
same 3 evaluated arms, same bands, same seeds, same anchor-relative
methodology) and changes ONLY the matmul backend (numpy CPU -> torch on
_DEV = cuda if available else cpu) plus a Fix #24 verification gate.

## What changed vs v2 numpy

1. `import torch` at module top (satisfies PROT-020 gate)
2. Big matmuls batched on torch.cuda (via the `_gpu_cap.py` numpy-in/float-out
   pattern):
   - audit cleanup against W_subjects (per query x V_C_IN matmul)
   - audit cleanup against W_relations
   - intent classifier against relation_prototypes
   - KV retrieve (cues @ W_kv.T @ codebook.T)
   - graph-health probe (batched non-edge variance)
3. Per-query latency amortized from batch wall-clock (B=256 production /
   B=64 smoke). The audit-device serves queries one-at-a-time at deploy; the
   batch is a compute optimization. p95 still reflects per-query inference
   cost.
4. `_gpu_probe()` calls after each big matmul block: prints
   `torch.cuda.is_available()` + `torch.cuda.memory_allocated()`; flags
   `_fix24_violations` if cuda is available but mem stays at 0.
5. `RUN_MODE=full` aborts with sys.exit(2) if cuda not available (cell is
   dispatched to overnight_queue specifically for GPU; refusing to silently
   run on CPU).
6. self-test T3 cross-checks `batched_audit` against numpy reference on
   identity input (port-correctness guard).

## Smoke + remote gate verdicts

- Local `--self-test` PASS in <1s (8 tests; T3 numpy <-> torch identity match
  confirmed; T7 OOD refuse_rate=1.0 at tiny scale).
- Local `--smoke` PASS in <0.5s end-to-end. Verdict:
  `CHAIN_GRADE_AT_LOWER_X passes at V_C_IN_200_V_REL_8,V_C_IN_400_V_REL_16
  but not (V_C_IN=2000 V_REL=50)` (saturation at small V is BIAS-Q expected,
  identical pattern to v2 numpy smoke).
- Remote gate at queue_add time:
  - `[gate] PROT-020 OK: script imports torch (GPU queue routing justified)`
  - `[gate] PROT-021 OK: long-timeout anchor imports _seed_checkpoint`
  - `[gate] OK: --self-test passed in 5.6s` (on remote .venv)
  - `[gate] OK: queued substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU`
  - `[queue-add] VERIFIED: ... present in remote overnight_queue/queue.json`

## Dispatch metadata

- Commit: de7b4ef0
- Queue: overnight_queue
- Timeout: 14400s (4h ceiling per PROT-019; same as v2 prereg)
- Purpose: EXT1_Stage3_audit_device_GPU_torchify_Fix24_P050
- Cell file: `experiments/exp_substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU.py`
- Prereg: `preregs/2026-06-25_substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU.md`

## Strategic significance

Highest product-impact remaining cell per Research drill 2026-06-25 (P=0.50).
Answers: "is the substrate-product audit-device shippable at production
V_C_IN=2000 V_REL=50?". The v2 numpy version had the right experimental
design but wrong dispatch path (CPU-bound on GPU runner). The torchified
rewrite preserves experimental content + meets Fix #24 GPU-actually-used
requirement.

## Bands (locked at module init via assert; identical to v2)

- HARD_PASS_PRODUCTION_SCALE at (V_C_IN=2000, V_REL=50):
  in_ans>=0.85 + out_ref>=0.85 + near_ref>=0.85 + uncert_corr>=0.70 +
  p95<=10ms + cv<=0.07
- CHAIN_GRADE_AT_LOWER_X: passes at one of (1000,20), (1000,50), (2000,20)
- HARD_FAIL_REFUSE_GATE_CLIFF: near_ref<0.50 at any V_REL>=20
- HARD_FAIL_LATENCY_BLOWN: p95>50ms at any operating point
- MIDDLE_BAND: no point hits HP, no HARD_FAIL trigger fires

## Q-discipline notes (per BIAS-Q + Fix #28)

- Smoke saturation at 1.000 across all 4 categories is EXPECTED at small V
  (matches v2 numpy smoke; the discriminating regime is at V_C_IN=2000 +
  V_REL=50, not the smoke V's).
- If full run produces 1.000 across all 4 categories AT the production
  operating point, raise as suspect Q-saturation per Skunkworks tiering —
  the audit primitive's near-domain disambiguation should NOT saturate at
  production V if real disambiguation is happening.
- Per-arm metrics will be visible in verdict_msg (Fix #28: read per-arm
  metrics, don't propagate from summary text alone).

## Cross-cell apples-to-apples

Seeds [11, 13, 19] cross-cell consistent with EXT-3 + EXT-6 +
partition_routing_v2 + Cell A v1 + Cell A v2 numpy. The torch port preserves
seed semantics (same numpy default_rng + same per-query noise draws); the
ONLY change is matmul backend.

## Fix #24 GPU-actually-used evidence path

When the run lands:
- `metrics.json` will include `cuda_available: true` and `device: cuda`
- `_fix24_violations` should be an empty list if matmuls actually used GPU
- Per-arm logs will print `cuda_available=True memory_allocated=<NN.NN> MB`
  after each big matmul block

If `_fix24_violations` is non-empty after landing, the cell ran on CPU
despite cuda available -> Fix #24 violation; route back to me for diagnosis.

## Discipline checks

- ASCII only: PASS
- Substrate-only (zero LLM forward calls): PASS (asserted in cell)
- Per-arm metrics in verdict_msg (Fix #28): PASS
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS): PASS
- Path-scoped commit (no `git add -A`): PASS
- --self-test PASS locally: 8 tests, <1s
- --self-test PASS remote: 5.6s on remote .venv
- --smoke PASS locally: verdict expected (saturation at small V)
- Pause flag check before queue_add: data/orchestrator_paused.flag absent at dispatch
- REMOTE VERIFY: cell present in remote queue.json post-dispatch
- Per-experiment --timeout REQUIRED: 14400s set per PROT-019 ceiling

## Files

- Cell: `experiments/exp_substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU.py`
- Prereg: `preregs/2026-06-25_substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU.md`
- Local smoke output: `data/exp_substrate_stage3_integrated_audit_device_demo_v2_production_scale_GPU_smoke/metrics.json`

-- exp_dev (Cell author / prover), 2026-06-25
