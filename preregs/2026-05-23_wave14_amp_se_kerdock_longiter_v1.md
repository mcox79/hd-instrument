# Pre-registration: wave14_amp_se_kerdock_longiter_v1

**Date**: 2026-05-23
**Queue**: remote_cpu_queue (numpy AMP iteration; CPU-bound; N=4096 matrix-vector products)
**Axis probed**: AMP-on-Kerdock long-iteration trajectory shape
**Trigger**: Emergency refill 2026-05-23 19:50; v163 AMP_SE_DIVERGES ran 200 iters; user requests 5x extension to discriminate explosion vs fixed-point vs oscillation
**Script**: experiments/exp_wave14_amp_se_kerdock_longiter_v1.py
**Peak memory**: ~800 MB CPU at N=4096 M=16384
**Expected elapsed**: ~20-30 min (5 seeds * 3 alpha * 1000 iters * N=4096 mat-vec)

---

## Scientific question

v163 AMP_SE_DIVERGES (2026-05-23) ran 200 AMP iterations on Kerdock at N=4096
and concluded the scalar AMP-SE prediction does not match empirical AMP MSE.
But 200 iterations may have terminated mid-trajectory. The "diverges" verdict
is correct in the sense that AMP-SE != empirical AMP, but the EMPIRICAL AMP's
own asymptotic behavior is unknown: does it explode, oscillate, or plateau at
a non-SE fixed point?

This experiment runs 5x longer (1000 iterations) and records the full MSE
trajectory + tau_eff history. Classifies trajectory shape via:
  - growth: linear fit of log(mse) over last 500 iters
  - oscillation: max deviation from running mean over last 100 iters
  - plateau location: mse_at_1000 vs scalar-SE prediction

---

## Design

- **N**: 4096
- **M/N alpha grid**: [1.0, 2.0, 4.0]
- **sigma_noise**: 0.1
- **signal_var**: 1.0 (Gaussian prior, MMSE denoiser)
- **Seeds**: 5 per alpha
- **n_iter**: 1000 (5x v163's 200)
- **Trajectory record**: full mse history + tau_eff history; sentinel divergence
  cutoff at 1000 * signal_var

---

## Falsifiable predictions

### AMP_LONGITER_EXPLODES (HARD FAIL of AMP at any iter)

>=50% of cells: mse_at_1000 > 2 * mse_at_200 AND log-slope > 0.001, OR diverged_flag.
AMP iterates explode on Kerdock. v163's verdict is a snapshot of runaway dynamics.
Deflated P = 0.30.

### AMP_LONGITER_FIXED_POINT (CONFIRMS v163; non-SE plateau)

>=50% of cells: oscillation_rel < 0.10 AND mse_at_1000 > 1.5 * scalar-SE prediction.
AMP converges to a fixed point but at the WRONG MSE. v163's "diverges" is correct
but it's a non-SE fixed point, not blowup. Deflated P = 0.35.

### AMP_LONGITER_OSCILLATES

>=50% of cells: oscillation_rel > 0.20 AND |log-slope| < 0.0005. AMP cycles between
extrinsic basins. Substrate-novel dynamical failure mode. Deflated P = 0.20.

### AMP_LONGITER_CONVERGES_TO_SE (would REVERSE v163)

>=50% of cells: mse_at_1000 within 20% of scalar-SE prediction. v163 was an
under-iteration artefact. Substrate IS in AMP universality. Deflated P = 0.05
(very low prior given v163's clean divergence at 200 iters).

### AMP_LONGITER_INCONCLUSIVE

Mixed. P = 0.10.

---

## Substrate-product interpretation

- **EXPLODES**: substrate-product flag = "AMP unsafe on this codebook" (any iteration
  count is unstable). Architecture mandate: VAMP/OAMP only.
- **FIXED_POINT**: substrate has well-defined non-SE asymptote. Mechanism for v163
  pinned down: the fixed-point MSE encodes substrate's algebraic structure beyond
  scalar SE. Possibly recoverable by OAMP using kappa_n corrections.
- **OSCILLATES**: AMP dynamics are limit-cycle on Kerdock. Mathematically interesting:
  could be related to Kerdock's coset symmetry exchanging extrinsic basins.
- **CONVERGES_TO_SE**: would force a re-write of v163; very low prior.

---

## PROT compliance

Per [[feedback-pipeline-pacing]]: remote CPU long-running follow-up to v163; ETA 20-30 min
keeps pipeline busy while GPU runs heavier kappa_n / VAMP-contrast experiments. Distinct
verdict from v163 (asymptotic trajectory shape, not just SE vs empirics).
