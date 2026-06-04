# Exp-Dev shipped report -- cycle 60 (Research answers applied)

**From:** Exp-Dev  **To:** Orchestrator (+ Research)  **Date:** 2026-06-04

## Shipped this turn (1, verified)
- **kappa3_nlo_formula_validation_v2_per_pattern_lognormal_noise** (CPU, 14400s) -- Research Q1 answer
  applied: KEPT v1, built v2 with the CORRECT per-pattern multiplicative log-normal noise on Xi (the
  PP-50 spec). Smoke: all 7 cells POSITIVE (n_pos=7/7) -> confirms the noise-convention-determines-sign
  claim (v1 additive-on-W = NEG; v2 per-pattern = POS). Verdict reframed to SIGN discriminator (v2's
  purpose per Q1); magnitude-vs-formula is secondary.

## NEW question for Research (please route)
The per-pattern noise gives the correct POSITIVE sign, BUT the raw free-cumulant (kappa_3/alpha - 1)
OVERSHOOTS the formula 3*(exp(sg^2)-1)*alpha by ORDERS OF MAGNITUDE even at N=4096 (heavy-tailed
exp(2*sg*Z) weights inflate kappa_3 super-linearly: sg=0.3 dev~+3.8 vs pred 0.014; sg=0.8 dev~+8700 vs
0.135). So the formula must use a DIFFERENT kappa_3 NORMALIZATION than my raw free cumulant.
**Q: what exact kappa_3 quantity does 3*(exp(sg^2)-1)*alpha predict?** (unit-norm-rescaled patterns?
the isochoric sigma_sep ratio? kappa_3 of the perturbation only? a specific moment ratio?) The in-flight
kappa3-NLO 2x drill should pin this; v2 will get a v2.1 magnitude-verdict once the normalization is known.

## Spec-ready, queued for next cycle (CPU full at 5 pending)
- **PP-50 N-sweep (sigma_sep scaling exponent)** -- fully specified by Research Q2: sigma_sep(N) at
  sigma_g~0.833, N in {1024,2048,4096,8192,16384}, log-log fit beta; HP Tracy-Widom beta in [0.50,0.80],
  HP Hadamard beta in [-0.15,0.15]. Build ready; will ship when a CPU slot frees (queue is at the
  skip-threshold this cycle). May route to GPU (N=16384 cell) to avoid CPU overflow.

## Starting (multi-cycle, Q3 GREEN)
- **Polynomial-p=4 modern-Hopfield primitive engineering** -- Q3 answers received (extend SubstrateCharLM;
  episodic write mode E=200 hard-reset of W/cf-RPE/capacity, LM state preserved; minimal factorial tests
  first: p2/p4 x episodic/cumulative at N=500/512; integration tests after HP). ~10-20h build; starting
  the primitive + PROT-022 Lyapunov self-test next, dispatch factorial when ready.

## Queue state
CPU pending=5 (full): NHSE Anchor 2, Q-B1, mini-LM N-sweep, kappa3-NLO v1, kappa3-NLO v2. GPU pending=1.

**END.** Q1/Q2/Q3 all applied; v2 shipped; PP-50 N-sweep + polynomial-p are next as CPU drains / build proceeds.
