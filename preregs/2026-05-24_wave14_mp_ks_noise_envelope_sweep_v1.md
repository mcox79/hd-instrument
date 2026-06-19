# Pre-registration: wave14_mp_ks_noise_envelope_sweep_v1 (Cap 12 ✅ E1' noise-envelope mapping)

**Date**: 2026-05-24
**Wave**: 14 (MP-KS pre-flight diagnostic)
**Driver**: verdict_handler pre-registered follow-up to E1 MIDDLE-BAND verdict
**Capability under stress**: Cap 12 (AMP-vs-VAMP inference routing infrastructure) at ✅
**Anchor role**: E1' — noise-envelope sweep (map eta_critical at fixed tau=0.20)
**Script**: `experiments/exp_wave14_mp_ks_noise_envelope_sweep_v1.py`
**Queue**: `remote_cpu_queue`
**ETA**: 30-45 min (5 codebooks × 5 seeds × N=1024 × 6 eta values; ~2× E1 cost)

## Hypothesis

E1 (`exp_wave14_mp_ks_noisy_substrate_v1`) tested a SINGLE noise level (eta=0.10) at three tau values. The verdict_handler landed E1 in the MIDDLE-BAND and pre-registered this follow-up sub-probe: instead of sweeping tau at fixed eta, FIX tau=0.20 (the v175 / E1 anchor) and SWEEP eta to map the noise envelope.

Concrete question: at what eta_critical does Cap 12 routing accuracy first drop below 4/5? Knowing this lets the substrate-product claim be sharpened from the current "robust to 10% noise (middle band)" to a precise "robust to eta <= eta_critical" envelope statement.

## Bands (HARD PASS / HARD FAIL / MIDDLE BAND)

Per [[feedback-envelope-expansion-fail-bands]], all three bands pre-registered verbatim before queue submission.

### HARD PASS — Cap 12 ✅ envelope extends to eta <= 0.05

Routing accuracy >= 4/5 at eta = 0.05 AND at all smaller eta in the grid (i.e. >= 4/5 at eta ∈ {0.0, 0.01, 0.025, 0.05}).

Substrate-product claim: "Cap 12 tolerates noise up to eta = 5% before degrading." (Production matrix noise is almost always below 5%; this is a substantive envelope.)

### HARD FAIL — Cap 12 ✅ reverts to 🟢 with clean-only annotation

Routing accuracy < 4/5 at eta = 0.01 (capability breaks immediately on any meaningful noise).

Substrate-product claim collapses to "clean-only routing"; the v175 ✅ promotion was an artifact of clean-codebook conditions.

### MIDDLE BAND — narrow noise tolerance window (1% < eta_critical < 5%), ✅ with annotation

Routing accuracy >= 4/5 at eta = 0.01 but < 4/5 at eta = 0.05. Envelope is positive but narrow.

Substrate-product claim: "Cap 12 ✅ stands with explicit noise-envelope annotation: routes correctly up to eta_critical ∈ (0.01, 0.05); Strategy may dispatch finer grid to pin the threshold."

## Design

- Sweep eta ∈ {0.0, 0.01, 0.025, 0.05, 0.075, 0.10}.
- For each eta: same v174/v175/E1 protocol (5 codebooks × N=1024 × M/N=1.0 × 5 seeds × n_iter=300) at fixed tau=0.20.
- For each (eta, codebook, seed):
  1. Build clean W (M × N) via codebook builder (seed_val = seed * 1000 + 17).
  2. Apply per-entry sign-flip noise with probability eta:
     mask = rng.random(W.shape) < eta; signs = where(mask, -1, +1); W_noisy = W * signs.
     Noise seed = seed_val + 50_000 + round(eta * 1_000_000) — independent draws per eta cell, reproducible.
  3. SVD of W_noisy.
  4. Compute MP-KS statistic on noisy eigenvalues.
  5. Build noisy signal y = W_noisy @ x_true + observation_noise (sigma=0.1).
  6. Run AMP and VAMP loops on (W_noisy, y) for n_iter=300 each.
  7. amp_rel = |amp_emp - amp_se_pred| / max; same for vamp_rel.
  8. Empirical truth label: AMP_OK if amp_rel < 0.10 else VAMP_REQUIRED.
