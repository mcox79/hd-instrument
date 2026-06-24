# PRE-REG: substrate_n1_v3_readout_x_cfrpe_plasticity_compose_v1

Date: 2026-06-24
Owner: exp_dev
Anchor: `substrate_n1_v3_readout_x_cfrpe_plasticity_compose_v1`
Routing: overnight_queue (GPU)

## Strategic context (per Skunkworks VET 2026-06-23/24)

The chain-grade substrate-as-LM anchor `n1_concept_lm_substrate_native_token_decode_v3`
(cert row 588) attains top1=0.4455 (+61.6% over unigram_top1=0.2761) via a
**nearest-neighbor HD readout**: VQ tokens to concept codes, Willshaw single-step
recall of the next concept, then a per-concept word distribution from a Hebbian
decode memory D.

The latest cf-RPE plasticity landing
(`substrate_cfrpe_n_steps_curve_v1`, N=5000_cfrpe) attains top1=0.2438 (+12.3%
over unigram) via the **standard logit-mixer readout** (cosine-softmax over
word2vec-projected sparse-bipolar vocab).

5x lift-ratio gap. Skunkworks's diagnosis: cf-RPE plasticity improves STORED
representations but the standard logit-mixer readout does not extract the
gain. The chain-grade bottleneck is the READOUT, not the plasticity.

HYPOTHESIS: combining the n1_v3 readout with cf-RPE plasticity should compose
to BOTH advantages and produce super-additive lift.

## Cell design (4 arms x 3 seeds, N_DIM=8192, text8 V=4000, N_TRAIN=100k)

Encoder: SAME word2vec-google-news-300 projected to N_DIM=8192 sparse-bipolar
(f=0.05) used by fair_harness + cf-RPE chain-grade. Each arm fits FRESH W /
fresh substrate state; no cross-contamination.

Arms:

1. `ARM_UNIGRAM` — analytic floor (top1 + BPC + MRR).
2. `ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY` — n1_v3 readout (VQ -> concept ->
   sparse Willshaw concept transition -> decode-D word distribution) +
   one-pass Hebbian concept transition matrix W_C. Reproduces n1_v3 reference
   top1=0.4455 +/- 0.03 on text8 word-LM.
3. `ARM_LOGIT_MIXER_READOUT_CFRPE_PLASTICITY` — fair_harness logit-mixer
   readout (pred @ E.T -> joint T,lambda sweep) + cf-RPE iterative delta-rule
   plasticity over word-level W (N_STEPS=2000). Reproduces cf-RPE reference
   top1=0.2438 +/- 0.03.
4. `ARM_N1_V3_READOUT_CFRPE_PLASTICITY` — n1_v3 readout + cf-RPE plasticity
   applied to the concept-level transition matrix W_C (N_STEPS=2000). THE TEST
   ARM.

## Pre-registered HARD bands (TOP1 primary; BPC reported but not load-bearing
per META_HARNESS_RIGGED row 588)

Sanity rails (Fix #28 verify-the-referent on the composition components):
- ARM 2 top1 within +/- 0.03 of n1_v3 reference 0.4455 (provenance for n1_v3 readout).
- ARM 3 top1 within +/- 0.03 of cf-RPE reference 0.2438 (provenance for cf-RPE plasticity).

ARM 4 (N1_V3 x CFRPE) verdict bands:
- HARD_PASS: top1 >= 0.50 (super-additive lift over both knobs)
- CHAIN_GRADE_BONUS: HARD_PASS AND top1 >= 0.55 AND cv < 0.05 (substantial
  new chain-grade evidence; substrate-mine validates compositional readout x
  plasticity stacking).
- MIDDLE_BAND: top1 in [0.46, 0.50] (additive but not super-additive).
- HARD_FAIL: top1 <= 0.45 (no super-additive composition; n1_v3 readout
  dominates regardless of plasticity rule, i.e. the readout is the only
  load-bearing knob).

Stability rail: cv across seeds < 0.05 for all reported PASS configs.

Sanity rail (deflate): if EITHER provenance rail (ARM 2 / ARM 3) fails by >
0.03, demote the verdict to PROVENANCE_FAIL and treat the cell as DESIGN-
ERROR rather than substrate evidence (the components have to reproduce
before the composition can be interpreted).

## Methodology

- TEMP_GRID, LAMBDA_GRID: same as fair_harness / cf-RPE production
  (LAMBDA_GRID excludes 0.0 per META C7 anti-calibration-collapse).
- TOP1: predicted via argmax over the calibrated logit-mixer (ARMs 1/3) or
  argmax over D @ concept-code -> word (ARMs 2/4); calibrated with the SAME
  T, lambda joint sweep on dev half (no asymmetry across arms).
- BPC reported but interpreted with the row 588 caveat: cosine-softmax
  underestimates substrate confidence; the BPC may HARD_FAIL while top1
  cleanly clears bigram.
- cf-RPE: N_STEPS=2000 (top1 plateau per cf-RPE N_STEPS_curve audit;
  past-plateau steps may degrade per the row 587 curve).
- Concept-level cf-RPE: same delta-rule applied to (C[c_t+1] - C[c_t] @ W_C^T)^T @ C[c_t] / batch over concept transitions; N_STEPS=2000 on concept
  pairs (smaller than word vocab so faster per step).
- Substrate-only-decode invariant: ZERO LLM forward calls at inference.
  word2vec embedding lookup at ingest is NOT an inference-time LLM call.
- V_C=256 (matches n1_v3 reference); f=0.05 sparse bipolar matches
  fair_harness / cf-RPE encoders.
- SEEDS=[7,17,23] (matches both reference cells).

## What this does NOT show

- Generalization beyond text8 (single corpus).
- BPC chain-grade per row 588 methodology audit (BPC harness rigged in this
  regime; report but not load-bearing).
- Effect at N_DIM != 8192 or V != 4000.
- Composition with STDP or other plasticity rules (only cf-RPE).

## Discipline gates applied

- Fix #14: ONE cell.
- Fix #17: smoke + runtime measurement; cell-author smoke + dispatch on remote.
- Fix #28: per-arm metrics read directly from `metrics.json -> detail.by_arm_agg`;
  not from verdict_msg framings; the verdict logic computes a `provenance_check`
  flag from ARM 2 and ARM 3 top1 measurements.
- A5 role-separation: exp_dev produces, Skunkworks cert-grades.
- Substrate-only verified (zero LLM call counter at inference).
- C7: LAMBDA_GRID excludes 0.0 (anti-calibration-collapse).

## Cites

- `data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json` (n1_v3 reference; cert row 588).
- `experiments/exp_n1_concept_lm_substrate_native_token_decode_v3.py` (n1_v3 source).
- `data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json` (cf-RPE N=5000 reference).
- `experiments/exp_substrate_cfrpe_n_steps_curve_v1.py` (cf-RPE source).
- `experiments/exp_fair_harness_substrate_as_lm_v1.py` (logit-mixer readout + joint T,lambda sweep).
- `experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py` (cf-RPE plasticity source pattern).
- Skunkworks VET 2026-06-23 (chain-grade bottleneck is the READOUT not the plasticity).
- USER 2026-06-23 (META_HARNESS_RIGGED row 588; top1 is the load-bearing metric).
