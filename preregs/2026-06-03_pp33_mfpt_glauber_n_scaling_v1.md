# Prereg: pp33_mfpt_glauber_n_scaling_v1_n4096_8192_16384

**Date:** 2026-06-03
**Anchor:** pp33_mfpt_glauber_n_scaling_v1_n4096_8192_16384
**Queue:** remote_cpu_queue (Glauber MCMC; pure CPU; N-scaling sweep ~2h wall)
**Source:** exp_dev_handoff_research_pp33_barrier_mfpt_probe_2026-06-03.md
           research_routing_v359_drill_battery_synthesis_2026-06-03.md Section 3 Exp 1

---

## Capability question

Does substrate MFPT scale as N^(1/3) (1-RSB phase per Aspelmeier-Bray-Moore 2004),
as N^1 (standard AGS RS), or N^0 (near-critical marginal)?

---

## N-suffix

No single _nN suffix. Multi-N sweep: N in {4096, 8192, 16384}. Production N_VALUES = [4096, 8192, 16384].
PROT-018 explicit exemption: "No single _nN suffix; multi-N sweep; N-scaling probe; all 3 N values
are load-bearing axes."

---

## Pre-registered threshold bands

**HARD-PASS (1-RSB N^(1/3) confirmed):**
- scaling exponent (from ln(tau) vs ln(N) regression) in [0.25, 0.45]
- R^2 for N^(1/3) fit (ln(tau) vs N^(1/3)) >= 0.95

**MIDDLE-BAND:**
- scaling exponent in (0.10, 0.70) -- between 1-RSB and AGS RS
- (includes AGS RS if exponent ~1.0 and R^2 > 0.90 -- product narrative intact)

**HARD-FAIL (near-critical, Exp C):**
- scaling exponent < 0.10 (tau N-independent)
- OR exponent > 0.70 (too steep; inconsistent with 1-RSB or AGS RS)

Strategic outcomes:
- HARD-PASS: PP-33 sub-property RE-OPENED with revised E_a closed-form
- MIDDLE (AGS RS): product narrative "predictable barriers" intact with different scaling
- HARD-FAIL: "predictable retention barriers" narrative weakened

---

## Formula self-tests (PROT-022)

1. N^(1/3) scaling ratio: (32768/4096)^(1/3) = 8^(1/3) = 2.0 within 1e-9
2. Glauber accept prob: h=1, T=2.0 -> 1/(1+exp(1.0)) = 0.26894 within 0.0001
3. M check: int(0.10 * 4096) = 409
4. Retrieval overlap > 0.5 at N=256, alpha=0.02, 1 seed

All verified in _instrumentation_selftest().

---

## Test design

- N_VALUES = [4096, 8192, 16384], alpha = 0.10, 5 seeds [7, 17, 23, 31, 41]
- Glauber dynamics at T = 2.0 (above critical temp for escape within reasonable steps)
- Escape criterion: max_overlap < 0.30 (softer than strict < 0.0 to avoid max_steps saturation)
- MAX_GLAUBER_STEPS = 5000 per trajectory (cap for wall-time tractability)
- N_TRAJECTORIES = 10 per (N, seed)
- Initial state: retrieved pattern with 5% noise
- Basin-escape criterion: max overlap with all stored patterns < 0.0

---

## Timeout estimate

N=4096 per seed: 2000 * 4096^2 = 3.36e10 flops. At 1e10 flops/s: ~3.4s/seed -> 17s for 5 seeds.
N=8192: 2000 * 8192^2 = 1.34e11 -> 13.4s/seed -> 67s.
N=16384: 2000 * 16384^2 = 5.37e11 -> 53.7s/seed -> 269s.
Total: 17 + 67 + 269 = 353s. But N_TRAJECTORIES=10 multiplies by 10 -> ~3530s.
With 2x margin: 7200s. Flag: long run > 7200s per contract.
timeout = 7200s.

NOTE: Glauber inner loop is vectorized (batch spin update not per-step sequential) so actual
wall time may be substantially less. 7200s is conservative.

---

## OOM check

W CPU float64: N=16384 -> 2.15 GB RAM. Remote machine 16+ GB. Fine.
N=8192: 0.54 GB. N=4096: 0.13 GB. No OOM risk at any N.

---

## Calibration notes

Prior PP-33: nf_crit proxy stuck at ~0.5 (N-independent boundary) -- proxy broken.
This is FIRST direct MFPT measurement for PP-33. No prior empirical MFPT anchor.
Bands set from 1-RSB theory (Aspelmeier-Bray-Moore 2004) and AGS RS expectations.
Per calibration-probe policy: no prior empirical anchor -> bands cover +-50% of prediction.
1-RSB exponent = 1/3 = 0.333; band [0.25, 0.45] = +-35% around prediction. Within +-50%.
HARD-FAIL at exponent < 0.10: this is > 3x below prediction. Appropriate.
