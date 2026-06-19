# Prereg: wave14_R_transform_kerdock_v1_multi_N

**Date**: 2026-05-23 cycle 184 (post-v164 cap_map commit)
**Owner**: Exp Dev (dispatched by verdict_handler in batched-mode, GPU refill action per pipeline-pacing)
**Script**: `experiments/exp_wave14_R_transform_kerdock_v1_multi_N.py`
**Queue**: overnight_queue (GPU; CPU-bound numpy SVDs but routed to GPU machine for faster CPU + persistent runner)
**Timeout**: 3600 s

## Motivation

v164 cap_map (committed 74afa6e, batched two-verdict update) added a new evidence-strength row under "Substrate-physics characterization":

> "Free-cumulant fingerprint of Kerdock R-transform (substrate-novel observability)" 🟢 Validated, want stronger (single-N N=1024 5/5 cells exceed 20% kappa_n deviation; max_dev=1.125 at kappa_4 alpha=2.00)

The row sits at evidence-strength 🟢 because we only have single-N (N=1024) data. This experiment supplies the multi-N scaling test that either (a) promotes the row to ✅ if the deviation is dimension-stable, (b) keeps it 🟢 with a thermodynamic-limit caveat if the deviation shrinks with N (finite-N artifact), or (c) promotes it to ✅ with a growth annotation if the deviation grows with N (substrate-novel scaling regime).

Companion goal: supply the spectral input (kappa_n profile per alpha) for the deferred VAMP-SE-on-Kerdock follow-up that v163 + v164a motivate (the Onsager-correction coefficients in the exact VAMP-SE recursion ARE the free cumulants of the noise spectrum).

## Scientific question

For Kerdock 4-coset codebooks at N in {1024, 4096} and alpha = M/N in {0.5, 1.0, 2.0}, do the empirical free cumulants kappa_n (n=2,3,4) of the singular-value spectrum maintain max |kappa_n / c - 1| > 0.20 (the v164 threshold) as N grows, or does the deviation shrink toward MP?

## Pre-registered outcomes

| Verdict tag | Trigger | v164 row impact |
|---|---|---|
| `R_TRANSFORM_STABLE_IN_N` | >= 1/2 alpha cells stay above 0.20 deviation across the N range AND |max_dev(N_max) - max_dev(N_min)| < 0.20 | v164 free-cumulant fingerprint row promotes 🟢 -> ✅ (dimension-stable substrate-novel observability) |
| `R_TRANSFORM_GROWS_IN_N` | >= 1/2 alpha cells show dev_max - dev_min > 0.20 across the N range | v164 row promotes 🟢 -> ✅ with growth annotation (substrate-novel scaling regime) |
| `R_TRANSFORM_SHRINKS_IN_N` | >= 1/2 alpha cells show dev_min - dev_max > 0.20, OR cells go MP-like at large N | v164 row stays 🟢 with thermodynamic-limit caveat; v163 AMP_SE_DIVERGES spectral explanation NEEDS A NON-FREE-CUMULANT MECHANISM (e.g., eigenvector localization) |
| `R_TRANSFORM_INCONCLUSIVE` | mixed; no >= 1/2 majority | v164 row stays 🟢; consider wider N range or more seeds |

## Hypothesis (pre-test belief)

Based on the v1 smoke + FULL data showing max_dev=1.125 at kappa_4 alpha=2.00 (substantial), and the v120 + v163 + v164a stacking argument that the substrate's algebraic Kerdock structure is dimension-invariant by construction (4-coset MM codebook from GF(2^t)), the most likely outcome is `R_TRANSFORM_STABLE_IN_N`. The substrate's higher kappa_n should not shrink under N because the codebook structure itself does not change with N — only the codeword length changes. This is the "the substrate's algebra is provably outside AMP universality" claim's most natural completion.

Per [[feedback-lit-scan-calibration-penalty]] deflated P estimates:
- P(STABLE_IN_N) = 0.50 (most likely; substrate-algebra-invariant)
- P(GROWS_IN_N) = 0.20 (plausible if finite-N effects subtractively flatten the spectrum at small N)
- P(SHRINKS_IN_N) = 0.20 (plausible if v1's deviation IS partly a finite-N artifact; would refute spectral mechanism)
- P(INCONCLUSIVE) = 0.10

## Configuration

- N_list: {1024, 4096} (limited by PRIMITIVE_POLY registry: t=5 → N=1024; t=6 → N=4096; extending to t=7 (N=16384) is a future patch)
- M_over_N_list (alpha): {0.5, 1.0, 2.0}
- n_seeds: 5 per (N, alpha) cell
- n_max_moment: 4 (kappa_1 through kappa_4)
- Expected runtime: SVD of (M × N) where M up to 8192 × 4096 = 33M cells dense float matrix → seconds per seed; 6 cells × 5 seeds = 30 SVDs total; under 10 min on persistent CPU.

## Pause-gate compliance

Pause flag CLEARED at time of dispatch. Verdict_handler Step 2 pipeline-pacing reflex active: GPU queue depth = 0 at v164 commit, so ONE GPU refill is authorized.

## Routing context

This experiment is the v164a row promotion probe. If STABLE or GROWS lands, the cap_map gains a ✅ row + the VAMP-SE-on-Kerdock follow-up has its spectral input. If SHRINKS lands, the substrate-product positioning ("our algebra is outside AMP universality") needs to be re-anchored to a non-free-cumulant mechanism (e.g., eigenvector localization).
