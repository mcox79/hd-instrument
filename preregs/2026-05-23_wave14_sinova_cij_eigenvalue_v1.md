# Pre-registration: wave14_sinova_cij_eigenvalue_v1

**Date**: 2026-05-23
**Queue**: local_cpu_queue (pure CPU numpy; ~30-60 min FULL; all data generated in-script)
**Axis probed**: Substrate-physics -- Sinova C_ij extensive-eigenvalue RSB discriminator
**Trigger**: research_meta_map_and_adjacencies_2026-05-23.md Drill 1 (H1), P_deflated=0.50;
  cited as "cleanest finite-N RSB discriminator -- cleaner than Parisi P(q)";
  observability_suite_v1 RS-cert needed cross-family eigenvalue validation
**Script**: experiments/exp_wave14_sinova_cij_eigenvalue_v1.py
**Peak memory**: ~205 MB CPU (W=67 MB + C_avg_accum=134 MB + samples=4 MB per K at N=4096)
**Expected elapsed**: 30-60 min (5 K values x 5 seeds x 200 samples x 20-sweep intervals at N=4096)

---

## Scientific question

Does the substrate's C_ij covariance matrix (connected spin-spin correlator) have any
EXTENSIVE eigenvalues -- eigenvalues that scale with N -- or are all eigenvalues intensive
(lambda/N -> 0)?

In a spin glass / RSB system (Sinova, Houdayer, Martin PRL 82:1999):
  - RSB phase: a few eigenvalues are extensive (lambda_k / N stays finite at large N)
  - RS paramagnet: all eigenvalues intensive (lambda_k / N -> 0)

This is a cleaner finite-N discriminator than scalar Parisi P(q) because:
  1. No q-binning artifact (continuous eigenvalue spectrum)
  2. Counts are hard integers (not sensitive to histogram bin width)
  3. Subtracting W-inherited extensive count isolates PURE RSB signal

---

## Design

- **N**: 4096 (FULL); 256 (smoke)
- **K grid**: [50, 100, 200, 400, 800] (substrate operating regime; FULL)
  - alpha = K/N range: 0.012 to 0.195
  - Smoke: [10, 25]
- **beta**: 2.0 (same as observability_suite_v1; below T_c in substrate operating regime)
- **n_seeds**: 5 independent MC chains per K (FULL); 2 (smoke)
- **n_burn**: 100 Glauber sweeps per chain (FULL); 10 (smoke)
- **n_sample**: 200 configurations per chain (FULL); 20 (smoke)
- **sample_interval**: 20 sweeps between samples (FULL); 3 (smoke)
- **threshold_rel**: 0.1 (lambda/N > 0.1 = extensive)
- **Excess extensive count**: n_extensive(C_ij) - n_extensive(W)
  (subtracts W-encoded pattern eigenmodes from correlation signal)

---

## Falsifiable predictions

### Verdicts

- **SINOVA_RS_PARAMAGNET**: excess extensive eigvals == 0 at >= 2/3 of K points.
  Interpretation: purely intensive spectrum; substrate is RS at finite N.
  Consistent with cycle-122 4-anchor RS certification; confirms observability_suite_v1.

- **SINOVA_RSB_DETECTED**: excess extensive eigvals >= 2 at >= half of K points.
  Interpretation: substrate has hidden RSB not captured by scalar P(q).
  Would require re-examination of RS-cert anchors and Bet E conclusions.

- **SINOVA_INCONCLUSIVE**: excess == 1 at all K (boundary case) or noisy spectrum.
  Action: increase N or n_samples; or accept as uninformative for this protocol.

### Pre-registered expectation

Based on 4-anchor RS certification from observability_suite_v1 (cycle 122) and
Parisi P(q) sweep results (multiple FULL runs: PARISI_DISCRIMINATES_CODEBOOK,
RSB_CONFIRMED but finite-N only, binder declining with N):
  - P(SINOVA_RS_PARAMAGNET) = 0.55 (consistent with RS phase at operating K-grid)
  - P(SINOVA_RSB_DETECTED) = 0.25 (substrate may have RSB not visible in scalar P(q))
  - P(SINOVA_INCONCLUSIVE) = 0.20 (boundary excess==1 plateau at finite N=4096)

Calibration note: P_base was 0.80 (research_meta_map H1 row) before deflation.
Deflated by 0.30 for "never fired at FULL before" per feedback_lit_scan_calibration_penalty.

### Hard fail threshold

If n_extensive_C == 0 AND n_extensive_W == 0 across all K AND top scaled eigval < 0.05:
  substrate is deep paramagnetic (high-T phase); beta may be too high or W too dilute.
  Action: re-run at beta=4.0 or revisit alpha range.

---

## Substrate-product interpretation

- SINOVA_RS_PARAMAGNET: confirms observability_suite_v1 RS-cert; adds a second
  independent cross-family consistency anchor (Pattern 7 meta-pattern). Strengthens
  the "RS-phase-certified substrate" product narrative. No cap_map changes needed.

- SINOVA_RSB_DETECTED: contradicts current RS-cert; would require investigation of
  whether RSB is K-dependent (only at high K=800?). Could open new "hidden RSB
  operating regime" angle if localized to specific K range. Cap map impact: Bet E
  status and RS-cert row would require re-evaluation.

- Either outcome is decisive for the substrate-physics cross-family consistency record.

---

## PROT compliance

Not a cap_map closure; no PROT-004/006 required.
Substrate-physics characterization experiment (eigenvalue probe).
PROT-001 (exp_dev_decisions log entry) paired with this filing.
