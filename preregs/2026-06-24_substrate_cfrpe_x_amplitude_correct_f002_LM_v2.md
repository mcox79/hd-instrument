# Pre-registration: substrate_cfrpe_x_amplitude_correct_f002_LM_v2

Filed: 2026-06-24
Anchor: substrate_cfrpe_x_amplitude_correct_f002_LM_v2
Queue: overnight_queue (GPU; N_DIM=8192 triggers Fix #22 routing threshold)
Script: experiments/exp_substrate_cfrpe_x_amplitude_correct_f002_LM_v2.py

## Rescue rationale

v1 (substrate_cfrpe_x_amplitude_correct_f002_LM_v1) exhausted its 900s timeout without
completing. Root cause: 6 arms x 3 seeds x N_DIM=8192 x N_TRAIN=100k required more than
900s even on GPU. v2 rescues by:
  1. Dropping ARM_HEBBIAN_f002_UNSCALED (dead-zone sanity arm; expected to collapse per
     viability shotgun; not load-bearing for verdict computation; saves ~20% wall time)
  2. Increasing timeout_s from 900 to 3600 (4x headroom)
  No logic changes to any surviving arm.

## Hypothesis

cf-RPE delta rule composes super-additively with amplitude-correct sparse-bipolar at f=0.02.

Empirical drivers:
- cf-RPE x STDP heterogeneous: CHAIN-GRADE per Skunkworks VET; +0.141 BPC lift over
  fair_harness baseline at f=0.05 (ARM_CFRPE_STDP_HETEROGENEOUS in heterogeneous_plasticity_v1)
- Viability shotgun: sparse-bipolar amplitude scaling at f=0.02 is BINARY
  (6% unscaled -> 99% scaled recall at N=8192)
- Open question: does cf-RPE chain-grade lift ALSO apply when the codebook uses
  amplitude-correct f=0.02 instead of unscaled f=0.05?

## Five Arms (v2; ARM_HEBBIAN_f002_UNSCALED dropped vs v1)

1. ARM_UNIGRAM -- analytic baseline
2. ARM_HEBBIAN_f005_UNSCALED -- baseline; reproduces fair_harness chain-grade BPC 7.3065
3. ARM_HEBBIAN_f002_AMPLITUDE_SCALED -- sanity check: should lift vs Hebbian baseline
4. ARM_CFRPE_f005_UNSCALED -- reproduces +0.141 chain-grade lift (cf-RPE at f=0.05)
5. ARM_CFRPE_f002_AMPLITUDE_SCALED -- COMBINED arm: cf-RPE + amplitude-correct f=0.02

## Pre-registered HARD bands (same as v1)

PRIMARY verdict criterion: ARM_CFRPE_f002_AMPLITUDE_SCALED vs ARM_CFRPE_f005_UNSCALED.
lift_vs_cfrpe = cfrpe_f005_bpc - cfrpe_f002_scaled_bpc (positive = combined better).

HARD_PASS_SUPER_ADDITIVE:
  lift_vs_hebbian >= +0.30 bits AND lift_vs_cfrpe >= +0.10 bits

HARD_PASS_ADDITIVE:
  lift_vs_cfrpe >= +0.10 bits

MIDDLE_BAND:
  lift_vs_cfrpe in [+0.03, +0.10) bits

HARD_FAIL:
  lift_vs_cfrpe <= +0.00 bits

cv < 0.05 (mandatory sanity rail)

## PROT-018 N-suffix

No _nN suffix in anchor name. Production N = 8192 (N_DIM = 8192 in full config).
Rationale: anchor name already fully descriptive of f-sparsity + method combination.

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

## Smoke result (2026-06-24, laptop CPU N_DIM=512)

All 10 self-tests: PASS (ST10 confirms ARM_HEBBIAN_f002_UNSCALED absent).
All 4 plasticity arms ran successfully at smoke scale.
Smoke verdict: HARD_FAIL as expected (N-dependent effect; explained in v1 prereg).
Smoke BPCs: heb_f005=5.178 | heb_f002_amp=5.230 | cfrpe_f005=4.874 | cfrpe_f002_amp=5.160
lift_vs_cfrpe (smoke) = -0.286 (negative at N=512; effect expected at N=8192 only)
Smoke wall: ~40s; metrics all finite, no constant arms.
Suspicious-result gate: PASS.

## Timeout estimate

v1 exhausted 900s on GPU without completing. v2 estimate:
  v1 had 6 plasticity arms; v2 has 4 (dropped 1 from 5 remaining).
  Reduction: 4/5 = 0.80 of v1 wall time.
  v1 wall >= 900s; estimated true wall ~1200-1500s per GPU run at 5 arms.
  v2 at 4 arms: ~1200-1500 x 0.80 = 960-1200s.
  Safety margin 1.5x: ~1440-1800s -> round up to 2100s.
  Extra headroom for encoder load + checkpoint IO: 3600s (2x safety).
  timeout_s: 3600 (4x v1; well above estimated 1800s ceiling)

## Routing note (Fix #22)

N_DIM=8192 triggers Fix #22 routing threshold -> overnight_queue (GPU).
Script uses torch.cuda when available (Fix #24 mandate); CPU fallback for smoke.
Encoder hoisted outside arm loop (Fix #24 pattern).

## Cites

- preregs/2026-06-23_substrate_cfrpe_x_amplitude_correct_f002_LM_v1.md
- experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py
- notes/substrate_viability_shotgun_LIVE_DEAD_map_2026-06-23.md
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (baseline 7.3065 BPC)
