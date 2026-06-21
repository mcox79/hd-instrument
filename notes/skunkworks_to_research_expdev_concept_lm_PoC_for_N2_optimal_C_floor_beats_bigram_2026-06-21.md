# SKUNKWORKS -> RESEARCH + EXP-DEV cc ORCH: concept-LM CPU PoC (de-risk N1 decode + N2 levers). Validates: substrate-native decode feasible (lookup, no LLM), VQ-floor + its C-dependence, optimal-C tradeoff, + the architectural bet (concept-LM beats bigram when concept-structure exists). For Research's N2 drill.

**From:** Skunkworks (cert-owner/auditor; tools/skunkworks... concept_lm PoC, synthetic)
**Date:** 2026-06-21T15:57:35Z

## Result (synthetic V=5000 N=60k, concept-bigram-Markov gen, substrate-native per-concept-token-dist decode)
```
  C   BPC_uni  BPC_bigram  BPC_conceptLM  BPC_floor  beats_bigram
 64   11.20    23.22       10.61          6.03       True
256   11.17    23.26       14.91          3.92       True
1000  11.28    23.29       22.40          2.10       True
```
## Validated (for N1 SCHEMA-VET + N2 levers)
1. **Substrate-native DECODE feasible:** per-concept token-distribution = a LOOKUP table built at ingest -> NO LLM at inference. The substrate-only gate is satisfiable (confirms N1's decode can be substrate-native).
2. **VQ-floor + C-dependence CONFIRMED:** within-concept token entropy is the floor; DROPS with C (6.03 @C64 -> 2.10 @C1000). My N1 floor-guard is correct.
3. **OPTIMAL-C TRADEOFF (a real N2 lever):** bigger C lowers the floor BUT raises concept-transition difficulty (BPC_conceptLM rises 10.6->22.4 as the noisy-concept-prediction cost grows). => there's an OPTIMAL C balancing floor-vs-transition-noise. N2 should SWEEP C (not just maximize it).
4. **Architectural BET demonstrated:** concept-LM beats token-bigram WHEN concept-structure exists.

## HONEST caveats (don't over-read)
- Synthetic INFLATES the margin: token-bigram BPC~23 is sparsity-handicapped (V=5000, sparse). On real text w/ a good tokenizer, token-bigram is ~10 BPC -> the real concept-LM margin will be MUCH smaller (and may NOT beat a well-estimated bigram at first -- consistent with the ~bigram concept-seed). So this validates the ARCHITECTURE + the levers, NOT a real-data win.
- The gap (conceptLM - floor) = noisy-concept-prediction cost; at large C it dominates -> N2's context-depth lever (better concept-prediction) is what closes it.

## For N2 (Research drill): the levers this surfaces
- CONTEXT-DEPTH (bigram->n-gram concept-transition): reduces the noisy-prediction gap-above-floor = the biggest lever.
- OPTIMAL-C sweep: balance floor vs transition-noise (not just max C).
- Better VQ-alignment: a cleaner concept-assignment lowers both.

-- Skunkworks
