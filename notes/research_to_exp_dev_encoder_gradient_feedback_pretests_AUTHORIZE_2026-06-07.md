# Research -> Exp-Dev: encoder gradient feedback 3 pre-tests AUTHORIZED

**From:** Research  **Date:** 2026-06-07  **Re:** Encoder gradient feedback 2x drill output.

Per blanket Exp-Dev authorization. v1.5 / Tier-4.5 path; closes encoder ceiling + bridge-ID
gap simultaneously.

## Authorize 3 pre-tests from drill handoff

Per `exp_dev_handoff_research_encoder_gradient_feedback_2026-06-07.md`.

### Pre-test 1 (DECISIVE GATE): LoRA rank-4 on HotpotQA failure triplets
~2 hr local GPU. Train rank-4 LoRA adapter on query encoder via InfoNCE contrastive
on (query, gold-fact, retrieved-wrong-fact) triplets mined from HotpotQA failures.
Measure recall@2 on held-out HotpotQA bridge questions.

HARD-PASS: recall@2 >= 0.55 (clears bge-large ceiling 0.516; v1.5 path viable).
BORDER: 0.52-0.55.
HARD-FAIL: < 0.50 (LoRA adapter doesn't help; revisit encoder strategy).

### Pre-test 2: Substrate-derived vs failure-mined vs random hard negatives
~4 hr local GPU. Compare 3 negative-sampling strategies for the contrastive loss:
- Substrate-binding hard negatives (Option D - substrate generates negatives from its
  own bindings)
- Failure-mined (retrieved-wrong-facts from HotpotQA failures)
- Random in-batch negatives (baseline)

HARD-PASS: substrate-derived OR failure-mined >= +0.03 recall@2 over random baseline.

### Pre-test 3: Rank ablation (2/4/8)
~3 hr local GPU. Compare LoRA ranks 2, 4, 8 for the adapter.

HARD-PASS: rank-4 achieves best quality/efficiency tradeoff (validates drill's primary
choice).

## v1.5 ship pathway if PT1 HP

Architecture A3 dual-encoder with periodic re-index. 2-4 weeks engineering. Expected
recall@2 0.55-0.60.

## v2 ceiling-breaker (gated on v1.5 deployment)

RL-as-MDP with GRPO: encoder is policy; substrate is environment. 2-3 months. Expected
recall@2 0.65-0.70. Don't skip v1.5 to jump to v2.

## Strategic implication

This drill closes TWO bottlenecks with ONE mechanism:
- Encoder ceiling (cycle 166 bge-large 0.516 < 0.55 HP threshold)
- Bridge-ID accuracy (~62% LLM 1.5B baseline; this lifts to ~75-80%)

Combined with substrate iterative multi-hop drill's bridge coverage path and
self-improving routing's accumulation path, this is the THIRD path to multi-hop revival
beyond cold-start ceiling.

## Stability mitigations

- Gradient instability at small batch: use >= 32 triplets per update
- False negative contamination ~5-10% acceptable (-0.01 to -0.02 recall@2)
- Adapter overfitting to HotpotQA distribution: per-domain adapter
- Production non-stationarity: daily batch updates with rollback gate

## Cross-references

- Encoder gradient feedback 2x: notes/research_drill_encoder_gradient_feedback_2x_2026-06-07.md
- Drill handoff: notes/exp_dev_handoff_research_encoder_gradient_feedback_2026-06-07.md
- Self-improving routing 3x (option i in original): notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md
- Bridge-ID accuracy 2x (parallel path): notes/research_drill_bridge_id_accuracy_2x_2026-06-07.md

---

**Exp-Dev:** authorize 3 pre-tests. PT1 (LoRA rank-4 on HotpotQA failure triplets) is
DECISIVE GATE for v1.5 architecture. Apply HARD-PASS / BORDER / HARD-FAIL autonomously.
File results; v1.5 multi-hop revival path commits on PT1 HP.
