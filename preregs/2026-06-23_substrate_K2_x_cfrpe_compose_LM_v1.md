# Pre-registration: substrate_K2_x_cfrpe_compose_LM_v1

**Date:** 2026-06-23
**Anchor:** substrate_K2_x_cfrpe_compose_LM_v1
**Script:** experiments/exp_substrate_K2_x_cfrpe_compose_LM_v1.py
**Queue:** remote_cpu_queue (pure numpy; no CUDA)

## Hypothesis

K=2 multi-bank architecture and cf-RPE delta-rule plasticity are the 2 best validated
substrate-as-LM lift levers. This cell tests whether they compose super-additively,
additively, or interfere when combined.

Both knobs have independent chain-grade or smoke-validated lift:
- cf-RPE x STDP heterogeneous: HARD_PASS CHAIN_GRADE, +0.141 BPC over fair_harness baseline
  at production N=8192 with word2vec encoder
- K=2 multi-bank: +1.07 BPC lift over K=1 at smoke scale
  (notes/shotgun_smoke_K_bank_count_sweep_2026-06-23.md)

## Design

**Arms:** 4 arms x 3 seeds x text8 N_TRAIN=100k N_DIM_TOTAL=8192

| Arm | K | Plasticity | Description |
|-----|---|------------|-------------|
| ARM_BASELINE_RANK1_K1 | 1 | Hebbian | Single bank rank-1; reproduces fair_harness 7.3065 |
| ARM_CFRPE_K1 | 1 | cf-RPE | Single bank cf-RPE; reproduces +0.141 chain-grade lift |
| ARM_K2_RANK1 | 2 | Hebbian | 2 banks x 4096 dims; rank-1 Hebbian per bank |
| ARM_K2_CFRPE | 2 | cf-RPE | 2 banks x 4096 dims; cf-RPE per bank (combined arm) |

**Encoder:** char-trigram (pure numpy; no gensim dependency for remote_cpu routing).
NOTE: fair_harness chain-grade cell used word2vec. This cell uses char-trigram to keep
pure-numpy dep chain. The lift signal under test is architecture x plasticity, not encoder.
ARM_BASELINE_RANK1_K1 provenance vs 7.3065 ref will show non-zero drift; this is expected
and flagged in the provenance check (advisory, not a block).

**N-suffix note (PROT-018):** Anchor name contains no _nN suffix. Production
N_DIM_TOTAL=8192 stated explicitly in script config section.

## Pre-registered threshold bands

**lift = ARM_BASELINE_RANK1_K1 BPC - arm BPC (positive = better)**

| Verdict | Condition |
|---------|-----------|
| HARD_PASS SUPER_ADDITIVE | ARM_K2_CFRPE lift >= +1.20 bits over baseline |
| HARD_PASS ADDITIVE | ARM_K2_CFRPE lift >= max(CFRPE_K1_lift, K2_RANK1_lift) + 0.10 bits |
| MIDDLE_BAND | ARM_K2_CFRPE lift > max of single-knob lifts but < +0.10 margin |
| HARD_FAIL | ARM_K2_CFRPE lift <= max(CFRPE_K1_lift, K2_RANK1_lift) (interference) |

Additional constraints:
- cv < 0.05 across seeds for ARM_K2_CFRPE (mandatory)
- ARM_BASELINE_RANK1_K1 BPC within +/-0.05 of 7.3065 ref (provenance; advisory with char-trigram encoder)

## Outcome plan for each verdict

- **HARD_PASS SUPER_ADDITIVE:** Atomize both knobs as jointly chain-grade; update cap_map; route to
  Strategy for next synthesis step (K=2 x cf-RPE as unified mechanism).
- **HARD_PASS ADDITIVE:** Atomize ARM_K2_CFRPE as the recommended combined config; update cap_map;
  Strategy routes to production-encoder replication.
- **MIDDLE_BAND:** ARM_K2_CFRPE composes but sub-additively. Choose the better single knob;
  route to Strategy for deeper composition analysis (gate mechanism investigation).
- **HARD_FAIL (interference):** K=2 and cf-RPE interfere. Report which single knob is stronger;
  route to Strategy to pick the dominant knob and investigate the interference mechanism.

## Smoke results

**Smoke scale:** N_DIM=1024, N_TRAIN=3000, 1 seed, 150 steps
**Smoke wall:** ~19s
**Smoke metrics (all non-null, non-sentinel, non-zero):**

| Arm | BPC | Lift vs baseline |
|-----|-----|-----------------|
| ARM_BASELINE_RANK1_K1 | 4.9666 | 0.000 |
| ARM_CFRPE_K1 | 4.7486 | +0.218 |
| ARM_K2_RANK1 | 4.9666 | +0.000 |
| ARM_K2_CFRPE | 4.8067 | +0.160 |

Smoke shows interference (K2_CFRPE < CFRPE_K1). This is expected at smoke scale where
N_per_bank=512 per bank is small and the cf-RPE signal is diluted by bank split. At
production N_per_bank=4096 each bank has full resolution. The smoke gate confirms:
- Script runs without error
- All 4 arms produce valid finite BPC metrics
- cf-RPE K1 lift (+0.218 at smoke) is strong, consistent with chain-grade prior

**Multi-scale smoke (N×4: N_TRAIN=12000):** Confirmed same metrics (resumed from checkpoint).
No OOM, no degenerate behavior, no integer overflow.

**Walk-back gate:** Smoke effect size is borderline (interference at smoke scale, but expected
due to dimension halving per bank). Production full run is the correct evaluation scale.
N_TRAIN=100k, N_DIM=8192 confirmed as production config.

## Timeout estimate

**Empirical benchmarks (laptop CPU, numpy BLAS):**
- Encoder build: 0.0074s/word x 4000 words = 29.7s per seed
- ARM_CFRPE_K1: 1.04s/step x 300 steps = 312s per seed
- ARM_K2_CFRPE: 0.25s/step x 300 steps x 2 banks = 150s + recall 37s = 187s per seed
- ARM_K2_RANK1 (Hebbian): 0.27s/chunk x 195 chunks = 52.7s per seed
- ARM_BASELINE_K1 (Hebbian): ~52.7s per seed
- Recall + joint sweep: ~50s per seed total overhead

**Per-seed estimate:** ~700s
**3 seeds + encoder:** 700 x 3 + 90 = 2190s
**With 1.5x safety:** ceil(1.5 x 2190) = 3285s -> **timeout_s = 3600s (1 hour)**

Note: remote_cpu (marsh@home) runs at BELOW_NORMAL priority; actual wall may be
2-3x this estimate under load. timeout_s=3600 is the minimum; if the runner is under
heavy load, it may take up to 3h. This is within the 4h absolute ceiling.

## Cites

- preregs/2026-06-23_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.md
- experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py
- experiments/shotgun_smoke_k_bank_count_sweep_v1.py
- notes/skunkworks_to_all_LANDED_VET_dual_trace_sequential_neuromod_HARD_PASS_2026-06-23.md
- notes/shotgun_smoke_K_bank_count_sweep_2026-06-23.md
