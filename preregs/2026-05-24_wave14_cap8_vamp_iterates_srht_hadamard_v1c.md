# Prereg: wave14_cap8_vamp_iterates_srht_hadamard_v1c

Date: 2026-05-24
Queue: remote_cpu_queue
ETA: 30-45 min CPU
Type: DATA GENERATION (no hypothesis test; downstream input for Anchor 2)

## Purpose

Composition A audit v1 yielded `rho = 1.0` on Kerdock (perfect alignment
of kappa_n divergence and Schur-Weyl irrep mass deviation across orders
n=2..5) but NaN on SRHT and Hadamard, blocking the cross-family hard-pass
check. Per the routing brief: "those codebooks didn't have saved Cap 8
VAMP iterate traces."

This anchor runs the canonical VAMP loop at Cap 8 protocol shape
(N=4096, M/N=1.0, 5 seeds, alpha in {0.5, 0.75, 1.0}) on SRHT + Hadamard
codebooks and SAVES per-iteration:

- `x_hat_norms`, `x_hat_2_norms` (pre-/post-denoiser estimate norms)
- `mse_per_iter`
- `denoiser_output_norm` (alias of x_hat_2_norms)
- `onsager_term_norm` (proxy: `gamma_2 * ||r_2||` per iter)
- `gamma_1`, `gamma_2` precision parameters per iter

## Output layout

```
data/exp_wave14_cap8_vamp_iterates_srht_hadamard_v1cb/
  iterates/srht/alpha_{0p50,0p75,1p00}/seed_{0013,1013,2013,3013,4013}.json
  iterates/hadamard/alpha_{0p50,0p75,1p00}/seed_{0013,1013,2013,3013,4013}.json
  metrics.json    (summary + 30-file manifest)
```

30 trace files total (2 codebooks * 3 alpha * 5 seeds).

## Hypothesis test

NONE -- this is data generation. No hard-pass/hard-fail thresholds on
scientific content. The downstream Anchor 2 owns the Composition A
hypothesis test.

## Verdict bands (data-gen integrity)

- **CAP8_ITERATES_GENERATED**: all 30 trace files written successfully
  with >=10 VAMP iterates each; downstream Anchor 2 has full data.
- **CAP8_ITERATES_PARTIAL**: some files written but <30; Anchor 2 must
  check existence per cell and may still compute rho on partial data.
- **CAP8_ITERATES_FAILED**: <10 files written; the data gap is NOT
  filled and Anchor 2 cannot resolve SRHT/Hadamard.

## Self-tests (executed before main run)

1. `alpha_label` formatting deterministic.
2. SRHT + Hadamard builders execute at N=4096 (production shape).
3. VAMP converges on iid Gaussian near AMP-SE prediction (within 20% rel).
4. Iterate JSON round-trip (write+read+key check).
5. Per-iter quantities are finite and shape-consistent.
6. Verdict branches synthesize correctly.

## Smoke (PASS)

```
N=64, 1 seed, alpha=1.0, SRHT only -> 1 trace file with n_iter=5
VERDICT: CAP8_ITERATES_GENERATED (smoke threshold=1 iter)
```

## Open questions / risks

- VAMP early-stops when MSE plateau detected (5 consecutive iters within
  1e-10); production runs at n_iter=300 should produce >=10 iters in
  almost all cells. If Hadamard converges in <10 iters, those cells will
  count as "missing" in the verdict; downstream Anchor 2 handles partial.
