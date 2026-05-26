# Pre-registration: wave14p_erase_multiprobe

Date: 2026-05-20
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14p_erase_multiprobe.py](../experiments/exp_wave14p_erase_multiprobe.py)

## Why

wave14h_alpha_sweep_v2 showed argmax-leak = 0% at alpha=1.5 with no kept-recall
drop. That's suspiciously good. The "Mirage of Model Editing" paper
(arXiv:2503.06991, ACL 2025) explicitly warned: ROME-edited facts often pass
argmax tests but FAIL paraphrase / representation / MIA probes.

This is the validation test. If alpha=1.5 truly forgets the fact, we should
see ALL probes collapse: argmax leak low, rank in codebook high, norm of
retrieval near zero, cosine near zero, AND the same behavior under paraphrased
queries (key with 10% bits flipped).

If only the argmax probe collapses while rank stays at 1 and norm/cos stay
high, we have the Mirage failure mode -- the substrate "looks erased" only to
naive queries but still contains the information.

## Hypothesis

At some alpha in [0.5, 3.0], ALL probes collapse simultaneously:
  - argmax_leak <= 10%
  - mean_rank in codebook >= n_facts * 0.3
  - norm_ratio <= 0.30 (retrieved vector is small)
  - cosine to true value <= 0.25
  - paraphrase argmax_leak <= 20%

Backup: argmax-only collapse (MULTIPROBE_ARGMAX_ONLY) means we know the
GDPR pitch needs caveats.

## Oracle assertions

1. pairwise_std at largest K in [0.03, 0.50]
2. Baseline (no erase) argmax leak >= 0.70
3. At max alpha: mean_rank > 1.5 OR (baseline_argmax - argmax_leak) >= 0.20.
   In other words, erase must move SOMETHING measurable.

## Operational definition

- N=4096, n_facts=200, n_erase=50, rank_L=50 (strong correlation)
- alphas: {0.5, 0.85, 1.0, 1.1, 1.2, 1.3, 1.5, 2.0, 3.0}
- 5 seeds per alpha
- For each erased fact e:
  - Compute retrieved = W_B @ k_e
  - argmax leak: argmax(retrieved @ values.T) == e?
  - rank: position of e in sorted similarity list (1-indexed)
  - norm_ratio: ||retrieved|| / sqrt(N)
  - cosine: cos(retrieved, values[e])
  - paraphrase: same metrics but with k_e_perturbed (10% bits flipped)

## Cited mechanism / sources

- ROME (arXiv:2202.05262), MEMIT (arXiv:2210.07229)
- "Mirage of Model Editing" (arXiv:2503.06991, ACL 2025) -- the canonical
  warning about argmax-only artifacts
- "Are We Truly Forgetting?" (arXiv:2503.06991) -- multi-probe framework
- Foldiak 1990 -- anti-Hebbian convergence under correlation

## Expected runtime

Smoke (N=512, 2 alphas, 1 seed): ~5 sec
Full (N=4096, 9 alphas, 5 seeds): ~5-8 min on GPU

## Verdict labels

- `MULTIPROBE_GDPR_GRADE`: all probes confirm at some alpha
- `MULTIPROBE_ARGMAX_ONLY`: Mirage failure (argmax says erased, probes disagree)
- `MULTIPROBE_NO_ERASURE`: even argmax doesn't erase
- `MULTIPROBE_INCONCLUSIVE`: empty data

## What product decision this enables

GDPR_GRADE: real GDPR pitch holds. Anti-Hebbian rank-1 is a defensible erase
mechanism under correlated keys, multi-probe verified.

ARGMAX_ONLY: anti-Hebbian alone is NOT a GDPR mechanism. Need ROME-style
direct write or key orthogonalization preconditioning. wave14q follow-up
tests these.

NO_ERASURE: even the basic mechanism fails in our regime. Different
architecture needed.
