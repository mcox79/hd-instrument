# Pre-registration: wave14z_multihop_hadamard_entities

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14z_multihop_hadamard_entities.py](../experiments/exp_wave14z_multihop_hadamard_entities.py)
Priority source: follow-up to [wave14x_multihop_N_scaling](../experiments/exp_wave14x_multihop_N_scaling.py)
verdict `MULTIHOP_N_IMPROVES_BUT_BOUNDED` (acc_1hop only +0.01 per
log2(N); substrate width is not the lever for the ~0.95-0.97 1-hop ceiling)
Author: experiment_dev session, pipeline tick 11

## Why

The multi-hop 1-hop ceiling is bounded at ~0.95-0.97 across N ∈ {4096,
8192, 16384} and NUM_FACTS ∈ {50, 100, 200, 400, 800}. Substrate width
slope is +0.01 per log2(N) doubling — too slow to reach 0.99 without
N >> 100k. The bottleneck is not noise from substrate dimensionality;
it's something in the mechanism.

Candidate mechanism hypothesis: the dense random BSC **entity codebook**
creates cross-talk in the cleanup step. Each pair of random ±1 entity
atoms has |IP|/N ~ 1/sqrt(N), with Gaussian tails that occasionally
spike. With NUM_ENTITIES=200 candidates, the cleanup argmax can shift to
a "near-true" entity when the probe has significant noise.

Test: replace the random BSC entity codebook with a Hadamard codebook
(NUM_ENTITIES distinct rows of the Sylvester Hadamard matrix). Hadamard
rows are exactly orthogonal — |IP|/N = 0 between distinct entities.

## Hypothesis

At N=4096 (matches v3), NUM_FACTS=100, HOP_DEPTHS={1, 10, 50}, 3 seeds,
sweeping CODEBOOK_TYPE ∈ {random_bsc, hadamard}:

- Hadamard codebook gives acc_1hop ≥ 0.99 (the 1-hop ceiling lifts because
  cleanup no longer has cross-entity bridges)
- Hadamard codebook gives higher per-hop retention than random BSC
  (each hop's cleanup is tighter)
- Hadamard codebook may NOT help at deeper hops if the bottleneck is in
  bind/superpose, not cleanup

## Multi-probe success criteria

Verdict captures the *comparison* between the two arms:

1. acc_1hop on Hadamard arm ≥ 0.99 → "Hadamard lifts the ceiling"
2. acc_1hop on Hadamard arm > acc_1hop on random arm + 0.02 → "Hadamard
   meaningfully helps"
3. acc_50hop on Hadamard arm vs random arm — does the gap persist at depth?

## Kill criterion

If Hadamard acc_1hop ≤ random acc_1hop + 0.005, the cleanup mechanism
isn't the bottleneck. Verdict `HADAMARD_NO_HELP` — points to binding
or superposition as the mechanism limit. Routes to next-cycle
mechanism investigation.

## Verdict labels (5)

- `HADAMARD_LIFTS_1HOP_CEILING` — Hadamard arm acc_1hop ≥ 0.99 AND
  hadamard - random ≥ 0.02
- `HADAMARD_MEANINGFUL_HELP` — Hadamard > random + 0.02 but < 0.99
- `HADAMARD_NO_HELP` — Hadamard ≤ random + 0.005 (mechanism is elsewhere)
- `HADAMARD_PARTIAL_HELP` — Hadamard > random by 0.005 to 0.02 (small gain)
- `HADAMARD_ENTITIES_INCONCLUSIVE` — missing data

## Oracle assertions (smoke mode)

1. Hadamard entity_codebook is exactly orthogonal: max pairwise |IP|/N < 1e-6
2. Random BSC entity_codebook has pairwise |IP|/N in the expected Gaussian
   range (assert max < 0.30 at smoke scale)
3. At smoke's smallest depth=1, BOTH arms produce acc > 0.80 (sanity)

## Pre-mortem (3 failure causes)

1. **NUM_ENTITIES=200 doesn't fit in NUM_FACTS=100 distractor chain
   without entity collisions**: chain entities need to be distinct;
   200 ≥ 100+1 covers any chain length up to 99 (lower than max_depth=50).
   Fine.
2. **Hadamard codebook breaks the binding algebra**: in BSC, Hadamard_a *
   Hadamard_b = Hadamard_{a XOR b} which IS in the codebook for some
   indices. This means bind products of stored entities land on OTHER
   stored entities, which could shift cleanup in unexpected ways.
   Mitigation: report per-trial bind-collision rate; verdict_msg notes
   if collision rate > 5%.
3. **Hadamard codebook at NUM_ENTITIES=200, N=4096 has 4096 rows
   available but we only use 200 — distractor binds (E_i * E XOR R_i *
   R) might land on a stored E with probability 200/4096 = 5% per bind.
   At NUM_FACTS=100 distractor facts, ~5 expected hits per probe**.
   These could shift cleanup. Mitigation: same as 2.

## Operational definition

Reuses [exp_wave14t_multihop_v3.py](../experiments/exp_wave14t_multihop_v3.py)
core: build_factbase, run_chain, cleanup_argmax. Two arms in one script:

- Arm A (Hadamard): entity_atoms drawn from rows of Sylvester Hadamard at N
- Arm B (random BSC): entity_atoms generated as in v3 (random ±1)

Both arms use the same relation_codebook (random BSC) — only entity
codebook differs.

## Cited mechanism / sources

- wave14e_multi_hop_v2 + wave14t_multihop_v3 (own work): multi-hop infra
- Plate 1995 / Kanerva 2009: BSC binding/cleanup primitives
- Sylvester Hadamard: orthogonal codebook construction
- v1's structured-key intuition: orthogonal codebooks reduce cross-talk

## Expected runtime

- Smoke (N=512, NUM_FACTS=20, depths=[1, 10], 5 trials, 1 seed, 2 arms):
  ~3-6 s on CPU
- Full (N=4096, NUM_FACTS=100, depths=[1, 10, 50], 50 trials, 3 seeds,
  2 arms): ~2-5 min on GPU

## What product decision this enables

- `LIFTS_1HOP_CEILING` → cap_map row "multi-hop reasoning" can move to
  "high-fidelity with Hadamard entity codebook"; mechanism understood
- `MEANINGFUL_HELP` → Hadamard codebook is a recommended product
  configuration; cap_map row notes envelope improvement
- `NO_HELP` → mechanism investigation routes to binding/superposition
  layers (sparse codes, asymmetric binding, etc.)
- `PARTIAL_HELP` → cleanup is part of the bottleneck but not all of it
