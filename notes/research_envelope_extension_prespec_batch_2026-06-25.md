# Envelope extension pre-spec batch — push each capability envelope

**Date:** 2026-06-25
**Driver:** Substrate basis chain-grade WITHIN envelope per Skunkworks tier-rulings today. Extensions push envelopes; don't change basis story. Pre-spec'd for user approval; not yet dispatched.

## Why these matter

After today's Skunkworks rulings, every chain-grade capability has a known operating envelope. Production deployment will need envelopes that match production demands. Each pre-spec below extends one capability envelope toward production-realistic values.

Priority ordered by leverage (highest first).

## EXT-1: Audit-device scale-up (the integrated demo at production V)

**Why:** Cell A landed chain-grade at V_C_IN=600 / V_REL=8 / M_KV=10k. Production audit-device likely needs V_C_IN ≥ 1000 (richer concept library) and V_REL ≥ 50 (more relations).

**Anchor:** `substrate_stage3_integrated_audit_device_demo_v2_production_scale`
**Routing:** GPU overnight_queue (V_C_IN=2000 + V_REL=50 at N=8192 will saturate local CPU)

**Grid:**
- (V_C_IN, V_REL) ∈ {(1000, 20), (1000, 50), (2000, 20), (2000, 50)}
- N=8192, M_KV=10k, 3 seeds
- 3000 mixed queries per (V_C_IN, V_REL) point

**Bands:**
- HARD_PASS_PRODUCTION_SCALE: all 4 categories ≥ 0.85 AT (V_C_IN, V_REL) = (2000, 50) AND p95 ≤ 10ms
- CHAIN_GRADE_AT_LOWER_ENVELOPE_X: passes at one of (1000, 20), (1000, 50), (2000, 20)
- HARD_FAIL_ENVELOPE_CLIFF: refuse-gate fails at V_REL ≥ 20

**Strategic significance:** answers "is the audit-device shippable at production V" — the integrated demo at production V is the final productionization gate.

## EXT-2: KG (d, sigma) phase sweep (M=100k or M=1M target)

**Per separate pre-spec:** `notes/research_KG_d_sigma_phase_sweep_v2_prespec_2026-06-25.md`
- 12 (d, sigma) combinations
- Binary search per combination for cliff M
- Target: chain-grade at M=1M for SOME (d, sigma) operating point
- Expected: cliff at M=1M achievable at d=2048 sigma=0.05 OR d=4096 sigma=0.10

## EXT-3: Intent classifier scaling to 100+ intents

**Why:** Cell `a1_substrate_intent_classifier_v1` chain-grade at acc=0.754 with 50 intents. Production intent classification often needs 100+ intents (e.g., customer support, multi-domain assistants).

**Anchor:** `substrate_intent_classifier_v2_production_scale_100plus_intents`
**Routing:** local_cpu_queue (small-data; should be fast)

**Grid:**
- n_intents ∈ {50 (rail), 100, 200, 500, 1000}
- N=8192, 3 seeds
- 100 test queries per intent (held-out)

**Bands:**
- HARD_PASS_PRODUCTION_INTENT_SCALE: acc ≥ 0.65 AT n_intents=500 AND p95 ≤ 5ms
- CHAIN_GRADE_AT_CLIFF_X: passes at one of 100, 200, 500 but cliffs at higher
- HARD_FAIL_CLIFF_AT_100: doesn't extend beyond rail

**Strategic significance:** answers "how many intents can the substrate distinguish" — load-bearing for substrate-product as a customer-facing classifier.

## EXT-4: Continual learning at 1000+ cycles

**Why:** Cell `a8_continual_writes_no_catastrophic_forgetting_v1` chain-grade at 200 cycles with forget=0.006. Production continual learning needs 1000+ cycles. We don't know if forget rate stays bounded or compounds.

**Anchor:** `substrate_continual_learning_v2_1000plus_cycles_scale`
**Routing:** local_cpu_queue (small per-cycle work)

**Grid:**
- n_cycles ∈ {200 (rail), 500, 1000, 2000, 5000}
- N=8192, 3 seeds
- forget rate measured at every 100 cycles

**Bands:**
- HARD_PASS_FORGET_RATE_BOUNDED_AT_5K: forget ≤ 0.05 at 5000 cycles
- CHAIN_GRADE_AT_CLIFF_X: forget stays ≤ 0.05 up to N cycles
- HARD_FAIL_FORGET_COMPOUNDS: forget rate scales worse than O(log N) → continual learning has a horizon

**Strategic significance:** answers "is the substrate continually-learning at production cadence" — load-bearing for substrate-product as a deployable system that ingests new facts over time.

## EXT-5: Stage 2 FREQ_ROUTED_DEEPER at N=16384+

