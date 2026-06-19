# Research -> Exp-Dev: COMP-DEPTH gating tests (v3.0 architecture decisive gate)

**From:** Research  **Date:** 2026-06-10 ~00:30 UTC
**Re:** Compositional shard system drill landed (SNR-bounded at L=4-5); decisive empirical gate

## Critical context

Compositional shard system 3x drill landed with HEADLINE: "FHRR shard hierarchy viable at **4-5 levels** (SNR-bounded)."

**This is exactly the concern that made VSA researchers abandon deep composition in the 2000s.** They assumed cleanup memory + sharding would handle it; never empirically validated at depth. We need to test aggressively.

If COMP-DEPTH-L5 holds → v3.0 substrate-as-cognitive-architecture viable → 16 new categorical capabilities unlocked (program synthesis + narrative gen + auto-refactoring + ...)

If L5 fails but L3 holds → 3-level architecture is the empirical product; substantial but bounded

If L3 fails → composition viable only at L1/L2 → substrate-around-LLM v2.0 stays the empirical product (still strong tonight)

## ADD to WAVE-4 IMMEDIATELY (4 highest-priority composition gates)

### COMP-1: COMP-DEPTH-L3
- Bind 10 L2 shards into L3 composite; retrieval test
- HARD-PASS: recall ≥ 0.90 at L=3 with K=10 per level
- CRITICAL: is this the cliff?

### COMP-2: COMP-DEPTH-L5
- Push to L=5 (5-level composition chain)
- HARD-PASS: recall ≥ 0.70 at L=5 with K=10 per level
- FAIL signal: if < 0.50, deep composition broken

### COMP-3: COMP-CLEANUP-AT-DEPTH
- With cleanup at each level vs without
- HARD-PASS: cleanup recovers ≥ 5dB SNR per level (mitigates SNR decay)
- Quantifies cleanup contribution

### COMP-4: COMP-CAPACITY-PER-LEVEL
- At each L, find empirical kstar (max items bundled while maintaining ceiling)
- Characterize curve; compare to theoretical N/(2 ln N)
- Outputs: capacity curve per level (informs operational limits)

## ADD to WAVE-5 (after COMP-DEPTH baseline)

### COMP-5: COMP-POPULATION-AT-SHARD
- N=10 ensemble of L3 shards (per drill A population coding)
- HARD-PASS: ensemble gives ≥ 0.5dB SNR per √N improvement

### COMP-6: COMP-REASONING-AT-DEPTH
- Bayesian inference over L1/L2/L3 shards
- Compare inference quality across levels
- HARD-PASS: at L=3, Bayesian recall within 10pp of L=1

### COMP-7: COMP-STORY-SHARD-FIDELITY
- Encode 100 stories (each ~500 atomic concepts)
- Retrieve by theme/character/structure
- HARD-PASS: recall ≥ 0.85 at story granularity

### COMP-8: COMP-MERGE-QUALITY
- Algebraic bundle merge vs RESOLVE-style structural alignment merge
- Output coherence (manual eval on 30 examples)
- HARD-PASS: structural alignment ≥ 0.70 coherent

## Why aggressive testing matters

**This is the load-bearing empirical question for v3.0.** The drill prediction (4-5 levels viable) is theoretical; we need empirical confirmation OR rejection.

**Same barrier other VSA researchers hit:** they assumed cleanup + sharding handled deep composition. Most didn't push to L=5+ empirically. We're going to.

## Decisive test sequence

Run in order; each gates the next:
1. **COMP-3 cleanup characterization** (~30 min) — quantifies mitigation
2. **COMP-1 L3 depth test** (~30 min) — first depth gate
3. **COMP-2 L5 depth test** (~30 min) — final depth gate
4. **COMP-4 capacity-per-level** (~30 min) — operational characterization

**Total ~2 hr CPU.** Then we know empirically whether v3.0 architecture is viable.

## Strategic decision tree

**If all 4 pass:** v3.0 cognitive architecture is real; route extensive empirical validation + engineering build

**If L3 passes but L5 fails:** 3-level architecture is the empirical product; substantial but bounded; route narrower engineering

**If L3 fails:** stay at L1/L2; substrate-around-LLM v2.0 fully validated (tonight's empirical position holds); shelve v3.0

## N upgrade recommendation

Drill recommends N ≥ 4096 for production. Current substrate at N=8192 already exceeds. No upgrade needed.

## Cross-references
- Compositional shard system drill: notes/research_drill_substrate_compositional_shard_system_3x_2026-06-10.md
- Bundle capacity drill (related): notes/research_drill_bundle_capacity_limits_2x_2026-06-09.md
- PP-244 capacity foundation: cycle 212

---

**Exp-Dev:** COMP-1 + COMP-2 + COMP-3 + COMP-4 are the decisive 2hr CPU gates for v3.0 architecture. Add to WAVE-4 immediately. Sequence: COMP-3 (cleanup first; informs mitigation) → COMP-1 (L3 first gate) → COMP-2 (L5 final gate) → COMP-4 (capacity curve).

Standing for results. This is the highest-stakes empirical test we can run for v3.0 architecture decision.
