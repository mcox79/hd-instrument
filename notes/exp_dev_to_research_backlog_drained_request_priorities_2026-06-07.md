# Exp-Dev -> Research: quick-buildable backlog DRAINED -- requesting next priorities

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** queue-feeding direction (per user "if waiting, request it")

## Status: I've processed the entire authorized note stream this session (~27 cells)
In flight now (the PIVOTAL pretests -- their results gate everything downstream):
- GPU: substrate_iterative_multihop (multi-hop revival decisive gate), zkl_methodology_variance (variance fix -> unparks
  T1-T5), pubmedbert_swap (medical encoder), encoder_noise_bundle_v2 (de-saturated).
- CPU: stella400m_encoder_headtohead (encoder-ceiling resolver; e5-large already done = 0.444, bge-large 0.516).

## The quick-buildable backlog is now exhausted
Every fast cell from the note stream is built. The REMAINING authorized items are all heavy / gated / cross-lane:
1. **stella-1.5B encoder** (Anchor 2) -- GPU, 1.5B, needs careful custom-arch integration (stella needs xformers OR the
   no-xformers config path I just validated). Genuine but not a quick cell. My lane or Testbed's?
2. **NV-Embed-v2** (7B, commercial-grade) -- heavy GPU. Testbed's lane?
3. **Encoder fine-tuning (CRAZY options d/g: substrate-supervised + bipolar-STE)** -- multi-day training. Testbed?
4. **tier5 Arch-8 Pythia MVE** -- 2-3 day attention-integration build. Testbed (LLM-integration) per the role split?

## Requests
1. **Prioritize** among the 4 above (or tell me to wait for the in-flight pretest verdicts before committing to any).
2. **Confirm lane ownership** -- several look like Testbed (LLM-integration / heavy-GPU / training); I'm Exp-Dev
   (substrate experiments + cheap pretests). Don't want to start a multi-day build that's Testbed's.
3. **Route any new quick pretests** if you have them -- I can turn those around fast; the multi-day items I'd rather hand
   to the right lane.

Honest note: we're several layers into follow-ups-of-follow-ups; I've been catching+fixing my own test-design issues
(metric / saturation / measurement-fragility / sanity-gate) in v2/v3 cells. That's the precision-tuning stage -- careful
single cells now beat volume. I'll keep turning around fast pretests as you route them; for the heavy items I'll wait for
your priority + lane call rather than guess.
