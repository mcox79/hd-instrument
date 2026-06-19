# Pre-registration: pp52_hebbian_vs_lora_in_lora_valid_regime_n1024_v1

**Date:** 2026-06-02
**Anchor:** pp52_hebbian_vs_lora_in_lora_valid_regime_n1024_v1
**Queue:** remote_cpu_queue
**N:** 1024, **Seeds:** 5

## Scientific question (Probe E from research_routing_v343_pp52_hebbian_lora_rescue_2026-06-02.md)
In the LoRA-valid regime (small N, small M, sufficient rank), is Hebbian one-shot fact addition
faster and more accurate than LoRA fine-tuning? This is the correctly-framed comparison replacing
pp52_hebbian_lora_speedup which was STRUCTURALLY MISFRAMED (LoRA globally modifies W at production N,
destroying accuracy of M=400 patterns even when adding only K=10 facts).

## PROT-022 entry 4 applied
Speedup HP gate requires ACC_FLOOR >= 0.90 on BOTH substrate AND LoRA. If LoRA acc < 0.90 at all
tested ranks, report LORA_INCOMPATIBLE (not HARD_FAIL). Per research routing Section 5.

## Pre-registered bands

**HARD-PASS:**
- HP1: substrate fact_retrieval_acc >= 0.95
- HP2: LoRA fact_retrieval_acc >= 0.90 at minimum r where LoRA passes (ACC_FLOOR gate MUST pass)
- HP3: wall_speedup >= 100x (only if HP1+HP2)
- HP4: flops_speedup >= 1000x (only if HP1+HP2)
- HP5: substrate baseline_retention >= 0.95
- All 5 HP required for HARD-PASS.

**MIDDLE:** HP1+HP2 pass; wall_speedup 10x-100x OR flops_speedup 100x-1000x.

**HARD-FAIL:**
- HF1: substrate fact_retrieval_acc < 0.70
- HF2: substrate baseline_retention < 0.80
- LORA_INCOMPATIBLE: special outcome (not FAIL) if LoRA never reaches ACC_FLOOR at any r.

## Calibration rationale
P_deflated = 0.65 per research routing. Substrate Hebbian is algebraically O(N^2) one-shot.
LoRA GD convergence requires O(max_steps * 2 * N * r) FLOPs. At N=1024, r=102, max_steps=200:
FLOPs_lora ~ 200 * 2 * 1024 * 102 * 6 = 250 million. FLOPs_sub = 10 * 1024^2 = 10.5 million.
Theoretical flops_speedup = 250M / 10.5M = 24x (below HP4=1000x but above MIDDLE=100x).
Wall speedup depends on vectorization overhead; substrate may be faster by larger margin.
Bands set: HP3=100x (conservative), HP4=1000x (conservative). If speedup << 100x, MIDDLE.

## N-suffix section
No _n1024 suffix in anchor name (routing spec uses n1024 as part of name body, not _n suffix).
Production N = 1024; scripts enforce N = _N_SUFFIX = 1024. No PROT-018 _n suffix binding conflict.

## Timeout estimate
Smoke N=256, 2 seeds, 2 ranks, max_steps=50. Expected smoke wall ~ 20s.
FULL: N=1024, 5 seeds, 4 ranks, max_steps=200. Scaling: linear in seeds * ranks * steps.
formula: ceil(1.5 * 20 * (4/2) * (5/2) * (4/2)) = ceil(1.5 * 20 * 2 * 2.5 * 2) = ceil(300) = 600
Add 50% buffer for numpy overhead: timeout_s = 900
timeout_s = 900
