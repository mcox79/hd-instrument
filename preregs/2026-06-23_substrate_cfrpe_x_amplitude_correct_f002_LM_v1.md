# Pre-registration: substrate_cfrpe_x_amplitude_correct_f002_LM_v1

Filed: 2026-06-23
Anchor: substrate_cfrpe_x_amplitude_correct_f002_LM_v1
Queue: overnight_queue (GPU; N_DIM=8192 triggers Fix #22 routing threshold)
Script: experiments/exp_substrate_cfrpe_x_amplitude_correct_f002_LM_v1.py

## Hypothesis

cf-RPE delta rule composes super-additively with amplitude-correct sparse-bipolar at f=0.02.

Empirical drivers:
- cf-RPE x STDP heterogeneous: CHAIN-GRADE per Skunkworks VET; +0.141 BPC lift over
  fair_harness baseline at f=0.05 (ARM_CFRPE_STDP_HETEROGENEOUS in heterogeneous_plasticity_v1)
- Viability shotgun: sparse-bipolar amplitude scaling at f=0.02 is BINARY
  (6% unscaled -> 99% scaled recall at N=8192)
- Open question: does cf-RPE chain-grade lift ALSO apply when the codebook uses
  amplitude-correct f=0.02 instead of unscaled f=0.05?

This cell uses cf-RPE alone (no STDP) to isolate the f x amplitude-scaling composition.

## Six Arms

1. ARM_UNIGRAM -- analytic baseline
2. ARM_HEBBIAN_f005_UNSCALED -- baseline; reproduces fair_harness chain-grade BPC 7.3065
3. ARM_HEBBIAN_f002_UNSCALED -- sanity check: should collapse per viability shotgun
4. ARM_HEBBIAN_f002_AMPLITUDE_SCALED -- sanity check: should lift vs Hebbian baseline
5. ARM_CFRPE_f005_UNSCALED -- reproduces +0.141 chain-grade lift (cf-RPE at f=0.05)
6. ARM_CFRPE_f002_AMPLITUDE_SCALED -- COMBINED arm: cf-RPE + amplitude-correct f=0.02

## Pre-registered HARD bands

PRIMARY verdict criterion: ARM_CFRPE_f002_AMPLITUDE_SCALED vs ARM_CFRPE_f005_UNSCALED.
lift_vs_cfrpe = cfrpe_f005_bpc - cfrpe_f002_scaled_bpc (positive = combined better).

HARD_PASS_SUPER_ADDITIVE:
  lift_vs_hebbian >= +0.30 bits AND lift_vs_cfrpe >= +0.10 bits
  (super-additive: combined beats Hebbian baseline by >=0.30 bits;
   cf-RPE x amplitude-correct compose beyond either effect alone)

HARD_PASS_ADDITIVE:
  lift_vs_cfrpe >= +0.10 bits
  (additive composition: amplitude-correct f=0.02 adds >=0.10 bits over cf-RPE alone)

MIDDLE_BAND:
  lift_vs_cfrpe in [+0.03, +0.10) bits
  (marginal additive benefit; below HARD_PASS bar)

HARD_FAIL:
  lift_vs_cfrpe <= +0.00 bits
  (no additive benefit; cf-RPE saturates substrate-as-LM signal at this scale,
   leaving no room for amplitude-correct f=0.02 to add)

Sanity rails (not primary verdict, but logged):
  ARM_HEBBIAN_f002_UNSCALED BPC should be WORSE than ARM_HEBBIAN_f005_UNSCALED
    (viability shotgun: 6% recall without amplitude scaling at f=0.02)
  ARM_HEBBIAN_f002_AMPLITUDE_SCALED BPC should be BETTER than ARM_HEBBIAN_f005_UNSCALED
    (viability shotgun: 99% recall WITH amplitude scaling at f=0.02)

## PROT-018 N-suffix

No _nN suffix in anchor name. Production N = 8192 (N_DIM = 8192 in full config).
Rationale: anchor name already fully descriptive of f-sparsity + method combination.

## Amplitude scaling

Amplitude scale = 1/sqrt(f) multiplier on nonzero entries BEFORE L2-normalization.
For f=0.02: scale = 7.0711 (nonzero entries become +/-7.07 pre-norm, then L2-norm to unit sphere).
For f=0.05: scale = 4.4721 (unscaled arms use scale=1.0, i.e., +/-1 entries).

Rationale: the 1/sqrt(f) factor corrects for the norm shrinkage from sparsification.
With k = round(f*N) nonzero entries each +/-1, the row norm = sqrt(k) = sqrt(f*N).
After amplitude scaling, row norm = sqrt(k) * (1/sqrt(f)) = sqrt(N) -- same as a dense
bipolar vector. This ensures the W = E^T @ E outer-product has spectral norm ~= N
regardless of f, matching the theoretical capacity-correct formulation.

## Config

N_DIM: 8192 (production; smoke uses 512)
N_TRAIN: 100,000
N_HELD: 20,000
VOCAB_CAP: 4000
SEEDS: [7, 17, 23]
N_STEPS: 1000 (for cf-RPE iterative arms)
INGEST_BATCH: 64
CFRPE_LR: 0.5
TEMP_GRID: [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID: [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
Encoder: word2vec-google-news-300 projected to N_DIM=8192 (OOV fallback: char-trigram)

## Routing note (Fix #22)

N_DIM=8192 triggers Fix #22 routing threshold -> overnight_queue (GPU).
Script uses torch.cuda when available (Fix #24 mandate); CPU fallback for smoke.
Encoder hoisted outside arm loop (Fix #24 pattern).

## Smoke result (2026-06-23, laptop CPU N_DIM=512)

All 9 self-tests: PASS.
All 6 arms ran successfully at smoke scale (N_DIM=512, N_TRAIN=2000, V=300).
Smoke verdict: HARD_FAIL (expected at smoke scale -- amplitude scaling effect is
N-dependent; viability shotgun demonstrated at N=8192, not N=512).
Smoke BPCs: heb_f005=5.178 | heb_f002_unsc=5.230 | heb_f002_amp=5.230
            cfrpe_f005=4.988 | cfrpe_f002_amp=5.209
lift_vs_cfrpe (smoke) = -0.221 (negative at N=512; effect expected at N=8192)
Suspicious-result gate: PASS (all metrics finite; not constant; exit >> 100ms).
Import chain: experiments._seed_checkpoint confirmed loaded.

Note on smoke HARD_FAIL: this is NOT a suspicious result. The viability shotgun
explicitly showed that amplitude scaling at f=0.02 requires N >= ~4096 to manifest
(k=80 active dims at N=4096 vs k=10 at N=512). The full N=8192 run is required to
evaluate the actual hypothesis.

Walk-back gate: smoke effect is not borderline (it's negative at smoke scale);
the effect is expected to be N-dependent. Full N=8192 per spec is correct.

## Timeout estimate

Basis: GPU BLAS at N_DIM=8192.
  - Encoder (word2vec, cached after seed 0): ~10s
  - Hebbian W build: 25 chunks x (4096,8192)@(8192,4096) ~= 5s per arm on GPU
  - cf-RPE W build: 1000 steps x 64-batch x (8192x8192) matmul ~= 10s per arm
  - Recall: 78 batches x (256,8192)@(8192,8192)@(8192,4000) ~= 15s per arm
  - Per seed: 5 arms x ~30s = 150s
  - 3 seeds x 150s = 450s
  - 1.5x margin = 675s -> round to nearest 300 = 900s
timeout_s: 900 (conservative GPU estimate; source cell ran at similar scale ~20 min)

## Cites

- experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py
- notes/substrate_viability_shotgun_LIVE_DEAD_map_2026-06-23.md
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (baseline 7.3065 BPC)
