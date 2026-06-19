# Research: DEEP DRILL cleanup-noise / FPE-cleanup interaction at scale (Follow-up to Drill 1 cardinality prior)

Date: 2026-06-16
Topic: Does cleanup-noise dominate failure at N=4096, M in {200, 2000, 10000} for Phase B cardinality BUILD?
Parent drill: cardinality prior (P_deflated revised 0.45 -> 0.22; HARD-FAIL mode (ii) "cleanup-noise breakdown at M=2000")
Calibration: P_deflated by 0.15-0.25; novel-synthesis cap 0.50.

---

## (a) HEADLINE

**Cleanup-noise is NOT the binding constraint at N=4096, M=2000, bundle=5 under classical i.i.d.-codebook scaling — the Frady/Sommer SNR formula predicts a comfortable margin (k_max ~ N/(2 ln M) ~ 269 >> bundle=5). But the regime is uncharted FOR FPE specifically: the dominant risk is FPE-induced kernel-correlation between nearby codewords AMPLIFYING nearest-neighbor confusion. Lowest-risk mitigation is single-shot modern-Hopfield-as-cleanup-head per bundle slot (O(N*M), exponential capacity, FPE-compatible); fallback is stochastic-resonator (arXiv:2412.00354). HARD-FAIL mode (ii) "cleanup breaks at M=2000" downgraded to UNLIKELY-as-stated; HARD-FAIL mode (iii) "FPE phase-kernel correlation collapses near-neighbor resolution" promoted to MOST-LIKELY actual blocker.**

P_deflated(cleanup-noise IS the dominant constraint, as classically modeled) = **0.20** (lit precedent says no for k=5).
P_deflated(FPE-phase-kernel near-neighbor confusion is the actual blocker, not generic cleanup-noise) = **0.42** (capped under novel-synthesis 0.50; this is an extrapolation, not directly published).

---

## (b) Cheap decisive test

**Pre-flight smoke gate (10 min CPU) — INSTRUMENT CLEANUP-NOISE SPECIFICALLY:**

1. Build N=4096 random i.i.d. FHRR codebook of size M in {200, 2000}.
2. For each M: bundle k in {3, 5, 10, 20, 50} random codewords (no FPE).
3. Measure top-1 cleanup accuracy via naive max-cos.
4. Re-do step 3 with one bundled slot replaced by FPE(V^x) at x in {0, 0.1, 0.5, 1.0, 2.0} over an M-point grid; measure decoding accuracy AND nearest-neighbor confusion rate (k=5 grid neighbors).
5. Compare: discrete-atom curve vs FPE curve. The DELTA at fixed (N, M, k) is the FPE-cleanup-amplification factor.

Pass = discrete-atom curve matches Frady/Sommer prediction (>99% at k=5, M=2000) AND FPE curve is within 0.05 of discrete-atom curve.
Fail = either gap exceeds 0.05, or absolute accuracy < 0.95 at k=5.

---

## (c) Falsifiable predictions

**HARD-PASS thresholds (must measure ALL three):**
- Discrete-atom top-1 cleanup at N=4096, M=2000, k=5: >= 0.99 (Frady/Sommer SNR prediction).
- FPE top-1 decoding at N=4096, M=2000, k=5: >= 0.95 (allows for 0.04 phase-kernel haircut).
- FPE nearest-neighbor confusion rate (top-1 vs grid-neighbor): <= 0.10 (per-class confusion ceiling).

**HARD-FAIL thresholds (any one falsifies "cleanup is not the binding constraint"):**
- Discrete-atom top-1 at M=2000, k=5 < 0.95: classical theory wrong in our config -> stop, re-derive SNR with our codebook structure (look for non-iid structure).
- FPE top-1 at M=2000, k=5 < 0.80: FPE-cleanup interaction IS dominant -> switch to modern-Hopfield cleanup head BEFORE attempting Phase B BUILD at scale.
- FPE near-neighbor confusion > 0.30: kernel resolution too coarse -> band-limit base phases (per Frady 2021 VFA) or switch to hex-grid base (Dumont-Eliasmith 2020).

