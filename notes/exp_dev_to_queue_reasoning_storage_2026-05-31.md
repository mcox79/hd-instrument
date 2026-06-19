# exp_dev -> queue: reasoning storage anchors (2026-05-31)

Origin: notes/research_substrate_reasoning_storage_2x_synthesis_v1_2026-05-31.md
Dispatched by: exp_dev (HDLAB_EXP_NAME=7d39e13)
Status: SHIPPED + REMOTE VERIFIED

## Shipped anchors

```
queue=remote_cpu_queue name=reasoning_storage_scheme_b_smoke_v1_n16384 script=experiments/exp_reasoning_storage_scheme_b_smoke_v1_n16384.py prereg=preregs/2026-05-31_reasoning_storage_scheme_b_smoke_v1_n16384.md timeout=21600
queue=remote_cpu_queue name=reasoning_storage_threshold_sweep_v1_n4096 script=experiments/exp_reasoning_storage_threshold_sweep_v1_n4096.py prereg=preregs/2026-05-31_reasoning_storage_threshold_sweep_v1_n4096.md timeout=14400
```

## Summary

Two anchors shipping the Phase 1 reasoning-storage smoke from the 2x deep research
synthesis. Both target CPU (remote_cpu_queue); no CUDA required.

**reasoning_storage_scheme_b_smoke_v1_n16384** (N=16384, 3 seeds, ~90 min ETA):
- Arm A: Scheme B encoding audit -- exact three-way bipolar unbinding confidence
- Arm B: Structured vs random key differential (per-step retrieval accuracy ratio)
- Arm C: Conclusion re-encoding mitigation (Steinberg-Sompolinsky 2022 rho permutation)
- HP bands: struct_acc/rand_acc >= 0.95 = HARD_PASS; <= 0.85 = HARD_FAIL
- Research note predicts: Arm A HARD_PASS (algebraically exact); Arm B TBD (0.35-0.62
  P_def range); Arm C TBD (0.55-0.70 P_def from lit-grounded Steinberg-Sompolinsky)

**reasoning_storage_threshold_sweep_v1_n4096** (N=4096, 3 seeds, ~15 min ETA):
- Sweep: #shared-rule chains {100, 1K, 10K, 44K, 100K}
- Metric: sigma_1/sigma_2 ratio (collapse criterion > 3.0)
- HP: no collapse at <= 44K = confirms drill A 32N/3 threshold
- HF: collapse at <= 10K = threshold 4x lower than predicted
- Note: k_step = r_modus * k1_rand * k2_rand is still random BSC given large k1/k2 pools
  (200 entity x 20 relation = 4000 combos). Expecting HARD_PASS but empirical test needed.

## Queue state at ship time

remote_cpu_queue: 5 pending (was 4; 2 new added)
overnight_queue: 16 pending (unchanged)
runner: cpu_runner_0 running modern_hopfield_cpu_extended_v10_n16384

Commit + push deferred to main thread per feedback-subagent-permission-inheritance-gap.
