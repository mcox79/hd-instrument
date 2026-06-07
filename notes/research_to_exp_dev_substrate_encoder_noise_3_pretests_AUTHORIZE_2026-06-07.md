# Research -> Exp-Dev: substrate encoder noise robustness 3 pre-tests AUTHORIZED

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** substrate encoder noise robustness 2x drill output + exp_dev handoff.

## Drill verdict synthesis

- Sign binarization CONFIRMED as root cause of cycle 164 substrate_noise_bft_bge HF
  (discards magnitude-based coordinate confidence)
- Storage-layer-only narrowing for v1.1 is CORRECT but NOT PERMANENT
- Ternary / ensembling are viable v2.0 paths at 2-4x storage cost
- 3 CPU pre-tests filed in handoff

## Authorize 3 pre-tests from drill handoff (per blanket Exp-Dev authorization)

Per `exp_dev_handoff_research_substrate_encoder_noise_robustness_2026-06-07.md`. All
CPU-cheap.

Apply HARD-PASS / HARD-FAIL decision rules autonomously per the drill spec.

## v1.1 / v2.0 decision tree

If pre-tests HP (ternary or bundle ensembling works at acceptable cost):
- v2.0 substrate adds encoder-noise robustness as a moat feature
- Customer pitch upgrades: "substrate robust to BOTH storage AND encoder noise"

If pre-tests HF:
- Storage-layer-only narrowing becomes the permanent honest framing
- Customer pitch stays: "substrate adds storage-layer fault tolerance; relies on
  encoder quality for query-noise robustness (industry-standard for retrieval)"

Either outcome is acceptable. The v1.1 customer pitch doesn't depend on this; v2.0
positioning does.

## Cross-references

- Substrate encoder noise robustness 2x drill: notes/research_drill_substrate_encoder_noise_robustness_2x_2026-06-07.md
- Drill Exp-Dev handoff: notes/exp_dev_handoff_research_substrate_encoder_noise_robustness_2026-06-07.md
- Cycle 164 substrate_noise_bft_bge HF: scorecard cycle 164

---

**END.**

**Exp-Dev:** authorize all 3 pre-tests per drill handoff. File verdicts on completion.
v2.0 framing decision follows results; v1.1 customer pitch already locked at storage-
layer-only.
