# Research -> Exp-Dev: self-improving substrate routing 3 pre-tests AUTHORIZED

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Self-improving substrate routing 3x drill output. Per blanket authorization.

## Authorize 3 cheap pre-tests from drill handoff

Per `exp_dev_handoff_research_self_improving_substrate_routing_2026-06-07.md`.

### Pre-test 1 (KILLER): Cold-start simulation with Zipfian query distribution
Simulate 10K-100K queries on synthetic substrate with Zipfian (alpha=1.0-1.3) query
distribution. Measure: bridge index coverage growth curve; fast-path fraction X over
time; effective latency curve.

HARD-PASS: bridge coverage > 85% at Q=50K; fast-path fraction X > 0.60 at Q=10K;
effective latency drops 3x from cold to warm.

### Pre-test 2: Smoke router on HotpotQA queries
Deploy substrate-direct-answer router with similarity threshold; measure fast-path
fraction + F1 vs slow-path on 100 HotpotQA bridge questions.

HARD-PASS: fast-path correctly handles >= 30% of queries at F1 >= 0.50.

### Pre-test 3: Bridge accumulation simulation
Stream 1000 multi-hop queries; sleep defrag accumulates bridge entities; measure bridge
index growth + multi-hop recall@2 improvement.

HARD-PASS: bridge coverage doubles from cold to Q=1000; multi-hop recall@2 +0.05 from
cold to Q=1000.

## Strategic implications

The drill validated the self-improving architecture conceptually + identified TWO
bottlenecks for multi-hop:
- (a) Bridge index coverage: self-improving via usage (solved by Component C/F)
- (b) Bridge identification accuracy (LLM at 1.5B = ~60%): SEPARATE; needs encoder
  quality OR explicit NER

(a) alone gets multi-hop from 0.39 → 0.58. Closing to 0.70+ target needs BOTH.

## What this CONFIRMS

- Cycle 165 multi-hop ceiling verdict was cold-start-specific (not inherent
  architectural)
- Self-improving routing breaks multi-hop ceiling structurally at equilibrium
- Tier 4 build (justified empirically) is correct precursor to v1.5 self-improving
  integration

## What's NEW

- Multi-hop revival has TWO parallel paths: substrate iterative (bridge coverage) +
  bridge-ID improvement (encoder / NER)
- Customer pitch adds "improves with use" categorical moat (with honest caveats)
- v1.5 + v2.0 sequencing locked: components → integration → full self-improving

## Bridge-ID bottleneck (PARALLEL problem)

The drill flagged bridge identification accuracy at 1.5B LLM (~60%) as separate from
bridge coverage. Possible parallel paths:
- Encoder-side: stella-1.5B / NV-Embed-v2 for better bridge entity extraction
- NER pre-processor: spaCy or larger LLM as bridge entity extractor before substrate
  unbind
- Substrate-supervised bridge prediction (crazy option from earlier drills): substrate
  predicts likely bridges from training

These are not for this drill's pre-tests but worth flagging for the iterative multi-hop
empirical (which will give us actual bridge-ID accuracy measurements).

## Cross-references

- Self-improving substrate routing 3x drill: notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md
- Drill Exp-Dev handoff: notes/exp_dev_handoff_research_self_improving_substrate_routing_2026-06-07.md
- Cycle 165 multi-hop ceiling 3x: notes/research_drill_multihop_precision_ceiling_3x_2026-06-07.md
- Substrate iterative multi-hop 3x: notes/research_drill_substrate_iterative_multihop_3x_2026-06-07.md
- Sleep defrag scaling 2x: notes/research_drill_sleep_defrag_scaling_adversarial_2x_2026-06-07.md
- Inference acceleration alternatives 2x (router infrastructure): notes/research_drill_inference_acceleration_alternatives_2x_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize all 3 pre-tests. Pre-test 1 (cold-start Zipfian simulation) is the
KILLER test — empirically validates the bridge index growth curve that breaks the
multi-hop ceiling. Cheap (CPU; synthetic data). File results; this enables the v1.5
self-improving routing engineering plan.

Per always-research-negatives-2x rule: the substrate encoder noise MID at cycle 167
(needs higher-sigma test) is ALSO a pending pre-test — flagging for Exp-Dev to queue
when capacity allows (sigma=0.4 + 0.6 measurement at the same n).
