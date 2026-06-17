# PREREG (DRAFT): Efficiency-composition RECAPTURE -- 3-arm operator-swap bake-off (unitarity / resonator / GSBC)

**Author:** Exp-Dev (Prover)  **Date:** 2026-06-17  **Status:** DRAFT (R4 Track-F; Day-2 REMOTE) -- pending Skunkworks SCHEMA-VET + Director STEP-2 LOCK before cell-author.
**Drill source:** notes/research_efficiency_composition_recapture_3x_2026-06-17.md (18-citation 3-angle lit-scan + Opus synthesis).
**Recaptures:** scorecard claim 18 (efficiency-composition) -- STEP-4 disposition = MIDDLE sub-multiplicative 16x (partial; not a multiplicative-composition win).
**Part of:** Director R4 Tier-2 ECONOMICS BATCH (8a active-gating + 8b surprise-gating + 18 efficiency-composition; this prereg = the 18 component).

## Honest-recapture framing (load-bearing; HONEST-NEGATIVE acceptable)
The MIDDLE 16x sub-mult verdict is currently read as a PARTIAL composition win. The drill reframes it honestly (per the
USER-LOCKED measured-bounds rule): 16x is the envelope OF THIS METHOD/CONFIG (current binder + brute decoder + dense
coding), NOT fundamental. Smolensky 1990: true multiplicative k^d is provably unreachable in fixed-width VSA without
N^d storage -- so "multiplicative recapture" must come from one of 3 mechanisms (unitary binder / resonator decoder /
dense-Hopfield energy), NOT from raw same-space binding. This is NOT a re-run of the failing config; it swaps the
operator class. HARD-FAIL on ALL arms is an ACCEPTABLE, load-bearing outcome (verdict HONEST_BOUNDED): "sub-mult ceiling
is INTRINSIC to same-space binding; only Smolensky tensor-product [storage-prohibitive] or Dense-Hopfield order-n energy
[architectural pivot] remain" -- a real finding that bounds the substrate's composition claim. P(>=1 HARD-PASS)=0.65;
P(all-fail intrinsic)=0.20 (drill, deflated).

## Design (3-arm bake-off; operator-swap only; reuse existing cell harness)
```
BASE CELL: experiments/exp_substrate_efficiency_composition_b3axb3b_v1_n2048.py (N=2048; the MIDDLE-16x anchor).
METRIC (decisive): ratio observed_capacity / theoretical_multiplicative at held-out composition depths d=2,3,4.
   Secondary: decode latency scaling (O(f*k) vs O(k^f)); sparsity preservation across iterated binding (ARM C).
ARM A (unitarity recapture): swap binder -> UNITARY projection (Plate complex-magnitude OR Gosmann-Eliasmith VTB).
   N held FIXED. Tests whether a non-fully-unitary binder (variance amplification) is the capacity-slope bottleneck.
ARM B (resonator-decoder recapture): keep binder, swap decoder -> RESONATOR dynamics (Kent-Frady 2020 iterative
   codebook projection). Storage held FIXED. Tests addressable k^f composite space at O(f*k) decode vs brute O(k^f).
ARM C (sparse block-code recapture): swap -> GSBC (Hersche 2023) sparse binding + stochastic factorizer. Tests
   multiplicative addressable reach AND lower decode latency than ARM B.
SEEDS: smoke 1; FULL >=3 (cert-chain target). COMPUTE: HEAVY (operator swaps + capacity sweeps d<=4 at N=2048+) ->
   REMOTE (R4 Day-2 per Director 3-track plan). NOT laptop.
```

## Pre-registered bands (from drill (c); per-arm)
```
ARM A HARD-PASS: capacity slope >= 0.85 * linear-in-N theoretical at d=2 AND sub-mult factor closes to <= 4x (from 16x).
   HARD-FAIL:    capacity slope <= 0.60 of linear-in-N -> binder is NOT the bottleneck.
ARM B HARD-PASS: factorization success >= 0.80 at f=3,k=N^(1/3) AND decode latency O(f*k) not O(k^f).
   HARD-FAIL:    factorization success <= 0.50 at f=3 -> decoder dynamics do not recover multiplicative reach.
ARM C HARD-PASS (R2 -- ABSOLUTE bar, independent of ARM-B so it is scorable when ARM-B fails): factorization
   success >= 0.80 at f=3,k=N^(1/3) (the SAME absolute bar as ARM-B's target, NOT "matches ARM-B") AND >= 2x faster
   wall-clock than ARM-B's decode AND sparsity preserved across >= 3 depths.
   HARD-FAIL:    factorization success <= 0.50 at f=3 OR sparsity collapses (density grows linearly with depth).
```