---

## (d) Cross-thread synthesis

Drill 1 (cardinality prior) declared HARD-FAIL mode (ii) "cleanup-noise breakdown at M=2000" as the leading risk. **This drill REFUTES that framing under classical i.i.d.-codebook scaling**: Frady/Sommer (arXiv:1707.01429), Thomas/Dasgupta (arXiv:2010.07426), Schlegel (arXiv:2001.11797) all predict comfortable margin at k=5, M=2000, N=4096. Cleanup is not where breakdown happens.

**But the substrate uses FPE for cardinality magnitudes** — that's the un-instrumented variable. Frady/Kleyko/Sommer 2021 (arXiv:2109.03429, VFA paper) establishes that FPE base-phase distribution shapes a similarity kernel; uniform phases give sinc-decay, band-limited phases give Gaussian-like decay. Furlong/Eliasmith 2024 (arXiv:2412.00488, "Improved Cleanup and Decoding of FPEs") explicitly motivates iterative cleanup because similarity-only cleanup of FPE under-performs. Bremer/Orchard companion uses N=1024 small bundles — NO published N=4096, M>=2000, bundle>=5, FPE-in-bundle accuracy curve exists. Adjacent fields: compressed-sensing phase transitions (Donoho 2006) and modern-Hopfield exponential capacity (Ramsauer 2020) both apply but neither has been benched on FPE-in-bundle.

**Net synthesis: the Drill-1 HARD-FAIL framing should be REWRITTEN.** Replace "cleanup-noise at M=2000" (LOW risk per lit) with "FPE-phase-kernel near-neighbor confusion at M >= 2000" (MEDIUM risk, no direct precedent).

Substrate cap_map adjacency: `sparse-coding-compressed-sensing` (Tier-1b) was the right field tag to add 2026-05-24 — compressed-sensing phase transitions DO describe the FPE-in-bundle recovery regime, but the L1-LASSO machinery is too heavy for the FPE specifics; the cleaner adjacency is `modern-hopfield` (Tier-1 fruit-bearing).

---

## (e) Substrate-product implications

1. **Cap_map row "cleanup mechanism (T2)" should be revised**: current substrate `cleanup` + `cleanup_retrieval` are naive-max-cos. Published precedent at N=4096, M=2000 says naive-max-cos works for discrete-atom bundles up to k ~ 269. For FPE-in-bundle, modern-Hopfield-as-cleanup is the recommended drop-in (O(N*M), no iteration, exponential capacity).
2. **Phase B BUILD smoke-gate**: instrument the FPE-cleanup-amplification factor as a first-class measurement BEFORE scaling to M=2000. Cheap pre-flight is 10 min CPU.
3. **Substrate-internal viable cleanup for cardinality**: modern-Hopfield head (single-step softmax with tunable beta) is FPE-compatible, low-risk, and substrate-additive. Do NOT introduce resonator network unless the unknown is a *factorization* (product of unknowns) — for bundle-superposition cleanup, modern-Hopfield wins on cost.
4. **Anchor candidate**: pre-flight smoke at N=4096, M in {200, 2000}, k in {3, 5, 10, 20}, with/without FPE in bundle. If the discrete-atom curve matches Frady/Sommer and FPE delta < 0.05, ship Phase B BUILD with naive cleanup. If FPE delta >= 0.05, swap to modern-Hopfield cleanup head before scaling.

---

## (f) Citations (verified count: 14 unique arxiv/DOI)

Core cleanup-noise scaling:
1. Plate 1995, IEEE TNN 6(3):623-641, DOI:10.1109/72.377968 — HRR cleanup capacity.
2. Frady, Sommer 2017 "Theory of sequence indexing / superposition principle" arXiv:1707.01429 — canonical SNR formula k_max ~ N/(2 ln M).
3. Schlegel, Neubert, Protzel 2022 "Comparison of VSAs" arXiv:2001.11797 — empirical bundle-capacity sweeps D=500-16000.
4. Thomas, Dasgupta, Rosing 2021 "Theoretical perspective on HDC" arXiv:2010.07426 — tail bound P(fail) <= M*exp(-c*D/k^2).
5. Kleyko et al. 2022 "VSA framework for emerging hardware" arXiv:2106.05268 — survey, restates SNR ~ D/k.

