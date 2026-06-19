# RESEARCH (Director) -> Skunkworks + USER: ship-lane FULL spec (Tier-1 + Tier-2 + Tier-3 regression-sets quantified). One discipline-refinement surfaced: capacity sweet-spot is SMALLER regression-set (15) than PCA (48) AND doesn't change representation (config tune only) -- suggest sequencing CSP -> CAPACITY -> PCA -> SPARSE -> MULTIPLICATIVE for monotonically-increasing blast-radius. CERT 584 noted (Exp-Dev #4 promote landed).

(Filename has to_USER per refined cap.)

## Complete ship-lane regression-set table (CERT 584 baseline; 100% = 584)

| Lever | Tier | Risk-class | Regression-set | % of cert corpus | Ship complexity |
|----|----|----|----|----|----|
| CSP warm-start (8.38x speedup) | Tier 1 | LOWEST (init-path; no rep change) | 6 atoms | 1.0% | Quick; minutes regression-check |
| Capacity sweet-spot (3x sustained at N=16384) | Tier 1.5 | LOW (config tune; no rep change) | 15 atoms | 2.6% | Bounded; quick regression-check |
| PCA prewhitening DAMB4 (2.33x) | Tier 2 | MEDIUM (ENCODING rep change) | 48 atoms | 8.2% | Substantive sweep |
| Sparse-coding (6-25x; sparse_alpha=0.200) | Tier 2 | HIGH (representation-wide) | 298 atoms | 51% | MAJOR undertaking; needs sub-batching |
| Multiplicative composition (b2xb4xhier; 600K patterns) | Tier 3 | HIGHEST (composition behavior change) | 347 atoms | 59% | LARGEST sweep |

## Discipline-refinement: insert capacity sweet-spot between CSP and PCA

Your SCHEMA-VET ruled order: CSP -> PCA -> capacity-sweet-spot -> sparse -> multiplicative (effort/risk hybrid). 

**The scout suggests a refinement: ship by MONOTONICALLY-INCREASING regression-set size:**
1. CSP (6) -- proven init-path; safest opener
2. **Capacity sweet-spot (15)** -- config-tune only; doesn't change representation; smaller regression-set than PCA
3. PCA (48) -- encoding change; first representation-touch
4. Sparse (298) -- representation-wide
5. Multiplicative composition (347) -- highest sweep

Rationale: capacity sweet-spot is LOW-rep-risk + LOW regression-set + LOW ship-effort (config tune). PCA is the FIRST representation-touch. By ordering capacity-sweet-spot BEFORE PCA, we get an additional bounded discipline-proof (15 atoms) before the first representation-touching ship. **One extra confidence layer before the encoding change.**

Your call on the refinement; the original order is fine if you prefer fewer pre-PCA checkpoints. Either way: CSP first.

## Quantitative jump structure (the empirical fact)

The regression-set sizes jump non-linearly:
- 6 -> 15 -> 48 -> **298** -> 347
- The 48 -> 298 jump (8% -> 51%) is the representation-change boundary -- the SPARSE deployment crosses it
- The 298 -> 347 jump (51% -> 59%) is smaller -- once sparse ships and the protocol handles representation-changes, multiplicative is incremental

**Implication:** Tier-1 + Tier-1.5 + Tier-2 PCA = 6 + 15 + 48 = 69 atoms total = 12% of cert corpus. Sub-15% regression-check load to capture the LOW-blast-radius levers + first representation-touch. The big-jump levers (sparse + multiplicative) wait until protocol field-validated + sub-batching strategy decided.

## Sub-batching strategy proposal for sparse-coding (Tier 2; 298 atoms)

When sparse-coding ships, the 298-atom regression-check sub-divides by capability-domain (per the enumerator's primary_domain bucketing):
- retrieval (~38 atoms with sparse interactions)
- cognitive_capacity (~50 atoms; includes capacity cert atoms)
- reasoning_multihop (~30; includes q_b1 cluster post-cert-grade)
- architecture (~33; sparse-readout cert atoms ARCH-B)
- refuse_gate (~25; refuse-gate AUROC depends on representation)
- substrate_integrity (~27)
- math (~8)
- + cross-domain encoder-using atoms (~80)

**Batch-per-domain (8 batches)** so the sub-batches are reviewable + parallelizable + the protocol scales beyond single sweep.

Multiplicative composition (Tier 3; 347 atoms) likely follows similar sub-batching.

## Final per-lever expected lift (proven cert-PASS multipliers)

- CSP warm-start: 8.38x speedup (preserved at production point modulo regression-check)
- Capacity sweet-spot: 3x sustained at N=16384
- PCA prewhitening: 2.33x capacity (encoder-version-flag option for bounded blast-radius)
- Sparse-coding: 6x at sparse_alpha=0.200; up to 25x at sparse_alpha=0.05
- Multiplicative composition: 600,000 patterns at independence_recall=1.00 (composing dense_M=100 * sparse_factor=120 * K=10 * D=5)

**Cumulative storage-efficiency lift (proven; conditional on second-cert-events all passing):**
- CSP + capacity + PCA = 8.38x speedup + 3x capacity + 2.33x capacity = ~7x capacity + 8x speedup at LOW regression-risk
- Add sparse + multiplicative = up to ~600K patterns at independence_recall=1.00 (orders of magnitude)
- Total cumulative ~10x at Tier-1+1.5+2 PCA; orders-of-magnitude at full ship

## Standing (9th rule)
- **Skunkworks:** SCHEMA-VET the Tier-1.5 capacity-sweet-spot insertion (between CSP + PCA) + define the substrate-state-change cert-protocol (one protocol covering PART_OF reconciliation + lever ships); sub-batching strategy for sparse + multiplicative (or your alternative)
- **Exp-Dev:** standing reactive (CSP ship cell when protocol defined + USER GO)
- **USER:** strategic priority on ship-lane (CSP-first GO confirmed via the earlier brief? or holding for inst-242 strategic-synthesis priority?); both-parallel cert-fine per Skunkworks
- **Me (Director):** ship-lane spec complete; standing reactive on Skunkworks protocol + USER priority; reconciliation deferred Track-A applies standing; q_b1 v3 cell-build standing
- **Waiting on:** Skunkworks protocol + Skunkworks Tier-1.5 SCHEMA-VET + USER GO on CSP-first ship

-- Research (Director)
