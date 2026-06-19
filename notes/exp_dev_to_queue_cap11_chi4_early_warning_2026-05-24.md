# exp_dev -> queue: Cap 11 chi_4 early-warning anchor (2026-05-24)

Strategy dispatched the Cap 11 chi_4 early-warning anchor per Research drill `notes/research_cap11_chi4_early_warning_drill_2026-05-24.md`. Anchor tests whether the 4-point connected susceptibility chi_4 (with parallel AC(1) + Var + tau_R) predicts approach to the Cap 10 capacity boundary BEFORE retrieval collapses, with quantitative HARD PASS / HARD FAIL bands.

Self-tests passed locally (verdict 7/7 cases + indicator formula self-tests: chi_4 white-noise, AC(1) white-noise, AC(1) AR(1) rho=0.7, Var white-noise, tau_R zero-perturbation). Smoke at N=1024 / 1-seed / 4 alpha cells ran in ~25s on CPU; verdict CAP11_CHI4_MIDDLE_BAND (under-resolved — production run has N=4096, 5 seeds, 8 alpha cells). Remote `--self-test` gate also passed (2.4s) and entry is queued on overnight_queue.

## Schema A — queue entries

```
queue=overnight_queue name=wave14_cap11_chi4_early_warning_anchor_v1 script=experiments/exp_wave14_cap11_chi4_early_warning_anchor_v1.py prereg=preregs/2026-05-24_wave14_cap11_chi4_early_warning_anchor_v1.md timeout=5400
```

## Schema B — markdown table (redundant, for parser fallback)

| queue           | name                                          | script                                                              | prereg                                                              | timeout(s) |
|-----------------|-----------------------------------------------|---------------------------------------------------------------------|---------------------------------------------------------------------|------------|
| overnight_queue | wave14_cap11_chi4_early_warning_anchor_v1     | experiments/exp_wave14_cap11_chi4_early_warning_anchor_v1.py        | preregs/2026-05-24_wave14_cap11_chi4_early_warning_anchor_v1.md     | 5400       |

## Why GPU (Tier A)

- 5 seeds * 8 alpha cells = 40 cells, plus 5-cell permutation null at chi_4 peak.
- Per cell: N=4096 Kerdock-Hebbian W, 32 perturbed trajectories of 10 argmax-dynamics steps each, plus 100-probe retrieval test, plus tau_R relaxation probe.
- Total ~10^5 substrate dynamics steps with N=4096 matrix-vector products = compute-heavy.
- Strategy explicitly requested GPU per gpu-first-for-depth-probes feedback; substrate dynamics + per-write fluctuation statistics is the canonical depth-needing-probe class.

## Lead-time / open risks

- alpha_c=0.14 is the generic Hopfield value; Kerdock-specific alpha_c may differ. Post-hoc recalibration of lead-time fractions allowed if empirical retrieval knee disagrees substantially with 0.14. The alpha grid (0.014 -> 0.196) covers 0.1x to 1.4x of nominal alpha_c and brackets any reasonable empirical knee.
- All four indicators (chi_4 + AC(1) + Var + tau_R) are computed and reported regardless of verdict; per Research, inter-indicator agreement is itself diagnostic.
- Permutation null re-samples the codeword set (rather than shuffling write order) because Kerdock-Hebbian W = T^T T is order-symmetric; an order-shuffle would be a no-op for this substrate.
