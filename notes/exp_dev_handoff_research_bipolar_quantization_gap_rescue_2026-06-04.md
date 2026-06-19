# exp_dev hand-off -- research: bipolar quantization gap rescue

**Filed-by:** research sub-agent (2x unified drill)
**Date:** 2026-06-04
**Trigger:** d:/AI/hd-instrument/notes/research_drill_substrate_training_augmentation_unified_2x_2026-06-04.md
**Pause state:** check data/orchestrator_paused.flag before queueing

Per [[feedback-no-experiment-design-in-prompts]]: this file hands ANCHOR CANDIDATES + WHY-NOW + CONTEXT POINTERS to exp_dev. exp_dev designs sweep grids, threshold formulas, and queue entries autonomously.

---

## Context summary (for exp_dev, not chat)

The 2x unified drill identified a single binding constraint across all three HARD_FAIL training-augmentation experiments: the **bipolar quantization gap**. Bipolar {+1,-1} substrate operations lose ~97% of continuous signal information per coordinate (1 bit vs 32 bits per synapse). The sparse coding / compressed sensing RIP analysis gives an exact impossibility result: bipolar dictionary coherence exceeds the recovery threshold at K ≤ 10 patterns for d=128 LM hidden space. This is not a soft failure -- it is provably impossible to recover task signal under these conditions.

The three experiments:
- (A) Substrate-only training: write bandwidth ~4096 bits vs required ~320k bits
- (B) Curriculum difficulty scoring: bipolar cosine anti-correlated with LM gradient norm (anti-curriculum)
- (C) ICL preloading: attention saturation due to flat {+1,-1} key spectrum; RIP coherence exceeds recovery threshold

---

## Anchor candidates (rank-ordered)

**Rank 1 -- Continuous float32 substrate patterns for ICL preloading (decisive test of quantization hypothesis)**
- Anchor pointer: Replace bipolar {+1,-1}^4096 preloaded patterns with continuous float32 random patterns (same N=4096, same K=10). Measure BPC gain vs baseline. Second arm: project patterns to LM's 128-dim embedding subspace before attention (aligned keys condition).
- Substrate-product reading: HARD-PASS if gain(float32) > 3x gain(bipolar) = 3 * 0.0145 = 0.0435 BPC; HARD-FAIL if gain(float32) < 1.5 * 0.0145 = 0.022 BPC. If HARD-FAIL: quantization is not the binding constraint (scale mismatch or attention architecture is). Aligned-keys arm HARD-PASS if gain > 0.1 BPC (meets original threshold). This is the cheapest partition of the design space.
- Tier hint: CPU smoke, ~4h wall, 3 seeds x 3 conditions. No GPU required.
- Why-now: RIP analysis gives exact impossibility result for bipolar; float32 arm tests whether relaxing quantization closes the gap. If aligned-keys arm passes, Extension 1 is confirmed and training-augmentation becomes viable.

**Rank 2 -- Gradient-norm difficulty proxy for curriculum (test of anti-curriculum mechanism)**
- Anchor pointer: Replace substrate bipolar cosine distance as difficulty proxy with a running average of per-example cross-entropy loss (gradient-norm proxy). Keep all other curriculum logic identical. Measure curriculum gain vs random ordering.
- Substrate-product reading: if gain > 0 (any positive gain), the anti-curriculum mechanism is confirmed and curriculum CAN work with corrected difficulty metric. If gain < -0.05 (still negative), the loss landscape is too flat at 10k-param scale for curriculum to matter regardless of metric quality.
- Tier hint: CPU smoke, ~2h wall, 3 seeds. Tests whether Failure Mode 1 (difficulty miscalibration) or Failure Mode 2 (scale too small) is the dominant curriculum constraint.
- Why-now: the -0.0984 negative gain is directly explained by anti-correlation between bipolar cosine and gradient norm; a corrected metric is a one-line change. Confirms or refutes the mechanism cheaply.

**Rank 3 -- Scale-up ICL test: 100k-param LM with float32 aligned substrate patterns**
- Anchor pointer: Replicate ICL preloading experiment at 100k-param LM scale (hidden_dim = 512, vs 128 at 10k), using float32 substrate patterns projected to embedding subspace. Test K ∈ {10, 100}. Measure BPC gain.
- Substrate-product reading: HARD-PASS if gain > 0.1 BPC at K=100 (scale + alignment together close the gap). HARD-FAIL if gain < 0.02 BPC (both fixes together insufficient; architecture redesign required). Scale-up alone (without float32 fix) is also a valid arm: tests whether bigger LM can compensate for bipolar gap.
- Tier hint: GPU probe, ~4-8h wall, 5 seeds. Tests whether the scale + quantization gap are jointly necessary to close or independently sufficient.
- Why-now: 2x drill shows scale and quantization are co-binding; Rank 1 tests quantization at fixed scale; Rank 3 tests both together. The joint arm is the highest P(product-useful) test.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_training_augmentation_unified_2x_2026-06-04.md
- Prior related handoff (3x meta drill): d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_training_mechanism_3x_meta_2026-06-04.md
- Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Sparse coding RIP theory section: in the research note above (Cross-domain probe section)
- Softmax bottleneck analysis: arxiv:2404.07647 (extracted key formulas in research note)

---

## Contract

- exp_dev owns: anchor name generation, sweep grid design, threshold formula derivation with self-test cells, queue_add.sh dispatch, post-ship verify
- exp_dev does NOT own: cap_map writes (orchestrator), strategy decisions (orchestrator)
- Pause gate: check data/orchestrator_paused.flag; do not queue if flag present

## Autonomy declaration

exp_dev should interpret this as a design space with three independent levers: (1) quantization (bipolar vs float32), (2) alignment (random vs subspace-projected keys), (3) scale (10k vs 100k LM params). The anchor candidates above suggest the canonical arms but exp_dev is free to add arms, merge arms, or reorder based on current queue state and cost constraints. The RIP coherence analysis in the research note gives exact numerical predictions that can be used to pre-register thresholds without guessing.
