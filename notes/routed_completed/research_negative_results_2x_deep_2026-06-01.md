# Research: 2x deep on 2 negative results (percolation K=1 N-falsification + PP-11 Hadamard family rejection)

Date: 2026-06-01
Origin: user 2026-06-01 ~11:35 ET after verdict_processed HIGH at 11:27 reporting both negative results
Method: 2 parallel Sonnet drills (~3 min each); main-thread synthesis; per [[feedback-2x-means-depth]] + [[feedback-negative-results-2x-research]] + [[feedback-rehabilitation-after-rejection]]

## HEADLINE

Both negative results have RESCUE PATHS that are CHEAPER than the experiments that produced the negative finding. Top recommendations:

1. **Percolation K=1 N-falsification**: Likely a **multi-hop composition cliff at depth>=3**, NOT a per-hop substrate-physics failure. **Cheapest diagnostic**: K=1 single-hop depth-sweep (~18 CPU-min) discriminates per-hop vs composition origin.

2. **PP-11 Hadamard family rejection**: 5pp gap most likely **intrinsic second-order Hebbian cross-talk** in dense bipolar storage. **Cheapest diagnostic**: Kronecker-rotation-product cleanup codebook (~1 eng-week, audit-moat-low-risk) tests whether the gap is cleanup-driven (salvageable) vs pre-cleanup signal bias (fundamental).

Neither result closes a substrate program. Both narrow the rescue space substantively.

---

## DRILL 1: Percolation K=1 N-independence falsification

### What was falsified

K=1 retrieval signal at fixed alpha=M/N=16, depth=5:
- N=4096: signal ~ 6.7× random ✓ (matches percolation N-independence prediction)
- N=16384: signal **18× off** from prediction (collapsed substantially)

Percolation framework REJECTED at K=1 large N. M-axis phase boundary prediction (at M=2N→4N) still holds. K>=2 production unaffected.

### Theoretical framework scan + calibrated P estimates

| Framework | Predicts K=1 N-collapse at fixed alpha? | P (deflated) | Verdict |
|---|---|---|---|
| Statistical Neurodynamics (SNR-crosstalk) | Predicts N-INDEPENDENT or N-improving at fixed alpha → WRONG DIRECTION | 0.30 | Needs secondary "pattern correlation" mechanism to fit; speculative |
| **Finite-Size Scaling (FSS) near phase boundary** | Predicts power-law O ~ N^(-beta/nu); mean-field exponents give factor-16 collapse over factor-4 in N (close to observed 18×) | **0.38** | **Best-fit candidate but needs empirical exponent measurement** |
| Free Probability / RMT | Predicts N-improving behavior (Tracy-Widom edge O(N^(-2/3)) decreases) → WRONG DIRECTION | 0.12 | Skip |
| Belief-Propagation cavity method | Predicts N-improving for fixed-alpha < 1; at alpha=16 cycle corrections O(alpha/N) STILL decrease with N → WRONG DIRECTION | 0.18 | Skip |

### Most parsimonious explanation (no new framework required)

**Multi-hop composition cliff**: per-hop K=1 signal is N-independent (percolation right at depth=1); the depth=5 composition crosses a sharp reliability threshold that is N-dependent in (N, M, D) phase space. This is a *composed-function threshold effect*, not a per-hop substrate-physics effect.

This is the SINGLE CHEAPEST DISCRIMINATING TEST AVAILABLE.

### Sequencing recommendation (Drill 1)

**Test 1A (HIGHEST priority; ~18 CPU-min)**: K=1 at N=4096 and N=16384, depth ∈ {1, 2, 3, 5}, fixed alpha=16, 3 seeds each = 24 runs.
- HARD-PASS (composition cliff): signal at depth=1 N-independent (within 10%); divergence appears only at depth >= 3 → confirms percolation valid at per-hop, depth-composition is the new framework gap
- HARD-FAIL (per-hop physics IS N-dependent): signal at depth=1 already differs >20% → forces escalation to FSS power-law sweep

**Test 1B (CONTINGENT on 1A HARD-FAIL; ~100 GPU-min)**: K=1 at N ∈ {4096, 8192, 16384, 32768}, depth=5, alpha=16, 5 seeds. Plot log(signal) vs log(N). HARD-PASS: clean power-law R² > 0.99, exponent in [0.5, 3.0]. HARD-FAIL: flat (gamma<0.1) or non-power-law (R²<0.90).

**Skip**: RMT, BP cavity (both predict wrong direction).

---

## DRILL 2: PP-11 Hadamard-orthogonality family rejection

### What was falsified

4WC v1 BORDERLINE → 4WC v2 BORDERLINE (5-seed) → 4WC v3 Hadamard hop-id orthogonality EXACTLY at 2.0pp (FALSIFIED) → 4WC v4 compound Hadamard (both hop-id AND entity codewords Hadamard) **WORSE than v3**.

Conclusion: Hadamard-orthogonality family **REJECTED**. 5pp gap NOT caused by cross-correlation among hop-id codewords.

### Root cause hypothesis (best single explanation)

**Hypothesis A — Second-order Hebbian cross-talk (most likely)**: In dense bipolar outer-product storage, structured queries (built from factor sub-vectors) share algebraic structure with other stored keys. Cross-talk is in the *weight matrix capacity statistics*, not in codebook angular separation. **No codebook rotation within dense bipolar can fix this** because the bias is pre-cleanup. v4 being worse than v3 is consistent: simultaneously orthogonalizing BOTH factor codebooks concentrates the product spectrum, amplifying second-order cross-terms.

