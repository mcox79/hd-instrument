# Research -> Exp-Dev: COMPOSITIONAL DEPTH OVERCOMING BATCH (aggressive empirical attack)

**From:** Research  **Date:** 2026-06-10 ~00:45 UTC
**Re:** User direction: queue ALL experiments to overcome compositional shard depth barrier

## Strategic intent

**This is the barrier other VSA researchers abandoned at.** They assumed cleanup + sharding handled deep composition; never validated past L=2 empirically. **We're going to attack it from every angle.**

Three parallel objectives:
1. **CHARACTERIZE** the cliff empirically (where + why does SNR collapse?)
2. **MITIGATE** via every known mechanism (cleanup + GHRR + sharding + population + 1-bit + Welch + stochastic-resonance + drift-diffusion + active inference)
3. **OVERCOME** via architectural variants (algebraic vs structural-align vs schema-extract vs tree-compose)

Plus production-scale validation if depth holds.

## P0 — DECISIVE GATES (already filed; ~2hr CPU)

- COMP-1 DEPTH-L3 (first cliff test)
- COMP-2 DEPTH-L5 (final cliff test)
- COMP-3 CLEANUP-AT-DEPTH (quantifies mitigation)
- COMP-4 CAPACITY-PER-LEVEL (operational curve)

These four tell us **if there's a problem and how big it is.** Run first.

## P1 — EXTENDED DEPTH SWEEP (~3hr CPU)

If COMP-1/2 reveal a cliff, characterize it precisely:

### COMP-5 DEPTH-L4
- Between L3 and L5; intermediate test
- HARD-PASS: recall ≥ 0.80 at L=4 with K=10 per level

### COMP-6 DEPTH-L6
- Push past L=5
- HARD-PASS: recall ≥ 0.60 at L=6 with K=10
- Characterizes cliff location

### COMP-7 DEPTH-L8
- Extreme depth (where humans typically max out)
- HARD-PASS: any nonzero recall (characterize asymptote)
- INFORMATIONAL: even if low, helps map the curve

### COMP-8 DEPTH-VARIABLE-K
- Sweep K per level (5, 10, 20, 50) at fixed L=3
- Shows capacity-vs-depth trade-off

## P2 — MITIGATION MECHANISMS (~5hr CPU; parallel tests)

Each tests a known noise-reduction lever at depth:

### COMP-9 GHRR-BLOCK-DIAGONAL-AT-DEPTH
- Substrate uses GHRR (validated PathHD 86.2%) at L=3, L=4, L=5
- HARD-PASS: GHRR at L=5 ≥ 0.85 (vs flat FHRR baseline)
- TESTS: does block-diagonal preserve orthogonality through composition

### COMP-10 PER-LEVEL-SHARDING
- Each shard level has own type-shard pool (atomic / sentence / paragraph / story)
- HARD-PASS: capacity compounds 50x at L=5 (vs flat)
- TESTS: per-predicate sharding (production-validated) lifts to per-level

### COMP-11 1-BIT-AT-DEPTH
- PP-200 1-bit quantization at L=3, L=4, L=5
- HARD-PASS: <5% accuracy loss vs float at L=5
- TESTS: counterintuitively 1-bit might preserve signal (binary noise less correlated)

### COMP-12 WELCH-BOUND-CODEBOOK-AT-DEPTH
- Proper low-coherence construction (LAP4-1 rescue; Welch-bound ETF / chirp / Paley)
- HARD-PASS: 1.5x+ capacity gain at L=3
- TESTS: does proper codebook construction extend to depth?

### COMP-13 HIERARCHICAL-CLEANUP
- Cleanup memory at EACH level (cascading Hopfield)
- HARD-PASS: SNR restored to ≥0.9x atomic at L=5
- TESTS: cleanup compounds; signal restored at each layer

### COMP-14 POPULATION-AT-DEEP
- N=10 ensemble of L=5 shards; majority vote
- HARD-PASS: ensemble +20% recall vs single at L=5
- TESTS: PP-249 population effect at deep composition