**Why:** Cell 2 v5 chain-grade-definitive at N=4096 + N=8192 (cross-N replicated). Unknown at N=16384+; substrate-product may want N=16384 or N=32768 for larger M_KV scale-up.

**Anchor:** `substrate_compose_freq_routing_v6_N16384_N32768_extension`
**Routing:** GPU overnight_queue (N=32768 will be GPU-bound)

**Grid:**
- N ∈ {4096 (rail), 8192 (rail), 16384, 32768}
- 5 seeds (Cell 2 v5 used 5 seeds)
- n_steps=3000 plateau verified per N

**Bands:**
- HARD_PASS_N_SCALING_CONFIRMED: BPC lift over baseline maintained at N=16384 AND N=32768
- CHAIN_GRADE_AT_N_CLIFF: lift cliffs at some N
- HARD_FAIL_LIFT_DEGRADES_WITH_N: lift decreases as N increases

**Strategic significance:** extends Stage 2 mechanism #1 envelope to larger N. Load-bearing for the (d, sigma) phase sweep — many of those operating points will use N=16384.

## EXT-6: Working memory at K > 32 with cleanup

**Why:** WM-HRR-slots production cell chain-grade at K≤32 perfect at sigma=1.0; K=128 at 0.95 / K=256 at 0.64. Production WM may want K>32 reliably.

**Anchor:** `substrate_working_memory_v2_extended_K_with_cleanup_per_slot`
**Routing:** local_cpu_queue

**Grid:**
- K ∈ {32 (rail), 64, 128, 256, 512}
- Two modes: NAIVE (current) and CLEANUP_PER_SLOT (read slot → cleanup → use)
- N=4096, 3 seeds

**Bands:**
- HARD_PASS_CLEANUP_LIFTS_K_TO_128: CLEANUP arm scores ≥ 0.95 at K=128 (vs NAIVE 0.95 at K=32)
- CHAIN_GRADE_K_EXTENSION_X: cleanup lifts K-ceiling by 2× or more
- HARD_FAIL_NAIVE_IS_OPTIMAL: cleanup doesn't help (NAIVE is already at K-ceiling)

**Strategic significance:** WM is the PFC analog; if K>32 is feasible, substrate has better-than-brain WM at production scale.

## EXT-7: NESS envelope beyond alpha=0.7

**Why:** `kmax_ness_envelope_gpu_v1` chain-grade at alpha∈[0.3, 0.7]. Beyond 0.7 unknown — does graph traversal still work or does cleanup-augmented chain break?

**Anchor:** `substrate_NESS_envelope_v2_alpha_extension_beyond_0p7`
**Routing:** GPU overnight_queue

**Grid:**
- alpha ∈ {0.7 (rail), 0.8, 0.85, 0.9}
- N=8192, 3 seeds
- K_grid same as v1

**Bands:**
- HARD_PASS_ALPHA_EXTENSION: ratio_to_eq ≥ 2.0 AND ext_hopfrac ≥ 0.95 at alpha=0.85
- CHAIN_GRADE_AT_ALPHA_CLIFF: cliff identified between 0.7 and 0.9
- HARD_FAIL_RAPID_DEGRADATION: cliff at alpha=0.75

**Strategic significance:** extends NESS envelope toward larger alpha (more concentrated walks); useful if substrate-product applications need graph traversal at higher density.

## Batch dispatch plan (if user approves)

**Local CPU runner queue (4 cells in serial):**
1. EXT-3 intent classifier scaling (smallest; runs first)
2. EXT-4 continual learning extension
3. EXT-6 working memory K extension
4. EXT-7 NESS alpha extension (might need GPU; consider routing)

**GPU runner queue (3 cells in serial):**
1. EXT-1 audit-device production V scale-up
2. EXT-5 Stage 2 N=16384 / N=32768 extension
3. EXT-2 KG (d, sigma) phase sweep (largest; runs last)

**Total wall budget:** 6-12h GPU + 1-3h local CPU. Most can run overnight.

## What this batch DOESN'T do

- Doesn't change the substrate basis (basis is finalized)
- Doesn't re-investigate Barrier 1 multi-hop (3-for-3 refuted; ceiling permanent at this regime)
- Doesn't pursue LM-equivalence (deferred per USER)
- Doesn't compose any new mechanism (uses chain-grade primitives at extended scale)

## Decision points for USER

1. Approve dispatch of all 7 extensions as a coordinated batch? (this is the next major investment)
2. Or pick a subset based on substrate-product priority? (e.g., just EXT-1 + EXT-2 if product wants production V + M=1M)
3. Or hold all until Cell H' v2b lands and we see encoder-envelope direction? (Cell H' v2b PASS would shift priorities — if Path C opens, multi-hop and encoder become priorities again)

— Research (Director)
