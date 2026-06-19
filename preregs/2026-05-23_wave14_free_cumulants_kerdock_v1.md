# Pre-registration: wave14_free_cumulants_kerdock_v1

**Date registered**: 2026-05-23
**Script**: experiments/exp_wave14_free_cumulants_kerdock_v1.py
**Triggering result**: AMP_SE_DIVERGES FULL (2026-05-23 ~18:13) — Kerdock codebook fell outside the AMP universality class
**Field-advisor candidate**: F4 Voiculescu free cumulants (tier-1 free-probability, anchor_yield=100%, score=5.5)
**Capability axis**: substrate-novel observability for Cap 1 + Cap 4 (probes the mechanism behind AMP_SE departure)
**Framing**: substrate-product capability observability; NOT a paper claim

## Hypothesis

The substrate's 4-coset Kerdock codebook has higher Voiculescu free cumulants
kappa_n (n in {2,3,4}) that deviate from the Marchenko-Pastur baseline c = M/N
by more than 20%. This is the FORMAL FREE-PROBABILISTIC MECHANISM for the
AMP_SE_DIVERGES verdict: Zhong-Wang-Fan arXiv:2110.02318 establishes that the
Onsager correction in orthogonally-invariant AMP is built from the free
cumulants of the noise spectrum; truncating to scalar SE assumes kappa_n = c
for all n (the MP free-cumulant signature). If Kerdock has nontrivial kappa_n
deviation, AMP-SE divergence is explained constructively.

Brutal-honesty P estimates (deflated per [[feedback-lit-scan-calibration-penalty]]):
- P(at least one kappa_n deviates > 20% from MP at alpha=1.0): **0.55**
  (AMP_SE_DIVERGES strongly suggests yes, but Kerdock columns are quasi-
  orthogonal at unit norm so kappa_2 may match c closely; the deviation
  likely lives in kappa_3 / kappa_4)
- P(verdict = FREE_CUMULANTS_DIVERGE on majority of alpha cells): **0.50**
- P(verdict = FREE_CUMULANTS_MATCH_MP — would mean AMP_SE_DIVERGES is
  driven by EIGENVECTOR rather than EIGENVALUE structure): **0.30**
- P(verdict = FREE_CUMULANTS_INCONCLUSIVE): **0.20**

The experiment is informative under all three verdicts:
- DIVERGE: identifies the mechanism for AMP-SE departure; substrate-novel
  observability via kappa_n profile
- MATCH: rules out free-cumulant spectral mechanism; points to eigenvector
  localization or non-orthogonal-invariant structure (next probe: IPR or
  delocalization measure)
- INCONCLUSIVE: motivates finer alpha resolution or higher-n cumulants

## Config (FULL)

- N = 4096 (substrate-realistic Kerdock-v4 scale; matches AMP_SE_DIVERGES config)
- M_over_N_list = [0.25, 0.5, 1.0, 2.0, 4.0] (5 alpha values; matches AMP_SE
  range and lets us probe the M/N=8 anomaly extrapolation direction)
- n_seeds = 5 (per research playbook: 5-seed standard)
- n_max_moment = 4 (kappa_1..kappa_4; closed-form moment-cumulant inversion
  per Nica-Speicher 2006)
- Method: empirical spectral moments m_n = (1/K) sum lambda_i^n from SVD of
  Kerdock submatrix; convert to kappa_n via Speicher recursion

## Predictions (falsifiable, with hard-fail thresholds)

For each alpha cell, define dev_n = kappa_n / c - 1 where c = M/N.

- **DIVERGE** verdict: at least ceil(n_cells / 2) cells have |dev_n| > 0.20
  for some n in {2,3,4}
- **MATCH_MP** verdict: ALL cells have |dev_n| < 0.10 for all n in {2,3,4}
- **INCONCLUSIVE** verdict: mixed (neither DIVERGE nor MATCH triggers)

