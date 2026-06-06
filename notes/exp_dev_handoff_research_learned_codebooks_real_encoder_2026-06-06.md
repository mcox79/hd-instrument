# exp_dev hand-off -- research: learned codebook collision mitigation for real-encoder substrate

## Filed-by
Research sub-agent, 2026-06-06

## Trigger
Research note: notes/research_drill_learned_codebooks_real_encoder_rescue_1x_2026-06-06.md
Topic: Codebook-collision mitigation for real LM encoder embeddings (synthetic 10x vs real 2.75x gap)

## Pause state
Check data/orchestrator_paused.flag before dispatching any GPU anchor.
All three cells (A, B, C) are CPU-only and are NOT pause-gated.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT only.
Exp_dev designs the anchor grid, sweep parameters, threshold formulas, and queue assignment.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY -- CPU, ~30 min)
Pointer: Cell C from research note Section E + Section C
Substrate-product reading: Does sparse Hadamard mixture (k random rows summed, then sign)
  decorrelate the encoder anisotropy bottleneck that limits real-input capacity to 2.75x?
  If yes, this is a zero-training-cost codebook improvement that ships immediately.
Tier hint: CPU; ~30 min wall; no GPU required; no training overhead
Why-now: Cheapest decisive test. Falsifies or confirms the encoder-anisotropy hypothesis.
  If HARD-PASS, codebook change ships in next infrastructure update. If HARD-FAIL, informs
  whether Cell A (learned) is worth the training cost.
Pre-registered bands from research note Section E:
  HARD-PASS: SHM capacity >= 1.5x Hadamard at matched conditions
  MIDDLE-BAND: 1.1x to 1.5x
  HARD-FAIL: <= 1.1x Hadamard

### Anchor 2 (CPU, ~90 min total -- k-means training + benchmark)
Pointer: Cell A from research note Section E + Section A
Substrate-product reading: Does k-means codebook initialization on real MiniLM embeddings
  reduce pairwise coherence enough to recover 2-3x capacity beyond Hadamard?
  This tests the distribution-alignment hypothesis algebraically confirmed by Achilli et al.
  2025 (manifold-aligned codebooks increase capacity) and Bielmeier-Friedland 2025
  (feature correlations reduce capacity prefactor).
Tier hint: CPU; ~30 min k-means + ~60 min substrate bench; no GPU required
Why-now: Run after Anchor 1 result is known. If Anchor 1 passes (encoder IS anisotropic),
  Anchor 2 should show larger gain by targeting distribution precisely.
Pre-registered bands:
  HARD-PASS: learned capacity >= 2.0x Hadamard
  MIDDLE-BAND: 1.2x to 2.0x
  HARD-FAIL: <= 1.2x Hadamard

### Anchor 3 (CPU, ~45 min -- basis pursuit sparse coding)
Pointer: Cell B from research note Section E + Section B
Substrate-product reading: Can a 4x overcomplete dictionary with k=8 sparse codes enable
  3x+ capacity over Hadamard by breaking the V_c <= N_sub ceiling?
  Tests whether Hopfield dynamics are compatible with sparse-support retrieval
  (theoretical backing: arXiv:1611.09621 Ganguli et al. expander decoding).
Tier hint: CPU; ~45 min; no GPU; requires OMP (orthogonal matching pursuit) implementation
Why-now: Run LAST -- highest complexity, highest upside. Informs architecture decision on
  whether to support sparse-code concept addresses in V2 substrate.
Pre-registered bands:
  HARD-PASS: sparse-code capacity >= 3.0x Hadamard
  MIDDLE-BAND: 1.5x to 3.0x
  HARD-FAIL: <= 1.5x Hadamard

---

## Context pointers

- Research note: notes/research_drill_learned_codebooks_real_encoder_rescue_1x_2026-06-06.md
  (algebraic derivations, lit citations, cross-thread synthesis, full hard-fail rescue paths)
- Prior codebook research: notes/research_N65536_codebook_engineering_2026-05-22.md
  (Kerdock as optimal binary codebook for V_c >> N; Hadamard for V_c = N)
- Prior semantic codebook: notes/research_BetP_semantic_codebook_2026-05-21.md
  (context on crowded-field concern; learned VQ is the substrate-specific exception)
- Cap_map: substrate_capability_map.md (VQ codebook row)
- Bielmeier-Friedland 2025: arXiv:2508.01395 (feature correlations reduce capacity prefactor)
- Achilli et al. 2025: arXiv:2503.09518 (manifold hypothesis -- capacity INCREASES with alignment)
- Hu et al. 2024: arXiv:2410.23126 (spherical codes = optimal Hopfield memory config)

---

## Contract

- Exp_dev designs ALL anchor grids, sweep parameters, threshold formulas, and queue assignment.
- Exp_dev does NOT add design elements not present in this file's Anchor descriptions.
- All three cells are CPU-only. No cloud dispatch without explicit orchestrator authorization.
- Timeout formula per [[feedback-per-experiment-timeout-required]] applies.
- ASCII-only in all script output per [[feedback-ascii-only-in-scripts]].
- write_metrics() required per [[feedback-metrics-required-fields-write-metrics]].

## Autonomy declaration

Exp_dev has full autonomy over:
  - Exact N_sub, V_c, FLIP values within the ranges described
  - Whether to use auto-assoc or bidirectional substrate configuration
  - Implementation of OMP for Cell B (any standard library acceptable)
  - Whether to run Anchors 2 and 3 conditioned on Anchor 1 result or unconditionally
  - Queue assignment (all three anchors are CPU, so remote_cpu_queue or laptop_queue)
