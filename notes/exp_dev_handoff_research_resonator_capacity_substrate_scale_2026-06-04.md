# exp_dev hand-off -- research: resonator capacity at substrate-class N (2x)

Filed-by: research sub-agent
Trigger: notes/research_drill_resonator_capacity_at_substrate_scale_2x_2026-06-04.md
Pause state: check data/orchestrator_paused.flag before queuing

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev determines all anchor names, sweep
grids, threshold formulas, queue routing, and timing. This file provides TASK + WHY + CONTRACT
only.

---

## Anchor candidates (rank-ordered)

### 1. Dense resonator K sweep at N=4096 [TIER: smoke, CPU, ~5 min]
Anchor pointer: dense resonator factorization, K=5 to K=11, V=100, >=99% accuracy
Substrate-product reading: confirms N^2 scaling law at substrate-class N; sets baseline K_max
    for Mode 4 NC1 capability claim
Tier hint: rung-1 CPU smoke -- cheapest possible; no GPU needed
Why now: routing_mode4_resonator_falsifier_test_2026-06-04.md ships today; this sweep
    characterizes the CAPACITY ENVELOPE (not just single K)
Pre-reg: HARD-PASS K_max >= 8; MIDDLE 5-7; HARD-FAIL K_max < 5

### 2. Noise-injected resonator (IMF) at N=4096 [TIER: CPU, ~30 min]
Anchor pointer: resonator with gaussian noise injection (sigma ~ 0.05-0.2) per iteration,
    K sweep 5-15, N=4096
Substrate-product reading: 50x search-space extension with zero codebook redesign; if confirmed,
    default-on for all resonator substrate implementations
Tier hint: CPU; the 2024 result used D in {1000,1500,2000} so N=4096 is a genuine extension
Why now: immediately actionable if the sweep PASSES; adds no implementation overhead

### 3. Sparse resonator K=26 at N=4096 [TIER: CPU, ~1 hr]
Anchor pointer: sparse resonator (f=0.05 activity fraction), codebook of 26 factors (letter
    alphabet), N=4096
Substrate-product reading: K=26 at N=5000 was published (Cunningham 2024); K=26 at N=4096
    (smaller N) is the product-relevant test for char-LM language decoding
Tier hint: CPU; sparse ops are efficient; no GPU needed at N=4096
Why now: flagship upgrade path; K=26 is a concrete capability milestone for language applications

### 4. Position-bound sequence resonator at N=4096 [TIER: CPU, ~30 min]
Anchor pointer: VSA sequence with position keys, K=10-50 positions, V=70 content codebook,
    known position keys (not recovered), N=4096
Substrate-product reading: K_max ~ sqrt(N) ~ 43 at N=4096; tests whether 30-character sequences
    are decodable by substrate resonator -- the primary language-NC1 path
Tier hint: CPU; position keys are precomputed; no training needed
Why now: directly connects to routing_position_binding_combined_architecture_bundle_e_2026-06-04.md

---

## Context pointers

- Research note: notes/research_drill_resonator_capacity_at_substrate_scale_2x_2026-06-04.md
- Operating modes drill: notes/research_drill_substrate_operating_modes_beyond_single_pass_2x_2026-06-04.md
- Position binding drill: notes/research_drill_delinguistification_position_binding_2x_2026-06-04.md
- Mode4 falsifier routing: notes/routing_mode4_resonator_falsifier_test_2026-06-04.md
- Position binding routing: notes/routing_position_binding_combined_architecture_bundle_e_2026-06-04.md
- Frady-Sommer 2020 NeCo Part 2: https://direct.mit.edu/neco/article/32/12/2332/95653/
- Noise injection paper: arXiv:2412.00354
- Sparse resonator: arXiv:2404.19126

---

## Contract

exp_dev owns:
    - All anchor names, sweep grid parameters, threshold formulas, queue routing, ETA
    - Rung/ladder assignment (rung 1-2 CPU first per small-scale-first methodology)
    - Pre-reg with explicit HP/MID/HF bands per envelope-expansion-fail-bands protocol
    - Per-experiment --timeout calculation per feedback-per-experiment-timeout-required

Orchestrator approves:
    - Queue dispatch authorization (check pause flag)
    - Cap_map update after verdict

Research provides (this file):
    - TASK: four experiments ranked by information value and cost
    - WHY: substrate-product implications for each
    - CONTRACT: boundaries above

---

## Autonomy declaration

exp_dev has full autonomy over implementation details within the anchor candidates listed above.
Research recommends sequencing cheapest first (smoke -> CPU -> GPU if needed). Do not pad with
marginal variants per [[feedback-no-padding-experiments]].
