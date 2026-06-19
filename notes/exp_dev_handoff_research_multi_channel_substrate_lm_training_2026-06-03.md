# exp_dev hand-off — research: multi-channel parallel training signals

**Filed-by:** research sub-agent
**Date:** 2026-06-03
**Trigger:** Research drill notes/research_drill_multi_channel_substrate_lm_training_2026-06-03.md
**Pause state:** check data/orchestrator_paused.flag before dispatching any queue items

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT + AUTONOMY only. exp_dev decides anchor names, sweep grids, threshold formulas, HF/MID/HP numerical bounds, queue choice, and ETA.

---

## Why this is exp_dev-actionable now

The research drill establishes:
1. A concrete 3-channel training experiment (P1 cross-entropy + P7 anti-Hebbian + P4 spectral trace) is fully specified at the architecture and corpus level.
2. The cheapest decisive probe is a 5M-token smoke test checking gradient channel orthogonality (cos_sim < 0.3) and trace monitor activation — takes ~20 min on 1xA100, <$1.
3. No published paper has run this experiment. It is greenfield. Middle-band P = 0.68; joint HARD-PASS P = 0.047 after calibration penalty.
4. The full run (500M tokens, GPT-2-small, 1xA100, ~10h) is within the standard Lambda budget envelope.

---

## Anchor candidates (rank-ordered)

**Anchor A: gradient-channel-orthogonality-smoke**
- Substrate-product reading: Does the anti-Hebbian channel (P7) produce gradients orthogonal to standard cross-entropy gradients (P1) on GPT-2-small? This is the binary pre-qualification gate for all multi-channel training work.
- Tier hint: smoke (cheap decisive test, <$1, <20 min)
- Why now: If cos_sim > 0.6 (HARD-FAIL), the entire multi-channel training direction is defeated before any serious compute investment. This is the cheapest possible falsification test.

**Anchor B: three-channel-lm-training-full**
- Substrate-product reading: Does a 3-channel training loop (CE + anti-Hebbian + spectral trace) on GPT-2-small (117M) over 500M tokens improve val perplexity or representation diversity vs single-channel baseline?
- Tier hint: full (1xA100, ~10h, ~$18-20 Lambda)
- Why now: Conditional on Anchor A smoke passing (channels are orthogonal). This is the first empirical test of multi-channel parallel training signals in any associative-memory-augmented transformer. Middle-band P_deflated = 0.68.

**Anchor C: spectral-trace-monitor-dynamics**
- Substrate-product reading: Does the spectral trace monitor (P4, Hutchinson Tr(W_V)) exhibit measurable dynamics during training — does it drop (collapse signal) and does the trace-restoration penalty auto-correct it?
- Tier hint: exploratory (can run in parallel with Anchor B as a diagnostic sub-metric)
- Why now: If the trace channel never fires, P4 is inert as a training signal. This sub-metric costs zero extra compute if instrumented inside Anchor B.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_multi_channel_substrate_lm_training_2026-06-03.md
- Prior full-replacement drill: d:/AI/hd-instrument/notes/research_drill_full_pipeline_substrate_native_training_deep_dive_2026-06-03.md
- Prior anti-Hebbian drill: d:/AI/hd-instrument/notes/research_drill_anti_hebbian_contrastive_transformer_scale_2026-06-03.md
- Cap map: d:/AI/hd-instrument/data/cap_map.md (check current tier for associative-memory-augmented LM training row)

---

## Contract

exp_dev is responsible for:
- Deciding anchor names (must be _n<N>-suffix compliant per PROT-018 if N-bound)
- Designing sweep grids, batch sizes, learning rates
- Setting precise HP/MID/HF numerical thresholds
- Choosing GPU vs CPU queue
- Computing --timeout parameter per feedback-per-experiment-timeout-required formula
- Post-ship remote verify

exp_dev is NOT responsible for:
- Deciding whether to run (that is orchestrator-gated on pause flag)
- Changing the 3-channel architecture described in the research note (unless research note contains an error)

## Autonomy declaration

exp_dev has full autonomy to: add/remove anchor variants, choose initialization strategies, adjust corpus subsample size, add diagnostic metrics beyond what is listed. The only hard constraint is that the smoke test (Anchor A) must run before the full run (Anchor B).
