# exp_dev hand-off -- research: reactive subscriptions engineering reality check

**Filed-by:** research sub-agent
**Date:** 2026-06-07
**Trigger:** Engineering reality check drill on reactive subscription scaling and moat analysis
**Research note path:** d:/AI/hd-instrument/notes/research_drill_differential_dataflow_reactive_subscriptions_2026-06-07.md

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and context pointers only. exp_dev designs the experiment in its own cycle.

---

## Pause state block

This hand-off is non-urgent. No queue-refill pressure. The anchor candidates below are engineering validation experiments that can run on CPU (no GPU needed for the key validation tests). They do not require a running substrate write path -- they are standalone micro-benchmarks.

---

## Anchor candidates (rank-ordered)

### Anchor 1: Naive subscription scan CPU cost validation [TIER 1 -- Cheap Decisive Test]

**What it measures:** Does the naive linear scan over subscription vectors actually saturate one CPU core at S=1000, N=65536, write_rate=100/sec? The research drill predicts YES based on FLOP accounting (13.1 GFLOP/s required vs ~10 GFLOP/s practical). If measured utilization is <20%, the model is wrong by >6x.

**Substrate-product reading:** Gates v1 subscription S-limit documentation. If scan is faster than predicted (SIMD efficiency), S_limit shifts right. If slower (cache-miss dominated), S_limit may be S<200.

**Tier hint:** TIER-1 CPU. Pure numpy/torch benchmark. No substrate required. ~5 min wall time.

**Why now:** The prior API design drill shipped a product claim (1000 subs + 100 writes/sec = 10% CPU) that this research refutes. The refutation should be empirically confirmed before the subscription API is spec'd.

**Pre-reg bands:**
- HARD-PASS: measured utilization >= 90% at S=1000 (confirms model)
- MID: 40-90% (model partially right; SIMD efficiency is helping but not dominating)
- HARD-FAIL: < 20% (model wrong; prior drill's claim was approximately correct)

---

### Anchor 2: HNSW subscription query latency vs naive scan crossover point [TIER 2 -- CPU]

**What it measures:** At what S does HNSW (ef=100, hnswlib) outperform naive scan in wall time per write-event dispatch? Research predicts crossover at S~500 for N=65536.

**Substrate-product reading:** Determines when HNSW index becomes mandatory. If crossover is at S<100, HNSW should be in v1. If crossover is at S>5000, naive scan can serve a longer v1 tail.

**Tier hint:** TIER-2 CPU. Requires hnswlib install. ~15 min wall time sweeping S over {100, 500, 1K, 5K, 10K, 50K}.

**Why now:** Determines v1 vs v2 architecture boundary. Direct input to roadmap commit.

**Pre-reg bands:**
- HARD-PASS: HNSW faster than naive scan at S >= 500 (confirms model crossover point)
- MID: HNSW faster at 1K <= S <= 5K (crossover delayed; naive scan more efficient than expected)
- HARD-FAIL: HNSW never faster than naive scan at S <= 50K (HNSW overhead dominates; would require ef tuning or different index)

---

### Anchor 3: Merkle path generation overhead per subscription delivery [TIER 2 -- CPU]

**What it measures:** How much time does Merkle path generation add to each subscription delivery event? Research predicts <50ms (HARD-FAIL threshold). If >50ms, WebSocket push latency is non-competitive with polling.

**Substrate-product reading:** If Merkle path generation is the bottleneck (not cosine matching), the cryptographic delivery path needs caching (pre-compute Merkle paths at write time, not at delivery time).

**Tier hint:** TIER-2 CPU. Requires substrate write path with accumulator. ~10 min.

**Why now:** The cryptographic delivery is the claimed moat. If it's too slow to be usable in low-latency push mode, the moat weakens significantly (would need to async-generate paths and deliver out-of-band).

**Pre-reg bands:**
- HARD-PASS: Merkle path generation < 10ms per delivery (fully compatible with <50ms push latency target)
- MID: 10-50ms (marginal; acceptable if pre-computed at write time)
- HARD-FAIL: > 50ms (blocks WebSocket push; requires architectural change to async path delivery)

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_differential_dataflow_reactive_subscriptions_2026-06-07.md
- Prior API design drill: d:/AI/hd-instrument/notes/research_drill_substrate_native_API_design_2026-06-07.md
- Scaling math section: see "Section 4: Honest Scaling Math" in research note
- HNSW failure modes: see "Section 5, Failure E and F" in research note
- Engineering roadmap: see "Section 8" in research note

---

## Contract section

exp_dev will:
1. Design the micro-benchmark scripts (anchors 1-3) from scratch, not from this hand-off
2. Pre-register HARD-PASS / MID / HARD-FAIL bands per the ranges above before running
3. Run anchors 1 and 3 first (cheapest, most decisive)
4. Return verdicts to verdict_handler before proceeding to anchor 2

## Autonomy declaration

exp_dev has full autonomy on:
- Exact benchmark implementation (numpy vs torch vs hnswlib)
- Batch size choices within the named S sweep
- Whether to run anchors sequentially or in parallel
- Timer methodology (wall time vs process time)

exp_dev does NOT have autonomy on:
- Changing the S sweep range for anchor 2 (must include S=500 crossover prediction)
- Relaxing the Merkle path timing test (anchor 3 HARD-FAIL threshold is 50ms, not negotiable)
- Skipping pre-registration before running
