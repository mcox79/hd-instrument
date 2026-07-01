# Pre-Registration: multihop_depth_15_hint_alternatives_v1

**Date:** 2026-07-01
**Author:** exp_dev
**Cell:** `experiments/exp_multihop_depth_15_hint_alternatives_v1.py`

## Purpose

Test alternative hint mechanisms at depth=15 vs partition-oracle CG landing (0.808 3-seed mean; Skunkworks tiered MEASURED_MECHANISM under by-construction-saturation because partition-oracle uses gen-time target-partition access).

Alternatives (4 arms x 3 seeds; 12 units):
- **ARM_A** `partition_oracle_reference` — reference; same as parent CG ARM_B (gen-time target_part oracle)
- **ARM_B** `learned_gate` — analytical partition-prototype scoring; softmax argmax over 5 partitions from mean pre-cleanup state (trained on 200 chains x 15 hops = 3000 hop samples, 600/partition)
- **ARM_C** `top_k_softmax_attention` — softmax-weighted mixture over all 5 partitions (K=5, temp=1.0); weighted-argmax across V_C via partition-weighted contributions
- **ARM_D** `mem_aug_hint` — memory-augmented; nearest-train-chain lookup on E[s] cosine supplies partition hint (3000 train entries)

## Discriminator

Which alternative (if any) matches partition-oracle 0.808 within noise? Matching (best_alt >= 0.808 - 0.05 = 0.758) breaks by-construction-saturation critique and elevates mechanism-class to CHAIN_GRADE (informed hint w/o gen-time oracle access).

## Regime (LOCKED)

| Param | Value | Rationale |
|---|---|---|
| N | 8192 | Match parent CG regime |
| V_C | 4000 | Match parent CG |
| V_P | 10 | Match parent CG |
| depth | 15 | Match parent CG |
| n_partitions | 5 | Match parent CG ARM_B (best CG arm) |
| part_size | 800 | 4000/5 |
| n_chains_train | 200 | Match parent CG; supplies 3000 hop samples (600/partition — well-conditioned prototypes) |
| n_chains_test | 200 (full) / 100 (smoke) | Match parent CG cadence |
| SEEDS (full) | [11, 13, 19] | Match parent CG 3-seed set for direct comparison |
| SEEDS (smoke) | [11] | Single seed |
| K_TOP_SOFTMAX | 5 | Full softmax (all partitions) |
| gate_temp | 1.0 | No temperature scaling |
| attn_temp | 1.0 | No temperature scaling |

## Cross-talk (computed)

- CROSSTALK_PART = sqrt(799/8192) = 0.3123
- CROSSTALK_BASELINE = sqrt(3999/8192) = 0.6989

## Pre-registered bands (META_RULE_AL; LOCKED)

**HARD_PASS (chain-grade; novel finding = alternative matches oracle):**
- arm_A.top1@d15 in [0.60, 0.95] (regime replication)
- best(arm_B, arm_C, arm_D).top1@d15 in [0.50, 0.95]
- arm_A.top1 - best_alt.top1 <= 0.05 (within noise of oracle)
- cv(arm_A across seeds) < 0.15 AND cv(best_alt across seeds) < 0.15
- arms_distinct == True (SHA-256)
- saturation == False (best_alt < 0.95)

**MIDDLE_BAND:**
- best_alt in [0.30, 0.50) — partial mechanism
- OR best_alt in [0.50, 0.95) but >0.05 below oracle
- OR HP band hit but cv >= 0.15

**HARD_FAIL:**
- best_alt <= 0.30 (all alternatives die → confirms partition-oracle is trivially informed; by-construction-saturation critique CONFIRMED)
- OR arm_A < 0.50 (regime replication broken; no comparison possible)
- OR cardinality != 12
- OR arms_tied

## Substrate-KB prior work check (2026-07-01)

Query: `multi-hop hint mechanism alternative partition oracle attention`
- Top hit cosine=0.3262: parent CG landing (depth-15 partition-oracle MEASURED_MECHANISM under by-construction-saturation tiering).
- Hits #2/#4/#5: LLM attention/FFN capability separation drills (informative for TOP_K_SOFTMAX_ATTN arm).
- Hit #3 cosine=0.3096: depth-5 partition-oracle at 0.95.
- **No prior work on hint-mechanism alternatives at depth-15.** Genuinely novel.

Related older-depth cells exist (informative but different regime):
- `exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_{7,13,19}.py`
- `exp_substrate_barrier1_hint_learned_linear_planner_drill2_v1_seed_7.py`

## Number tagging (META_RULE_AC)

- MEASURED@CG_ORACLE_D15_3SEED_MEAN = 0.808 (parent CG seeds 11/13/19 mean)
- HYPOTHESIZED@ARM_A_REFERENCE_BAND = [0.60, 0.95]
- HYPOTHESIZED@BEST_ALT_MATCH_BAND = [0.50, 0.95]
- HYPOTHESIZED@ALT_WITHIN_ORACLE_DELTA = 0.05
- THEORETICAL@RANDOM_GATE_FLOOR = 0.2^15 ~ 3e-11 (from parent RANDOM_E arm at 0.0)
- CITED@MANTE_2013: PFC goal-conditioned attention

## Dispatch plan

- SMOKE: local_cpu_queue (single seed, N=8192, 100 test chains; expected 8-15 min based on parent CG smoke)
- FULL: overnight_queue (GPU-eligible; matmul-heavy; N=8192 V_C=4000 seeds=[11,13,19] test=200 chains)

## Source citations (META_RULE_AE; absolute paths)

- Parent CG cells: `d:/AI/hd-instrument/experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_{11,13,19}_v1.py`
- Parent CG metrics: `d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_{11,13,19}_v1/metrics.json`

## Discipline tags

META_RULE_AC / META_RULE_AE / META_RULE_AF / META_RULE_AG / META_RULE_AH / META_RULE_AL / META_RULE_AN / META_RULE_H; BIAS-Q; BIAS-N; BIAS-S; DISCRIMINATOR-MUST-SURVIVE-SCALE (smoke at N=8192 full-N); Fix #28 per-arm reads.
