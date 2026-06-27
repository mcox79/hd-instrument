# Pre-registration: phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1

**Date:** 2026-06-26
**Author:** exp_dev (Opus 4.7 1M)
**Trigger:** USER 2026-06-26 directive "what about phase diagram build out?" via Research routing-correction handoff.

## Anchor

`phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1`

## Routing

- **Queue:** overnight_queue (GPU; remote_gpu via hdi_orchestrator)
- **Reason:** N=8192 + 4 W matrices @ 268MB each + per-hop matmul cleanup; GPU-batched per Fix #24
- **GPU util gate:** smoke MUST profile gpu_util >= 50% on remote GPU before full dispatch

## Hypothesis

Prior cell `phase_diagram_multihop_depth_extension_via_partition_oracle_v1` chain-graded multi-hop at depth 15 (PART_15HOP=0.808 cv=0.024) via partition-oracle routed cleanup. Per-step accuracy was 0.95-0.99. Predicted compounding to depth 30 at 0.97^30 = 0.40.

**Question:** does the partition-oracle routing primitive scale to depth 30, or does it cliff between 15 and 30?

## Mechanism

Partition-oracle per-hop cleanup (VERBATIM port from depth-extension v1): at each hop, scope argmax cleanup to the target partition (target_part = target_o // part_size); this dramatically cuts the cleanup search space and rescues compounding.

For each depth D in {15, 20, 25, 30}, build a separate W from chains constructed at max_depth=D (so the chains exist for the test). E and R are shared across all four arms.

## Arms (4)

| Arm | Depth | W source | Role |
|-----|-------|----------|------|
| ARM_PART_ORACLE_15HOP | 15 | W_d15 (3000 bindings) | sanity rail: reproduce 0.808+/-0.05 |
| ARM_PART_ORACLE_20HOP | 20 | W_d20 (4000 bindings) | novel phase point |
| ARM_PART_ORACLE_25HOP | 25 | W_d25 (5000 bindings) | novel phase point |
| ARM_PART_ORACLE_30HOP | 30 | W_d30 (6000 bindings) | novel phase point |

## Pre-reg bands (LOCKED at module init)

**Sanity rail (verdict pre-emption on majority-seed breach):**
- RAIL_DEPTH_15: PART_15HOP NOT in [0.758, 0.858] -> SANITY_BREACH (target 0.808 +/- 0.05)

**Phase points (per-arm):**
- 20HOP: HARD_PASS if mean >= 0.55; HARD_FAIL if mean < 0.30
- 25HOP: HARD_PASS if mean >= 0.40; HARD_FAIL if mean < 0.18
- 30HOP: HARD_PASS if mean >= 0.30; HARD_FAIL if mean < 0.12

**Stability:** cv across seeds <= 0.10 for HARD_PASS

## Verdicts

| Verdict | Condition |
|---------|-----------|
| CHAIN_GRADE_DEPTH_CEILING_30 | rail PASS + all 3 (20/25/30) HARD_PASS |
| PARTIAL_DEPTH_CEILING_25 | rail + 20+25 HARD_PASS, 30 below |
| PARTIAL_DEPTH_CEILING_20 | rail + 20 HARD_PASS, 25 below |
| DEPTH_15_IS_CEILING | rail only; 20+25+30 all fail |
| SANITY_BREACH | rail breach majority of seeds |
| MIDDLE_BAND | mixed phase points |

## Config

- N_DIM=8192 (full); N_CHAINS=200; V_C=200; V_P=10; N_PARTITIONS=20; PART_SIZE=10
- Seeds: [11, 13, 19]
- Encoder provenance: SUBSTRATE_NATIVE
- Substrate-only decode (assert _LLM_CALL_COUNTER[0] == 0)

## ETA

Per-seed full-run estimate (based on depth-extension v1 actual times):
- 4 W ingests x ~5s = 20s/seed
- 4 part-oracle arms x ~3s/depth_unit = ~22s/seed
- Total: ~45-60s/seed; 3 seeds = ~3-5 min wall on GPU
- With overhead: timeout 1200s (20 min)

## Smoke verdict (laptop CPU 2026-06-26)

SMOKE_PASS: mechanism end-to-end at depths 15/20/25/30 OK
- PART_15HOP=1.000 (smoke over-performs by design; rail check skipped in smoke)
- PART_20HOP=0.960; PART_25HOP=1.000; PART_30HOP=0.920
- Mechanism stable across all 4 depths at smoke regime (N=2048 V_C=200 N_CHAINS=25)
- gpu_util check DEFERRED to remote GPU smoke (laptop has no CUDA)
