# Pre-registration: substrate_k_module_heterogeneous_compose_LM_v1

**Date:** 2026-06-23
**Anchor:** substrate_k_module_heterogeneous_compose_LM_v1
**Queue:** overnight_queue (GPU)
**Research basis:** notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md (Levy-Horn-Ruppin 1997)

## Scientific question

Does K-module HETEROGENEOUS compose (each module with independent readout, log-linear combined) break
the +0.44 bit BPC envelope cap that all prior homogeneous-compose cells have hit?

Prior evidence:
- exp_fair_harness_substrate_as_lm_v1: ARM_SPARSE_BIPOLAR_ONLY = 7.3065 BPC (chain-grade; N=8192)
- exp_substrate_neuromodulator_3axis_gated_compose_LM_v1: READOUT_DEGENERATE (homogeneous compose)
- exp_substrate_dual_trace_sequential_neuromod_LM_v1: +0.085 BPC (partial heterogeneity; 2-trace)
- Research drill: Levy-Horn-Ruppin N^M scaling requires INDEPENDENT module readouts

Untested hypothesis: K substrate chain-grade primitives (sparse-bipolar dim / lock-in freq /
HRR convolution / refuse-gate routing) live in non-overlapping algebraic structures -> INDEPENDENT
readouts -> multiplicative capacity compose -> envelope break.

## Config

- N_DIM: 8192
- N_TRAIN: 100000
- N_HELD: 20000
- VOCAB_CAP: 4000
- seeds: [7, 17, 23]
- mode: full (GPU)
- SPARSE_BIPOLAR_F: 0.05
- LOCK_IN_P: 64, LOCK_IN_K_FREQ: 31
- HRR_CONTEXT_WINDOW: 5
- REFUSE_MARGIN_THR: 0.30

## Arms

1. ARM_UNIGRAM -- analytic baseline
2. ARM_SPARSE_BIPOLAR_ONLY -- M1 alone; must reproduce ~7.3065 BPC +/- 0.05
3. ARM_M1_PLUS_LOCKIN -- M1 + M2 (frequency-domain)
4. ARM_M1_M2_PLUS_HRR -- M1 + M2 + M3 (convolutional)
5. ARM_K_MODULE_FULL_HETERO -- M1 + M2 + M3 + M4 refuse-gate (LOAD-BEARING)

## Pre-registered bands (IMMUTABLE)

HARD_PASS:
- ARM_K_MODULE_FULL_HETERO BPC lift >= +0.30 bits vs ARM_SPARSE_BIPOLAR_ONLY
- cv across 3 seeds < 0.05

CHAIN_GRADE_BONUS:
- lift >= +0.50 bits (N^M scaling visible at K=4 modules)

MIDDLE_BAND:
- lift +0.10 to +0.30 bits (partial; route to v2)

HARD_FAIL:
- lift <= +0.10 bits OR ARM_K_MODULE collapses to unigram BPC

## Falsifiable predictions

| Prediction | HARD_PASS | HARD_FAIL |
|---|---|---|
| K-module hetero compose lifts BPC | ARM_FULL lift >= +0.30 | ARM_FULL lift <= +0.10 |
| Progressive module ordering | M1 < M1+M2 < M1+M2+M3 < FULL (strictly) | any ordering inversion |
| cv stable | cv < 0.05 | cv > 0.15 |

## Calibration

P_deflated(HARD_PASS) = 0.55 (Levy-Horn-Ruppin theoretical guarantee; brain existence proof;
substrate has K chain-grade primitives in non-overlapping algebraic structures; cap relaxed
per USER brain-existence-proof directive 2026-06-23)

## Smoke gate passed

Smoke (N=512, N_TRAIN=2000, seed=[7], CPU):
- Wall time: ~30s
- All arms complete (no crashes)
- ARM_SPARSE_BIPOLAR_ONLY: 4.9672 BPC < 5.3501 unigram (M1 learning at smoke scale)
- raw_bpc_T1L1 values: 7.7-7.0 (non-trivial; not stuck at vocab entropy 11.97)
- Multi-module arms show lambda=0 best at smoke scale (expected: scale-sensitive capacity mechanism;
  N_TRAIN=2000 insufficient for lock-in/HRR modules to manifest; not a gate-blocking condition)
- SUSPICIOUS-RESULT criteria NOT met (no all-zero, all-constant, 0-valid, <100ms exit)
- Self-test: 5/5 PASS (M1 sparse-bipolar + M2 lock-in + M3 HRR + M4 refuse-gate + logits)

## Routing rationale (overnight_queue GPU)

N_DIM=8192, 3 separate W matrices (each 8192x8192 float32 = 256MB), 4-module compose,
3 seeds. Matmul-bound. Lock-in carrier applies P=64 phase rotations per key. GPU dispatch
per Fix #24: torch.cuda + batched ops.