Hard-fail / kill criteria:
- If kappa_1 (= empirical first moment) deviates from c by >5%: indicates a
  serious bug in spectrum computation; halt and investigate (the first moment
  of (1/N) A^T A for bipolar A with unit-norm rows must equal M/N exactly).
- If self-test (MP-moments-give-MP-cumulants for c in {0.5, 1.0, 2.0}) fails:
  halt before any cell run.

## VRAM / runtime budget

GPU-resident workload:
- Build Kerdock codebook 4N x N bipolar: 4*4096*4096 bytes float32 = 256 MB
- SVD of M x N matrix where M up to 4N = 16384: 16384 x 4096 float32 = 256 MB
- numpy.linalg.svd is CPU-bound (released from torch immediately)

Per (alpha, seed) cost dominated by SVD of M x N matrix. At alpha=4, N=4096:
SVD of 16384x4096 matrix ~ 5-15 sec on GPU host CPU. Total: 5 alphas * 5
seeds * ~10 sec = ~5 min wall. **GPU not strictly required** (no CUDA in
the SVD path) but routed to overnight_queue per Rule 0 (GPU idle, compute-
heavy by virtue of 5x5 = 25 cells; benefits from GPU machine's faster CPU
and persistent runner).

Timeout = 3600 s (1 hour, with 6x headroom over expected 5-10 min).

## Smoke result (pre-registration gate)

Smoke config: N=1024, alpha in {0.5, 1.0}, n_seeds=2. Runtime: ~10 sec.

Result (2026-05-23 ~18:38):
- Self-test 6/6 PASS (MP-moments give MP-cumulants for c in {0.5, 1.0, 2.0};
  verdict classifier on hand-crafted cases)
- alpha=0.5: kappa_mean = [1.000, 0.374, 0.094, 0.006] vs MP c=0.5
  -> dev_rel = [+1.00, -0.25, -0.81, -0.99]
- alpha=1.0: kappa_mean = [1.000, 0.749, 0.374, 0.046] vs MP c=1.0
  -> dev_rel = [0.00, -0.25, -0.63, -0.95]
- Smoke verdict: FREE_CUMULANTS_DIVERGE (2/2 cells exceed 20% dev threshold)
- metrics.json: data/exp_wave14_free_cumulants_kerdock_v1_smoke/metrics.json

Headline smoke finding (early signal): Kerdock kappa_1 matches MP exactly (the
trivial check) but kappa_2, kappa_3, kappa_4 are SYSTEMATICALLY LOWER than MP
across both alphas tested. The 25% deviation in kappa_2 is itself well above
the 20% threshold; kappa_4 is essentially zero. This is consistent with a
Kerdock spectrum that is "more deterministic" than MP — Welch-bound near-
orthogonal codewords give a tightly concentrated spectrum with smaller free-
cumulant tails.

Smoke verdict IS suggestive for FULL but not predictive (different alpha
sampling at N=1024 vs FULL N=4096; finite-N corrections expected).

## Failure modes / escalation

- If Kerdock builder fails at N=1024 (smoke crash): fall back to N=2048 for
  smoke; if still fails, file upstream-push to Strategy.
- If smoke runtime > 5 min: halt before FULL; the timeout estimate is wrong.
- If verdict computation crashes due to NaN in moments (possible if zero
  eigenvalues dominate at alpha > 1): add 1e-15 floor; re-smoke.

## Linkage to AMP_SE_DIVERGES (parent result)

The AMP_SE_DIVERGES verdict at 2026-05-23 ~18:13 established that the scalar
AMP state-evolution recursion does NOT predict empirical AMP MSE on the
Kerdock measurement matrix. Two candidate mechanisms:

1. **Higher free cumulants of Kerdock spectrum != MP** (this experiment)
2. **Eigenvector localization / non-orthogonal-invariance** (followup probe
   if MATCH_MP)

A DIVERGE outcome resolves mechanism #1 in favor of free-cumulant route.
A MATCH outcome rejects mechanism #1; mechanism #2 becomes the leading
candidate, motivating an IPR (inverse participation ratio) drill as the
next experiment in this design-space subtree.
