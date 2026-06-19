# exp_dev hand-off -- research: multi-channel scale differentiation

Filed-by: research sub-agent
Date: 2026-06-04
Trigger: notes/research_drill_multi_channel_scale_differentiation_3x_2026-06-04.md

## Pause state block

This handoff was written while experiments may be paused. exp_dev MUST check data/orchestrator_paused.flag before queuing any anchor. Do not auto-queue; present anchor candidates to orchestrator for selection.

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY pointers only. exp_dev designs the sweep grid, threshold formulas, HP/HF numerical bounds, and queue routing autonomously based on the research note. No inline experiment design is provided here.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY): Bottleneck adaptor orthogonality test at LM rung 1 (10k params, N=4096)

Anchor pointer: rung-1-orthogonal-adaptor
Substrate-product reading: Insert a K*h linear map M between substrate modulator signals and LM hidden states, trained with orthogonality regularization ||M^T M - I||_F. If this structural fix causes norm_ratio to exceed 0.50 WITHOUT scale increase, it proves that channel collapse is a coupling architecture failure, not a scale threshold. This is the cheapest possible test of the multi-channel hypothesis.
Tier hint: CPU / local smoke (only 10k param LM; adds K*h ~ 128-256 params)
Why-now: Cheapest falsifiable intervention; testable before rung 2 is queued; resolves whether scale increase is necessary at all.

### Anchor 2: K-reduction sweep at rung 1 (K=2 vs K=4 vs K=8 at N=4096, LM 10k)

Anchor pointer: rung-1-K-sweep
Substrate-product reading: Biology and MTL theory predict K_optimal ~ 2-3 for N=4096. Testing K=2 (cf-RPE only + one sparse gate) against K=4 and K=8 at rung 1 directly measures whether K reduction recovers channel distinctness. Expected outcome per theory: K=2 shows norm_ratio > 0.40; K=8 shows norm_ratio < 0.35.
Tier hint: CPU / local smoke (rung-1 scale, 5 seeds per K value)
Why-now: Directly tests the K_optimal ~ 2-3 prediction; requires zero scale increase; costs less than rung-2 run.

### Anchor 3: Rung-2 joint D+H test (LM 100k, N=4096, K=4 and K=8)

Anchor pointer: rung-2-joint-DH-100k
Substrate-product reading: At LM ~100k params (h~128), the router has 4x headroom over the h >= 4*K threshold. Research predicts norm_ratio should improve to 0.35-0.45 at this scale even if BPC differentiation threshold (>= 0.05 nats) is not crossed. The diagnostic metrics (norm_ratio + channel cosine similarity) are as important as primary BPC. Middle-band outcome (norm_ratio 0.40-0.50 with BPC delta < 0.05) still provides strong evidence that rung 3 will cross.
Tier hint: GPU (100k LM params is modest but 5-seed sweep with 3 K-values + diagnostics warrants GPU)
Why-now: Next natural rung after rung-1 confirmation; P_deflated 0.22 for K=4 differentiation; cheap relative to rung 3.

### Anchor 4: Rung-3 joint D+H test (LM 1M, N=4096, K=4)

Anchor pointer: rung-3-joint-DH-1M-K4
Substrate-product reading: At 1M params (h~512), effective rank ~ 50-80, router headroom 16x over h >= 4*K threshold, and K=4 channels are expected to be comfortably linearly independent. P_deflated 0.40 for BPC differentiation >= 0.05 nats. This is the primary scale hypothesis test.
Tier hint: GPU (1M params + 5 seeds warrants dedicated GPU run; estimate ~2-4h wall)
Why-now: Conditional on rung-2 middle-band or hard-fail result; do not queue before rung-2 verdict.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_multi_channel_scale_differentiation_3x_2026-06-04.md
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Prior verdict (rung-1 5-arm ablation, all arms BPC 3.73-3.81): referenced in task context
- Architecture constraint (SKAH-M confirmed): d:/AI/hd-instrument/notes (project_substrate_skahm_class_confirmed_2026-05-27 memory file)

---

## Contract

exp_dev autonomously:
- Designs sweep grid, seed count, timeout formula
- Selects queue (local_cpu / local_gpu / cloud)
- Writes pre-reg HP/HF/MID bands per envelope-fail-bands feedback
- Verifies non-collision with existing queue names before ship
- Does NOT commit to cap_map (orchestrator only)

## Autonomy declaration

exp_dev has full autonomy over experiment implementation details. This file specifies WHAT to test and WHY; HOW is exp_dev's domain. Bottleneck adaptor orthogonality test (Anchor 1) is the recommended starting point as cheapest and most informative.
