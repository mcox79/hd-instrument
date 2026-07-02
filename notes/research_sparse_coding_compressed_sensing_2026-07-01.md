# Sparse-Coding / Compressed-Sensing Research Drill — 2026-07-01

**Filed:** 2026-07-01 post-compaction (durable copy of sub-agent return; sub-agent did not persist)
**Trigger:** Follow-up drill from hidden phase-diagram dimensions research (Dim H distributional-shape mapped to L1-recovery phase transitions)
**Field:** sparse-coding / compressed-sensing (drill_count=0 → 1)

## HEADLINE

Substrate is NOT a direct compressed-sensing system, but its capacity wall is structurally isomorphic to the Donoho-Tanner L1-recovery phase boundary — with the AMP denoising frame being the tightest analogy for the cleanup pass, and Zipfian workloads predicted to push the effective wall ~15-30% earlier than uniform-signal CS theory would project.

**P_deflated = 0.38** (strong structural isomorphism claim; deflated from raw 0.55 due to Gram-matrix vs. random-matrix mismatch and absence of direct empirical test in substrate).

## Ranking of Candidate Mappings

1. **D: Message-passing / AMP framing (P_def = 0.48)** — strongest. Substrate cleanup pass is mechanistically isomorphic to one step of AMP denoising. State evolution (Donoho-Maleki-Montanari 2009) predicts phase transition at Bayes-optimal threshold = observed cliff. Predicts a **hard phase** region where patterns are stored but unrecoverable by iterative cleanup alone.

2. **A: Direct Donoho-Tanner mapping (P_def = 0.38)** — moderate. Substrate analogy: N=vector-dim, M=stored-patterns, K=effective-support. Wall condition K/N ≈ 0.14 (classical Hopfield) maps to ρ=K/M ~ 1 at δ=M/N ~ 0.14 — sits ON the Donoho-Tanner strong threshold curve. Caveat: W is a Gram matrix, not a random measurement matrix; RIP violated; qualitative structure preserved, quantitative bounds degraded.

3. **B: Random matrix / RIP framing (P_def = 0.30)** — informative cross-check. For i.i.d. Gaussian patterns, W/N → Wishart; Marchenko-Pastur bounds. Data-dependent Gram matrix limits direct RIP application.

4. **C: Sparse dictionary learning (P_def = 0.25)** — weak. Substrate is nearest-neighbor Gram-search, not overcomplete-basis dictionary. Superposition-hypothesis literature (Elhage 2022) is adjacent for feature packing but not the algorithm.

5. **F: Hopfield-CS equivalence via Löwe (P_def = 0.22)** — Löwe 1998 correlated-pattern collapse is closer to SK spin-glass than CS. Same numerical answer at uniform-pattern limit via different mathematics. Cannot straightforwardly import Donoho-Tanner curves for Zipfian via Löwe route.

6. **E: Kernel PCA / effective rank (P_def = 0.18)** — least applicable. Wall is not a rank-saturation phenomenon but an interference-explosion phenomenon; effective-rank analysis gives smooth degradation not cliff.

## Zipfian-Workload Prediction (LOAD-BEARING FOR DIM H)

Donoho-Tanner is for uniform K-sparse signals. Under Zipfian amplitude power-law, effective sparsity K_eff is reduced (concentrates in ~K/α dimensions). Effective phase-diagram point shifts toward lower-left = deeper into recovery region for dominant patterns, but tail patterns sit near failure boundary.

**Two-tier wall structure prediction:**
- High-frequency patterns (large amplitude in W superposition): remain recoverable past nominal cliff.
- Low-frequency patterns (sparse contribution to W): fail first and fail earlier than uniform-signal CS.

For α=1.0 (standard web frequency): low-frequency tail failure onset at M/N ~ 0.10 vs 0.14 → **~28% earlier wall for tail patterns**.

**This directly drives Dim H (Zipfian) cell design:** test must sweep loads near cliff + noise axis to reveal Q1 (head) vs Q4 (tail) differential recall. Underloaded (M/N=0.10 far from wall) ceiling regime is *by construction saturated* on dense-Hopfield exponential capacity.

## Cheap Decisive Test

Sweep (K/M, M/N) grid on substrate; plot empirical wall vs Donoho-Tanner ρ_S(δ) = (2e·log(1/δ))^{-1}. Cost: 2-3 CPU-hr, N=1024, M∈[50, 300].

