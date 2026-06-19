# Exp-Dev shipped report -- cycle 58 (user: "do the next 5 high priority now")

**From:** Exp-Dev  **To:** Orchestrator  **Date:** 2026-06-04

## Shipped this turn (2, verified)
- **q_f5_oscillating_envelope_v2_n8192** (GPU/overnight, 21600s) -- existing unrun script; oscillatory
  phase-noise handoff. Remote --self-test passed.
- **kappa3_nlo_formula_validation_sigma_g_v1_n4096** (CPU, 14400s) -- kappa3_noise_robustness_nlo
  handoff Anchor 1; validates kappa_3^free/alpha-1 = 3*(exp(sg^2)-1)*alpha. SIGN FLAG: magnitude tracks
  the formula well (N=4096 diagnostic) but sign is NEGATIVE under my multiplicative-log-normal noise vs
  the formula's predicted increase -> Research should confirm the intended noise model/convention.

## Why only 2 (honest)
- Existing UNRUN substrate-physics scripts are EXHAUSTED -- I checked ~12 candidates (kappa3 sigma_g,
  capacity_phase, pp33 mfpt, pp49 depth-band, pp58 isochoric, activation_barrier, q_f5): all DONE
  except q_f5 v2 (shipped). The substrate-physics handoff backlog is largely COVERED by prior runs.
- CPU queue is FULL: remote_cpu pending=4 running=1 = 5 active (at the skip-if-pending>=5 threshold).
  Adding more CPU would breach the guard. GPU pending=1 running=1.
- Remaining genuinely-NEW items need fresh builds that carry a NOISE-MODEL-SPEC risk: my guessed models
  for PP-50 transition-zone (0 violations) and kappa3-NLO (sign flip) did not reproduce documented
  behavior. Burning compute on more guessed-model experiments is low-integrity.

## What unblocks more high-priority throughput
1. Research provides the EXACT noise/capacity/violation model for: PP-50 transition-zone (the
   "5/10-cells-violated" mechanism) and the kappa3-NLO noise convention (additive vs multiplicative; on
   W vs on patterns Xi; signed vs |deviation|). Then I rebuild both to reproduce documented behavior.
2. OR new research directions/handoffs with clear specs (the current substrate-physics backlog is thin
   -- mostly shipped).
3. The full CPU queue (NHSE Anchor 2, Q-B1, N-sweep, kappa3-NLO + 1) will drain over the next hours;
   verdicts then inform the Orchestrator's next priorities.

## Queue state
CPU: 5 active (full). GPU: 2 active (q_f5 v2 + 1 from prior). Healthy; not padded.

**END.** Recommend: provide the two noise-model specs above and I'll rebuild PP-50 + a sign-corrected
kappa3-NLO; otherwise the high-priority substrate-physics backlog is largely shipped.
