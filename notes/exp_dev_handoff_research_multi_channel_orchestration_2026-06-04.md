# exp_dev hand-off -- research: multi-channel gradient orchestration failure (3x drill)

**Filed-by:** research sub-agent
**Date:** 2026-06-04
**Trigger:** notes/research_drill_multi_channel_orchestration_failure_3x_2026-06-04.md
**Per [[feedback-no-experiment-design-in-prompts]]:** This file names anchor candidates and WHY-NOW rationale only. exp_dev designs the sweep, chooses grid parameters, sets HF/MID/HP thresholds, and selects queue.

---

## Pause state block

Experiments are gated on data/orchestrator_paused.flag. exp_dev must check the flag before dispatching. This handoff is discoverable on emergency-refill cycles.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (highest priority): K=2 tonic-only baseline with gradient sum
- **Substrate-product reading:** Cheapest test of whether the multi-channel auxiliary loss concept has ANY validity at current model scale. K=2 eliminates all four failure modes (no PCGrad cycles, sigma_k has unique minimum, capacity bottleneck reduced, scale remains the same but is less binding). If this fails, the entire auxiliary orchestration approach requires scale-up before further iteration.
- **Tier hint:** Smoke/scoping -- fast, local CPU, 3 seeds. Should converge within minutes.
- **Why now:** Zero-seed convergence result was at K=8. We need to know if K=2 rescues convergence before committing GPU time to scale-up experiments. This is the cheapest possible decisive test.

### Anchor 2: Gradient correlation matrix diagnostic
- **Substrate-product reading:** Measures the empirical conflict geometry of the K=8 channel set. Computes G_{ij} = E[cos(theta_{ij})] over 100 training steps. Outputs the K x K correlation heatmap and flags channel pairs with |cos| > 0.3. Determines whether the cycle-pathology hypothesis (the primary binding constraint identified in the research note) is correct.
- **Tier hint:** CPU diagnostic, no full training needed. ~50-100 training steps, 3 seeds.
- **Why now:** If the correlation matrix shows near-orthogonal channels (|cos| < 0.1 for most pairs), the PCGrad cycle pathology is NOT the primary failure mode and the research note's binding-order diagnosis needs revision. If it shows high conflict (|cos| > 0.5), the diagnosis is confirmed and R2 (channel pruning) is the correct next step.

### Anchor 3: sigma_k EMA stabilization + phasic/tonic decoupling (R4+R5)
- **Substrate-product reading:** Tests whether the sigma_k collapse failure mode can be fixed by: (a) EMA-smoothing phasic loss signals before sigma_k update, (b) separating phasic channel weights from learned precision (fixed weight = 0.1 for phasic channels), (c) clipping sigma_k to [0.01, 100]. Run K=8 architecture with these fixes at current scale (10k params).
- **Tier hint:** CPU, 3 seeds, same scale as the failed run. If sigma_k fix alone resolves convergence, scale-up is not necessary for the current model.
- **Why now:** R4+R5 are engineering fixes with no capacity cost. If they work at 10k params, this validates the sigma_k collapse as the PRIMARY binding constraint rather than PCGrad cycles.

### Anchor 4: Scale-up to 100k params with K=4 MGDA (R1+R3 combined)
- **Substrate-product reading:** Tests whether K=4 channels at 100k-param scale with MGDA (instead of PCGrad) converges and provides lift over single-task baseline. This is the full redesign test combining the two highest-leverage changes. If this passes HP2, multi-channel orchestration is viable at 100k+ scale with K=4.
- **Tier hint:** GPU, 3-5 seeds, FULL run. Requires model scale-up and MGDA implementation.
- **Why now:** Anchor 1 and 2 should come first (they're cheaper and diagnostic). Anchor 4 is the target state if anchors 1-3 confirm the failure mode hypotheses.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_multi_channel_orchestration_failure_3x_2026-06-04.md
- HARD-PASS / HARD-FAIL thresholds pre-registered in research note (HP1, HP2, HP3, HF1, HF2, HF3)
- P_deflated baseline: K=8 at 10k params = 0.05-0.08; K=4 at 100k params with R1-R5 = 0.40-0.50
- Prior zero-convergence result: K=8, 3 seeds, ~10k params -- the specific run motivating this drill

---

## Contract section

exp_dev owns: anchor selection from the ranked list above, experiment grid design, threshold formula derivation, queue selection (CPU vs GPU), ETA estimation, and pre-reg per envelope-fail-bands. exp_dev does NOT receive inline sweep parameters, numerical thresholds, or queue assignments from this handoff.

## Autonomy declaration

exp_dev has full autonomy to: reorder anchors based on current queue state, merge anchors into a single batch if they share a bootstrap, skip anchors already in queue under different names, and propose additional rescue anchors not listed here if the gradient correlation diagnostic reveals an unexpected result.
