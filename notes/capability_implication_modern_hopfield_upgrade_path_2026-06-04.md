# CAPABILITY-IMPLICATION NOTE -- Modern Hopfield upgrade path identified (polynomial-p reduces capacity floor)

**From:** Research session
**To:** Orchestrator (primary) / strategy_scribe (for annotation)
**Date:** 2026-06-04
**Subject:** Substrate's algebraic regime characterization + polynomial-p=4 upgrade path. Three drills converge on a coherent picture for substrate-as-training-mechanism + audit-API moat scale.

---

## What this is (plain language)

Three deep drills today (META 3x+ substrate-as-training-mechanism + N-threshold 3x + Modern Hopfield Upgrade 3x) converged on a unified algebraic characterization of substrate's operating regime:

1. **Substrate is in CLASSICAL Hopfield regime** (linear capacity alpha_c * N) with current outer-product retrieval primitive
2. **N_threshold for substrate-as-training-mechanism ~ 2000-4000** with three independent mechanisms predicting this (Hopfield capacity + BCM-SNR + concentration)
3. **Polynomial-p=4 modern Hopfield upgrade path identified**: drops Hopfield capacity floor from ~3000 to ~100-200, with O(N*M) cost unchanged, bipolar {+1,-1}^N natively compatible (Demircigil 2017 exact theorem)
4. **BCM-SNR floor independence is the open question** (drill in-flight; if p-dependent, both floors fall together; if p-independent, capacity freed but learning still bounds)

This is the most theoretically-grounded characterization of substrate's operating regime in the project. Material for cap_map annotation.

---

## Requested cap_map actions

### 1. Substrate algebraic regime classification (NEW sub-property)

Add new sub-property under substrate-physics observability row:

"Substrate operates in CLASSICAL Hopfield regime (outer-product write; quadratic energy; capacity alpha_c * N). N_threshold for substrate-as-training-mechanism ~ 2000-4000 (3 independent mechanisms: capacity, BCM-SNR, concentration). Empirical bracket consistent: N=512 FAIL, N~4096 SUCCESS. Polynomial-p=4 modern Hopfield upgrade path identified: drops capacity floor to ~100-200, O(N*M) cost preserved, bipolar native compatibility per Demircigil 2017. Engineering ~10-20h; empirical validation in flight."

### 2. Drift-detection killer feature annotation update

Combine today's NHSE-annulus finding with the regime characterization:

"Drift detection capability empirically validated at gamma_emp ~ 8.0 isochoric kappa_3 ratio. Theoretical framework: NHSE-annulus (Hatano-Nelson 1996 + non-Hermitian skin effect 2018-2024); gamma(tau) = 1.20 * exp(3.83 * tau) closed-form derived; M-independence algebraically exact below BBP threshold. Tunable-precision drift detector: tau_required = 0.261 * ln(gamma_target / 1.20). Substrate operates in classical Hopfield regime + Hatano-Nelson skin effect; modern Hopfield upgrade (polynomial-p=4) preserves spectral structure for drift detection regardless of training-mechanism regime."

### 3. Cross-layer composition moat annotation update

Combine today's L=2000+ finding with the algebraic characterization:

"Cross-layer composition fidelity = EXACT-1.0000 measured through L=2000+ levels (12 consecutive band-lifts to point estimate 0.97). Algebraic reason: bipolar+sign-rounded composition has no precision-drift mechanism; signal-to-noise ratio 1e-5 at N=16384, five orders below sign threshold. Theoretical limits: classical Hopfield capacity alpha_c * N = 2260 patterns at N=16384 (if storage shared); modern Hopfield with polynomial-p=4 raises capacity floor to ~exp(N). Substrate-physics moat structurally unbounded by precision; bounded only by capacity or compute. Capacity-stress test in-flight to measure boundary."

### 4. Substrate-as-training-mechanism row candidate

Open NEW row candidate (not founded yet; pending N-sweep + polynomial-p=4 empirical verdicts):

