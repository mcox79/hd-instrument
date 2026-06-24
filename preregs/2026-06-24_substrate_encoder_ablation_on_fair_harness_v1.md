# Pre-reg: substrate_encoder_ablation_on_fair_harness_v1

Date filed: 2026-06-24
Filed-by: exp_dev
Trigger: notes/exp_dev_handoff_research_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md (Research rank 1)
Cell: experiments/exp_substrate_encoder_ablation_on_fair_harness_v1.py

## Purpose

Resolve the 3-cell-replicated 7.2268 vs fair_harness 7.3065 finding. Two
numbers measure DIFFERENT QUANTITIES on DIFFERENT METHODOLOGIES, not a real
+0.08 BPC lift. Research drill identified three candidate factors:
  1. encoder family (word2vec sparse-bipolar f=0.05 vs char-trigram dense)
  2. ctx-unk filter (fair_harness masks ctx==<unk>; cleanup-cells does not)
  3. alpha-Laplace smoothing on unigram floor (fair=0.1, cleanup=+1.0)

This cell ablates each axis on a single unified pipeline, using the
fair_harness scaffolding (rank-1 Hebbian; joint (T,lambda) sweep on dev) for
all 5 arms. Same encoder pool; same held positions; same eval; only the
4-tuple (encoder, sparsify, filter, alpha) varies per arm.

Substrate-product reading: if char-trigram dense (arm C) reproduces 7.22
under the fair_harness filter, the canonical chain-grade rail moves from
7.30 to 7.22 and all cf-RPE / STDP / heterogeneous-plasticity deltas must
be re-tiered.

## Arms (5 arms, single seed=7)

| Arm | Encoder | Sparsify | Filter ctx==unk | Alpha-Laplace | Predicted BPC |
|-----|---------|----------|------------------|----------------|----------------|
| A_FAIR_HARNESS_ASSHIPPED         | word2vec     | YES (f=0.05) | YES | 0.1 | 7.30 (sanity rail) |
| B_W2V_DENSE_NO_SPARSIFY          | word2vec     | NO           | YES | 0.1 | 7.15-7.25 |
| C_CHAR_TRIGRAM_DENSE_FAIR_FILTER | char-trigram | NO           | YES | 0.1 | 7.18-7.25 (DECISIVE) |
| D_W2V_SPARSE_NO_FILTER           | word2vec     | YES (f=0.05) | NO  | 0.1 | 7.32-7.36 |
| E_CHAR_TRIGRAM_NO_FILTER_ALPHA1  | char-trigram | NO           | NO  | 1.0 | 7.22 (sanity rail) |

## Pre-registered HARD bands (PRE-REGISTERED BEFORE RUN; do NOT adjust after seeing data)

HARD_PASS_METHODOLOGY_RESOLVED:
  Sanity rail A within +/- 0.05 of 7.3065 (provenance fair_harness)
  AND sanity rail E within +/- 0.05 of 7.2268 (provenance cleanup-cells)
  AND arm C within +/- 0.05 of EITHER 7.22 OR 7.30
  => methodology gap fully attributed; canonical rail decided by whichever
  end-point C lands on.

CHAIN_GRADE_BONUS_RAIL_FLIP:
  arm B BPC <= 7.25
  => removing f=0.05 sparsification yields a free lift; canonical rail
  moves to ~7.20 and cf-RPE / STDP / heterogeneous-plasticity claims re-tier.

MIDDLE_BAND:
  Both sanity rails reproduce but arm C lands in [7.25, 7.30] (strictly
  between rails, beyond +/-0.05 of either) => filter + encoder share
  attribution; no clean rail flip.

HARD_FAIL (any of):
  EITHER sanity rail diverges from its reference by > 0.10
  OR arm C outside [7.18, 7.35]
  => either harness bug (cannot conclude) or 4th unidentified factor
  (W normalization, batch precision, dtype) ... action = drill again

## Config (FULL run)

- N_DIM = 8192
- N_TRAIN = 100_000 tokens, N_HELD = 20_000 tokens
- VOCAB_CAP = 4000
- text8 corpus (data/text8_cache/text8.txt)
- TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- MRR_K = 10
- seeds = [7]
- Rank-1 Hebbian W; joint (T, lambda) sweep on dev half; report on test half
- Routing: remote_cpu_queue (pure numpy; PROT-020 avoidance)

## Why single seed is sufficient

- Deterministic encoder pipelines (word2vec via gensim cache; char-trigram via blake2b seeds)
- Sanity rails A and E act as their own cross-check against historical references
- Research drill: "cv low because deterministic encoder pipelines"

## What this cell does NOT show

- It does NOT claim a substrate-as-LM advance; it ATTRIBUTES a prior
  methodology delta to one of three axes.
- It is a CALIBRATION cell, not a science cell.
- Downstream cf-RPE / STDP / heterogeneous-plasticity TIERING is the
  consumer of this result, not the cell's own claim.
- The 7.2268 ARM_BASELINE_NO_CLEANUP finding from multi-iter / tanh /
  cue_clamped is REPLICATED here under arm E; this cell only resolves
  whether the gap to 7.3065 is encoder, filter, or alpha.

## Cites

- notes/research_surprise_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md
- notes/exp_dev_handoff_research_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md
- experiments/exp_fair_harness_substrate_as_lm_v1.py (fair-harness canonical 7.3065)
- experiments/exp_substrate_multi_iteration_cleanup_LM_v1.py (cleanup-cells 7.2268)
- experiments/exp_substrate_continuous_tanh_attractor_dynamics_v1.py (7.2332 N=4096)
- experiments/exp_substrate_iterative_cleanup_cue_clamped_production_v1.py (7.2268)

## Disciplines applied

- ASCII-only
- Fix #28: per-arm metrics ONLY in verdict; no cross-arm framing in verdict_msg
- A5: path-scoped commit (no `git add -A`)
- Pre-reg filed BEFORE smoke run
- PROT-018: no _nN suffix in anchor; N_DIM stated above
- PROT-020: pure numpy -> remote_cpu_queue (not GPU)
- WHAT_THIS_DOES_NOT_SHOW clause in detail
