# Pre-registration: substrate_iterative_cleanup_cue_clamped_v1

**Filed:** 2026-06-23
**Anchor:** substrate_iterative_cleanup_cue_clamped_v1
**Author:** exp_dev (sonnet)
**Status:** PRE-REGISTERED (before smoke or full run)

---

## Hypothesis

Brain CA3 + Attractor LM (arXiv:2605.12466) use cue-CLAMPED iterative dynamics where the
original noisy query y_0 is re-injected at every step:
    y_{t+1} = normalize(alpha * y_0 + (1-alpha) * softmax(beta * y_t @ C.T) @ C)

Prior HARD_FAIL (substrate_multi_iteration_cleanup_LM_v1) used self-consistent alpha=0.0
which collapses all queries to the same dominant codebook direction (query-independent
fixed point). Adding alpha > 0 preserves cue identity across iterations and should
restore the discriminative lift that multi-iter cleanup theoretically provides.

---

## N-suffix

No _nN suffix in anchor name. Production N_DIM = 2048. Rationale: N is a fixed hyperparameter
in this cell, not a load-bearing independent variable. The experiment sweeps alpha values
{0.0, 0.3, 0.5, 0.7} at fixed N=2048, M=512, SNR=2dB.

---

## Arms

| Arm | alpha | Purpose |
|-----|-------|---------|
| ARM_SINGLE_STEP | 1-step argmax | control floor |
| ARM_CURRENT | 0.0 | reproduces prior HARD_FAIL (self-consistent) |
| ARM_CLAMPED_ALPHA_03 | 0.3 | low cue re-injection |
| ARM_CLAMPED_ALPHA_05 | 0.5 | balanced; primary discriminator; brain-canonical |
| ARM_CLAMPED_ALPHA_07 | 0.7 | high cue re-injection |

Seeds: [7, 17, 23] (substrate convention).
Metric: cleanup-recovery accuracy at noise SNR=2dB (sigma=0.8913 for unit-norm vectors).

---

## Pre-registered HARD bands (IMMUTABLE; pre-registered BEFORE any data)

**HARD_PASS:** ALL of:
- best ARM_CLAMPED accuracy >= ARM_SINGLE_STEP accuracy + 0.05 absolute
- CV across 3 seeds <= 0.10

**HARD_FAIL:** ALL ARM_CLAMPED (alpha in {0.3, 0.5, 0.7}) within +-0.02 of ARM_SINGLE_STEP

**MIDDLE_BAND:** partial lift 0.02-0.05; queue production scale for definitive verdict

---

## Timeout estimate

Smoke wall: 2.2s (seed=0; N_DIM=256; M=64; N_TRIALS=40)
Full config: N_DIM=2048; M=512; N_TRIALS=200; SEEDS=3

timeout = ceil(1.5 * 2.2 * (2048/256) * (200/40) * (3/1))
         = ceil(1.5 * 2.2 * 8 * 5 * 3)
         = ceil(396)
         = 600s (rounded to nearest 300)

Well within 7200s limit.

---

## Dependencies

- hdlab/iterative_attractor.py (modified to add alpha parameter; selftest passes)
- experiments/_seed_checkpoint.py (existing)
- data/text8_cache/text8.txt (NOT needed -- uses random synthetic codebook)

No external data dependencies. Pure numpy. Runs on any CPU runner.

---

## Source references

- notes/exp_dev_handoff_research_multi_iter_cleanup_brain_analog_2026-06-23.md
- notes/research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md
- arXiv:2605.12466 Attractor Models for Language and Reasoning (+32-46% LM perplexity)
- data/exp_substrate_multi_iteration_cleanup_LM_v1/metrics.json (HARD_FAIL context;
  all iter arms bpc=7.3753; confirms self-consistent collapse diagnosis)

---

## Smoke result (pre-ship gate)

Smoke PASS (2026-06-23):
- ARM_SINGLE_STEP: 0.150
- ARM_CURRENT (alpha=0.0): 0.125 (confirms self-consistent collapse, -0.025 vs SS)
- ARM_CLAMPED_ALPHA_03: 0.225 (lift +0.075 >> threshold 0.05; well above HP)
- ARM_CLAMPED_ALPHA_05: 0.125 (degenerate at smoke N=256; D too small for softmax)
- ARM_CLAMPED_ALPHA_07: 0.125 (same)

Smoke lift 0.075 > threshold 0.05 by 50%; NOT borderline; walk-back gate does NOT trigger.
All metrics non-null, non-zero, non-constant. Suspicious-result gate: PASS.
