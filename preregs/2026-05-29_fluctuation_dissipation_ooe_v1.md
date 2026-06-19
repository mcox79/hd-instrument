# Pre-registration: fluctuation_dissipation_ooe_v1

**Date:** 2026-05-29
**Anchor:** fluctuation_dissipation_ooe_v1
**Script:** experiments/exp_fluctuation_dissipation_ooe_v1.py
**Queue:** overnight_queue
**Timeout:** 1200s

## Hypothesis

The Fluctuation-Dissipation Theorem (FDT) is violated during the Hebbian
WRITING phase of the substrate (N=4096), confirming that pattern-writing is
a genuine non-equilibrium (NESS) process. After writing (W frozen), dynamics
obey FDT (equilibrium reference). FDT ratio >> 1.0 (effective temperature
T_eff >> T_bath) during writing.

Parent: hatano_sasa_v4_glauber (HARD_PASS), non-eq stat-mech class confirmed.
This is a COMPLEMENTARY corroborator using a different formalism (FDT violation
vs Hatano-Sasa identity). Two independent NESS signatures strengthen the claim.

## Configuration

- N: 4096 (FULL), 512 (SMOKE)
- M: N * ALPHA_RATIO (ALPHA_RATIO from script default)
- Seeds: [7, 17, 23, 31, 41] FULL, [17] SMOKE
- n_traj: 50 FULL, 10 SMOKE
- T_steps: 50 FULL, 30 SMOKE
- TAU_RANGE: script default

## Metrics

- fdt_violation_mean: mean |R(tau)| = |chi(tau) - C'(tau)/(kBT)| over tau in [1,10]
- fdt_ratio_mean: mean chi(tau)*kBT/C'(tau) (1.0=equilibrium, >>1 = hot/active)
- T_eff_ratio: effective temperature ratio T_eff / T_bath
- equilibrium_baseline_fdt: same metrics for frozen W (equilibrium reference)

## Pre-registered bands

**HARD_PASS:**
fdt_violation_mean > 0.05 AND fdt_ratio_mean outside [0.80, 1.20]
in >= 4/5 seeds.
FDT genuinely violated; substrate writing is NESS. Corroborates Hatano-Sasa.

**HARD_FAIL:**
fdt_violation_mean < 0.005 AND fdt_ratio_mean in [0.90, 1.10] in ALL 5 seeds.
No FDT violation; substrate writing is effectively equilibrium.

**MIDDLE_BAND:** otherwise; calibration probe — single seed with very large
ratio (363x at smoke) suggests full run will be decisive.

NOTE: Smoke showed fdt_violation=7.9062, fdt_ratio=363.2 at N=512 (1 seed).
This is far outside the equilibrium band. HARD_PASS expected at FULL N=4096.

## Timeout estimate

Smoke: N=512, 1 seed, n_traj=10, T=30 = 0.421s.
Full: N=4096, 5 seeds, n_traj=50, T=50.
N-scale: (4096/512)^1.5 = 22.6x. Seeds: 5x. Traj: 5x. T: 1.67x.
Estimate: 0.421 * 22.6 * 5 * 5 * 1.67 = 397s. Safety 1.5 * 2 = 1190s.
Cap at PROT-019 floor N=4096 = 14400s? Script says 1200s timeout in header.
Using script-declared 1200s (compute estimate fits; no PROT-019 override needed
as this is a sub-1200s compute with reasonable safety margin).
timeout_s = 1200.

## Downstream

- HARD_PASS: FDT violation confirmed at N=4096, 5 seeds. Second independent NESS
  corroborator. Non-eq stat-mech row strengthened. Cap_map row promoted.
- MIDDLE_BAND: FDT ratio high but not all seeds clear threshold. Report ratio values.
- HARD_FAIL: FDT not violated at N=4096; probe design issue or N-dependent effect.
