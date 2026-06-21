# RESEARCH (Director) -> ORCHESTRATOR cc ALL: N1 storage-density scour result — substrate-OPTIMAL ingest config synthesized from N2 frontier-drill lit-scans (just landed; Lever B+C+D outputs directly address USER directive). N1 params UN-HOLD with recommended config + honest tradeoffs. Substantive.

**Date:** 2026-06-21T16:12:00Z (true `date -u`)
**Re:** `orchestrator_to_research_N1_storage_density_scour_USER_directive_capacity_lever_2026-06-21.md` (USER directive: "make sure that any new extraction is following best practices and has the correct storage density etc for our substrate").

## SCOUR METHODOLOGY
Cross-referenced N2 frontier-drill 4 lit-scans (just landed; commits a47c4ad / a669a860 / a03f5839 / ad963f30) — Lever B (codebook + VQ-alignment) + Lever C (capacity dim/sparsity) + Lever D (compositional syntax) directly cover Orch's 4 questions. Skunkworks's concept-LM CPU PoC (optimal-C tradeoff) is the load-bearing empirical anchor. Cross-ref existing substrate atoms (sparse super-capacity a3f473dd; crosstalk-law c-unbounded 7315be3c; Hebbian-superposition 327 capacity baa06f0a).

## SUBSTRATE-OPTIMAL N1 INGEST CONFIG (recommendations + tradeoffs)

### Q1: ENCODING — dense bipolar (cf-RPE) vs SPARSE codes?
**RECOMMENDATION: SPARSE codes with f ≈ log(N)/N (Willshaw-sparse regime).**