- Aggregate ks across 5 seeds per (codebook, eta); aggregate amp_rel / vamp_rel; pick empirical label from amp_rel_mean.
- For each eta: route_from_ks(ks_mean, tau=0.20); compare to empirical label per codebook; per_eta_correct ∈ {0..5}.
- Identify eta_critical = smallest eta in grid with per_eta_correct < 4. If none, eta_critical = ">0.100".
- Verdict from per_eta_correct against the three bands.

## Why this answers "where does routing break?"

The eta grid is dense at the low end (0, 0.01, 0.025) where customer noise typically lives, with coarser steps (0.05, 0.075, 0.10) covering the upper envelope and reconnecting to E1's single-point measurement at eta=0.10. The chosen grid resolves the boundary between "envelope to 5%" (HARD PASS) and "narrow envelope < 5%" (MIDDLE BAND) directly.

## Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

The script self-tests 13 formula assertions, all of which must pass before the experiment runs:

1. `apply_signflip_noise(W, eta=0)` returns W unchanged.
2. `apply_signflip_noise(W, eta=1)` returns -W.
3. `apply_signflip_noise(W_big, eta=0.025)` flip fraction in (0.018, 0.034).
4. `route_from_ks(ks, tau=0.20)` boundary: ks=0.20 → AMP_OK (<= boundary), ks=0.21 → VAMP_REQUIRED.
5. `empirical_truth_from_errs` boundary cases.
6. `identify_eta_critical` returns first sub-threshold eta (e.g. 0.050 when correct drops at eta=0.05).
7. `identify_eta_critical` returns `">0.100"` when no failure in grid.
8. `identify_eta_critical` returns `"0.000"` when even eta=0 fails.
9. `compute_verdict` on synthetic all-5/5 dataset → HARD PASS with eta_critical=">0.100".
10. `compute_verdict` on synthetic 0/5 at eta=0.01 → HARD FAIL with eta_critical="0.010".
11. `compute_verdict` on synthetic 3/5 at eta=0.05 → MIDDLE BAND with eta_critical="0.050".
12. `compute_verdict` on insufficient cells → INCONCLUSIVE.
13. ETA_GRID monotonic ascending and contains required pillars {0.0, 0.01, 0.05}.

All 13 pass locally before queue submission. Remote-side `--self-test` gate will re-run pre-execution.

## Acceptance criteria for queue submission

- [x] Script includes `sys.stdout.reconfigure(...)` block at top.
- [x] Script includes metrics-write block (`write_metrics` with atomic .tmp + rename).
- [x] Script includes env-var-driven `HDLAB_EXP_NAME` outdir.
- [x] Self-test runs at start of `run_main` (and `run_smoke`).
- [ ] Pre-run smoke at N=64 / 1-seed / 2-eta / 2-codebook completed locally; produced valid metrics.json.
- [x] HARD PASS / HARD FAIL / MIDDLE BAND verbatim in this prereg.
- [x] HARD_FAIL_ETA_FLOOR = 0.01, HARD_PASS_ETA_CEILING = 0.05 are CONSTANTS in the script (not magic numbers in compute_verdict).

## Pause-flag compliance

`data/orchestrator_paused.flag` ABSENT at dispatch time. exp_dev verified flag is not present before writing this prereg.

## Notes

- Inherits ALL machinery from `exp_wave14_mp_ks_noisy_substrate_v1.py` (signflip noise, MP-KS routine, AMP/VAMP loops, codebook builders) — only the sweep axis changes (eta sweep at fixed tau vs tau sweep at fixed eta).
- Noise realizations are independent per eta cell (eta_offset injected into noise seed). This ensures eta=0.025 is not a strict subset of eta=0.10's mask — they sample independently. For reproducibility, the same (codebook, seed, eta) triple always produces the same W_noisy.
- The eta=0.10 + tau=0.20 cell of THIS experiment partially overlaps with E1's eta=0.10 + tau=0.20 measurement (different noise seed offset due to grid-aware seeding); used as a cross-check against E1's MIDDLE-BAND finding.