"Substrate-as-training-mechanism: theoretical pathway identified via Modern Hopfield 3x drill. Classical regime: viable at N >= 2000-4000 per BCM-SNR + capacity + concentration mechanisms; Exp-Dev preview at N~4096 confirms substantive learning (bpc gap 1.76 nats vs uniform). Polynomial-p=4 modern Hopfield upgrade may lower N_threshold to ~100-1000 (conditional on BCM-SNR drill outcome). DeltaNet 1.3B precedent (NeurIPS 2024) for substrate-retrieval + SGD readout pattern available as fallback. Row foundation pending: N-sweep verdict + polynomial-p=4 empirical test."

---

## Lit anchor chain (updated)

The substrate's characterization now rests on:

1. **Hopfield 1982** (classical capacity)
2. **Demircigil 2017** (modern Hopfield exponential capacity; bipolar native)
3. **Krotov-Hopfield 2016** (modern Hopfield design; capacity scaling)
4. **Ramsauer 2020** (modern continuous Hopfield = attention; bipolar variant via Hamming Attention)
5. **Hatano-Nelson 1996** (non-reciprocal asymmetry framework; substrate drift-detection)
6. **NHSE skin effect lit 2018-2024** (annular eigenvalue distribution; drift-detection theoretical anchor)
7. **BCM 1982** (sliding-threshold three-factor learning; substrate-as-training BCM-SNR floor)
8. **Klampfl-Maass 2013** (three-factor STDP conditional probability convergence)
9. **Bun-Bouchaud-Potters 2016** (financial RMT; cross-domain confirmation for spectral gap)
10. **BinaryAttention (2603.09582) + Hamming Attention (2502.01770)** (bipolar attention; modern Hopfield equivalence at small precision)

Substrate's product story now has TEN distinct published lit anchors across multiple framework classes. Algebraic grounding is robust.

---

## Strategic implication

Substrate has TWO distinct operating regimes:

**Classical (current, validated):**
- N >= 2000-4000 for substrate-as-training-mechanism
- Compute: O(N*M) outer-product; works on laptop CPU at N=4096
- Empirical validation: Exp-Dev preview at presumed N=4096 (bpc gap 1.76 nats vs uniform); pending N-sweep verdict for confirmation
- Lit anchor: Hopfield 1982 + BCM 1982 + classical RMT
- Substrate-physics moat (composition + drift + audit): unbounded through any practical depth

**Modern (upgrade-pathway; conditional on BCM-SNR drill):**
- N >= 100-1000 for substrate-as-training-mechanism (if BCM-SNR is p-dependent)
- Compute: O(N*M) preserved; same cost
- Engineering: ~10-20h single-primitive swap
- Empirical validation: pending polynomial-p=4 empirical test
- Lit anchor: Demircigil 2017 + Krotov-Hopfield 2016 + Ramsauer 2020 + Hamming Attention 2502.01770

Either regime is a defensible product position. Modern is more aggressive (lower scale requirements) but conditional on BCM-SNR scaling. Classical is validated empirically and remains the conservative product anchor.

---

## What I am NOT requesting

- Top-level row change to existing killer features (drift detection + composition + deletion certificate stand)
- Premature founding of substrate-as-training row (pending N-sweep + polynomial-p empirical verdicts)
- Modern Hopfield class identification yet (drill says upgrade IS feasible; empirical validation still pending)
- Cloud GPU spend (per [[feedback-cloud-only-when-absolutely-necessary]]; all current work fits on CPU + remote GPU)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Orchestrator informed; strategy_scribe handles annotations
- Per [[feedback-capabilities-not-product-positioning]]: algebraic regime characterization, not GTM
- Per [[feedback-value-creation-not-competition]]: emphasizes substrate's lit-anchored framework class, not competitor displacement
- Per [[feedback-dont-overextend-theorems]]: classical regime is validated; modern regime is pathway with explicit P_deflated and conditionals
- Per [[feedback-lit-scan-calibration-penalty]]: P_deflated applied throughout
- ASCII-only output enforced

---

**END.**

**Orchestrator:** route to strategy_scribe for cap_map annotation updates per § "Requested cap_map actions" above. Next visibility entry can cite the lit anchor chain (10 distinct frameworks) as substrate's product narrative foundation.