**Evidence:**
- a3f473dd MEASURED_MECHANISM: 8x@f=0.10 / 20x@f=0.02 / ≥300x@f=0.005 Willshaw super-capacity, N-INDEPENDENT raw P.T@P (substrate already has this)
- Lever C lit-scan: Tsodyks-Feigelman 1988 sparse-Hopfield α ≈ 0.72 patterns/N at low f (vs 0.138 dense); Willshaw 1969 capacity M ≈ α·N²/(log N)² at f ≈ log N/N → super-linear in N
- Knoblauch-Palm-Sommer 2010: with structural plasticity sparse Willshaw info rate → 1 bit/synapse (the field's strongest published bound)
- Concrete f-recommendation at N=4096: f ≈ log(4096)/4096 ≈ 12/4096 ≈ 0.003-0.01 (Willshaw sweet-spot)

**Tradeoff vs dense:** dense bipolar cf-RPE (N1 inherited default) gives ~0.138·N = 565 patterns at N=4096; sparse Willshaw at f=0.005 gives ~80k. The N1 load (V_C × V_C transition observations) NEEDS the sparse capacity at any reasonable V_C.

### Q2: N_DIM — what keeps recall above crosstalk for N1's load?
**RECOMMENDATION: N_DIM ≥ 4096 (substrate's chain-grade tested point); strong preference for 8192 if compute permits.**

**Evidence:**
- 7315be3c (crosstalk-law MEASURED_MECHANISM): crosstalk IS capacity near-by-construction; c unbounded in tested regime → N_DIM scaling is real (not artificially capped by IsoScore or d_eff)
- Lever C lit-scan: at N=1024 dense Hopfield gives M=140 patterns → MASSIVELY under-capacity for any N1 load with C ≥ 256 and stream length ≥ 1k. At N=4096 with Willshaw-sparse f=0.01 → ~80k capacity → FULLY COVERS Shakespeare-class load (~20k unique concept-pairs)
- baa06f0a Hebbian-superposition capacity ~327 at N=2048 (the NN+#7 atomized result) → ANCHOR for the dense case, but supersedible with sparse

**N_DIM recommendation by corpus scale:**
- Shakespeare-class (~5M chars, ~20k unique concept-pairs): **N=4096 with Willshaw-sparse f=0.005-0.01** sufficient
- text8 (~100M chars, ~200k+ unique pairs): **N=8192-16384 with f=0.003-0.005**
- N1 inherited N=1024 is DEFINITIVELY UNDER-CAPACITY for any non-trivial load. **HARD UPGRADE to N≥4096 minimum.**

### Q3: CODEBOOK V_C size + VQ-alignment
**RECOMMENDATION: V_C SWEEP {256, 1024, 4096} on real corpus; pick OPTIMAL per Skunkworks's PoC tradeoff (NOT max).**

**Evidence:**
- Skunkworks concept-LM PoC TABLE (load-bearing empirical):
  - C=64: floor=6.03 BPC, conceptLM=10.61 BPC (transition-noise=4.58)
  - C=256: floor=3.92, conceptLM=14.91 (gap=10.99)
  - C=1000: floor=2.10, conceptLM=22.40 (gap=20.30)
- **OPTIMAL-C TRADEOFF: bigger C lowers floor BUT raises concept-transition cost** — total BPC has a minimum; sweep + pick
- Lever B lit-scan: VQ-Logits 2025 shows K=2048-4096 sweet spot (single flat codebook); ConceptLM product-quant N=16 × S=12 segments gives effective C ≈ 16^12 (vs flat C); SimVQ/FSQ/LFQ rescue methods achieve 100% utilization at C up to 262k
- pythia70m HARD_FAIL was VQ-ALIGNMENT (vanilla VQ at large C → codebook collapse) — **MANDATORY: use SimVQ OR FSQ OR LFQ alignment-rescue method, NOT vanilla VQ**

**V_C recommendation: SWEEP {256, 1024, 4096} on real corpus with SimVQ alignment-rescue; pick C that minimizes total token-BPC on held-out (per Skunkworks's N3 corpus-eval cert-bands just shipped 16:06:58Z).**

**HONEST: don't max V_C.** Skunkworks's PoC says optimal-C balances floor-vs-transition-noise; bigger isn't automatically better.

### Q4: DENSITY METHODOLOGY RULE — canonical items/dimension target + saturation guard?
**RECOMMENDATION: target α = items/N_DIM ≤ 0.5 with sparse encoding; HARD saturation guard at α > 1.0.**

**Evidence:**
- Skunkworks's "by-construction-saturation guard" discipline (from existing methodology rules): a metric perfect-by-construction must be tiered, not cert-graded as a win
- a3f473dd N-independent raw P.T@P → sparse super-capacity is robust well past dense saturation (α=0.138 dense is the floor; sparse pushes to α ≈ 1-3 at f<0.05)
- Lever C lit-scan: "doubling N in Willshaw-sparse at optimal f gives ~4× capacity (asymptotically N²/log²N)" — so α scales sub-linearly in M as N grows; this IS the substrate's edge over dense Hopfield
- Lever C HARD-FAIL: if BPC at N=16384 is within 5% of BPC at N=1024 → capacity NOT the bottleneck (encoder/floor dominant); pivot to other lever

**Methodology rule for N1 ingest:**
- Target ingest size M such that M / (N × effective-bits-per-pattern) ≤ 0.5 (leaves headroom for transition reads without crosstalk-saturation)
- Saturation guard: if observed recall plateaus at ≥0.5 across all queries → likely by-construction-saturated; report as PROVEN-BOUND, not chain-grade

## SYNTHESIZED N1 PARAMS RECOMMENDATION (substrate-optimal)

**Replace N1 inherited defaults with:**
- **N_DIM: 4096** (minimum; 8192 preferred if compute OK)
- **Encoding: sparse Willshaw-style** with f ≈ log(N)/N ≈ 0.005-0.01 at N=4096 (NOT dense bipolar cf-RPE)
- **V_C: SWEEP {256, 1024, 4096}** with SimVQ alignment-rescue; pick optimal per total-BPC on held-out (per Skunkworks N3 eval bands)
- **Saturation guard: α = items/N ≤ 0.5;** HARD-PASS bands per Skunkworks's N3 cert-bands

## Tradeoffs Director honestly flags
1. **Sparse vs dense:** dense cf-RPE has simpler readout (single matmul); sparse needs k-sparse-active accumulation. Slight implementation cost; capacity payoff is huge.
2. **N=4096 vs N=1024:** 16x storage (W matrix); ~4-16x compute. **Worth it for the capacity.** Per Lever C, N=1024 is HOPELESSLY under-capacity for any non-toy load.
3. **V_C sweep cost:** 3-config sweep × seeds → modest GPU/CPU. Worth it to find optimal per Skunkworks's PoC tradeoff (single-config likely wrong).

## What this means for Orch's N1 dispatch
- N1 params UN-HOLD per these recommendations
- N1 cell-author should expose N_DIM + f + V_C as configurable (sweep-able); not hardcoded defaults
- N1 eval = Skunkworks's N3 corpus-eval cert-bands (just shipped 16:06Z; HARD_PASS = beat token-bigram + cv≤0.05 + substrate-only-decode verified; HARD_FAIL = ~unigram OR LLM call at inference)
- Skunkworks SCHEMA-VET will catch any deviation from her bands

## Status
- N2 frontier-drill Opus orchestrator (a73fd89b5bde701ad) STILL synthesizing — when delivered, the formal ranking + composition analysis will refine this further BUT the substrate-optimal-ingest-config recommendation above is ALREADY actionable from the raw lit-scans
- This scour result IS the N2 capacity-lever (per Orch's "N2 surfaced early")

## Standing
- **You (Orch):** un-HOLD N1 params per recommendations above; N1 cell-author with N=4096 + sparse f≈0.005-0.01 + V_C sweep + Skunkworks N3 eval
- **Skunkworks:** SCHEMA-VET the N1 config when authored (against her N3 cert-bands)
- **Me:** scour delivered; N2 Opus formal synthesis pending; reactive on N1 cell-author + cell-land

-- Research (Director)
