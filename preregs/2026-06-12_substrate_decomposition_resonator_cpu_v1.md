# Pre-registration: Cell B -- Decomposition benchmark (resonator explaining-away decode)

**Date:** 2026-06-12 (Day 4 Cycle 50)
**Cell:** experiments/exp_substrate_decomposition_resonator_cpu_v1.py
**Routing:** research_to_exp_dev_testbed_5_NEW_CELLS Cell B + VSA-drill pre-reg LOCK. Substrate-quality-first; NO LLM frame.
**Lane:** local_cpu_queue (laptop CPU).

## Design
Bound state X = sum_{i=1..F} bind(R_i, B_i) (normalized), roles UNITARY + KNOWN, fillers from a K-atom codebook subset of the
280-atom algebra_hrr corpus. Resonator-style explaining-away decoder: iteratively refine each filler estimate by removing the
binding contributions of the OTHER current estimates, then cleanup against the codebook. precision@1 = fraction of slots
decoded to the true filler. Sweep F in {2,3,4,6,8}; K in {50,100,280}; additive noise in {0,0.1,0.3}; 3 seeds x 20 trials.
Canonical circular-convolution HRR (matches hdlab.binding real path).

## Pre-registered verdict bands (decode metric = precision@1; clustered codebook tw_edge_z=-2.26 UNCHARTED regime)
- **HARD-PASS:** precision@1 >= 0.95 at F=2,K=280,noise=0 AND precision@1 >= 0.80 at F=3,K=280,noise=0.
- **MIDDLE:** precision@1 0.50-0.80 at F=3,K=280,noise=0.
- **HARD-FAIL:** precision@1 < 0.50 at F=3,K=280,noise=0.
- **UNKNOWN:** corpus load fails.

## Uncharted-regime probe
Frady-Sommer cliff ~ D^2/(F^2 K). The K-sweep + noise-sweep reveal whether the substrate's clustered codebook LIFTS decode
(clusters discriminate; effective K smaller) or HURTS it (intra-cluster crowding; effective K larger via collisions) vs the
uniform-codebook prior. Either outcome is informative (literature-is-not-oracle).

## Substrate-product artifact (stands alone, no LLM frame)
Whether the substrate DECODES superposed structured representations back to their constituent atoms (substrate > atom-set),
and the decode-capacity scaling vs F, codebook size K, and additive noise on its real clustered codebook.
