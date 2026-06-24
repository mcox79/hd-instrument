# Prereg: substrate_serotonin_mode_switch_bank_select_LM_v1

Date: 2026-06-23
Author: exp_dev
Gap: #3 from substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md

## Hypothesis

Serotonin as MODE-SWITCH (bank selector) not gain-modulation. Brain (Drosophila MB) uses
compartment-selective DAN modulation: gate selects WHICH memory bank to access, not HOW
MUCH to amplify. 4 parallel W banks x N_DIM_BANK=2048 = same parameter budget as single W
at N_DIM=8192. Feature-gated routing should outperform random routing and single-bank.

P_inherited = 0.55 (Drosophila MB compartments canonical) deflated to 0.45 for substrate LM.

## Config

- anchor: substrate_serotonin_mode_switch_bank_select_LM_v1
- queue: remote_cpu_queue (PURE NUMPY -- no torch -- avoids PROT-020 GPU routing)
- N_DIM=8192 (single-bank), N_DIM_BANK=2048 x N_BANKS=4 (multi-bank; same budget)
- N_TRAIN=100k, N_HELD=20k, VOCAB_CAP=4000
- seeds=[7, 17, 23]
- encoder: char-trigram (pure numpy; per-bank diversity via distinct seeds)
- Hebbian W build: rank-1 outer-product, chunked
- gate: Hebbian co-occurrence with bank-utility proxy (argmax selection at recall)
- BPC: joint (T, lambda) sweep; T in [0.01..1.0], lambda in [0.0..1.0]

## Arms

1. ARM_UNIGRAM -- analytic floor
2. ARM_SINGLE_BANK -- one W at N_DIM=8192
3. ARM_4_BANK_RANDOM_SELECT -- 4 banks x N_DIM_BANK=2048; random bank per token
4. ARM_4_BANK_FEATURE_GATED_SELECT -- 4 banks; gate selects based on input feature

## Pre-registered bands (HARD)

Pre-registered before any full run. Smoke verdict (2026-06-23): MIDDLE_BAND (lift=0.050 at
N_TRAIN=2000/N=512 smoke scale; 1-seed).

HARD_PASS: feature_gated_bpc < single_bank_bpc - 0.10 bits (mode-switch outperforms)
CHAIN_GRADE_BONUS: lift >= 0.20 bits AND feature_gated beats random by >= 0.10 bits
MIDDLE_BAND: feature_gated beats single_bank by +0.03 to +0.10 bits
HARD_FAIL: feature_gated <= single_bank + 0.03 bits (mode-switch does NOT help)
CV_MAX: cv < 0.05

## Walk-back gate

Smoke effect size (d = lift/std): smoke ran 1 seed, lift=0.050. At full scale (3 seeds,
N_TRAIN=100k), if the effect is BORDERLINE (lift < 1.5x HARD_PASS threshold = 0.15), the
verdict_handler should flag for FULL sample size doubling (N_TRAIN=200k, seeds=5).

## Smoke results (pre-registered before queue_add)

mode=smoke N_DIM=512 N_DIM_BANK=128 seed=0 N_TRAIN=2000
gated_bpc=4.9448 single_bpc=4.9948 random_bpc=5.0399 unigram_bpc=5.0133
lift_vs_single=0.0500 lift_vs_random=0.0951
verdict=MIDDLE_BAND wall_time=0.8s

Note: smoke is at tiny scale; FULL scale (N_TRAIN=100k, N_DIM=8192) expected to shift
result -- per brain-existence-proof prior, feature-gating benefit grows with N and training data.

## References

- Aso, Hattori 2014: Drosophila MB compartments; DAN-gated synaptic plasticity by compartment
- Cohn, Modi, Owald, Waddell 2015: compartment-selective memory assignment in MB
- data/exp_substrate_neuromodulator_3axis_gated_compose_LM_v1/metrics.json (READOUT_DEGEN)
- notes/substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md (GAP #3)
- USER_2026-06-23_path_c_substrate_owned_encoder
- USER_2026-06-23_brain_existence_proof_higher_prior
