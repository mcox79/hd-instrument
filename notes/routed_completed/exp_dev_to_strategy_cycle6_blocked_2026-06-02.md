# exp_dev cycle 6 -- 3 blocked anchors (to Strategy for redesign)

## 1. substrate_spectral_health_check_v1 -- INSTRUMENTATION_SUSPECT

**Block reason**: Z-score formula mismatched to Hopfield W eigenspectrum.
The Marchenko-Pastur upper edge E_MP = (1+sqrt(alpha))^2 is derived for the
unrestricted Wishart matrix. The Hopfield W = Xi^T Xi / N WITH diagonal removal
has a DIFFERENT eigenspectrum. At alpha=0.05, the actual lambda_max << E_MP,
giving Z << -3 even for the null case (no anomaly).

**Redesign needed**: measure E_lambda_max empirically at alpha_null via bootstrapping
100 W matrices; use that empirical E[lambda_max] and std[lambda_max] as the normalization.
The Z-score then measures deviation from the EMPIRICAL distribution, not the
theoretical MP formula. This produces a valid TW-class test even for diagonal-removed W.

**Cap_map impact**: spectral health monitoring row -- Z-score formulation needs fix.

---

## 2. tau_mem_m_sweep_v1 -- INSTRUMENTATION DESIGN FAULT

**Block reason**: T_MAX=500 (smoke) / T_MAX=2000 (full) are << tau_theory = 3954 steps.
The experiment measures the half-life t_{1/2} where overlap drops to m_0/2.
If t_{1/2} > T_MAX, the measurement returns T_MAX (saturated at boundary).
rel_err_M1 = 0.999 confirms: tau never reached T_MAX/2 = 250 << tau_theory=3954.

**Redesign needed**:
- Either T_MAX >> tau_theory (needs T_MAX ~ 10*4000 = 40000 -- impractical at N=1024)
- Or measure the DECAY RATE instead of half-life: fit m(t) ~ m_0*exp(-t/tau) at early times.
  The early-time slope gives 1/tau without needing t >> tau.
- Alternative: use a weaker gamma (gamma=0.01 instead of 0.001) to get tau_theory ~ 395.
  Then T_MAX=2000 is adequate.

**Revised parameters**: gamma=0.01, lambda=0.01, tau_theory ~ 395. T_MAX=2000 sufficient.

---

## 3. multiagent_emergence_v1 -- HARD_FAIL smoke (design fault, not instrumentation)

**Block reason**: cos_joint=0.484 < HP=0.70. Cell A fails, Cell C (improvement) fails.
Root cause: LAMBDA_SHARED=0.5 dilutes the shared component.
With N_AGENTS=8 agents each writing LAMBDA_SHARED*xi_shared + (1-LAMBDA_SHARED)*noise,
the shared component accumulates N_AGENTS * LAMBDA_SHARED = 4.0 total weight.
The noise accumulates N_AGENTS * M_PER_AGENT * (1-LAMBDA_SHARED) = 8*5*0.5 = 20 noise patterns.
SNR = 4.0 / sqrt(20) ~ 0.89 -- below retrieval threshold.

**Redesign**: increase LAMBDA_SHARED to 0.8 (noise weight = 0.2 per write).
Then SNR = 4.0 / sqrt(8) ~ 1.4 at N=1024. Or reduce M_PER_AGENT to 2.
Also: cell C improvement metric was negative because joint adds MORE noise from extra agents
than signal from the shared component at LAMBDA_SHARED=0.5. At 0.8, joint should beat single.

**Fix**: experiment/exp_multiagent_emergence_v2.py with LAMBDA_SHARED=0.8, M_PER_AGENT=3.

---

Acted-on 2026-06-02: cycle 6 blocked items rolled into Wave 1+2 redesigns
