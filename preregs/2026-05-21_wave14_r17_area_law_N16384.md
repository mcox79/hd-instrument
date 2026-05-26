# Pre-registration: wave14_r17_area_law_probe1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Strategy push #5 (cycle 43 update — R17 Probe 1; ZERO GPU; cheap)
Author: experiment_dev session, pipeline tick 71

## Why

R17 holographic landed LARGELY NEGATIVE. Probe 1 is a cheap analyzer-only
test that distinguishes:
- (a) substrate is classical (volume-law entropy scaling, ~55-70% prior)
- (b) substrate is RT-QEC-like (area-law entropy scaling, ~25-40% prior)

Per Harlow 2017 RT-QEC area-law expectation. If neither fits, R17 framework
inapplicable.

## Mechanism (per R17 Probe 1 spec)

For a substrate W = sum_i v_i k_i^T / N (M random outer-product Hebbian):
  Treat W reshaped as bipartite vector |W> with row-index and col-index subsystems.
  For random bipartition A of rows of size |A|:
    M_A = W[A, :] / ||W||_F
    rho_A = M_A @ M_A.T  (size |A| x |A|, trace = ||M_A||_F^2)
    S_2(A) = -log(Tr(rho_A @ rho_A))

Sweep |A| in {N/8, N/4, N/2}; multiple bipartition seeds; fit log(S_2) vs log(|A|).
- Slope ~ 1 -> volume-law
- Slope ~ 0 -> area-law-like (1D boundary)
- Slope between -> intermediate / unclear

## Verdict labels

- R17_AREA_LAW_LIKE (slope < 0.4 — substrate has bounded entropy, consistent with RT-QEC)
- R17_VOLUME_LAW (slope > 0.85 — substrate is "high-dimensional", classical)
- R17_INTERMEDIATE (0.4 <= slope <= 0.85)
- R17_INCONCLUSIVE

## Runtime: ~3 min (CPU; SVD of submatrices)