## P3 — ARCHITECTURAL VARIANTS (~4hr CPU; test composition patterns)

Different ways to bundle shards at each level:

### COMP-15 ALGEBRAIC-BUNDLE-MERGE
- Standard FHRR sum + renormalize at depth
- HARD-PASS: ≥0.70 recall at L=5
- BASELINE for other variants

### COMP-16 STRUCTURAL-ALIGN-MERGE (RESOLVE)
- RESOLVE-pattern relational homomorphism at depth (PP-275 base; extended)
- HARD-PASS: ≥0.80 recall at L=5
- TESTS: structure-aware merge preserves semantics

### COMP-17 SCHEMA-EXTRACT-AT-DEPTH
- Sleep-defrag analog: factor common pattern out at each level
- HARD-PASS: ≥0.80 recall at L=5 with 30%+ items consolidated
- TESTS: compression via abstraction extends to deep composition

### COMP-18 GHRR-SEQUENTIAL-BINDING
- Sequential bind preserves order; non-commutative
- HARD-PASS: order-dependent retrieval ≥0.85 at L=5
- TESTS: order-preserving paths through deep composition

### COMP-19 TREE-COMPOSE
- Tree-structured composition (left-right balanced) vs flat
- HARD-PASS: tree ≥0.80 vs flat baseline at L=5
- TESTS: hierarchical reduces compounding noise

### COMP-20 SPARSE-COMPOSE
- Only bind top-K most-similar sub-shards (not all)
- HARD-PASS: sparse ≥0.85 with 70% fewer bindings
- TESTS: sparsity reduces noise; preserves dominant signal

## P4 — REASONING AT DEPTH (~3hr CPU)

Do validated reasoning primitives still work at deep shards?

### COMP-21 BAYESIAN-AT-L3
- PP-246 Bayesian over L3 composite shards
- HARD-PASS: Bayesian recall ≥0.85 at L=3 (within 10pp of L=1)

### COMP-22 CAUSAL-AT-L3
- PP-270 Pearl do-calculus over L3 module shards
- HARD-PASS: do() intervention recall ≥0.80 at L=3

### COMP-23 MULTI-HOP-THROUGH-COMPOSITES
- K-hop traversal through composite shards (each hop is to another L3 composite)
- HARD-PASS: 3-hop through composites recall ≥0.70

### COMP-24 ANALOGICAL-AT-L3
- PP-275 RotatE-style mapping between L3 composites (cross-domain)
- HARD-PASS: cross-composite analogy Hits@1 ≥0.70

## P5 — PRODUCTION-SCALE COMPOSITION (~6hr CPU; if depth holds)

Real-world shard sizes:

### COMP-25 STORY-SHARD-L3
- Each story = ~500 atomic concepts; L=3 composition
- HARD-PASS: story retrieval by theme ≥0.85 on 100 stories
- TESTS: production-scale narrative composition

### COMP-26 PROGRAM-SHARD-L3
- Each module = ~100 functions; L=3 composition
- HARD-PASS: program retrieval by behavior ≥0.80 on 50 modules

### COMP-27 ARGUMENT-SHARD-L3
- Each argument = ~20 premises; L=3 composition
- HARD-PASS: argument retrieval by structure ≥0.85 on 50 arguments

### COMP-28 KNOWLEDGE-BASE-SHARD-L3
- Each KB = ~1000 facts; L=3 composition (KB-of-KBs)
- HARD-PASS: KB-level retrieval ≥0.80

## P6 — SNR ENGINEERING (~4hr CPU; active restoration)

Mechanisms to RESTORE signal at depth:

### COMP-29 WHITENING-AT-DEPTH
- ZCA-style whitening at each level (anti-correlation)
- HARD-PASS: SNR +5dB per level vs no-whitening

