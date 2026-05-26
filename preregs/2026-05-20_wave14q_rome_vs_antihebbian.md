# Pre-registration: wave14q_rome_vs_antihebbian

Date: 2026-05-20
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14q_rome_vs_antihebbian.py](../experiments/exp_wave14q_rome_vs_antihebbian.py)

## Why

wave14p_erase_multiprobe showed anti-Hebbian rank-1 fails the Mirage test
under correlated keys: argmax says erased but rank/norm/cos disagree.

Research (ROME arXiv:2202.05262) uses W' = W - (Wk)(C^{-1}k)^T / (k^T C^{-1}k)
where C is the empirical key covariance. The C^{-1} compensates for key
correlation that breaks anti-Hebbian.

This experiment runs BOTH methods through the multi-probe framework.

## Hypothesis

ROME-style direct write (with C^{-1} conditioning) passes the GDPR-grade
multi-probe criteria at some alpha in [0.3, 3.0]; anti-Hebbian fails them
in this regime (already shown in wave14p).

## Kill criterion

If BOTH methods fail the multi-probe (BOTH_MIRAGE), neither approach is
GDPR-grade under our correlation regime. Need: stronger preconditioning
(Householder/Gram-Schmidt) or iterative refinement (wave14r).

## Oracle assertions

1. `pairwise_std in [0.03, 0.50]` (correlated keys)
2. At max alpha, mean_rank > 1.5 for at least one of {ROME, anti-Hebbian}
   (something moved)

## Operational definition

- N=4096, n_facts=300, n_erase=75, rank_L=75 (strong correlation)
- alphas: {0.3, 0.5, 0.7, 0.85, 1.0, 1.1, 1.2, 1.3, 1.5, 1.75, 2.0, 2.5, 3.0}
- 7 seeds
- For each method in {anti-Hebbian, ROME}:
  - For each alpha:
    - Build W, compute C if ROME (with regularization 0.01 * I)
    - Iteratively erase n_erase facts
    - Multi-probe: argmax_leak, mean_rank, norm_ratio, cos, paraphrase same
- Compare best alpha across methods

## Cited mechanism

- ROME (arXiv:2202.05262): the original rank-1 W edit with key covariance
- MEMIT (arXiv:2210.07229): mass-edit extension
- Mirage paper (arXiv:2503.06991): argmax-only artifacts to watch for
- Kanter-Sompolinsky projector: pseudoinverse erase as alternative

## Expected runtime

Smoke (N=512, 2 alphas, 1 seed): ~10 sec
Full (N=4096, 13 alphas, 7 seeds, 2 methods): ~10-15 min on GPU

## Verdict labels

- `ROME_WINS_GDPR`: ROME passes multi-probe, anti-Hebbian doesn't
- `BOTH_PASS_GDPR`: both pass at some alpha
- `BOTH_MIRAGE`: both fail deeper probes
- `AH_WINS`: unexpected (anti-Hebbian passes but not ROME)
- `NEITHER_ERASE`: even argmax fails

## What product decision this enables

ROME_WINS_GDPR -> "Our memory tier supports ROME-style provable forgetting
with cryptographic-grade GDPR guarantees. Math from the canonical ROME paper
applies directly."

BOTH_MIRAGE -> stronger machinery needed (Householder preconditioning,
iterative refinement). Move to wave14r.

NEITHER -> our substrate fundamentally can't do GDPR erase under this
correlation level. Different architecture or weaker correlation regime.
