# ROUTING -- Redirect depth-ladder to capacity stress test (PP-12/Q-A3 family)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Substrate-physics experiment design redirect

---

## Capability question

At fixed N, does substrate cross-layer composition fidelity remain EXACT-1.0000 as stored pattern count M approaches the Hopfield capacity bound alpha_c, OR does fidelity degrade at the algebraic capacity boundary M ~ alpha_c * N?

## Why this redirect

Substrate composition has now been measured at L=200, L=300, L=700, and L=2000+ levels -- all returning EXACT-1.0000 across all seeds. Per algebraic analysis:

**Substrate's bipolar+sign-rounded composition has NO precision-drift mechanism.** Each retrieval step snaps to bipolar via sign(W @ x), removing floating-point noise at every layer. Float32 absolute precision at N=16384 is ~1e-3; signal magnitude is ~sqrt(N)=128; noise-to-signal ratio ~1e-5. Five orders of magnitude below the sign threshold. No accumulating-error pathway exists.

**Theoretical depth limits we know exist:**
- Classical Hopfield capacity: M/N < alpha_c = 0.138; at N=16384 this is M < 2260
- Modern Hopfield: exponential capacity, essentially unbounded
- Compute/wall: practical (linear scaling)

**At L=2000+ with M ~ 0 (negligible storage pressure), no algebraic mechanism predicts failure.** We're confirming a known algebraic property at increasing depth. Further depth tests are not informative beyond establishing the empirical anchor.

**Where the algebra DOES bend:** at capacity boundary M ~ alpha_c * N. This is the unmeasured regime; the algebraically interesting one.

## Proposed redirect

Instead of continuing the depth ladder (L=3000, L=5000, L=10000), redirect to **capacity-stress test**: sweep M near alpha_c at fixed moderate L. This is where substrate composition algebra would actually start to fail.

### Cells

Anchor name: `substrate_capacity_stress_composition_v1_n16384`

- N = 16384 fixed
- M sweep: M / N in {0.03, 0.06, 0.09, 0.12, 0.15, 0.18, 0.21} (range 500-3500 stored patterns; spans below + at + above classical alpha_c = 0.138)
- L = 50 (moderate composition depth; keeps wall reasonable; well-within current proven range)
- 5 seeds per cell
- 7 cells total = 35 measurements

### Measurement protocol

For each (M, L) cell:
1. Build substrate with M random bipolar patterns stored via outer-product Hopfield write
2. Apply L composition operations (same protocol as PP-12/Q-A3)
3. Measure per-layer fidelity (cosine vs theoretical expected)
4. Aggregate: mean fidelity across L levels per seed; per-seed pass/fail at fidelity = 1.0000

### Wall estimate

Per-cell wall scales with M (Hopfield write) + L (composition). At M=3500 stored + L=50 levels, expect ~30-90s per seed at N=16384. Total: 7 cells x 5 seeds x ~60s = ~35 min. Cost $0 (CPU or GPU; substrate-physics existing infrastructure).

## Pre-reg HP/MID/HF bands

**HARD-PASS (capacity boundary detected):**
- Fidelity = 1.0000 EXACT at M/N <= 0.12 (below alpha_c)
- Fidelity degrades monotonically at M/N >= 0.15 (at + above alpha_c)
- Boundary visible in 5-cell range (M/N from 0.09 to 0.21)
- 5/5 seeds consistent

**MIDDLE (capacity boundary unclear):**
- Fidelity degrades but at M/N significantly different from alpha_c = 0.138 (e.g., at M/N = 0.05 OR M/N = 0.25)
- OR partial degradation; 3/5 seeds consistent

**HARD-FAIL (no capacity boundary observed in this range):**
- Fidelity = 1.0000 EXACT at ALL M/N including M/N = 0.21 (above classical alpha_c)
- Would suggest:
  - Substrate is in modern-Hopfield regime (exponential capacity); classical alpha_c doesn't apply OR
  - Test is not actually loading the substrate sufficiently (composition uses dedicated structure, not shared with stored M)
  - Either way, informative about substrate's algebraic class

## P_deflated

- Capacity boundary detected at M/N ~ 0.138 (classical alpha_c): 0.35 (substrate is likely closer to modern-Hopfield regime per Krotov-Hopfield 2016; alpha_c may be much higher)
- Capacity boundary detected at higher M/N (modern-Hopfield regime, alpha_c >> 0.138): 0.45
- No boundary detected up to M/N = 0.21: 0.20 (would refute classical-Hopfield-class identification; further M push needed)

Lit-scan calibration penalty applied (0.15-0.25); cap novel-synthesis at 0.50.

## What this is NOT

- NOT a refutation of the depth-ladder results. L=2000+ at M~0 IS algebraically expected and empirically confirmed.
- NOT a redesign of the substrate. The substrate is unchanged.
- NOT a request to re-run failed depth tests.

It IS a redirect of further effort to the INFORMATIVE regime (capacity boundary) rather than the already-confirmed regime (depth scaling under negligible storage pressure).

## What to STOP

Per user direction: stop running deeper depth tests (L=3000, L=5000, L=10000) on PP-12/Q-A3 family. They confirm algebraic prediction without adding capability evidence. The point is made at L=200+ with band collapsed to 0.97 point estimate. Additional depth-ladder runs are not informative.

If product narrative needs an even-deeper anchor for marketing/demo reasons, ONE single run at L=10000 would suffice (rather than continuing the ladder). Cap_map already has 12 consecutive lifts on this row.

## Strategic implication

Cap_map should add a NEW PP-12/Q-A3 sub-property founding under "capacity stress" once this test lands:

- "Substrate composition fidelity remains EXACT-1.0000 below M/N = X; degrades at M/N > X" -- with X measured empirically
- This sets the BOUNDARY of the audit-API composition moat; previously unmeasured
- Substantively new evidence for the product capability claim ("composition holds up to capacity boundary at alpha_c * N stored patterns")

If alpha_c turns out high (modern-Hopfield class confirmed), the moat is structurally larger than classical-Hopfield literature predicts.

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: capacity stress test is the genuinely-informative next experiment; depth-ladder is now padding
- Per [[feedback-keep-research-exploratory-not-narrowing]]: explores the unmeasured capacity-boundary dimension rather than re-confirming depth
- Per [[feedback-2x-means-depth]]: this is genuine depth (capacity boundary) not re-verification
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF bands tied to classical alpha_c prediction
- ASCII-only output enforced

PROT-018: anchor name `substrate_capacity_stress_composition_v1_n16384` with _n16384 suffix
PROT-021: source=remote substrate runner, run_mode=full, n_seeds=5

---

**END.**

**Exp-Dev:** redirect PP-12/Q-A3 depth-ladder dispatch effort to capacity-stress test. Estimate engineering ~2-3h (M-sweep parameter + capacity-tracking instrumentation; reuses existing PP-12/Q-A3 composition infrastructure). Experiment wall ~35 min. Cost $0.

**Orchestrator:** informed. Cap_map sub-property founding pending verdict.

**Research session:** holds for capacity-stress verdict; will synthesize capability-implication update afterward.
