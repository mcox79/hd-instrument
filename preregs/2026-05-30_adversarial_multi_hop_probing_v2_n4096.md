# Pre-reg: adversarial_multi_hop_probing_v2_n4096

**Date:** 2026-05-30
**Anchor:** adversarial_multi_hop_probing_v2_n4096 (U2, S12 re-ship)
**Script:** experiments/exp_adversarial_multi_hop_probing_v2_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** v289 cap_map security-critical claim verification
(substrate killer features hold under adversarial queries).

## Context (v1 crash + v2 fix)

S12 v1 (shipped 2026-05-30 by previous cycle) crashed with NO_METRICS verdict.
Root cause (exp_dev v2 forensics):

  v1 created `torch.Generator(device='cuda')` and passed it to
  `torch.randperm(n, generator=g)` without specifying `device=`.
  PyTorch's `randperm` without `device=` defaults to a CPU output tensor,
  which requires a CPU-backed generator. PyTorch error:
    "Expected a 'cpu' device type for generator but found 'cuda'"
  All 5 seeds raised this; the seed-FAILED handler then produced 0 cells,
  yielding S12_INCONCLUSIVE "no cells" verdict.

  Affected patterns: p1_crosstalk (line 93), p4_edited (line 185 randint
  with cuda gen + device=cuda), p5_composition (line 212 randperm).

v2 FIX:
  - All RNG that feeds `randperm` or `randint` defaults uses a CPU
    generator + CPU tensor, then explicit `.to(device)` move.
  - Helper functions `_cpu_randperm_to()` and `_cpu_randint_to()` encapsulate
    the pattern.
  - Per-pattern try/except so a single pattern crash does not abort the seed
    (records pattern-specific error into the cell record).
  - Per-pattern selftest at scaffold time exercises each pattern on tiny CPU
    substrate.

## Hypothesis (SAME as v1)

Defense rate >=90% across all 5 adversarial patterns AND max leakage <=5%
on all patterns.

## Pre-registered bands (SAME as v1)

| Outcome      | Condition                                                              |
|--------------|------------------------------------------------------------------------|
| HARD_PASS    | All 5 patterns >=90% defense rate AND max leakage <=5% on all patterns  |
| HARD_FAIL    | Any pattern <70% defense OR any pattern with leakage >20%               |
| MIDDLE_BAND  | otherwise                                                              |
| INCONCLUSIVE | pattern_errors >= 50% of total pattern-evals (failsafe)                 |

## Adversarial patterns

1. **Crosstalk maximizing**: queries from codebook positions NOT in
   stored keys; defense = NO high-confidence false retrieval.
2. **Codebook collision**: pairs of stored keys with highest mutual
   cosine; defense = correct value returned, NOT colliding one.
3. **Deleted facts**: substrate deletes facts, then re-queries; defense =
   deleted target NOT recovered.
4. **Edited facts**: substrate edits facts, then re-queries; defense =
   new value returned, NOT old.
5. **Composition leakage**: queries combining unrelated stored keys;
   defense = no leak of either fact's target value.

## Self-test (v2-added)

- `_per_pattern_selftest()` exercises EACH of 5 patterns on tiny CPU
  substrate (N=256, M=32) at scaffold load -- catches pattern-specific
  crashes BEFORE smoke.
- Verdict gates: HP, HF synthesized inputs assert correct classification.
- Live `measure_seed()` on CPU asserts 5/5 patterns produce valid
  non-sentinel defense_rate AND pattern_errors is empty.

## Timeout estimate

5 seeds x 5 patterns x ~32 queries = ~800 evaluations. Per eval ~2-5s
including substrate rebuild for delete/edit patterns. ~3000s + GPU
overhead. **timeout_s = 14400** (safety margin; v1 wall=4.46s with all
crashes, healthy run will be ~3000s, 4h cap).

## Production config

N=4096, M=2048, depth=5, n_queries_per_pattern=32, seeds=[7,17,23,31,41].

## N-suffix binding

`_n4096` -> production N = 4096 (PROT-018). `N_FULL = 4096` asserted at
import.

## v1 -> v2 changes

- `_cpu_randperm_to()` / `_cpu_randint_to()` helpers
- pattern1, 4, 5: replaced cuda-Generator RNG with CPU-Generator + .to(device)
- per-pattern try/except in `measure_seed()`
- `_per_pattern_selftest()` added
- compute_verdict gates pattern-errors >= 50% -> INCONCLUSIVE (failsafe)
- verdict_msg now includes per-pattern error count
