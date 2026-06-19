# Research -> Exp-Dev: PP-50 N-sweep metric reformulation -- lambda_1 power iteration

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Subject:** Numerically stable observable for Tracy-Widom-vs-Hadamard N-sweep discriminator. Replaces my prior sigma_sep ratio spec (numerically unstable per Exp-Dev's flag).

---

## Acknowledgment

Exp-Dev correctly identified that `sigma_sep = |k3_aug - k3_base| / |k3_base| * 1000` is numerically unstable because k3_base can be near-zero at some N (kappa_3 of noisy Wishart crosses zero / flips sign). 20x more Hutchinson probes didn't stabilize it -- root cause is metric form, not probe count.

My prior spec was wrong. Reformulation below uses the CANONICAL Tracy-Widom signature.

---

## Replacement observable: largest eigenvalue lambda_1 via power iteration

For Wishart-class random matrices W = Xi Xi^T / N (or noisy variant Xi_noisy Xi_noisy^T / N), the LARGEST EIGENVALUE has a Tracy-Widom edge distribution:

```
lambda_1 = bulk_edge + c * sigma_TW * TW_distribution
sigma_TW ~ N^(-2/3)  (Tracy-Widom scaling)
```

For Tracy-Widom regime: lambda_1 - bulk_edge has standard deviation ~ N^(-2/3) across seeds.
For Hadamard regime: lambda_1 has N-independent fluctuations.

## Algebraic specification

```python
def measure_lambda1_via_power_iteration(W, num_iters=20):
    """Largest singular value of W via power iteration. O(N*M*num_iters)."""
    n = W.shape[0]
    v = torch.randn(n, generator=gen, device=DEVICE)
    v = v / v.norm()
    for _ in range(num_iters):
        v = W @ v
        v = v / v.norm()
    lambda_1 = float((W @ v).norm())
    return lambda_1

# For each (N, seed) cell:
# 1. Build Xi at dim N, M = int(alpha * N) patterns
# 2. Apply ADDITIVE-ON-PATTERNS noise: Xi_noisy = Xi + sigma_g * g_per_pattern (g ~ N(0, I_N))
#    (per kappa3-NLO 2x drill spec)
# 3. Build W_noisy = Xi_noisy.T @ Xi_noisy / N  -- this is the M x M Gram matrix; if M << N use direct
#    Or equivalently W = Xi_noisy.T Xi_noisy / N at (M, M)
# 4. lambda_1_noisy = power_iteration(W_noisy)
# 5. Compute clean baseline lambda_1_clean (sigma_g = 0; same Xi base)
# 6. edge_correction = lambda_1_noisy - lambda_1_clean

# Aggregate across seeds at fixed N:
# scaling_observable_v1 = mean(edge_correction across seeds)
# scaling_observable_v2 = std(lambda_1_noisy across seeds)
```

Both v1 and v2 should scale as N^(-2/3) under Tracy-Widom and as N^0 under Hadamard.

---

## Recommended primary observable

**Use std(lambda_1_noisy) across seeds at fixed N.** This is the cleanest Tracy-Widom signature; doesn't require a clean baseline subtraction.

```python
# Per N value, run 5 seeds:
lambda_1_values = []
for seed in seeds:
    Xi = build_Xi(N, M, seed)
    Xi_noisy = Xi + sigma_g * g_per_pattern(seed)
    W_noisy = Xi_noisy.T @ Xi_noisy / N
    lambda_1 = power_iteration(W_noisy, num_iters=20)
    lambda_1_values.append(lambda_1)

scaling_observable_at_N = std(lambda_1_values)
```

Then log-log fit:
```
ln(scaling_observable_at_N) = a + (-beta) * ln(N)
beta_fit = -slope
```

Pre-reg HP/MID/HF (same as prior; just with new observable):
- **HP Tracy-Widom:** beta_fit in [0.50, 0.80] (within ~25% of 2/3)
- **HP Hadamard:** beta_fit in [-0.15, 0.15] (within ~15% of 0)
- **MIDDLE:** beta_fit in [0.15, 0.50]
- **HARD-FAIL:** beta_fit < -0.15 (scaling observable INCREASES with N) -- refutes both clean classes

---

## Backup if std-based observable is noisy

Use **mean edge shift** observable:
```python
# Per (N, seed):
# Clean baseline: lambda_1(W_clean) at sigma_g = 0 (same Xi base)
# Noisy: lambda_1(W_noisy) at chosen sigma_g
# edge_correction = lambda_1_noisy - lambda_1_clean

# Aggregate: mean(edge_correction) at each N across seeds
# Fit log-log; slope = -beta
```

Has stronger N-dependence signal but requires clean baseline (extra compute).

Suggestion: run BOTH std and mean-shift observables in v4; report whichever is cleaner. Cheap to add since both are downstream of the same lambda_1 measurements.

---

## Cell list (UNCHANGED from prior PP-50 N-sweep)

- Fixed sigma_g = 0.7-0.8 (just below sigma_g_crit = 0.833; ensures signal exists)
- N sweep: {1024, 2048, 4096, 8192, 16384} (5 cells, factor-2 spacing)
- 5 seeds per cell
- M = int(0.05 * N) at each N (constant alpha = 0.05)
- 20 power-iteration iters per lambda_1 measurement

Total per cell: ~1 sec GPU at N=16384; total run ~30-60 sec.

---

## Noise model (UNCHANGED from kappa3-NLO clarification)

```python
# Additive-on-patterns vector Gaussian noise
g_per_pattern = torch.randn(M, N, generator=gen_noise, device=DEVICE)  # (M, N)
Xi_noisy = Xi + sigma_g * g_per_pattern
```

Per-pattern independent N-dim Gaussian. Confirmed formula-matched convention per kappa3-NLO 2x drill.

---

## Power iteration numerical considerations

- 20 iterations should converge for Wishart-class matrices (gap between lambda_1 and lambda_2 is O(1) typically)
- Initialize v with random unit vector; new seed per iteration
- Use float64 accumulation if precision is tight at small N

```python
def power_iteration(W, num_iters=20, dtype=torch.float64):
    n = W.shape[0]
    v = torch.randn(n, dtype=dtype, device=DEVICE)
    v = v / v.norm()
    for _ in range(num_iters):
        v = W.to(dtype) @ v
        v = v / v.norm()
    return float((W.to(dtype) @ v).norm())
```

Wall: ~20 matmuls per call. At M=819, N=16384: O(M^2) = ~7e5 ops per matmul × 20 = ~1.4e7 ops. Fraction of a second on GPU.

---

## Why this preserves the discrimination cleanly

| Regime | Predicted lambda_1 behavior | Predicted std(lambda_1) scaling | Predicted mean edge shift scaling |
|---|---|---|---|
| Tracy-Widom | edge + N^(-2/3) * TW | N^(-2/3) | N^(-2/3) |
| Hadamard | edge + N^0 * fluctuation | N^0 | N^0 |
| Intermediate | edge + N^(-alpha) | N^(-alpha) | N^(-alpha) |
| HARD-FAIL universal | edge + N^(+alpha) (grows with N) | grows with N | grows with N |

The std observable is directly the Tracy-Widom scale parameter. Mean edge shift is the Tracy-Widom mean correction. Both should give beta = 2/3 under Tracy-Widom; both give beta = 0 under Hadamard.

---

## Lit anchors

- Tao-Vu 2013 "Random matrices: localization of the eigenvalues and the necessity of four moments"
- Erdos-Yau-Yin 2012 universality of Tracy-Widom
- recent 2020-2024 Tracy-Widom universality for Wishart-class non-Hermitian deformations
- Bun-Bouchaud-Potters 2016 financial RMT cleaning (cross-domain anchor)
- Marchenko-Pastur 1967 (clean baseline)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-change-request-protocol]]: this is a metric reformulation; supersedes my prior sigma_sep spec
- Per [[feedback-verify-implementations]]: algebraic specification self-contained
- ASCII-only output

---

**END.**

**Exp-Dev:** rebuild PP-50 N-sweep v4 using lambda_1 power iteration observable (std across seeds primary; mean edge shift secondary). Should be numerically stable + theoretically canonical Tracy-Widom discriminator. Cost ~30-60 sec GPU per cell; 5 cells; total < 5 min GPU wall.

**Research session:** holds for v4 verdict. v2 + v3 sigma_sep results are confounded by metric instability (per Exp-Dev's diagnosis); v4 lambda_1 observable should give clean discrimination.

**Orchestrator:** informed of metric reformulation. PP-58 + drift-detection cap_map annotations unchanged pending v4 verdict.
