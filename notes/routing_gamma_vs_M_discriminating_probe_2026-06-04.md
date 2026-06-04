# ROUTING — γ-vs-M discriminating probe (SCS vs RSB vs Lyapunov)

**From:** Research session
**To:** Orchestrator (primary), Testbed (engineering if needed)
**Date:** 2026-06-04
**Status:** USER AUTHORIZED 2026-06-04 ($0 CPU; ~2-4h wall; orchestrator dispatches).

---

## What this is (plain language)

Empirical probe to discriminate which of three top-ranked spectral-gap theories correctly predicts substrate's observed γ ≈ 8.0. The 2x drill identified SCS + non-Hermitian BBP (P=0.38) as top candidate, with Lyapunov amplification (P=0.28) and 1-RSB (P=0.25) as co-predictors. Each framework predicts a DIFFERENT γ(M) scaling behavior at fixed N. Plot γ vs M at two N values; identify which framework fits.

This experiment empirically confirms (or refutes) the SCS framework as the theoretical foundation for substrate's spectral-gap drift-detection capability.

---

## Test design

**Anchor name:** `substrate_spectral_gap_gamma_vs_M_scaling_v1_n4096_n16384`

**Resource:** local CPU (substrate-physics class; existing isochoric κ_3 separation protocol can be reused per-cell)
**Wall:** ~2-4 hours
**Cost:** $0

### Cells

For each N ∈ {4096, 16384}:
- M-sweep: M / N ∈ {0.05, 0.075, 0.10, 0.125, 0.15} (5 cells per N, spanning α = 0.05 to 0.15)
- For N=4096: M ∈ {205, 307, 410, 512, 614}
- For N=16384: M ∈ {819, 1229, 1638, 2048, 2458}
- 5 seeds per cell
- Per cell: measure γ_emp via existing isochoric κ_3 separation protocol (the protocol that gave ratio=8.00 at the PP-58 reference cell)

Total: 10 cells × 5 seeds = 50 measurements. Per-cell wall ~15-25 min on CPU.

### Auxiliary measurement (HARD-FAIL-universal check)

For each (N, M) cell, additionally record:
- τ_estimate from sample asymmetry: τ = ||W_sym|| / ||W_total||
- d_estimate from leading SVD: d = σ_1(W) / mean(σ_bulk(W))

Allows post-hoc verification that the empirical γ matches the SCS formula γ = (d + τ/d) / (1+τ) when τ and d are independently measured.

---

## Pre-registered framework predictions

**SCS framework prediction:**
- γ(M) ~ (√(M/N) + τ/√(M/N)) / (1+τ)
- Sub-linear saturation in M (square-root growth at low M; saturation near critical α)
- Ratio γ(M = 0.05·N) / γ(M = 0.10·N) ≈ 0.71 (theoretical √(0.05/0.10) under SCS)
- Ratio γ(M = 0.05·N) / γ(M = 0.15·N) > 0.50

**1-RSB framework prediction:**
- γ diverges near capacity α_c via 1/(1-q_EA(M)) pole
- Sharp rise + divergence as M approaches critical
- Ratio γ(M = 0.05·N) / γ(M = 0.15·N) < 0.30 (sharp pole-driven growth)

**Lyapunov-only framework prediction:**
- γ approximately flat vs M (purely time-protocol-dependent, not M-dependent)
- Ratio γ(M = 0.05·N) / γ(M = 0.15·N) ≈ 1.0

**HARD-FAIL universal (refutes all six):**
- γ scales as N^α with α > 0 across the two N values
- No thermodynamic-limit framework predicts O(N) gap growth
- Would refute the entire spectral-gap-as-substrate-capability claim

---

## Pre-registered HP / MID / HF bands

**HARD-PASS (SCS confirmed):**
- γ-vs-M is monotone increasing AND sub-linear (saturating) at both N
- Ratio γ(M = 0.05·N) / γ(M = 0.15·N) in [0.50, 0.75] at both N
- τ_estimate ≈ 0.05-0.15 across cells (near-Ginibre confirmed)
- SCS formula prediction matches empirical γ within 30% at 3+ cells per N

**MIDDLE (uncertain / mixed):**
- γ-vs-M monotone but ratio outside [0.50, 0.75] at one N
- OR SCS formula prediction matches at 1-2 cells per N (rather than 3+)
- OR τ_estimate doesn't fall in near-Ginibre range
- Triggers framework re-examination — RSB or Lyapunov alternatives become more weighted

**HARD-FAIL (SCS refuted):**
- Ratio γ(M = 0.05·N) / γ(M = 0.15·N) < 0.30 at either N → RSB-consistent
- OR γ approximately flat vs M (ratio ≈ 1.0) → Lyapunov-only
- OR γ scales as N^α with α > 0 → universal refutation of thermodynamic-limit frameworks

---

## Strategic outcomes

### If HARD-PASS SCS

- PP-58 sub-property founding upgrades from "SCS-predicted" to "SCS-CONFIRMED"
- Drift-detection killer feature claim becomes algebraically guaranteed + empirically validated
- Lit anchors locked: SCS 1988 + Bun-Bouchaud-Potters 2016 + Ginibre 1965
- Cross-domain confirmation chain: substrate spectral gap ↔ SCS ellipse ↔ financial-RMT cleaning
- Capability claim strengthens to flagship-class

### If MIDDLE

- Run discriminating cells (e.g., near-α_c probe to test RSB divergence)
- Cost: ~1h CPU, $0
- Likely resolution within a single follow-up cycle

### If HARD-FAIL (SCS refuted, RSB confirmed)

- Major theory finding: substrate is genuinely in 1-RSB regime
- 1-RSB at q_EA ≈ 0.78 → connects to first-order multi-basin row (per `project_pred4_hysteresis_first_order_confirmed_2026-05-27`)
- Drift-detection capability claim still holds (γ ≈ 8 empirically) but theoretical foundation is RSB not SCS
- Strengthens spin-glass-class identification for substrate

### If HARD-FAIL (universal refutation)

- All thermodynamic-limit frameworks refuted
- Spectral-gap-as-substrate-capability claim weakens substantially
- Substrate has spectral separation but no clean theoretical foundation
- Forces re-examination of the underlying ensemble class

---

## Existing-protocol reuse

The isochoric κ_3 separation protocol that produced PP-58 ratio=8.00 already exists. This experiment reuses it across 10 (N, M) cells. Engineering effort is minimal — wrapper script for the M-sweep + auxiliary τ/d measurement; reuses existing primitives.

Estimated engineering: 1-2h if scratch; less if reusing existing PP-58 isochoric script with parameterization.

---

## Discipline declarations

- Per `feedback_routings_address_orchestrator_not_testbed`: orchestrator is primary addressee
- Per `feedback_plain_language_experiment_tracking`: experiment described by what it tests
- Per `feedback_no_padding_experiments`: each (N, M) cell discriminates framework predictions
- Per `feedback_no_smoke_preframing_in_task_prompts`: HP/MID/HF bands tied to drill predictions
- Per `feedback_envelope_expansion_fail_bands`: HF bands pre-registered including universal-refutation case
- Per `feedback_testbed_progress_logging_and_restart`: per-cell partial JSON
- PROT-018: anchor name uses _n4096_n16384 multi-N suffix
- PROT-021: source=remote run_mode=full n_seeds=5

---

**END.**

**Orchestrator:** dispatch when CPU bandwidth allows. Engineering scope minimal (existing isochoric κ_3 script + parameterization). Surface verdict + framework-fit classification per drill predictions.

**Research session:** holds for verdict; ships capability-implication update to cap_map per outcome.
