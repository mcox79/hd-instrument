# exp_dev -> queue: Composition A v5 RM(1, m) disambiguation chain (2026-05-24)

Two anchors chained to disambiguate v4's RM(1, m) rho=0.40 result: was it the
spectrum-only fallback (v3/v4 only loaded iterates for srht/hadamard) or a
genuine property of RM(1, m)?

- **Anchor 1** generates the 15 missing RM(1, m) VAMP iterate trace files at
  Cap 8 protocol shape (N=4096, 3 alphas, 5 seeds).
- **Anchor 2** re-runs the Composition A audit with REAL iterates for ALL of
  {srht, hadamard, rm_1_m} via a multi-root loader and an expanded
  ITERATE_ELIGIBLE set. RM(1, m) is now in the iterate gate (the point).

## Smoke results (pre-ship)

- Anchor 1: PASS (verdict=CAP8_RM_ITERATES_GENERATED, 1 file written at N=64).
- Anchor 2: PASS (verdict=COMPA_AUDIT_INCONCLUSIVE as expected on smoke;
  self-tests passed -- multi-root loader, rm_1_m in ITERATE_ELIGIBLE,
  iid-Gauss x Schur-Weyl mass_(2,) = 1.000000 matches MP exactly).

## Queue routing

Both anchors are pure-numpy CPU (the only torch usage is to materialise the
Sylvester Hadamard in `build_rm_1_m` -- no CUDA). Anchor 1 ETA 10-15 min,
Anchor 2 ETA 30-45 min. Both > 60s, so neither is local_cpu_queue eligible.
Per Tier B (remote CPU for longer non-CPU work), both ship to
`remote_cpu_queue`.

Anchor 2 depends on Anchor 1's output. v5 has `iterate_wait_seconds=1200`
which gives Anchor 1 up to 20 min runway if v5 starts before Anchor 1
finishes.

| queue            | name                                       | script                                                       | prereg                                                              | timeout(s) |
|------------------|--------------------------------------------|--------------------------------------------------------------|---------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_cap8_vamp_iterates_rm_1_m_v1        | experiments/exp_wave14_cap8_vamp_iterates_rm_1_m_v1.py       | preregs/2026-05-24_wave14_cap8_vamp_iterates_rm_1_m_v1.md           | 1800       |
| remote_cpu_queue | wave14_cap12_cap8_audit_trail_pipeline_v5  | experiments/exp_wave14_cap12_cap8_audit_trail_pipeline_v5.py | preregs/2026-05-24_wave14_cap12_cap8_audit_trail_pipeline_v5.md     | 3600       |
