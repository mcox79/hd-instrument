# Research -> Exp-Dev: URGENT ZKL entropy-max real-encoder validation + ZKL alternatives T1-T5 defense-in-depth

**From:** Research session
**To:** Exp-Dev (primary)
**Date:** 2026-06-07
**Re:** Cycle 164 zkl_hypC_entropy_max HP CONDITIONAL (synthetic only); ZKL alternatives
3x drill delivered top-5 pre-tests T1-T5.

## PRIORITY 1: zkl_hypC_entropy_max real-encoder validation (URGENT)

Cycle 164 result: α=1.00 entropy-max whitening drops ZKL from 0.40 baseline to 0.030
(below HIPAA absolute 0.10) with F1 unchanged. BUT sanity_ok=False — synthetic harness
only. The synthetic-vs-real-encoder gap has burned us before (cycle 159 T5 paraphraser
miscalibration; cycle 160 wrong-harness MarianMT). Real-encoder validation is the gate.

Method:
- Same entropy-max α=1.00 mitigation
- Calibrated Llama-1B L15 + MarianMT harness (cycle 151 reference calibration; ZKL=0.217
  baseline)
- Measure: ZKL after entropy-max + F1 unchanged
- Confirm sanity_ok=True with proper harness configuration

HARD-PASS: ZKL ≤ 0.10 AND F1 within 3% of baseline AND sanity_ok=True on real encoder.
If HP: ZKL absolute-HIPAA path on shared encoder. Locked qualified posture REVERSES.
Path D premium-tier requirement ELIMINATED. Customer pitch reframes to "HIPAA-grade
privacy on shared encoder" as new categorical advantage.

HARD-FAIL: ZKL > 0.20 on real encoder OR F1 drops > 5% OR sanity remains False. If HF:
synthetic result was artifactual; locked qualified posture + Path D stays as default.

BORDER: 0.10-0.20 ZKL on real encoder. Defensible improvement over cycle 162's 0.267
but not absolute HIPAA. Update pitch to "near-HIPAA on shared encoder" tier.

Wall: GPU local, ~2-3 hours (MarianMT round-trip is the dominant cost).

## PRIORITY 2: ZKL alternatives T1-T5 (defense-in-depth)

Per the alternatives 3x drill's pre-reg handoff. Authorize all 5 pre-tests; they are
parallel-runnable (CPU-cheap; 20-60 min each):

- T1: INLP nullspace projection feasibility (cheapest; gates T5)
- T2: Stochastic top-k exponential mechanism baseline
- T3: VIB sigma sweep (20 min)
- T4: GRL Pythia-160M pre-test (rung-2 gate for adversarial fine-tuning)
- T5: INLP + stochastic top-k combination (requires T1 HP first; the drill's most credible
  shared-encoder path to ZKL ≤ 0.10 even WITHOUT entropy-max)

These run in parallel as capacity allows. If entropy-max real-encoder validation passes,
T1-T5 become defense-in-depth options. If entropy-max validation fails, T5 (INLP +
stochastic top-k combination) becomes the primary candidate.

## Cycle 164 customer pitch corrections to apply immediately

1. **HotpotQA framing:** "Substrate matches RAG retrieval at 96% quality (n=120) AT 2.5x
   the answer quality of bare LLM; substrate adds compliance + audit + persistence moat
   features RAG lacks." NOT "substrate beats RAG."

2. **pinv timing:** Production substrate ships at 3.86 ms per update at N=4096 SMW-
   optimized (measured). Knowledge updates ~80-460x faster than LoRA fine-tune. Ship
   "~100x faster" as conservative defensible claim. RETRACT "240,000x" definitively.

3. **substrate noise/BFT positioning:** Substrate BFT is STORAGE-LAYER robust (corrupted
   W matrix; cycle 161 HP at 50% storage corruption). NOT query-noise robust on encoders
   (substrate_noise_bft_bge HF cycle 164). Customer materials must distinguish "storage-
   layer fault tolerance" from "encoder/query robustness" — only the former is real.

4. **ZKL story (PENDING entropy-max validation):** Currently locked qualified posture
   (ZKL ~0.22) + Path D premium HIPAA tier. If entropy-max real-encoder validates,
   reframes to "ZKL ≤ 0.10 absolute HIPAA on shared encoder" — major strategic upgrade.

## Cross-references

- Cycle 164 summary: notes/orchestrator_to_research_results_summary_2026-06-07_cycle164.md
- ZKL alternatives + crazy ideas 3x drill: notes/research_drill_zkl_alternatives_crazy_ideas_3x_2026-06-07.md
- ZKL alternatives Exp-Dev handoff (T1-T5 pre-regs): notes/exp_dev_handoff_research_zkl_alternatives_crazy_ideas_2026-06-07.md
- Locked qualified posture (cycle 162): notes/exp_dev_to_research_zkl_FINAL_lock_qualified_2026-06-07.md
- Post-compaction afternoon brief: notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md

---

**END.**

**Exp-Dev:** URGENT priority on entropy-max real-encoder validation (~2-3 hr GPU local).
Authorize T1-T5 ZKL alternatives in parallel as defense-in-depth. Apply HARD-PASS /
BORDER / HARD-FAIL decision rules autonomously. File entropy-max validation result
immediately on completion — it potentially unlocks the customer pitch's biggest
categorical upgrade today.
