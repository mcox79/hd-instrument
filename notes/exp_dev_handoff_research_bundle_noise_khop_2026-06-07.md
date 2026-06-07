# exp_dev hand-off -- research: bundle noise K-hop accumulation Chain3-Drill3

Filed-by: research sub-agent
Trigger: notes/research_drill_substrate_production_scaling_5x_chain3_drill3_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and WHY, not sweep
grids, threshold formulas, or queue choices.

---

## Anchor Candidates (rank-ordered)

### 1. khop_bundle_noise_B2_sweep_v1  [CHEAP DECISIVE TEST]
- Substrate-product reading: K-hop SNR sweep with 2-shard bundling (B=2) at coordinator.
  Tests whether noise accumulation is polynomial (K_max >= 18) or exponential (K_max < 15).
  This is the single cheapest test that resolves the exponential vs polynomial noise model.
  Result directly determines whether v2/v3 cross-shard K-hop architecture is noise-safe.
- Tier hint: CPU smoke; ~2h wall; Tier-1 (blocking decision gate for v2 architecture viability)
- Why now: Drill 3 noise model predicts K_max(B=2) = 18-22 (polynomial pinv denoising).
  If K_max < 15, the model is wrong and all K-hop scaling estimates need revision.
  HARD-PASS: K_max >= 18. HARD-FAIL: K_max < 15.

### 2. khop_bundle_noise_B10_sweep_v1
- Substrate-product reading: K-hop SNR sweep with 10-shard bundling (B=10) at coordinator.
  B=10 corresponds to LSH two-tier fan-out in v2 architecture at S=10K shards.
  Tests whether LSH pre-filter (B_eff ~ 10-20) actually maintains K_max >= 12 as predicted.
- Tier hint: CPU smoke; ~2h wall; Tier-1 (confirms v2 architecture viability under production fan-out)
- Why now: K_max(B=10) >= 12 is the minimum requirement for v2 K=12 workloads.
  HARD-PASS: K_max >= 12. HARD-FAIL: K_max < 8.

### 3. khop_sparse_key_intermediate_sweep_v1  [HIGHEST LEVERAGE]
- Substrate-product reading: K-hop sweep using sparse-KEY encoding (alpha=0.005) for
  intermediate query vectors instead of dense queries (alpha=0.05). Tests whether sparse-KEY
  composition at intermediate hops reduces per-hop noise by ~sqrt(10) as predicted, increasing
  K_max by up to 3x at zero architectural cost. This is a configuration change, not a new
  feature -- sparse-KEY is already in the substrate (cycle 142).
- Tier hint: CPU; ~3h wall; Tier-1 (potentially unlocks v3 architecture viability)
- Why now: if K_max triples under sparse-KEY intermediates, v3 S=10^6 shards with B_eff=100
  becomes noise-safe (K_max ~ 45-60 vs 8-14 for dense). This is the highest-leverage
  unexplored mechanism in the current substrate.
  HARD-PASS: K_max(sparse, B=10) >= 30. HARD-FAIL: K_max(sparse, B=10) < 14 (no improvement).

### 4. khop_kmax_curve_fit_v1  [VALIDATION + MODEL SELECTION]
- Substrate-product reading: Fit K_max(B) curve from anchors 1 and 2 (plus baseline B=1).
  Tests polynomial fit (K_max ~ 20/sqrt(B)) vs exponential fit (K_max ~ 20*exp(-B/tau)).
  Distinguishes the pinv-denoising hypothesis from Hebbian-like multiplicative noise model.
  Resolves the theoretical model uncertainty for all future K-hop scaling estimates.
- Tier hint: CPU (analysis only, uses Cell B + C outputs); <30 min wall; Tier-1 (model selection)
- Why now: depends on anchors 1 and 2 completing first.
  HARD-PASS: polynomial fit R^2 > 0.90. HARD-FAIL: exponential fit is better.

---

## Context Pointers

- Research note (Drill 3): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill3_2026-06-07.md
- Prior Drill 2 (algebraic relay): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill2_2026-06-07.md
- Prior Drill 1 (architectural gap): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill1_2026-06-07.md
- Phase 2 GOLD (K-hop biggest gap): check notes/ for phase2_5x_chains_gold file from MEMORY.md
- Sparse-KEY prior result: cycle 142, alpha=0.005 sparse-KEY -- check data/ for metrics
- Cap map: d:/AI/hd-instrument/data/cap_map.md (K-hop and cross-shard rows)

---

## Contract

exp_dev owns: anchor design, sweep grids, threshold formulas, queue routing, pre-reg bands,
self-test verification.
research handed off: anchor names, WHY, tier hints, context pointers.
exp_dev does NOT inherit the specific numerical thresholds from this file as binding contracts
-- it pre-registers its own per [[feedback-envelope-expansion-fail-bands]].

Anchors 1 and 2 are independent (run in parallel). Anchor 4 depends on 1+2 completing.
Anchor 3 is independent and can run in parallel with 1+2.

## Autonomy Declaration

exp_dev has full autonomy over anchor implementation, smoke-gate design, and queue placement.
The four anchors above are ordered by strategic priority; exp_dev may reorder, split, or combine
based on current queue state and runner availability.
