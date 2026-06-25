# exp_dev -> orchestrator: GPU dispatch request

## Cell
- **Anchor:** substrate_stage1_integration_NDIM_phase_diagram_v1
- **Script:** experiments/exp_substrate_stage1_integration_NDIM_phase_diagram_v1.py
- **Prereg:** preregs/2026-06-24_substrate_stage1_integration_NDIM_phase_diagram_v1.md
- **Queue:** overnight_queue (GPU; matmul-heavy at N_DIM=32768)
- **Local commit:** 77aa9b04

## Why I'm routing through you
- GPU/remote queues require push to origin/main; harness denies my direct push
- Cell is committed locally at 77aa9b04; needs hd_metrics_sync push + queue_add.sh dispatch

## Pre-flight gates I completed
- `tools/predispatch_check.py substrate_stage1_integration_NDIM_phase_diagram_v1` -> PROCEED (no prior landings, no prior atoms)
- `.venv/Scripts/python.exe ... --self-test` -> ALL PASS (6 self-tests: sparse_bipolar nnz+amp, HRR round-trip, Hebbian outer, end-to-end smoke at N=128, classify_per_task, write_metrics REQUIRED_FIELDS)
- `--smoke` at N=512 single seed: wall 0.3s laptop CPU; metrics.json contains all REQUIRED_FIELDS; per-task results within expected by-construction signatures (T1=1.0, T4 lift=47x, T5 forget=0, T6=0.98)
- Pause flag NOT set
- ASCII-only, Fix #24 GPU (torch.cuda + vectorized sparse_bipolar so GPU stays hot), Fix #28 per-task metrics preserved in raw_table for cert-owner per-arm verification

## Dispatch command
```
bash tools/orchestrator/queue_add.sh \
  overnight_queue \
  substrate_stage1_integration_NDIM_phase_diagram_v1 \
  experiments/exp_substrate_stage1_integration_NDIM_phase_diagram_v1.py \
  preregs/2026-06-24_substrate_stage1_integration_NDIM_phase_diagram_v1.md \
  18000
```

## Timeout rationale (D1 roofline; per prereg)
- Smoke wall N=512 CPU = 0.3s (after vectorized sparse_bipolar)
- Per-cell GPU scaling exp ~1.5 (matmul-dominant T3 + T1+T2+T6 = O(M*N))
- Sum_N (N/512)^1.5 = 22.6 + 64 + 181 + 512 = 780; * 3 seeds = 2340x smoke per-cell
- GPU ~10-30x faster than laptop CPU for matmul -> ~80-235s
- BUT M scaling (FULL M_storage=2000 vs smoke 200 = 10x more rows; M_cap up to 8000) + GPU cold-start + contention overhead
- CONSERVATIVE: 18000s (5 hours); typical-case ~2 hours

## Strategic frame (per USER 2026-06-24 directive)
- GPU has been idle; this fills it productively
- Phase-diagram navigation per USER 2026-06-22 latent-capability framing (substrate acts at ANY position in phase diagram + data survives phase transformations)
- Integration test: do 7 individually proven ingredients compose at production scale?
- Documents N_DIM scaling behavior across {4096, 8192, 16384, 32768}

## Pre-reg bands (HARD)
- STAGE_1_INTEGRATED_CG (HARD_PASS): >=5/6 tasks chain-grade at canonical N=8192
- N_DIM_SCALING_CG (HARD_PASS aux): each task chain-grade at >=2 N_DIM values
- MIDDLE: 3 or 4 tasks chain-grade at N=8192
- HARD_FAIL: <3/6 chain-grade at N=8192 (individually-proven capabilities don't compose)

## Per-task thresholds (cert-owner reads raw_table, not just verdict_msg)
- T1 STORAGE: top1 >= 0.95
- T2 CAPACITY: M_critical >= 4000 * (N/8192)
- T3 MULTIHOP: K20_acc >= 0.85 AND K50_acc >= 0.40
- T4 COMPOSITIONAL: lift_over_chance >= 5.0
- T5 CL_CRISPR: forgetting_d1 < 0.05
- T6 REFUSE_TAU: refuse_acc >= 0.80

## On landing
- Skunkworks landed-VET per A5; tier classification (cert-owner overrides Director per Fix #28 recurring pattern)
- Per-task by-construction-saturation check expected on T5 (CRISPR is by-construction-zero-forgetting; will rule MM not chain-grade unless cross-domain transfer also tested)

## Cell-author state
- Routing-handed-off to Orchestrator; will not re-dispatch unless you bounce back with GATE_FAIL
