# Pre-registration: substrate_k_module_compose_RESCUE_v1

**Filed:** 2026-06-23
**Anchor:** substrate_k_module_compose_RESCUE_v1
**Script:** experiments/exp_substrate_k_module_compose_RESCUE_v1.py
**Queue:** overnight_queue (GPU)

## Scientific question

Prior cell substrate_k_module_heterogeneous_compose_LM_v1 returned INSTRUMENTATION_SUSPECT.
Root cause: m2_ok=false on all 3 seeds -- lock-in encode module silently raised exception,
fell back to `logits_m1.copy()`, so ARM_M1_PLUS_LOCKIN and ARM_K_MODULE_FULL_HETERO both
got M1+M1 (identical logits). Log-linear combine of identical distributions selects lambda=0
(pure unigram wins), collapsing all multi-module arms to 7.7378 (bit-exact unigram).

This rescue applies 5 session-discovered fixes to test the genuine K-module hypothesis:
  Fix 1: amplitude scaling 1/sqrt(f) on ALL sparse-bipolar entries (viability shotgun P2)
  Fix 2: sigmoid-additive compose NOT multiplicative (shotgun P6: mult collapses 100x)
  Fix 3: K=2 banks (K-bank shotgun: K*=2 gives +1.07 BPC lift at smoke scale)
  Fix 4: cf-RPE delta rule per bank (dopamine-gated writes on positive surprise)
  Fix 5: logit copy-through guard (abort with INSTRUMENTATION_SUSPECT if modules are copies)

## Configuration

- N_DIM = 8192 (production; matches fair_harness)
- N_TRAIN = 100,000 text8 tokens
- N_HELD = 20,000 tokens
- VOCAB_CAP = 4000
- SEEDS = [7, 17, 23]
- K_BANKS = 2, N_PER_BANK = 4096
- SPARSE_BIPOLAR_F = 0.02 (f=0.02 optimal from viability P2)
- AMPLITUDE_SCALE = 1/sqrt(0.02) = 7.0711
- CFRPE_LR = 0.01, running_mean_alpha = 0.05
- Device: CUDA (overnight_queue GPU)

## Arms

1. ARM_BASELINE: sparse-bipolar f=0.02, amplitude-scaled, rank-1 Hebbian W. Reference arm.
2. ARM_SPARSE_BIPOLAR_AMPLITUDE_CORRECT: alias for ARM_BASELINE (provenance verification).
3. ARM_K2_MODULES: K=2 banks, Hebbian W per bank, sigmoid-additive compose.
4. ARM_K2_PLUS_CFRPE: K=2 banks + cf-RPE delta rule per bank.
5. ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE: K=2 + cf-RPE + explicit sigmoid-additive
   gate using cf-RPE prediction confidence as gate input (LOAD-BEARING ARM).

## Pre-registered hard bands (IMMUTABLE)

HARD_PASS: ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE BPC lift >= +0.30 bits vs
           ARM_BASELINE AND cv <= 0.05
CHAIN_GRADE_BONUS: lift >= +0.50 bits (Levy-Horn-Ruppin N^M factorial escape)
MIDDLE_BAND: lift +0.10 to +0.30 bits
HARD_FAIL: lift <= +0.10 bits OR any compose arm collapses to unigram BPC

SANITY RAILS:
  ARM_BASELINE within +/- 0.005 of fair_harness reference 7.3065
  Any arm with bpc within 0.005 of unigram -> INSTRUMENTATION_SUSPECT (not HARD_FAIL)

## Empirical drivers

- Prior cell INSTRUMENTATION_SUSPECT confirmed K-module compose is UNTESTED (not DEAD)
- Viability shotgun P2: 1/sqrt(f) scaling is binary LIVE/DEAD (6% vs 99% recall at f=0.02)
- Viability shotgun P6: sigmoid-additive gate_mean=0.805 vs multiplicative 0.12; +0.37 BPC
- K-bank shotgun: K=2 gives +1.07 BPC lift vs K=1 (N_TOTAL=2048 smoke scale)
- Levy-Horn-Ruppin 1997: N^M combined capacity with M independent modules

## Timeout estimate

Smoke wall: measured during smoke run (see below).
Formula: timeout_s = ceil(1.5 * smoke_wall_s * (100000/3000)^1.5 * (3/1))
         scaling_exp=1.5 (matmul-bound but less than O(N^2) since batched)
         FULL_N/smoke_N ~ N_TRAIN ratio = 33x; seeds = 3x vs 1x smoke
Estimate: ceil(1.5 * 180 * 33^1.5 * 3) = ceil(1.5 * 180 * 189 * 3) = ceil(152,730) -> capped
Note: prior cell took 902s for 3 seeds at same N_DIM. 5 arms vs 5 prior arms.
Empirical estimate: 5 arms * 300s per arm per seed * 3 seeds = 4500s. Add 50% margin = 6750s.
Timeout: 7200s (2 hours; flagged as long run). Under the 4h limit.

## Smoke

Smoke config: N_DIM=512, N_TRAIN=3000, N_HELD=600, VOCAB_CAP=400, SEEDS=[7], smoke=True.
Smoke results logged below after run.

## Fix #28 per-arm note

Read metrics.json per-arm BEFORE any tier/framing claim.
Do NOT propagate cross-arm narrative from verdict_msg alone.

## WHAT_THIS_DOES_NOT_SHOW

- Not testing K>2 (K-bank shotgun shows K=2 optimal at N=2048; may differ at N=8192)
- Not testing N_DIM > 8192 (GPU memory budget at K=2 banks)
- Not testing super-additivity beyond K=2 banks
- Not testing cf-RPE with learned gate (gate here is from embedding norms / prediction confidence)
- Not testing any inter-module routing beyond sigmoid-additive interpolation
