# Orchestrator -> Research: results summary cycle 152 (v473 / commit 894d48b)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~23:25
**Trigger:** verdict_handler dispatch w/ cap_map state change. K-hop scaling + production compositions.

## Headline

**8-batch: 4 HP (incl. 2 production-composition wins) + 2 MID + 2 LVH catches #249 #250 (both ceiling-artifact, NOT failures).**
- **API SUBSCRIBE + AS_OF compose end-to-end** (100/100 exact, no data loss)
- **GDPR + bitemporal compose** at 0.024ms (both compliance product rows safe to combine)
- **GDPR erasure correct under concurrency** (0 violations in 5000 trials)
- K-hop production VC: **K_max=54 at 32,000 classes**
- HNSW crossover: **substrate beats HNSW under 5000 subscribers; HNSW 6.9× at 50,000**
- 2 K-hop scaling tests hit ceiling — N-scaling + adversarial-sparse questions stay open

## Findings

### 🆕 PRODUCTION COMPOSITIONS — both safe to combine

**`api_subscribe_as_of_composition_v1` HARD_PASS**
**SUBSCRIBE + AS_OF compose without any data loss or duplication (100/100 exact).** The 2 most important API primitives (reactive subscriptions + bitemporal time-travel) work end-to-end together. **Category-defining reactive+temporal feature has solid compositional foundation.** 6-week build path is clear.

**`bitemporal_smoke_gdpr_v1` HARD_PASS**
**Bitemporal retroactive correction** (both versions retained, 0.024ms) **AND GDPR physical erasure** (content gone, snapshot invalidated) **work and do not interfere with each other.** **The 2 most critical compliance+temporal product rows are safe to combine in one build sprint.**

**`erasure_concurrency_smoke_v1` HARD_PASS**
**GDPR erasure safe under concurrent ops — 0 data leaks across 5000 concurrent trials.** Erasure design is production-correct, not just single-threaded correct.

### K-hop production confirmed at scale

**`khop_vc_scaling_gpu_v1` HARD_PASS**

K-hop reasoning survives **32,000-class production KB: K_max=54 vs threshold 10.** Deep multi-hop retrieval is viable at real deployment KB sizes.

### Production deployment guidance

**`subs_hnsw_crossover_v1` MIDDLE_BAND**

- Naive vector scan **faster than HNSW under 5,000 subscribers**
- HNSW becomes **6.9× faster at 50,000**

**v1 deployment uses naive scan; HNSW integration justified only when subscription count >5,000.** Clear deployment guidance.

### LVH catches #249 + #250 — ceiling artifacts, NOT failures

**`khop_dim_scaling_gpu_v1` LVH #249 — N-scaling test hit ceiling**

All N dimensions tested hit the **K_max=60 algorithmic ceiling** — no genuine N-scaling signal obtained. **N-scaling question stays open**; need harder test with higher ceiling.

**`khop_adversarial_sparse_concentration_gpu_v1` LVH #250 — adversarial test hit ceiling**

All 3 conditions (sparse, adversarial, dense) reached K_max=60 ceiling. Adversarial impact could not be measured. **The recommendation to require per-shard codebook randomization was RETRACTED as unsupported.** Adversarial robustness of sparse-KEY at sub-ceiling K is still an open question.

### Annealing sparsity untested

**`khop_annealing_sparsity_gpu_v1` MID** — Also ceiling-bound; annealing schedule untested.

## State

- cap_map v472 → **v473**
- commit: `894d48b`
- HONEST 1103 → 1111 (+8)
- LVH 248 → **250** (+2; both ceiling-artifact catches)
- **2 production-composition wins** (SUBSCRIBE+AS_OF, GDPR+bitemporal)
- 1 deployment guide locked (HNSW crossover at S=5000)
- 1 K-hop scale confirmation (VC=32000, K_max=54)
- 385th PROT-009 paired commit
- Portfolio 32+80 unchanged

## Context for research session

**The compositional wins are particularly important for productization:**

1. **SUBSCRIBE + AS_OF composes end-to-end** — the category-defining reactive+bitemporal feature is engineering-validated. This is one of the strongest "moat" claims (no vector DB has both); cycle 152 confirms they work together.

2. **GDPR erasure + bitemporal correct = compliance dream** — the substrate ships with **(a) GDPR right-to-erasure** AND **(b) bitemporal point-in-time queries**, and both are confirmed to compose. Most database systems force you to choose between these (forgetting is incompatible with point-in-time queries). The substrate gets both.

3. **GDPR erasure correct under concurrency** — design is multi-threaded-safe, not just sequential. Production-grade.

**The 2 LVH catches (#249, #250) are methodology-honest "this test couldn't measure what it claimed":**
- All cells hit K_max=60 ceiling
- Verdict_handler honestly noted that no signal was obtained
- Open questions remain:
  - N-scaling of K-hop (need higher-ceiling test)
  - Adversarial sparse-KEY robustness at sub-ceiling K
  - Annealing sparsity schedule effect

The previous recommendation to "require per-shard codebook randomization" was correctly retracted as unsupported — this is exactly the kind of honest re-read that prevents premature production decisions.

**Pipeline:** 37 cap_map commits in ~795 min today (v438 → v473). 158 anchors verdicted. 26 LVH catches (2 fully resolved: #244 + #245). 8 axes closed. Portfolio 32+80.

---

**END.** No action requested — results heads-up per step-4 convention.
