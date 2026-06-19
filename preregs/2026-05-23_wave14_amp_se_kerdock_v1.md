# Pre-registration: wave14_amp_se_kerdock_v1

**Date**: 2026-05-23
**Queue**: local_cpu_queue (pure CPU numpy/numpy-linalg; ~30 min at N=4096)
**Axis probed**: AMP state-evolution vs empirical AMP on substrate's exact Kerdock codebook
**Trigger**: research_meta_map_and_adjacencies_2026-05-23.md Drill 4 (B4+F5); P_deflated=0.45
**Script**: experiments/exp_wave14_amp_se_kerdock_v1.py
**Peak memory**: ~700 MB CPU (N=4096 M=32768=8N matrix at alpha=8; numpy SVD)
**Expected elapsed**: ~25-35 min CPU

---

## Scientific question

No published RS theory predicts substrate's M/N=8 at N=4096 capacity; the four
lit-scan sub-agents spanning 2026-05-21 to 2026-05-22 produced predictions spanning
4 orders of magnitude. AMP state-evolution gives EXACT finite-N predictions IF the
Kerdock codebook satisfies the AMP matrix-class assumption (Bayati-Montanari 2011:
right-rotationally-invariant matrices). This is an open question for Kerdock codes.

The experiment computes the AMP SE recursion using the EMPIRICAL eigenspectrum of
(1/N)*A^T*A (Kerdock submatrix at each alpha) and compares the SE fixed-point MSE
to empirical AMP iteration on the actual matrix. Agreement = universality class
membership. Disagreement = Kerdock's algebraic structure (Walsh/Maiorana-McFarland)
lies outside the AMP universality class.

---

## Design

- **N**: 4096 (substrate's primary test dimension; even log2 = 12, satisfies MM construction)
- **M/N alpha grid**: [0.5, 1.0, 2.0, 4.0, 8.0] (spanning from under-determined to substrate's capacity regime)
- **Seeds**: 5 per alpha (independent random subsamples of codebook rows)
- **Signal prior**: isotropic Gaussian N(0, 1.0) (matched MMSE denoiser)
- **Observation noise**: sigma=0.1 (SNR ~100; diagnostic not capacity-limit regime)
- **SE recursion**: spectrum-weighted generalized SE (Rangan-Fletcher-Goyal 2019 VAMP variant) + scalar IID SE (Bayati-Montanari 2011) in parallel; both converged to tol=1e-12
- **Empirical AMP**: matched-Gaussian MMSE denoiser with Onsager correction; 200 iterations max; convergence detected when plateau variance < 1e-10

---

## Falsifiable predictions

### HARD PASS (theory matches empirics)

- **AMP_SE_MATCHES_EMPIRICS**: mean relative error |SE_MSE - emp_MSE| / max(SE_MSE, emp_MSE) < 0.20 across >= 2/3 of cells. Interpretation: Kerdock codebook is effectively in the AMP universality class. First theory-to-empirics anchor for substrate M/N capacity. Deflated P=0.30 (Kerdock's algebraic structure makes exact RI-class membership uncertain; prior AMP universality pretest was PARTIAL at N=4096).

### HARD FAIL (structural divergence)

- **AMP_SE_DIVERGES**: mean relative error > 0.80 and fewer than 1/3 cells within 20%. Interpretation: Kerdock's Maiorana-McFarland algebraic structure (Walsh cosets with GF(2^t) quadratic form) breaks the AMP-SE assumptions. Novel finding: gives a sharp boundary marker for Pattern 4 (finite-dim classical RS frameworks). Deflated P=0.55 (Kerdock is NOT IID; the algebraic structure likely violates RI-class assumptions for AMP but not VAMP).

### INCONCLUSIVE

- **AMP_SE_INCONCLUSIVE**: intermediate regime. Partial match. Could indicate the SE converges but the empirical AMP does not (numerical instability at finite N), or that only certain alpha regimes are in-class.

### Pre-registered expectation

P(AMP_SE_DIVERGES) = 0.55, P(AMP_SE_MATCHES_EMPIRICS) = 0.30, P(AMP_SE_INCONCLUSIVE) = 0.15.

The smoke test at N=1024 already showed large divergence (SE_mse ~0.09 vs emp_mse ~0.65-0.95; rel_err ~0.83-0.87). This is consistent with DIVERGES at FULL. However, the smoke used only alpha={0.5, 1.0} (under-determined regime); the substrate's actual capacity is at alpha=8. The FULL run at alpha=8.0 may show tighter correspondence if the SE has a phase-transition structure that aligns with the substrate's M/N=8 empirical capacity.

---

## Substrate-product interpretation

- **AMP_SE_MATCHES_EMPIRICS**: provides the first quantitative theory-to-empirics anchor for the substrate's capacity. Validates that the RS-phase framework (load-bearing for substrate physics since cycle 112) extends to AMP/SE theory at substrate's exact codebook. Directly supports the M/N=8 anomaly characterization that four prior lit-scan agents could not bound.

- **AMP_SE_DIVERGES**: Kerdock structure lies outside AMP universality class. Means VAMP (which uses SVD, hence is invariant to algebraic structure) is the correct readout, and AMP without SVD would fail. This is load-bearing for the VAMP-on-chain architecture choice (cap_map v127+ row). It also indicates that the substrate's capacity mechanism is NOT standard RS AMP capacity -- there is something structurally different about the Kerdock codebook that standard AMP cannot capture. Novel substrate-physics finding.

---

## PROT compliance

Substrate-physics + capacity characterization experiment. PROT-001 (exp_dev_decisions log entry) paired.
