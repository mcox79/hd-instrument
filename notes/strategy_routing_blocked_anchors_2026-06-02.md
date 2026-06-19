# Strategy Routing: 3 Blocked Anchors (2026-06-02)
Source: exp_dev smoke gate failures — genuine scientific findings, not instrumentation errors.

## Blocked Anchor 1: pp47_deletion_cert_composition_v1
Script: experiments/exp_pp47_deletion_cert_composition_v1.py
Smoke result: HARD_FAIL HF2 (cosine_del=0.799; threshold HP<0.20)
Root cause: At N=1024 K=51 alpha=0.05, Gaussian sigma=2 place-field patterns have substantial
  overlap between neighboring positions. Rank-1 subtraction W' = W - (1/N)*xi_X*xi_X^T
  removes the direct memory trace for xi_X, but the correlated neighbors (xi_{X+1}, xi_{X+2})
  retain enough weight to reconstruct xi_X via crosstalk. The Hopfield dynamics converge to
  a state close to xi_X even after deletion.
  
Design question for Strategy:
  1. Does N=4096 (FULL scale) reduce crosstalk enough? K=204, sigma=2 still gives
     overlap ~exp(-d^2/8) between positions distance d apart. At d=1, overlap ~0.88.
     Rank-1 deletion may still be insufficient regardless of N.
  2. Is the deletion certificate ξ_X^T(W'-W)ξ_X/N = -1 correct and sufficient,
     or does it only certify algebraic cancellation not retrieval suppression in
     the correlated-input regime?
  3. Rescue options:
     a) Multi-rank deletion: subtract contributions from ALL patterns that significantly
        overlap xi_X (e.g., remove xi_{X-2}...xi_{X+2} components)
     b) Change PLACE_FRAC: reduce M so system is deeper below capacity; lower crosstalk
     c) Change sigma: use sigma=0.5 (near-delta patterns) to reduce overlap
     d) Change test: HP2 should be "cosine < 0.50 OR cosine < cosine_pre_deletion * 0.70"
        (relative drop) not absolute threshold
     e) Higher-order deletion: W'' = W - sum_j lambda_j v_j v_j^T where v_j = eigenvectors
        with large xi_X weight

Pre-registration for smoke: HP1 cert=-1.000 PASS (confirmed algebraically exact)

## Blocked Anchor 2: streaming_prediction_6_v1
Script: experiments/exp_streaming_prediction_6_v1.py
Smoke result: HARD_FAIL (Spearman rho=0.29; threshold HP>=0.60)
Root cause: At M=20 patterns, N=1024, alpha=0.05, system is well BELOW capacity
  (~M/N = 0.020 vs critical ~0.14). All patterns retrieve near-perfectly regardless
  of importance weights. Importance-weighted Hebbian changes the weight magnitudes but
  the basin depth differences are too small to measure with cosine fidelity when all
  patterns achieve cosine>0.95.
  
Design question for Strategy:
  1. Importance-weighted fidelity ONLY discriminates near capacity. The test needs
     M >= 0.10*N to 0.14*N to see differentiation.
  2. Correct regime: M_smoke=100, N=1024 (alpha=0.10); M_full=500, N=1024 (alpha=0.49).
     But this risks OOM at alpha=0.49.
  3. Alternative metric: measure BASIN RADIUS (max noise level for reliable retrieval)
     rather than fidelity. Basin radius should differ between high/low importance patterns
     even below capacity.
  4. Alternative architecture: use SPARSE or BINARY patterns where importance-weighting
     can create measurable capacity asymmetry at lower load.

## Blocked Anchor 3: streaming_prediction_7_v1
Script: experiments/exp_streaming_prediction_7_v1.py
Smoke result: HARD_FAIL (Spearman rho=-1.0; r_eff increases with alpha, not decreases)
Root cause: Hypothesis was backwards. r_eff = exp(H(sigma(W))) is the EFFECTIVE RANK
  of the weight matrix, which INCREASES monotonically as more patterns are stored
  (each new pattern adds an eigenvalue). It is NOT a predictive capacity indicator that
  decreases as the system fills. Prior anchor effective_rank_sweep_v1 confirmed
  frac_monotone=1.00 (r_eff grows with M below capacity).
  
Design question for Strategy:
  1. r_eff cannot be used as a "remaining capacity" gauge the way we hypothesized.
     As M increases, r_eff increases (more rank in W), not decreases.
  2. What DOES decrease with filling? Spectral gap? Min eigenvalue? Fraction of
     eigenvalues near zero? Spurious attractors count?
  3. The PP-44 gauge is confirmed as a CAPACITY TRACKER (monotone up), not a
     REMAINING CAPACITY estimator.
  4. Rescue: redefine SP7 as testing "r_eff / M is constant below capacity" (Marchenko-
     Pastur prediction). This is a meaningful scaling law that doesn't require the
     wrong-direction hypothesis.
  5. Alternative capacity gauge: track max eigenvalue lambda_max relative to
     bulk Marchenko-Pastur edge (lambda_max - lambda_MP_edge) as a capacity warning.

## Routing priority
- pp47: HIGH (blocking Tier-6 LLM-integration testbed Phase 0)
- SP6: MEDIUM (importance-weighted storage is a core Bet-A feature)
- SP7: MEDIUM (capacity prediction is a monitoring primitive; rescue is clean)
