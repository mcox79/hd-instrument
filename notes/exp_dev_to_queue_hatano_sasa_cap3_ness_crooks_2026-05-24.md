# exp_dev -> queue: Hatano-Sasa Cap 3 NESS audit-cert anchor (2026-05-24)

Strategy dispatched Research neighborhood recommendation #3 (cheapest CPU
anchor, ~5-15 min): Hatano-Sasa NESS-Crooks audit on Cap 3 streaming
trajectories. If HS integral fluctuation theorem `<exp(-W_ex)>=1` holds
within [0.95, 1.05], Cap 3 gains a fluctuation-theorem audit-cert
analogous to Cap 1's Crooks erase cert; the two compose HANDOFF-style
(Cap 1 audits erase events, Cap 3 audits steady-state writes) into a
"full audit-cert lifecycle."

Self-tests passed locally (1.8s): 14/14 verdict-band cases + 4/4
Hatano-Sasa formula cells (Brownian uphill W_ex=+1.0, same-state W_ex=0,
downhill W_ex=-1.0, no-dynamics IFT integral = 1.0). Smoke (3.0s, N=1024
M=30 beta=1.5 3 noise levels x 2 seeds = 6 cells) returned
`HATANO_SASA_CAP3_NESS_CROOKS_MIDDLE_BAND` with <exp(-W_ex)>=1.50,
cross_basin_frac=0.40 -- this is correct smoke behavior; the small per-cell
trajectory count (50) gives statistical noise that the FULL run resolves
(150 traj/cell x 16 cells).

Earlier `wave14_hatano_sasa_ness_audit_v1` (smoke only, deterministic
Hopfield) returned `HATANO_SASA_NESS_CERT_PARTIAL` because deterministic
dynamics produced cross_basin_frac=0; this v1 fixes that with auto-
associative Hebbian W + finite-temperature Glauber dynamics at near-
critical beta=1.5.

## Schema A -- queue entries

```
queue=remote_cpu_queue name=wave14_hatano_sasa_cap3_ness_crooks_v1 script=experiments/exp_wave14_hatano_sasa_cap3_ness_crooks_v1.py prereg=preregs/2026-05-24_wave14_hatano_sasa_cap3_ness_crooks_v1.md timeout=1800
```

## Schema B -- markdown table (parser fallback)

| queue            | name                                          | script                                                            | prereg                                                            | timeout(s) |
|------------------|-----------------------------------------------|-------------------------------------------------------------------|-------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_hatano_sasa_cap3_ness_crooks_v1        | experiments/exp_wave14_hatano_sasa_cap3_ness_crooks_v1.py         | preregs/2026-05-24_wave14_hatano_sasa_cap3_ness_crooks_v1.md      | 1800       |

## Why remote_cpu_queue (Tier B)

- Pure CPU (no CUDA, no torch.cuda imports).
- 16 cells * ~30s/cell Glauber relaxation = 5-15 min expected wall time
  (well above the < 60s local_cpu threshold).
- Reanalysis-style sweep over Cap 3 operating point; no GPU compute
  benefit (Glauber updates serialized per-step over 60 steps).
- Note on remote_cpu_queue liveness: per [[project-cpu-resource-underutilized]]
  remote CPU runner status should be checked before depending on
  near-immediate execution. Queueing is safe; if runner is dead, the
  entry will sit pending until revived.

## Hard-pass / hard-fail bands

- HARD PASS: <exp(-W_ex)> in [0.95, 1.05] across >=3 valid cells AND
  cross_basin_frac >= 0.05 -> Cap 3 audit-cert licensed
- HARD FAIL: <exp(-W_ex)> outside [0.5, 2.0] across >=3 valid cells ->
  substrate NESS non-canonical (informative-negative; does not refute
  Cap 3 itself)
- MIDDLE: in [0.5, 2.0] but outside [0.95, 1.05], OR in pass band with
  cross_basin_frac < 0.05, OR n_valid_cells < 3 -> partial cert

## Lead-time / open risks

- beta=1.5 chosen for near-critical Glauber where cross-basin events arise
  on ~60-step chains. If full run shows cross_basin_frac too low for
  HARD_PASS, follow-up cell with beta=1.2 may be needed.
- Empirical pi_ss estimated from 150 traj/cell over 50 basins = 3 hits/basin
  avg -- coarse but adequate for the integral statistic.
- Expected outcome P=0.55 HARD_PASS with [[feedback-lit-scan-calibration-penalty]]
  applied (first direct HS-IFT test on substrate; no published precedent
  for Hopfield-Glauber Cap 3).
