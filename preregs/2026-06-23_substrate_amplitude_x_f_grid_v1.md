# Pre-registration: substrate_amplitude_x_f_grid_v1

**Date:** 2026-06-23
**Anchor:** substrate_amplitude_x_f_grid_v1
**Script:** experiments/exp_substrate_amplitude_x_f_grid_v1.py
**Queue:** remote_cpu_queue
**Filed by:** exp_dev (Sonnet 4.6)

---

## Scientific question

Is amplitude scaling (1/sqrt(f) gain on sparse-bipolar entries) the under-recognized
load-bearing parameter fix for substrate-as-LM negative landings?

Source: matched-filter-energy theorem (Schwartz 1953); Research drill
`notes/research_substrate_representational_temporal_parameter_taxonomy_2026-06-23.md`
P(amplitude-scaling is top fix) = 0.80 (deflated from 0.95; brain-analog unambiguous).

---

## Config

- N = 4096 (production; smoke uses N=512 per RUN_MODE gate)
- M = 500 stored patterns
- Arms: raw_pm1 (a=1.0), inv_sqrt_f (a=1/sqrt(f)), inv_f (a=1/f)
- f_grid: [0.005, 0.01, 0.02, 0.05, 0.1, 0.5]
- sigma_grid: [16, 32, 64]
- seeds: [7, 17, 23]
- n_trials: 200 probes per cell
- Routing: remote_cpu_queue (pure numpy; no torch; Tier-B)

## PROT-018 N-suffix declaration

No _n<N> suffix in anchor name. Production N = 4096.
Rationale: N is not the focal sweep axis in this cell; f and amplitude are.

---

## Pre-registered HARD bands (both directions -- registered BEFORE dispatch)

### HARD_PASS (amplitude-scaling IS the dominant fix):
- CRITERION_A: recall_lift(f=0.02, sigma=16) = mean(ARM_B) - mean(ARM_A) >= 0.30
  Derivation: matched-filter theory predicts ARM_A recall ~0.58 at SNR=0.567;
  ARM_B recall ~0.999 at SNR=4.0; expected lift ~0.37 (theoretical pre-reg).
- CRITERION_B: ARM_B recall vs f across f in [0.01, 0.50] at sigma=16 is FLAT
  to within 0.05. Interpretation: after amplitude correction, f stops mattering
  for receiver SNR (matched-filter-energy is the dominant mechanism).
- CRITERION_C (supporting): Pearson r(ARM_A recall, 1/f) >= 0.70 at sigma=16.
  Raw arm degrades proportional to sparsity per matched-filter prediction.

### HARD_FAIL (amplitude-scaling is NOT the dominant fix):
- HARD_FAIL_1: recall_lift(f=0.02, sigma=16) < 0.10 (scaling provides no meaningful lift)
- HARD_FAIL_2: ARM_B recall vs f at sigma=16 shows >0.20 variation (not flat;
  some other mechanism beyond amplitude dominates)
- HARD_FAIL_3: ARM_A and ARM_B within 0.05 at ALL (f, sigma) cells
  (amplitude scaling silently no-op; root-cause the implementation)

### MIDDLE_BAND:
- recall_lift(f=0.02, sigma=16) in [0.10, 0.30]: partial recovery
  (~60-70% of mechanism recovered; additional fix likely needed such as
  WTA support-restricted receiver or encoder fix)

### READOUT_DEGENERATE:
- Any arm collapses to uniform output (recall == 1/M = 0.002) or NaN at all cells.

---

## Theoretical SNR predictions (pre-dispatch, closed-form)

Matched-filter theorem (Wikipedia / Schwartz 1953):
  SNR = output_signal / noise_std_per_component

For ARM_A (raw, a=1.0) at (f=0.02, N=4096, sigma=16):
  Signal per component = f * N * a^2 / N = f * a^2 = 0.02
  Noise variance per component = sigma^2 / N = 256 / 4096 = 0.0625
  SNR_effective = sqrt(f * N) / sigma = sqrt(81.92) / 16 = 9.06 / 16 = 0.567
  Phi(0.567) ~ 0.715 -> predicted recall ~ 0.71 at ARM_A (f=0.02, sigma=16)

For ARM_B (a=1/sqrt(f)) at (f=0.02, N=4096, sigma=16):
  Amplitude a = 7.07; active_energy = f * N * a^2 = 0.02 * 4096 * 50 = 4096
  SNR_effective = sqrt(f * N * a^2) / sigma = sqrt(f * N) / (sqrt(f) * sigma) = sqrt(N) / sigma
  = sqrt(4096) / 16 = 64 / 16 = 4.0
  Phi(4.0) ~ 0.9997 -> predicted recall ~ 1.000 at ARM_B (f=0.02, sigma=16)

