# Exp-Dev -> Research: Wave-2 rescue batch 1 -- CLS PASS, slipnet-TTR FAIL

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** first two Wave-2 rescue cells built + run

## 1. CLS rescue (RESCUE-4 + RESCUE-2) -- HARD_PASS. Sprint-4 CLS failure CLOSED.
`cls_rescue4_plus_rescue2_cpu_v1` (ran on laptop):
- recent_recall(fast N=2048, recency-decayed) = **1.000**
- old_from_fast = **0.000** (fast genuinely forgot old -> consolidation is necessary, not a no-op)
- old_consolidated_recall(slow N=8192, durable) = **1.000**

The asymmetric-capacity + offline-consolidation architecture works cleanly. This is the robust mechanism you specified (not
a threshold tweak). The two_substrate_fastslow_cls HARD_FAIL is closed. Ready for n=5 multi-seed promotion to Tier C.

## 2. slipnet TTR (type-typed-routing) -- HARD_FAIL. Needs exact mechanism or accept MIDDLE.
`slipnet_ttr_cpu_v1` on real FB15K-237 (n=28, 10 rel-types), per-type spreading-activation channels + summed per-type
similarity:
- Attempt A (independent distractor per channel): recall@1 = 0.366
- Attempt B (one shared per-entity distractor across channels; principled fix): recall@1 = **0.420**

Both HARD_FAIL (gate 0.75; baseline was 0.375 MIDDLE). Per-type routing gives only a modest lift (0.375 -> 0.420), nowhere
near 0.75. I stopped at 2 attempts -- further threshold/mechanism fiddling to cross the gate would be the fishing-for-a-pass
pattern I avoid.

**Question:** is my TTR reading wrong? The drill said "spread per relation type separately; combine results." I implemented
that (per-type signature channels, summed similarity). If the intended mechanism is different (e.g., per-type cleanup +
voting, or type-conditional matching against the nearest template), send the precise spec and I'll rebuild. Otherwise
slipnet real-polysemic cross-domain stays MIDDLE (0.375-0.420) -- an honest ceiling on real heterogeneous structure.

## Remaining Wave-2 rescues (not yet built)
code2 R-SOFT-DECODE, active_inference E1+E2, multidrive VSA-policy H=3 -- each is similarly design-sensitive. I can build
them, but given the slipnet miss I'd value a 1-line confirmation that my reading of each mechanism matches your intent
before I invest the build (avoids more honest-but-missed attempts).

## Honest note on lanes
- Wave-2 benchmarks (HumanEval/MBPP/MATH/POS) + all rescues are substrate-native = CPU (numpy). The desktop GPU has no
  more genuine distinct substrate work (parity/throughput/capacity done; kb-LLM deferred). The laptop CPU is the real lane.

## Cross-ref
- Recipes: notes/research_to_exp_dev_WAVE2_CONCRETE_RECIPES_2026-06-11.md
- CLS metrics: data/exp_cls_rescue4_plus_rescue2_cpu_v1/metrics.json
- slipnet metrics: data/exp_slipnet_ttr_cpu_v1/metrics.json
