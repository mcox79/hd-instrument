# PREREG: substrate_multihop_pfc_chunked_2hop_decomposition_v1

**Date:** 2026-06-25
**Author:** exp_dev (via Research 5x revival drill)
**Revival angle:** ANGLE 5 (PFC task-decomposition chunking)
**Source drill:** `notes/research_multihop_revival_5x_drill_2026-06-25.md`
**Brain prior:** STRONGEST of 5 angles (PFC + basal ganglia chunking is brain's universal multi-step reasoning circuit; Miller 1956, Cowan 2000, Graybiel 1998, Botvinick 2008)

## Hypothesis

Multi-hop chains compound per-hop error. The substrate's 2-hop primitive is empirically chain-grade (n8 ConceptNet HARD_PASS), but its 5-hop and 10-hop are HARD_FAIL because per-step accuracy of ~0.69 -> 0.69^5 = 0.156 (empirical: 0.122). Decomposing the chain into 2-hop sub-queries with CLEAN-ENTITY hand-off between chunks lifts each per-chunk accuracy toward the proven 2-hop rail. For 5-hop -> 2+2+1; for 10-hop -> 2+2+2+2+2.

Critical pre-req (built into the cell): the 2-hop sub-query starting from a clean entity index must accuracy approach the 2-hop sanity rail (0.65+/-0.03) at the V_C=200/V_P=10 regime. If 2-hop from clean only achieves 0.485 (the chain-from-noisy regime), chunking won't help.

## Mechanism (substrate-only; zero LLM forward calls)

- ARM_PFC_CHUNKED_5HOP: split 5-hop chain into chunks [2, 2, 1]. Each chunk starts from a CLEAN atomic E[] vector (the cleaned argmax index from previous chunk's final hop). Within each chunk, do bind/walk hops without intermediate cleanup, then argmax-cleanup to atomic at chunk end. Hand off atomic E[next-start] to next chunk.
- ARM_PFC_CHUNKED_10HOP: same with chunks [2, 2, 2, 2, 2].
- ARM_SINGLE_CHAIN_5HOP: monolithic 5-hop forward via pointer-chain v2 mechanism (per-step cleanup; argmax after every hop). This is the RAIL we must beat.
- ARM_BASELINE_HRR_2HOP: beta-sweep regime verbatim (V_P=2, fixed-pair); sanity rail [0.62, 0.68].

## Regime

- N=8192, V_C=200, V_P=10, K_SET=20, n_chains=200, seeds=[7, 17, 23]
- Apples-to-apples with pointer-chain v2

## Pre-registered bands (LOCKED via assert at module init)

- **HARD_PASS_CHAIN_GRADE_BARRIER_1_VIA_CHUNKING**: PFC_CHUNKED_5HOP top1 >= 0.50 AND PFC_CHUNKED_10HOP top1 >= 0.30 AND cv (both) <= 0.07
- **HARD_PASS_PARTIAL**: PFC_CHUNKED_5HOP top1 >= 0.30 (>= 2.5x lift over 0.122 rail)
- **MIDDLE_BAND**: PFC_CHUNKED_5HOP top1 in [0.20, 0.30]
- **HARD_FAIL_CHUNKING_DOESNT_HELP**: PFC_CHUNKED_5HOP top1 < 0.20
- **SANITY_BREACH**: ARM_BASELINE not in [0.62, 0.68] for majority of seeds

## META-discipline

- META_PROSPECTIVE_BANDS_FRESH_SEEDS: bands locked at module-init via assert
- META_M7: smoke must NOT show >> 0.50 lift over rail; if it does, ABORT (smoke regime mismatch is today's 4-cell smoke-inflation pattern)
- Fix #28: per-arm metrics reported; verdict reads per-arm not summary

## Strategic significance

- HARD_PASS: substrate-native Barrier 1 revival via PFC-style task decomposition; n-hop reasoning compositionally reachable for n=10 via [2]x5 chunks; brain-aligned mechanism validated
- MIDDLE_BAND: partial lift; compose with Angle 1 (fly-LSH per-chunk) as second wave
- HARD_FAIL: rules out chunked-with-cleanup as revival path; per-hop primitive itself is the bottleneck and downstream mechanisms can't fix it

## Cost

~15-20 min on local_cpu_queue (substrate-only; numpy; 3 seeds)