### COMP-30 STOCHASTIC-RESONANCE-AT-DEPTH
- PP-276 stochastic resonance at deep retrieval
- HARD-PASS: noise-tuned recall improves ≥10% at L=5

### COMP-31 DRIFT-DIFFUSION-AT-DEPTH
- PP-279 evidence accumulation across multiple L=5 retrievals
- HARD-PASS: DDM accuracy ≥0.90 at L=5 (vs 0.70 single-shot)

### COMP-32 ACTIVE-INFERENCE-AT-DEPTH
- PP-272 active inference loop at deep shards
- HARD-PASS: convergence at L=5 within 5 iterations

## P7 — HYBRID SUBSTRATE-NEURAL (~3hr CPU)

If pure VSA hits cliff, hybrid approaches:

### COMP-33 LEARNED-PROJECTION-PER-LEVEL
- PP-225 projection head pattern at each L
- HARD-PASS: per-level projection ≥0.85 recall at L=5
- TESTS: trained projection per level overcomes naive composition

### COMP-34 NEURAL-CLEANUP-AT-DEPTH
- Neural cleanup memory (trained denoiser) at each level
- HARD-PASS: ≥0.85 recall at L=5

### COMP-35 LEARNED-CODEBOOK-PER-LEVEL
- Manifold-aligned learned codebooks per shard level
- HARD-PASS: ≥1.5x capacity gain per level (compounds)

## SEQUENCING

**Run in priority order:**

**Night 1 (immediate; 2-4hr):**
- P0 COMP-1/2/3/4 — characterize cliff

**Night 2 (if cliff exists; 5-7hr):**
- P1 COMP-5/6/7/8 — extended depth sweep
- P2 COMP-9/10/11 — first mitigations (GHRR + sharding + 1-bit)

**Night 3 (if mitigations help; 6-8hr):**
- P2 COMP-12/13/14 — Welch-codebook + cleanup + population
- P3 COMP-15/16/17/18 — architectural variants

**Night 4 (validation of architecture; 4-6hr):**
- P3 COMP-19/20 — tree + sparse
- P4 COMP-21/22/23/24 — reasoning at depth

**Night 5+ (production scale; if architecture validated; 10+ hr):**
- P5 COMP-25/26/27/28 — production shard sizes
- P6 COMP-29/30/31/32 — SNR engineering
- P7 COMP-33/34/35 — hybrid neural-substrate

## Total scope

**35 experiments. ~30-40 hr total CPU.** Pure-numpy/VSA where possible (most are CPU-friendly).

**If we find ANY architectural variant + mitigation combination that holds at L=5, v3.0 substrate-as-compositional-cognitive-architecture is empirically grounded.**

## Strategic significance

**No published VSA work has empirically validated deep composition with this aggressive a test suite.** Other researchers abandoned at L=2 assuming the cliff was insurmountable.

**Best case:** discover the architectural pattern that overcomes the cliff → v3.0 categorical position
**Honest case:** find the cliff precisely → architectural decisions made empirically
**Worst case:** confirm cliff at L=3 → substrate-around-LLM v2.0 (tonight's empirical position) is the product

**Either way, the test suite ENDS the 30-year-old VSA deep-composition question empirically.**

## Cross-references
- COMP-DEPTH gating: notes/research_to_exp_dev_COMP_DEPTH_GATING_2026-06-10.md
- Compositional shard system drill: notes/research_drill_substrate_compositional_shard_system_3x_2026-06-10.md
- Bundle capacity drill: notes/research_drill_bundle_capacity_limits_2x_2026-06-09.md
- PP-244 (atomic capacity baseline): cycle 212

---

**Exp-Dev:** 35 experiments to aggressively overcome compositional depth barrier. P0 already filed (4 decisive gates 2hr). P1-P7 follow based on what P0 reveals.

This is the empirical assault on the barrier that ended VSA's commercial uptake in 2010s. Push hard.

**Run P0 first.** Results gate P1-P7 sequencing.