## R1 -- DISCRIMINATING-REGIME GUARD per depth (Skunkworks-required; DEGENERATE-REGIME-NOT-REFUTATION class)
```
BEFORE scoring per-arm HARD-PASS/HARD-FAIL at a depth d, CONFIRM that depth is in the DISCRIMINATING range:
   a REFERENCE point (e.g. ARM-A unitary at the lowest load, or the dense oracle) achieves composite recall
   measurably > chance AND < ceiling at d. If at depth d ALL arms (incl. the reference) collapse to ~0 -- e.g.
   d=4 at N=2048 may be beyond EVERY method's reach -- that depth is a NON-TEST (the task is degenerate-hard there,
   not the methods failing): REPORT it as NON-TEST, DO NOT score it as HARD-FAIL, and DO NOT let it drive the
   all-arms-fail -> "intrinsic sub-mult ceiling" verdict. The HONEST_BOUNDED (intrinsic-ceiling) verdict requires
   all arms to fail AT A DEPTH THAT IS DEMONSTRABLY DISCRIMINATING (reference > chance). (D-ECR both-1.000 lesson
   applied to the low-end dead-zone: saturation at EITHER end = a non-test, not a verdict.)
VERDICT MAP:
   any arm HARD-PASS -> PASS (recapture; cap_map green "linear-capacity vectors address k^f composite space"); the
      winning arm's mechanism is the recaptured capability (cert-grade at FULL >=3 seeds; method-contingent envelope).
   all 3 HARD-FAIL  -> HONEST_BOUNDED (sub-mult ceiling INTRINSIC; next = Dense-Hopfield order-n drill OR Smolensky
      [storage-prohibitive]). Claim 18 stays at the qualified "sub-mult ceiling under fixed operator class".
   mixed/between    -> MIDDLE_BAND per-arm (report the surface; inform the architectural-pivot decision).
```

## Provenance (recapture_of populated per Skunkworks ruling B; structured metadata)
- recapture_of = scorecard_claim_18_efficiency_composition (MIDDLE sub-mult 16x; cell efficiency_composition_b3axb3b_v1_n2048)
- failing_config_avoided = same-space binding (non-fully-unitary circular conv) + brute O(k^f) decoder + dense coding
  -> sub-mult 16x ceiling (read as partial-win; actually operator-class-bound, not fundamental)
- method_delta = operator-class SWAP on 3 independent axes (binder->unitary / decoder->resonator / coding->GSBC-sparse),
  same cell harness + same N; tests whether the 16x ceiling is a unitarity/decoder/sparsity artifact vs intrinsic.
- FULL >=3 seeds -> CERT_CHAIN_GRADE. method-contingent (operator-class + N axes).

## Cert-chain next steps
1. Skunkworks SCHEMA-VET: method-genuinely-different (YES: operator-swap, not re-run); falsifiable (per-arm bands);
   metric-matches-semantic (capacity-ratio = the multiplicative-composition claim; no Goodhart); cert-criteria (>=3 seed).
   + confirm the "good-enough efficiency" Tier-2 framing (this is the COMPOSITION-CAPACITY component; the gating-efficiency
   components 8a/8b are separate preregs in the same batch).
2. Director STEP-2 LOCK.
3. Exp-Dev cell-author (3-arm operator-swap harness) + verification witness + smoke (laptop, tiny N) -> FULL (REMOTE, N=2048+,
   d<=4, >=3 seeds) -> verdict -> re-atomize.

## Batch note (8a + 8b siblings; separate preregs)
This is 1 of 3 in the Director's Tier-2 economics batch. SIBLINGS to draft next (their drills):
  - 8b surprise-gating: notes/research_surprise_gating_B3b_recapture_3x_2026-06-17.md (next draft).
  - 8a active-gating: notes/research_drill_multiplicative_gating_vs_additive_2x + storage-efficiency drills.
All 3 run R4 Day-2 REMOTE as one track ("good-enough efficiency" honest bar; gates overlap -> sub-multiplicative expected).
B8 logit-residual = SKIPPED (Director: resolved as memory-reconstruction, not LM-frontier).

-- Exp-Dev (Prover) [DRAFT]
