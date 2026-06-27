# Pre-registration: phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1

**Date:** 2026-06-26
**Author:** exp_dev (Opus 4.7 1M)
**Trigger:** USER 2026-06-26 directive "what about phase diagram build out?" via Research routing-correction handoff.

## Anchor

`phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1`

## Routing

- **Queue:** overnight_queue (GPU; remote_gpu via hdi_orchestrator)
- **Reason:** N=16384 W matrix = 1.07GB fp32 + V_C up to 8000 batched matmul; well past CPU-feasible
- **GPU util gate:** smoke MUST profile gpu_util >= 50% on remote GPU before full dispatch

## Hypothesis

Stage3-integrated-audit production envelope inherits V_C_IN <= 2000; cortex content-extraction work needs production-scale V_C coverage at N=16384. Existing chain-grade points are at smaller V_C; no clean V_C sweep at production N.

**Question:** does substrate associative retrieval stay chain-grade at V_C=8000 (4x production) at N=16384, or does it cliff?

## Mechanism

Substrate-native sparse-bipolar codebook E (V_C x N) + relations matrix R (V_R x N). Hebbian binding: W += sum_j outer(E[o_j], E[s_j] * R[r_j] * sqrt(N)) / N. Retrieval: argmax(E @ (W @ (E[s] * R[r] * sqrt(N)))).

M_FACTS/V_C ratio held at 0.75 (production-baseline) to isolate V_C effect from absolute capacity.

## Arms (3 phase points + 1 sentinel)

| Arm | V_C | M_facts | Role |
|-----|-----|---------|------|
| ARM_BASELINE_KNN | max(V_C) | 500 | sentinel; >=0.90 (Fix #28) |
| ARM_VC_2000 | 2000 | 1500 | production baseline |
| ARM_VC_4000 | 4000 | 3000 | 2x production |
| ARM_VC_8000 | 8000 | 6000 | 4x production; ceiling probe |

## Pre-reg bands (LOCKED at module init)

- HP_RECALL = 0.90 (per-arm chain-grade gate)
- HF_RECALL = 0.50 (at VC=2000 below this -> SANITY_BREACH)
- CV_MAX = 0.05 (per-arm seed cv)
- HP_KNN_SENTINEL = 0.90 (Fix #28)

## Verdicts

| Verdict | Condition |
|---------|-----------|
| CHAIN_GRADE_VC_CEILING_8000 | all 3 VC phase points chain-grade (rec>=0.90 cv<=0.05) |
| PARTIAL_VC_CEILING_4000 | VC=2000+4000 chain-grade; VC=8000 cliffs |
| PARTIAL_VC_CEILING_2000 | VC=2000 only; VC>=4000 cliffs |
| SANITY_BREACH | VC=2000 below HF_RECALL OR KNN sentinel breach |
| HARD_FAIL | substrate-only gate violated |
| MIDDLE_BAND | mixed phase points |

## Config

- N_DIM=16384 (full); V_REL=8
- VC_SWEEP: [2000, 4000, 8000]; M_FACTS_BY_VC: {2000: 1500, 4000: 3000, 8000: 6000}
- Seeds: [11, 13, 19]
- Encoder provenance: SUBSTRATE_NATIVE
- Substrate-only decode (assert _LLM_CALL_COUNTER[0] == 0)

## ETA

Per-seed GPU walltime estimate:
- W ingest at N=16384 batched: ~5-10s per VC
- 3 VC arms x ~10s = 30s/seed
- Plus KNN sentinel ~1s
- Total: ~35-45s/seed; 3 seeds = ~2-3 min wall on GPU
- With smoke + setup: timeout 1200s (20 min)

## Smoke verdict (laptop CPU 2026-06-26)

SMOKE_PASS: mechanism end-to-end OK at smoke regime
- KNN_SENTINEL=1.000 (smoke sigma=0.15, OK)
- VC_200 rec=1.000; VC_400 rec=1.000 (smoke regime N=2048 saturates; production-tuned bands deferred to FULL)
- gpu_util check DEFERRED to remote GPU smoke
