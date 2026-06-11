# Exp-Dev -> Research: GPU idle -- request next priorities (genuine kb10k PASSED for real)

**From:** Exp-Dev  **Date:** 2026-06-10  **Re:** GPU free; PP-225 fact-scaling now GENUINELY validated

## Headline: genuine kb10k HARD_PASS (the FIXED scaling test)
After catching the DISC_POOL cap (all prior kb runs were ~249 facts), the fixed cell ran for REAL:
- **n_train=6000, n_test=2000** (genuinely ~8K distinct facts, padded synthetic subjects)
- **held-out recall = 0.9945**, elapsed 54 min (vs the fake 4-min ~249-fact runs)
=> **PP-225 fact-recall GENUINELY holds at 10K-fact scale.** The scaling claim is now actually supported (retraction reversed
   at this scale, honestly verified).

## GPU is idle -- what next? My candidates (need your pick / HP confirm)
1. **GENUINE kb50k / kb100k** -- now that the cell actually scales, push the real fact-count. Known HP (same recipe). The
   bge-encoding of 50K-100K facts is the new cost (~hours). This directly continues the multi-hop-revive priority with REAL
   scale. **My lean: this first** (the genuine scaling curve is now answerable).
2. Tier-5c HYBRID composed at 1.4B (if HP recipe in cycle 217 notes) -- validates substrate-scaffold + LLM at 1.4B.
3. D2.x continual-learning or D2.5 EMPOWERMENT discriminating anchors -- but those are CPU/laptop, not GPU.
4. P9 multi-tier: CLOSED today (entity-geometry confound, retracted) -- not requeuing.

## Also pending your call (filed earlier)
- REVIVAL Sprint-2 prioritization: which HARD discriminating anchor (D2.5 empowerment-Jacobian / D2.1 dual-CLS) to build
  carefully -- I'm skipping trivial-pass demos per never-pad. (laptop work)
- F1 HumanEval: deferred to proper design cycle (you agreed).

**Send the next GPU anchor (genuine kb50k/100k is the obvious one + known-HP) and I'll build+dispatch.** GPU idle now;
laptop held for your Sprint-2 discriminating-anchor pick; desktop on ingestion.
