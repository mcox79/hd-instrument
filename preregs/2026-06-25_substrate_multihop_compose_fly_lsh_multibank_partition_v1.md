# PREREG: substrate_multihop_compose_fly_lsh_multibank_partition_v1

**Date:** 2026-06-25
**Author:** exp_dev (via Research 5x revival drill)
**Revival angle:** ANGLE 1 (compose today's 3 chain-grade wins)
**Source drill:** `notes/research_multihop_revival_5x_drill_2026-06-25.md`
**Brain prior:** STRONG (3 brain-aligned mechanisms — cerebellar/KC fan-in; PFC working memory parcellation; hippocampal place-cell-style episode decomposition)

## Hypothesis

Today's three chain-grade wins each address a different per-step bottleneck:
- fly-LSH sparse expansion (anisotropy_rescue_4arm v2 ARM B): lifts retrieval from 0.018 raw to 0.997 by expanding cues into sparse-random subspace.
- multi-bank WM 8x32 (working_memory_multi_bank_routing v1): recall 1.000 at K=256 vs single-bank K=256=0.46.
- partition-routing M=10M (partition_routing_10M_full v2): chain-grade @ M=100k, HARD_PASS_PARTIAL @ M=1M.

If each lift composes onto the per-hop primitive in multi-hop chains, per-step accuracy could lift from 0.69 to 0.85+, giving 5-hop top1 of 0.85^5 = 0.44 minimum (vs current 0.122).

## Mechanism (substrate-only; zero LLM forward calls)

- ARM_COMPOSE_FLY_LSH_5HOP: fly-LSH expansion per cue; cleanup against E_expanded codebook
- ARM_COMPOSE_MULTI_BANK_5HOP: V_C=200 split into 8 banks of 25; per-hop cleanup in target bank (ORACLE-routed; favorable-conditions test)
- ARM_COMPOSE_PARTITION_5HOP: V_C=200 split into 20 partitions of 10; per-hop cleanup in target partition (ORACLE-routed)
- ARM_COMPOSE_ALL_3_5HOP: all three composed (expanded space + per-bank W + bank-local cleanup)
- ARM_SINGLE_CHAIN_5HOP: pointer-chain v2 monolithic 5hop (rail)
- ARM_BASELINE_HRR_2HOP: beta-sweep sanity rail

NOTE: bank/partition arms are ORACLE-routed (target bank/partition known a priori). This is the favorable-conditions test: if oracle-routed STILL fails, the lift mechanism is not the bottleneck. If oracle-routed passes, follow-up cell builds a real router. Documented in cell DESIGN_NOTE.

## Regime

- N=8192, V_C=200, V_P=10, K_SET=20, n_chains=200, seeds=[7, 17, 23]
- N_BANKS=8, N_PARTITIONS=20 (V_C must divide cleanly), N_LSH_EXPANSIONS=5, LSH_TOPK=20

## Pre-registered bands (LOCKED via assert at module init)

- **HARD_PASS_CHAIN_GRADE_COMPOSITION_SUPERADDITIVE**: ALL_3 top1 >= 0.50 AND cv <= 0.07 AND ALL_3_lift > sum(FLY_lift + BANK_lift + PART_lift) (i.e. super-additive composition)
- **HARD_PASS_CHAIN_GRADE_COMPOSITION_ADDITIVE**: ALL_3 top1 >= 0.50 AND cv <= 0.07 (just additive composition works)
- **HARD_PASS_PARTIAL**: any single arm (FLY / BANK / PART) top1 >= 0.30
- **MIDDLE_BAND**: ALL_3 top1 in [0.20, 0.50]
- **HARD_FAIL_COMPOSITION_DOESNT_HELP**: ALL_3 top1 < 0.20
- **SANITY_BREACH**: ARM_BASELINE not in [0.62, 0.68] for majority of seeds

## META-discipline

- META_PROSPECTIVE_BANDS_FRESH_SEEDS: bands locked at module-init via assert
- META_M7: smoke must NOT show >> 0.50 lift over rail; if it does, ABORT
- Fix #28: per-arm metrics reported; ablation analysis explicit

## Strategic significance

- HARD_PASS_SUPERADDITIVE: 3 chain-grade primitives genuinely compose; multi-hop revival mechanism validated; high transfer to other deep-compounding cells
- HARD_PASS_ADDITIVE: composition works but individual primitives could substitute
- HARD_PASS_PARTIAL: at least one primitive lifts in isolation; suggests next-wave cell isolates the working primitive
- MIDDLE_BAND: partial — useful negative direction for which primitives don't lift
- HARD_FAIL: ablation rules out THIS composition; routes back to Angle 3 (bidirectional) or Angle 5 (PFC chunking) which attack different bottlenecks

## Cost

~20-30 min on local_cpu_queue (substrate-only; numpy; 3 seeds; 5 expansions x N=8192 fly-LSH projections is memory-bound)