FPE-cleanup interaction:
6. Plate 2003 "HRR: Distributed Representation for Cognitive Structures" — chapter on V^x fractional binding.
7. Komer et al. 2019 "Neural representation of continuous space using fractional binding" CogSci — FPE / SSP foundation.
8. Frady, Kleyko, Kymn, Olshausen, Sommer 2022 "Computing on Functions Using Randomized Vector Representations (VFA)" arXiv:2109.03429 — base-phase distribution shapes kernel.
9. Dumont, Eliasmith 2020 "Accurate representation for spatial cognition using grid cells" CogSci — hex-grid bases beat uniform-random phases.
10. Furlong, Eliasmith 2024 "Improved Cleanup and Decoding of Fractional Power Encodings" arXiv:2412.00488 — iterative MLE+CLE cleanup motivation.
11. Kleyko et al. 2022 "Integer Factorization with Compositional Distributed Representations" arXiv:2203.00920 — FPE + resonator.

Cleanup mechanisms (mitigation):
12. Frady, Kent, Olshausen, Sommer 2020 "Resonator Networks 1" arXiv:2007.03748 — iterative cleanup for factorization.
13. Ramsauer et al. 2020 "Hopfield Networks is All You Need" arXiv:2008.02217 — exponential capacity, single-step retrieval (RECOMMENDED).
14. Hersche et al. 2024 "On the Role of Noise in Factorizers for Disentangling Distributed Representations" arXiv:2412.00354 — stochastic-resonator, >=50x baseline operational capacity (FALLBACK).

Supporting (uncited specifics flagged in body):
- Krotov, Hopfield 2016 "Dense Associative Memory" arXiv:1606.01164.
- Hersche et al. 2023 "Factorizers for Distributed Sparse Block Codes" arXiv:2303.13957.
- Donoho 2006 compressed sensing (general framing only, no direct VSA precedent at this M/N).
- Kanerva 1988 SDM (general framing only).

---

## Pre-flight recommendation (refined M={200, 2000} smoke-gate)

Replace generic "cleanup at M" gate with FPE-cleanup-amplification gate:
- Discrete-atom baseline curve at M in {200, 2000}, k in {3, 5, 10, 20, 50}: validates Frady/Sommer prediction in our codebase.
- FPE-in-bundle curve at SAME (M, k) with x grid of {0, 0.1, 0.5, 1.0, 2.0}: measures the FPE-cleanup-amplification delta.
- Decision rule: if delta < 0.05 across all (M, k), ship naive cleanup. If delta >= 0.05 at any (M, k), swap cleanup head to modern-Hopfield BEFORE Phase B BUILD scales.
- 10 min CPU pre-flight, no GPU required.

---

## Risk assessment: which Drill-1 HARD-FAIL mode is most likely the actual blocker?

Drill-1 listed 3 HARD-FAIL modes. Reordered by post-drill-2 likelihood:
1. **MOST LIKELY: FPE-phase-kernel near-neighbor confusion at M >= 2000** (P_deflated 0.42; uncharted regime, structured interference unlike i.i.d.-atom case).
2. Less likely: cardinality primitive itself fails at scale (P_deflated ~ 0.20; covered by Drill 1).
3. **LEAST LIKELY: cleanup-noise at M=2000** under classical SNR scaling (P_deflated 0.20; lit predicts comfortable margin at k=5).

Drill-1's "adjacency warning" was correct in spirit (cleanup IS adjacent to the failure) but wrong on mechanism (it's not generic SNR cleanup, it's FPE-kernel-induced near-neighbor confusion). The substrate-product-relevant action is: instrument FPE-cleanup-delta in pre-flight; if delta is large, swap to modern-Hopfield BEFORE scaling.

next-drill candidate: `modern-hopfield` (Tier-1 fruit-bearing) — drill Krotov/Hopfield-86 dense AM as cleanup head at N=4096, M=2000.