**HARD-PASS predictions:**
- CS-frame vindicated: empirical wall at K/M = 0.20 ± 0.03 when M/N = 0.14 (Gaussian random patterns, N=1024)
- AMP hard-phase exists: recall at load just above cliff shows partial (~30-50%) not complete failure (~0%); confirmed by comparing iterative cleanup vs simulated annealing recall

**HARD-FAIL predictions:**
- Wall at K/M > 0.35 at M/N = 0.14, OR no sharpening with N → substrate diverges fundamentally from CS
- Zipfian and uniform walls indistinguishable at p<0.05 → Zipfian-CS correction not operating

## Cross-Thread Synthesis

1. **Spin-glass connection (prior drills):** Hopfield-SK equivalence + CS frame are DUAL not competing. Kabashima et al. 2009 showed CS L1 = replica 1-RSB fixed point. Replica gives thermodynamic (theoretically recoverable); CS gives algorithmic (what iterative cleanup achieves).

2. **AMP/VAMP prior drills (33% yield):** Substrate cleanup is AMP-like but lacks Onsager correction term. Naive AMP diverges before Bayes-optimal threshold → predicts earlier empirical wall than theoretical AMP wall.

3. **Free probability (100% yield, 1 drill):** W eigenvalues follow Marchenko-Pastur for random Gaussian patterns. RIP constants determined by extreme eigenvalues of W restricted to K-sparse subspaces; Tracy-Widom fluctuations. Next-drill candidate.

## Substrate-Product Implications

1. **Capacity wall analytically predictable** from (N, K, α) — removes need for exhaustive capacity sweeps per config.

2. **Hard phase = recoverable with smarter cleanup** — patterns in M/N=0.14-0.18 stored but iterative cleanup can't retrieve. Simulated-annealing / beam-search cleanup would recover. Concrete product capability gap with known CS-theory solution.

3. **Zipfian correction for staging** — current capacity certs use uniform patterns; real workloads are Zipfian. Cert should report two-tier capacity rating (head vs tail) from Zipfian-CS correction.

4. **BIAS-O validation** — CS convention places labels at readout (pattern identity), not storage (basis index). Storage matrix W encodes patterns in superposition; "which pattern" determined at retrieval. Validates existing BIAS-O discipline from master checklist.

## Citations (verified from search)

1. Donoho & Tanner (2006). "Thresholds for the Recovery of Sparse Solutions via L1 Minimization." CISS 2006.
2. Donoho, Maleki & Montanari (2009). "Message-passing algorithms for compressed sensing." PNAS 106(45). Foundational AMP + state evolution.
3. Kabashima, Wadayama & Tanaka (2009). "A typical reconstruction limit for compressed sensing based on Lp-norm minimization." J. Stat. Mech. Bridges spin-glass and CS.
4. Donoho & Montanari (2016). "The Noise-Sensitivity Phase Transition in Compressed Sensing."
5. arXiv 2411.09868 (2024). "Phase Transitions with Structured Sparsity." Extension to non-uniform / block sparsity.
6. arXiv 1702.01096. "On the Strong Restricted Isometry Property of Bernoulli Random Matrices."
7. Elhage et al. (2022). "Toy Models of Superposition." Anthropic. Superposition-hypothesis for feature packing.

## Next-Drill Candidate

**Free-probability / Tracy-Widom on W eigenvalues (F2)** — directly constrains RIP constants that determine how far from Donoho-Tanner the substrate wall actually sits, given W is data-dependent Gram matrix not random measurement matrix. Would produce a mechanistic reason for the K/M=0.20 wall placement.

## Cells Driven By This Drill (2026-07-01)

- **Dim H Zipfian v2** — cell-author widening to add σ ∈ {0, 0.1, 0.2, 0.3} query-noise axis + load-sweep to {0.10, 0.20, 0.30, 0.50, 0.80, 1.20}; adds HP_TWO_TIER_ZIPFIAN metric (Q1-Q4 gap ≥ 0.15 at σ≥0.2, load≥0.30, α=1.0) as direct falsifier of two-tier prediction
- **Dim I HRR depth_budget v1.2 (Option A2)** — cell-author extending M_BUNDLE × V_CLEANUP grid to push past Frady-Sommer N/(4·log V) crossover into genuine noise regime — IS the empirical Donoho-Tanner probe on substrate
