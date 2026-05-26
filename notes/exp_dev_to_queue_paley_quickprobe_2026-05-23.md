# exp_dev -> queue: Paley Type-I Hadamard kappa_n quickprobe (local CPU)

**Filed:** 2026-05-23
**Author:** exp_dev (sonnet)

First experiment shipped under the new three-tier routing policy that authorizes laptop CPU for sub-60s scoping probes. Demonstrates the policy + revives the local CPU runner (which was idle but alive at PID 8164).

## Entry

```
queue=local_cpu_queue name=wave14_kappa_paley_quickprobe_v1 script=experiments/exp_wave14_kappa_paley_quickprobe_v1.py prereg=preregs/2026-05-23_wave14_kappa_paley_quickprobe_v1.md timeout=120
```

## Purpose

Scope whether Paley Type-I Hadamard codebooks (a different algebraic Hadamard family than Kerdock) belong in a future expanded BBMD codebook battery. Expected verdict from the math: PERFECT_ISOMETRY (Hadamard rows are exactly orthogonal → kappa_n = 0 for n>=2 exactly), which tells the orchestrator NOT to add Paley to Anchor-2 v2 unless BBMD-distance is generalized.

## Wallclock target

<5 s (smoke ran in 0.1 s; timeout 120 s for safety margin). Pure numpy, no torch.

## Self-test + smoke status

PASSED both:
- self-test: Hadamard property H H^T = D·I_D verified for p ∈ {3, 7, 11}; Legendre table for p=7 correct.
- smoke: produced verdict PALEY_QUICKPROBE_PERFECT_ISOMETRY (as expected) in 0.1 s with metrics.json validated.

## Dependencies

- Reuses `moments_to_free_cumulants_general`, `mp_reference_cumulants`, `spectral_moments` from `experiments/exp_wave14_kappa_n_profile_v1.py` (existing, tested).
- No new framework code; no torch.

## Notes for runner

- Pure CPU (numpy SVD on 510x1020 bipolar; LAPACK).
- Self-contained; no remote codebook files needed.