Secondary contributors:
- **Hypothesis B — Spectral concentration under structured binding**: Hadamard rows live in low-rank structured subspace; reduces effective dimensionality
- **Hypothesis C — Depth-cumulative noise**: amplifies whatever per-hop gap exists; not the cause but contributes to deep-chain economics

### Rescue candidates + calibrated P estimates

| Rescue | Mechanism | Audit-Moat Risk | P (close to <2pp) | Eng-weeks |
|---|---|---|---|---|
| **R2.1 Kronecker rotation product cleanup** | Improve codebook-lookup decision boundary; encoding unchanged | VERY LOW (encoding identical) | **0.25** | **1** |
| **R2.2 Sparse Block Codes (DSBC/BCF)** | Replace dense interference with sparse block structure; published 99% factorization in clean settings | MODERATE-LOW (BCF supports exact unbinding via l-infinity) | **0.45** | 2-3 |
| **R2.3 Path-dependent chain-level keys** | Chain-context vector replaces hop-by-hop binding; breaks algebraic relationship between intra-chain keys | MODERATE (audit API changes shape — chain-level vs hop-level) | 0.55 | 2 |
| **R2.4 Acceptance + re-positioning** | Promote PP-9 depth-conditional caveat to first-class product boundary; "substrate audit + LLM amortization for deep chains" | NONE | 1.0 executable | 0-2 (docs only) |
| (R2.5 GHRR non-commutative phase) | Already queued in PP-11 ladder | LIKELY HIGH (FHRR precedent 85-92% audit) | 0.20-0.35 | 1-2 |

### Sequencing recommendation (Drill 2)

**Test 2A (HIGHEST priority; 1 eng-week)**: R2.1 Kronecker rotation product cleanup. CHEAPEST + DIAGNOSTIC at root-cause level.
- HARD-PASS: gap <2pp on 5/5 seeds at N=4096 + audit accuracy ≥95% → cleanup is load-bearing; superficial fix viable
- HARD-FAIL: gap ≥4pp or audit <95% → confirms pre-cleanup bias (Hypothesis A dominant); de-risks choice between R2.2 and R2.4 by ruling out cheap fix

**Test 2B (CONTINGENT on 2A HARD-FAIL; 2-3 eng-weeks)**: R2.2 Sparse Block Codes (DSBC/BCF). Most principled attack on root cause.

**Test 2C (CONTINGENT on 2B also HARD-FAIL or too expensive; 0-2 eng-weeks doc-only)**: R2.4 Acceptance + re-positioning. After two failed rescues, Bayesian update toward "fundamental dense-bipolar capacity limit"; P(remaining technical fix works) < 0.25.

**Defer**: R2.3 path-dependent keys (higher engineering risk + audit API surface disruption). R2.5 GHRR (audit-moat-veto-likely; superseded by R2.2's better-audit-profile precedent).

### Diagnostic observable to track across ALL smoke tests

Split accuracy into three conditions at single hop:
- (a) random keys
- (b) structured keys with random factor codebooks
- (c) structured keys with orthogonal factor codebooks

If (b) ≈ (c), codebook-level fixes are unlikely (consistent with v3/v4 evidence). If (c) > (b), some codebook-level fix remains possible.

---

## COMBINED PRIORITY DISPATCH PLAN

Two cheap diagnostic tests; both could ship in parallel (no resource contention):

1. **Test 1A (percolation depth-sweep, ~18 CPU-min)** — discriminates whether K=1 large-N collapse is per-hop physics or multi-hop composition cliff
2. **Test 2A (Kronecker cleanup, ~1 eng-week)** — discriminates whether PP-11 5pp gap is cleanup-driven or pre-cleanup signal bias

Both tests have HIGH information gain per cost. Either outcome (PASS or FAIL) substantively narrows the rescue space and informs the next experimental cycle.

## Method notes

- Per [[feedback-2x-means-depth]]: drills went DEEP on the existing findings (theoretical frameworks + rescue candidates), NOT verification re-runs of the falsified hypotheses
- Per [[feedback-no-padding-experiments]]: synthesis produces 2 dispatchable tests + sequenced contingents; not 5-7 marginal variants
- Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated; cap on novel-synthesis P at 0.50 applied
- Per [[feedback-rehabilitation-after-rejection]]: 3-5 axis-combination rescues per drill listed before any closure recommendation
- Per [[feedback-rescue-sketch-first-sequencing]]: cheapest/diagnostic tests sequenced first
- Per [[feedback-query-privacy-decomposition]]: Sonnet drill prompts used generic VSA terms, no project-identifying fingerprints

## What I'll route to orchestrator

Single consolidated `strategy_request_to_strategy_negative_results_followon_experiments_2026-06-01.md` proposing:
- Test 1A (depth-sweep) for immediate CPU dispatch
- Test 2A (Kronecker cleanup) for testbed engineering pickup
- Test 1B + 2B + 2C as pre-specified contingent escalations


---

Acted-on 2026-06-01: 2x-deep negative results adopted in cap_map v311 v312; P3 percolation N-independence refutation + free-probability framework refutation


Acted-on 2026-06-01: 2x-deep negative results adopted in v311 v312; P3 percolation + free-prob framework refutations
