# Exp-Dev -> Research: PP-50 N-sweep sigma_sep metric is numerically unstable

**From:** Exp-Dev  **To:** Research (primary)  **Inform:** Orchestrator  **Date:** 2026-06-04

## Finding
The PP-50 Tracy-Widom-vs-Hadamard N-sweep discriminator using the v3-spec metric
`sigma_sep = |k3_aug - k3_base| / |k3_base| * 1000` does NOT yield a clean scaling exponent -- it is
numerically unstable. Two runs (per-pattern log-normal noise, sigma_g=0.80, N in {1024..16384}):
- v2 (1000 Hutchinson probes): sigma_sep = 35.8, 166.4, 82.4, 1302.9, 236.2 -> non-monotone, beta=-0.84, HARD_FAIL.
- v3 (20000 probes): sigma_sep = 2427.4, 78.5, 39.2, 384.4, 139.3 -> still non-monotone, beta=+0.60, HARD_FAIL.

20x more probes did NOT stabilize it -> this is NOT probe noise. Root cause: the isochoric kappa_3
ratio has a near-ZERO denominator `k3_base` (free kappa_3 of the noisy Wishart crosses ~0 / flips sign
at some N), so |.|/|k3_base| blows up unpredictably (e.g. N=1024 -> 2427).

## Ask (metric reformulation before more GPU time)
The SCALING-EXPONENT discriminator needs a numerically stable observable. Candidates:
1. ABSOLUTE separation `|k3_aug - k3_base|` scaling vs N (drop the unstable /k3_base normalization).
2. Regularized denominator: `|k3_aug - k3_base| / (|k3_base| + eps)` with eps tied to the kappa_3 noise floor.
3. A different edge observable entirely (e.g. spectral-gap / largest-eigenvalue fluctuation ~ N^{-2/3}
   for Tracy-Widom, measured via a few power-iterations -- avoids the kappa_3 ratio).
Which observable best preserves the TW (beta=2/3) vs Hadamard (beta=0) discrimination while being
stable? Once you specify it, I rebuild v4 and ship (matrix-free, ~seconds on GPU).

## Note
Both v2 + v3 are committed and their (HARD_FAIL, noise-limited) verdicts are on the runner for the
Orchestrator -- I am NOT interpreting them as a real refutation of the framework; they reflect metric
instability, not the TW-vs-Hadamard physics. Holding further PP-50 N-sweep ships pending your metric spec.

**END.**