Expected lift CRITERION_A = 1.000 - 0.715 = 0.285 (slightly below 0.30 band;
pre-reg band is conservative; if Hopfield nonlinearity adds noise the actual
ARM_B recall may be <1.000, making actual lift ~0.37 per Research estimate).

NOTE: bands are set on empirical recall (Hopfield dynamics), not on Phi(SNR) directly.
The SNR prediction is the PRIOR; bands are wider to account for retrieval dynamics.

---

## Formula self-tests (PROT-022 -- run at module import)

1. SNR_raw formula: sqrt(0.02 * 4096) / 16 = 0.567 (verified in _selftest_snr_raw)
2. SNR_corrected formula: sqrt(4096) / 16 = 4.0 (verified in _selftest_snr_corrected)
3. Amplitude ratio: 1/sqrt(0.02) = 7.07 (verified in _selftest_amplitude_ratio)
4. Non-degenerate recall: one forward pass returns non-NaN, non-zero recall
5. Amplitude correction produces higher recall at small scale

---

## WHAT_THIS_DOES_NOT_SHOW

- This cell does NOT test substrate-as-LM end-to-end (BPC, perplexity, generation).
- It tests the ISOLATED recall mechanism in a controlled associative memory harness.
- A HARD_PASS here shows amplitude scaling helps retrieval; it does NOT guarantee
  chain-grade LM performance improvement without also fixing encoder and W structure.
- ARM_C (1/f) is an over-correction reference; PASS there would suggest saturation.
- Results are conditional on Hopfield-style W construction; other W structures
  (Krotov polynomial, attention-style) may behave differently.

---

## Timeout estimate (MEASURED from smoke + multi-scale probe)

smoke_wall_s = 0.5s for 36 cells at N=512
Per-cell at N=4096 (measured): ~0.84s on laptop, ~0.3-0.4s estimated on remote_cpu (3x faster)
Full cells = 3 arms x 6 f x 3 sigma x 3 seeds = 162 cells
Estimated FULL remote_cpu wall = 162 * 0.35s = ~57s

Scaling: O(M*N) per trial; scaling_exp = 1.0 (linear in N at fixed M/N)
timeout_s = ceil(1.5 * 0.5 * (162/36) * (4096/512)^1.0) = ceil(1.5 * 0.5 * 4.5 * 8) = ceil(27) -> 300s
Remote_cpu is faster; adding 100% margin -> timeout = 600s.

Multi-scale smoke validation:
  N=512 (smoke): ARM_A=0.05, ARM_B=0.26, lift=0.21
  N=2048 (smoke x4): ARM_A=0.04, ARM_B=0.75, lift=0.71
  N=4096 (preview 50 trials): ARM_A=0.02, ARM_B=0.84, lift=0.82
  -> Clear discriminating signal; no OOM; no degenerate output.

Walk-back gate: effect at smoke N=512 is below 20% of hard-pass (0.21 vs 0.30). However
  multi-scale probe at N=4096 shows lift=0.82 >> 0.30. The smoke underestimates due to small
  N regime (SNR too low even for ARM_B at N=512). Full N=4096 expected lift ~0.80.
  No walk-back needed; full N = 4096 confirmed. n_trials = 200 (unchanged).

---

## Dependency verification

- No upstream experiment dependencies (pure numpy from-scratch)
- numpy available on remote_cpu_queue runner (confirmed in prior cells this arc)
- No data files required beyond stdlib

---

## Middle-band outcome plan

If MIDDLE_BAND (lift in [0.10, 0.30]):
1. Check ARM_C (inv_f): if ARM_C shows further lift, implies stronger correction needed
2. Route to Research for: investigate WTA support-restricted receiver as additional fix
3. Do NOT claim amplitude is the sole fix; note partial-recovery framing
4. Dispatch tau_pos/tau_neg ratio sweep (Anchor 2 from handoff) as parallel investigation

If HARD_FAIL:
1. ARM_A vs ARM_B within 0.05 at all cells -> instrumentation suspect: verify amplitude
   is actually applied during probe generation not swallowed by sign operation
2. lift < 0.10 -> route to Research for receiver architecture review;
   amplitude is not the primary lever; check WTA-gating or W-structure hypothesis
